"""
GeoGebra MCP Streamable HTTP 运行入口。

本模块职责：
1. 为低层 MCP Server 组装 Streamable HTTP ASGI 应用
2. 统一管理 HTTP session 生命周期与浏览器资源回收
3. 提供 uvicorn 启动封装，避免入口文件重复拼接 Starlette 细节
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from mcp.server import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.types import Receive, Scope, Send

from session import GeoGebraSessionManager


class StreamableHTTPASGIApp:
    """将 StreamableHTTP session manager 暴露为 ASGI app。"""

    def __init__(self, session_manager: StreamableHTTPSessionManager):
        self.session_manager = session_manager

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.session_manager.handle_request(scope, receive, send)


def _normalize_http_path(path: str) -> str:
    """确保 MCP 端点路径以 `/` 开头。"""
    normalized = (path or "/mcp").strip()
    if not normalized:
        return "/mcp"
    if not normalized.startswith("/"):
        return f"/{normalized}"
    return normalized


def create_streamable_http_app(
    server: Server,
    *,
    browser_session_manager: GeoGebraSessionManager,
    path: str = "/mcp",
    json_response: bool = False,
    stateless: bool = False,
    debug: bool = False,
) -> Starlette:
    """创建 GeoGebra MCP 的 Streamable HTTP Starlette 应用。"""
    http_session_manager = StreamableHTTPSessionManager(
        app=server,
        json_response=json_response,
        stateless=stateless,
    )
    mcp_path = _normalize_http_path(path)
    streamable_http_app = StreamableHTTPASGIApp(http_session_manager)

    @asynccontextmanager
    async def lifespan(_: Starlette) -> AsyncIterator[None]:
        async with http_session_manager.run():
            try:
                yield
            finally:
                browser_session_manager.close_all()

    return Starlette(
        debug=debug,
        routes=[
            Route(
                mcp_path,
                endpoint=streamable_http_app,
                name="mcp_streamable_http",
            )
        ],
        lifespan=lifespan,
    )


def run_streamable_http_server(
    server: Server,
    *,
    browser_session_manager: GeoGebraSessionManager,
    host: str = "127.0.0.1",
    port: int = 8000,
    path: str = "/mcp",
    json_response: bool = False,
    stateless: bool = False,
    debug: bool = False,
    log_level: str = "info",
) -> None:
    """运行 GeoGebra MCP 的 Streamable HTTP 服务。"""
    app = create_streamable_http_app(
        server,
        browser_session_manager=browser_session_manager,
        path=path,
        json_response=json_response,
        stateless=stateless,
        debug=debug,
    )
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=log_level,
    )
