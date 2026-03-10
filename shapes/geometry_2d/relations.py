"""
2D 关系型图形 handlers。

本模块职责：
1. 处理依赖已有对象关系的 2D 图形。
2. 主入口统一采用标准参数格式。
3. 延续原实现的 GeoGebra 命令逻辑，不改变作图结果。
"""

from __future__ import annotations

from .basic import _add_point_if_coordinates, _build_context, _resolve_point_ref
from shapes.common import execute_context, stderr_print


# ========== 2D 关系型辅助逻辑 ==========
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


def _require_step_id(params: dict, draw_type: str) -> str:
    """获取当前标准步骤对应的对象名。"""
    step_id = params.get("id")
    if not isinstance(step_id, str) or not step_id.strip():
        raise Exception(f"{draw_type} 需要提供明确的 id，不能依赖隐式命名")
    return step_id.strip()


def _resolve_object_ref(object_ref) -> str:
    """解析标准参数中的对象引用。"""
    if isinstance(object_ref, str) and object_ref.strip():
        return object_ref.strip()

    raise Exception("对象引用必须是已存在对象的 id 字符串")


def _default_slider_config_for_object(object_name: str) -> tuple[float, float, float, float]:
    """根据对象名称推断默认滑动条范围。"""
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
    if "arc_" in object_name or "Arc" in object_name:
        return 0, 1, 0.01, 0
    return 0, 1, 0.01, 0.5


def _resolve_line_name(line_param) -> str:
    """解析垂线依赖的目标直线。"""
    if isinstance(line_param, str) and line_param.strip():
        return line_param.strip()

    raise Exception("perpendicular_line.target 需要提供目标直线 id")


def _resolve_pick_index(params: dict, fallback: int = 1) -> int:
    """解析标准参数中的多解选取方式。"""
    pick = params.get("pick")
    if pick is None:
        return fallback

    if not isinstance(pick, dict):
        raise Exception("pick 必须是对象")

    mode = pick.get("mode", "index")
    if mode != "index":
        raise Exception(f"当前仅支持 pick.mode=index，当前为 {mode}")

    value = pick.get("value")
    if value is None:
        raise Exception("pick.mode=index 时必须提供 value")
    return value


# ========== 2D 关系型图形 ==========
def handle_point_on(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """在对象上创建标准格式的 2D 点。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    point_name = _require_step_id(params, "point_on")
    object_name = _resolve_object_ref(params.get("object"))
    placement = params.get("placement")

    if placement is None:
        # 默认通过滑动条控制点在对象上的位置，保留交互性。
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
    else:
        if not isinstance(placement, dict):
            raise Exception("placement 必须是对象")

        placement_mode = placement.get("mode", "slider")
        if placement_mode == "fixed":
            value = placement.get("value")
            if value is None:
                raise Exception("placement.mode=fixed 时必须提供 value")
            ctx.collector.add(f"{point_name} = Point[{object_name}, {value}]")
        elif placement_mode == "slider":
            slider_name = placement.get("name", f"t_{point_name}")
            slider_min = placement.get("min", 0)
            slider_max = placement.get("max", 1)
            slider_step = placement.get("step", 0.01)
            slider_init = placement.get("init", slider_min)
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
            raise Exception(f"当前仅支持 placement.mode=fixed/slider，当前为 {placement_mode}")

    ctx.collector.add(f"SetLabelStyle[{point_name}, 0]")
    ctx.collector.add(f"SetLabelVisible[{point_name}, true]")

    execute_context(ctx)


def handle_intersection(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """创建两个对象的标准交点。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    point_name = _require_step_id(params, "intersection")
    objects = params.get("objects")
    if not isinstance(objects, (list, tuple)) or len(objects) != 2:
        raise Exception("intersection 需要提供 objects，且长度为 2")

    object1 = _resolve_object_ref(objects[0])
    object2 = _resolve_object_ref(objects[1])
    index = _resolve_pick_index(params, fallback=1)

    # 沿用原实现：交点始终交给 GeoGebra 精确计算，不手动推坐标。
    ctx.collector.add(f"{point_name} = Intersect[{object1}, {object2}, {index}]")

    execute_context(ctx)


def handle_tangent(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制标准格式的切线。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    point_name, point_coordinates = _resolve_point_ref(params.get("through"))
    target_name = _resolve_object_ref(params.get("target"))
    tangent_name = _require_step_id(params, "tangent")
    pick = params.get("pick")

    _add_point_if_coordinates(ctx, point_name, point_coordinates)

    # GeoGebra 原生命令负责切线求解，这里只统一参数和命名。
    if pick is None:
        ctx.collector.add(f"{tangent_name} = Tangent[{point_name}, {target_name}]")
    else:
        index = _resolve_pick_index(params, fallback=1)
        ctx.collector.add(f"{tangent_name} = Tangent[{point_name}, {target_name}, {index}]")

    execute_context(ctx)
    stderr_print(f"[Tangent] 过点 {point_name} 作曲线 {target_name} 的切线 {tangent_name}")


def handle_angle_bisector(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制标准格式的角平分线。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    points = params.get("points")
    if not isinstance(points, (list, tuple)) or len(points) != 3:
        raise Exception("angle_bisector 需要提供 points，且长度为 3")

    p1_name, p1_coordinates = _resolve_point_ref(points[0])
    vertex_name, vertex_coordinates = _resolve_point_ref(points[1])
    p2_name, p2_coordinates = _resolve_point_ref(points[2])

    _add_point_if_coordinates(ctx, p1_name, p1_coordinates)
    _add_point_if_coordinates(ctx, vertex_name, vertex_coordinates)
    _add_point_if_coordinates(ctx, p2_name, p2_coordinates)

    # 角平分线直接由 GeoGebra 的三点角平分命令生成。
    bisector_name = _require_step_id(params, "angle_bisector")
    ctx.collector.add(
        f"{bisector_name} = AngleBisector[{p1_name}, {vertex_name}, {p2_name}]"
    )

    execute_context(ctx)


def handle_perpendicular_line(
    page,
    draw_type: str,
    params: dict,
    skip_coord_init: bool = False,
) -> None:
    """绘制标准格式的垂线。"""
    ctx = _build_context(page, skip_coord_init=skip_coord_init)

    point_name, point_coordinates = _resolve_point_ref(params.get("through"))
    target_name = _resolve_line_name(params.get("target"))

    _add_point_if_coordinates(ctx, point_name, point_coordinates)

    # 保持旧实现：垂线直接由 GeoGebra 根据点与目标直线生成。
    perpendicular_name = _require_step_id(params, "perpendicular_line")
    ctx.collector.add(f"{perpendicular_name} = PerpendicularLine[{point_name}, {target_name}]")

    execute_context(ctx)
