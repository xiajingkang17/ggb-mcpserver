"""
2D 圆锥曲线基础 handler。

本模块职责：
1. 先迁移最简单的 2D 圆锥曲线图形。
2. 保持现有命令生成方式不变，只把实现位置从旧大分支挪到 shapes 层。

当前包含：
- circle_center_radius
- ellipse_equation
- parabola_equation
- hyperbola_equation
"""

from __future__ import annotations

import math

from .basic import _add_point_if_coordinates, _build_context
from shapes.common import execute_context


# ========== 2D 圆锥曲线辅助逻辑 ==========
def _resolve_2d_point_name(ctx, point_param, default_name: str) -> str:
    """解析 2D 点参数，并在需要时创建点。"""
    if isinstance(point_param, dict):
        point_name = point_param.get("name", default_name)
        _add_point_if_coordinates(
            ctx,
            point_name,
            point_param.get("coordinates", None),
        )
        return point_name

    point_name = default_name
    _add_point_if_coordinates(ctx, point_name, point_param)
    return point_name


# ========== 2D 圆锥曲线 ==========
def handle_circle_center_radius(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制圆心半径形式的 2D 圆。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    center = params.get("center", {})
    center_name = center.get("name", "O")
    center_coordinates = center.get("coordinates", None)
    radius = params.get("radius", 1)

    _add_point_if_coordinates(ctx, center_name, center_coordinates)

    circle_name = f"circ_{center_name}"
    ctx.collector.add(f"{circle_name} = Circle[{center_name}, {radius}]")
    ctx.collector.add(f"ShowLabel[{circle_name}, false]")

    execute_context(ctx)
    return None


def handle_ellipse_equation(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制椭圆。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    center_param = params.get("center", [0, 0])
    a = params.get("a", 2)
    b = params.get("b", 1)

    semimajor = max(a, b)
    focus_distance = math.sqrt(abs(a * a - b * b))

    if isinstance(center_param, dict):
        center_name = center_param.get("name", "O_ellipse")
        center_coordinates = center_param.get("coordinates", None)

        if center_coordinates is not None:
            cx, cy = center_coordinates[0], center_coordinates[1]
            _add_point_if_coordinates(ctx, center_name, center_coordinates)
            focus1_name = f"F1_{center_name}"
            focus2_name = f"F2_{center_name}"
            if a >= b:
                ctx.collector.add(f"{focus1_name} = ({cx - focus_distance}, {cy})")
                ctx.collector.add(f"{focus2_name} = ({cx + focus_distance}, {cy})")
            else:
                ctx.collector.add(f"{focus1_name} = ({cx}, {cy - focus_distance})")
                ctx.collector.add(f"{focus2_name} = ({cx}, {cy + focus_distance})")
        else:
            focus1_name = f"F1_{center_name}"
            focus2_name = f"F2_{center_name}"
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

        ellipse_name = f"ellipse_{center_name}"
        ctx.collector.add(
            f"{ellipse_name} = Ellipse[{focus1_name}, {focus2_name}, {semimajor}]"
        )
        ctx.collector.add(f"ShowLabel[{ellipse_name}, false]")
    else:
        cx, cy = center_param[0], center_param[1]
        if a >= b:
            ctx.collector.add(
                f"Ellipse[({cx - focus_distance}, {cy}), ({cx + focus_distance}, {cy}), {semimajor}]"
            )
        else:
            ctx.collector.add(
                f"Ellipse[({cx}, {cy - focus_distance}), ({cx}, {cy + focus_distance}), {semimajor}]"
            )

    execute_context(ctx)
    return None


def handle_parabola_equation(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制抛物线。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    vertex_param = params.get("vertex", [0, 0])
    focus_param = params.get("focus", [0, 1])

    vertex_name = _resolve_2d_point_name(ctx, vertex_param, "V")
    focus_name = _resolve_2d_point_name(ctx, focus_param, "F")

    ctx.collector.add(
        f"directrix_{focus_name} = PerpendicularLine[{vertex_name}, Line[{focus_name}, {vertex_name}]]"
    )
    parabola_name = f"parabola_{focus_name}"
    ctx.collector.add(f"{parabola_name} = Parabola[{focus_name}, directrix_{focus_name}]")
    ctx.collector.add(f"ShowLabel[{parabola_name}, false]")

    execute_context(ctx)
    return None


def handle_hyperbola_equation(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制双曲线。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    center_param = params.get("center", [0, 0])
    a = params.get("a", 2)
    b = params.get("b", 1)

    semimajor = max(a, b)
    focus_distance = math.sqrt(a * a + b * b)

    if isinstance(center_param, dict):
        center_name = center_param.get("name", "O_hyperbola")
        center_coordinates = center_param.get("coordinates", None)

        if center_coordinates is not None:
            cx, cy = center_coordinates[0], center_coordinates[1]
            _add_point_if_coordinates(ctx, center_name, center_coordinates)
            focus1_name = f"F1_{center_name}"
            focus2_name = f"F2_{center_name}"
            if a >= b:
                ctx.collector.add(f"{focus1_name} = ({cx - focus_distance}, {cy})")
                ctx.collector.add(f"{focus2_name} = ({cx + focus_distance}, {cy})")
            else:
                ctx.collector.add(f"{focus1_name} = ({cx}, {cy - focus_distance})")
                ctx.collector.add(f"{focus2_name} = ({cx}, {cy + focus_distance})")
        else:
            focus1_name = f"F1_{center_name}"
            focus2_name = f"F2_{center_name}"
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

        hyperbola_name = f"hyperbola_{center_name}"
        ctx.collector.add(
            f"{hyperbola_name} = Hyperbola[{focus1_name}, {focus2_name}, {semimajor}]"
        )
        ctx.collector.add(f"ShowLabel[{hyperbola_name}, false]")
    else:
        cx, cy = center_param[0], center_param[1]
        if a >= b:
            ctx.collector.add(
                f"Hyperbola[({cx - focus_distance}, {cy}), ({cx + focus_distance}, {cy}), {semimajor}]"
            )
        else:
            ctx.collector.add(
                f"Hyperbola[({cx}, {cy - focus_distance}), ({cx}, {cy + focus_distance}), {semimajor}]"
            )

    execute_context(ctx)
    return None
