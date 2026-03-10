#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3D 几何绘图兼容入口。
本模块职责：
1. 保留历史模块名与函数签名，避免外部导入路径在重构后失效。
2. 将旧版 `draw_3d_shape(...)` 调度到新的 shapes 层精确 handler。
3. 继续提供 3D 工具列表，供 registry 层做覆盖校验与兼容查询。
"""

from __future__ import annotations

from typing import Callable

from tool_catalog import TOOLS_3D
from shapes.geometry_3d import (
    handle_cone_radius_height,
    handle_cylinder_radius_height,
    handle_point_3d,
    handle_point_on_segment_3d,
    handle_polygon_3d,
    handle_prism_all_vertices,
    handle_pyramid_all_vertices,
    handle_segment_3d,
    handle_sphere_center_radius,
)


# ========== 3D handler 映射 ==========
# 旧版大 if/elif 已全部迁入 shapes 层，这里只保留名称到 handler 的精确映射。
HANDLERS_3D: dict[str, Callable[..., None]] = {
    "point_3d": handle_point_3d,
    "segment_3d": handle_segment_3d,
    "point_on_segment_3d": handle_point_on_segment_3d,
    "polygon_3d": handle_polygon_3d,
    "sphere_center_radius": handle_sphere_center_radius,
    "cylinder_radius_height": handle_cylinder_radius_height,
    "cone_radius_height": handle_cone_radius_height,
    "pyramid_all_vertices": handle_pyramid_all_vertices,
    "prism_all_vertices": handle_prism_all_vertices,
}


# ========== 兼容导出函数 ==========
def draw_3d_shape(page, draw_type: str, params: dict) -> str:
    """绘制 3D 几何图形。

    说明：
    1. 这里保留旧版函数签名，供历史调用方继续使用。
    2. 实际绘图逻辑已经全部下沉到 shapes/geometry_3d。

    Args:
        page: 当前 Playwright 页面对象
        draw_type: 3D 图形类型
        params: 图形参数字典

    Returns:
        None，保留旧版返回约定
    """
    try:
        handler = HANDLERS_3D.get(draw_type)
        if handler is None:
            raise Exception(f"未知的3D绘制类型：{draw_type}")

        handler(page, draw_type, params)
        return None
    except Exception as exc:
        raise Exception(f"3D图形绘制失败：{str(exc)}") from exc


def get_3d_tools():
    """获取 3D 几何工具列表。"""
    return list(TOOLS_3D)
