"""
GeoGebra 绘图工具注册表。

本模块职责：
1. 统一维护标准 type -> category / handler 的映射关系。
2. 对外提供工具枚举、3D 判断和统一绘图分发能力。
3. 为 MCP 输入 schema 提供标准工具清单。
"""

from __future__ import annotations

from typing import Any, Iterable

from drawing_tools.tool_catalog import ALL_TOOLS, FUNCTION_TOOLS, TOOLS_2D, TOOLS_3D

from .models import ToolCategory, ToolSpec
from .schemas.common import id_schema, single_draw_conditional, step_schema
from .schemas import build_standard_params_schema_map


# ========== 核心注册表 ==========
class ToolRegistry:
    """统一管理绘图工具元数据与运行时分发。"""

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
        """根据注册信息统一执行绘图分发。"""
        spec = self.get(draw_type)

        if spec.category == "2d":
            return spec.handler(
                page,
                draw_type,
                params,
                skip_coord_init=skip_coord_init,
            )

        return spec.handler(page, draw_type, params)

    def build_export_input_schema(self) -> dict[str, Any]:
        """构建 export_interactive_html 的统一输入 schema。"""
        tool_specs = self.list_tool_specs()
        tool_names = [spec.name for spec in tool_specs]

        step_variants = [
            step_schema(spec.name, spec.params_schema)
            for spec in tool_specs
        ]

        draw_type_conditionals = [
            single_draw_conditional(spec.name, spec.params_schema)
            for spec in tool_specs
        ]

        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "draw_type": {
                    "type": "string",
                    "description": "单个图形类型（与 steps 二选一）",
                    "enum": tool_names,
                },
                "id": id_schema("单个图形模式下创建对象的唯一标识"),
                "params": {
                    "type": "object",
                    "description": "单个图形参数；其精确结构由 draw_type 决定",
                },
                "steps": {
                    "type": "array",
                    "minItems": 1,
                    "description": (
                        "连续绘制步骤列表（与 draw_type/params 二选一），"
                        "格式：[{type:'point', id:'A', params:{...}}]"
                    ),
                    "items": {
                        "oneOf": step_variants,
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
            "oneOf": [
                {"required": ["draw_type", "id", "params"]},
                {"required": ["steps"]},
            ],
            "allOf": draw_type_conditionals,
        }


# ========== 默认元数据构建 ==========
def _build_default_category_map() -> dict[str, ToolCategory]:
    """构建默认工具类别映射。"""
    category_map: dict[str, ToolCategory] = {}

    for tool_name in FUNCTION_TOOLS:
        category_map[tool_name] = "function"
    for tool_name in TOOLS_2D:
        category_map[tool_name] = "2d"
    for tool_name in TOOLS_3D:
        category_map[tool_name] = "3d"

    return category_map


def _build_default_handler_map() -> dict[str, Any]:
    """构建默认工具 handler 映射。"""
    from shapes.functions import handle_function
    from shapes.geometry_2d import (
        handle_angle_bisector,
        handle_arc,
        handle_circle,
        handle_ellipse,
        handle_hyperbola,
        handle_intersection,
        handle_line,
        handle_parabola,
        handle_perpendicular_line,
        handle_point,
        handle_point_on,
        handle_segment,
        handle_tangent,
    )
    from shapes.geometry_3d import (
        handle_cone,
        handle_cylinder,
        handle_point_3d,
        handle_point_on_3d,
        handle_segment_3d,
        handle_sphere,
    )

    return {
        "function": handle_function,
        "point": handle_point,
        "segment": handle_segment,
        "line": handle_line,
        "circle": handle_circle,
        "ellipse": handle_ellipse,
        "parabola": handle_parabola,
        "hyperbola": handle_hyperbola,
        "arc": handle_arc,
        "point_on": handle_point_on,
        "intersection": handle_intersection,
        "perpendicular_line": handle_perpendicular_line,
        "angle_bisector": handle_angle_bisector,
        "tangent": handle_tangent,
        "point_3d": handle_point_3d,
        "segment_3d": handle_segment_3d,
        "point_on_3d": handle_point_on_3d,
        "sphere": handle_sphere,
        "cylinder": handle_cylinder,
        "cone": handle_cone,
    }


def _build_default_specs() -> list[ToolSpec]:
    """批量构建默认 ToolSpec 列表。"""
    category_map = _build_default_category_map()
    handler_map = _build_default_handler_map()
    params_schema_map = build_standard_params_schema_map()

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
            params_schema=params_schema_map.get(tool_name, {"type": "object", "description": "图形参数"}),
        )
        for tool_name in ALL_TOOLS
    ]


# ========== 默认注册表构建 ==========
def create_default_registry() -> ToolRegistry:
    """基于当前仓库已有绘图实现构建默认注册表。"""
    registry = ToolRegistry(_build_default_specs())

    expected_tools = list(ALL_TOOLS)
    actual_tools = registry.list_tool_names()
    if actual_tools != expected_tools:
        raise ValueError(
            f"registry 工具顺序或清单不一致：expected={expected_tools}, actual={actual_tools}"
        )

    return registry
