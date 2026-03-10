"""
表达式型函数图像 handler。

本模块职责：
1. 以 GeoGebra 原生表达式作为函数绘图的唯一核心输入。
2. 支持在表达式绘图前批量创建所需滑动条。
3. 保持函数场景初始化与命令提交流程统一。
"""

from __future__ import annotations

from typing import Any

from shapes.common import CommandCollector, ShapeContext, execute_context
from shapes.scene import initialize_function_scene


# ========== 执行上下文辅助 ==========
def _build_context(page) -> ShapeContext:
    """创建函数表达式 handler 使用的执行上下文。"""
    initialize_function_scene(page)
    return ShapeContext(page=page, collector=CommandCollector())


# ========== 滑动条辅助 ==========
def _validate_slider(slider: Any) -> dict[str, Any]:
    """校验单个滑动条参数。"""
    if not isinstance(slider, dict):
        raise Exception("function 的 sliders 项必须是对象")

    required_fields = ("name", "min", "max", "step", "init")
    missing_fields = [field for field in required_fields if field not in slider]
    if missing_fields:
        raise Exception(f"function 的 slider 缺少字段：{missing_fields}")

    slider_name = slider["name"]
    slider_min = slider["min"]
    slider_max = slider["max"]
    slider_step = slider["step"]
    slider_init = slider["init"]

    if not isinstance(slider_name, str) or not slider_name.strip():
        raise Exception("function 的 slider.name 必须是非空字符串")
    if slider_step <= 0:
        raise Exception("function 的 slider.step 必须大于 0")
    if slider_max <= slider_min:
        raise Exception("function 的 slider.max 必须大于 slider.min")
    if slider_init < slider_min or slider_init > slider_max:
        raise Exception("function 的 slider.init 必须落在 [min, max] 范围内")

    return {
        "name": slider_name.strip(),
        "min": slider_min,
        "max": slider_max,
        "step": slider_step,
        "init": slider_init,
    }


def _add_slider(ctx: ShapeContext, slider: dict[str, Any]) -> None:
    """向当前构造添加函数滑动条。"""
    slider_name = slider["name"]
    slider_min = slider["min"]
    slider_max = slider["max"]
    slider_step = slider["step"]
    slider_init = slider["init"]

    ctx.collector.add(f"{slider_name} = Slider[{slider_min}, {slider_max}, {slider_step}]")
    ctx.collector.add(f"SetValue[{slider_name}, {slider_init}]")
    ctx.collector.add(f"SetLabelStyle[{slider_name}, 0]")
    ctx.collector.add(f"SetLabelVisible[{slider_name}, true]")


# ========== 标准函数图像 ==========
def handle_function(page, draw_type: str, params: dict) -> None:
    """绘制表达式型函数图像。"""
    ctx = _build_context(page)

    function_name = params.get("id")
    expr = params.get("expr")
    sliders = params.get("sliders", [])

    if not isinstance(function_name, str) or not function_name.strip():
        raise Exception("function 需要提供明确的 id，不能依赖隐式命名")
    if not isinstance(expr, str) or not expr.strip():
        raise Exception("function 需要提供非空 expr 表达式")
    if "=" in expr:
        raise Exception("function 的 expr 只接受函数右侧表达式，不要包含 '='")
    if not isinstance(sliders, list):
        raise Exception("function 的 sliders 必须是数组")

    for slider in sliders:
        _add_slider(ctx, _validate_slider(slider))

    ctx.collector.add(f"{function_name}(x) = {expr.strip()}")
    execute_context(ctx)
    return None
