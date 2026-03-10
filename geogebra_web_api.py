#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GeoGebra Web MCP 服务端入口。

这个文件现在只保留“装配职责”，不再直接承担工具注册表维护与绘图分发逻辑。

==============================
【当前职责】
==============================

1. 创建 session 管理器
   - 负责把 browser / page 生命周期管理能力接入 server

2. 创建默认 registry
   - 统一维护 draw_type 的类别、handler 映射、参数 schema

3. 装配 MCP Server
   - 把 registry、session、prompt 注册表拼接为最终可运行的 MCP 服务

==============================
【层次关系】
==============================

- registry 层：
  维护图形工具元数据，替代分散的 get_*_tools() + if/elif 分发。

- session 层：
  负责 Playwright、页面复用、画布清理、HTML 导出编排。

- mcp_server 层：
  负责 MCP tool / prompt 注册，以及参数编排与调用分发。

说明：
主文件现在不再保存兼容包装函数，也不再直接判断“某个 draw_type 属于 2D 还是 3D”。
这部分逻辑已经统一下沉到 registry 层。
"""

import asyncio
from functools import partial

from mcp_server import create_server, run_server
from prompts.prompts_unified import PROMPTS_UNIFIED
from registry import create_default_registry
from session import (
    GeoGebraSessionManager,
    clear_geogebra_canvas as session_clear_geogebra_canvas,
    export_interactive_html_sync as session_export_interactive_html_sync,
)


# ========== 运行时核心对象 ==========
# 统一管理 Playwright 生命周期与 2D / 3D 页面槽位。
session_manager = GeoGebraSessionManager()

# 统一管理 draw_type -> handler / category / schema 的注册关系。
tool_registry = create_default_registry()


# ========== Session 到 Server 的业务桥接 ==========
# server 层只接收稳定函数签名，不需要感知 session 与 registry 的内部结构。
clear_canvas_handler = partial(
    session_clear_geogebra_canvas,
    session_manager,
)

export_html_sync_handler = partial(
    session_export_interactive_html_sync,
    session_manager=session_manager,
    draw_shape=tool_registry.dispatch_draw,
    is_3d_tool=tool_registry.is_3d_tool,
)


# ========== MCP Server 装配 ==========
server = create_server(
    server_name="geogebra-web-drawer",
    tool_registry=tool_registry,
    prompt_registry=PROMPTS_UNIFIED,
    clear_canvas=clear_canvas_handler,
    export_html_sync=export_html_sync_handler,
)


if __name__ == "__main__":
    asyncio.run(
        run_server(
            server,
            print,
            server_name="geogebra-web-drawer",
            server_version="2.0.0",
        )
    )
