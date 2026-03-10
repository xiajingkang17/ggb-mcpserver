"""
2D 基础图形 handler。

本模块职责：
1. 处理最基础、最稳定的一批 2D 图形。
2. 让这些图形先从 tools_2d_new.py 的大 if/elif 分支中迁出。
3. 作为后续拆分 2D shapes 的样板模块。

当前包含：
- point_2d
- segment
- line
"""

from __future__ import annotations

from shapes.common import CommandCollector, ShapeContext, execute_context
from shapes.scene import initialize_geometry_2d_scene


# ========== 2D 基础执行辅助 ==========
def _build_context(page, skip_coord_init: bool = False) -> ShapeContext:
    """创建 2D 基础图形 handler 使用的执行上下文。"""
    if not skip_coord_init:
        initialize_geometry_2d_scene(page)

    return ShapeContext(
        page=page,
        collector=CommandCollector(),
        skip_coord_init=skip_coord_init,
    )


def _add_point_if_coordinates(
    ctx: ShapeContext,
    point_name: str,
    point_coordinates,
) -> None:
    """仅在提供坐标时创建 2D 点。

    说明：
    这里保留旧实现中的约定。
    如果调用方只传名称、不传坐标，则认为该点可能已在当前构造中存在，不重复创建。
    """
    if point_coordinates is None:
        return

    x, y = point_coordinates[0], point_coordinates[1]
    ctx.collector.add(f"{point_name} = ({x}, {y})")
    ctx.collector.add(f"ShowLabel[{point_name}, true]")


# ========== 2D 基础图形 ==========
def handle_point_2d(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制 2D 点。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    point = params.get("point", {})
    name = point.get("name", "A")
    coordinates = point.get("coordinates", [0, 0])
    x, y = coordinates[0], coordinates[1]

    ctx.collector.add(f"{name} = ({x}, {y})")
    ctx.collector.add(f"ShowLabel[{name}, true]")

    execute_context(ctx)
    return None


def handle_segment(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制 2D 线段。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

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
    ctx.collector.add(f"ShowLabel[{segment_name}, false]")

    execute_context(ctx)
    return None


def handle_line(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制 2D 直线。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    point1 = params.get("point1", {})
    point2 = params.get("point2", {})
    p1_name = point1.get("name", "A")
    p2_name = point2.get("name", "B")
    p1_coordinates = point1.get("coordinates", None)
    p2_coordinates = point2.get("coordinates", None)

    _add_point_if_coordinates(ctx, p1_name, p1_coordinates)
    _add_point_if_coordinates(ctx, p2_name, p2_coordinates)

    line_name = f"line_{p1_name}{p2_name}"
    ctx.collector.add(f"{line_name} = Line[{p1_name}, {p2_name}]")
    ctx.collector.add(f"ShowLabel[{line_name}, false]")

    execute_context(ctx)
    return None
