#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GeoGebra 工具目录清单。

本模块职责：
1. 统一维护当前仓库支持的工具名称清单。
2. 以标准 type 作为目录主语言。
3. 为 registry、schema 和调度层提供稳定的枚举来源。
"""

# ========== 函数工具清单 ==========
FUNCTION_TOOLS = (
    "function",
)


# ========== 2D 标准工具清单 ==========
TOOLS_2D = (
    "point",
    "segment",
    "line",
    "circle",
    "ellipse",
    "parabola",
    "hyperbola",
    "arc",
    "point_on",
    "intersection",
    "perpendicular_line",
    "angle_bisector",
    "tangent",
)


# ========== 3D 工具清单 ==========
TOOLS_3D = (
    "point_3d",
    "segment_3d",
    "point_on_3d",
    "sphere",
    "cylinder",
    "cone",
)


# ========== 全量工具清单 ==========
ALL_TOOLS = FUNCTION_TOOLS + TOOLS_2D + TOOLS_3D
