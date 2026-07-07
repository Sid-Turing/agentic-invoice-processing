"""Deterministic arithmetic tool (safe AST evaluation — numbers and + - * / ( )
only; no names, calls, or attribute access)."""
from __future__ import annotations

import ast
import operator

from strands import tool

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.Pow: operator.pow,
}


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("unsupported expression")


def evaluate(expression: str) -> float:
    """Pure evaluator (importable without the tool wrapper, for tests)."""
    tree = ast.parse(expression, mode="eval")
    return _eval(tree.body)


@tool
def calculate(expression: str) -> float:
    """Evaluate an arithmetic expression deterministically (for totals, tax, and
    tolerance checks).

    Args:
        expression: An arithmetic expression, e.g. '4250.00 * 2 + 5800.00'.
    """
    return evaluate(expression)
