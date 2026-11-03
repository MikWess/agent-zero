"""Evaluate arithmetic without executing model-supplied Python code."""
import ast
import math
import operator

_BINARY = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
           ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod}
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def calculator(expression: str) -> str:
    """Return a number or a tool-readable error. Only basic arithmetic is allowed."""
    try:
        if not isinstance(expression, str) or len(expression) > 256:
            raise ValueError("Use an arithmetic expression of at most 256 characters")
        tree = ast.parse(expression, mode="eval")
        if sum(1 for _ in ast.walk(tree)) > 64:
            raise ValueError("Expression is too complex")

        def evaluate(node):
            if isinstance(node, ast.Constant) and type(node.value) in (int, float):
                result = node.value
            elif isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
                result = _BINARY[type(node.op)](evaluate(node.left), evaluate(node.right))
            elif isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
                result = _UNARY[type(node.op)](evaluate(node.operand))
            else:
                raise ValueError("Only numbers, parentheses, +, -, *, /, // and % are supported")
            if not math.isfinite(result) or abs(result) > 1e100:
                raise ValueError("Number is out of range")
            return result

        return str(evaluate(tree.body))
    except (SyntaxError, ValueError, ArithmeticError, TypeError) as error:
        return f"Error: {error}"
