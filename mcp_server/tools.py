"""
MCP Tool 注册与调用分发。

本模块职责：
1. 统一构建 MCP tool 元信息。
2. 统一处理 MCP tool 调用分发。
3. 通过 registry 抽象隔离 server 层与底层绘图工具细节。
"""

import asyncio
from typing import Any, Callable, Protocol, Sequence

from mcp.types import ImageContent, TextContent, Tool


# ========== 类型约束 ==========
ExportHtmlSync = Callable[..., tuple[bool, str, str]]
ClearCanvas = Callable[[], str]


class ToolRegistryLike(Protocol):
    """约束 server 层依赖的 registry 能力边界。"""

    def build_export_input_schema(self) -> dict[str, Any]:
        """返回 export_interactive_html 对应的输入 schema。"""


# ========== Tool 定义构建 ==========
def build_tool_definitions(tool_registry: ToolRegistryLike) -> list[Tool]:
    """构建 MCP tool 定义。

    说明：
    当前 MCP 层仍然只暴露两个顶层工具：
    1. clear_canvas_web
    2. export_interactive_html

    其中 export_interactive_html 的 draw_type / steps 枚举，
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
                "支持单个图形或连续绘制多个图形。"
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
        params = arguments.get("params", {})
        steps = arguments.get("steps")
        mode = arguments.get("mode", "auto")
        save_dir = arguments.get("save_dir")

        try:
            success, message, html = await asyncio.to_thread(
                export_html_sync,
                draw_type=draw_type,
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
