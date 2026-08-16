import re
from .ast_parser import parse_prefix_expression, extract_indicators, node_to_mql5

class MT5Exporter:
    """Generate dynamic, compilable MQL5 Expert Advisor code matching exact strategy logic and risk settings."""

    INDICATOR_HANDLES = {
        "rsi": {
            "param": "input int      InpRSIPeriod = 14;  // RSI Period",
            "handle": "handle_rsi = iRSI(_Symbol, _Period, InpRSIPeriod, PRICE_CLOSE);",
            "type": "rsi"
        },
        "ema": {
            "param": "input int      InpEMAPeriod = 20;  // EMA Period",
            "handle": "handle_ema = iMA(_Symbol, _Period, InpEMAPeriod, 0, MODE_EMA, PRICE_CLOSE);",
            "type": "ema"
        },
        "sma": {
            "param": "input int      InpSMAPeriod = 20;  // SMA Period",
            "handle": "handle_sma = iMA(_Symbol, _Period, InpSMAPeriod, 0, MODE_SMA, PRICE_CLOSE);",
            "type": "sma"
        },
        "atr": {
            "param": "input int      InpATRPeriod = 14;  // ATR Period",
            "handle": "handle_atr = iATR(_Symbol, _Period, InpATRPeriod);",
            "type": "atr"
        },
        "aroon": {
            "param": "input int      InpAroonPeriod = 25; // Aroon Period",
            "handle": "handle_aroon = iAroon(_Symbol, _Period, InpAroonPeriod);",
            "type": "aroon"
        },
        "psar": {
            "param": "input double   InpPSARStep = 0.02; // PSAR Step\ninput double   InpPSARMax  = 0.2;  // PSAR Max",
            "handle": "handle_psar = iSAR(_Symbol, _Period, InpPSARStep, InpPSARMax);",
            "type": "psar"
        },
        "macd": {
            "param": "input int      InpMACDFast = 12; // MACD Fast\ninput int      InpMACDSlow = 26; // MACD Slow\ninput int      InpMACDSig  = 9;  // MACD Signal",
            "handle": "handle_macd = iMACD(_Symbol, _Period, InpMACDFast, InpMACDSlow, InpMACDSig, PRICE_CLOSE);",
            "type": "macd"
        },
        "bollinger_bands": {
            "param": "input int      InpBBPeriod = 20;   // Bollinger Period\ninput double   InpBBDev    = 2.0;  // Bollinger Deviation",
            "handle": "handle_bollinger_bands = iBands(_Symbol, _Period, InpBBPeriod, 0, InpBBDev, PRICE_CLOSE);",
            "type": "bb"
        },
        "bbands": {
            "param": "input int      InpBBPeriod = 20;   // Bollinger Period\ninput double   InpBBDev    = 2.0;  // Bollinger Deviation",
            "handle": "handle_bbands = iBands(_Symbol, _Period, InpBBPeriod, 0, InpBBDev, PRICE_CLOSE);",
            "type": "bb"
        },
        "williams_r": {
            "param": "input int      InpWPRPeriod = 14;  // Williams %R Period",
            "handle": "handle_williams_r = iWPR(_Symbol, _Period, InpWPRPeriod);",
            "type": "wpr"
        },
        "williams_pct": {
            "param": "input int      InpWPRPeriod = 14;  // Williams %R Period",
            "handle": "handle_williams_pct = iWPR(_Symbol, _Period, InpWPRPeriod);",
            "type": "wpr"
        },
        "stochastic": {
            "param": "input int      InpStochK = 14; // Stochastic %K\ninput int      InpStochD = 3;  // Stochastic %D",
            "handle": "handle_stochastic = iStochastic(_Symbol, _Period, InpStochK, InpStochD, 3, MODE_SMA, STO_LOWHIGH);",
            "type": "stoch"
        },
        "obv": {
            "param": "// OBV indicator",
            "handle": "handle_obv = iOBV(_Symbol, _Period, VOLUME_TICK);",
            "type": "obv"
        },
        "vwap": {
            "param": "input int      InpVWAPPeriod = 14; // VWAP / Volume Price Period",
            "handle": "handle_vwap = iMA(_Symbol, _Period, InpVWAPPeriod, 0, MODE_LWMA, PRICE_WEIGHTED);",
            "type": "vwap"
        },
        "cci": {
            "param": "input int      InpCCIPeriod = 20;  // CCI Period",
            "handle": "handle_cci = iCCI(_Symbol, _Period, InpCCIPeriod, PRICE_TYPICAL);",
            "type": "cci"
        },
        "adx": {
            "param": "input int      InpADXPeriod = 14;  // ADX Period",
            "handle": "handle_adx = iADX(_Symbol, _Period, InpADXPeriod);",
            "type": "adx"
        }
    }

    def export(self, strategy: dict) -> str:
        name = strategy.get("id", "AlgoForge_Strategy")
        score = strategy.get("total_score", 0.0)
        sharpe = strategy.get("sharpe_ratio", 0.0)
        mc = strategy.get("mc_robustness", 0.0)
        tree_str = strategy.get("strategy_tree", "")
        risk_cfg = strategy.get("risk_config", {})

        # Risk parameters
        sizing_mode = 0 if risk_cfg.get("sizingMode") == "lots" else 1
        lot_size = float(risk_cfg.get("lotSize", 0.1))
        risk_pct = float(risk_cfg.get("riskPct", 1.0))
        
        sl_type_val = 0 if risk_cfg.get("slType") == "pips" else (1 if risk_cfg.get("slType") == "atr" else 2)
        sl_pips = float(risk_cfg.get("slPips", 50.0))
        sl_atr_mult = float(risk_cfg.get("slAtrMult", 1.5))
        
        tp_type_val = 0 if risk_cfg.get("tpType") == "pips" else (1 if risk_cfg.get("tpType") == "atr" else 2)
        tp_pips = float(risk_cfg.get("tpPips", 100.0))
        tp_atr_mult = float(risk_cfg.get("tpAtrMult", 3.0))

        # Parse AST & Transpile
        ast = parse_prefix_expression(tree_str)
        used_indicators = extract_indicators(ast)
        transpiled_expr = node_to_mql5(ast)

        # Ensure ATR handle exists if ATR stops are used
        needs_atr_handle = (sl_type_val == 1 or tp_type_val == 1)
        if needs_atr_handle:
            used_indicators.add("ATR")

        # Build dynamic indicator inputs & handles
        inputs_list = []
        handles_decl = []
        handles_init = []
        handles_check = []
        handles_release = []
        buffer_copies = []

        for raw_ind in sorted(used_indicators):
            clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", raw_ind).lower()
            ind_info = self.INDICATOR_HANDLES.get(clean_name)
            
            if not ind_info:
                ind_info = {
                    "param": f"input int      Inp_{clean_name}_Period = 14; // {raw_ind} Period",
                    "handle": f"handle_{clean_name} = iMA(_Symbol, _Period, Inp_{clean_name}_Period, 0, MODE_EMA, PRICE_CLOSE);",
                    "type": "ma"
                }

            inputs_list.append(ind_info["param"])
            handles_decl.append(f"int handle_{clean_name};")
            handles_init.append(f"   {ind_info['handle']}")
            handles_check.append(f"handle_{clean_name} == INVALID_HANDLE")
            handles_release.append(f"   IndicatorRelease(handle_{clean_name});")

            buffer_copies.append(
                f"   double {clean_name}_val[];\n"
                f"   ArraySetAsSeries({clean_name}_val, true);\n"
                f"   if(CopyBuffer(handle_{clean_name}, 0, 0, 3, {clean_name}_val) < 2) return;"
            )

        if not inputs_list:
            inputs_list.append("input int InpMAPeriod = 14; // Fallback MA Period")
            handles_decl.append("int handle_ma;")
            handles_init.append("   handle_ma = iMA(_Symbol, _Period, InpMAPeriod, 0, MODE_SMA, PRICE_CLOSE);")
            handles_check.append("handle_ma == INVALID_HANDLE")
            handles_release.append("   IndicatorRelease(handle_ma);")
            buffer_copies.append(
                "   double ma_val[];\n"
                "   ArraySetAsSeries(ma_val, true);\n"
                "   if(CopyBuffer(handle_ma, 0, 0, 3, ma_val) < 2) return;"
            )

        inputs_code = "\n".join(inputs_list)
        handles_decl_code = "\n".join(handles_decl)
        handles_init_code = "\n".join(handles_init)
        handles_check_code = " ||\n      ".join(handles_check)
        handles_release_code = "\n".join(handles_release)
        buffer_copies_code = "\n\n".join(buffer_copies)

        return f"""//+------------------------------------------------------------------+
//|                                     AlgoForge Expert Advisor     |
//|                                  https://github.com/algoforge    |
//| Strategy ID: {name:<20} Total Score: {score:<6.2f}          |
//| Sharpe: {sharpe:<6.2f}             MC Robustness: {mc:<6.1f}%          |
//| Evolved Logic: {tree_str}
//+------------------------------------------------------------------+
#property copyright "AlgoForge AI"
#property link      "https://algoforge.io"
#property version   "1.00"
#property strict

#include <Trade\\Trade.mqh>

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

//--- Risk & Money Management Inputs
input group "=== Risk Management ==="
input ENUM_SIZING_MODE InpSizingMode      = {sizing_mode};     // Sizing Mode
input double           InpLotSize         = {lot_size:.2f};   // Fixed Lot Size (if Sizing=Lots)
input double           InpRiskPercent     = {risk_pct:.2f};   // Risk % of Equity (if Sizing=Risk%)
input ENUM_STOP_TYPE   InpStopLossType    = {sl_type_val};    // Stop Loss Mode
input double           InpStopLossPips    = {sl_pips:.1f};    // Stop Loss Pips
input double           InpStopLossATRMult = {sl_atr_mult:.1f};    // Stop Loss ATR Multiplier
input ENUM_STOP_TYPE   InpTakeProfitType  = {tp_type_val};    // Take Profit Mode
input double           InpTakeProfitPips  = {tp_pips:.1f};   // Take Profit Pips
input double           InpTakeProfitATRMult = {tp_atr_mult:.1f};  // Take Profit ATR Multiplier
input ulong            InpMagicNumber     = 101202;   // Magic Number

input group "=== Evolved Indicator Parameters ==="
{inputs_code}

//--- Global Objects & Handles
CTrade trade;
{handles_decl_code}

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

{handles_init_code}

   if({handles_check_code})
   {{
      Print("Error creating indicator handles in OnInit");
      return INIT_FAILED;
   }}

   return INIT_SUCCEEDED;
}}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{{
{handles_release_code}
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
   last_bar_time = current_bar_time;

{buffer_copies_code}

   // --- Evolved Logic Expression Evaluation ---
   double signal_val = {transpiled_expr};

   bool buy_condition  = (signal_val > 0.0);
   bool sell_condition = (signal_val < 0.0);

   // --- Position Management ---
   int total_positions = PositionsTotal();
   bool has_position = false;

   for(int i = total_positions - 1; i >= 0; i--)
   {{
      ulong ticket = PositionGetTicket(i);
      if(PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == InpMagicNumber)
      {{
         has_position = true;
         long pos_type = PositionGetInteger(POSITION_TYPE);
         
         if(pos_type == POSITION_TYPE_BUY && sell_condition)
         {{
            trade.PositionClose(ticket);
            has_position = false;
         }}
         else if(pos_type == POSITION_TYPE_SELL && buy_condition)
         {{
            trade.PositionClose(ticket);
            has_position = false;
         }}
      }}
   }}

   // --- Order Entry ---
   if(!has_position)
   {{
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
      double atr_current = 0.0;
      {"atr_current = atr_val[0];" if needs_atr_handle else ""}

      if(buy_condition)
      {{
         double sl_dist = 0.0;
         double sl = 0.0;
         if(InpStopLossType == STOP_PIPS && InpStopLossPips > 0.0)
         {{
            sl_dist = InpStopLossPips * 10.0 * point;
            sl = ask - sl_dist;
         }}
         else if(InpStopLossType == STOP_ATR && InpStopLossATRMult > 0.0 && atr_current > 0.0)
         {{
            sl_dist = InpStopLossATRMult * atr_current;
            sl = ask - sl_dist;
         }}

         double tp = 0.0;
         if(InpTakeProfitType == STOP_PIPS && InpTakeProfitPips > 0.0)
            tp = ask + (InpTakeProfitPips * 10.0 * point);
         else if(InpTakeProfitType == STOP_ATR && InpTakeProfitATRMult > 0.0 && atr_current > 0.0)
            tp = ask + (InpTakeProfitATRMult * atr_current);

         double volume = GetTradeLotSize(sl_dist);
         trade.Buy(volume, _Symbol, ask, sl, tp, "AlgoForge Buy Signal");
      }}
      else if(sell_condition)
      {{
         double sl_dist = 0.0;
         double sl = 0.0;
         if(InpStopLossType == STOP_PIPS && InpStopLossPips > 0.0)
         {{
            sl_dist = InpStopLossPips * 10.0 * point;
            sl = bid + sl_dist;
         }}
         else if(InpStopLossType == STOP_ATR && InpStopLossATRMult > 0.0 && atr_current > 0.0)
         {{
            sl_dist = InpStopLossATRMult * atr_current;
            sl = bid + sl_dist;
         }}

         double tp = 0.0;
         if(InpTakeProfitType == STOP_PIPS && InpTakeProfitPips > 0.0)
            tp = bid - (InpTakeProfitPips * 10.0 * point);
         else if(InpTakeProfitType == STOP_ATR && InpTakeProfitATRMult > 0.0 && atr_current > 0.0)
            tp = bid - (InpTakeProfitATRMult * atr_current);

         double volume = GetTradeLotSize(sl_dist);
         trade.Sell(volume, _Symbol, bid, sl, tp, "AlgoForge Sell Signal");
      }}
   }}
}}
"""
