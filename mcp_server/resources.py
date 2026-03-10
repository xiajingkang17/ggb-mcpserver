"""
MCP Resource 注册与读取。

本模块职责：
1. 暴露可供 LLM 主动读取的协议说明资源。
2. 提供固定 resources 与参数化 resource templates。
3. 将动态工具规格和静态规则文档统一封装为 MCP 资源。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import urlparse

from mcp.server.lowlevel.helper_types import ReadResourceContents
from mcp.types import Resource, ResourceTemplate


# ========== 类型约束 ==========
class ToolSpecLike(Protocol):
    """约束资源层依赖的工具规格边界。"""

    name: str
    category: str
    params_schema: dict[str, Any]
    description: str


class ToolRegistryLike(Protocol):
    """约束资源层依赖的 registry 能力边界。"""

    def list_tool_specs(self) -> list[ToolSpecLike]:
        """返回全部工具规格。"""

    def get(self, name: str) -> ToolSpecLike:
        """返回指定工具规格。"""


# ========== 资源常量 ==========
RESOURCE_ROOT = Path(__file__).resolve().parent.parent / "mcp_knowledge" / "resources"
RECIPE_ROOT = Path(__file__).resolve().parent.parent / "mcp_knowledge" / "recipes"

OVERVIEW_URI = "ggb://catalog/overview"
NAMING_URI = "ggb://rules/naming"
REFERENCES_URI = "ggb://rules/references"
ARCS_URI = "ggb://rules/arcs"
INTERSECTION_URI = "ggb://rules/intersection"
TYPE_SPEC_TEMPLATE = "ggb://spec/type/{type}"
RECIPE_TOPIC_TEMPLATE = "ggb://recipe/topic/{topic}"

FIXED_RESOURCE_FILES = {
    NAMING_URI: RESOURCE_ROOT / "naming.md",
    REFERENCES_URI: RESOURCE_ROOT / "references.md",
    ARCS_URI: RESOURCE_ROOT / "arcs.md",
    INTERSECTION_URI: RESOURCE_ROOT / "intersection.md",
}


# ========== 资源定义构建 ==========
def build_resource_definitions(tool_registry: ToolRegistryLike) -> list[Resource]:
    """构建固定 resource 定义。"""
    return [
        Resource(
            name="ggb_overview",
            title="GeoGebra 能力总览",
            uri=OVERVIEW_URI,
            description="当前 MCP 支持的 function / 2D / 3D 标准 type 总览",
            mimeType="text/markdown",
        ),
        Resource(
            name="ggb_naming_rules",
            title="对象命名规则",
            uri=NAMING_URI,
            description="公共对象 id、私有辅助对象和引用规则说明",
            mimeType="text/markdown",
        ),
        Resource(
            name="ggb_reference_rules",
            title="对象引用规则",
            uri=REFERENCES_URI,
            description="点引用、对象引用、单步与多步模式的写法说明",
            mimeType="text/markdown",
        ),
        Resource(
            name="ggb_arc_rules",
            title="弧规则",
            uri=ARCS_URI,
            description="优弧、劣弧与弧对象引用规则说明",
            mimeType="text/markdown",
        ),
        Resource(
            name="ggb_intersection_rules",
            title="交点规则",
            uri=INTERSECTION_URI,
            description="当前交点 pick 写法与 index 使用说明",
            mimeType="text/markdown",
        ),
    ]


def build_resource_template_definitions() -> list[ResourceTemplate]:
    """构建参数化 resource template 定义。"""
    return [
        ResourceTemplate(
            name="ggb_type_spec",
            title="按 type 查询参数规范",
            uriTemplate=TYPE_SPEC_TEMPLATE,
            description="读取某个标准 type 的类别、schema 和关键说明",
            mimeType="application/json",
        ),
        ResourceTemplate(
            name="ggb_recipe_topic",
            title="按题型查询标准 recipe",
            uriTemplate=RECIPE_TOPIC_TEMPLATE,
            description="读取常见几何题型的标准 steps 组织方式",
            mimeType="text/markdown",
        )
    ]


# ========== 资源读取辅助 ==========
def _read_static_markdown(path: Path) -> str:
    """读取静态 markdown 资源。"""
    return path.read_text(encoding="utf-8")


def _read_recipe_markdown(topic: str) -> str:
    """读取指定题型 recipe。"""
    recipe_path = RECIPE_ROOT / f"{topic}.md"
    if not recipe_path.exists():
        raise ValueError(f"未知 recipe topic：{topic}")
    return recipe_path.read_text(encoding="utf-8")


def _group_tool_names(tool_registry: ToolRegistryLike) -> dict[str, list[str]]:
    """按类别汇总工具名称。"""
    grouped: dict[str, list[str]] = {
        "function": [],
        "2d": [],
        "3d": [],
    }
    for spec in tool_registry.list_tool_specs():
        grouped.setdefault(spec.category, []).append(spec.name)
    return grouped


def _build_overview_markdown(tool_registry: ToolRegistryLike) -> str:
    """动态构建能力总览 markdown。"""
    grouped = _group_tool_names(tool_registry)
    lines = [
        "# GeoGebra MCP 能力总览",
        "",
        "## 总体规则",
        "- 所有公共对象都必须提供显式 `id`",
        "- 后续引用对象时，只能引用对象 `id`",
        "- 辅助对象使用稳定的派生命名，可作为后续步骤的引用目标",
        "- `function` 使用表达式 `expr` 作为唯一核心输入",
        "",
        "## Function",
    ]

    for name in grouped.get("function", []):
        lines.append(f"- `{name}`")

    lines.extend(["", "## 2D"])
    for name in grouped.get("2d", []):
        lines.append(f"- `{name}`")

    lines.extend(["", "## 3D"])
    for name in grouped.get("3d", []):
        lines.append(f"- `{name}`")

    return "\n".join(lines)


def _build_type_spec_json(tool_registry: ToolRegistryLike, type_name: str) -> str:
    """动态构建指定 type 的规范说明。"""
    spec = tool_registry.get(type_name)
    payload = {
        "type": spec.name,
        "category": spec.category,
        "requires_id": True,
        "params_schema": spec.params_schema,
        "notes": [
            "公共对象必须显式提供 id",
            "后续引用对象时只能使用对象 id",
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _parse_uri(uri: str) -> tuple[str, list[str]]:
    """解析自定义 ggb 资源 URI。"""
    parsed = urlparse(uri)
    parts = [parsed.netloc, *[part for part in parsed.path.split("/") if part]]
    return parsed.scheme, parts


# ========== 对外资源读取 ==========
def read_resource_content(
    uri: str,
    *,
    tool_registry: ToolRegistryLike,
) -> list[ReadResourceContents]:
    """根据 URI 读取资源内容。"""
    if uri == OVERVIEW_URI:
        return [
            ReadResourceContents(
                content=_build_overview_markdown(tool_registry),
                mime_type="text/markdown",
            )
        ]

    static_file = FIXED_RESOURCE_FILES.get(uri)
    if static_file is not None:
        return [
            ReadResourceContents(
                content=_read_static_markdown(static_file),
                mime_type="text/markdown",
            )
        ]

    scheme, parts = _parse_uri(uri)
    if scheme != "ggb":
        raise ValueError(f"不支持的资源 URI：{uri}")

    if parts[:2] == ["spec", "type"] and len(parts) == 3:
        type_name = parts[2]
        return [
            ReadResourceContents(
                content=_build_type_spec_json(tool_registry, type_name),
                mime_type="application/json",
            )
        ]

    if parts[:2] == ["recipe", "topic"] and len(parts) == 3:
        topic = parts[2]
        return [
            ReadResourceContents(
                content=_read_recipe_markdown(topic),
                mime_type="text/markdown",
            )
        ]

    raise ValueError(f"未知资源 URI：{uri}")
