"""
3D 立体图形 handlers。

本模块职责：
1. 处理 sphere / cylinder / cone 三类标准 3D 立体对象。
2. 延续原实现的几何构造逻辑，不改变作图结果。
3. 统一对象命名方式，避免辅助对象命名冲突。
"""

from __future__ import annotations

from .basic import _add_point_if_coordinates, _build_context
from shapes.common import execute_context


# ========== 3D 立体图形辅助逻辑 ==========
def _require_step_id(params: dict, draw_type: str) -> str:
    """获取当前标准步骤对应的对象名。"""
    step_id = params.get("id")
    if not isinstance(step_id, str) or not step_id.strip():
        raise Exception(f"{draw_type} 需要提供明确的 id，不能依赖隐式命名")
    return step_id.strip()


def _resolve_named_point(point_param, param_name: str) -> tuple[str, object]:
    """解析标准参数中的 3D 点引用。"""
    if point_param is None:
        raise Exception(f"{param_name} 需要提供点引用")

    if isinstance(point_param, str):
        return point_param, None

    if isinstance(point_param, dict):
        point_name = point_param.get("id")
        if not point_name:
            raise Exception(f"{param_name} 点对象必须提供 id")
        return point_name, point_param.get("coords")

    raise Exception(f"{param_name} 必须是字符串或包含 id 的对象")


def _build_offset_point_expression(center_name: str, center_coordinates, radius) -> str:
    """根据圆心与半径生成辅助点表达式。"""
    if center_coordinates is not None:
        x, y, z = center_coordinates
        return f"({x + radius}, {y}, {z})"

    return f"(x({center_name}) + {radius}, y({center_name}), z({center_name}))"


# ========== 3D 立体图形 ==========
def handle_sphere(page, draw_type: str, params: dict) -> None:
    """绘制标准格式的球体。"""
    ctx = _build_context(page)

    center_name, center_coordinates = _resolve_named_point(params.get("center"), "sphere.center")
    radius = params.get("radius")
    if radius is None:
        raise Exception("sphere 需要提供 radius")

    _add_point_if_coordinates(ctx, center_name, center_coordinates)
    sphere_name = _require_step_id(params, "sphere")
    ctx.collector.add(f"{sphere_name} = Sphere[{center_name}, {radius}]")
    ctx.collector.add(f"SetLabelStyle[{sphere_name}, 0]")
    ctx.collector.add(f"SetLabelVisible[{sphere_name}, false]")

    execute_context(ctx)


def handle_cylinder(page, draw_type: str, params: dict) -> None:
    """绘制标准格式的圆柱。"""
    ctx = _build_context(page)

    center_name, center_coordinates = _resolve_named_point(
        params.get("center"),
        "cylinder.center",
    )
    radius = params.get("radius")
    height = params.get("height")
    if radius is None or height is None:
        raise Exception("cylinder 需要提供 radius 和 height")

    _add_point_if_coordinates(ctx, center_name, center_coordinates)

    cylinder_name = _require_step_id(params, "cylinder")
    point_name = f"P_{cylinder_name}_radius"
    circle_name = f"circ_{cylinder_name}_base"
    point_expr = _build_offset_point_expression(center_name, center_coordinates, radius)

    # 保持旧实现：先构造底面圆，再通过 Circle + height 生成圆柱。
    ctx.collector.add(f"{point_name} = {point_expr}")
    ctx.collector.add(f"{circle_name} = Circle[{center_name}, {point_name}]")
    ctx.collector.add(f"{cylinder_name} = Cylinder[{circle_name}, {height}]")
    ctx.collector.add(f"SetLabelStyle[{cylinder_name}, 0]")
    ctx.collector.add(f"SetLabelVisible[{cylinder_name}, false]")

    execute_context(ctx)


def handle_cone(page, draw_type: str, params: dict) -> None:
    """绘制标准格式的圆锥。"""
    ctx = _build_context(page)

    center_name, center_coordinates = _resolve_named_point(params.get("center"), "cone.center")
    radius = params.get("radius")
    height = params.get("height")
    if radius is None or height is None:
        raise Exception("cone 需要提供 radius 和 height")

    _add_point_if_coordinates(ctx, center_name, center_coordinates)

    cone_name = _require_step_id(params, "cone")
    point_name = f"P_{cone_name}_radius"
    circle_name = f"circ_{cone_name}_base"
    point_expr = _build_offset_point_expression(center_name, center_coordinates, radius)

    # 保持旧实现：先构造底面圆，再通过 Circle + height 生成圆锥。
    ctx.collector.add(f"{point_name} = {point_expr}")
    ctx.collector.add(f"{circle_name} = Circle[{center_name}, {point_name}]")
    ctx.collector.add(f"{cone_name} = Cone[{circle_name}, {height}]")
    ctx.collector.add(f"SetLabelStyle[{cone_name}, 0]")
    ctx.collector.add(f"SetLabelVisible[{cone_name}, false]")

    execute_context(ctx)
