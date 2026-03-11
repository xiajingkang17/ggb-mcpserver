#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GeoGebra MCP 运行时装配。
"""

from __future__ import annotations

from dataclasses import dataclass
from threading import Lock

from mcp.server import Server

from mcp_server import create_server
from prompts.prompts_unified import PROMPTS_UNIFIED
from session import (
    GeoGebraSessionManager,
    clear_geogebra_canvas as session_clear_geogebra_canvas,
    export_interactive_html_sync as session_export_interactive_html_sync,
)

SERVER_NAME = "geogebra-web-drawer"
SERVER_VERSION = "3.0.0"


@dataclass(slots=True)
class GeoGebraMCPRuntime:
    """GeoGebra MCP 服务运行时。"""

    server: Server
    session_manager: GeoGebraSessionManager


def create_geogebra_runtime() -> GeoGebraMCPRuntime:
    """创建一套单轨命令 JSON 的 GeoGebra 运行时对象。"""
    session_manager = GeoGebraSessionManager()
    operation_lock = Lock()

    def clear_canvas_handler() -> str:
        with operation_lock:
            return session_clear_geogebra_canvas(session_manager)

    def export_html_sync_handler(
        *,
        commands: list[dict[str, str]] | None = None,
        mode: str = "",
        save_dir: str | None = None,
    ) -> tuple[bool, str, str]:
        with operation_lock:
            return session_export_interactive_html_sync(
                commands=commands,
                mode=mode,
                save_dir=save_dir,
                session_manager=session_manager,
            )

    server = create_server(
        server_name=SERVER_NAME,
        prompt_registry=PROMPTS_UNIFIED,
        clear_canvas=clear_canvas_handler,
        export_html_sync=export_html_sync_handler,
    )
    server.version = SERVER_VERSION

    return GeoGebraMCPRuntime(
        server=server,
        session_manager=session_manager,
    )
