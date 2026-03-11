#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GeoGebra Web MCP Streamable HTTP 服务入口。

使用示例：
    python geogebra_web_api_http.py --host 0.0.0.0 --port 8000

默认 MCP endpoint：
    http://127.0.0.1:8000/mcp
"""

from __future__ import annotations

import argparse

from geogebra_runtime import create_geogebra_runtime
from mcp_server import run_streamable_http_server


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run GeoGebra MCP server over Streamable HTTP.",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="HTTP bind host. Use 0.0.0.0 to expose to other machines.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="HTTP bind port.",
    )
    parser.add_argument(
        "--path",
        default="/mcp",
        help="Streamable HTTP endpoint path.",
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="uvicorn log level.",
    )
    parser.add_argument(
        "--json-response",
        action="store_true",
        help="Prefer JSON HTTP responses instead of SSE streams when possible.",
    )
    parser.add_argument(
        "--stateless",
        action="store_true",
        help="Create a fresh Streamable HTTP transport for each request.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable Starlette debug mode.",
    )
    return parser


def main() -> None:
    """启动 Streamable HTTP MCP server。"""
    args = _build_arg_parser().parse_args()
    runtime = create_geogebra_runtime()

    try:
        run_streamable_http_server(
            runtime.server,
            browser_session_manager=runtime.session_manager,
            host=args.host,
            port=args.port,
            path=args.path,
            json_response=args.json_response,
            stateless=args.stateless,
            debug=args.debug,
            log_level=args.log_level,
        )
    finally:
        runtime.session_manager.close_all()


if __name__ == "__main__":
    main()
