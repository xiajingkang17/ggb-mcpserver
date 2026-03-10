"""
GeoGebra 标准 2D 参数 schema。

本模块职责：
1. 定义标准 2D type 的精确 `params_schema`。
2. 统一 2D 核心几何语言的字段结构。
3. 为 registry 层提供可直接挂接的 2D schema 映射。
"""

from __future__ import annotations

from typing import Any

from .common import (
    coords_2d_schema,
    number_schema,
    object_pair_schema,
    object_ref_schema,
    pick_schema,
    placement_schema,
    point_pair_2d_schema,
    point_ref_2d_schema,
    point_triple_2d_schema,
    strict_object,
    string_schema,
)


# ========== 标准 2D params_schema ==========
def _focus_id_pair_schema(description: str) -> dict[str, Any]:
    """构建长度为 2 的焦点 id 数组 schema。"""
    return {
        "type": "array",
        "description": description,
        "items": string_schema("焦点对象 id"),
        "minItems": 2,
        "maxItems": 2,
    }


def build_standard_2d_params_schema_map() -> dict[str, dict[str, Any]]:
    """返回标准 2D type -> params_schema 映射。"""
    return {
        "point": strict_object(
            properties={
                "coords": coords_2d_schema("二维点坐标 [x, y]"),
            },
            required=["coords"],
            description="标准点参数",
        ),
        "segment": strict_object(
            properties={
                "endpoints": point_pair_2d_schema("线段两个端点"),
            },
            required=["endpoints"],
            description="标准线段参数",
        ),
        "line": strict_object(
            properties={
                "through": point_pair_2d_schema("直线经过的两个点"),
            },
            required=["through"],
            description="标准直线参数",
        ),
        "circle": strict_object(
            properties={
                "center": point_ref_2d_schema("圆心点引用"),
                "radius": number_schema("圆半径", positive_only=True),
            },
            required=["center", "radius"],
            description="标准圆参数",
        ),
        "ellipse": strict_object(
            properties={
                "center": point_ref_2d_schema("椭圆中心点引用"),
                "a": number_schema("椭圆参数 a", positive_only=True),
                "b": number_schema("椭圆参数 b", positive_only=True),
                "focus_ids": _focus_id_pair_schema("椭圆两个焦点的对象 id"),
            },
            required=["center", "a", "b", "focus_ids"],
            description="标准椭圆参数",
        ),
        "parabola": strict_object(
            properties={
                "vertex": point_ref_2d_schema("抛物线顶点引用"),
                "focus": point_ref_2d_schema("抛物线焦点引用"),
            },
            required=["vertex", "focus"],
            description="标准抛物线参数",
        ),
        "hyperbola": strict_object(
            properties={
                "center": point_ref_2d_schema("双曲线中心点引用"),
                "a": number_schema("双曲线参数 a", positive_only=True),
                "b": number_schema("双曲线参数 b", positive_only=True),
                "focus_ids": _focus_id_pair_schema("双曲线两个焦点的对象 id"),
            },
            required=["center", "a", "b", "focus_ids"],
            description="标准双曲线参数",
        ),
        "arc": strict_object(
            properties={
                "kind": {
                    "type": "string",
                    "enum": ["minor", "major"],
                    "description": "弧类型，支持 minor（劣弧）和 major（优弧）",
                    "default": "minor",
                },
                "center": point_ref_2d_schema("弧心点引用"),
                "start": point_ref_2d_schema("弧起点引用"),
                "end": point_ref_2d_schema("弧终点引用"),
            },
            required=["center", "start", "end"],
            description="标准圆弧参数",
        ),
        "point_on": strict_object(
            properties={
                "object": object_ref_schema("承载该点的目标对象"),
                "placement": placement_schema(),
            },
            required=["object"],
            description="标准对象上点参数",
        ),
        "intersection": strict_object(
            properties={
                "objects": object_pair_schema("两个求交对象"),
                "pick": pick_schema(),
            },
            required=["objects"],
            description="标准交点参数",
        ),
        "perpendicular_line": strict_object(
            properties={
                "through": point_ref_2d_schema("垂线经过的点"),
                "target": string_schema("目标直线对象 id"),
            },
            required=["through", "target"],
            description="标准垂线参数",
        ),
        "angle_bisector": strict_object(
            properties={
                "points": point_triple_2d_schema("角平分线对应的三个点，第二个点为顶点"),
            },
            required=["points"],
            description="标准角平分线参数",
        ),
        "tangent": strict_object(
            properties={
                "through": point_ref_2d_schema("切线经过的点"),
                "target": string_schema("目标圆锥曲线对象 id"),
                "pick": pick_schema(),
            },
            required=["through", "target"],
            description="标准切线参数",
        ),
    }
