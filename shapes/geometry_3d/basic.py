"""
3D 基础图形 handlers。

本模块职责：
1. 处理 point_3d / segment_3d / point_on_3d 三类标准 3D 对象。
2. 保持原有 GeoGebra 构造逻辑不变，只统一参数格式。
3. 统一由步骤 id 作为对象名，便于后续步骤直接引用。
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

    if not isinstance(point_coordinates, (list, tuple)) or len(point_coordinates) != 3:
        raise Exception("3D 点坐标必须是长度为 3 的数组或元组")

    x, y, z = point_coordinates
    ctx.collector.add(f"{point_name} = ({x}, {y}, {z})")
    ctx.collector.add(f"SetLabelStyle[{point_name}, 0]")
    ctx.collector.add(f"SetLabelVisible[{point_name}, true]")


def _require_step_id(params: dict, draw_type: str) -> str:
    """获取当前标准步骤对应的对象名。"""
    step_id = params.get("id")
    if not isinstance(step_id, str) or not step_id.strip():
        raise Exception(f"{draw_type} 需要提供明确的 id，不能依赖隐式命名")
    return step_id.strip()


def _resolve_point_ref(point_ref) -> tuple[str, object]:
    """解析标准参数中的 3D 点引用。"""
    if isinstance(point_ref, str):
        return point_ref, None

    if isinstance(point_ref, dict):
        point_name = point_ref.get("id")
        if not point_name:
            raise Exception("3D 点引用对象必须提供 id")
        return point_name, point_ref.get("coords")

    raise Exception("3D 点引用必须是字符串或包含 id 的对象")


def _resolve_object_ref(object_ref) -> str:
    """解析标准参数中的 3D 对象引用。"""
    if isinstance(object_ref, str) and object_ref.strip():
        return object_ref.strip()

    raise Exception("3D 对象引用必须是已存在对象的 id 字符串")


def _add_slider(
    collector,
    slider_name: str,
    slider_min,
    slider_max,
    slider_step,
    slider_init,
) -> None:
    """统一创建 3D 滑动条命令。"""
    collector.add(f"{slider_name} = Slider[{slider_min}, {slider_max}, {slider_step}]")
    collector.add(f"SetValue[{slider_name}, {slider_init}]")
    collector.add(f"SetLabelStyle[{slider_name}, 0]")
    collector.add(f"SetLabelVisible[{slider_name}, true]")
    collector.add(f"SetVisibleInView[{slider_name}, 1, true]")


# ========== 3D 基础图形 ==========
def handle_point_3d(page, draw_type: str, params: dict) -> None:
    """绘制标准格式的 3D 点。"""
    ctx = _build_context(page)

    point_name = _require_step_id(params, "point_3d")
    coordinates = params.get("coords")
    if coordinates is None:
        raise Exception("point_3d 需要提供 coords")
    if not isinstance(coordinates, (list, tuple)) or len(coordinates) != 3:
        raise Exception("point_3d.coords 必须是长度为 3 的数组或元组")

    x, y, z = coordinates
    ctx.collector.add(f"{point_name} = ({x}, {y}, {z})")
    ctx.collector.add(f"SetLabelStyle[{point_name}, 0]")
    ctx.collector.add(f"SetLabelVisible[{point_name}, true]")

    execute_context(ctx)


def handle_segment_3d(page, draw_type: str, params: dict) -> None:
    """绘制标准格式的 3D 线段。"""
    ctx = _build_context(page)

    endpoints = params.get("endpoints")
    if not isinstance(endpoints, (list, tuple)) or len(endpoints) != 2:
        raise Exception("segment_3d 需要提供 endpoints，且长度为 2")

    p1_name, p1_coordinates = _resolve_point_ref(endpoints[0])
    p2_name, p2_coordinates = _resolve_point_ref(endpoints[1])

    # 沿用原实现：只有在提供坐标时才补建端点。
    _add_point_if_coordinates(ctx, p1_name, p1_coordinates)
    _add_point_if_coordinates(ctx, p2_name, p2_coordinates)

    segment_name = _require_step_id(params, "segment_3d")
    ctx.collector.add(f"{segment_name} = Segment[{p1_name}, {p2_name}]")
    ctx.collector.add(f"SetLabelStyle[{segment_name}, 0]")
    ctx.collector.add(f"SetLabelVisible[{segment_name}, false]")

    execute_context(ctx)


def handle_point_on_3d(page, draw_type: str, params: dict) -> None:
    """在对象上创建标准格式的 3D 点。"""
    ctx = _build_context(page)

    point_name = _require_step_id(params, "point_on_3d")
    object_name = _resolve_object_ref(params.get("object"))
    placement = params.get("placement")

    if placement is None:
        slider_name = f"t_{point_name}"
        _add_slider(ctx.collector, slider_name, 0, 1, 0.01, 0.5)
        ctx.collector.add(f"{point_name} = Point[{object_name}, {slider_name}]")
    else:
        if not isinstance(placement, dict):
            raise Exception("point_on_3d.placement 必须是对象")

        placement_mode = placement.get("mode", "slider")
        if placement_mode == "fixed":
            value = placement.get("value")
            if value is None:
                raise Exception("point_on_3d 在 fixed 模式下必须提供 value")
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
            raise Exception(
                f"point_on_3d 当前仅支持 placement.mode=fixed/slider，当前为 {placement_mode}"
            )

    ctx.collector.add(f"SetLabelStyle[{point_name}, 0]")
    ctx.collector.add(f"SetLabelVisible[{point_name}, true]")

    execute_context(ctx)
