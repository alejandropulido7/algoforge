import re
from typing import Any

class ExpressionNode:
    def __init__(self, token: str, args: list['ExpressionNode'] | None = None):
        self.token = token
        self.args = args or []

    def is_leaf(self) -> bool:
        return len(self.args) == 0

    def __repr__(self) -> str:
        if self.is_leaf():
            return self.token
        return f"{self.token}({', '.join(repr(a) for a in self.args)})"

def parse_prefix_expression(expr_str: str) -> ExpressionNode:
    """Parse a DEAP prefix expression string into an AST tree."""
    expr_str = expr_str.strip()
    if not expr_str:
        return ExpressionNode("0.0")

    match = re.match(r"^([a-zA-Z0-9_%-]+)\((.*)\)$", expr_str)
    if not match:
        return ExpressionNode(expr_str)

    func_name = match.group(1)
    inner = match.group(2)

    args = []
    depth = 0
    curr = []
    for char in inner:
        if char == '(':
            depth += 1
            curr.append(char)
        elif char == ')':
            depth -= 1
            curr.append(char)
        elif char == ',' and depth == 0:
            args.append("".join(curr).strip())
            curr = []
        else:
            curr.append(char)
    if curr:
        args.append("".join(curr).strip())

    return ExpressionNode(func_name, [parse_prefix_expression(a) for a in args if a])

def is_number(s: str) -> bool:
    """Check if token string represents a numerical constant."""
    try:
        float(s)
        return True
    except (ValueError, TypeError):
        return False

def parse_constant_value(s: str) -> float:
    """Extract float value from constant token (e.g. c_50, c_neg_10, -0.95, 30)."""
    if s.startswith("c_"):
        val_str = s.replace("c_", "").replace("neg_", "-")
        try:
            return float(val_str)
        except ValueError:
            return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0

def extract_indicators(node: ExpressionNode) -> set[str]:
    """Find all technical indicator symbols used in the AST, ignoring numbers and constants."""
    indicators = set()
    KNOWN_FUNCS = {
        "add", "sub", "mul", "div", "gt", "lt", "gte", "lte", "eq",
        "and_op", "or_op", "not_op", "neg", "abs_diff", "crossover",
        "crossunder", "cross_above", "cross_below", "if_then_else",
        "max_op", "min_op", "safe_add", "safe_sub", "safe_mul", "safe_div"
    }

    def walk(n: ExpressionNode):
        tok = n.token
        if n.is_leaf():
            if not tok.startswith("c_") and not is_number(tok) and tok not in KNOWN_FUNCS:
                indicators.add(tok)
        else:
            for child in n.args:
                walk(child)

    walk(node)
    return indicators

def node_to_mql5(node: ExpressionNode) -> str:
    """Transpile AST node into valid compilable MQL5 C++ expression referencing closed bar [1]."""
    tok = node.token

    if node.is_leaf():
        if tok.startswith("c_") or is_number(tok):
            val = parse_constant_value(tok)
            return f"{val:.2f}"
        clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", tok).lower()
        return f"{clean_name}_val[1]"

    args = [node_to_mql5(a) for a in node.args]

    # Arithmetic
    if tok in ("add", "safe_add") and len(args) == 2:
        return f"({args[0]} + {args[1]})"
    elif tok in ("sub", "safe_sub") and len(args) == 2:
        return f"({args[0]} - {args[1]})"
    elif tok in ("mul", "safe_mul") and len(args) == 2:
        return f"({args[0]} * {args[1]})"
    elif tok in ("div", "safe_div") and len(args) == 2:
        # Parity with Python's safe_div (primitives.py): denominator below
        # 1e-6 in magnitude returns 1.0, NOT 0.0.
        return f"(MathAbs({args[1]}) > 1e-6 ? ({args[0]} / {args[1]}) : 1.0)"
    elif tok == "neg" and len(args) == 1:
        return f"(-{args[0]})"
    elif tok == "abs_diff" and len(args) == 2:
        return f"MathAbs({args[0]} - {args[1]})"
    elif tok == "max_op" and len(args) == 2:
        return f"MathMax({args[0]}, {args[1]})"
    elif tok == "min_op" and len(args) == 2:
        return f"MathMin({args[0]}, {args[1]})"

    # Relational (Always return 1.0 for true, 0.0 for false)
    elif tok == "gt" and len(args) == 2:
        return f"({args[0]} > {args[1]} ? 1.0 : 0.0)"
    elif tok == "lt" and len(args) == 2:
        return f"({args[0]} < {args[1]} ? 1.0 : 0.0)"
    elif tok == "gte" and len(args) == 2:
        return f"({args[0]} >= {args[1]} ? 1.0 : 0.0)"
    elif tok == "lte" and len(args) == 2:
        return f"({args[0]} <= {args[1]} ? 1.0 : 0.0)"
    elif tok == "eq" and len(args) == 2:
        return f"({args[0]} == {args[1]} ? 1.0 : 0.0)"

    # Crossovers: true ONLY on the crossing bar, matching Python's
    # cross_above/cross_below (primitives.py) which compare the current
    # element with the previous one (np.roll). The current value is read
    # from bar [1] (last closed), so the previous value comes from bar [2].
    elif tok in ("crossover", "cross_above") and len(args) == 2:
        prev0 = args[0].replace("[1]", "[2]")
        prev1 = args[1].replace("[1]", "[2]")
        return f"({args[0]} > {args[1]} && {prev0} <= {prev1} ? 1.0 : 0.0)"
    elif tok in ("crossunder", "cross_below") and len(args) == 2:
        prev0 = args[0].replace("[1]", "[2]")
        prev1 = args[1].replace("[1]", "[2]")
        return f"({args[0]} < {args[1]} && {prev0} >= {prev1} ? 1.0 : 0.0)"

    # Logical
    elif tok == "and_op" and len(args) == 2:
        return f"(({args[0]} > 0.0 && {args[1]} > 0.0) ? 1.0 : 0.0)"
    elif tok == "or_op" and len(args) == 2:
        return f"(({args[0]} > 0.0 || {args[1]} > 0.0) ? 1.0 : 0.0)"
    elif tok == "not_op" and len(args) == 1:
        return f"({args[0]} <= 0.0 ? 1.0 : 0.0)"

    # Safe fallback for binary operations: NEVER join with comma
    if len(args) == 2:
        return f"({args[0]} > {args[1]} ? 1.0 : 0.0)"
    elif len(args) == 1:
        return f"({args[0]})"

    return "0.0"

def node_to_pine(node: ExpressionNode) -> str:
    """Transpile AST node into TradingView Pine Script v5 expression."""
    tok = node.token

    if node.is_leaf():
        if tok.startswith("c_") or is_number(tok):
            val = parse_constant_value(tok)
            return f"{val:.2f}"
        clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", tok).lower()
        return f"{clean_name}_val"

    args = [node_to_pine(a) for a in node.args]

    if tok in ("add", "safe_add") and len(args) == 2:
        return f"({args[0]} + {args[1]})"
    elif tok in ("sub", "safe_sub") and len(args) == 2:
        return f"({args[0]} - {args[1]})"
    elif tok in ("mul", "safe_mul") and len(args) == 2:
        return f"({args[0]} * {args[1]})"
    elif tok in ("div", "safe_div") and len(args) == 2:
        return f"(math.abs({args[1]}) > 1e-6 ? ({args[0]} / {args[1]}) : 1.0)"
    elif tok == "neg" and len(args) == 1:
        return f"(-{args[0]})"
    elif tok == "abs_diff" and len(args) == 2:
        return f"math.abs({args[0]} - {args[1]})"
    elif tok == "max_op" and len(args) == 2:
        return f"math.max({args[0]}, {args[1]})"
    elif tok == "min_op" and len(args) == 2:
        return f"math.min({args[0]}, {args[1]})"

    elif tok == "gt" and len(args) == 2:
        return f"({args[0]} > {args[1]})"
    elif tok == "lt" and len(args) == 2:
        return f"({args[0]} < {args[1]})"
    elif tok == "gte" and len(args) == 2:
        return f"({args[0]} >= {args[1]})"
    elif tok == "lte" and len(args) == 2:
        return f"({args[0]} <= {args[1]})"
    elif tok == "eq" and len(args) == 2:
        return f"({args[0]} == {args[1]})"
    elif tok in ("crossover", "cross_above") and len(args) == 2:
        return f"ta.crossover({args[0]}, {args[1]})"
    elif tok in ("crossunder", "cross_below") and len(args) == 2:
        return f"ta.crossunder({args[0]}, {args[1]})"

    elif tok == "and_op" and len(args) == 2:
        return f"({args[0]} and {args[1]})"
    elif tok == "or_op" and len(args) == 2:
        return f"({args[0]} or {args[1]})"
    elif tok == "not_op" and len(args) == 1:
        return f"(not {args[0]})"

    if len(args) == 2:
        return f"({args[0]} > {args[1]})"
    elif len(args) == 1:
        return f"({args[0]})"

    return "0.0"
