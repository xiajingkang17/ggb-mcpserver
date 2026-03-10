"""
MCP Server 运行入口

本模块职责：
1. 统一封装 stdio 运行逻辑
2. 统一配置 InitializationOptions
3. 保持主入口文件足够精简
"""

from collections.abc import Callable

from mcp.server.models import InitializationOptions, ServerCapabilities
from mcp.server.stdio import stdio_server


# ========== Server 运行入口 ==========
async def run_server(
    server,
    stderr_print: Callable[..., None],
    *,
    server_name: str,
    server_version: str,
) -> None:
    """运行 stdio MCP server。

    Args:
        server: 已注册完成的 MCP Server
        stderr_print: 标准错误输出函数
        server_name: server 名称
        server_version: server 版本
    """
    stderr_print("[MCP] GeoGebra Web MCP Server 启动中...")

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=server_name,
                server_version=server_version,
                capabilities=ServerCapabilities(
                    tools={},
                    prompts={},
                ),
            ),
        )
