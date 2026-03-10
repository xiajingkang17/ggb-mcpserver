"""
2D 关系类图形 handler。

本模块职责：
1. 处理依赖已有对象关系的 2D 图形。
2. 保持旧实现中的命令顺序与默认参数策略不变。

当前包含：
- point_on_object
- intersect_2d
- tangent
- angle_bisector
- perpendicular_line
"""

from __future__ import annotations

from .basic import _add_point_if_coordinates, _build_context
from shapes.common import execute_context, stderr_print


# ========== 2D 关系类辅助逻辑 ==========
def _add_slider(
    collector,
    slider_name: str,
    slider_min,
    slider_max,
    slider_step,
    slider_init,
) -> None:
    """统一创建 2D 滑动条命令。"""
    collector.add(f"{slider_name} = Slider[{slider_min}, {slider_max}, {slider_step}]")
    collector.add(f"SetValue[{slider_name}, {slider_init}]")
    collector.add(f"SetLabelStyle[{slider_name}, 0]")
    collector.add(f"SetLabelVisible[{slider_name}, true]")


def _default_slider_config_for_object(object_name: str) -> tuple[float, float, float, float]:
    """根据对象名称推断默认滑动条范围。

    这里保留旧实现中的启发式规则，不额外引入新的对象类型判断。
    """
    if "seg_" in object_name or "Segment" in object_name:
        return 0, 1, 0.01, 0.5
    if "circ_" in object_name or "Circle" in object_name:
        return 0, 1, 0.01, 0
    if "ellipse_" in object_name or "Ellipse" in object_name:
        return 0, 1, 0.01, 0
    if "parabola_" in object_name or "Parabola" in object_name:
        return 0, 1, 0.01, 0
    if "hyperbola_" in object_name or "Hyperbola" in object_name:
        return 0, 1, 0.01, 0
    return 0, 1, 0.01, 0.5


def _resolve_line_name(ctx, line_param) -> str:
    """解析 perpendicular_line 所依赖的直线参数。"""
    if isinstance(line_param, dict):
        if "point1" in line_param and "point2" in line_param:
            line_p1 = line_param["point1"]
            line_p2 = line_param["point2"]
            line_p1_name = line_p1.get("name", "A")
            line_p2_name = line_p2.get("name", "B")

            _add_point_if_coordinates(
                ctx,
                line_p1_name,
                line_p1.get("coordinates", None),
            )
            _add_point_if_coordinates(
                ctx,
                line_p2_name,
                line_p2.get("coordinates", None),
            )

            line_name = line_param.get("name", f"line_{line_p1_name}{line_p2_name}")
            if "name" not in line_param:
                ctx.collector.add(f"{line_name} = Line[{line_p1_name}, {line_p2_name}]")
                ctx.collector.add(f"ShowLabel[{line_name}, false]")
            return line_name

        if "name" in line_param:
            return line_param.get("name")

        raise Exception("perpendicular_line需要提供line参数（包含point1和point2，或name）")

    if isinstance(line_param, str):
        return line_param

    raise Exception("perpendicular_line需要提供line参数")


# ========== 2D 关系类图形 ==========
def handle_point_on_object(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """在已有对象上创建 2D 点。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    point_name = params.get("point_name", "P")
    object_name = params.get("object", "circ_O")
    parameter = params.get("parameter", None)
    slider = params.get("slider", None)

    if parameter is not None:
        ctx.collector.add(f"{point_name} = Point[{object_name}, {parameter}]")
    elif slider is not None:
        slider_name = slider.get("name", f"t_{point_name}")
        slider_min = slider.get("min", 0)
        slider_max = slider.get("max", 1)
        slider_step = slider.get("step", 0.01)
        slider_init = slider.get("init", slider_min)

        _add_slider(
            ctx.collector,
            slider_name,
            slider_min,
            slider_max,
            slider_step,
            slider_init,
        )
        ctx.collector.add(f"{point_name} = Point[{object_name}, {slider_name}]")
    else:
        slider_name = f"t_{point_name}"
        slider_min, slider_max, slider_step, slider_init = _default_slider_config_for_object(
            object_name
        )

        _add_slider(
            ctx.collector,
            slider_name,
            slider_min,
            slider_max,
            slider_step,
            slider_init,
        )
        ctx.collector.add(f"{point_name} = Point[{object_name}, {slider_name}]")

    ctx.collector.add(f"SetLabelStyle[{point_name}, 0]")
    ctx.collector.add(f"SetLabelVisible[{point_name}, true]")

    execute_context(ctx)
    return None


def handle_intersect_2d(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """创建两个 2D 几何对象的交点。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    point_name = params.get("point_name", "P")
    object1 = params.get("object1")
    object2 = params.get("object2")
    index = params.get("index", 1)

    if not object1 or not object2:
        raise Exception("intersect_2d需要提供object1和object2参数")

    ctx.collector.add(f"{point_name} = Intersect[{object1}, {object2}, {index}]")
    ctx.collector.add(f"ShowLabel[{point_name}, true]")

    execute_context(ctx)
    return None


def handle_tangent(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制点到曲线的切线。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    point = params.get("point", {})
    conic = params.get("conic", {})
    index = params.get("index", None)

    point_name = point.get("name", "P")
    conic_name = conic.get("name", "circ_O")

    if index is not None:
        tangent_name = f"tan_{point_name}_{index}"
        ctx.collector.add(f"{tangent_name} = Tangent[{point_name}, {conic_name}, {index}]")
    else:
        tangent_name = f"tan_{point_name}"
        ctx.collector.add(f"{tangent_name} = Tangent[{point_name}, {conic_name}]")

    ctx.collector.add(f"ShowLabel[{tangent_name}, false]")

    execute_context(ctx)
    stderr_print(f"[Tangent] 过点 {point_name} 作曲线 {conic_name} 的切线 {tangent_name}")
    return None


def handle_angle_bisector(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制角平分线。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    point1 = params.get("point1", {})
    vertex = params.get("vertex", {})
    point2 = params.get("point2", {})

    p1_name = point1.get("name", "A")
    vertex_name = vertex.get("name", "B")
    p2_name = point2.get("name", "C")

    _add_point_if_coordinates(ctx, p1_name, point1.get("coordinates", None))
    _add_point_if_coordinates(ctx, vertex_name, vertex.get("coordinates", None))
    _add_point_if_coordinates(ctx, p2_name, point2.get("coordinates", None))

    bisector_name = f"bisector_{p1_name}{vertex_name}{p2_name}"
    ctx.collector.add(
        f"{bisector_name} = AngleBisector[{p1_name}, {vertex_name}, {p2_name}]"
    )
    ctx.collector.add(f"ShowLabel[{bisector_name}, false]")

    execute_context(ctx)
    return None


def handle_perpendicular_line(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制过点垂线。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    point = params.get("point", {})
    line_param = params.get("line", {})

    point_name = point.get("name", "P")
    _add_point_if_coordinates(ctx, point_name, point.get("coordinates", None))

    line_name = _resolve_line_name(ctx, line_param)

    perpendicular_name = f"perp_{point_name}_{line_name}"
    ctx.collector.add(
        f"{perpendicular_name} = PerpendicularLine[{point_name}, {line_name}]"
    )
    ctx.collector.add(f"ShowLabel[{perpendicular_name}, false]")

    execute_context(ctx)
    return None
