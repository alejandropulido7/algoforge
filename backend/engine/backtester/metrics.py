import numpy as np

def calculate_sharpe(returns, risk_free=0.0):
    if np.std(returns) == 0: return 0
    return np.mean(returns - risk_free) / np.std(returns) * np.sqrt(252)

def calculate_max_drawdown(equity_curve):
    roll_max = np.maximum.accumulate(equity_curve)
    drawdowns = (equity_curve - roll_max) / roll_max
    return np.min(drawdowns)

def calculate_win_rate(trades):
    if not trades: return 0
    winning = sum(1 for t in trades if t > 0)
    return winning / len(trades)

def calculate_profit_factor(trades):
    gross_profit = sum(t for t in trades if t > 0)
    gross_loss = abs(sum(t for t in trades if t < 0))
    return gross_profit / gross_loss if gross_loss != 0 else float('inf')
