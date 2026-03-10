#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2D 几何绘图入口。

本模块职责：
1. 统一维护标准 2D type 到 handler 的调度映射。
2. 对外只暴露标准 2D type。
3. 保持 2D 绘图主路径与 registry 注册信息一致。
"""

from __future__ import annotations

from typing import Callable

from .tool_catalog import TOOLS_2D
from shapes.geometry_2d import (
    handle_angle_bisector,
    handle_arc,
    handle_circle,
    handle_ellipse,
    handle_hyperbola,
    handle_intersection,
    handle_line,
    handle_parabola,
    handle_perpendicular_line,
    handle_point,
    handle_point_on,
    handle_segment,
    handle_tangent,
)


# ========== 标准 2D handler 映射 ==========
STANDARD_HANDLERS_2D: dict[str, Callable[..., None]] = {
    "point": handle_point,
    "segment": handle_segment,
    "line": handle_line,
    "circle": handle_circle,
    "ellipse": handle_ellipse,
    "parabola": handle_parabola,
    "hyperbola": handle_hyperbola,
    "arc": handle_arc,
    "point_on": handle_point_on,
    "intersection": handle_intersection,
    "perpendicular_line": handle_perpendicular_line,
    "angle_bisector": handle_angle_bisector,
    "tangent": handle_tangent,
}


# ========== 统一 2D 调度入口 ==========
HANDLERS_2D: dict[str, Callable[..., None]] = STANDARD_HANDLERS_2D


def draw_2d_shape(page, draw_type: str, params: dict, skip_coord_init: bool = False) -> str:
    """按 draw_type 分发 2D 几何图形绘制。"""
    try:
        handler = HANDLERS_2D.get(draw_type)
        if handler is None:
            raise Exception(f"未知的 2D 绘制类型：{draw_type}")

        handler(page, draw_type, params, skip_coord_init=skip_coord_init)
        return None
    except Exception as exc:
        raise Exception(f"2D 图形绘制失败：{str(exc)}") from exc


def get_2d_tools():
    """返回对外暴露的标准 2D 工具列表。"""
    return list(TOOLS_2D)
