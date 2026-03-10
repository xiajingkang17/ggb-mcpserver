#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2D 几何绘图兼容入口。
本模块职责：
1. 保留历史模块名与函数签名，避免外部导入路径在重构后失效。
2. 将旧版 `draw_2d_shape(...)` 调度到新的 shapes 层精确 handler。
3. 继续提供 2D 工具列表，供 registry 层做覆盖校验与兼容查询。
"""

from __future__ import annotations

from typing import Callable

from tool_catalog import TOOLS_2D
from shapes.geometry_2d import (
    handle_angle_bisector,
    handle_circle_center_radius,
    handle_ellipse_equation,
    handle_hyperbola_equation,
    handle_intersect_2d,
    handle_line,
    handle_parabola_equation,
    handle_perpendicular_line,
    handle_point_2d,
    handle_point_on_object,
    handle_polygon_points,
    handle_segment,
    handle_tangent,
    handle_triangle_points,
)


# ========== 2D handler 映射 ==========
# 旧版大 if/elif 已全部迁入 shapes 层，这里只保留名称到 handler 的精确映射。
HANDLERS_2D: dict[str, Callable[..., None]] = {
    "point_2d": handle_point_2d,
    "point_on_object": handle_point_on_object,
    "segment": handle_segment,
    "line": handle_line,
    "circle_center_radius": handle_circle_center_radius,
    "triangle_points": handle_triangle_points,
    "polygon_points": handle_polygon_points,
    "ellipse_equation": handle_ellipse_equation,
    "parabola_equation": handle_parabola_equation,
    "hyperbola_equation": handle_hyperbola_equation,
    "intersect_2d": handle_intersect_2d,
    "tangent": handle_tangent,
    "angle_bisector": handle_angle_bisector,
    "perpendicular_line": handle_perpendicular_line,
}


# ========== 兼容导出函数 ==========
def draw_2d_shape(page, draw_type: str, params: dict, skip_coord_init: bool = False) -> str:
    """绘制 2D 几何图形。

    说明：
    1. 这里保留旧版函数签名，供历史调用方继续使用。
    2. 实际绘图逻辑已经全部下沉到 shapes/geometry_2d。

    Args:
        page: 当前 Playwright 页面对象
        draw_type: 2D 图形类型
        params: 图形参数字典
        skip_coord_init: 是否跳过 2D 坐标系初始化

    Returns:
        None，保留旧版返回约定
    """
    try:
        handler = HANDLERS_2D.get(draw_type)
        if handler is None:
            raise Exception(f"未知的2D绘制类型：{draw_type}")

        handler(page, draw_type, params, skip_coord_init=skip_coord_init)
        return None
    except Exception as exc:
        raise Exception(f"2D图形绘制失败：{str(exc)}") from exc


def get_2d_tools():
    """获取 2D 几何工具列表。"""
    return list(TOOLS_2D)
