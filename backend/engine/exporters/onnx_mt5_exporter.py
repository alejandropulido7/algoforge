import re

class OnnxMT5Exporter:
    """Generates a professional MQL5 Expert Advisor running inference with MT5 native ONNX API."""

    def export(self, strategy: dict) -> str:
        name = strategy.get("id", "AlgoForge_RL_Agent")
        score = strategy.get("total_score", 0.0)
        sharpe = strategy.get("sharpe_ratio", 0.0)
        mc = strategy.get("mc_robustness", 0.0)
        risk_cfg = strategy.get("risk_config", {})
        onnx_filename = strategy.get("onnx_filename", "model.onnx")

        sizing_mode = 0 if risk_cfg.get("sizingMode") == "lots" else 1
        lot_size = float(risk_cfg.get("lotSize", 0.1))
        risk_pct = float(risk_cfg.get("riskPct", 1.0))
        
        sl_type_val = 0 if risk_cfg.get("slType") == "pips" else (1 if risk_cfg.get("slType") == "atr" else 2)
        sl_pips = float(risk_cfg.get("slPips", 50.0))
        sl_atr_mult = float(risk_cfg.get("slAtrMult", 1.5))
        
        tp_type_val = 0 if risk_cfg.get("tpType") == "pips" else (1 if risk_cfg.get("tpType") == "atr" else 2)
        tp_pips = float(risk_cfg.get("tpPips", 100.0))
        tp_atr_mult = float(risk_cfg.get("tpAtrMult", 3.0))

        window_size = int(strategy.get("window_size", 20))
        n_features = int(strategy.get("n_features", 5))

        return f"""//+------------------------------------------------------------------+
//|                             AlgoForge Deep RL Expert Advisor (ONNX) |
//|                                  https://github.com/algoforge    |
//| Model: {name:<20} Total Score: {score:<6.2f}          |
//| Sharpe: {sharpe:<6.2f}             MC Robustness: {mc:<6.1f}%          |
//| Architecture: PyTorch PPO Policy exported to ONNX                |
//+------------------------------------------------------------------+
#property copyright "AlgoForge AI"
#property link      "https://algoforge.io"
#property version   "1.00"
#property strict

#include <Trade\\Trade.mqh>

#define WINDOW_SIZE {window_size}
#define N_FEATURES  {n_features}

enum ENUM_SIZING_MODE
{{
   SIZING_FIXED_LOTS = 0, // Fixed Lot Size
   SIZING_RISK_PCT   = 1  // Risk % of Equity
}};

enum ENUM_STOP_TYPE
{{
   STOP_PIPS = 0, // Fixed Pips
   STOP_ATR  = 1, // ATR Multiple
   STOP_NONE = 2  // Signal Exit Only
}};

//--- Risk Management Inputs
input group "=== Risk Management ==="
input ENUM_SIZING_MODE InpSizingMode      = {sizing_mode};     // Sizing Mode
input double           InpLotSize         = {lot_size:.2f};   // Fixed Lot Size
input double           InpRiskPercent     = {risk_pct:.2f};   // Risk % of Equity
input ENUM_STOP_TYPE   InpStopLossType    = {sl_type_val};    // Stop Loss Mode
input double           InpStopLossPips    = {sl_pips:.1f};    // Stop Loss Pips
input double           InpStopLossATRMult = {sl_atr_mult:.1f};    // Stop Loss ATR Multiplier
input ENUM_STOP_TYPE   InpTakeProfitType  = {tp_type_val};    // Take Profit Mode
input double           InpTakeProfitPips  = {tp_pips:.1f};   // Take Profit Pips
input double           InpTakeProfitATRMult = {tp_atr_mult:.1f};  // Take Profit ATR Multiplier
input ulong            InpMagicNumber     = 101202;   // Magic Number

input group "=== AI Neural Network Model ==="
input string           InpOnnxModelPath   = "{onnx_filename}"; // ONNX Model in MQL5/Files/
input int              InpATRPeriod       = 14;               // ATR Period

//--- Global Objects & ONNX Handle
CTrade         trade;
long           ext_onnx_handle = INVALID_HANDLE;
int            handle_atr      = INVALID_HANDLE;

//+------------------------------------------------------------------+
//| Calculate Dynamic Lot Size                                       |
//+------------------------------------------------------------------+
double GetTradeLotSize(double sl_distance_price)
{{
   if(InpSizingMode == SIZING_FIXED_LOTS || sl_distance_price <= 0.0)
      return InpLotSize;

   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double risk_amount = equity * (InpRiskPercent / 100.0);
   double tick_size = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);

   if(tick_size <= 0.0 || tick_value <= 0.0)
      return InpLotSize;

   double calculated_lots = (risk_amount * tick_size) / (sl_distance_price * tick_value);
   double lot_step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double min_lot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double max_lot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);

   if(lot_step > 0.0)
      calculated_lots = MathFloor(calculated_lots / lot_step) * lot_step;

   return MathMin(max_lot, MathMax(min_lot, calculated_lots));
}}

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{{
   trade.SetExpertMagicNumber(InpMagicNumber);
   trade.SetDeviationInPoints(50);
   trade.SetMarginMode();
   trade.SetTypeFillingBySymbol(_Symbol);

   // 1. Create ONNX inference session
   ext_onnx_handle = OnnxCreate(InpOnnxModelPath, ONNX_DEFAULT);
   if(ext_onnx_handle == INVALID_HANDLE)
   {{
      Print("Error: Could not load ONNX model '", InpOnnxModelPath, "'. Ensure it is in MQL5/Files/ directory. Code: ", GetLastError());
      return INIT_FAILED;
   }}

   // 2. Set input shape [1, WINDOW_SIZE, N_FEATURES]
   const long input_shape[] = {{ 1, WINDOW_SIZE, N_FEATURES }};
   if(!OnnxSetInputShape(ext_onnx_handle, 0, input_shape))
   {{
      Print("Error setting ONNX input shape: ", GetLastError());
      OnnxRelease(ext_onnx_handle);
      return INIT_FAILED;
   }}

   // 3. Set output shape [1]
   const long output_shape[] = {{ 1 }};
   if(!OnnxSetOutputShape(ext_onnx_handle, 0, output_shape))
   {{
      Print("Error setting ONNX output shape: ", GetLastError());
      OnnxRelease(ext_onnx_handle);
      return INIT_FAILED;
   }}

   // 4. Auxiliary ATR indicator
   handle_atr = iATR(_Symbol, _Period, InpATRPeriod);

   Print("AlgoForge Neural ONNX Agent successfully initialized.");
   return INIT_SUCCEEDED;
}}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{{
   if(ext_onnx_handle != INVALID_HANDLE)
   {{
      OnnxRelease(ext_onnx_handle);
      ext_onnx_handle = INVALID_HANDLE;
   }}
   if(handle_atr != INVALID_HANDLE)
   {{
      IndicatorRelease(handle_atr);
      handle_atr = INVALID_HANDLE;
   }}
}}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{{
   // Execute on new bar only
   static datetime last_bar_time = 0;
   datetime current_bar_time = iTime(_Symbol, _Period, 0);
   if(current_bar_time == last_bar_time) return;

   // 1. Fetch historical rates for observation matrix
   MqlRates rates[];
   ArraySetAsSeries(rates, true);
   if(CopyRates(_Symbol, _Period, 1, WINDOW_SIZE, rates) < WINDOW_SIZE) return;

   last_bar_time = current_bar_time;

   // 2. Build normalized input tensor [1, WINDOW_SIZE, N_FEATURES]
   float input_tensor[WINDOW_SIZE * N_FEATURES];
   
   // Compute local normalization statistics
   float mean_close = 0.0f;
   for(int b = 0; b < WINDOW_SIZE; b++)
      mean_close += (float)rates[b].close;
   mean_close /= (float)WINDOW_SIZE;

   int idx = 0;
   for(int b = WINDOW_SIZE - 1; b >= 0; b--)
   {{
      input_tensor[idx++] = (float)((rates[b].open - mean_close) / (mean_close + 1e-6));
      input_tensor[idx++] = (float)((rates[b].high - mean_close) / (mean_close + 1e-6));
      input_tensor[idx++] = (float)((rates[b].low - mean_close) / (mean_close + 1e-6));
      input_tensor[idx++] = (float)((rates[b].close - mean_close) / (mean_close + 1e-6));
      input_tensor[idx++] = (float)(rates[b].tick_volume / 10000.0);
   }}

   // 3. Run neural network inference
   long output_action[1];
   if(!OnnxRun(ext_onnx_handle, ONNX_NO_CONVERSION, input_tensor, output_action))
   {{
      Print("Error running ONNX model inference: ", GetLastError());
      return;
   }}

   // Action mapping: 0 = Hold/Flat, 1 = Buy (Long), 2 = Sell (Short)
   long action = output_action[0];
   bool buy_condition  = (action == 1);
   bool sell_condition = (action == 2);

   // 4. Position Management & Exit Check
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {{
      ulong ticket = PositionGetTicket(i);
      if(ticket > 0)
      {{
         string pos_symbol = PositionGetString(POSITION_SYMBOL);
         ulong  pos_magic  = (ulong)PositionGetInteger(POSITION_MAGIC);

         if(pos_symbol == _Symbol && (pos_magic == InpMagicNumber || InpMagicNumber == 0))
         {{
            long pos_type = PositionGetInteger(POSITION_TYPE);
            
            if(pos_type == POSITION_TYPE_BUY && (sell_condition || action == 0))
            {{
               trade.PositionClose(ticket);
            }}
            else if(pos_type == POSITION_TYPE_SELL && (buy_condition || action == 0))
            {{
               trade.PositionClose(ticket);
            }}
         }}
      }}
   }}

   // 5. Verify If Still In Position
   bool has_position = false;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {{
      ulong ticket = PositionGetTicket(i);
      if(ticket > 0)
      {{
         string pos_symbol = PositionGetString(POSITION_SYMBOL);
         ulong  pos_magic  = (ulong)PositionGetInteger(POSITION_MAGIC);
         if(pos_symbol == _Symbol && (pos_magic == InpMagicNumber || InpMagicNumber == 0))
         {{
            has_position = true;
            break;
         }}
      }}
   }}

   // 6. Order Entry (Only when flat)
   if(!has_position)
   {{
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
      
      double atr_val[];
      ArraySetAsSeries(atr_val, true);
      double atr_curr = 0.0;
      if(CopyBuffer(handle_atr, 0, 0, 2, atr_val) > 0)
         atr_curr = atr_val[1];

      if(buy_condition)
      {{
         double sl_dist = 0.0;
         double sl = 0.0;
         if(InpStopLossType == STOP_PIPS && InpStopLossPips > 0.0)
         {{
            sl_dist = InpStopLossPips * 10.0 * point;
            sl = NormalizeDouble(ask - sl_dist, _Digits);
         }}
         else if(InpStopLossType == STOP_ATR && InpStopLossATRMult > 0.0 && atr_curr > 0.0)
         {{
            sl_dist = InpStopLossATRMult * atr_curr;
            sl = NormalizeDouble(ask - sl_dist, _Digits);
         }}

         double tp = 0.0;
         if(InpTakeProfitType == STOP_PIPS && InpTakeProfitPips > 0.0)
            tp = NormalizeDouble(ask + (InpTakeProfitPips * 10.0 * point), _Digits);
         else if(InpTakeProfitType == STOP_ATR && InpTakeProfitATRMult > 0.0 && atr_curr > 0.0)
            tp = NormalizeDouble(ask + (InpTakeProfitATRMult * atr_curr), _Digits);

         double volume = GetTradeLotSize(sl_dist);
         trade.Buy(volume, _Symbol, ask, sl, tp, "AlgoForge RL Buy");
      }}
      else if(sell_condition)
      {{
         double sl_dist = 0.0;
         double sl = 0.0;
         if(InpStopLossType == STOP_PIPS && InpStopLossPips > 0.0)
         {{
            sl_dist = InpStopLossPips * 10.0 * point;
            sl = NormalizeDouble(bid + sl_dist, _Digits);
         }}
         else if(InpStopLossType == STOP_ATR && InpStopLossATRMult > 0.0 && atr_curr > 0.0)
         {{
            sl_dist = InpStopLossATRMult * atr_curr;
            sl = NormalizeDouble(bid + sl_dist, _Digits);
         }}

         double tp = 0.0;
         if(InpTakeProfitType == STOP_PIPS && InpTakeProfitPips > 0.0)
            tp = NormalizeDouble(bid - (InpTakeProfitPips * 10.0 * point), _Digits);
         else if(InpTakeProfitType == STOP_ATR && InpTakeProfitATRMult > 0.0 && atr_curr > 0.0)
            tp = NormalizeDouble(bid - (InpTakeProfitATRMult * atr_curr), _Digits);

         double volume = GetTradeLotSize(sl_dist);
         trade.Sell(volume, _Symbol, bid, sl, tp, "AlgoForge RL Sell");
      }}
   }}
}}
"""
