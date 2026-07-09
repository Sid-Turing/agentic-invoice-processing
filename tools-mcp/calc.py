"""Safe arithmetic evaluator (numbers, + - * / % ** ( ), comparisons, abs/round/min/max)."""
from __future__ import annotations

import ast
import operator

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.USub: operator.neg, ast.UAdd: operator.pos,
        ast.Pow: operator.pow, ast.Mod: operator.mod}
_CMP = {ast.Eq: operator.eq, ast.NotEq: operator.ne, ast.Lt: operator.lt,
        ast.LtE: operator.le, ast.Gt: operator.gt, ast.GtE: operator.ge}
_FUNCS = {"abs": abs, "round": lambda x, n=0: round(x, int(n)), "min": min, "max": max}


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.Compare) and len(node.ops) == 1 and type(node.ops[0]) in _CMP:
        return float(_CMP[type(node.ops[0])](_eval(node.left), _eval(node.comparators[0])))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCS:
        return float(_FUNCS[node.func.id](*[_eval(a) for a in node.args]))
    raise ValueError("unsupported expression")


def evaluate(expression: str) -> float:
    return _eval(ast.parse(expression, mode="eval").body)
