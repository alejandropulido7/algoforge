import pytest
from engine.exporters.ast_parser import (
    parse_prefix_expression,
    node_to_mql5,
    node_to_pine,
)

def test_cross_above_transpiles_real_crossover():
    # Python's cross_above fires only on the crossing bar (prev <= cur && cur > b).
    # The MQL5 output must reference both bar [1] (current) and bar [2] (previous).
    ast = parse_prefix_expression("cross_above(RSI, c_30)")
    code = node_to_mql5(ast)
    assert code == "(rsi_val[1] > 30.00 && rsi_val[2] <= 30.00 ? 1.0 : 0.0)"

def test_cross_below_transpiles_real_crossover():
    ast = parse_prefix_expression("cross_below(EMA, SMA)")
    code = node_to_mql5(ast)
    assert code == "(ema_val[1] < sma_val[1] && ema_val[2] >= sma_val[2] ? 1.0 : 0.0)"

def test_cross_above_nested_expression_shifts_bars():
    ast = parse_prefix_expression("cross_above(mul(RSI, Stochastic), c_80)")
    code = node_to_mql5(ast)
    assert code == "((rsi_val[1] * stochastic_val[1]) > 80.00 && (rsi_val[2] * stochastic_val[2]) <= 80.00 ? 1.0 : 0.0)"

def test_safe_div_parity_with_python():
    # Python safe_div returns 1.0 when |denominator| <= 1e-6; MQL5 must match.
    ast = parse_prefix_expression("div(RSI, EMA)")
    code = node_to_mql5(ast)
    assert code == "(MathAbs(ema_val[1]) > 1e-6 ? (rsi_val[1] / ema_val[1]) : 1.0)"

def test_safe_div_pine_parity():
    ast = parse_prefix_expression("div(RSI, c_0)")
    code = node_to_pine(ast)
    assert code == "(math.abs(0.00) > 1e-6 ? (rsi_val / 0.00) : 1.0)"

def test_plain_gt_unchanged():
    ast = parse_prefix_expression("gt(RSI, c_70)")
    assert node_to_mql5(ast) == "(rsi_val[1] > 70.00 ? 1.0 : 0.0)"