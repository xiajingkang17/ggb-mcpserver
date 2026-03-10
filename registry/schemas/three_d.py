"""
GeoGebra 标准 3D 参数 schema。

本模块职责：
1. 定义标准 3D type 的精确 `params_schema`。
2. 统一 3D 核心几何语言的字段结构。
3. 为 registry 层提供可直接挂接的 3D schema 映射。
"""

from __future__ import annotations

from typing import Any

from .common import (
    coords_3d_schema,
    number_schema,
    object_ref_schema,
    placement_schema,
    point_pair_3d_schema,
    point_ref_3d_schema,
    strict_object,
)


# ========== 标准 3D params_schema ==========
def build_standard_3d_params_schema_map() -> dict[str, dict[str, Any]]:
    """返回标准 3D type -> params_schema 映射。"""
    return {
        "point_3d": strict_object(
            properties={
                "coords": coords_3d_schema("三维点坐标 [x, y, z]"),
            },
            required=["coords"],
            description="标准 3D 点参数",
        ),
        "segment_3d": strict_object(
            properties={
                "endpoints": point_pair_3d_schema("3D 线段两个端点"),
            },
            required=["endpoints"],
            description="标准 3D 线段参数",
        ),
        "point_on_3d": strict_object(
            properties={
                "object": object_ref_schema("承载该点的 3D 目标对象"),
                "placement": placement_schema(),
            },
            required=["object"],
            description="标准 3D 对象上点参数",
        ),
        "sphere": strict_object(
            properties={
                "center": point_ref_3d_schema("球心点引用"),
                "radius": number_schema("球半径", positive_only=True),
            },
            required=["center", "radius"],
            description="标准球体参数",
        ),
        "cylinder": strict_object(
            properties={
                "center": point_ref_3d_schema("底面圆心点引用"),
                "radius": number_schema("底面圆半径", positive_only=True),
                "height": number_schema("圆柱高度", positive_only=True),
            },
            required=["center", "radius", "height"],
            description="标准圆柱参数",
        ),
        "cone": strict_object(
            properties={
                "center": point_ref_3d_schema("底面圆心点引用"),
                "radius": number_schema("底面圆半径", positive_only=True),
                "height": number_schema("圆锥高度", positive_only=True),
            },
            required=["center", "radius", "height"],
            description="标准圆锥参数",
        ),
    }
