"""
2D 基础图形 handlers。

本模块职责：
1. 处理 point / segment / line 三类标准 2D 基础对象。
2. 保持原有 GeoGebra 构造逻辑不变，只统一参数格式。
3. 统一由步骤 id 作为对象名，便于后续步骤直接引用。
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
    """仅在提供坐标时创建 2D 点。"""
    if point_coordinates is None:
        return

    if not isinstance(point_coordinates, (list, tuple)) or len(point_coordinates) != 2:
        raise Exception("点坐标必须是长度为 2 的数组或元组")

    x, y = point_coordinates[0], point_coordinates[1]
    ctx.collector.add(f"{point_name} = ({x}, {y})")


def _require_step_id(params: dict, draw_type: str) -> str:
    """获取当前标准步骤对应的对象名。"""
    step_id = params.get("id")
    if not isinstance(step_id, str) or not step_id.strip():
        raise Exception(f"{draw_type} 需要提供明确的 id，不能依赖隐式命名")
    return step_id.strip()


def _resolve_point_ref(point_ref) -> tuple[str, object]:
    """解析标准参数中的点引用。

    标准写法只保留两种：
    1. 直接传点 id 字符串，例如 `"A"`
    2. 传 `{"id": "A", "coords": [0, 1]}`，在引用前按需补点
    """
    if isinstance(point_ref, str):
        return point_ref, None

    if isinstance(point_ref, dict):
        point_name = point_ref.get("id")
        if not point_name:
            raise Exception("点引用对象必须提供 id")
        return point_name, point_ref.get("coords")

    raise Exception("点引用必须是字符串或包含 id 的对象")


# ========== 2D 基础图形 ==========
def handle_point(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制标准格式的 2D 点。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    point_name = _require_step_id(params, "point")
    coordinates = params.get("coords")
    if coordinates is None:
        raise Exception("point 需要提供 coords")
    if not isinstance(coordinates, (list, tuple)) or len(coordinates) != 2:
        raise Exception("point.coords 必须是长度为 2 的数组或元组")

    x, y = coordinates[0], coordinates[1]
    ctx.collector.add(f"{point_name} = ({x}, {y})")

    execute_context(ctx)


def handle_segment(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制标准格式的 2D 线段。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    endpoints = params.get("endpoints")
    if not isinstance(endpoints, (list, tuple)) or len(endpoints) != 2:
        raise Exception("segment 需要提供 endpoints，且长度为 2")

    p1_name, p1_coordinates = _resolve_point_ref(endpoints[0])
    p2_name, p2_coordinates = _resolve_point_ref(endpoints[1])

    # 沿用原实现：只有在提供坐标时才补建端点。
    _add_point_if_coordinates(ctx, p1_name, p1_coordinates)
    _add_point_if_coordinates(ctx, p2_name, p2_coordinates)

    segment_name = _require_step_id(params, "segment")
    ctx.collector.add(f"{segment_name} = Segment[{p1_name}, {p2_name}]")

    execute_context(ctx)


def handle_line(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制标准格式的 2D 直线。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    through = params.get("through")
    if not isinstance(through, (list, tuple)) or len(through) != 2:
        raise Exception("line 需要提供 through，且长度为 2")

    p1_name, p1_coordinates = _resolve_point_ref(through[0])
    p2_name, p2_coordinates = _resolve_point_ref(through[1])

    # 沿用原实现：直线只负责连结两点，不主动改写点对象。
    _add_point_if_coordinates(ctx, p1_name, p1_coordinates)
    _add_point_if_coordinates(ctx, p2_name, p2_coordinates)

    line_name = _require_step_id(params, "line")
    ctx.collector.add(f"{line_name} = Line[{p1_name}, {p2_name}]")

    execute_context(ctx)
