import ast
import math
import operator as op

from userbot.core import cat_cmd, edit_delete, edit_or_reply

_OPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv, ast.Mod: op.mod, ast.Pow: op.pow,
    ast.USub: op.neg, ast.UAdd: op.pos,
}
_FUNCS = {
    "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "log": math.log, "log10": math.log10, "abs": abs, "round": round,
    "floor": math.floor, "ceil": math.ceil, "factorial": math.factorial,
}
_CONST = {"pi": math.pi, "e": math.e}


def safe_eval(node):
    if isinstance(node, ast.Expression):
        return safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id in _CONST:
        return _CONST[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        left, right = safe_eval(node.left), safe_eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 1000:
            raise ValueError("exponent too large")
        return _OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](safe_eval(node.operand))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCS:
        args = [safe_eval(a) for a in node.args]
        if node.func.id == "factorial" and args and args[0] > 500:
            raise ValueError("too large")
        return _FUNCS[node.func.id](*args)
    raise ValueError("unsupported expression")


@cat_cmd("calc", command=("calc <expression>", "Calculator: + - * / // % ** sqrt sin cos log pi e ..."), allow_sudo=True)
async def calc(event):
    expr = (event.pattern_match.group(1) or "").strip()
    if not expr:
        return await edit_delete(event, "`Usage: calc 2*(3+4)`")
    try:
        result = safe_eval(ast.parse(expr, mode="eval"))
    except Exception as e:  # noqa: BLE001
        return await edit_delete(event, f"`Invalid expression:` {e}")
    await edit_or_reply(event, f"**Expression:** `{expr}`\n**Result:** `{result}`")
