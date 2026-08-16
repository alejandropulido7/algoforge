import numpy as np
from engine.montecarlo.simulator import MonteCarloSimulator

def test_monte_carlo_simulation():
    sim = MonteCarloSimulator(n_simulations=50)
    trade_pnls = [0.05, -0.02, 0.08, -0.03, 0.04, -0.01, 0.06]
    res = sim.simulate(trade_pnls, initial_balance=10000.0, method="permutation")
    
    assert len(res.final_balances) == 50
    assert len(res.max_drawdowns) == 50
    assert 0.0 <= res.robustness_score <= 100.0
    assert 0.0 <= res.probability_of_ruin <= 1.0

def test_monte_carlo_bootstrap():
    sim = MonteCarloSimulator(n_simulations=50)
    trade_pnls = [100.0, -50.0, 200.0, -80.0, 150.0]
    res = sim.simulate(trade_pnls, initial_balance=5000.0, method="bootstrap")
    assert len(res.final_balances) == 50
