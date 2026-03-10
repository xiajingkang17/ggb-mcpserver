"""
2D 多边形类 handler。

本模块职责：
1. 迁移由多个顶点组成的基础 2D 图形。
2. 保持旧实现中的“仅在提供坐标时创建点”约定。

当前包含：
- triangle_points
- polygon_points
"""

from __future__ import annotations

from .basic import _add_point_if_coordinates, _build_context
from shapes.common import execute_context


# ========== 2D 多边形类图形 ==========
def handle_triangle_points(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制由三个点确定的三角形。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    point1 = params.get("point1", {})
    point2 = params.get("point2", {})
    point3 = params.get("point3", {})

    p1_name = point1.get("name", "A")
    p2_name = point2.get("name", "B")
    p3_name = point3.get("name", "C")
    p1_coordinates = point1.get("coordinates", None)
    p2_coordinates = point2.get("coordinates", None)
    p3_coordinates = point3.get("coordinates", None)

    _add_point_if_coordinates(ctx, p1_name, p1_coordinates)
    _add_point_if_coordinates(ctx, p2_name, p2_coordinates)
    _add_point_if_coordinates(ctx, p3_name, p3_coordinates)

    ctx.collector.add(f"seg_{p1_name}{p2_name} = Segment[{p1_name}, {p2_name}]")
    ctx.collector.add(f"ShowLabel[seg_{p1_name}{p2_name}, false]")

    ctx.collector.add(f"seg_{p2_name}{p3_name} = Segment[{p2_name}, {p3_name}]")
    ctx.collector.add(f"ShowLabel[seg_{p2_name}{p3_name}, false]")

    ctx.collector.add(f"seg_{p3_name}{p1_name} = Segment[{p3_name}, {p1_name}]")
    ctx.collector.add(f"ShowLabel[seg_{p3_name}{p1_name}, false]")

    execute_context(ctx)
    return None


def handle_polygon_points(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制由多个顶点确定的 2D 多边形。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    vertices = params.get("vertices", [])
    if len(vertices) < 3:
        raise Exception("多边形至少需要3个顶点")

    point_names: list[str] = []
    for index, vertex in enumerate(vertices):
        name = vertex.get("name", f"Point{index + 1}")
        coordinates = vertex.get("coordinates", None)
        point_names.append(name)
        _add_point_if_coordinates(ctx, name, coordinates)

    point_count = len(point_names)
    for index in range(point_count):
        point1 = point_names[index]
        point2 = point_names[(index + 1) % point_count]
        segment_name = f"seg_{point1}{point2}"
        ctx.collector.add(f"{segment_name} = Segment[{point1}, {point2}]")
        ctx.collector.add(f"ShowLabel[{segment_name}, false]")

    execute_context(ctx)
    return None
