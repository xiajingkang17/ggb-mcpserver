#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GeoGebra Web MCP stdio 服务入口。

当前文件保留原有 stdio 启动方式：
- `python geogebra_web_api.py`

如果需要远程接入，请使用并行提供的 HTTP 入口：
- `python geogebra_web_api_http.py`
"""

import asyncio

from geogebra_runtime import SERVER_NAME, SERVER_VERSION, create_geogebra_runtime
from mcp_server import run_server

runtime = create_geogebra_runtime()
server = runtime.server


def main() -> None:
    """启动 stdio MCP server。"""
    try:
        asyncio.run(
            run_server(
                server,
                print,
                server_name=SERVER_NAME,
                server_version=SERVER_VERSION,
            )
        )
    finally:
        runtime.session_manager.close_all()


if __name__ == "__main__":
    main()
