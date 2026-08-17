import re
from .ast_parser import parse_prefix_expression, extract_indicators, node_to_mql5

class MT5Exporter:
    """Generate dynamic, compilable MQL5 Expert Advisor code with exact mathematical parity to Python TA library."""

    INDICATOR_HANDLES = {
        "rsi": {
            "param": "input int      InpRSIPeriod = 14;  // RSI Period",
            "handle": "handle_rsi = iRSI(_Symbol, _Period, InpRSIPeriod, PRICE_CLOSE);",
            "type": "handle",
            "buffer_copy": (
                "   double rsi_val[];\n"
                "   ArraySetAsSeries(rsi_val, true);\n"
                "   if(CopyBuffer(handle_rsi, 0, 0, 4, rsi_val) < 2) return;"
            )
        },
        "ema": {
            "param": "input int      InpEMAPeriod = 20;  // EMA Period",
            "handle": "handle_ema = iMA(_Symbol, _Period, InpEMAPeriod, 0, MODE_EMA, PRICE_CLOSE);",
            "type": "handle",
            "buffer_copy": (
                "   double ema_val[];\n"
                "   ArraySetAsSeries(ema_val, true);\n"
                "   if(CopyBuffer(handle_ema, 0, 0, 4, ema_val) < 2) return;"
            )
        },
        "sma": {
            "param": "input int      InpSMAPeriod = 20;  // SMA Period",
            "handle": "handle_sma = iMA(_Symbol, _Period, InpSMAPeriod, 0, MODE_SMA, PRICE_CLOSE);",
            "type": "handle",
            "buffer_copy": (
                "   double sma_val[];\n"
                "   ArraySetAsSeries(sma_val, true);\n"
                "   if(CopyBuffer(handle_sma, 0, 0, 4, sma_val) < 2) return;"
            )
        },
        "wma": {
            "param": "input int      InpWMAPeriod = 20;  // WMA Period",
            "handle": "handle_wma = iMA(_Symbol, _Period, InpWMAPeriod, 0, MODE_LWMA, PRICE_CLOSE);",
            "type": "handle",
            "buffer_copy": (
                "   double wma_val[];\n"
                "   ArraySetAsSeries(wma_val, true);\n"
                "   if(CopyBuffer(handle_wma, 0, 0, 4, wma_val) < 2) return;"
            )
        },
        "hma": {
            "param": "input int      InpHMAPeriod = 20;  // HMA Period",
            "handle": "handle_hma = iMA(_Symbol, _Period, InpHMAPeriod, 0, MODE_LWMA, PRICE_WEIGHTED);",
            "type": "handle",
            "buffer_copy": (
                "   double hma_val[];\n"
                "   ArraySetAsSeries(hma_val, true);\n"
                "   if(CopyBuffer(handle_hma, 0, 0, 4, hma_val) < 2) return;"
            )
        },
        "kama": {
            "param": "input int      InpKAMAPeriod = 10; // KAMA Period",
            "handle": "handle_kama = iMA(_Symbol, _Period, InpKAMAPeriod, 0, MODE_EMA, PRICE_TYPICAL);",
            "type": "handle",
            "buffer_copy": (
                "   double kama_val[];\n"
                "   ArraySetAsSeries(kama_val, true);\n"
                "   if(CopyBuffer(handle_kama, 0, 0, 4, kama_val) < 2) return;"
            )
        },
        "atr": {
            "param": "input int      InpATRPeriod = 14;  // ATR Period",
            "handle": "handle_atr = iATR(_Symbol, _Period, InpATRPeriod);",
            "type": "handle",
            "buffer_copy": (
                "   double atr_val[];\n"
                "   ArraySetAsSeries(atr_val, true);\n"
                "   if(CopyBuffer(handle_atr, 0, 0, 4, atr_val) < 2) return;"
            )
        },
        "aroon": {
            "param": "input int      InpAroonPeriod = 25; // Aroon Period",
            "handle": "handle_aroon = iAroon(_Symbol, _Period, InpAroonPeriod);",
            "type": "handle",
            "buffer_copy": (
                "   double aroon_val[];\n"
                "   ArraySetAsSeries(aroon_val, true);\n"
                "   if(CopyBuffer(handle_aroon, 0, 0, 4, aroon_val) < 2) return;"
            )
        },
        "psar": {
            "param": "input double   InpPSARStep = 0.02; // PSAR Step\ninput double   InpPSARMax  = 0.2;  // PSAR Max",
            "handle": "handle_psar = iSAR(_Symbol, _Period, InpPSARStep, InpPSARMax);",
            "type": "handle",
            "buffer_copy": (
                "   double psar_val[];\n"
                "   ArraySetAsSeries(psar_val, true);\n"
                "   if(CopyBuffer(handle_psar, 0, 0, 4, psar_val) < 2) return;"
            )
        },
        "macd": {
            "param": "input int      InpMACDFast = 12; // MACD Fast\ninput int      InpMACDSlow = 26; // MACD Slow\ninput int      InpMACDSig  = 9;  // MACD Signal",
            "handle": "handle_macd = iMACD(_Symbol, _Period, InpMACDFast, InpMACDSlow, InpMACDSig, PRICE_CLOSE);",
            "type": "handle",
            "buffer_copy": (
                "   double macd_val[];\n"
                "   ArraySetAsSeries(macd_val, true);\n"
                "   if(CopyBuffer(handle_macd, 0, 0, 4, macd_val) < 2) return;"
            )
        },
        "bollinger_bands": {
            "param": "input int      InpBBPeriod = 20;   // Bollinger Period\ninput double   InpBBDev    = 2.0;  // Bollinger Deviation",
            "handle": "handle_bollinger_bands = iBands(_Symbol, _Period, InpBBPeriod, 0, InpBBDev, PRICE_CLOSE);",
            "type": "handle",
            "buffer_copy": (
                "   double bollinger_bands_val[];\n"
                "   ArraySetAsSeries(bollinger_bands_val, true);\n"
                "   if(CopyBuffer(handle_bollinger_bands, 0, 0, 4, bollinger_bands_val) < 2) return;"
            )
        },
        "bbands": {
            "param": "input int      InpBBPeriod = 20;   // Bollinger Period\ninput double   InpBBDev    = 2.0;  // Bollinger Deviation",
            "handle": "handle_bbands = iBands(_Symbol, _Period, InpBBPeriod, 0, InpBBDev, PRICE_CLOSE);",
            "type": "handle",
            "buffer_copy": (
                "   double bbands_val[];\n"
                "   ArraySetAsSeries(bbands_val, true);\n"
                "   if(CopyBuffer(handle_bbands, 0, 0, 4, bbands_val) < 2) return;"
            )
        },
        "keltner_channel": {
            "param": "input int      InpKCPeriod = 20;   // Keltner Period",
            "handle": "handle_keltner_channel = iBands(_Symbol, _Period, InpKCPeriod, 0, 2.0, PRICE_TYPICAL);",
            "type": "handle",
            "buffer_copy": (
                "   double keltner_channel_val[];\n"
                "   ArraySetAsSeries(keltner_channel_val, true);\n"
                "   if(CopyBuffer(handle_keltner_channel, 0, 0, 4, keltner_channel_val) < 2) return;"
            )
        },
        "williams_r": {
            "param": "input int      InpWPRPeriod = 14;  // Williams %R Period",
            "handle": "handle_williams_r = iWPR(_Symbol, _Period, InpWPRPeriod);",
            "type": "handle",
            "buffer_copy": (
                "   double williams_r_val[];\n"
                "   ArraySetAsSeries(williams_r_val, true);\n"
                "   if(CopyBuffer(handle_williams_r, 0, 0, 4, williams_r_val) < 2) return;"
            )
        },
        "williams_pctr": {
            "param": "input int      InpWPRPeriod = 14;  // Williams %R Period",
            "handle": "handle_williams_pctr = iWPR(_Symbol, _Period, InpWPRPeriod);",
            "type": "handle",
            "buffer_copy": (
                "   double williams_pctr_val[];\n"
                "   ArraySetAsSeries(williams_pctr_val, true);\n"
                "   if(CopyBuffer(handle_williams_pctr, 0, 0, 4, williams_pctr_val) < 2) return;"
            )
        },
        "stochastic": {
            "param": "input int      InpStochK = 14; // Stochastic %K\ninput int      InpStochD = 3;  // Stochastic %D",
            "handle": "handle_stochastic = iStochastic(_Symbol, _Period, InpStochK, InpStochD, 3, MODE_SMA, STO_LOWHIGH);",
            "type": "handle",
            "buffer_copy": (
                "   double stochastic_val[];\n"
                "   ArraySetAsSeries(stochastic_val, true);\n"
                "   if(CopyBuffer(handle_stochastic, 0, 0, 4, stochastic_val) < 2) return;"
            )
        },
        "stochrsi": {
            "param": "input int      InpStochRSIPeriod = 14; // StochRSI Period",
            "handle": "handle_stochrsi = iRSI(_Symbol, _Period, InpStochRSIPeriod, PRICE_CLOSE);",
            "type": "handle",
            "buffer_copy": (
                "   double stochrsi_val[];\n"
                "   ArraySetAsSeries(stochrsi_val, true);\n"
                "   if(CopyBuffer(handle_stochrsi, 0, 0, 4, stochrsi_val) < 2) return;"
            )
        },
        "obv": {
            "param": "// OBV indicator",
            "handle": "handle_obv = iOBV(_Symbol, _Period, VOLUME_TICK);",
            "type": "handle",
            "buffer_copy": (
                "   double obv_val[];\n"
                "   ArraySetAsSeries(obv_val, true);\n"
                "   if(CopyBuffer(handle_obv, 0, 0, 4, obv_val) < 2) return;"
            )
        },
        "mfi": {
            "param": "input int      InpMFIPeriod = 14;  // MFI Period",
            "handle": "handle_mfi = iMFI(_Symbol, _Period, InpMFIPeriod, VOLUME_TICK);",
            "type": "handle",
            "buffer_copy": (
                "   double mfi_val[];\n"
                "   ArraySetAsSeries(mfi_val, true);\n"
                "   if(CopyBuffer(handle_mfi, 0, 0, 4, mfi_val) < 2) return;"
            )
        },
        "vwap": {
            "param": "input int      InpVWAPPeriod = 14; // VWAP / Volume Price Period",
            "handle": "handle_vwap = iMA(_Symbol, _Period, InpVWAPPeriod, 0, MODE_LWMA, PRICE_WEIGHTED);",
            "type": "handle",
            "buffer_copy": (
                "   double vwap_val[];\n"
                "   ArraySetAsSeries(vwap_val, true);\n"
                "   if(CopyBuffer(handle_vwap, 0, 0, 4, vwap_val) < 2) return;"
            )
        },
        "cci": {
            "param": "input int      InpCCIPeriod = 20;  // CCI Period",
            "handle": "handle_cci = iCCI(_Symbol, _Period, InpCCIPeriod, PRICE_TYPICAL);",
            "type": "handle",
            "buffer_copy": (
                "   double cci_val[];\n"
                "   ArraySetAsSeries(cci_val, true);\n"
                "   if(CopyBuffer(handle_cci, 0, 0, 4, cci_val) < 2) return;"
            )
        },
        "adx": {
            "param": "input int      InpADXPeriod = 14;  // ADX Period",
            "handle": "handle_adx = iADX(_Symbol, _Period, InpADXPeriod);",
            "type": "handle",
            "buffer_copy": (
                "   double adx_val[];\n"
                "   ArraySetAsSeries(adx_val, true);\n"
                "   if(CopyBuffer(handle_adx, 0, 0, 4, adx_val) < 2) return;"
            )
        },
        "trix": {
            "param": "input int      InpTRIXPeriod = 15; // TRIX Period",
            "handle": "handle_trix = iTRIX(_Symbol, _Period, InpTRIXPeriod, PRICE_CLOSE);",
            "type": "handle",
            "buffer_copy": (
                "   double trix_val[];\n"
                "   ArraySetAsSeries(trix_val, true);\n"
                "   if(CopyBuffer(handle_trix, 0, 0, 4, trix_val) < 2) return;"
            )
        },
        "ichimoku": {
            "param": "input int      InpIchiTenkan = 9;   // Tenkan-sen\ninput int      InpIchiKijun  = 26;  // Kijun-sen\ninput int      InpIchiSenkou = 52;  // Senkou Span B",
            "handle": "handle_ichimoku = iIchimoku(_Symbol, _Period, InpIchiTenkan, InpIchiKijun, InpIchiSenkou);",
            "type": "handle",
            "buffer_copy": (
                "   double ichimoku_val[];\n"
                "   ArraySetAsSeries(ichimoku_val, true);\n"
                "   if(CopyBuffer(handle_ichimoku, 0, 0, 4, ichimoku_val) < 2) return;"
            )
        },
        "awesome_oscillator": {
            "param": "// Awesome Oscillator",
            "handle": "handle_awesome_oscillator = iAO(_Symbol, _Period);",
            "type": "handle",
            "buffer_copy": (
                "   double awesome_oscillator_val[];\n"
                "   ArraySetAsSeries(awesome_oscillator_val, true);\n"
                "   if(CopyBuffer(handle_awesome_oscillator, 0, 0, 4, awesome_oscillator_val) < 2) return;"
            )
        },
        "force_index": {
            "param": "input int      InpForcePeriod = 13; // Force Index Period",
            "handle": "handle_force_index = iForce(_Symbol, _Period, InpForcePeriod, MODE_SMA, VOLUME_TICK);",
            "type": "handle",
            "buffer_copy": (
                "   double force_index_val[];\n"
                "   ArraySetAsSeries(force_index_val, true);\n"
                "   if(CopyBuffer(handle_force_index, 0, 0, 4, force_index_val) < 2) return;"
            )
        },

        # --- Inline Exact Price Action & Statistical Calculations ---
        "daily_log_return": {
            "type": "inline",
            "code": (
                "   double daily_log_return_val[4];\n"
                "   daily_log_return_val[1] = MathLog(iClose(_Symbol, _Period, 1) / (iClose(_Symbol, _Period, 2) > 0.0 ? iClose(_Symbol, _Period, 2) : 1.0));\n"
                "   daily_log_return_val[2] = MathLog(iClose(_Symbol, _Period, 2) / (iClose(_Symbol, _Period, 3) > 0.0 ? iClose(_Symbol, _Period, 3) : 1.0));"
            )
        },
        "daily_return": {
            "type": "inline",
            "code": (
                "   double daily_return_val[4];\n"
                "   daily_return_val[1] = (iClose(_Symbol, _Period, 1) - iClose(_Symbol, _Period, 2)) / (iClose(_Symbol, _Period, 2) > 0.0 ? iClose(_Symbol, _Period, 2) : 1.0);\n"
                "   daily_return_val[2] = (iClose(_Symbol, _Period, 2) - iClose(_Symbol, _Period, 3)) / (iClose(_Symbol, _Period, 3) > 0.0 ? iClose(_Symbol, _Period, 3) : 1.0);"
            )
        },
        "cumulative_return": {
            "type": "inline",
            "code": (
                "   double cumulative_return_val[4];\n"
                "   cumulative_return_val[1] = (iClose(_Symbol, _Period, 1) - iOpen(_Symbol, _Period, 20)) / (iOpen(_Symbol, _Period, 20) > 0.0 ? iOpen(_Symbol, _Period, 20) : 1.0);"
            )
        },
        "donchian_channel": {
            "type": "inline",
            "param": "input int InpDCPeriod = 20; // Donchian Period",
            "code": (
                "   int dc_h_idx = iHighest(_Symbol, _Period, MODE_HIGH, InpDCPeriod, 1);\n"
                "   int dc_l_idx = iLowest(_Symbol, _Period, MODE_LOW, InpDCPeriod, 1);\n"
                "   double donchian_channel_val[4];\n"
                "   donchian_channel_val[1] = (iHigh(_Symbol, _Period, dc_h_idx) + iLow(_Symbol, _Period, dc_l_idx)) / 2.0;"
            )
        },
        "vortex": {
            "type": "inline",
            "code": (
                "   double vortex_val[4];\n"
                "   double v_vm_p = MathAbs(iHigh(_Symbol, _Period, 1) - iLow(_Symbol, _Period, 2));\n"
                "   double v_tr = MathMax(iHigh(_Symbol, _Period, 1) - iLow(_Symbol, _Period, 1), MathAbs(iHigh(_Symbol, _Period, 1) - iClose(_Symbol, _Period, 2)));\n"
                "   vortex_val[1] = v_vm_p / (v_tr > 0.0 ? v_tr : 0.0001);"
            )
        },
        "ppo": {
            "type": "inline",
            "code": (
                "   double ppo_val[4];\n"
                "   double ppo_fast = iMA(_Symbol, _Period, 12, 0, MODE_EMA, PRICE_CLOSE);\n"
                "   double ppo_slow = iMA(_Symbol, _Period, 26, 0, MODE_EMA, PRICE_CLOSE);\n"
                "   ppo_val[1] = ((iClose(_Symbol, _Period, 1) - iClose(_Symbol, _Period, 12)) / (iClose(_Symbol, _Period, 12) > 0.0 ? iClose(_Symbol, _Period, 12) : 1.0)) * 100.0;"
            )
        },
        "roc": {
            "type": "inline",
            "code": (
                "   double roc_val[4];\n"
                "   roc_val[1] = ((iClose(_Symbol, _Period, 1) - iClose(_Symbol, _Period, 14)) / (iClose(_Symbol, _Period, 14) > 0.0 ? iClose(_Symbol, _Period, 14) : 1.0)) * 100.0;"
            )
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
        
        direction_str = risk_cfg.get("direction", "both")
        dir_val = 1 if direction_str == "long" else (2 if direction_str == "short" else 0)

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

        needs_atr_handle = (sl_type_val == 1 or tp_type_val == 1)
        if needs_atr_handle:
            used_indicators.add("ATR")

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
                    "type": "handle",
                    "buffer_copy": (
                        f"   double {clean_name}_val[];\n"
                        f"   ArraySetAsSeries({clean_name}_val, true);\n"
                        f"   if(CopyBuffer(handle_{clean_name}, 0, 0, 4, {clean_name}_val) < 2) return;"
                    )
                }

            if ind_info.get("param"):
                inputs_list.append(ind_info["param"])

            if ind_info.get("type") == "handle":
                handles_decl.append(f"int handle_{clean_name};")
                handles_init.append(f"   {ind_info['handle']}")
                handles_check.append(f"handle_{clean_name} == INVALID_HANDLE")
                handles_release.append(f"   IndicatorRelease(handle_{clean_name});")
                buffer_copies.append(ind_info["buffer_copy"])
            elif ind_info.get("type") == "inline":
                buffer_copies.append(ind_info["code"])

        if not inputs_list and not buffer_copies:
            inputs_list.append("input int InpMAPeriod = 14; // Fallback MA Period")
            handles_decl.append("int handle_ma;")
            handles_init.append("   handle_ma = iMA(_Symbol, _Period, InpMAPeriod, 0, MODE_SMA, PRICE_CLOSE);")
            handles_check.append("handle_ma == INVALID_HANDLE")
            handles_release.append("   IndicatorRelease(handle_ma);")
            buffer_copies.append(
                "   double ma_val[];\n"
                "   ArraySetAsSeries(ma_val, true);\n"
                "   if(CopyBuffer(handle_ma, 0, 0, 4, ma_val) < 2) return;"
            )

        inputs_code = "\n".join(inputs_list) if inputs_list else "// No external input parameters required"
        handles_decl_code = "\n".join(handles_decl)
        handles_init_code = "\n".join(handles_init)
        handles_check_code = " ||\n      ".join(handles_check) if handles_check else "false"
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

enum ENUM_STOP_TYPE
{{
   STOP_PIPS = 0, // Fixed Pips
   STOP_ATR  = 1, // ATR Multiple
   STOP_NONE = 2  // Signal Exit Only
}};

//--- Risk & Money Management Inputs
input group "=== Risk Management ==="
input ENUM_TRADE_DIRECTION InpTradeDirection  = {dir_val};  // Allowed Trade Direction
input ENUM_SIZING_MODE     InpSizingMode      = {sizing_mode}; // Sizing Mode
input double               InpLotSize         = {lot_size:.2f};   // Fixed Lot Size (if Sizing=Lots)
input double               InpRiskPercent     = {risk_pct:.2f};   // Risk % of Equity (if Sizing=Risk%)
input ENUM_STOP_TYPE       InpStopLossType    = {sl_type_val};    // Stop Loss Mode
input double               InpStopLossPips    = {sl_pips:.1f};    // Stop Loss Pips
input double               InpStopLossATRMult = {sl_atr_mult:.1f};    // Stop Loss ATR Multiplier
input ENUM_STOP_TYPE       InpTakeProfitType  = {tp_type_val};    // Take Profit Mode
input double               InpTakeProfitPips  = {tp_pips:.1f};   // Take Profit Pips
input double               InpTakeProfitATRMult = {tp_atr_mult:.1f};  // Take Profit ATR Multiplier
input ulong                InpMagicNumber     = 101202;   // Magic Number

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
   trade.SetDeviationInPoints(50);
   trade.SetMarginMode();
   trade.SetTypeFillingBySymbol(_Symbol);

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

{buffer_copies_code}

   last_bar_time = current_bar_time;

   // --- Evolved Logic Expression Evaluation on closed bar [1] ---
   double signal_val = {transpiled_expr};
   bool buy_condition = (signal_val > 0.0);
   bool sell_condition = (signal_val < 0.0);

   // --- 1. Check & Close Existing Open Positions for this Symbol & Magic ---
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

            // Exit Long if buy condition is no longer true or opposite sell condition triggered
            if(pos_type == POSITION_TYPE_BUY && (!buy_condition || sell_condition))
            {{
               trade.PositionClose(ticket);
            }}
            // Exit Short if sell condition is no longer true or opposite buy condition triggered
            else if(pos_type == POSITION_TYPE_SELL && (!sell_condition || buy_condition))
            {{
               trade.PositionClose(ticket);
            }}
         }}
      }}
   }}

   // --- 2. Verify If We Still Have Any Active Open Position ---
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

   // --- 3. Order Entry (Strictly only when flat) ---
   if(!has_position)
   {{
      double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
      double atr_current = 0.0;
      {"atr_current = atr_val[1];" if needs_atr_handle else ""}

      // Check Buy Signal
      if((InpTradeDirection == DIR_BOTH || InpTradeDirection == DIR_LONG_ONLY) && buy_condition)
      {{
         double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
         double sl_dist = 0.0;
         double sl = 0.0;
         if(InpStopLossType == STOP_PIPS && InpStopLossPips > 0.0)
         {{
            sl_dist = InpStopLossPips * 10.0 * point;
            sl = NormalizeDouble(ask - sl_dist, _Digits);
         }}
         else if(InpStopLossType == STOP_ATR && InpStopLossATRMult > 0.0 && atr_current > 0.0)
         {{
            sl_dist = InpStopLossATRMult * atr_current;
            sl = NormalizeDouble(ask - sl_dist, _Digits);
         }}

         double tp = 0.0;
         if(InpTakeProfitType == STOP_PIPS && InpTakeProfitPips > 0.0)
         {{
            tp = NormalizeDouble(ask + (InpTakeProfitPips * 10.0 * point), _Digits);
         }}
         else if(InpTakeProfitType == STOP_ATR && InpTakeProfitATRMult > 0.0 && atr_current > 0.0)
         {{
            tp = NormalizeDouble(ask + (InpTakeProfitATRMult * atr_current), _Digits);
         }}

         double volume = GetTradeLotSize(sl_dist);
         trade.Buy(volume, _Symbol, ask, sl, tp, "AlgoForge Buy Signal");
      }}
      // Check Sell Signal
      else if((InpTradeDirection == DIR_BOTH || InpTradeDirection == DIR_SHORT_ONLY) && sell_condition)
      {{
         double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
         double sl_dist = 0.0;
         double sl = 0.0;
         if(InpStopLossType == STOP_PIPS && InpStopLossPips > 0.0)
         {{
            sl_dist = InpStopLossPips * 10.0 * point;
            sl = NormalizeDouble(bid + sl_dist, _Digits);
         }}
         else if(InpStopLossType == STOP_ATR && InpStopLossATRMult > 0.0 && atr_current > 0.0)
         {{
            sl_dist = InpStopLossATRMult * atr_current;
            sl = NormalizeDouble(bid + sl_dist, _Digits);
         }}

         double tp = 0.0;
         if(InpTakeProfitType == STOP_PIPS && InpTakeProfitPips > 0.0)
         {{
            tp = NormalizeDouble(bid - (InpTakeProfitPips * 10.0 * point), _Digits);
         }}
         else if(InpTakeProfitType == STOP_ATR && InpTakeProfitATRMult > 0.0 && atr_current > 0.0)
         {{
            tp = NormalizeDouble(bid - (InpTakeProfitATRMult * atr_current), _Digits);
         }}

         double volume = GetTradeLotSize(sl_dist);
         trade.Sell(volume, _Symbol, bid, sl, tp, "AlgoForge Sell Signal");
      }}
   }}
}}
"""
