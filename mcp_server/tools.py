"""
MCP Tool 注册与调用分发。

本模块职责：
1. 统一构建 MCP tool 元信息。
2. 统一处理 MCP tool 调用分发。
3. 通过 registry 抽象隔离 server 层与底层绘图工具细节。
"""

import asyncio
import json
from typing import Any, Callable, Protocol, Sequence

from mcp.types import ImageContent, TextContent, Tool


# ========== 类型约束 ==========
ExportHtmlSync = Callable[..., tuple[bool, str, str]]
ClearCanvas = Callable[[], str]


class ToolSpecLike(Protocol):
    """约束资源层依赖的工具规格边界。"""

    name: str
    category: str
    params_schema: dict[str, Any]
    description: str


class ToolRegistryLike(Protocol):
    """约束 server 层依赖的 registry 能力边界。"""

    def build_export_input_schema(self) -> dict[str, Any]:
        """返回 export_interactive_html 对应的输入 schema。"""

    def list_tool_specs(self) -> list[ToolSpecLike]:
        """返回全部工具规格。"""

    def get(self, name: str) -> ToolSpecLike:
        """返回指定工具规格。"""


# ========== Tool 定义构建 ==========
def _parse_step_string(raw_step: str, index: int) -> dict[str, Any]:
    """Parse a JSON-encoded step object from string input."""
    try:
        parsed = json.loads(raw_step)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"steps[{index}] 必须是 JSON 对象字符串：{exc.msg}"
        ) from exc

    if not isinstance(parsed, dict):
        raise ValueError(f"steps[{index}] 解析后必须是对象")

    return parsed


def _normalize_steps(steps: Any) -> list[dict[str, Any]] | None:
    """Accept native step objects and JSON-string fallbacks from MCP bridges."""
    if steps is None:
        return None

    if isinstance(steps, str):
        try:
            steps = json.loads(steps)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"steps 必须是数组，或可解析为数组的 JSON 字符串：{exc.msg}"
            ) from exc

    if not isinstance(steps, list):
        raise ValueError("steps 必须是对象数组，或 JSON 字符串数组")

    normalized: list[dict[str, Any]] = []
    for index, step in enumerate(steps):
        if isinstance(step, dict):
            normalized.append(step)
            continue
        if isinstance(step, str):
            normalized.append(_parse_step_string(step, index))
            continue
        raise ValueError(f"steps[{index}] 必须是对象或 JSON 对象字符串")

    return normalized


def build_tool_definitions(tool_registry: ToolRegistryLike) -> list[Tool]:
    """构建 MCP tool 定义。

    说明：
    当前 MCP 层仍然只暴露两个顶层工具：
    1. clear_canvas_web
    2. export_interactive_html

    其中 export_interactive_html 的 draw_type / id / steps 枚举，
    统一从 registry 层获取，不再由 server 层手工维护。
    """
    export_schema = tool_registry.build_export_input_schema()

    return [
        Tool(
            name="clear_canvas_web",
            description="清除GeoGebra画布，清空所有图形（可选使用，一般不需要）",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="export_interactive_html",
            description=(
                "绘制并导出可交互的 GeoGebra HTML，"
                "支持单个图形或连续绘制多个图形；"
                "所有公共对象都必须提供显式 id。"
            ),
            inputSchema=export_schema,
        ),
    ]


# ========== Tool 调用分发 ==========
async def handle_tool_call(
    name: str,
    arguments: dict[str, Any],
    *,
    clear_canvas: ClearCanvas,
    export_html_sync: ExportHtmlSync,
) -> Sequence[TextContent | ImageContent]:
    """处理 MCP tool 调用。

    这里不直接承载绘图逻辑，只负责：
    1. 解析 MCP 入参
    2. 调用对应业务函数
    3. 组装 MCP 返回值
    """
    if name == "clear_canvas_web":
        try:
            result = await asyncio.to_thread(clear_canvas)
            return [TextContent(type="text", text=result)]
        except Exception as exc:
            return [TextContent(type="text", text=f"清除失败：{exc}")]

    if name == "export_interactive_html":
        draw_type = arguments.get("draw_type")
        object_id = arguments.get("id")
        params = arguments.get("params", {})
        mode = arguments.get("mode", "auto")
        save_dir = arguments.get("save_dir")

        try:
            steps = _normalize_steps(arguments.get("steps"))
            success, message, html = await asyncio.to_thread(
                export_html_sync,
                draw_type=draw_type,
                id=object_id,
                params=params,
                steps=steps,
                mode=mode,
                save_dir=save_dir,
            )

            if not success:
                return [TextContent(type="text", text=message)]

            response: list[TextContent | ImageContent] = [
                TextContent(type="text", text=message)
            ]
            if html:
                response.append(TextContent(type="text", text=f"HTML内容：\n\n{html}"))
            return response
        except Exception as exc:
            return [TextContent(type="text", text=f"导出可交互HTML失败：{exc}")]

    return [TextContent(type="text", text=f"未知工具：{name}")]
