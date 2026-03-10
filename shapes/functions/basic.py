"""
基础函数图像 handler。

本模块职责：
1. 先迁移最基础、最稳定的一批函数图像。
2. 让这些函数从 tools_function_new.py 的大 if/elif 分支中迁出。
3. 作为后续 slider 版和高级函数拆分的样板。

当前包含：
- linear_general
- quadratic_standard
"""

from __future__ import annotations

from shapes.common import CommandCollector, ShapeContext, execute_context
from shapes.scene import initialize_function_scene


# ========== 函数基础执行辅助 ==========
def _build_context(page) -> ShapeContext:
    """创建基础函数 handler 使用的执行上下文。"""
    initialize_function_scene(page)
    return ShapeContext(page=page, collector=CommandCollector())


# ========== 基础函数图像 ==========
def handle_quadratic_standard(page, draw_type: str, params: dict) -> None:
    """绘制标准式二次函数。"""
    ctx = _build_context(page)

    a = params.get("a", 1)
    b = params.get("b", 0)
    c = params.get("c", 0)

    # 保持旧实现逻辑，按系数拼出 GeoGebra 可直接识别的表达式。
    if a == 1:
        func_expr = "x^2"
    elif a == -1:
        func_expr = "-x^2"
    else:
        func_expr = f"{a}x^2"

    if b != 0:
        if b > 0:
            func_expr += f" + {b}x"
        else:
            func_expr += f" - {-b}x"

    if c != 0:
        if c > 0:
            func_expr += f" + {c}"
        else:
            func_expr += f" - {-c}"

    ctx.collector.add(f"f(x) = {func_expr}")

    execute_context(ctx)
    return None


def handle_linear_general(page, draw_type: str, params: dict) -> None:
    """绘制一般式一次函数。"""
    ctx = _build_context(page)

    a = params.get("a", 1)
    b = params.get("b", 1)
    c = params.get("c", 0)

    if b != 0:
        # 转换为 y = mx + b 形式，保持与旧实现完全一致。
        m = -a / b
        b_val = -c / b
        func_expr = f"{m}x + {b_val}"
    else:
        # b 为 0 时退化为垂直线 x = -c / a。
        x_val = -c / a
        func_expr = f"x = {x_val}"

    ctx.collector.add(f"f(x) = {func_expr}")

    execute_context(ctx)
    return None
