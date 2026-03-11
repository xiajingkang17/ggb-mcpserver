"""
MCP Server 创建与注册。
"""

from typing import Sequence

from mcp.server import Server
from mcp.types import ImageContent, Prompt, Resource, TextContent, Tool

from .prompts import PromptRegistry, build_prompt_definitions, handle_prompt_get
from .resources import build_resource_definitions, read_resource_content
from .tools import ClearCanvas, ExportHtmlSync, build_tool_definitions, handle_tool_call


def create_server(
    *,
    server_name: str,
    prompt_registry: PromptRegistry,
    clear_canvas: ClearCanvas,
    export_html_sync: ExportHtmlSync,
) -> Server:
    """创建并注册 MCP Server。"""
    server = Server(server_name)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return build_tool_definitions()

    @server.list_resources()
    async def list_resources() -> list[Resource]:
        return build_resource_definitions()

    @server.read_resource()
    async def read_resource(uri) -> Sequence[object]:
        return read_resource_content(str(uri))

    @server.call_tool()
    async def call_tool(
        name: str,
        arguments: dict[str, object],
    ) -> Sequence[TextContent | ImageContent]:
        return await handle_tool_call(
            name,
            arguments,
            clear_canvas=clear_canvas,
            export_html_sync=export_html_sync,
        )

    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        return build_prompt_definitions(prompt_registry)

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict[str, object]) -> Sequence[TextContent]:
        return await handle_prompt_get(
            name,
            arguments,
            prompt_registry=prompt_registry,
        )

    return server
