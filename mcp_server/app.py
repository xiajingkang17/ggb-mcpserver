"""
MCP Server 创建与注册。

本模块职责：
1. 创建 MCP Server 实例。
2. 统一注册 tool / prompt。
3. 把 server 层与 registry / session 业务函数解耦。
"""

from typing import Sequence

from mcp.server import Server
from mcp.types import ImageContent, Prompt, Resource, ResourceTemplate, TextContent, Tool

from .prompts import PromptRegistry, build_prompt_definitions, handle_prompt_get
from .resources import (
    build_resource_definitions,
    build_resource_template_definitions,
    read_resource_content,
)
from .tools import (
    ClearCanvas,
    ExportHtmlSync,
    ToolRegistryLike,
    build_tool_definitions,
    handle_tool_call,
)


# ========== Server 装配入口 ==========
def create_server(
    *,
    server_name: str,
    tool_registry: ToolRegistryLike,
    prompt_registry: PromptRegistry,
    clear_canvas: ClearCanvas,
    export_html_sync: ExportHtmlSync,
) -> Server:
    """创建并注册 MCP Server。

    Args:
        server_name: MCP server 名称
        tool_registry: registry 层对外提供的工具元数据入口
        prompt_registry: prompt 注册表
        clear_canvas: 清空画布业务函数
        export_html_sync: 导出 HTML 业务函数

    Returns:
        已完成 tool / prompt 注册的 MCP Server
    """
    server = Server(server_name)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """列出可用的 MCP tools。"""
        return build_tool_definitions(tool_registry)

    @server.list_resources()
    async def list_resources() -> list[Resource]:
        """列出可用的 MCP resources。"""
        return build_resource_definitions(tool_registry)

    @server.read_resource()
    async def read_resource(uri) -> Sequence[object]:
        """读取指定 resource 内容。"""
        return read_resource_content(str(uri), tool_registry=tool_registry)

    @server.list_resource_templates()
    async def list_resource_templates() -> list[ResourceTemplate]:
        """列出可用的 MCP resource templates。"""
        return build_resource_template_definitions()

    @server.call_tool()
    async def call_tool(
        name: str,
        arguments: dict[str, object],
    ) -> Sequence[TextContent | ImageContent]:
        """处理 MCP tool 调用。"""
        return await handle_tool_call(
            name,
            arguments,
            clear_canvas=clear_canvas,
            export_html_sync=export_html_sync,
        )

    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        """列出可用的 MCP prompts。"""
        return build_prompt_definitions(prompt_registry)

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict[str, object]) -> Sequence[TextContent]:
        """获取指定 prompt 内容。"""
        return await handle_prompt_get(
            name,
            arguments,
            prompt_registry=prompt_registry,
        )

    return server
