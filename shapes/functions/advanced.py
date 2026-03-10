"""
普通高级函数图像 handler。

本模块职责：
1. 迁移非 slider 的三角函数、指数函数、对数函数。
2. 保持旧实现中的表达式拼接方式不变。

当前包含：
- sin_function
- cos_function
- tan_function
- exponential_function
- logarithmic_function
"""

from __future__ import annotations

from .basic import _build_context
from shapes.common import execute_context


# ========== 普通高级函数图像 ==========
def handle_sin_function(page, draw_type: str, params: dict) -> None:
    """绘制正弦函数。"""
    ctx = _build_context(page)

    amplitude = params.get("A", 1)
    frequency = params.get("B", 1)
    phase = params.get("C", 0)
    offset = params.get("D", 0)

    func_expr = f"{amplitude} * sin({frequency} * x + {phase}) + {offset}"
    ctx.collector.add(f"f(x) = {func_expr}")

    execute_context(ctx)
    return None


def handle_cos_function(page, draw_type: str, params: dict) -> None:
    """绘制余弦函数。"""
    ctx = _build_context(page)

    amplitude = params.get("A", 1)
    frequency = params.get("B", 1)
    phase = params.get("C", 0)
    offset = params.get("D", 0)

    func_expr = f"{amplitude} * cos({frequency} * x + {phase}) + {offset}"
    ctx.collector.add(f"f(x) = {func_expr}")

    execute_context(ctx)
    return None


def handle_tan_function(page, draw_type: str, params: dict) -> None:
    """绘制正切函数。"""
    ctx = _build_context(page)

    amplitude = params.get("A", 1)
    frequency = params.get("B", 1)
    phase = params.get("C", 0)
    offset = params.get("D", 0)

    func_expr = f"{amplitude} * tan({frequency} * x + {phase}) + {offset}"
    ctx.collector.add(f"f(x) = {func_expr}")

    execute_context(ctx)
    return None


def handle_exponential_function(page, draw_type: str, params: dict) -> None:
    """绘制指数函数。"""
    ctx = _build_context(page)

    base = params.get("a", 2)
    offset_y = params.get("b", 1)
    offset_x = params.get("c", 0)

    func_expr = f"{base}^(x + {offset_x}) + {offset_y}"
    ctx.collector.add(f"f(x) = {func_expr}")

    execute_context(ctx)
    return None


def handle_logarithmic_function(page, draw_type: str, params: dict) -> None:
    """绘制对数函数。"""
    ctx = _build_context(page)

    base = params.get("a", 10)
    coefficient = params.get("b", 1)
    offset_x = params.get("c", 0)

    func_expr = f"{coefficient} * log({base}, x + {offset_x})"
    ctx.collector.add(f"f(x) = {func_expr}")

    execute_context(ctx)
    return None
