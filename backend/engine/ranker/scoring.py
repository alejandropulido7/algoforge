class StrategyRanker:
    """Ranks generated trading strategies using a multi-objective weighted composite score."""

    WEIGHTS = {
        "sharpe": 0.25,
        "mc_robustness": 0.25,
        "return": 0.15,
        "drawdown": 0.15,
        "win_rate": 0.10,
        "profit_factor": 0.10,
    }

    def rank(self, strategies: list[dict]) -> list[dict]:
        """Rank and enrich strategies with scores and rank order."""
        scored = []
        for s in strategies:
            sharpe = float(s.get("sharpe_ratio", 0.0) or 0.0)
            ret = float(s.get("total_return_pct", 0.0) or 0.0)
            dd = float(s.get("max_drawdown_pct", 0.0) or 0.0)
            win_rate = float(s.get("win_rate", 0.0) or 0.0)
            pf = float(s.get("profit_factor", 1.0) or 1.0)
            mc_rob = float(s.get("mc_robustness", 50.0) or 50.0)

            # Normalization (0-1) where percentage fields are 0-100
            norm_sharpe = min(max(sharpe / 3.0, 0.0), 1.0)
            norm_mc = min(max(mc_rob / 100.0, 0.0), 1.0)
            norm_ret = min(max(ret / 100.0, 0.0), 1.0)
            norm_dd = 1.0 - min(max(dd / 100.0, 0.0), 1.0)
            norm_wr = min(max(win_rate / 100.0, 0.0), 1.0)
            norm_pf = min(max((pf - 1.0) / 3.0, 0.0), 1.0)

            total_score = (
                self.WEIGHTS["sharpe"] * norm_sharpe +
                self.WEIGHTS["mc_robustness"] * norm_mc +
                self.WEIGHTS["return"] * norm_ret +
                self.WEIGHTS["drawdown"] * norm_dd +
                self.WEIGHTS["win_rate"] * norm_wr +
                self.WEIGHTS["profit_factor"] * norm_pf
            ) * 100.0

            s_copy = dict(s)
            s_copy["total_score"] = round(total_score, 2)
            scored.append(s_copy)

        scored.sort(key=lambda x: x.get("total_score", 0.0), reverse=True)
        for i, item in enumerate(scored):
            item["rank"] = i + 1

        return scored
