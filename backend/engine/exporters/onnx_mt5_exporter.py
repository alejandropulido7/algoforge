import re

class OnnxMT5Exporter:
    """Generates a professional MQL5 Expert Advisor running inference with MT5 native ONNX API."""

    def export(self, strategy: dict) -> str:
        rank = strategy.get("rank", 21)
        name = strategy.get("id", f"AlgoForge_RL_Agent_{rank}")
        symbol = strategy.get("symbol") or "_Symbol"
        timeframe = strategy.get("timeframe") or "_Period"
        score = float(strategy.get("total_score", 0.0))
        sharpe = float(strategy.get("sharpe_ratio", 0.0))
        total_return = float(strategy.get("total_return_pct", 0.0))
        gross_profit = float(strategy.get("gross_profit", 0.0))
        gross_loss = float(strategy.get("gross_loss", 0.0))
        net_profit = float(strategy.get("total_net_profit", gross_profit - gross_loss))
        win_rate = float(strategy.get("win_rate", 0.0))
        profit_factor = float(strategy.get("profit_factor", 0.0))
        n_trades = int(strategy.get("n_trades", 0))
        max_dd = float(strategy.get("max_drawdown_pct", 0.0))
        mc_score = float(strategy.get("mc_robustness", 0.0))
        mc_ruin = float(strategy.get("mc_prob_ruin", 0.0))
        mc_95_dd = float(strategy.get("mc_95_drawdown", 0.0))
        
        onnx_filename = strategy.get("onnx_filename")
        if not onnx_filename:
            job_id = strategy.get("job_id", "")
            onnx_filename = f"AlgoForge_Strategy_{rank}.onnx" if not job_id else f"AlgoForge_Job_{job_id}.onnx"

        # Extract Risk Configuration
        risk_cfg = strategy.get("risk_config")
        if not risk_cfg or not isinstance(risk_cfg, dict):
            risk_cfg = strategy.get("exit_rules", {}).get("risk_config", {})
        if not isinstance(risk_cfg, dict):
            risk_cfg = {}

        # 1. Sizing Mode & Lots
        sizing_mode_str = str(risk_cfg.get("sizingMode") or risk_cfg.get("sizing_mode") or "lots").lower()
        sizing_mode = 0 if sizing_mode_str == "lots" else 1
        lot_size = float(risk_cfg.get("lotSize") or risk_cfg.get("lot_size") or 0.1)
        risk_pct = float(risk_cfg.get("riskPct") or risk_cfg.get("risk_pct") or 1.0)
        
        # 2. Trade Direction
        direction_str = str(risk_cfg.get("direction", "both")).lower()
        dir_val = 1 if direction_str == "long" else (2 if direction_str == "short" else 0)

        # 3. Order Execution Mode
        order_type_str = str(risk_cfg.get("orderType") or risk_cfg.get("order_type") or "market").lower()
        order_exec_val = 1 if order_type_str == "stop" else (2 if order_type_str == "limit" else 0)
        pending_timeout = int(risk_cfg.get("pendingTimeoutBars") or risk_cfg.get("pending_timeout_bars") or 3)
        pending_offset = float(risk_cfg.get("pendingOffsetPips") or risk_cfg.get("pending_offset_pips") or 5.0)
        max_holding_bars = int(risk_cfg.get("maxHoldingBars") or risk_cfg.get("max_holding_bars") or 0)

        # 4. Consecutive Loss Protection & Reactivation
        consec_action_str = str(risk_cfg.get("consecutiveLossAction") or risk_cfg.get("consecutive_loss_action") or "none").lower()
        consec_action_val = 1 if consec_action_str == "reduce_risk" else (2 if consec_action_str == "stop_bot" else 0)
        consec_threshold = int(risk_cfg.get("consecutiveLossThreshold") or risk_cfg.get("consecutive_loss_threshold") or 3)
        consec_reduction = float(risk_cfg.get("consecutiveLossReductionPct") or risk_cfg.get("consecutive_loss_reduction_pct") or 50.0)

        consec_reactivate_str = str(risk_cfg.get("consecutiveLossReactivation") or risk_cfg.get("consecutive_loss_reactivation") or "none").lower()
        reactivation_mode_map = {
            "none": 0,
            "cooldown_bars": 1,
            "next_session": 2,
            "next_day": 3,
            "days_count": 4,
            "next_week": 5
        }
        reactivation_val = reactivation_mode_map.get(consec_reactivate_str, 0)
        cooldown_bars = int(risk_cfg.get("consecutiveLossCooldownBars") or risk_cfg.get("consecutive_loss_cooldown_bars") or 20)
        cooldown_days = int(risk_cfg.get("consecutiveLossCooldownDays") or risk_cfg.get("consecutive_loss_cooldown_days") or 1)

        # 5. Stop Loss & Take Profit
        sl_type_str = str(risk_cfg.get("slType") or risk_cfg.get("sl_type") or "pips").lower()
        sl_type_val = 0 if sl_type_str == "pips" else (1 if sl_type_str == "atr" else 2)
        sl_pips = float(risk_cfg.get("slPips") or risk_cfg.get("sl_pips") or 50.0)
        sl_atr_mult = float(risk_cfg.get("slAtrMult") or risk_cfg.get("sl_atr_mult") or 1.5)
        
        tp_type_str = str(risk_cfg.get("tpType") or risk_cfg.get("tp_type") or "pips").lower()
        tp_type_val = 0 if tp_type_str == "pips" else (1 if tp_type_str == "atr" else 2)
        tp_pips = float(risk_cfg.get("tpPips") or risk_cfg.get("tp_pips") or 100.0)
        tp_atr_mult = float(risk_cfg.get("tpAtrMult") or risk_cfg.get("tp_atr_mult") or 3.0)

        window_size = int(strategy.get("window_size", 20))
        n_features = int(strategy.get("n_features", 5))

        return f"""//+------------------------------------------------------------------+
//|                             AlgoForge Deep RL Expert Advisor (ONNX) |
//|                                  https://github.com/algoforge    |
//| Strategy Rank: #{rank}           Strategy ID: {name}
//| Symbol: {symbol}     Timeframe: {timeframe}
//| Total Net Profit: ${net_profit:.2f} | Total Return: {total_return:.2f}%
//| Win Rate: {win_rate:.2f}% | Profit Factor: {profit_factor:.2f} | Total Trades: {n_trades}
//| Sharpe Ratio: {sharpe:.2f} | Max Drawdown: {max_dd:.2f}%
//| Monte Carlo Robustness: {mc_score:.1f}% | Prob of Ruin: {mc_ruin:.2f}%
//| MC 95% Confidence Drawdown: {mc_95_dd:.2f}%
//| Architecture: Deep Reinforcement Learning (PyTorch PPO/A2C)      |
//+------------------------------------------------------------------+
#property copyright "AlgoForge AI"
#property link      "https://algoforge.io"
#property version   "1.00"
#property description "AlgoForge Deep RL Strategy #{rank} - Win Rate: {win_rate:.2f}%, Sharpe: {sharpe:.2f}, MC: {mc_score:.1f}%"
#property strict

//--- Embed ONNX Model binary as compiled resource (Official MT5 pattern for Strategy Tester & Live)
#resource "\\\\Files\\\\AlgoForge_Strategy_{rank}.onnx" as uchar ExtOnnxModel[]

//--- Instruct MetaTrader 5 Strategy Tester to pass the file to remote/local tester agents
#property tester_file "AlgoForge_Strategy_{rank}.onnx"
#property tester_file "{onnx_filename}"
#property tester_file "model.onnx"

#include <Trade\\Trade.mqh>

#define WINDOW_SIZE {window_size}
#define N_FEATURES  {n_features}

enum ENUM_TRADE_DIRECTION
{{
   DIR_BOTH       = 0, // Long & Short
   DIR_LONG_ONLY  = 1, // Long Only
   DIR_SHORT_ONLY = 2  // Short Only
}};

enum ENUM_SIZING_MODE
{{
   SIZING_FIXED_LOTS = 0, // Fixed Lot Size
   SIZING_RISK_PCT   = 1  // Risk % of Equity
}};

enum ENUM_CONSEC_LOSS_ACTION
{{
   LOSS_ACTION_NONE        = 0, // No Restriction (Normal Trading)
   LOSS_ACTION_REDUCE_RISK = 1, // Reduce Lot Size After X Losses
   LOSS_ACTION_STOP_BOT    = 2  // Halt EA Trading After X Losses
}};

enum ENUM_REACTIVATION_MODE
{{
   REACTIVATE_MANUAL       = 0, // Manual (Permanently Paused Until Reset)
   REACTIVATE_COOLDOWN_BAR = 1, // Cooldown Bars (Velas de Espera)
   REACTIVATE_NEXT_SESSION = 2, // Next Trading Session
   REACTIVATE_NEXT_DAY     = 3, // Next Calendar Day (00:00)
   REACTIVATE_DAYS_COUNT   = 4, // After X Days
   REACTIVATE_NEXT_WEEK    = 5  // Next Week (Monday)
}};

enum ENUM_STOP_TYPE
{{
   STOP_PIPS = 0, // Fixed Pips
   STOP_ATR  = 1, // ATR Multiple
   STOP_NONE = 2  // Signal Exit Only
}};

//--- Risk & Execution Management Inputs (Configured in AlgoForge Analysis)
input group "=== Risk & Execution Management ==="
input ENUM_TRADE_DIRECTION    InpTradeDirection       = {dir_val};  // Allowed Trade Direction
input int                     InpMaxHoldingBars       = {max_holding_bars}; // Max Holding Bars (0 = Disabled)
input ENUM_CONSEC_LOSS_ACTION InpConsecLossAction     = {consec_action_val}; // Consecutive Losses Protection
input int                     InpConsecLossThreshold  = {consec_threshold}; // Consecutive Losses Trigger (X)
input double                  InpConsecLossReduction  = {consec_reduction:.1f}; // Risk / Lot Reduction % (if Reduce Mode)
input ENUM_REACTIVATION_MODE  InpReactivationMode     = {reactivation_val}; // Auto-Reactivation Rule (if Paused)
input int                     InpCooldownBars         = {cooldown_bars}; // Cooldown Bars (if Mode=Bars)
input int                     InpCooldownDays         = {cooldown_days}; // Cooldown Days (if Mode=Days)
input ENUM_SIZING_MODE        InpSizingMode           = {sizing_mode};     // Sizing Mode
input double                  InpLotSize              = {lot_size:.2f};   // Fixed Lot Size (if Sizing=Lots)
input double                  InpRiskPercent          = {risk_pct:.2f};   // Risk % of Equity (if Sizing=Risk%)
input ENUM_STOP_TYPE          InpStopLossType         = {sl_type_val};    // Stop Loss Mode
input double                  InpStopLossPips         = {sl_pips:.1f};    // Stop Loss Pips
input double                  InpStopLossATRMult      = {sl_atr_mult:.1f};    // Stop Loss ATR Multiplier
input ENUM_STOP_TYPE          InpTakeProfitType       = {tp_type_val};    // Take Profit Mode
input double                  InpTakeProfitPips       = {tp_pips:.1f};   // Take Profit Pips
input double                  InpTakeProfitATRMult    = {tp_atr_mult:.1f};  // Take Profit ATR Multiplier
input ulong                   InpMagicNumber          = 101202;   // Magic Number

input group "=== AI Neural Network Model ==="
input string                  InpOnnxModelPath        = "AlgoForge_Strategy_{rank}.onnx"; // Fallback ONNX Model Name
input int                     InpATRPeriod            = 14;               // ATR Period

//--- Global Objects & ONNX Handle
CTrade         trade;
long           ext_onnx_handle = INVALID_HANDLE;
int            handle_atr      = INVALID_HANDLE;

//+------------------------------------------------------------------+
//| Count Consecutive Losses in Account History                      |
//+------------------------------------------------------------------+
int GetConsecutiveLosses()
{{
   if(!HistorySelect(0, TimeCurrent())) return 0;
   int deals_total = HistoryDealsTotal();
   int losses = 0;
   for(int i = deals_total - 1; i >= 0; i--)
   {{
      ulong deal_ticket = HistoryDealGetTicket(i);
      if(deal_ticket > 0)
      {{
         string d_symbol = HistoryDealGetString(deal_ticket, DEAL_SYMBOL);
         ulong  d_magic  = (ulong)HistoryDealGetInteger(deal_ticket, DEAL_MAGIC);
         long   d_entry  = HistoryDealGetInteger(deal_ticket, DEAL_ENTRY);
         if(d_symbol == _Symbol && (d_magic == InpMagicNumber || InpMagicNumber == 0) && d_entry == DEAL_ENTRY_OUT)
         {{
            double profit = HistoryDealGetDouble(deal_ticket, DEAL_PROFIT);
            if(profit < 0.0) losses++;
            else if(profit > 0.0) break;
         }}
      }}
   }}
   return losses;
}}

//+------------------------------------------------------------------+
//| Get Time of the Last Closed Losing Deal                          |
//+------------------------------------------------------------------+
datetime GetLastLosingDealTime()
{{
   if(!HistorySelect(0, TimeCurrent())) return 0;
   int deals_total = HistoryDealsTotal();
   for(int i = deals_total - 1; i >= 0; i--)
   {{
      ulong deal_ticket = HistoryDealGetTicket(i);
      if(deal_ticket > 0)
      {{
         string d_symbol = HistoryDealGetString(deal_ticket, DEAL_SYMBOL);
         ulong  d_magic  = (ulong)HistoryDealGetInteger(deal_ticket, DEAL_MAGIC);
         long   d_entry  = HistoryDealGetInteger(deal_ticket, DEAL_ENTRY);
         if(d_symbol == _Symbol && (d_magic == InpMagicNumber || InpMagicNumber == 0) && d_entry == DEAL_ENTRY_OUT)
         {{
            double profit = HistoryDealGetDouble(deal_ticket, DEAL_PROFIT);
            if(profit < 0.0)
               return (datetime)HistoryDealGetInteger(deal_ticket, DEAL_TIME);
         }}
      }}
   }}
   return 0;
}}

//+------------------------------------------------------------------+
//| Check If Bot is Currently in Paused State or Reactivated         |
//+------------------------------------------------------------------+
bool IsBotHalted(int consec_losses)
{{
   if(InpConsecLossAction != LOSS_ACTION_STOP_BOT || consec_losses < InpConsecLossThreshold)
      return false;

   if(InpReactivationMode == REACTIVATE_MANUAL)
      return true;

   datetime last_loss_time = GetLastLosingDealTime();
   if(last_loss_time == 0) return false;

   datetime current_time = TimeCurrent();

   if(InpReactivationMode == REACTIVATE_COOLDOWN_BAR)
   {{
      int bars_since_loss = Bars(_Symbol, _Period, last_loss_time, current_time);
      if(bars_since_loss >= InpCooldownBars)
         return false; // Reactivated!
   }}
   else if(InpReactivationMode == REACTIVATE_NEXT_SESSION)
   {{
      if((current_time - last_loss_time) >= 28800)
         return false; // Reactivated after 8h / session transition!
   }}
   else if(InpReactivationMode == REACTIVATE_NEXT_DAY)
   {{
      MqlDateTime dt_loss, dt_curr;
      TimeToStruct(last_loss_time, dt_loss);
      TimeToStruct(current_time, dt_curr);
      if(dt_curr.day != dt_loss.day || dt_curr.mon != dt_loss.mon || dt_curr.year != dt_loss.year)
         return false; // Reactivated on next calendar day!
   }}
   else if(InpReactivationMode == REACTIVATE_DAYS_COUNT)
   {{
      if((current_time - last_loss_time) >= (InpCooldownDays * 86400))
         return false; // Reactivated after X days!
   }}
   else if(InpReactivationMode == REACTIVATE_NEXT_WEEK)
   {{
      MqlDateTime dt_curr;
      TimeToStruct(current_time, dt_curr);
      if((current_time - last_loss_time) >= 86400 && dt_curr.day_of_week == 1)
         return false; // Reactivated on Monday!
   }}

   return true;
}}

//+------------------------------------------------------------------+
//| Calculate Dynamic Lot Size with Loss Streak Protection           |
//+------------------------------------------------------------------+
double GetTradeLotSize(double sl_distance_price, int consec_losses = 0)
{{
   double base_lot = InpLotSize;
   if(InpSizingMode == SIZING_RISK_PCT && sl_distance_price > 0.0)
   {{
      double equity = AccountInfoDouble(ACCOUNT_EQUITY);
      double risk_amount = equity * (InpRiskPercent / 100.0);
      double tick_size = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
      double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
      if(tick_size > 0.0 && tick_value > 0.0)
         base_lot = (risk_amount * tick_size) / (sl_distance_price * tick_value);
   }}

   // Consecutive loss risk reduction
   if(InpConsecLossAction == LOSS_ACTION_REDUCE_RISK && consec_losses >= InpConsecLossThreshold)
   {{
      double factor = MathMax(0.1, 1.0 - (InpConsecLossReduction / 100.0));
      base_lot = base_lot * factor;
   }}

   double lot_step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double min_lot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double max_lot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);

   if(lot_step > 0.0)
      base_lot = MathFloor(base_lot / lot_step) * lot_step;

   return MathMin(max_lot, MathMax(min_lot, base_lot));
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

   // 1. Primary Method: Load directly from embedded #resource binary buffer (100% isolated & tester-safe)
   if(ArraySize(ExtOnnxModel) > 0)
   {{
      ext_onnx_handle = OnnxCreateFromBuffer(ExtOnnxModel, ONNX_DEFAULT);
      if(ext_onnx_handle != INVALID_HANDLE)
      {{
         Print("✓ [ONNX Loaded]: Successfully initialized from embedded #resource binary buffer (", ArraySize(ExtOnnxModel), " bytes)");
      }}
   }}

   // 2. Fallbacks: If not embedded or using external custom file
   if(ext_onnx_handle == INVALID_HANDLE)
   {{
      string candidate_names[] = {{
         "::Files\\\\AlgoForge_Strategy_{rank}.onnx",
         InpOnnxModelPath,
         "AlgoForge_Strategy_{rank}.onnx",
         "{onnx_filename}",
         "model.onnx"
      }};

      for(int i = 0; i < ArraySize(candidate_names); i++)
      {{
         string fn = candidate_names[i];
         if(fn == "") continue;

         // Try local MQL5/Files or tester agent
         ext_onnx_handle = OnnxCreate(fn, ONNX_DEFAULT);
         if(ext_onnx_handle != INVALID_HANDLE)
         {{
            Print("✓ [ONNX Loaded]: Mode ONNX_DEFAULT from '", fn, "'");
            break;
         }}

         // Try Common Files folder (Terminal -> Open Common Data Folder -> Files/)
         ext_onnx_handle = OnnxCreate(fn, ONNX_COMMON_FOLDER);
         if(ext_onnx_handle != INVALID_HANDLE)
         {{
            Print("✓ [ONNX Loaded]: Mode ONNX_COMMON_FOLDER from Common Files '", fn, "'");
            break;
         }}
      }}
   }}

   if(ext_onnx_handle == INVALID_HANDLE)
   {{
      int err = GetLastError();
      Print("❌ [ONNX Error]: Could not load ONNX model. Code: ", err);
      Print("👉 [Quick Solution]: Keep 'AlgoForge_Strategy_{rank}.onnx' in MT5/MQL5/Files/ and recompile this EA in MetaEditor (F7) to embed it.");
      return INIT_FAILED;
   }}

   // 3. Set input shape [1, WINDOW_SIZE, N_FEATURES]
   const long input_shape[] = {{ 1, WINDOW_SIZE, N_FEATURES }};
   if(!OnnxSetInputShape(ext_onnx_handle, 0, input_shape))
   {{
      Print("Error setting ONNX input shape: ", GetLastError());
      OnnxRelease(ext_onnx_handle);
      ext_onnx_handle = INVALID_HANDLE;
      return INIT_FAILED;
   }}

   // 4. Set output shape [1]
   const long output_shape[] = {{ 1 }};
   if(!OnnxSetOutputShape(ext_onnx_handle, 0, output_shape))
   {{
      Print("Error setting ONNX output shape: ", GetLastError());
      OnnxRelease(ext_onnx_handle);
      ext_onnx_handle = INVALID_HANDLE;
      return INIT_FAILED;
   }}

   // 5. Auxiliary ATR indicator
   handle_atr = iATR(_Symbol, _Period, InpATRPeriod);

   Print("AlgoForge Neural ONNX Agent successfully initialized on ", _Symbol);
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

   // Check Consecutive Losses Kill-Switch & Automatic Reactivation
   int current_consec_losses = GetConsecutiveLosses();
   if(IsBotHalted(current_consec_losses))
   {{
      Comment("AlgoForge RL EA: Paused due to ", current_consec_losses, " consecutive losses. Waiting for reactivation condition...");
      return;
   }}

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
            datetime pos_open_time = (datetime)PositionGetInteger(POSITION_TIME);
            int bars_in_trade = Bars(_Symbol, _Period, pos_open_time, iTime(_Symbol, _Period, 0));

            // Time-Based Exit (Max Holding Bars)
            if(InpMaxHoldingBars > 0 && bars_in_trade >= InpMaxHoldingBars)
            {{
               trade.PositionClose(ticket);
               continue;
            }}
            
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

      if((InpTradeDirection == DIR_BOTH || InpTradeDirection == DIR_LONG_ONLY) && buy_condition)
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

         double volume = GetTradeLotSize(sl_dist, current_consec_losses);
         trade.Buy(volume, _Symbol, ask, sl, tp, "AlgoForge RL Buy");
      }}
      else if((InpTradeDirection == DIR_BOTH || InpTradeDirection == DIR_SHORT_ONLY) && sell_condition)
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

         double volume = GetTradeLotSize(sl_dist, current_consec_losses);
         trade.Sell(volume, _Symbol, bid, sl, tp, "AlgoForge RL Sell");
      }}
   }}
}}
"""
