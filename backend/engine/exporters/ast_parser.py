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

    # Match function call token(args...)
    match = re.match(r"^([a-zA-Z0-9_%-]+)\((.*)\)$", expr_str)
    if not match:
        # Leaf token
        return ExpressionNode(expr_str)

    func_name = match.group(1)
    inner = match.group(2)

    # Split top-level comma arguments
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

def extract_indicators(node: ExpressionNode) -> set[str]:
    """Find all technical indicator symbols used in the AST."""
    indicators = set()
    KNOWN_FUNCS = {
        "add", "sub", "mul", "div", "gt", "lt", "gte", "lte", "eq",
        "and_op", "or_op", "not_op", "neg", "abs_diff", "crossover",
        "crossunder", "if_then_else", "max_op", "min_op"
    }

    def walk(n: ExpressionNode):
        tok = n.token
        if n.is_leaf():
            if not tok.startswith("c_") and tok not in KNOWN_FUNCS and not tok.replace('.', '', 1).isdigit():
                indicators.add(tok)
        else:
            for child in n.args:
                walk(child)

    walk(node)
    return indicators

def node_to_mql5(node: ExpressionNode) -> str:
    """Transpile AST node into valid MQL5 C++ expression."""
    tok = node.token

    if node.is_leaf():
        if tok.startswith("c_"):
            val = tok.replace("c_", "").replace("neg_", "-")
            return f"{float(val):.2f}"
        if tok.replace('.', '', 1).isdigit():
            return tok
        # Indicator buffer reference at current bar index [0]
        clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", tok).lower()
        return f"{clean_name}_val[0]"

    # Operations
    args = [node_to_mql5(a) for a in node.args]
    if tok == "add" and len(args) == 2:
        return f"({args[0]} + {args[1]})"
    elif tok == "sub" and len(args) == 2:
        return f"({args[0]} - {args[1]})"
    elif tok == "mul" and len(args) == 2:
        return f"({args[0]} * {args[1]})"
    elif tok == "div" and len(args) == 2:
        return f"({args[1]} != 0.0 ? ({args[0]} / {args[1]}) : 0.0)"
    elif tok == "gt" and len(args) == 2:
        return f"({args[0]} > {args[1]} ? 1.0 : 0.0)"
    elif tok == "lt" and len(args) == 2:
        return f"({args[0]} < {args[1]} ? 1.0 : 0.0)"
    elif tok == "gte" and len(args) == 2:
        return f"({args[0]} >= {args[1]} ? 1.0 : 0.0)"
    elif tok == "lte" and len(args) == 2:
        return f"({args[0]} <= {args[1]} ? 1.0 : 0.0)"
    elif tok == "and_op" and len(args) == 2:
        return f"(({args[0]} > 0.0 && {args[1]} > 0.0) ? 1.0 : 0.0)"
    elif tok == "or_op" and len(args) == 2:
        return f"(({args[0]} > 0.0 || {args[1]} > 0.0) ? 1.0 : 0.0)"
    elif tok == "not_op" and len(args) == 1:
        return f"({args[0]} <= 0.0 ? 1.0 : 0.0)"
    elif tok == "abs_diff" and len(args) == 2:
        return f"MathAbs({args[0]} - {args[1]})"
    elif tok == "crossover" and len(args) == 2:
        return f"(({args[0]} > {args[1]}) ? 1.0 : 0.0)"
    elif tok == "crossunder" and len(args) == 2:
        return f"(({args[0]} < {args[1]}) ? 1.0 : 0.0)"

    return f"({', '.join(args)})"

def node_to_pine(node: ExpressionNode) -> str:
    """Transpile AST node into TradingView Pine Script v5 expression."""
    tok = node.token

    if node.is_leaf():
        if tok.startswith("c_"):
            val = tok.replace("c_", "").replace("neg_", "-")
            return f"{float(val):.2f}"
        if tok.replace('.', '', 1).isdigit():
            return tok
        clean_name = re.sub(r"[^a-zA-Z0-9_]", "_", tok).lower()
        return f"{clean_name}Val"

    args = [node_to_pine(a) for a in node.args]
    if tok == "add" and len(args) == 2:
        return f"({args[0]} + {args[1]})"
    elif tok == "sub" and len(args) == 2:
        return f"({args[0]} - {args[1]})"
    elif tok == "mul" and len(args) == 2:
        return f"({args[0]} * {args[1]})"
    elif tok == "div" and len(args) == 2:
        return f"({args[1]} != 0 ? ({args[0]} / {args[1]}) : 0)"
    elif tok == "gt" and len(args) == 2:
        return f"({args[0]} > {args[1]})"
    elif tok == "lt" and len(args) == 2:
        return f"({args[0]} < {args[1]})"
    elif tok == "gte" and len(args) == 2:
        return f"({args[0]} >= {args[1]})"
    elif tok == "lte" and len(args) == 2:
        return f"({args[0]} <= {args[1]})"
    elif tok == "and_op" and len(args) == 2:
        return f"({args[0]} and {args[1]})"
    elif tok == "or_op" and len(args) == 2:
        return f"({args[0]} or {args[1]})"
    elif tok == "not_op" and len(args) == 1:
        return f"(not {args[0]})"
    elif tok == "abs_diff" and len(args) == 2:
        return f"math.abs({args[0]} - {args[1]})"
    elif tok == "crossover" and len(args) == 2:
        return f"ta.crossover({args[0]}, {args[1]})"
    elif tok == "crossunder" and len(args) == 2:
        return f"ta.crossunder({args[0]}, {args[1]})"

    return f"({', '.join(args)})"
