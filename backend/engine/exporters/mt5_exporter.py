import re
from .ast_parser import parse_prefix_expression, extract_indicators, node_to_mql5

class MT5Exporter:
    """Generate dynamic, compilable MQL5 Expert Advisor code with exact mathematical parity to Python TA library."""

    @classmethod
    def _build_indicator_info(cls, clean_name: str, raw_ind: str, params: dict) -> dict:
        p = params or {}
        
        if clean_name == "rsi":
            period = int(p.get("window", p.get("period", 14)))
            return {
                "param": f"input int      InpRSIPeriod = {period};  // RSI Period",
                "handle": "handle_rsi = iRSI(_Symbol, _Period, InpRSIPeriod, PRICE_CLOSE);",
                "type": "handle",
                "buffer_copy": (
                    "   double rsi_val[];\n"
                    "   ArraySetAsSeries(rsi_val, true);\n"
                    "   if(CopyBuffer(handle_rsi, 0, 0, 4, rsi_val) < 2) return;"
                )
            }
        elif clean_name == "ema":
            period = int(p.get("window", p.get("period", p.get("length", 20))))
            return {
                "param": f"input int      InpEMAPeriod = {period};  // EMA Period",
                "handle": "handle_ema = iMA(_Symbol, _Period, InpEMAPeriod, 0, MODE_EMA, PRICE_CLOSE);",
                "type": "handle",
                "buffer_copy": (
                    "   double ema_val[];\n"
                    "   ArraySetAsSeries(ema_val, true);\n"
                    "   if(CopyBuffer(handle_ema, 0, 0, 4, ema_val) < 2) return;"
                )
            }
        elif clean_name == "sma":
            period = int(p.get("window", p.get("period", p.get("length", 20))))
            return {
                "param": f"input int      InpSMAPeriod = {period};  // SMA Period",
                "handle": "handle_sma = iMA(_Symbol, _Period, InpSMAPeriod, 0, MODE_SMA, PRICE_CLOSE);",
                "type": "handle",
                "buffer_copy": (
                    "   double sma_val[];\n"
                    "   ArraySetAsSeries(sma_val, true);\n"
                    "   if(CopyBuffer(handle_sma, 0, 0, 4, sma_val) < 2) return;"
                )
            }
        elif clean_name == "wma":
            period = int(p.get("window", p.get("period", p.get("length", 20))))
            return {
                "param": f"input int      InpWMAPeriod = {period};  // WMA Period",
                "handle": "handle_wma = iMA(_Symbol, _Period, InpWMAPeriod, 0, MODE_LWMA, PRICE_CLOSE);",
                "type": "handle",
                "buffer_copy": (
                    "   double wma_val[];\n"
                    "   ArraySetAsSeries(wma_val, true);\n"
                    "   if(CopyBuffer(handle_wma, 0, 0, 4, wma_val) < 2) return;"
                )
            }
        elif clean_name == "hma":
            period = int(p.get("window", p.get("period", p.get("length", 20))))
            return {
                "param": f"input int      InpHMAPeriod = {period};  // HMA Period",
                "handle": "handle_hma = iMA(_Symbol, _Period, InpHMAPeriod, 0, MODE_LWMA, PRICE_WEIGHTED);",
                "type": "handle",
                "buffer_copy": (
                    "   double hma_val[];\n"
                    "   ArraySetAsSeries(hma_val, true);\n"
                    "   if(CopyBuffer(handle_hma, 0, 0, 4, hma_val) < 2) return;"
                )
            }
        elif clean_name == "kama":
            period = int(p.get("window", p.get("period", 10)))
            return {
                "param": f"input int      InpKAMAPeriod = {period}; // KAMA Period",
                "handle": "handle_kama = iMA(_Symbol, _Period, InpKAMAPeriod, 0, MODE_EMA, PRICE_TYPICAL);",
                "type": "handle",
                "buffer_copy": (
                    "   double kama_val[];\n"
                    "   ArraySetAsSeries(kama_val, true);\n"
                    "   if(CopyBuffer(handle_kama, 0, 0, 4, kama_val) < 2) return;"
                )
            }
        elif clean_name == "atr":
            period = int(p.get("window", p.get("period", 14)))
            return {
                "param": f"input int      InpATRPeriod = {period};  // ATR Period",
                "handle": "handle_atr = iATR(_Symbol, _Period, InpATRPeriod);",
                "type": "handle",
                "buffer_copy": (
                    "   double atr_val[];\n"
                    "   ArraySetAsSeries(atr_val, true);\n"
                    "   if(CopyBuffer(handle_atr, 0, 0, 4, atr_val) < 2) return;"
                )
            }
        elif clean_name == "aroon":
            period = int(p.get("window", p.get("period", 25)))
            return {
                "param": f"input int      InpAroonPeriod = {period}; // Aroon Period",
                "handle": "handle_aroon = iAroon(_Symbol, _Period, InpAroonPeriod);",
                "type": "handle",
                "buffer_copy": (
                    "   double aroon_val[];\n"
                    "   ArraySetAsSeries(aroon_val, true);\n"
                    "   if(CopyBuffer(handle_aroon, 0, 0, 4, aroon_val) < 2) return;"
                )
            }
        elif clean_name == "psar":
            step = float(p.get("step", p.get("af0", 0.02)))
            max_step = float(p.get("max_step", p.get("max_af", 0.2)))
            return {
                "param": f"input double   InpPSARStep = {step:.3f}; // PSAR Step\ninput double   InpPSARMax  = {max_step:.3f};  // PSAR Max",
                "handle": "handle_psar = iSAR(_Symbol, _Period, InpPSARStep, InpPSARMax);",
                "type": "handle",
                "buffer_copy": (
                    "   double psar_val[];\n"
                    "   ArraySetAsSeries(psar_val, true);\n"
                    "   if(CopyBuffer(handle_psar, 0, 0, 4, psar_val) < 2) return;"
                )
            }
        elif clean_name == "macd":
            fast = int(p.get("window_fast", p.get("fast", 12)))
            slow = int(p.get("window_slow", p.get("slow", 26)))
            sig = int(p.get("window_sign", p.get("signal", 9)))
            return {
                "param": f"input int      InpMACDFast = {fast}; // MACD Fast\ninput int      InpMACDSlow = {slow}; // MACD Slow\ninput int      InpMACDSig  = {sig};  // MACD Signal",
                "handle": "handle_macd = iMACD(_Symbol, _Period, InpMACDFast, InpMACDSlow, InpMACDSig, PRICE_CLOSE);",
                "type": "handle",
                "buffer_copy": (
                    "   double macd_val[];\n"
                    "   ArraySetAsSeries(macd_val, true);\n"
                    "   if(CopyBuffer(handle_macd, 0, 0, 4, macd_val) < 2) return;"
                )
            }
        elif clean_name in ["bollinger_bands", "bbands"]:
            period = int(p.get("window", p.get("period", 20)))
            dev = float(p.get("window_dev", p.get("std", p.get("deviation", 2.0))))
            return {
                "param": f"input int      InpBBPeriod = {period};   // Bollinger Period\ninput double   InpBBDev    = {dev:.2f};  // Bollinger Deviation",
                "handle": "handle_bbands = iBands(_Symbol, _Period, InpBBPeriod, 0, InpBBDev, PRICE_CLOSE);",
                "type": "handle",
                "buffer_copy": (
                    "   double bbands_val[];\n"
                    "   ArraySetAsSeries(bbands_val, true);\n"
                    "   if(CopyBuffer(handle_bbands, 0, 0, 4, bbands_val) < 2) return;"
                )
            }
        elif clean_name in ["keltner_channel", "kc"]:
            period = int(p.get("window", p.get("period", 20)))
            mult = float(p.get("multiplier", p.get("scalar", p.get("deviation", 2.0))))
            return {
                "param": f"input int      InpKCPeriod = {period};   // Keltner Period\ninput double   InpKCDev    = {mult:.2f}; // Keltner Multiplier",
                "handle": "handle_keltner_channel = iBands(_Symbol, _Period, InpKCPeriod, 0, InpKCDev, PRICE_TYPICAL);",
                "type": "handle",
                "buffer_copy": (
                    "   double keltner_channel_val[];\n"
                    "   ArraySetAsSeries(keltner_channel_val, true);\n"
                    "   if(CopyBuffer(handle_keltner_channel, 0, 0, 4, keltner_channel_val) < 2) return;"
                )
            }
        elif clean_name in ["williams_r", "williams_pctr", "willr"]:
            period = int(p.get("lbp", p.get("window", p.get("period", 14))))
            return {
                "param": f"input int      InpWPRPeriod = {period};  // Williams %R Period",
                "handle": "handle_williams_r = iWPR(_Symbol, _Period, InpWPRPeriod);",
                "type": "handle",
                "buffer_copy": (
                    "   double williams_r_val[];\n"
                    "   ArraySetAsSeries(williams_r_val, true);\n"
                    "   if(CopyBuffer(handle_williams_r, 0, 0, 4, williams_r_val) < 2) return;"
                )
            }
        elif clean_name in ["stochastic", "stoch"]:
            k = int(p.get("window", p.get("k_period", p.get("k", 14))))
            d = int(p.get("smooth_window", p.get("d_period", p.get("d", 3))))
            slowing = int(p.get("slowing", 3))
            return {
                "param": f"input int      InpStochK = {k}; // Stochastic %K\ninput int      InpStochD = {d};  // Stochastic %D\ninput int      InpStochSlowing = {slowing}; // Stochastic Slowing",
                "handle": "handle_stochastic = iStochastic(_Symbol, _Period, InpStochK, InpStochD, InpStochSlowing, MODE_SMA, STO_LOWHIGH);",
                "type": "handle",
                "buffer_copy": (
                    "   double stochastic_val[];\n"
                    "   ArraySetAsSeries(stochastic_val, true);\n"
                    "   if(CopyBuffer(handle_stochastic, 0, 0, 4, stochastic_val) < 2) return;"
                )
            }
        elif clean_name == "stochrsi":
            period = int(p.get("window", p.get("period", 14)))
            return {
                "param": f"input int      InpStochRSIPeriod = {period}; // StochRSI Period",
                "handle": "handle_stochrsi = iRSI(_Symbol, _Period, InpStochRSIPeriod, PRICE_CLOSE);",
                "type": "handle",
                "buffer_copy": (
                    "   double stochrsi_val[];\n"
                    "   ArraySetAsSeries(stochrsi_val, true);\n"
                    "   if(CopyBuffer(handle_stochrsi, 0, 0, 4, stochrsi_val) < 2) return;"
                )
            }
        elif clean_name == "obv":
            return {
                "param": "// OBV indicator (Volume Tick)",
                "handle": "handle_obv = iOBV(_Symbol, _Period, VOLUME_TICK);",
                "type": "handle",
                "buffer_copy": (
                    "   double obv_val[];\n"
                    "   ArraySetAsSeries(obv_val, true);\n"
                    "   if(CopyBuffer(handle_obv, 0, 0, 4, obv_val) < 2) return;"
                )
            }
        elif clean_name == "mfi":
            period = int(p.get("window", p.get("period", 14)))
            return {
                "param": f"input int      InpMFIPeriod = {period};  // MFI Period",
                "handle": "handle_mfi = iMFI(_Symbol, _Period, InpMFIPeriod, VOLUME_TICK);",
                "type": "handle",
                "buffer_copy": (
                    "   double mfi_val[];\n"
                    "   ArraySetAsSeries(mfi_val, true);\n"
                    "   if(CopyBuffer(handle_mfi, 0, 0, 4, mfi_val) < 2) return;"
                )
            }
        elif clean_name == "vwap":
            period = int(p.get("window", p.get("period", 14)))
            return {
                "param": f"input int      InpVWAPPeriod = {period}; // VWAP Period",
                "handle": "handle_vwap = iMA(_Symbol, _Period, InpVWAPPeriod, 0, MODE_LWMA, PRICE_WEIGHTED);",
                "type": "handle",
                "buffer_copy": (
                    "   double vwap_val[];\n"
                    "   ArraySetAsSeries(vwap_val, true);\n"
                    "   if(CopyBuffer(handle_vwap, 0, 0, 4, vwap_val) < 2) return;"
                )
            }
        elif clean_name == "cci":
            period = int(p.get("window", p.get("period", 20)))
            return {
                "param": f"input int      InpCCIPeriod = {period};  // CCI Period",
                "handle": "handle_cci = iCCI(_Symbol, _Period, InpCCIPeriod, PRICE_TYPICAL);",
                "type": "handle",
                "buffer_copy": (
                    "   double cci_val[];\n"
                    "   ArraySetAsSeries(cci_val, true);\n"
                    "   if(CopyBuffer(handle_cci, 0, 0, 4, cci_val) < 2) return;"
                )
            }
        elif clean_name == "adx":
            period = int(p.get("window", p.get("period", 14)))
            return {
                "param": f"input int      InpADXPeriod = {period};  // ADX Period",
                "handle": "handle_adx = iADX(_Symbol, _Period, InpADXPeriod);",
                "type": "handle",
                "buffer_copy": (
                    "   double adx_val[];\n"
                    "   ArraySetAsSeries(adx_val, true);\n"
                    "   if(CopyBuffer(handle_adx, 0, 0, 4, adx_val) < 2) return;"
                )
            }
        elif clean_name == "trix":
            period = int(p.get("window", p.get("period", 15)))
            return {
                "param": f"input int      InpTRIXPeriod = {period}; // TRIX Period",
                "handle": "handle_trix = iTRIX(_Symbol, _Period, InpTRIXPeriod, PRICE_CLOSE);",
                "type": "handle",
                "buffer_copy": (
                    "   double trix_val[];\n"
                    "   ArraySetAsSeries(trix_val, true);\n"
                    "   if(CopyBuffer(handle_trix, 0, 0, 4, trix_val) < 2) return;"
                )
            }
        elif clean_name == "ichimoku":
            tenkan = int(p.get("window1", p.get("tenkan", 9)))
            kijun = int(p.get("window2", p.get("kijun", 26)))
            senkou = int(p.get("window3", p.get("senkou", 52)))
            return {
                "param": f"input int      InpIchiTenkan = {tenkan};   // Tenkan-sen\ninput int      InpIchiKijun  = {kijun};  // Kijun-sen\ninput int      InpIchiSenkou = {senkou};  // Senkou Span B",
                "handle": "handle_ichimoku = iIchimoku(_Symbol, _Period, InpIchiTenkan, InpIchiKijun, InpIchiSenkou);",
                "type": "handle",
                "buffer_copy": (
                    "   double ichimoku_val[];\n"
                    "   ArraySetAsSeries(ichimoku_val, true);\n"
                    "   if(CopyBuffer(handle_ichimoku, 0, 0, 4, ichimoku_val) < 2) return;"
                )
            }
        elif clean_name == "awesome_oscillator":
            return {
                "param": "// Awesome Oscillator",
                "handle": "handle_awesome_oscillator = iAO(_Symbol, _Period);",
                "type": "handle",
                "buffer_copy": (
                    "   double awesome_oscillator_val[];\n"
                    "   ArraySetAsSeries(awesome_oscillator_val, true);\n"
                    "   if(CopyBuffer(handle_awesome_oscillator, 0, 0, 4, awesome_oscillator_val) < 2) return;"
                )
            }
        elif clean_name == "force_index":
            period = int(p.get("window", p.get("period", 13)))
            return {
                "param": f"input int      InpForcePeriod = {period}; // Force Index Period",
                "handle": "handle_force_index = iForce(_Symbol, _Period, InpForcePeriod, MODE_SMA, VOLUME_TICK);",
                "type": "handle",
                "buffer_copy": (
                    "   double force_index_val[];\n"
                    "   ArraySetAsSeries(force_index_val, true);\n"
                    "   if(CopyBuffer(handle_force_index, 0, 0, 4, force_index_val) < 2) return;"
                )
            }
        elif clean_name in ["donchian_channel", "dc"]:
            period = int(p.get("window", p.get("period", 20)))
            return {
                "type": "inline",
                "param": f"input int InpDCPeriod = {period}; // Donchian Period",
                "code": (
                    f"   int dc_h_idx = iHighest(_Symbol, _Period, MODE_HIGH, InpDCPeriod, 1);\n"
                    f"   int dc_l_idx = iLowest(_Symbol, _Period, MODE_LOW, InpDCPeriod, 1);\n"
                    f"   double donchian_channel_val[4];\n"
                    f"   donchian_channel_val[1] = (iHigh(_Symbol, _Period, dc_h_idx) + iLow(_Symbol, _Period, dc_l_idx)) / 2.0;"
                )
            }
        elif clean_name == "daily_log_return":
            return {
                "type": "inline",
                "code": (
                    "   double daily_log_return_val[4];\n"
                    "   daily_log_return_val[1] = MathLog(iClose(_Symbol, _Period, 1) / (iClose(_Symbol, _Period, 2) > 0.0 ? iClose(_Symbol, _Period, 2) : 1.0));\n"
                    "   daily_log_return_val[2] = MathLog(iClose(_Symbol, _Period, 2) / (iClose(_Symbol, _Period, 3) > 0.0 ? iClose(_Symbol, _Period, 3) : 1.0));"
                )
            }
        elif clean_name == "daily_return":
            return {
                "type": "inline",
                "code": (
                    "   double daily_return_val[4];\n"
                    "   daily_return_val[1] = (iClose(_Symbol, _Period, 1) - iClose(_Symbol, _Period, 2)) / (iClose(_Symbol, _Period, 2) > 0.0 ? iClose(_Symbol, _Period, 2) : 1.0);\n"
                    "   daily_return_val[2] = (iClose(_Symbol, _Period, 2) - iClose(_Symbol, _Period, 3)) / (iClose(_Symbol, _Period, 3) > 0.0 ? iClose(_Symbol, _Period, 3) : 1.0);"
                )
            }
        elif clean_name == "cumulative_return":
            return {
                "type": "inline",
                "code": (
                    "   double cumulative_return_val[4];\n"
                    "   cumulative_return_val[1] = (iClose(_Symbol, _Period, 1) - iOpen(_Symbol, _Period, 20)) / (iOpen(_Symbol, _Period, 20) > 0.0 ? iOpen(_Symbol, _Period, 20) : 1.0);"
                )
            }
        elif clean_name == "vortex":
            return {
                "type": "inline",
                "code": (
                    "   double vortex_val[4];\n"
                    "   double v_vm_p = MathAbs(iHigh(_Symbol, _Period, 1) - iLow(_Symbol, _Period, 2));\n"
                    "   double v_tr = MathMax(iHigh(_Symbol, _Period, 1) - iLow(_Symbol, _Period, 1), MathAbs(iHigh(_Symbol, _Period, 1) - iClose(_Symbol, _Period, 2)));\n"
                    "   vortex_val[1] = v_vm_p / (v_tr > 0.0 ? v_tr : 0.0001);"
                )
            }
        elif clean_name == "ppo":
            return {
                "type": "inline",
                "code": (
                    "   double ppo_val[4];\n"
                    "   double ppo_fast = iMA(_Symbol, _Period, 12, 0, MODE_EMA, PRICE_CLOSE);\n"
                    "   double ppo_slow = iMA(_Symbol, _Period, 26, 0, MODE_EMA, PRICE_CLOSE);\n"
                    "   ppo_val[1] = ((iClose(_Symbol, _Period, 1) - iClose(_Symbol, _Period, 12)) / (iClose(_Symbol, _Period, 12) > 0.0 ? iClose(_Symbol, _Period, 12) : 1.0)) * 100.0;"
                )
            }
        elif clean_name == "roc":
            period = int(p.get("window", p.get("period", 14)))
            return {
                "type": "inline",
                "code": (
                    f"   double roc_val[4];\n"
                    f"   roc_val[1] = ((iClose(_Symbol, _Period, 1) - iClose(_Symbol, _Period, {period})) / (iClose(_Symbol, _Period, {period}) > 0.0 ? iClose(_Symbol, _Period, {period}) : 1.0)) * 100.0;"
                )
            }
        else:
            period = int(p.get("window", p.get("period", 14)))
            return {
                "param": f"input int      Inp_{clean_name}_Period = {period}; // {raw_ind} Period",
                "handle": f"handle_{clean_name} = iMA(_Symbol, _Period, Inp_{clean_name}_Period, 0, MODE_EMA, PRICE_CLOSE);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {clean_name}_val[];\n"
                    f"   ArraySetAsSeries({clean_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{clean_name}, 0, 0, 4, {clean_name}_val) < 2) return;"
                )
            }

    def export(self, strategy: dict) -> str:
        rank = strategy.get("rank", 1)
        name = strategy.get("id", f"AlgoForge_Strategy_{rank}")
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
        tree_str = strategy.get("strategy_tree", "")

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

        # Build indicator parameters dictionary
        ind_configs = strategy.get("indicator_config") or []
        ind_param_map = {}
        if isinstance(ind_configs, list):
            for item in ind_configs:
                if isinstance(item, dict):
                    i_name = str(item.get("name", "")).lower().replace(" ", "_").replace("%", "pct")
                    ind_param_map[i_name] = item.get("params", {})
        elif isinstance(ind_configs, dict):
            for k, v in ind_configs.items():
                i_name = str(k).lower().replace(" ", "_").replace("%", "pct")
                ind_param_map[i_name] = v if isinstance(v, dict) else {}

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
            params = ind_param_map.get(clean_name) or ind_param_map.get(raw_ind.lower()) or {}
            ind_info = self._build_indicator_info(clean_name, raw_ind, params)

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
//| Strategy Rank: #{rank}           Strategy ID: {name}
//| Symbol: {symbol}     Timeframe: {timeframe}
//| Total Net Profit: ${net_profit:.2f} | Total Return: {total_return:.2f}%
//| Win Rate: {win_rate:.2f}% | Profit Factor: {profit_factor:.2f} | Total Trades: {n_trades}
//| Sharpe Ratio: {sharpe:.2f} | Max Drawdown: {max_dd:.2f}%
//| Monte Carlo Robustness: {mc_score:.1f}% | Prob of Ruin: {mc_ruin:.2f}%
//| MC 95% Confidence Drawdown: {mc_95_dd:.2f}%
//| Evolved Logic: {tree_str}
//+------------------------------------------------------------------+
#property copyright "AlgoForge AI"
#property link      "https://algoforge.io"
#property version   "1.00"
#property description "AlgoForge Strategy #{rank} - Win Rate: {win_rate:.2f}%, Sharpe: {sharpe:.2f}, MC Robustness: {mc_score:.1f}%"
#property strict

#include <Trade\\Trade.mqh>

enum ENUM_TRADE_DIRECTION
{{
   DIR_BOTH       = 0, // Long & Short
   DIR_LONG_ONLY  = 1, // Long Only
   DIR_SHORT_ONLY = 2  // Short Only
}};

enum ENUM_ORDER_EXECUTION
{{
   EXEC_ON_MARKET = 0, // On Market (Instant Execution)
   EXEC_STOP      = 1, // Buy Stop / Sell Stop
   EXEC_LIMIT     = 2  // Buy Limit / Sell Limit
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
input ENUM_ORDER_EXECUTION    InpOrderExecution       = {order_exec_val}; // Order Execution Mode
input int                     InpPendingTimeoutBars   = {pending_timeout}; // Cancel Pending Orders After X Bars
input double                  InpPendingOffsetPips    = {pending_offset:.1f}; // Pending Order Price Offset (Pips)
input int                     InpMaxHoldingBars       = {max_holding_bars}; // Max Holding Bars (0 = Disabled)
input ENUM_CONSEC_LOSS_ACTION InpConsecLossAction     = {consec_action_val}; // Consecutive Losses Protection
input int                     InpConsecLossThreshold  = {consec_threshold}; // Consecutive Losses Trigger (X)
input double                  InpConsecLossReduction  = {consec_reduction:.1f}; // Risk / Lot Reduction % (if Reduce Mode)
input ENUM_REACTIVATION_MODE  InpReactivationMode     = {reactivation_val}; // Auto-Reactivation Rule (if Paused)
input int                     InpCooldownBars         = {cooldown_bars}; // Cooldown Bars (if Mode=Bars)
input int                     InpCooldownDays         = {cooldown_days}; // Cooldown Days (if Mode=Days)
input ENUM_SIZING_MODE        InpSizingMode           = {sizing_mode}; // Sizing Mode
input double                  InpLotSize              = {lot_size:.2f};   // Fixed Lot Size (if Sizing=Lots)
input double                  InpRiskPercent          = {risk_pct:.2f};   // Risk % of Equity (if Sizing=Risk%)
input ENUM_STOP_TYPE          InpStopLossType         = {sl_type_val};    // Stop Loss Mode
input double                  InpStopLossPips         = {sl_pips:.1f};    // Stop Loss Pips
input double                  InpStopLossATRMult      = {sl_atr_mult:.1f};    // Stop Loss ATR Multiplier
input ENUM_STOP_TYPE          InpTakeProfitType       = {tp_type_val};    // Take Profit Mode
input double                  InpTakeProfitPips       = {tp_pips:.1f};   // Take Profit Pips
input double                  InpTakeProfitATRMult    = {tp_atr_mult:.1f};  // Take Profit ATR Multiplier
input ulong                   InpMagicNumber          = 101202;   // Magic Number

input group "=== Technical Indicator Parameters ==="
{inputs_code}

//--- Global Objects & Handles
CTrade trade;
{handles_decl_code}

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

   // --- Check Consecutive Losses Kill-Switch & Automatic Reactivation ---
   int current_consec_losses = GetConsecutiveLosses();
   if(IsBotHalted(current_consec_losses))
   {{
      Comment("AlgoForge EA: Paused due to ", current_consec_losses, " consecutive losses. Waiting for reactivation condition...");
      return;
   }}

   // --- Clean up / Cancel expired Pending Orders after X Bars ---
   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {{
      ulong order_ticket = OrderGetTicket(i);
      if(order_ticket > 0)
      {{
         string ord_symbol = OrderGetString(ORDER_SYMBOL);
         ulong  ord_magic  = (ulong)OrderGetInteger(ORDER_MAGIC);
         if(ord_symbol == _Symbol && (ord_magic == InpMagicNumber || InpMagicNumber == 0))
         {{
            datetime setup_time = (datetime)OrderGetInteger(ORDER_TIME_SETUP);
            int bars_alive = Bars(_Symbol, _Period, setup_time, iTime(_Symbol, _Period, 0));
            if(InpPendingTimeoutBars > 0 && bars_alive >= InpPendingTimeoutBars)
            {{
               trade.OrderDelete(order_ticket);
            }}
         }}
      }}
   }}

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
            datetime pos_open_time = (datetime)PositionGetInteger(POSITION_TIME);
            int bars_in_trade = Bars(_Symbol, _Period, pos_open_time, iTime(_Symbol, _Period, 0));

            // Time-Based Exit (Max Holding Bars)
            if(InpMaxHoldingBars > 0 && bars_in_trade >= InpMaxHoldingBars)
            {{
               trade.PositionClose(ticket);
               continue;
            }}

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

   // --- 2. Verify If We Still Have Any Active Open Position or Pending Order ---
   bool has_position_or_order = false;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {{
      ulong ticket = PositionGetTicket(i);
      if(ticket > 0)
      {{
         string pos_symbol = PositionGetString(POSITION_SYMBOL);
         ulong  pos_magic  = (ulong)PositionGetInteger(POSITION_MAGIC);
         if(pos_symbol == _Symbol && (pos_magic == InpMagicNumber || InpMagicNumber == 0))
         {{
            has_position_or_order = true;
            break;
         }}
      }}
   }}
   if(!has_position_or_order)
   {{
      for(int i = OrdersTotal() - 1; i >= 0; i--)
      {{
         ulong ticket = OrderGetTicket(i);
         if(ticket > 0)
         {{
            string ord_symbol = OrderGetString(ORDER_SYMBOL);
            ulong  ord_magic  = (ulong)OrderGetInteger(ORDER_MAGIC);
            if(ord_symbol == _Symbol && (ord_magic == InpMagicNumber || InpMagicNumber == 0))
            {{
               has_position_or_order = true;
               break;
            }}
         }}
      }}
   }}

   // --- 3. Order Entry (Strictly only when flat and no pending order) ---
   if(!has_position_or_order)
   {{
      double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
      double atr_current = 0.0;
      {"atr_current = atr_val[1];" if needs_atr_handle else ""}

      // Check Buy Signal
      if((InpTradeDirection == DIR_BOTH || InpTradeDirection == DIR_LONG_ONLY) && buy_condition)
      {{
         double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
         double target_order_price = ask;

         if(InpOrderExecution == EXEC_STOP)
            target_order_price = NormalizeDouble(iHigh(_Symbol, _Period, 1) + (InpPendingOffsetPips * 10.0 * point), _Digits);
         else if(InpOrderExecution == EXEC_LIMIT)
            target_order_price = NormalizeDouble(iLow(_Symbol, _Period, 1) - (InpPendingOffsetPips * 10.0 * point), _Digits);

         double sl_dist = 0.0;
         double sl = 0.0;
         if(InpStopLossType == STOP_PIPS && InpStopLossPips > 0.0)
         {{
            sl_dist = InpStopLossPips * 10.0 * point;
            sl = NormalizeDouble(target_order_price - sl_dist, _Digits);
         }}
         else if(InpStopLossType == STOP_ATR && InpStopLossATRMult > 0.0 && atr_current > 0.0)
         {{
            sl_dist = InpStopLossATRMult * atr_current;
            sl = NormalizeDouble(target_order_price - sl_dist, _Digits);
         }}

         double tp = 0.0;
         if(InpTakeProfitType == STOP_PIPS && InpTakeProfitPips > 0.0)
         {{
            tp = NormalizeDouble(target_order_price + (InpTakeProfitPips * 10.0 * point), _Digits);
         }}
         else if(InpTakeProfitType == STOP_ATR && InpTakeProfitATRMult > 0.0 && atr_current > 0.0)
         {{
            tp = NormalizeDouble(target_order_price + (InpTakeProfitATRMult * atr_current), _Digits);
         }}

         double volume = GetTradeLotSize(sl_dist, current_consec_losses);

         if(InpOrderExecution == EXEC_STOP)
            trade.BuyStop(volume, target_order_price, _Symbol, sl, tp, ORDER_TIME_GTC, 0, "AlgoForge Buy Stop");
         else if(InpOrderExecution == EXEC_LIMIT)
            trade.BuyLimit(volume, target_order_price, _Symbol, sl, tp, ORDER_TIME_GTC, 0, "AlgoForge Buy Limit");
         else
            trade.Buy(volume, _Symbol, ask, sl, tp, "AlgoForge Buy Signal");
      }}
      // Check Sell Signal
      else if((InpTradeDirection == DIR_BOTH || InpTradeDirection == DIR_SHORT_ONLY) && sell_condition)
      {{
         double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
         double target_order_price = bid;

         if(InpOrderExecution == EXEC_STOP)
            target_order_price = NormalizeDouble(iLow(_Symbol, _Period, 1) - (InpPendingOffsetPips * 10.0 * point), _Digits);
         else if(InpOrderExecution == EXEC_LIMIT)
            target_order_price = NormalizeDouble(iHigh(_Symbol, _Period, 1) + (InpPendingOffsetPips * 10.0 * point), _Digits);

         double sl_dist = 0.0;
         double sl = 0.0;
         if(InpStopLossType == STOP_PIPS && InpStopLossPips > 0.0)
         {{
            sl_dist = InpStopLossPips * 10.0 * point;
            sl = NormalizeDouble(target_order_price + sl_dist, _Digits);
         }}
         else if(InpStopLossType == STOP_ATR && InpStopLossATRMult > 0.0 && atr_current > 0.0)
         {{
            sl_dist = InpStopLossATRMult * atr_current;
            sl = NormalizeDouble(target_order_price + sl_dist, _Digits);
         }}

         double tp = 0.0;
         if(InpTakeProfitType == STOP_PIPS && InpTakeProfitPips > 0.0)
         {{
            tp = NormalizeDouble(target_order_price - (InpTakeProfitPips * 10.0 * point), _Digits);
         }}
         else if(InpTakeProfitType == STOP_ATR && InpTakeProfitATRMult > 0.0 && atr_current > 0.0)
         {{
            tp = NormalizeDouble(target_order_price - (InpTakeProfitATRMult * atr_current), _Digits);
         }}

         double volume = GetTradeLotSize(sl_dist, current_consec_losses);

         if(InpOrderExecution == EXEC_STOP)
            trade.SellStop(volume, target_order_price, _Symbol, sl, tp, ORDER_TIME_GTC, 0, "AlgoForge Sell Stop");
         else if(InpOrderExecution == EXEC_LIMIT)
            trade.SellLimit(volume, target_order_price, _Symbol, sl, tp, ORDER_TIME_GTC, 0, "AlgoForge Sell Limit");
         else
            trade.Sell(volume, _Symbol, bid, sl, tp, "AlgoForge Sell Signal");
      }}
   }}
}}
"""
