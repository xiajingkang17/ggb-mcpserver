#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GeoGebra 绘图工具入口包。

本模块职责：
1. 汇总当前仓库的工具目录与分类调度入口。
2. 为 registry 和其他上层模块提供稳定的导入路径。
3. 将原先分散在根目录的工具入口文件收拢到统一包结构。
"""

from .tool_2d import draw_2d_shape, get_2d_tools
from .tool_3d import draw_3d_shape, get_3d_tools
from .tool_catalog import ALL_TOOLS, FUNCTION_TOOLS, TOOLS_2D, TOOLS_3D
from .tool_function import draw_function, get_function_tools

__all__ = [
    "ALL_TOOLS",
    "FUNCTION_TOOLS",
    "TOOLS_2D",
    "TOOLS_3D",
    "draw_2d_shape",
    "get_2d_tools",
    "draw_3d_shape",
    "get_3d_tools",
    "draw_function",
    "get_function_tools",
]
