"""
3D 立体图形基础 handler。

本模块职责：
1. 先迁移最简单的 3D 立体图形。
2. 保持旧实现中的命令形式与对象创建顺序不变。

当前包含：
- sphere_center_radius
- cylinder_radius_height
- cone_radius_height
- pyramid_all_vertices
- prism_all_vertices
"""

from __future__ import annotations

from .basic import _add_point_if_coordinates, _build_context
from shapes.common import execute_context


# ========== 3D 立体图形 ==========
def handle_sphere_center_radius(page, draw_type: str, params: dict) -> None:
    """绘制球心半径形式的球体。"""
    ctx = _build_context(page)

    center = params.get("center", {})
    center_name = center.get("name", "O")
    center_coordinates = center.get("coordinates", None)
    radius = params.get("radius", 1)

    _add_point_if_coordinates(ctx, center_name, center_coordinates)
    ctx.collector.add(f"Sphere[{center_name}, {radius}]")

    execute_context(ctx)
    return None


def handle_cylinder_radius_height(page, draw_type: str, params: dict) -> None:
    """绘制圆柱。"""
    ctx = _build_context(page)

    center_param = params.get("center", [0, 0, 0])
    radius = params.get("radius", 1)
    height = params.get("height", 2)

    if isinstance(center_param, dict):
        center_name = center_param.get("name", "C")
        center_coordinates = center_param.get("coordinates", None)
        if center_coordinates is not None:
            x, y, z = center_coordinates
            _add_point_if_coordinates(ctx, center_name, center_coordinates)
        else:
            x, y, z = 0, 0, 0
    else:
        center_name = "C"
        x, y, z = center_param
        _add_point_if_coordinates(ctx, center_name, center_param)

    ctx.collector.add(f"P_cyl = ({x + radius}, {y}, {z})")
    ctx.collector.add(f"circle_cyl = Circle[{center_name}, P_cyl]")
    ctx.collector.add(f"Cylinder[circle_cyl, {height}]")

    execute_context(ctx)
    return None


def handle_cone_radius_height(page, draw_type: str, params: dict) -> None:
    """绘制圆锥。"""
    ctx = _build_context(page)

    center_param = params.get("center", [0, 0, 0])
    radius = params.get("radius", 1)
    height = params.get("height", 2)

    if isinstance(center_param, dict):
        center_name = center_param.get("name", "C")
        center_coordinates = center_param.get("coordinates", None)
        if center_coordinates is not None:
            x, y, z = center_coordinates
            _add_point_if_coordinates(ctx, center_name, center_coordinates)
        else:
            x, y, z = 0, 0, 0
    else:
        center_name = "C"
        x, y, z = center_param
        _add_point_if_coordinates(ctx, center_name, center_param)

    ctx.collector.add(f"P_cone = ({x + radius}, {y}, {z})")
    ctx.collector.add(f"circle_cone = Circle[{center_name}, P_cone]")
    ctx.collector.add(f"Cone[circle_cone, {height}]")

    execute_context(ctx)
    return None


def handle_pyramid_all_vertices(page, draw_type: str, params: dict) -> None:
    """绘制棱锥及其全部边。"""
    ctx = _build_context(page)

    vertices = params.get("vertices", [])
    if len(vertices) < 4:
        raise Exception("棱锥至少需要4个顶点")

    point_names: list[str] = []
    for index, vertex in enumerate(vertices):
        name = vertex.get("name", f"P{index + 1}")
        coordinates = vertex.get("coordinates", None)
        point_names.append(name)
        _add_point_if_coordinates(ctx, name, coordinates)

    apex_name = point_names[-1]
    base_points = point_names[:-1]

    point_count = len(base_points)
    for index in range(point_count):
        point1 = base_points[index]
        point2 = base_points[(index + 1) % point_count]
        segment_name = f"seg_{point1}{point2}"
        ctx.collector.add(f"{segment_name} = Segment[{point1}, {point2}]")
        ctx.collector.add(f"SetLabelStyle[{segment_name}, 0]")
        ctx.collector.add(f"SetLabelVisible[{segment_name}, false]")

    for base_point in base_points:
        segment_name = f"seg_{apex_name}{base_point}"
        ctx.collector.add(f"{segment_name} = Segment[{apex_name}, {base_point}]")
        ctx.collector.add(f"SetLabelStyle[{segment_name}, 0]")
        ctx.collector.add(f"SetLabelVisible[{segment_name}, false]")

    execute_context(ctx)
    return None


def handle_prism_all_vertices(page, draw_type: str, params: dict) -> None:
    """绘制棱柱及其全部边。"""
    ctx = _build_context(page)

    vertices = params.get("vertices", [])
    if len(vertices) < 6:
        raise Exception("棱柱至少需要6个顶点（3个底面 + 3个顶面）")

    point_names: list[str] = []
    for index, vertex in enumerate(vertices):
        name = vertex.get("name", f"P{index + 1}")
        coordinates = vertex.get("coordinates", None)
        point_names.append(name)
        _add_point_if_coordinates(ctx, name, coordinates)

    point_count = len(point_names) // 2
    base_points = point_names[:point_count]
    top_points = point_names[point_count:]

    for index in range(point_count):
        point1 = base_points[index]
        point2 = base_points[(index + 1) % point_count]
        segment_name = f"seg_{point1}{point2}"
        ctx.collector.add(f"{segment_name} = Segment[{point1}, {point2}]")
        ctx.collector.add(f"SetLabelStyle[{segment_name}, 0]")
        ctx.collector.add(f"SetLabelVisible[{segment_name}, false]")

    for index in range(point_count):
        point1 = top_points[index]
        point2 = top_points[(index + 1) % point_count]
        segment_name = f"seg_{point1}{point2}"
        ctx.collector.add(f"{segment_name} = Segment[{point1}, {point2}]")
        ctx.collector.add(f"SetLabelStyle[{segment_name}, 0]")
        ctx.collector.add(f"SetLabelVisible[{segment_name}, false]")

    for index in range(point_count):
        base_point = base_points[index]
        top_point = top_points[index]
        segment_name = f"seg_{base_point}{top_point}"
        ctx.collector.add(f"{segment_name} = Segment[{base_point}, {top_point}]")
        ctx.collector.add(f"SetLabelStyle[{segment_name}, 0]")
        ctx.collector.add(f"SetLabelVisible[{segment_name}, false]")

    execute_context(ctx)
    return None
