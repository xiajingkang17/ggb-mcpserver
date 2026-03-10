"""
GeoGebra 绘图工具注册表。
本模块职责：
1. 统一维护 draw_type -> category / handler / schema 的映射关系。
2. 对外提供工具枚举、3D 判断、统一绘图分发、MCP 输入 schema 构建能力。
3. 让主文件与 server 层不再依赖分散的工具列表和手写 if/elif 分发。

说明：
当前 registry 已经进入“精确注册”阶段：
- 每个 draw_type 都直接绑定到 shapes 层的精确 handler。
- 工具清单、类别信息、handler 映射都在本模块内统一编排。
- 构建默认注册表时，会校验工具目录、类别映射、handler 映射三者是否一致。
"""

from __future__ import annotations

from typing import Any, Iterable

from tool_catalog import ALL_TOOLS, FUNCTION_TOOLS, TOOLS_2D, TOOLS_3D

from .models import ToolCategory, ToolSpec


# ========== 核心注册表 ==========
class ToolRegistry:
    """绘图工具注册表。

    这个对象是 registry 层的统一入口。
    所有关于绘图工具的查询和分发，都应该通过这里完成。
    """

    def __init__(self, specs: Iterable[ToolSpec] | None = None):
        self._specs: dict[str, ToolSpec] = {}

        if specs is not None:
            self.register_many(specs)

    def register(self, spec: ToolSpec) -> None:
        """注册单个绘图工具。"""
        if spec.name in self._specs:
            raise ValueError(f"重复注册图形工具：{spec.name}")

        self._specs[spec.name] = spec

    def register_many(self, specs: Iterable[ToolSpec]) -> None:
        """批量注册多个绘图工具。"""
        for spec in specs:
            self.register(spec)

    def get(self, name: str) -> ToolSpec:
        """获取指定图形类型的注册信息。"""
        try:
            return self._specs[name]
        except KeyError as exc:
            raise KeyError(f"未注册的图形类型：{name}") from exc

    def list_tool_specs(self) -> list[ToolSpec]:
        """列出全部图形工具规格。"""
        return list(self._specs.values())

    def list_tool_names(self) -> list[str]:
        """列出全部图形工具名称。"""
        return [spec.name for spec in self.list_tool_specs()]

    def has_tool(self, name: str) -> bool:
        """判断指定图形类型是否已经注册。"""
        return name in self._specs

    def is_3d_tool(self, name: str) -> bool:
        """判断图形类型是否属于 3D 类别。"""
        return self.get(name).category == "3d"

    def dispatch_draw(
        self,
        draw_type: str,
        params: dict[str, Any],
        page,
        skip_coord_init: bool = False,
    ):
        """根据注册信息统一执行绘图分发。

        Args:
            draw_type: 图形类型
            params: 图形参数
            page: Playwright 页面对象
            skip_coord_init: 连续绘制时是否跳过坐标系初始化

        Returns:
            透传底层绘图函数返回值
        """
        spec = self.get(draw_type)

        # 目前只有 2D 绘图入口额外支持 skip_coord_init。
        if spec.category == "2d":
            return spec.handler(
                page,
                draw_type,
                params,
                skip_coord_init=skip_coord_init,
            )

        return spec.handler(page, draw_type, params)

    def build_export_input_schema(self) -> dict[str, Any]:
        """构建 export_interactive_html 的统一输入 schema。

        这里由 registry 统一提供工具枚举和步骤结构，
        避免 server 层继续手工维护 draw_type 的枚举列表。
        """
        tool_names = self.list_tool_names()

        return {
            "type": "object",
            "properties": {
                "draw_type": {
                    "type": "string",
                    "description": "单个图形类型（与 steps 二选一）",
                    "enum": tool_names,
                },
                "params": {
                    "type": "object",
                    "description": "单个图形参数（与 steps 二选一）",
                },
                "steps": {
                    "type": "array",
                    "description": (
                        "连续绘制步骤列表（与 draw_type/params 二选一），"
                        "格式：[{type:'point_3d', params:{...}}]"
                    ),
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "description": "图形类型",
                                "enum": tool_names,
                            },
                            "params": {
                                "type": "object",
                                "description": "图形参数",
                            },
                        },
                        "required": ["type", "params"],
                    },
                },
                "mode": {
                    "type": "string",
                    "enum": ["auto", "2d", "3d"],
                    "description": "模式：auto 自动判断、2d 二维、3d 三维",
                    "default": "auto",
                },
                "save_dir": {
                    "type": "string",
                    "description": "保存目录路径（强烈推荐提供）",
                },
            },
        }


# ========== 默认元数据构建 ==========
def _build_default_category_map() -> dict[str, ToolCategory]:
    """构建默认工具类别映射。

    说明：
    1. 工具归类本身属于 registry 的元数据职责。
    2. 这里基于 tool_catalog 统一生成，避免类别信息散落在注册代码中重复维护。
    """
    category_map: dict[str, ToolCategory] = {}

    for tool_name in FUNCTION_TOOLS:
        category_map[tool_name] = "function"
    for tool_name in TOOLS_2D:
        category_map[tool_name] = "2d"
    for tool_name in TOOLS_3D:
        category_map[tool_name] = "3d"

    return category_map


def _build_default_handler_map() -> dict[str, Any]:
    """构建默认工具 handler 映射。

    说明：
    1. 这里集中维护 draw_type -> handler 的绑定关系。
    2. 后续新增图形时，只需要补这一份映射，不需要再手写一长串 ToolSpec。
    """
    from shapes.functions import (
        handle_cubic_standard,
        handle_cubic_standard_slider,
        handle_cos_function,
        handle_cos_function_slider,
        handle_exponential_function,
        handle_exponential_function_slider,
        handle_linear_general,
        handle_linear_general_slider,
        handle_logarithmic_function,
        handle_logarithmic_function_slider,
        handle_polynomial_function,
        handle_quadratic_standard,
        handle_quadratic_standard_slider,
        handle_sin_function,
        handle_sin_function_slider,
        handle_tan_function,
        handle_tan_function_slider,
    )
    from shapes.geometry_2d import (
        handle_angle_bisector,
        handle_circle_center_radius,
        handle_ellipse_equation,
        handle_hyperbola_equation,
        handle_intersect_2d,
        handle_line,
        handle_parabola_equation,
        handle_perpendicular_line,
        handle_point_2d,
        handle_point_on_object,
        handle_polygon_points,
        handle_segment,
        handle_tangent,
        handle_triangle_points,
    )
    from shapes.geometry_3d import (
        handle_cone_radius_height,
        handle_cylinder_radius_height,
        handle_point_3d,
        handle_point_on_segment_3d,
        handle_polygon_3d,
        handle_prism_all_vertices,
        handle_pyramid_all_vertices,
        handle_segment_3d,
        handle_sphere_center_radius,
    )

    return {
        "linear_general": handle_linear_general,
        "linear_general_slider": handle_linear_general_slider,
        "quadratic_standard": handle_quadratic_standard,
        "quadratic_standard_slider": handle_quadratic_standard_slider,
        "cubic_standard": handle_cubic_standard,
        "cubic_standard_slider": handle_cubic_standard_slider,
        "polynomial_function": handle_polynomial_function,
        "sin_function": handle_sin_function,
        "sin_function_slider": handle_sin_function_slider,
        "cos_function": handle_cos_function,
        "cos_function_slider": handle_cos_function_slider,
        "tan_function": handle_tan_function,
        "tan_function_slider": handle_tan_function_slider,
        "exponential_function": handle_exponential_function,
        "exponential_function_slider": handle_exponential_function_slider,
        "logarithmic_function": handle_logarithmic_function,
        "logarithmic_function_slider": handle_logarithmic_function_slider,
        "point_2d": handle_point_2d,
        "point_on_object": handle_point_on_object,
        "segment": handle_segment,
        "line": handle_line,
        "circle_center_radius": handle_circle_center_radius,
        "triangle_points": handle_triangle_points,
        "polygon_points": handle_polygon_points,
        "ellipse_equation": handle_ellipse_equation,
        "parabola_equation": handle_parabola_equation,
        "hyperbola_equation": handle_hyperbola_equation,
        "intersect_2d": handle_intersect_2d,
        "tangent": handle_tangent,
        "angle_bisector": handle_angle_bisector,
        "perpendicular_line": handle_perpendicular_line,
        "point_3d": handle_point_3d,
        "segment_3d": handle_segment_3d,
        "point_on_segment_3d": handle_point_on_segment_3d,
        "polygon_3d": handle_polygon_3d,
        "sphere_center_radius": handle_sphere_center_radius,
        "cylinder_radius_height": handle_cylinder_radius_height,
        "cone_radius_height": handle_cone_radius_height,
        "pyramid_all_vertices": handle_pyramid_all_vertices,
        "prism_all_vertices": handle_prism_all_vertices,
    }


def _build_default_specs() -> list[ToolSpec]:
    """批量构建默认 ToolSpec 列表。

    说明：
    1. 这里用 `ALL_TOOLS` 保证注册顺序稳定。
    2. 这里同时校验目录清单、类别映射、handler 映射三者是否一致。
    """
    category_map = _build_default_category_map()
    handler_map = _build_default_handler_map()

    missing_categories = [name for name in ALL_TOOLS if name not in category_map]
    missing_handlers = [name for name in ALL_TOOLS if name not in handler_map]
    extra_handlers = [name for name in handler_map if name not in category_map]

    if missing_categories:
        raise ValueError(f"registry 缺少以下工具类别绑定：{missing_categories}")
    if missing_handlers:
        raise ValueError(f"registry 缺少以下工具 handler 绑定：{missing_handlers}")
    if extra_handlers:
        raise ValueError(f"registry 存在未收录到工具目录的 handler：{extra_handlers}")

    return [
        ToolSpec(
            name=tool_name,
            category=category_map[tool_name],
            handler=handler_map[tool_name],
        )
        for tool_name in ALL_TOOLS
    ]


# ========== 默认注册表构建 ==========
def create_default_registry() -> ToolRegistry:
    """基于当前仓库已有绘图实现构建默认注册表。

    当前阶段 registry 已经完成 shapes 层全量接管：
    1. 每个 draw_type 都绑定到精确的 shapes handler。
    2. 注册顺序、工具目录、类别信息统一由 registry 内部维护。
    3. 构建完成后，会校验工具目录与 handler 映射是否完整一致。
    """
    registry = ToolRegistry(_build_default_specs())

    expected_tools = list(ALL_TOOLS)
    actual_tools = registry.list_tool_names()

    # 这里继续保留最终一致性校验，避免后续修改时无意打乱注册顺序或遗漏工具。
    if actual_tools != expected_tools:
        raise ValueError(
            f"registry 工具顺序或清单不一致：expected={expected_tools}, actual={actual_tools}"
        )

    return registry
