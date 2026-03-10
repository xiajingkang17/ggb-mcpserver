"""
带滑动条的函数图像 handler。

本模块职责：
1. 迁移所有 slider 版本的函数图像。
2. 保持旧实现中的滑动条命名、范围计算和表达式拼接逻辑不变。
3. 让函数 shapes 层在这一阶段完成闭环。

当前包含：
- linear_general_slider
- quadratic_standard_slider
- cubic_standard_slider
- sin_function_slider
- cos_function_slider
- tan_function_slider
- exponential_function_slider
- logarithmic_function_slider
"""

from __future__ import annotations

from .basic import _build_context
from shapes.common import execute_context


# ========== 滑动条辅助逻辑 ==========
def _calculate_slider_range(
    init_value,
    default_min=None,
    default_max=None,
    min_limit=None,
    max_limit=None,
):
    """根据初始值计算滑动条范围。

    规则保持与旧实现一致：
    - 初始值不为 0 时，范围取初始值的正负 3 倍
    - 初始值为 0 时，退回到调用方指定的默认范围
    - 最后再应用最小值/最大值限制
    """
    if init_value == 0:
        min_val = default_min if default_min is not None else -5
        max_val = default_max if default_max is not None else 5
    else:
        min_val = init_value * -3
        max_val = init_value * 3

    if min_limit is not None and min_val < min_limit:
        min_val = min_limit
    if max_limit is not None and max_val > max_limit:
        max_val = max_limit

    return min_val, max_val


def _add_slider(ctx, slider_name: str, slider_min, slider_max, slider_init) -> None:
    """统一添加函数滑动条。"""
    ctx.collector.add(f"{slider_name} = Slider[{slider_min}, {slider_max}, 0.1]")
    ctx.collector.add(f"SetValue[{slider_name}, {slider_init}]")
    ctx.collector.add(f"SetLabelStyle[{slider_name}, 0]")
    ctx.collector.add(f"SetLabelVisible[{slider_name}, true]")


# ========== 基础多项式 slider ==========
def handle_linear_general_slider(page, draw_type: str, params: dict) -> None:
    """绘制带滑动条的一次函数。"""
    ctx = _build_context(page)

    a_init = params.get("a", 1)
    b_init = params.get("b", 1)
    c_init = params.get("c", 0)

    a_min, a_max = _calculate_slider_range(a_init)
    b_min, b_max = _calculate_slider_range(b_init)
    c_min, c_max = _calculate_slider_range(c_init)

    slider_a_name = "a_linear"
    slider_b_name = "b_linear"
    slider_c_name = "c_linear"

    _add_slider(ctx, slider_a_name, a_min, a_max, a_init)
    _add_slider(ctx, slider_b_name, b_min, b_max, b_init)
    _add_slider(ctx, slider_c_name, c_min, c_max, c_init)

    ctx.collector.add(
        f"f(x) = If[{slider_b_name} != 0, "
        f"(-{slider_a_name} / {slider_b_name}) * x + (-{slider_c_name} / {slider_b_name}), "
        f"If[{slider_a_name} != 0, x = -{slider_c_name} / {slider_a_name}, 0])"
    )

    execute_context(ctx)
    return None


def handle_quadratic_standard_slider(page, draw_type: str, params: dict) -> None:
    """绘制带滑动条的二次函数。"""
    ctx = _build_context(page)

    a_init = params.get("a", 1)
    b_init = params.get("b", 0)
    c_init = params.get("c", 0)

    a_min, a_max = _calculate_slider_range(a_init)
    b_min, b_max = _calculate_slider_range(b_init)
    c_min, c_max = _calculate_slider_range(c_init)

    slider_a_name = "a_quad"
    slider_b_name = "b_quad"
    slider_c_name = "c_quad"

    _add_slider(ctx, slider_a_name, a_min, a_max, a_init)
    _add_slider(ctx, slider_b_name, b_min, b_max, b_init)
    _add_slider(ctx, slider_c_name, c_min, c_max, c_init)

    ctx.collector.add(f"f(x) = {slider_a_name}x^2 + {slider_b_name}x + {slider_c_name}")

    execute_context(ctx)
    return None


def handle_cubic_standard_slider(page, draw_type: str, params: dict) -> None:
    """绘制带滑动条的三次函数。"""
    ctx = _build_context(page)

    a_init = params.get("a", 1)
    b_init = params.get("b", 1)
    c_init = params.get("c", 1)
    d_init = params.get("d", 1)

    a_min, a_max = _calculate_slider_range(a_init)
    b_min, b_max = _calculate_slider_range(b_init)
    c_min, c_max = _calculate_slider_range(c_init)
    d_min, d_max = _calculate_slider_range(d_init)

    slider_a_name = "a_cubic"
    slider_b_name = "b_cubic"
    slider_c_name = "c_cubic"
    slider_d_name = "d_cubic"

    _add_slider(ctx, slider_a_name, a_min, a_max, a_init)
    _add_slider(ctx, slider_b_name, b_min, b_max, b_init)
    _add_slider(ctx, slider_c_name, c_min, c_max, c_init)
    _add_slider(ctx, slider_d_name, d_min, d_max, d_init)

    ctx.collector.add(
        f"f(x) = {slider_a_name}x^3 + {slider_b_name}x^2 + {slider_c_name}x + {slider_d_name}"
    )

    execute_context(ctx)
    return None


# ========== 三角函数 slider ==========
def handle_sin_function_slider(page, draw_type: str, params: dict) -> None:
    """绘制带滑动条的正弦函数。"""
    ctx = _build_context(page)

    amplitude_init = params.get("A", 1)
    frequency_init = params.get("B", 1)
    phase_init = params.get("C", 0)
    offset_init = params.get("D", 0)

    amplitude_min, amplitude_max = _calculate_slider_range(amplitude_init)
    frequency_min, frequency_max = _calculate_slider_range(
        frequency_init,
        default_min=0,
        default_max=5,
        min_limit=0,
    )
    phase_min, phase_max = _calculate_slider_range(phase_init)
    offset_min, offset_max = _calculate_slider_range(offset_init)

    slider_a_name = "A_sin"
    slider_b_name = "B_sin"
    slider_c_name = "C_sin"
    slider_d_name = "D_sin"

    _add_slider(ctx, slider_a_name, amplitude_min, amplitude_max, amplitude_init)
    _add_slider(ctx, slider_b_name, frequency_min, frequency_max, frequency_init)
    _add_slider(ctx, slider_c_name, phase_min, phase_max, phase_init)
    _add_slider(ctx, slider_d_name, offset_min, offset_max, offset_init)

    ctx.collector.add(
        f"f(x) = {slider_a_name} * sin({slider_b_name} * x + {slider_c_name}) + {slider_d_name}"
    )

    execute_context(ctx)
    return None


def handle_cos_function_slider(page, draw_type: str, params: dict) -> None:
    """绘制带滑动条的余弦函数。"""
    ctx = _build_context(page)

    amplitude_init = params.get("A", 1)
    frequency_init = params.get("B", 1)
    phase_init = params.get("C", 0)
    offset_init = params.get("D", 0)

    amplitude_min, amplitude_max = _calculate_slider_range(amplitude_init)
    frequency_min, frequency_max = _calculate_slider_range(
        frequency_init,
        default_min=0,
        default_max=5,
        min_limit=0,
    )
    phase_min, phase_max = _calculate_slider_range(phase_init)
    offset_min, offset_max = _calculate_slider_range(offset_init)

    slider_a_name = "A_cos"
    slider_b_name = "B_cos"
    slider_c_name = "C_cos"
    slider_d_name = "D_cos"

    _add_slider(ctx, slider_a_name, amplitude_min, amplitude_max, amplitude_init)
    _add_slider(ctx, slider_b_name, frequency_min, frequency_max, frequency_init)
    _add_slider(ctx, slider_c_name, phase_min, phase_max, phase_init)
    _add_slider(ctx, slider_d_name, offset_min, offset_max, offset_init)

    ctx.collector.add(
        f"f(x) = {slider_a_name} * cos({slider_b_name} * x + {slider_c_name}) + {slider_d_name}"
    )

    execute_context(ctx)
    return None


def handle_tan_function_slider(page, draw_type: str, params: dict) -> None:
    """绘制带滑动条的正切函数。"""
    ctx = _build_context(page)

    amplitude_init = params.get("A", 1)
    frequency_init = params.get("B", 1)
    phase_init = params.get("C", 0)
    offset_init = params.get("D", 0)

    amplitude_min, amplitude_max = _calculate_slider_range(amplitude_init)
    frequency_min, frequency_max = _calculate_slider_range(
        frequency_init,
        default_min=0,
        default_max=5,
        min_limit=0,
    )
    phase_min, phase_max = _calculate_slider_range(phase_init)
    offset_min, offset_max = _calculate_slider_range(offset_init)

    slider_a_name = "A_tan"
    slider_b_name = "B_tan"
    slider_c_name = "C_tan"
    slider_d_name = "D_tan"

    _add_slider(ctx, slider_a_name, amplitude_min, amplitude_max, amplitude_init)
    _add_slider(ctx, slider_b_name, frequency_min, frequency_max, frequency_init)
    _add_slider(ctx, slider_c_name, phase_min, phase_max, phase_init)
    _add_slider(ctx, slider_d_name, offset_min, offset_max, offset_init)

    ctx.collector.add(
        f"f(x) = {slider_a_name} * tan({slider_b_name} * x + {slider_c_name}) + {slider_d_name}"
    )

    execute_context(ctx)
    return None


# ========== 指数与对数 slider ==========
def handle_exponential_function_slider(page, draw_type: str, params: dict) -> None:
    """绘制带滑动条的指数函数。"""
    ctx = _build_context(page)

    a_init = params.get("a", 2)
    b_init = params.get("b", 1)
    c_init = params.get("c", 0)

    a_min, a_max = _calculate_slider_range(
        a_init,
        default_min=0.1,
        default_max=5,
        min_limit=0.1,
    )
    b_min, b_max = _calculate_slider_range(b_init)
    c_min, c_max = _calculate_slider_range(c_init)

    slider_a_name = "a_exp"
    slider_b_name = "b_exp"
    slider_c_name = "c_exp"

    _add_slider(ctx, slider_a_name, a_min, a_max, a_init)
    _add_slider(ctx, slider_b_name, b_min, b_max, b_init)
    _add_slider(ctx, slider_c_name, c_min, c_max, c_init)

    ctx.collector.add(
        f"f(x) = {slider_a_name}^(x + {slider_c_name}) + {slider_b_name}"
    )

    execute_context(ctx)
    return None


def handle_logarithmic_function_slider(page, draw_type: str, params: dict) -> None:
    """绘制带滑动条的对数函数。"""
    ctx = _build_context(page)

    a_init = params.get("a", 10)
    b_init = params.get("b", 1)
    c_init = params.get("c", 0)

    a_min, a_max = _calculate_slider_range(
        a_init,
        default_min=0.1,
        default_max=10,
        min_limit=0.1,
    )
    b_min, b_max = _calculate_slider_range(b_init)
    c_min, c_max = _calculate_slider_range(c_init)

    slider_a_name = "a_log"
    slider_b_name = "b_log"
    slider_c_name = "c_log"

    _add_slider(ctx, slider_a_name, a_min, a_max, a_init)
    _add_slider(ctx, slider_b_name, b_min, b_max, b_init)
    _add_slider(ctx, slider_c_name, c_min, c_max, c_init)

    ctx.collector.add(
        f"f(x) = {slider_b_name} * log({slider_a_name}, x + {slider_c_name})"
    )

    execute_context(ctx)
    return None
