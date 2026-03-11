"""
MCP tool 定义与调用分发。
"""

from __future__ import annotations

import asyncio
import re
from typing import Any, Callable, Sequence

from mcp.types import ImageContent, TextContent, Tool

ExportHtmlSync = Callable[..., tuple[bool, str, str]]
ClearCanvas = Callable[[], str]

_COMMAND_ASSIGNMENT_RE = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)(?:\s*\([^)]*\))?\s*="
)
_FORBIDDEN_COMMAND_TOKENS = (
    "deleteall",
    "runscript",
    "execute",
)


def _build_export_schema() -> dict[str, Any]:
    """构建单轨导出工具的公开 schema。"""
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "mode": {
                "type": "string",
                "enum": ["2d", "3d"],
                "description": "导出模式，只能是 2d 或 3d，必须显式指定。",
            },
            "save_dir": {
                "type": "string",
                "description": "可选的 HTML 保存目录。省略时默认保存到 pic，不直接返回 HTML 文本。",
            },
            "commands": {
                "type": "array",
                "description": (
                    "GeoGebra 原生命令数组。每一项都必须是 {id, cmd}，"
                    "其中 cmd 必须是单条带显式赋值的 GeoGebra 原生命令，"
                    "且命令左侧对象名必须与 id 一致。"
                ),
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "对象名，必须与命令左侧对象名一致。",
                        },
                        "cmd": {
                            "type": "string",
                            "description": "单条带显式赋值的 GeoGebra 原生命令。",
                        },
                    },
                    "required": ["id", "cmd"],
                },
            },
        },
        "required": ["mode", "commands"],
    }


def _normalize_mode(mode: Any) -> str:
    """规范化 mode。"""
    if not isinstance(mode, str) or not mode.strip():
        raise ValueError("mode 必须是非空字符串")

    normalized = mode.strip().lower()
    if normalized not in {"2d", "3d"}:
        raise ValueError(f"mode 不支持：{mode}")
    return normalized


def _normalize_save_dir(save_dir: Any) -> str | None:
    """规范化 save_dir。"""
    if save_dir is None:
        return None
    if not isinstance(save_dir, str) or not save_dir.strip():
        raise ValueError("save_dir 必须是非空字符串")
    return save_dir.strip()


def _normalize_command_items(commands: Any) -> list[dict[str, str]]:
    """校验并规范化 commands。"""
    if not isinstance(commands, list):
        raise ValueError("commands 必须是对象数组")
    if not commands:
        raise ValueError("commands 不能为空")

    seen_ids: set[str] = set()
    normalized: list[dict[str, str]] = []

    for index, item in enumerate(commands):
        if not isinstance(item, dict):
            raise ValueError(f"commands[{index}] 必须是对象")

        extra_keys = sorted(key for key in item if key not in {"id", "cmd"})
        if extra_keys:
            joined = ", ".join(extra_keys)
            raise ValueError(f"commands[{index}] 存在不支持的字段：{joined}")

        item_id = item.get("id")
        command = item.get("cmd")

        if not isinstance(item_id, str) or not item_id.strip():
            raise ValueError(f"commands[{index}].id 必须是非空字符串")
        if not isinstance(command, str) or not command.strip():
            raise ValueError(f"commands[{index}].cmd 必须是非空字符串")

        normalized_id = item_id.strip()
        normalized_command = command.strip()

        if "\n" in normalized_command or "\r" in normalized_command:
            raise ValueError(f"commands[{index}].cmd 必须是单行命令")
        if ";" in normalized_command:
            raise ValueError(f"commands[{index}].cmd 不能包含多条命令")
        if normalized_id in seen_ids:
            raise ValueError(f"commands[{index}].id 重复：{normalized_id}")
        seen_ids.add(normalized_id)

        lowered = normalized_command.lower()
        for token in _FORBIDDEN_COMMAND_TOKENS:
            if token in lowered:
                raise ValueError(
                    f"commands[{index}].cmd 包含不允许的命令：{token}"
                )

        match = _COMMAND_ASSIGNMENT_RE.match(normalized_command)
        if not match:
            raise ValueError(
                f"commands[{index}].cmd 必须是带显式赋值的单条命令"
            )

        lhs_name = match.group(1)
        if lhs_name != normalized_id:
            raise ValueError(
                f"commands[{index}] 的 id 与命令左侧对象名不一致："
                f"{normalized_id} != {lhs_name}"
            )

        normalized.append({"id": normalized_id, "cmd": normalized_command})

    return normalized


def _extract_export_payload(arguments: dict[str, Any]) -> dict[str, Any]:
    """从公开 MCP 入参中提取导出 payload。"""
    allowed_keys = {"mode", "save_dir", "commands"}
    unexpected_keys = sorted(key for key in arguments if key not in allowed_keys)
    if unexpected_keys:
        joined = ", ".join(unexpected_keys)
        raise ValueError(f"不支持的导出字段：{joined}")

    if "mode" not in arguments:
        raise ValueError("export_interactive_html 必须显式提供 mode")
    if "commands" not in arguments:
        raise ValueError("export_interactive_html 必须提供 commands")

    return {
        "mode": _normalize_mode(arguments.get("mode")),
        "save_dir": _normalize_save_dir(arguments.get("save_dir")),
        "commands": _normalize_command_items(arguments["commands"]),
    }


def build_tool_definitions() -> list[Tool]:
    """构建对外公开的 MCP tools。"""
    export_schema = _build_export_schema()
    return [
        Tool(
            name="clear_canvas_web",
            description="清除 GeoGebra 画布，清空所有图形。",
            inputSchema={
                "type": "object",
                "additionalProperties": False,
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="export_interactive_html",
            description=(
                "使用 GeoGebra 原生命令 JSON 绘制并导出可交互 HTML。"
                "公开入参直接为 {mode, save_dir, commands}。"
                "commands 中每一项都必须提供 {id, cmd}。"
            ),
            inputSchema=export_schema,
        ),
    ]


async def handle_tool_call(
    name: str,
    arguments: dict[str, Any],
    *,
    clear_canvas: ClearCanvas,
    export_html_sync: ExportHtmlSync,
) -> Sequence[TextContent | ImageContent]:
    """处理 MCP tool 调用。"""
    if name == "clear_canvas_web":
        try:
            result = await asyncio.to_thread(clear_canvas)
            return [TextContent(type="text", text=result)]
        except Exception as exc:
            return [TextContent(type="text", text=f"清除失败：{exc}")]

    if name == "export_interactive_html":
        try:
            payload = _extract_export_payload(arguments)
            success, message, _output_path = await asyncio.to_thread(
                export_html_sync,
                commands=payload["commands"],
                mode=payload["mode"],
                save_dir=payload["save_dir"],
            )

            return [TextContent(type="text", text=message)]
        except Exception as exc:
            return [TextContent(type="text", text=f"导出命令 JSON HTML 失败：{exc}")]

    return [TextContent(type="text", text=f"未知工具：{name}")]
