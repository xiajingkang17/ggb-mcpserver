"""
Registry for GeoGebra drawing tools.
"""

from __future__ import annotations

from typing import Any, Iterable

from drawing_tools.tool_catalog import ALL_TOOLS, FUNCTION_TOOLS, TOOLS_2D, TOOLS_3D

from .models import ToolCategory, ToolSpec
from .schemas import build_standard_params_schema_map
from .schemas.common import id_schema, single_draw_conditional, step_schema


class ToolRegistry:
    """Central registry for tool metadata and draw dispatch."""

    def __init__(self, specs: Iterable[ToolSpec] | None = None):
        self._specs: dict[str, ToolSpec] = {}
        if specs is not None:
            self.register_many(specs)

    def register(self, spec: ToolSpec) -> None:
        if spec.name in self._specs:
            raise ValueError(f"Duplicate tool registration: {spec.name}")
        self._specs[spec.name] = spec

    def register_many(self, specs: Iterable[ToolSpec]) -> None:
        for spec in specs:
            self.register(spec)

    def get(self, name: str) -> ToolSpec:
        try:
            return self._specs[name]
        except KeyError as exc:
            raise KeyError(f"Unregistered tool: {name}") from exc

    def list_tool_specs(self) -> list[ToolSpec]:
        return list(self._specs.values())

    def list_tool_names(self) -> list[str]:
        return [spec.name for spec in self.list_tool_specs()]

    def has_tool(self, name: str) -> bool:
        return name in self._specs

    def is_3d_tool(self, name: str) -> bool:
        return self.get(name).category == "3d"

    def dispatch_draw(
        self,
        draw_type: str,
        params: dict[str, Any],
        page,
        skip_coord_init: bool = False,
    ):
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

        steps_schema = {
            "oneOf": [
                {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "oneOf": step_variants,
                    },
                },
                {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "string",
                        "description": "JSON-encoded step object",
                    },
                },
            ],
            "description": (
                "Step list for multi-draw mode. Accepts either native step objects "
                "or JSON-encoded step strings."
            ),
        }

        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "draw_type": {
                    "type": "string",
                    "description": "Single-draw type; mutually exclusive with steps",
                    "enum": tool_names,
                },
                "id": id_schema("Unique object id for single-draw mode"),
                "params": {
                    "type": "object",
                    "description": "Single-draw params; exact schema depends on draw_type",
                },
                "steps": steps_schema,
                "mode": {
                    "type": "string",
                    "enum": ["auto", "2d", "3d"],
                    "description": "Export mode",
                    "default": "auto",
                },
                "save_dir": {
                    "type": "string",
                    "description": "Output directory",
                },
            },
            "oneOf": [
                {"required": ["draw_type", "id", "params"]},
                {"required": ["steps"]},
            ],
            "allOf": draw_type_conditionals,
        }


def _build_default_category_map() -> dict[str, ToolCategory]:
    category_map: dict[str, ToolCategory] = {}

    for tool_name in FUNCTION_TOOLS:
        category_map[tool_name] = "function"
    for tool_name in TOOLS_2D:
        category_map[tool_name] = "2d"
    for tool_name in TOOLS_3D:
        category_map[tool_name] = "3d"

    return category_map


def _build_default_handler_map() -> dict[str, Any]:
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
    category_map = _build_default_category_map()
    handler_map = _build_default_handler_map()
    params_schema_map = build_standard_params_schema_map()

    missing_categories = [name for name in ALL_TOOLS if name not in category_map]
    missing_handlers = [name for name in ALL_TOOLS if name not in handler_map]
    extra_handlers = [name for name in handler_map if name not in category_map]

    if missing_categories:
        raise ValueError(f"Missing category bindings: {missing_categories}")
    if missing_handlers:
        raise ValueError(f"Missing handler bindings: {missing_handlers}")
    if extra_handlers:
        raise ValueError(f"Unexpected handlers outside catalog: {extra_handlers}")

    return [
        ToolSpec(
            name=tool_name,
            category=category_map[tool_name],
            handler=handler_map[tool_name],
            params_schema=params_schema_map.get(
                tool_name,
                {"type": "object", "description": "Shape params"},
            ),
        )
        for tool_name in ALL_TOOLS
    ]


def create_default_registry() -> ToolRegistry:
    registry = ToolRegistry(_build_default_specs())

    expected_tools = list(ALL_TOOLS)
    actual_tools = registry.list_tool_names()
    if actual_tools != expected_tools:
        raise ValueError(
            f"Registry tool order mismatch: expected={expected_tools}, actual={actual_tools}"
        )

    return registry
