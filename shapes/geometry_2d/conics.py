"""
2D 圆锥曲线与弧 handlers。

本模块职责：
1. 处理 circle / ellipse / parabola / hyperbola / arc 五类标准 2D 对象。
2. 延续原实现的几何构造逻辑，不改变作图结果。
3. 统一对象命名方式，使后续步骤可以直接通过 id 引用。
"""

from __future__ import annotations

import math

from .basic import _add_point_if_coordinates, _build_context
from shapes.common import execute_context


# ========== 2D 圆锥曲线辅助逻辑 ==========
def _resolve_named_point(point_param, param_name: str) -> tuple[str, object]:
    """解析标准参数中的点引用。"""
    if point_param is None:
        raise Exception(f"{param_name} 需要提供点引用")

    if isinstance(point_param, str):
        return point_param, None

    if isinstance(point_param, dict):
        point_name = point_param.get("id")
        if not point_name:
            raise Exception(f"{param_name} 点对象必须提供 id")
        point_coordinates = point_param.get("coords")
        return point_name, point_coordinates

    raise Exception(f"{param_name} 必须是字符串或包含 id 的对象")


def _require_step_id(params: dict, draw_type: str) -> str:
    """获取当前标准步骤对应的对象名。"""
    step_id = params.get("id")
    if not isinstance(step_id, str) or not step_id.strip():
        raise Exception(f"{draw_type} 需要提供明确的 id，不能依赖隐式命名")
    return step_id.strip()


def _resolve_focus_ids(params: dict, draw_type: str) -> tuple[str, str]:
    """解析椭圆/双曲线显式提供的焦点 id。"""
    focus_ids = params.get("focus_ids")
    if not isinstance(focus_ids, (list, tuple)) or len(focus_ids) != 2:
        raise Exception(f"{draw_type} 需要提供 focus_ids，且长度为 2")

    focus1_name = focus_ids[0]
    focus2_name = focus_ids[1]
    if not isinstance(focus1_name, str) or not focus1_name.strip():
        raise Exception(f"{draw_type}.focus_ids[0] 必须是非空字符串")
    if not isinstance(focus2_name, str) or not focus2_name.strip():
        raise Exception(f"{draw_type}.focus_ids[1] 必须是非空字符串")

    return focus1_name.strip(), focus2_name.strip()


# ========== 2D 圆锥曲线与弧 ==========
def handle_circle(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制标准格式的圆。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    center_name, center_coordinates = _resolve_named_point(params.get("center"), "circle.center")
    radius = params.get("radius")
    if radius is None:
        raise Exception("circle 需要提供 radius")

    _add_point_if_coordinates(ctx, center_name, center_coordinates)

    circle_name = _require_step_id(params, "circle")
    ctx.collector.add(f"{circle_name} = Circle[{center_name}, {radius}]")

    execute_context(ctx)


def handle_ellipse(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制标准格式的椭圆。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    center_name, center_coordinates = _resolve_named_point(
        params.get("center"),
        "ellipse.center",
    )
    a = params.get("a")
    b = params.get("b")
    if a is None or b is None:
        raise Exception("ellipse 需要提供 a 和 b")

    # 延续原实现：通过两焦点 + 半长轴长度构造 GeoGebra 椭圆。
    semimajor = max(a, b)
    focus_distance = math.sqrt(abs(a * a - b * b))
    ellipse_name = _require_step_id(params, "ellipse")
    focus1_name, focus2_name = _resolve_focus_ids(params, "ellipse")

    if center_coordinates is not None:
        cx, cy = center_coordinates[0], center_coordinates[1]
        _add_point_if_coordinates(ctx, center_name, center_coordinates)
        if a >= b:
            ctx.collector.add(f"{focus1_name} = ({cx - focus_distance}, {cy})")
            ctx.collector.add(f"{focus2_name} = ({cx + focus_distance}, {cy})")
        else:
            ctx.collector.add(f"{focus1_name} = ({cx}, {cy - focus_distance})")
            ctx.collector.add(f"{focus2_name} = ({cx}, {cy + focus_distance})")
    else:
        if a >= b:
            ctx.collector.add(
                f"{focus1_name} = (x({center_name}) - {focus_distance}, y({center_name}))"
            )
            ctx.collector.add(
                f"{focus2_name} = (x({center_name}) + {focus_distance}, y({center_name}))"
            )
        else:
            ctx.collector.add(
                f"{focus1_name} = (x({center_name}), y({center_name}) - {focus_distance})"
            )
            ctx.collector.add(
                f"{focus2_name} = (x({center_name}), y({center_name}) + {focus_distance})"
            )

    ctx.collector.add(f"{ellipse_name} = Ellipse[{focus1_name}, {focus2_name}, {semimajor}]")

    execute_context(ctx)


def handle_parabola(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制标准格式的抛物线。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    vertex_name, vertex_coordinates = _resolve_named_point(
        params.get("vertex"),
        "parabola.vertex",
    )
    focus_name, focus_coordinates = _resolve_named_point(
        params.get("focus"),
        "parabola.focus",
    )

    _add_point_if_coordinates(ctx, vertex_name, vertex_coordinates)
    _add_point_if_coordinates(ctx, focus_name, focus_coordinates)

    parabola_name = _require_step_id(params, "parabola")
    directrix_name = f"dir_{parabola_name}"
    # 保持旧实现的命令构造顺序：先做与轴垂直的准线，再生成抛物线。
    ctx.collector.add(
        f"{directrix_name} = PerpendicularLine[{vertex_name}, Line[{focus_name}, {vertex_name}]]"
    )
    ctx.collector.add(f"{parabola_name} = Parabola[{focus_name}, {directrix_name}]")

    execute_context(ctx)


def handle_hyperbola(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制标准格式的双曲线。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    center_name, center_coordinates = _resolve_named_point(
        params.get("center"),
        "hyperbola.center",
    )
    a = params.get("a")
    b = params.get("b")
    if a is None or b is None:
        raise Exception("hyperbola 需要提供 a 和 b")

    # 延续原实现：通过两焦点 + 实半轴长度构造 GeoGebra 双曲线。
    semimajor = max(a, b)
    focus_distance = math.sqrt(a * a + b * b)
    hyperbola_name = _require_step_id(params, "hyperbola")
    focus1_name, focus2_name = _resolve_focus_ids(params, "hyperbola")

    if center_coordinates is not None:
        cx, cy = center_coordinates[0], center_coordinates[1]
        _add_point_if_coordinates(ctx, center_name, center_coordinates)
        if a >= b:
            ctx.collector.add(f"{focus1_name} = ({cx - focus_distance}, {cy})")
            ctx.collector.add(f"{focus2_name} = ({cx + focus_distance}, {cy})")
        else:
            ctx.collector.add(f"{focus1_name} = ({cx}, {cy - focus_distance})")
            ctx.collector.add(f"{focus2_name} = ({cx}, {cy + focus_distance})")
    else:
        if a >= b:
            ctx.collector.add(
                f"{focus1_name} = (x({center_name}) - {focus_distance}, y({center_name}))"
            )
            ctx.collector.add(
                f"{focus2_name} = (x({center_name}) + {focus_distance}, y({center_name}))"
            )
        else:
            ctx.collector.add(
                f"{focus1_name} = (x({center_name}), y({center_name}) - {focus_distance})"
            )
            ctx.collector.add(
                f"{focus2_name} = (x({center_name}), y({center_name}) + {focus_distance})"
            )

    ctx.collector.add(
        f"{hyperbola_name} = Hyperbola[{focus1_name}, {focus2_name}, {semimajor}]"
    )

    execute_context(ctx)


def handle_arc(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制标准格式的圆弧。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    kind = params.get("kind", "minor")
    if kind not in {"minor", "major"}:
        raise Exception(f"arc 暂只支持 kind=minor/major，当前为 {kind}")

    center_name, center_coordinates = _resolve_named_point(params.get("center"), "arc.center")
    start_name, start_coordinates = _resolve_named_point(params.get("start"), "arc.start")
    end_name, end_coordinates = _resolve_named_point(params.get("end"), "arc.end")

    _add_point_if_coordinates(ctx, center_name, center_coordinates)
    _add_point_if_coordinates(ctx, start_name, start_coordinates)
    _add_point_if_coordinates(ctx, end_name, end_coordinates)

    arc_name = _require_step_id(params, "arc")

    # 主路径统一使用 GeoGebra 的 CircularArc 命令。
    # - kind=minor：按 start -> end 方向创建较短圆弧
    # - kind=major：交换端点顺序，创建对应的另一段圆弧
    if kind == "minor":
        ctx.collector.add(f"{arc_name} = CircularArc[{center_name}, {start_name}, {end_name}]")
    else:
        ctx.collector.add(f"{arc_name} = CircularArc[{center_name}, {end_name}, {start_name}]")

    execute_context(ctx)
