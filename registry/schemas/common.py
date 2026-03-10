"""
GeoGebra schema 公共结构。

本模块职责：
1. 提供 2D / 3D 共享的基础 schema 构造辅助。
2. 统一维护点引用、对象引用、placement、pick 等复用子结构。
3. 避免 2D / 3D schema 文件之间重复定义同一套公共规则。
"""

from __future__ import annotations

from typing import Any


# ========== schema 基础辅助 ==========
def strict_object(
    properties: dict[str, Any],
    required: list[str],
    description: str,
) -> dict[str, Any]:
    """构建严格对象 schema。"""
    return {
        "type": "object",
        "description": description,
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


def string_schema(description: str) -> dict[str, Any]:
    """构建字符串 schema。"""
    return {
        "type": "string",
        "description": description,
    }


def id_schema(description: str = "对象唯一标识") -> dict[str, Any]:
    """构建公共对象 id schema。"""
    return string_schema(description)


def number_schema(description: str, *, positive_only: bool = False) -> dict[str, Any]:
    """构建数值 schema。"""
    schema: dict[str, Any] = {
        "type": "number",
        "description": description,
    }
    if positive_only:
        schema["exclusiveMinimum"] = 0
    return schema


def integer_schema(description: str, *, minimum: int | None = None) -> dict[str, Any]:
    """构建整数 schema。"""
    schema: dict[str, Any] = {
        "type": "integer",
        "description": description,
    }
    if minimum is not None:
        schema["minimum"] = minimum
    return schema


def coords_2d_schema(description: str) -> dict[str, Any]:
    """构建二维坐标 schema。"""
    return {
        "type": "array",
        "description": description,
        "items": {"type": "number"},
        "minItems": 2,
        "maxItems": 2,
    }


def coords_3d_schema(description: str) -> dict[str, Any]:
    """构建三维坐标 schema。"""
    return {
        "type": "array",
        "description": description,
        "items": {"type": "number"},
        "minItems": 3,
        "maxItems": 3,
    }


# ========== 复用子结构 ==========
def point_ref_2d_schema(description: str) -> dict[str, Any]:
    """构建标准 2D 点引用 schema。"""
    return {
        "description": description,
        "oneOf": [
            string_schema("已存在点对象的 id"),
            strict_object(
                properties={
                    "id": string_schema("点对象 id"),
                    "coords": coords_2d_schema("可选；若该点尚未创建，则按此坐标先补点"),
                },
                required=["id"],
                description="内联点引用对象",
            ),
        ],
    }


def point_ref_3d_schema(description: str) -> dict[str, Any]:
    """构建标准 3D 点引用 schema。"""
    return {
        "description": description,
        "oneOf": [
            string_schema("已存在 3D 点对象的 id"),
            strict_object(
                properties={
                    "id": string_schema("3D 点对象 id"),
                    "coords": coords_3d_schema("可选；若该点尚未创建，则按此坐标先补点"),
                },
                required=["id"],
                description="内联 3D 点引用对象",
            ),
        ],
    }


def object_ref_schema(description: str) -> dict[str, Any]:
    """构建对象引用 schema。"""
    return string_schema(description)


def point_pair_2d_schema(description: str) -> dict[str, Any]:
    """构建长度为 2 的 2D 点引用数组 schema。"""
    return {
        "type": "array",
        "description": description,
        "items": point_ref_2d_schema("点引用"),
        "minItems": 2,
        "maxItems": 2,
    }


def point_pair_3d_schema(description: str) -> dict[str, Any]:
    """构建长度为 2 的 3D 点引用数组 schema。"""
    return {
        "type": "array",
        "description": description,
        "items": point_ref_3d_schema("3D 点引用"),
        "minItems": 2,
        "maxItems": 2,
    }


def point_triple_2d_schema(description: str) -> dict[str, Any]:
    """构建长度为 3 的 2D 点引用数组 schema。"""
    return {
        "type": "array",
        "description": description,
        "items": point_ref_2d_schema("点引用"),
        "minItems": 3,
        "maxItems": 3,
    }


def object_pair_schema(description: str) -> dict[str, Any]:
    """构建长度为 2 的对象引用数组 schema。"""
    return {
        "type": "array",
        "description": description,
        "items": object_ref_schema("对象引用"),
        "minItems": 2,
        "maxItems": 2,
    }


def placement_schema() -> dict[str, Any]:
    """构建点在对象上的定位方式 schema。"""
    fixed_schema = strict_object(
        properties={
            "mode": {
                "type": "string",
                "const": "fixed",
                "description": "固定参数位置",
            },
            "value": number_schema("固定位置参数值"),
        },
        required=["mode", "value"],
        description="固定位置 placement",
    )

    slider_schema = strict_object(
        properties={
            "mode": {
                "type": "string",
                "const": "slider",
                "description": "滑动条控制位置",
            },
            "name": string_schema("滑动条对象名"),
            "min": number_schema("滑动条最小值"),
            "max": number_schema("滑动条最大值"),
            "step": number_schema("滑动条步长", positive_only=True),
            "init": number_schema("滑动条初始值"),
        },
        required=["mode"],
        description="滑动条 placement",
    )

    return {
        "description": "点在对象上的定位方式",
        "oneOf": [fixed_schema, slider_schema],
    }


def pick_schema() -> dict[str, Any]:
    """构建多解选取 schema。"""
    return strict_object(
        properties={
            "mode": {
                "type": "string",
                "const": "index",
                "description": "按 GeoGebra 返回顺序选取",
            },
            "value": integer_schema("从 1 开始的解序号", minimum=1),
        },
        required=["mode", "value"],
        description="多解选取方式",
    )


# ========== 顶层请求复用结构 ==========
def step_schema(type_name: str, params_schema: dict[str, Any]) -> dict[str, Any]:
    """构建标准连续步骤 schema。"""
    return strict_object(
        properties={
            "type": {
                "type": "string",
                "const": type_name,
                "description": "图形类型",
            },
            "id": id_schema("当前步骤创建对象的唯一标识"),
            "params": params_schema,
        },
        required=["type", "id", "params"],
        description=f"{type_name} 步骤",
    )


def single_draw_conditional(type_name: str, params_schema: dict[str, Any]) -> dict[str, Any]:
    """构建单图形模式按 draw_type 分流的条件 schema。"""
    return {
        "if": {
            "properties": {
                "draw_type": {"const": type_name},
            },
            "required": ["draw_type"],
        },
        "then": {
            "properties": {
                "params": params_schema,
            }
        },
    }
