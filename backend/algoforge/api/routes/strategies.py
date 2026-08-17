import numpy as np
from fastapi import APIRouter, Depends
from algoforge.api.deps import get_supabase
from algoforge.services.export_service import _LOCAL_STRATEGIES

router = APIRouter()

SUMMARY_COLUMNS = (
    "id, job_id, user_id, rank, total_score, sharpe_ratio, "
    "total_return_pct, max_drawdown_pct, win_rate, profit_factor, "
    "n_trades, mc_robustness, mc_prob_ruin, mc_95_drawdown, "
    "strategy_tree, created_at"
)

@router.get("")
def list_strategies(job_id: str, db = Depends(get_supabase)):
    """Fetch strategy list summary fast without transferring megabytes of raw trade logs."""
    try:
        res = db.table("strategies").select(SUMMARY_COLUMNS).eq("job_id", job_id).order("rank", desc=False).execute()
        if res.data and len(res.data) > 0:
            for s in res.data:
                s["is_rl"] = "RL_Agent" in str(s.get("strategy_tree", ""))
            return res.data
    except Exception as e:
        print(f"[List strategies DB notice]: {e}")
    
    # Fallback to local memory
    local = [s for s in _LOCAL_STRATEGIES.values() if s.get("job_id") == job_id]
    if local:
        local.sort(key=lambda x: x.get("rank", 999))
        return [
            {k: v for k, v in s.items() if k not in ("equity_curve", "trade_log")}
            for s in local
        ]
    return []

@router.get("/{strategy_id}")
def get_strategy(strategy_id: str, db = Depends(get_supabase)):
    """Fetch complete strategy detail with unpacked MT5 tester metrics and trade logs."""
    strat = None
    try:
        res = db.table("strategies").select("*").eq("id", strategy_id).single().execute()
        if res.data:
            strat = res.data
    except Exception as e:
        print(f"[Get strategy DB notice]: {e}")
    
    if not strat and strategy_id in _LOCAL_STRATEGIES:
        strat = dict(_LOCAL_STRATEGIES[strategy_id])

    if strat:
        strat["is_rl"] = strat.get("is_rl", False) or "RL_Agent" in str(strat.get("strategy_tree", ""))
        
        # Unpack detailed metrics stored inside exit_rules JSONB
        exit_rules = strat.get("exit_rules") or {}
        if isinstance(exit_rules, dict) and "detailed_metrics" in exit_rules:
            for k, v in exit_rules["detailed_metrics"].items():
                if k not in strat or strat[k] is None:
                    strat[k] = v

        # If detailed metrics are still missing and trade_log exists, compute dynamically
        trade_log = strat.get("trade_log") or []
        if isinstance(trade_log, list) and len(trade_log) > 0 and (strat.get("gross_profit") is None or strat.get("gross_profit") == 0):
            pnls = [float(t.get("pnl", 0.0)) for t in trade_log]
            gross_p = sum(p for p in pnls if p > 0)
            gross_l = abs(sum(p for p in pnls if p < 0))
            net_p = sum(pnls)
            n_tr = len(pnls)

            strat["gross_profit"] = round(gross_p, 2)
            strat["gross_loss"] = round(gross_l, 2)
            strat["expected_payoff"] = round(net_p / max(1, n_tr), 2)

            curr_w = curr_l = max_w = max_l = 0
            curr_w_cash = curr_l_cash = max_w_cash = max_l_cash = 0.0
            w_streaks, l_streaks = [], []
            for p in pnls:
                if p > 0:
                    curr_w += 1
                    curr_w_cash += p
                    if curr_l > 0:
                        l_streaks.append(curr_l)
                        curr_l = curr_l_cash = 0
                    if curr_w > max_w: max_w = curr_w
                    if curr_w_cash > max_w_cash: max_w_cash = curr_w_cash
                elif p < 0:
                    curr_l += 1
                    curr_l_cash += abs(p)
                    if curr_w > 0:
                        w_streaks.append(curr_w)
                        curr_w = curr_w_cash = 0
                    if curr_l > max_l: max_l = curr_l
                    if curr_l_cash > max_l_cash: max_l_cash = curr_l_cash
            if curr_w > 0: w_streaks.append(curr_w)
            if curr_l > 0: l_streaks.append(curr_l)

            strat["consecutive_wins_max"] = max_w
            strat["consecutive_wins_max_cash"] = round(max_w_cash, 2)
            strat["consecutive_losses_max"] = max_l
            strat["consecutive_losses_max_cash"] = round(max_l_cash, 2)
            strat["consecutive_wins_avg"] = round(float(np.mean(w_streaks)), 1) if w_streaks else 1.0
            strat["consecutive_losses_avg"] = round(float(np.mean(l_streaks)), 1) if l_streaks else 1.0
            strat["recovery_factor"] = round(net_p / max(1.0, float(strat.get("max_drawdown_pct", 10.0))), 2)

        # Cap trade log payload to max 100 items for instant response
        if "trade_log" in strat and isinstance(strat["trade_log"], list) and len(strat["trade_log"]) > 100:
            strat["trade_log"] = strat["trade_log"][:100]
            
        return strat

    return {}
