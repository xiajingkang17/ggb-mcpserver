#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GeoGebra MCP 的 LangChain HTTP 集成示例。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from pathlib import Path
from typing import Any, Sequence

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient

PROJECT_ROOT = Path(__file__).resolve().parent
DOTENV_PATH = PROJECT_ROOT / ".env"
_JSON_CODE_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)

GEOMETRY_AGENT_SYSTEM_PROMPT = """你在调用一个 GeoGebra MCP。
对于几何绘图任务：
1. 优先调用 `read_mcp_resource` 读取 `ggb://catalog/overview`
2. 再调用 `read_mcp_resource` 读取 `ggb://rules/ggb-commands`
3. 再按题型补读子资源：
- 2D 基础对象与路径动点：`ggb://rules/ggb-commands-2d-basic`
- 2D 圆锥曲线：`ggb://rules/ggb-commands-2d-conics`
- 2D 几何关系：`ggb://rules/ggb-commands-2d-relations`
- 函数：`ggb://rules/ggb-commands-functions`
- 滑动条：`ggb://rules/ggb-commands-sliders`
- 3D 基础对象与动点：`ggb://rules/ggb-commands-3d`
4. 如需查看服务端 prompt，可调用 `read_mcp_prompt` 读取 `unified_geometry`
5. 只使用 `export_interactive_html`
6. 只使用 `{mode, save_dir, commands}` 这一种公开协议
7. 调用工具时直接传 `mode`、`save_dir`、`commands`
8. `mode` 必须显式指定为 `2d` 或 `3d`，不要传 `auto`
9. `commands` 中每一项必须只有 `id` 和 `cmd`
10. `cmd` 必须是单条带显式赋值的 GeoGebra 原生命令
11. `id` 必须和命令左侧对象名一致
12. 所有要显示或后续要引用的对象都必须显式命名
13. 题目给名对象优先使用题目名称；未命名辅助对象使用稳定名字
14. 切线、垂线等关系对象如果后续还要用到切点、垂足，必须再补一个点命令
15. 如果任务要求导出 HTML，就必须真的调用工具，不要只输出文字分析
"""


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Connect LangChain to the GeoGebra MCP server over HTTP.",
    )
    parser.add_argument(
        "--mcp-url",
        default="http://127.0.0.1:8000/mcp",
        help="Streamable HTTP MCP endpoint.",
    )
    parser.add_argument(
        "--server-name",
        default="geogebra",
        help="Logical server name used inside MultiServerMCPClient.",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Kimi model name. Defaults to KIMI_MODEL in .env.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Optional model temperature. Defaults to KIMI_TEMPERATURE in .env if set.",
    )
    parser.add_argument(
        "--query",
        help="Natural-language request for the LangChain agent. If omitted, only list tools.",
    )
    parser.add_argument(
        "--tool-name",
        help="Optional direct LangChain tool invocation target.",
    )
    parser.add_argument(
        "--tool-args-json",
        default="{}",
        help='JSON object string used with --tool-name, e.g. {"mode":"2d","commands":[...]}',
    )
    parser.add_argument(
        "--stateful",
        action="store_true",
        help="Keep one MCP session open for the lifetime of this script run.",
    )
    parser.add_argument(
        "--header",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Optional HTTP header passed to the MCP server. Can be repeated.",
    )
    return parser


def _load_environment() -> None:
    load_dotenv(dotenv_path=DOTENV_PATH, override=False)


def _get_env(*names: str, default: str | None = None) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value is not None:
            stripped = value.strip()
            if stripped:
                return stripped
    return default


def _looks_like_placeholder(value: str | None) -> bool:
    if value is None:
        return True
    normalized = value.strip().lower()
    return normalized in {
        "",
        "your_kimi_api_key_here",
        "your_moonshot_api_key_here",
        "replace_me",
    }


def _get_temperature(args: argparse.Namespace) -> float | None:
    if args.temperature is not None:
        return args.temperature

    raw = _get_env("KIMI_TEMPERATURE")
    if raw is None:
        return None

    try:
        return float(raw)
    except ValueError as exc:
        raise ValueError("KIMI_TEMPERATURE 必须是可解析的数字") from exc


def _build_kimi_chat_model(args: argparse.Namespace) -> ChatOpenAI:
    api_key = _get_env("KIMI_API_KEY", "MOONSHOT_API_KEY")
    if _looks_like_placeholder(api_key):
        raise ValueError(
            f"未在 {DOTENV_PATH.name} 中配置有效的 KIMI_API_KEY 或 MOONSHOT_API_KEY"
        )

    model_name = args.model or _get_env("KIMI_MODEL", default="kimi-k2-0905-preview")
    base_url = _get_env("KIMI_BASE_URL", default="https://api.moonshot.cn/v1")
    temperature = _get_temperature(args)

    kwargs: dict[str, Any] = {
        "model": model_name,
        "api_key": api_key,
        "base_url": base_url,
    }
    if temperature is not None:
        kwargs["temperature"] = temperature

    return ChatOpenAI(**kwargs)


def _parse_headers(raw_headers: list[str]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for raw_header in raw_headers:
        if "=" not in raw_header:
            raise ValueError(f"Invalid header format: {raw_header!r}. Expected KEY=VALUE.")
        key, value = raw_header.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Invalid header key: {raw_header!r}")
        headers[key] = value.strip()
    return headers


def _build_client(args: argparse.Namespace) -> MultiServerMCPClient:
    server_config: dict[str, Any] = {
        "transport": "http",
        "url": args.mcp_url,
    }
    headers = _parse_headers(args.header)
    if headers:
        server_config["headers"] = headers

    return MultiServerMCPClient(
        {
            args.server_name: server_config,
        }
    )


def _tool_names(tools: list[Any]) -> list[str]:
    names: list[str] = []
    for tool in tools:
        name = getattr(tool, "name", None) or getattr(tool, "tool_name", None)
        if isinstance(name, str):
            names.append(name)
        else:
            names.append(repr(tool))
    return names


def _normalize_message_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
                continue
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
                    continue
            parts.append(json.dumps(item, ensure_ascii=False))
        return "\n".join(parts)
    return json.dumps(content, ensure_ascii=False)


def _extract_final_text(result: Any) -> str:
    if isinstance(result, dict):
        messages = result.get("messages")
        if isinstance(messages, list) and messages:
            last_message = messages[-1]
            content = getattr(last_message, "content", None)
            if content is not None:
                return _normalize_message_content(content)
        return json.dumps(result, ensure_ascii=False, default=str, indent=2)

    return str(result)


def _truncate_text(text: str, *, limit: int = 4000) -> str:
    """限制调试输出长度。"""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...<truncated>"


def _format_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, default=str, indent=2)


def _normalize_tool_call_args(raw_args: Any) -> str:
    """把 tool call 参数整理成易读文本。"""
    if isinstance(raw_args, str):
        try:
            parsed = json.loads(raw_args)
        except json.JSONDecodeError:
            return raw_args
        return json.dumps(parsed, ensure_ascii=False, default=str, indent=2)
    return _format_value(raw_args)


def _extract_tool_calls(message: Any) -> list[dict[str, Any]]:
    """从 AIMessage 中提取标准化后的 tool call 列表。"""
    tool_calls = getattr(message, "tool_calls", None)
    if isinstance(tool_calls, list):
        return [tool_call for tool_call in tool_calls if isinstance(tool_call, dict)]

    additional_kwargs = getattr(message, "additional_kwargs", None)
    if not isinstance(additional_kwargs, dict):
        return []

    raw_tool_calls = additional_kwargs.get("tool_calls")
    if not isinstance(raw_tool_calls, list):
        return []

    normalized: list[dict[str, Any]] = []
    for raw_tool_call in raw_tool_calls:
        if not isinstance(raw_tool_call, dict):
            continue
        function_payload = raw_tool_call.get("function")
        if isinstance(function_payload, dict):
            normalized.append(
                {
                    "id": raw_tool_call.get("id"),
                    "name": function_payload.get("name"),
                    "args": function_payload.get("arguments"),
                }
            )
            continue
        normalized.append(raw_tool_call)
    return normalized


def _build_agent_trace(result: Any) -> str:
    """把 agent 执行过程整理成可读 trace。"""
    if not isinstance(result, dict):
        return ""

    messages = result.get("messages")
    if not isinstance(messages, list) or not messages:
        return ""

    lines: list[str] = []
    saw_tool_activity = False

    for index, message in enumerate(messages, start=1):
        message_type = message.__class__.__name__

        if message_type == "HumanMessage":
            continue

        tool_calls = _extract_tool_calls(message)
        if tool_calls:
            saw_tool_activity = True
            lines.append(f"[{index}] 模型发起工具调用")
            for tool_call in tool_calls:
                tool_name = tool_call.get("name") or "<unknown>"
                lines.append(f"tool: {tool_name}")
                lines.append("args:")
                lines.append(_truncate_text(_normalize_tool_call_args(tool_call.get("args"))))
            continue

        if message_type == "ToolMessage":
            saw_tool_activity = True
            tool_name = getattr(message, "name", None) or "<unknown>"
            lines.append(f"[{index}] 工具返回：{tool_name}")
            lines.append(
                _truncate_text(
                    _normalize_message_content(getattr(message, "content", ""))
                )
            )
            continue

        content = _normalize_message_content(getattr(message, "content", ""))
        if not content.strip():
            continue

        label = "模型最终回复" if index == len(messages) else "模型中间回复"
        lines.append(f"[{index}] {label}")
        lines.append(_truncate_text(content))

    if not lines:
        return ""

    if not saw_tool_activity:
        lines.insert(0, "[trace] 本次 agent 没有产生任何工具调用。")

    return "\n".join(lines)


def _has_tool_call(result: Any, tool_name: str) -> bool:
    """检查本轮 agent 是否真的调用过指定工具。"""
    if not isinstance(result, dict):
        return False

    messages = result.get("messages")
    if not isinstance(messages, list):
        return False

    for message in messages:
        for tool_call in _extract_tool_calls(message):
            if tool_call.get("name") == tool_name:
                return True
    return False


def _looks_like_export_payload(payload: Any) -> bool:
    """判断对象是否像 export_interactive_html 的公开入参。"""
    if not isinstance(payload, dict):
        return False

    allowed_keys = {"mode", "save_dir", "commands"}
    if any(key not in allowed_keys for key in payload):
        return False

    mode = payload.get("mode")
    commands = payload.get("commands")
    save_dir = payload.get("save_dir")

    if not isinstance(mode, str) or mode not in {"2d", "3d"}:
        return False
    if save_dir is not None and not isinstance(save_dir, str):
        return False
    if not isinstance(commands, list) or not commands:
        return False

    for item in commands:
        if not isinstance(item, dict):
            return False
        if set(item) != {"id", "cmd"}:
            return False
        if not isinstance(item.get("id"), str) or not item["id"].strip():
            return False
        if not isinstance(item.get("cmd"), str) or not item["cmd"].strip():
            return False

    return True


def _extract_first_json_object(text: str) -> str | None:
    """从普通文本里提取第一个平衡的大括号对象。"""
    start = -1
    depth = 0
    in_string = False
    escaped = False

    for index, char in enumerate(text):
        if start < 0:
            if char == "{":
                start = index
                depth = 1
            continue

        if escaped:
            escaped = False
            continue

        if char == "\\" and in_string:
            escaped = True
            continue

        if char == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == "{":
            depth += 1
            continue

        if char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]

    return None


def _extract_export_payload_from_text(text: str) -> dict[str, Any] | None:
    """从模型最终文本里提取合法的导出 JSON。"""
    candidates: list[str] = []
    stripped = text.strip()
    if stripped:
        candidates.append(stripped)

    candidates.extend(match.group(1).strip() for match in _JSON_CODE_BLOCK_RE.finditer(text))

    json_object = _extract_first_json_object(text)
    if json_object:
        candidates.append(json_object.strip())

    seen: set[str] = set()
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if _looks_like_export_payload(parsed):
            return parsed

    return None


async def _maybe_auto_invoke_export(tools: list[Any], result: Any) -> str | None:
    """模型没调导出工具但给了合法 JSON 时，自动补调一次。"""
    if _has_tool_call(result, "export_interactive_html"):
        return None

    final_text = _extract_final_text(result)
    payload = _extract_export_payload_from_text(final_text)
    if payload is None:
        return None

    export_tool = _find_tool(tools, "export_interactive_html")
    tool_result = await export_tool.ainvoke(payload)
    return _format_value(tool_result)


def _find_tool(tools: list[Any], tool_name: str) -> Any:
    for tool in tools:
        current_name = getattr(tool, "name", None) or getattr(tool, "tool_name", None)
        if current_name == tool_name:
            return tool
    available = ", ".join(_tool_names(tools))
    raise ValueError(f"Tool {tool_name!r} not found. Available tools: {available}")


def _format_prompt_messages(messages: Sequence[BaseMessage]) -> str:
    """把 MCP prompt 消息转成可读文本。"""
    if not messages:
        return "[EMPTY] prompt 返回为空"

    parts: list[str] = []
    for message in messages:
        role = "assistant" if isinstance(message, AIMessage) else "user"
        parts.append(f"[{role}]\n{_normalize_message_content(message.content)}")
    return "\n\n".join(parts)


def _build_context_tools(
    client: MultiServerMCPClient,
    server_name: str,
    *,
    session=None,
) -> list[StructuredTool]:
    """构建供 agent 主动读取资源和 prompt 的辅助工具。"""

    async def read_mcp_resource(uri: str) -> str:
        """读取指定 MCP resource 的文本内容。常用于读取 overview 和 ggb-commands 规则。"""
        try:
            if session is None:
                blobs = await client.get_resources(server_name=server_name, uris=uri)
            else:
                from langchain_mcp_adapters.resources import load_mcp_resources

                blobs = await load_mcp_resources(session, uris=uri)
        except Exception as exc:
            return f"[ERROR] 读取 resource 失败：{uri}\n{exc}"

        if not blobs:
            return f"[ERROR] 未找到 resource：{uri}"

        parts = []
        for blob in blobs:
            try:
                parts.append(blob.as_string())
            except Exception as exc:
                parts.append(f"[ERROR] 资源无法转成文本：{exc}")

        return f"[RESOURCE] {uri}\n\n" + "\n\n".join(parts)

    async def read_mcp_prompt(
        prompt_name: str,
        geometry_problem: str = "",
    ) -> str:
        """读取指定 MCP prompt 的文本内容。对 unified_geometry 可传入 geometry_problem。"""
        prompt_args = (
            {"geometry_problem": geometry_problem}
            if geometry_problem.strip()
            else {}
        )
        try:
            if session is None:
                messages = await client.get_prompt(
                    server_name,
                    prompt_name,
                    arguments=prompt_args or None,
                )
            else:
                from langchain_mcp_adapters.prompts import load_mcp_prompt

                messages = await load_mcp_prompt(
                    session,
                    prompt_name,
                    arguments=prompt_args or None,
                )
        except Exception as exc:
            return f"[ERROR] 读取 prompt 失败：{prompt_name}\n{exc}"

        return f"[PROMPT] {prompt_name}\n\n{_format_prompt_messages(messages)}"

    return [
        StructuredTool.from_function(
            coroutine=read_mcp_resource,
            name="read_mcp_resource",
            description=(
                "读取 MCP resource 的文本内容。优先用于读取 "
                "ggb://catalog/overview、ggb://rules/ggb-commands 及其子资源。"
            ),
        ),
        StructuredTool.from_function(
            coroutine=read_mcp_prompt,
            name="read_mcp_prompt",
            description=(
                "读取 MCP prompt 的文本内容。对于几何题，可读取 unified_geometry，"
                "并把当前题目通过 geometry_problem 传入。"
            ),
        ),
    ]


async def _maybe_invoke_direct_tool(tools: list[Any], args: argparse.Namespace) -> bool:
    if not args.tool_name:
        return False

    try:
        tool_args = json.loads(args.tool_args_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"--tool-args-json must be a JSON object: {exc.msg}") from exc

    if not isinstance(tool_args, dict):
        raise ValueError("--tool-args-json must decode to a JSON object")

    tool = _find_tool(tools, args.tool_name)
    result = await tool.ainvoke(tool_args)
    print("\nTool result:\n")
    print(_format_value(result))
    return True


async def _run_stateless(args: argparse.Namespace) -> None:
    client = _build_client(args)
    mcp_tools = await client.get_tools()
    helper_tools = _build_context_tools(client, args.server_name)
    tools = [*mcp_tools, *helper_tools]

    print("Loaded tools:")
    for name in _tool_names(tools):
        print(f"- {name}")

    if await _maybe_invoke_direct_tool(tools, args):
        return

    if not args.query:
        return

    agent = create_agent(_build_kimi_chat_model(args), tools)
    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "system",
                    "content": GEOMETRY_AGENT_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": args.query,
                },
            ]
        }
    )
    trace = _build_agent_trace(result)
    if trace:
        print("\nAgent trace:\n")
        print(trace)
    print("\nAgent result:\n")
    print(_extract_final_text(result))

    auto_export_result = await _maybe_auto_invoke_export(tools, result)
    if auto_export_result is not None:
        print("\nAuto export fallback:\n")
        print("[auto] 模型未直接调用 export_interactive_html，已根据最终回复中的 JSON 自动补调。")
        print(auto_export_result)


async def _run_stateful(args: argparse.Namespace) -> None:
    from langchain_mcp_adapters.tools import load_mcp_tools

    client = _build_client(args)

    async with client.session(args.server_name) as session:
        mcp_tools = await load_mcp_tools(session)
        helper_tools = _build_context_tools(
            client,
            args.server_name,
            session=session,
        )
        tools = [*mcp_tools, *helper_tools]

        print("Loaded tools from persistent session:")
        for name in _tool_names(tools):
            print(f"- {name}")

        if await _maybe_invoke_direct_tool(tools, args):
            return

        if not args.query:
            return

        agent = create_agent(_build_kimi_chat_model(args), tools)
        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "system",
                        "content": GEOMETRY_AGENT_SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": args.query,
                    },
                ]
            }
        )
        trace = _build_agent_trace(result)
        if trace:
            print("\nAgent trace:\n")
            print(trace)
        print("\nAgent result:\n")
        print(_extract_final_text(result))

        auto_export_result = await _maybe_auto_invoke_export(tools, result)
        if auto_export_result is not None:
            print("\nAuto export fallback:\n")
            print("[auto] 模型未直接调用 export_interactive_html，已根据最终回复中的 JSON 自动补调。")
            print(auto_export_result)


async def main_async() -> None:
    _load_environment()
    args = _build_arg_parser().parse_args()

    if args.stateful:
        await _run_stateful(args)
        return

    await _run_stateless(args)


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
