#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
函数绘图兼容入口。
本模块职责：
1. 保留历史模块名与函数签名，避免外部导入路径在重构后失效。
2. 将旧版 `draw_function(...)` 调度到新的 shapes 层精确 handler。
3. 继续提供函数工具列表，供 registry 层做覆盖校验与兼容查询。
"""

from __future__ import annotations

from typing import Callable

from tool_catalog import FUNCTION_TOOLS
from shapes.functions import (
    handle_cos_function,
    handle_cos_function_slider,
    handle_cubic_standard,
    handle_cubic_standard_slider,
    handle_exponential_function,
    handle_exponential_function_slider,
    handle_linear_general,
    handle_linear_general_slider,
    handle_logarithmic_function,
    handle_logarithmic_function_slider,
    handle_polynomial_function,
    handle_quadratic_standard,
    handle_quadratic_standard_slider,
    handle_sin_function,
    handle_sin_function_slider,
    handle_tan_function,
    handle_tan_function_slider,
)


# ========== 函数 handler 映射 ==========
# 旧版大 if/elif 已全部迁入 shapes 层，这里只保留名称到 handler 的精确映射。
FUNCTION_HANDLERS: dict[str, Callable[..., None]] = {
    "linear_general": handle_linear_general,
    "linear_general_slider": handle_linear_general_slider,
    "quadratic_standard": handle_quadratic_standard,
    "quadratic_standard_slider": handle_quadratic_standard_slider,
    "cubic_standard": handle_cubic_standard,
    "cubic_standard_slider": handle_cubic_standard_slider,
    "polynomial_function": handle_polynomial_function,
    "sin_function": handle_sin_function,
    "sin_function_slider": handle_sin_function_slider,
    "cos_function": handle_cos_function,
    "cos_function_slider": handle_cos_function_slider,
    "tan_function": handle_tan_function,
    "tan_function_slider": handle_tan_function_slider,
    "exponential_function": handle_exponential_function,
    "exponential_function_slider": handle_exponential_function_slider,
    "logarithmic_function": handle_logarithmic_function,
    "logarithmic_function_slider": handle_logarithmic_function_slider,
}


# ========== 兼容导出函数 ==========
def draw_function(page, draw_type: str, params: dict) -> str:
    """绘制函数图像。

    说明：
    1. 这里保留旧版函数签名，供历史调用方继续使用。
    2. 实际绘图逻辑已经全部下沉到 shapes/functions。

    Args:
        page: 当前 Playwright 页面对象
        draw_type: 函数类型
        params: 绘图参数字典

    Returns:
        None，保留旧版返回约定
    """
    try:
        handler = FUNCTION_HANDLERS.get(draw_type)
        if handler is None:
            raise Exception(f"未知的函数绘制类型：{draw_type}")

        handler(page, draw_type, params)
        return None
    except Exception as exc:
        raise Exception(f"函数绘制失败：{str(exc)}") from exc


def get_function_tools():
    """获取函数图像工具列表。"""
    return list(FUNCTION_TOOLS)
