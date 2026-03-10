#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
函数绘图统一入口。

本模块职责：
1. 提供函数类标准 type 的统一调度入口。
2. 维持 registry 层和 server 层所需的稳定模块路径。
3. 将函数绘图能力收敛到表达式驱动的单一 handler。
"""

from __future__ import annotations

from typing import Callable

from shapes.functions import handle_function

from .tool_catalog import FUNCTION_TOOLS


# ========== 函数 handler 映射 ==========
FUNCTION_HANDLERS: dict[str, Callable[..., None]] = {
    "function": handle_function,
}


# ========== 对外兼容函数 ==========
def draw_function(page, draw_type: str, params: dict) -> str:
    """绘制函数图像。"""
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
