"""
3D 基础图形 handler。

本模块职责：
1. 处理最基础的一批 3D 图形。
2. 让这些图形先从 tools_3d_new.py 的大 if/elif 分支中迁出。
3. 为后续 3D shapes 继续拆分提供样板。

当前包含：
- point_3d
- segment_3d
- point_on_segment_3d
- polygon_3d
"""

from __future__ import annotations

from shapes.common import CommandCollector, ShapeContext, execute_context
from shapes.scene import initialize_geometry_3d_scene


# ========== 3D 基础执行辅助 ==========
def _build_context(page) -> ShapeContext:
    """创建 3D 基础图形 handler 使用的执行上下文。"""
    initialize_geometry_3d_scene(page)
    return ShapeContext(page=page, collector=CommandCollector())


def _add_point_if_coordinates(
    ctx: ShapeContext,
    point_name: str,
    point_coordinates,
) -> None:
    """仅在提供坐标时创建 3D 点。"""
    if point_coordinates is None:
        return

    x, y, z = point_coordinates
    ctx.collector.add(f"{point_name} = ({x}, {y}, {z})")
    ctx.collector.add(f"SetLabelStyle[{point_name}, 0]")
    ctx.collector.add(f"SetLabelVisible[{point_name}, true]")


# ========== 3D 基础图形 ==========
def handle_point_3d(page, draw_type: str, params: dict) -> None:
    """绘制 3D 点。"""
    ctx = _build_context(page)

    point = params.get("point", {})
    name = point.get("name", "A")
    x, y, z = point.get("coordinates", [0, 0, 0])

    ctx.collector.add(f"{name} = ({x}, {y}, {z})")
    ctx.collector.add(f"SetLabelStyle[{name}, 0]")
    ctx.collector.add(f"SetLabelVisible[{name}, true]")

    execute_context(ctx)
    return None


def handle_segment_3d(page, draw_type: str, params: dict) -> None:
    """绘制 3D 线段。"""
    ctx = _build_context(page)

    point1 = params.get("point1", {})
    point2 = params.get("point2", {})
    p1_name = point1.get("name", "A")
    p2_name = point2.get("name", "B")
    p1_coordinates = point1.get("coordinates", None)
    p2_coordinates = point2.get("coordinates", None)

    _add_point_if_coordinates(ctx, p1_name, p1_coordinates)
    _add_point_if_coordinates(ctx, p2_name, p2_coordinates)

    segment_name = f"seg_{p1_name}{p2_name}"
    ctx.collector.add(f"{segment_name} = Segment[{p1_name}, {p2_name}]")

    execute_context(ctx)
    return None


def handle_point_on_segment_3d(page, draw_type: str, params: dict) -> None:
    """在线段上创建 3D 动点。"""
    ctx = _build_context(page)

    point_name = params.get("point_name", "P")
    segment_name = params.get("segment", None)
    parameter = params.get("parameter", None)
    slider = params.get("slider", None)

    if not segment_name:
        raise Exception("point_on_segment_3d需要提供segment参数（线段名称）")

    if parameter is not None:
        ctx.collector.add(f"{point_name} = Point[{segment_name}, {parameter}]")
    elif slider is not None:
        slider_name = slider.get("name", f"t_{point_name}")
        slider_min = slider.get("min", 0)
        slider_max = slider.get("max", 1)
        slider_step = slider.get("step", 0.01)
        slider_init = slider.get("init", slider_min)

        ctx.collector.add(
            f"{slider_name} = Slider[{slider_min}, {slider_max}, {slider_step}]"
        )
        ctx.collector.add(f"SetValue[{slider_name}, {slider_init}]")
        ctx.collector.add(f"SetLabelStyle[{slider_name}, 0]")
        ctx.collector.add(f"SetLabelVisible[{slider_name}, true]")
        ctx.collector.add(f"ShowLabel[{slider_name}, true]")
        ctx.collector.add(f"SetVisibleInView[{slider_name}, 1, true]")
        ctx.collector.add(f"{point_name} = Point[{segment_name}, {slider_name}]")
    else:
        slider_name = f"t_{point_name}"
        slider_min, slider_max, slider_step, slider_init = 0, 1, 0.01, 0.5

        ctx.collector.add(
            f"{slider_name} = Slider[{slider_min}, {slider_max}, {slider_step}]"
        )
        ctx.collector.add(f"SetValue[{slider_name}, {slider_init}]")
        ctx.collector.add(f"SetLabelStyle[{slider_name}, 0]")
        ctx.collector.add(f"SetLabelVisible[{slider_name}, true]")
        ctx.collector.add(f"ShowLabel[{slider_name}, true]")
        ctx.collector.add(f"SetVisibleInView[{slider_name}, 1, true]")
        ctx.collector.add(f"{point_name} = Point[{segment_name}, {slider_name}]")

    ctx.collector.add(f"SetLabelStyle[{point_name}, 0]")
    ctx.collector.add(f"SetLabelVisible[{point_name}, true]")

    execute_context(ctx)
    return None


def handle_polygon_3d(page, draw_type: str, params: dict) -> None:
    """绘制 3D 多边形。"""
    ctx = _build_context(page)

    vertices = params.get("vertices", [])
    if len(vertices) < 3:
        raise Exception("3D多边形至少需要3个顶点")

    point_names: list[str] = []
    for index, vertex in enumerate(vertices):
        name = vertex.get("name", f"Point{index + 1}")
        coordinates = vertex.get("coordinates", None)
        point_names.append(name)
        _add_point_if_coordinates(ctx, name, coordinates)

    names = ", ".join(point_names)
    ctx.collector.add(f"Polygon[{names}]")

    execute_context(ctx)
    return None
