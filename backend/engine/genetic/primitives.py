import operator
import numpy as np
from deap import gp

def safe_div(left, right):
    with np.errstate(divide='ignore', invalid='ignore'):
        res = np.where(np.abs(right) > 1e-6, left / right, 1.0)
        return res if isinstance(res, np.ndarray) else float(res)

def safe_add(left, right):
    return left + right

def safe_sub(left, right):
    return left - right

def safe_mul(left, right):
    return left * right

def gt(left, right):
    return (np.asarray(left) > np.asarray(right)).astype(float)

def lt(left, right):
    return (np.asarray(left) < np.asarray(right)).astype(float)

def cross_above(series_a, series_b):
    a = np.asarray(series_a)
    b = np.asarray(series_b)
    prev_a = np.roll(a, 1)
    prev_b = np.roll(b, 1)
    prev_a[0] = a[0]
    prev_b[0] = b[0]
    return ((prev_a <= prev_b) & (a > b)).astype(float)

def cross_below(series_a, series_b):
    a = np.asarray(series_a)
    b = np.asarray(series_b)
    prev_a = np.roll(a, 1)
    prev_b = np.roll(b, 1)
    prev_a[0] = a[0]
    prev_b[0] = b[0]
    return ((prev_a >= prev_b) & (a < b)).astype(float)

def create_primitive_set(n_indicators: int) -> gp.PrimitiveSet:
    """Create DEAP primitive set for trading strategy evolution."""
    pset = gp.PrimitiveSet("MAIN", n_indicators)
    pset.addPrimitive(safe_add, 2, name="add")
    pset.addPrimitive(safe_sub, 2, name="sub")
    pset.addPrimitive(safe_mul, 2, name="mul")
    pset.addPrimitive(safe_div, 2, name="div")
    pset.addPrimitive(gt, 2, name="gt")
    pset.addPrimitive(lt, 2, name="lt")
    pset.addPrimitive(cross_above, 2, name="cross_above")
    pset.addPrimitive(cross_below, 2, name="cross_below")

    pset.addEphemeralConstant("rand_const", lambda: float(np.round(np.random.uniform(-1, 1), 2)))
    for val in [0.0, 20.0, 30.0, 50.0, 70.0, 80.0, 100.0]:
        pset.addTerminal(val, name=f"c_{int(val)}")

    return pset
