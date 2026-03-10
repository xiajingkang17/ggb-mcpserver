"""
多项式类函数 handler。

本模块职责：
1. 迁移三次函数和通用多项式函数。
2. 保持旧实现中的表达式拼接策略不变，避免引入渲染差异。

当前包含：
- cubic_standard
- polynomial_function
"""

from __future__ import annotations

from .basic import _build_context
from shapes.common import execute_context


# ========== 多项式辅助逻辑 ==========
def _build_polynomial_term(coeff, power: int) -> str:
    """构建单项式字符串，保持与旧实现一致。"""
    if power == 0:
        return str(coeff) if coeff != 1 else "1"

    if power == 1:
        if coeff == 1:
            return "x"
        if coeff == -1:
            return "-x"
        return f"{coeff}x"

    if coeff == 1:
        return f"x^{power}"
    if coeff == -1:
        return f"-x^{power}"
    return f"{coeff}x^{power}"


# ========== 多项式类函数 ==========
def handle_cubic_standard(page, draw_type: str, params: dict) -> None:
    """绘制标准式三次函数。"""
    ctx = _build_context(page)

    a = params.get("a", 1)
    b = params.get("b", 0)
    c = params.get("c", 0)
    d = params.get("d", 0)

    # 保持旧实现逻辑，先从 x^3 项开始构建表达式。
    if a == 1:
        func_expr = "x^3"
    elif a == -1:
        func_expr = "-x^3"
    else:
        func_expr = f"{a}x^3"

    if b != 0:
        if b > 0:
            func_expr += f" + {b}x^2"
        else:
            func_expr += f" - {-b}x^2"

    if c != 0:
        if c > 0:
            func_expr += f" + {c}x"
        else:
            func_expr += f" - {-c}x"

    if d != 0:
        if d > 0:
            func_expr += f" + {d}"
        else:
            func_expr += f" - {-d}"

    # 这里保留旧实现中的兜底判断。
    if not func_expr:
        func_expr = "x^3"

    ctx.collector.add(f"f(x) = {func_expr}")

    execute_context(ctx)
    return None


def handle_polynomial_function(page, draw_type: str, params: dict) -> None:
    """绘制通用多项式函数。"""
    ctx = _build_context(page)

    coefficients = params.get("coefficients", [1, 0, 0, 0])
    if not isinstance(coefficients, list) or len(coefficients) == 0:
        raise Exception("polynomial_function需要提供coefficients参数（系数列表）")

    func_expr = ""
    degree = len(coefficients) - 1

    for index, coeff in enumerate(coefficients):
        if coeff == 0:
            continue

        power = degree - index
        term = _build_polynomial_term(coeff, power)

        if func_expr == "":
            func_expr = term
        else:
            if coeff > 0:
                func_expr += f" + {term}"
            else:
                # 这里保留旧实现中的负号处理规则，避免表达式形式发生变化。
                if term.startswith("-"):
                    func_expr += f" - {term[1:]}"
                else:
                    func_expr += f" + {term}"

    if not func_expr:
        func_expr = "0"

    ctx.collector.add(f"f(x) = {func_expr}")

    execute_context(ctx)
    return None
