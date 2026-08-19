import re
from .ast_parser import parse_prefix_expression, extract_indicators, node_to_mql5

class MT5Exporter:
    """Generate dynamic, compilable MQL5 Expert Advisor code with exact mathematical parity to Python TA library."""

    @classmethod
    def _build_indicator_info(cls, base_name: str, var_name: str, params: dict) -> dict:
        p = params or {}
        b = base_name.lower().replace(" ", "_").replace("%", "pct").replace("-", "_")

        # === 1. MOMENTUM ===
        if b in ["rsi"]:
            period = int(p.get("window", p.get("period", 14)))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // RSI Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Momentum\\\\RSI\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["stochastic", "stoch"]:
            k = int(p.get("window", p.get("k", 14)))
            d = int(p.get("smooth_window", p.get("d", 3)))
            slow = int(p.get("slowing", p.get("slow", 3)))
            return {
                "param": f"input int Inp_{var_name}_K = {k}; // Stoch %K\ninput int Inp_{var_name}_D = {d}; // Stoch %D\ninput int Inp_{var_name}_Slow = {slow}; // Stoch Slowing",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Momentum\\\\Stochastic\", Inp_{var_name}_K, Inp_{var_name}_D, Inp_{var_name}_Slow);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["stochrsi", "stoch_rsi"]:
            rsi_p = int(p.get("window", p.get("rsi_period", 14)))
            stoch_p = int(p.get("smooth1", p.get("period", 14)))
            return {
                "param": f"input int Inp_{var_name}_RSIPeriod = {rsi_p}; // StochRSI RSI Period\ninput int Inp_{var_name}_Period = {stoch_p}; // StochRSI Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Momentum\\\\StochRSI\", Inp_{var_name}_RSIPeriod, Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["tsi"]:
            slow = int(p.get("window_slow", p.get("slow", 25)))
            fast = int(p.get("window_fast", p.get("fast", 13)))
            return {
                "param": f"input int Inp_{var_name}_Slow = {slow}; // TSI Slow\ninput int Inp_{var_name}_Fast = {fast}; // TSI Fast",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Momentum\\\\TSI\", Inp_{var_name}_Slow, Inp_{var_name}_Fast);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["ultimate_oscillator", "ultimateoscillator", "ultimate"]:
            p1 = int(p.get("window1", 7))
            p2 = int(p.get("window2", 14))
            p3 = int(p.get("window3", 28))
            return {
                "param": f"input int Inp_{var_name}_P1 = {p1}; // UO Period 1\ninput int Inp_{var_name}_P2 = {p2}; // UO Period 2\ninput int Inp_{var_name}_P3 = {p3}; // UO Period 3",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Momentum\\\\UltimateOscillator\", Inp_{var_name}_P1, Inp_{var_name}_P2, Inp_{var_name}_P3);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["williams_r", "williams_pctr", "williams_pct_r", "willr", "wpr", "williamsr"]:
            period = int(p.get("lbp", p.get("window", p.get("period", 14))))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // Williams %R Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Momentum\\\\WilliamsR\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["awesome_oscillator", "awesomeoscillator", "ao"]:
            fast = int(p.get("window1", 5))
            slow = int(p.get("window2", 34))
            return {
                "param": f"input int Inp_{var_name}_Fast = {fast}; // AO Fast\ninput int Inp_{var_name}_Slow = {slow}; // AO Slow",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Momentum\\\\AO\", Inp_{var_name}_Fast, Inp_{var_name}_Slow);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["kama"]:
            period = int(p.get("window", 10))
            fast = int(p.get("pow1", 2))
            slow = int(p.get("pow2", 30))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // KAMA Period\ninput int Inp_{var_name}_Fast = {fast}; // KAMA Fast\ninput int Inp_{var_name}_Slow = {slow}; // KAMA Slow",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Momentum\\\\KAMA\", Inp_{var_name}_Period, Inp_{var_name}_Fast, Inp_{var_name}_Slow);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["roc"]:
            period = int(p.get("window", p.get("period", 12)))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // ROC Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Momentum\\\\ROC\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["ppo"]:
            fast = int(p.get("window_fast", 12))
            slow = int(p.get("window_slow", 26))
            sig = int(p.get("window_sign", 9))
            return {
                "param": f"input int Inp_{var_name}_Fast = {fast}; // PPO Fast\ninput int Inp_{var_name}_Slow = {slow}; // PPO Slow\ninput int Inp_{var_name}_Sig = {sig}; // PPO Signal",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Momentum\\\\PPO\", Inp_{var_name}_Fast, Inp_{var_name}_Slow, Inp_{var_name}_Sig);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 2, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["pvo"]:
            fast = int(p.get("window_fast", 12))
            slow = int(p.get("window_slow", 26))
            sig = int(p.get("window_sign", 9))
            return {
                "param": f"input int Inp_{var_name}_Fast = {fast}; // PVO Fast\ninput int Inp_{var_name}_Slow = {slow}; // PVO Slow\ninput int Inp_{var_name}_Sig = {sig}; // PVO Signal",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Momentum\\\\PVO\", Inp_{var_name}_Fast, Inp_{var_name}_Slow, Inp_{var_name}_Sig);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 2, 0, 4, {var_name}_val) < 2) return;"
                )
            }

        # === 2. TREND ===
        elif b in ["macd"]:
            fast = int(p.get("window_fast", p.get("fast", 12)))
            slow = int(p.get("window_slow", p.get("slow", 26)))
            sig = int(p.get("window_sign", p.get("signal", 9)))
            return {
                "param": f"input int Inp_{var_name}_Fast = {fast}; // MACD Fast\ninput int Inp_{var_name}_Slow = {slow}; // MACD Slow\ninput int Inp_{var_name}_Sig = {sig}; // MACD Signal",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Trend\\\\MACD\", Inp_{var_name}_Fast, Inp_{var_name}_Slow, Inp_{var_name}_Sig);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 2, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["sma"]:
            period = int(p.get("window", p.get("period", p.get("length", 10))))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // SMA Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Trend\\\\SMA\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["ema"]:
            period = int(p.get("window", p.get("period", p.get("length", 10))))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // EMA Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Trend\\\\EMA\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["wma"]:
            period = int(p.get("window", p.get("period", p.get("length", 9))))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // WMA Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Trend\\\\WMA\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["hma"]:
            period = int(p.get("window", p.get("period", p.get("length", 20))))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // HMA Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Trend\\\\HMA\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["adx"]:
            period = int(p.get("window", p.get("period", 14)))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // ADX Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Trend\\\\ADX\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["aroon"]:
            period = int(p.get("window", p.get("length", 25)))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // Aroon Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Trend\\\\Aroon\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_up[], {var_name}_dn[];\n"
                    f"   ArraySetAsSeries({var_name}_up, true);\n"
                    f"   ArraySetAsSeries({var_name}_dn, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_up) < 2) return;\n"
                    f"   if(CopyBuffer(handle_{var_name}, 1, 0, 4, {var_name}_dn) < 2) return;\n"
                    f"   double {var_name}_val[4];\n"
                    f"   for(int i=0; i<4; i++) {var_name}_val[i] = {var_name}_up[i] - {var_name}_dn[i];"
                )
            }
        elif b in ["cci"]:
            period = int(p.get("window", p.get("period", 20)))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // CCI Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Trend\\\\CCI\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["psar"]:
            step = float(p.get("step", 0.02))
            max_step = float(p.get("max_step", 0.2))
            return {
                "param": f"input double Inp_{var_name}_Step = {step:.3f}; // PSAR Step\ninput double Inp_{var_name}_MaxStep = {max_step:.3f}; // PSAR Max",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Trend\\\\PSAR\", Inp_{var_name}_Step, Inp_{var_name}_MaxStep);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["ichimoku"]:
            tenkan = int(p.get("window1", 9))
            kijun = int(p.get("window2", 26))
            senkou = int(p.get("window3", 52))
            return {
                "param": f"input int Inp_{var_name}_Tenkan = {tenkan}; // Tenkan\ninput int Inp_{var_name}_Kijun = {kijun}; // Kijun\ninput int Inp_{var_name}_Senkou = {senkou}; // Senkou",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Trend\\\\Ichimoku\", Inp_{var_name}_Tenkan, Inp_{var_name}_Kijun, Inp_{var_name}_Senkou);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 1, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["kst"]:
            return {
                "param": f"input int Inp_{var_name}_Signal = 9; // KST Signal",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Trend\\\\KST\", 10, 15, 20, 30, 10, 10, 10, 15, Inp_{var_name}_Signal);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["dpo"]:
            period = int(p.get("window", 20))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // DPO Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Trend\\\\DPO\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["trix"]:
            period = int(p.get("window", 15))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // TRIX Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Trend\\\\TRIX\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["mass_index", "massindex"]:
            fast = int(p.get("window_fast", 9))
            slow = int(p.get("window_slow", 25))
            return {
                "param": f"input int Inp_{var_name}_Fast = {fast}; // Mass Index Fast\ninput int Inp_{var_name}_Slow = {slow}; // Mass Index Slow",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Trend\\\\MassIndex\", Inp_{var_name}_Fast, Inp_{var_name}_Slow);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["vortex"]:
            period = int(p.get("window", 14))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // Vortex Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Trend\\\\Vortex\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_p[], {var_name}_m[];\n"
                    f"   ArraySetAsSeries({var_name}_p, true);\n"
                    f"   ArraySetAsSeries({var_name}_m, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_p) < 2) return;\n"
                    f"   if(CopyBuffer(handle_{var_name}, 1, 0, 4, {var_name}_m) < 2) return;\n"
                    f"   double {var_name}_val[4];\n"
                    f"   for(int i=0; i<4; i++) {var_name}_val[i] = {var_name}_p[i] - {var_name}_m[i];"
                )
            }
        elif b in ["stc"]:
            slow = int(p.get("window_slow", 50))
            fast = int(p.get("window_fast", 23))
            cycle = int(p.get("cycle", 10))
            return {
                "param": f"input int Inp_{var_name}_Slow = {slow}; // STC Slow\ninput int Inp_{var_name}_Fast = {fast}; // STC Fast\ninput int Inp_{var_name}_Cycle = {cycle}; // STC Cycle",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Trend\\\\STC\", Inp_{var_name}_Slow, Inp_{var_name}_Fast, Inp_{var_name}_Cycle, 3, 3);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }

        # === 3. VOLATILITY ===
        elif b in ["atr"]:
            period = int(p.get("window", p.get("period", 14)))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // ATR Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Volatility\\\\ATR\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["bollinger_bands", "bbands", "bollinger"]:
            period = int(p.get("window", p.get("period", 20)))
            dev = float(p.get("window_dev", p.get("std", p.get("deviation", 2.0))))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // Bollinger Period\ninput double Inp_{var_name}_Dev = {dev:.2f}; // Bollinger Dev",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Volatility\\\\Bollinger\", Inp_{var_name}_Period, Inp_{var_name}_Dev);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_mid[], {var_name}_upper[], {var_name}_lower[], {var_name}_close[];\n"
                    f"   ArraySetAsSeries({var_name}_mid, true);\n"
                    f"   ArraySetAsSeries({var_name}_upper, true);\n"
                    f"   ArraySetAsSeries({var_name}_lower, true);\n"
                    f"   ArraySetAsSeries({var_name}_close, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_mid) < 2) return;\n"
                    f"   if(CopyBuffer(handle_{var_name}, 1, 0, 4, {var_name}_upper) < 2) return;\n"
                    f"   if(CopyBuffer(handle_{var_name}, 2, 0, 4, {var_name}_lower) < 2) return;\n"
                    f"   if(CopyClose(_Symbol, _Period, 0, 4, {var_name}_close) < 2) return;\n"
                    f"   double {var_name}_val[4];\n"
                    f"   for(int i=0; i<4; i++) {{\n"
                    f"       double diff = {var_name}_upper[i] - {var_name}_lower[i];\n"
                    f"       if(diff != 0) {var_name}_val[i] = ({var_name}_close[i] - {var_name}_lower[i]) / diff;\n"
                    f"       else {var_name}_val[i] = 0;\n"
                    f"   }}"
                )
            }
        elif b in ["donchian_channel", "dc", "donchian"]:
            period = int(p.get("window", p.get("period", 20)))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // Donchian Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Volatility\\\\Donchian\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_upper[], {var_name}_lower[], {var_name}_close[];\n"
                    f"   ArraySetAsSeries({var_name}_upper, true);\n"
                    f"   ArraySetAsSeries({var_name}_lower, true);\n"
                    f"   ArraySetAsSeries({var_name}_close, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_upper) < 2) return;\n"
                    f"   if(CopyBuffer(handle_{var_name}, 1, 0, 4, {var_name}_lower) < 2) return;\n"
                    f"   if(CopyClose(_Symbol, _Period, 0, 4, {var_name}_close) < 2) return;\n"
                    f"   double {var_name}_val[4];\n"
                    f"   for(int i=0; i<4; i++) {{\n"
                    f"       double diff = {var_name}_upper[i] - {var_name}_lower[i];\n"
                    f"       if(diff != 0) {var_name}_val[i] = ({var_name}_close[i] - {var_name}_lower[i]) / diff;\n"
                    f"       else {var_name}_val[i] = 0;\n"
                    f"   }}"
                )
            }
        elif b in ["keltner_channel", "kc", "keltner"]:
            period = int(p.get("window", p.get("period", 20)))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // Keltner Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Volatility\\\\Keltner\", Inp_{var_name}_Period, true);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_upper[], {var_name}_lower[], {var_name}_close[];\n"
                    f"   ArraySetAsSeries({var_name}_upper, true);\n"
                    f"   ArraySetAsSeries({var_name}_lower, true);\n"
                    f"   ArraySetAsSeries({var_name}_close, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 1, 0, 4, {var_name}_upper) < 2) return;\n"
                    f"   if(CopyBuffer(handle_{var_name}, 2, 0, 4, {var_name}_lower) < 2) return;\n"
                    f"   if(CopyClose(_Symbol, _Period, 0, 4, {var_name}_close) < 2) return;\n"
                    f"   double {var_name}_val[4];\n"
                    f"   for(int i=0; i<4; i++) {{\n"
                    f"       double diff = {var_name}_upper[i] - {var_name}_lower[i];\n"
                    f"       if(diff != 0) {var_name}_val[i] = ({var_name}_close[i] - {var_name}_lower[i]) / diff;\n"
                    f"       else {var_name}_val[i] = 0;\n"
                    f"   }}"
                )
            }
        elif b in ["ulcer_index", "ui", "ulcerindex"]:
            period = int(p.get("window", 14))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // Ulcer Index Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Volatility\\\\UlcerIndex\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }

        # === 4. VOLUME ===
        elif b in ["adi"]:
            return {
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Volume\\\\ADI\");",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["cmf"]:
            period = int(p.get("window", 20))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // CMF Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Volume\\\\CMF\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["ease_of_movement", "eom"]:
            period = int(p.get("window", 14))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // EoM Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Volume\\\\EoM\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["force_index", "forceindex"]:
            period = int(p.get("window", 13))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // Force Index Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Volume\\\\ForceIndex\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["mfi"]:
            period = int(p.get("window", 14))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // MFI Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Volume\\\\MFI\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["nvi"]:
            return {
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Volume\\\\NVI\");",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["obv"]:
            return {
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Volume\\\\OBV\");",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["vpt"]:
            return {
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Volume\\\\VPT\");",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["vwap"]:
            period = int(p.get("window", 14))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // VWAP Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Volume\\\\VWAP\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }

        # === 5. OTHERS ===
        elif b in ["daily_return", "dailyreturn"]:
            return {
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Others\\\\DailyReturn\");",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["daily_log_return", "dailylogreturn"]:
            return {
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Others\\\\DailyLogReturn\");",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["cumulative_return", "cumulativereturn"]:
            return {
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Others\\\\CumulativeReturn\");",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        elif b in ["close", "open", "high", "low", "volume", "tick_volume"]:
            # Raw price/volume series read directly from the chart. Parity with
            # IndicatorCalculator.calculate_single (no transformation). Never
            # fall through to an iCustom EMA approximation.
            copy_func = {
                "close": "CopyClose", "open": "CopyOpen", "high": "CopyHigh",
                "low": "CopyLow", "volume": "CopyTickVolume",
                "tick_volume": "CopyTickVolume"
            }[b]
            return {
                "type": "inline",
                "code": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if({copy_func}(_Symbol, _Period, 0, 4, {var_name}_val) < 2) return;"
                )
            }
        else:
            period = int(p.get("window", p.get("period", 14)))
            return {
                "param": f"input int Inp_{var_name}_Period = {period}; // {var_name} Period",
                "handle": f"handle_{var_name} = iCustom(_Symbol, _Period, \"AlgoForge\\\\Trend\\\\EMA\", Inp_{var_name}_Period);",
                "type": "handle",
                "buffer_copy": (
                    f"   double {var_name}_val[];\n"
                    f"   ArraySetAsSeries({var_name}_val, true);\n"
                    f"   if(CopyBuffer(handle_{var_name}, 0, 0, 4, {var_name}_val) < 2) return;"
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
        max_trades = int(risk_cfg.get("maxSimultaneousTrades") or risk_cfg.get("max_simultaneous_trades") or 1)
        
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
            base_name = re.sub(r"_v\d+$", "", clean_name)
            params = ind_param_map.get(raw_ind) or ind_param_map.get(clean_name) or ind_param_map.get(raw_ind.lower()) or {}
            ind_info = self._build_indicator_info(base_name, clean_name, params)

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
input int                     InpMaxSimultaneousTrades = {max_trades}; // Max Simultaneous Positions

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
            int bars_alive = Bars(_Symbol, _Period, setup_time, iTime(_Symbol, _Period, 0)) - 1;
            if(InpPendingTimeoutBars > 0 && bars_alive >= InpPendingTimeoutBars)
            {{
               trade.OrderDelete(order_ticket);
            }}
         }}
      }}
   }}

   // --- Evolved Logic Expression Evaluation on closed bar [1] ---
   double signal_val = {transpiled_expr};
   // Parity with the Python simulator: entries use strictly positive signals,
   // exits use <= 0 (a value of exactly 0 exits the long and opens the short).
   bool buy_condition = (signal_val > 0.0);
   bool sell_condition = (signal_val <= 0.0);

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
            // Bars() counts both boundary bars; subtract 1 so bars_in_trade
            // matches the simulator's (bar index - entry index) convention.
            int bars_in_trade = Bars(_Symbol, _Period, pos_open_time, iTime(_Symbol, _Period, 0)) - 1;

            // Time-Based Exit (Max Holding Bars)
            if(InpMaxHoldingBars > 0 && bars_in_trade >= InpMaxHoldingBars)
            {{
               trade.PositionClose(ticket);
               continue;
            }}

            // Exit Long only if opposite sell condition triggered
            if(pos_type == POSITION_TYPE_BUY && sell_condition)
            {{
               trade.PositionClose(ticket);
            }}
            // Exit Short only if opposite buy condition triggered
            else if(pos_type == POSITION_TYPE_SELL && buy_condition)
            {{
               trade.PositionClose(ticket);
            }}
         }}
      }}
   }}

   // --- 2. Verify How Many Open Positions / Pending Orders We Have ---
   // Parity with the simulator: new entries are allowed while
   // positions + pendings < InpMaxSimultaneousTrades (one entry per bar).
   int position_count = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {{
      ulong ticket = PositionGetTicket(i);
      if(ticket > 0)
      {{
         string pos_symbol = PositionGetString(POSITION_SYMBOL);
         ulong  pos_magic  = (ulong)PositionGetInteger(POSITION_MAGIC);
         if(pos_symbol == _Symbol && (pos_magic == InpMagicNumber || InpMagicNumber == 0))
            position_count++;
      }}
   }}
   int pending_count = 0;
   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {{
      ulong ticket = OrderGetTicket(i);
      if(ticket > 0)
      {{
         string ord_symbol = OrderGetString(ORDER_SYMBOL);
         ulong  ord_magic  = (ulong)OrderGetInteger(ORDER_MAGIC);
         if(ord_symbol == _Symbol && (ord_magic == InpMagicNumber || InpMagicNumber == 0))
            pending_count++;
      }}
   }}

   // --- 3. Order Entry (only while capacity remains) ---
   if(position_count + pending_count < InpMaxSimultaneousTrades)
   {{
      double point = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
      // 1 pip = 10 points on 3/5-digit quotes (0.00001 on 5-digit EURUSD,
      // 0.001 on 3-digit JPY), and 1 point on 4-digit quotes.
      double pip_size = (_Digits == 3 || _Digits == 5) ? point * 10.0 : point;
      double atr_current = 0.0;
      {"atr_current = atr_val[1];" if needs_atr_handle else ""}

      // Check Buy Signal
      if((InpTradeDirection == DIR_BOTH || InpTradeDirection == DIR_LONG_ONLY) && buy_condition)
      {{
         double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
         double target_order_price = ask;

         if(InpOrderExecution == EXEC_STOP)
            target_order_price = NormalizeDouble(iHigh(_Symbol, _Period, 1) + (InpPendingOffsetPips * pip_size), _Digits);
         else if(InpOrderExecution == EXEC_LIMIT)
            target_order_price = NormalizeDouble(iLow(_Symbol, _Period, 1) - (InpPendingOffsetPips * pip_size), _Digits);

         double sl_dist = 0.0;
         double sl = 0.0;
         if(InpStopLossType == STOP_PIPS && InpStopLossPips > 0.0)
         {{
            sl_dist = InpStopLossPips * pip_size;
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
            tp = NormalizeDouble(target_order_price + (InpTakeProfitPips * pip_size), _Digits);
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
            target_order_price = NormalizeDouble(iLow(_Symbol, _Period, 1) - (InpPendingOffsetPips * pip_size), _Digits);
         else if(InpOrderExecution == EXEC_LIMIT)
            target_order_price = NormalizeDouble(iHigh(_Symbol, _Period, 1) + (InpPendingOffsetPips * pip_size), _Digits);

         double sl_dist = 0.0;
         double sl = 0.0;
         if(InpStopLossType == STOP_PIPS && InpStopLossPips > 0.0)
         {{
            sl_dist = InpStopLossPips * pip_size;
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
            tp = NormalizeDouble(target_order_price - (InpTakeProfitPips * pip_size), _Digits);
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
