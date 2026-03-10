#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3D 几何绘图入口。

本模块职责：
1. 统一维护标准 3D type 到 handler 的调度映射。
2. 对外只暴露标准 3D type。
3. 保持 3D 绘图主路径与 registry 注册信息一致。
"""

from __future__ import annotations

from typing import Callable

from .tool_catalog import TOOLS_3D
from shapes.geometry_3d import (
    handle_cone,
    handle_cylinder,
    handle_point_3d,
    handle_point_on_3d,
    handle_segment_3d,
    handle_sphere,
)


# ========== 标准 3D handler 映射 ==========
HANDLERS_3D: dict[str, Callable[..., None]] = {
    "point_3d": handle_point_3d,
    "segment_3d": handle_segment_3d,
    "point_on_3d": handle_point_on_3d,
    "sphere": handle_sphere,
    "cylinder": handle_cylinder,
    "cone": handle_cone,
}


# ========== 统一 3D 调度入口 ==========
def draw_3d_shape(page, draw_type: str, params: dict) -> str:
    """按 draw_type 分发 3D 几何图形绘制。"""
    try:
        handler = HANDLERS_3D.get(draw_type)
        if handler is None:
            raise Exception(f"未知的 3D 绘制类型：{draw_type}")

        handler(page, draw_type, params)
        return None
    except Exception as exc:
        raise Exception(f"3D 图形绘制失败：{str(exc)}") from exc


def get_3d_tools():
    """返回对外暴露的标准 3D 工具列表。"""
    return list(TOOLS_3D)
