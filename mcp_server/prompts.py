"""
MCP Prompt 注册与读取。
"""

from typing import Any, Callable, Mapping, Sequence

from mcp.types import Prompt, TextContent

PromptBuilder = Callable[[str], str]
PromptRegistry = Mapping[str, PromptBuilder]


def build_prompt_definitions(prompt_registry: PromptRegistry) -> list[Prompt]:
    """根据 prompt 注册表构建 MCP prompt 定义。"""
    prompts: list[Prompt] = []

    for prompt_name in prompt_registry:
        prompts.append(
            Prompt(
                name=prompt_name,
                description="将几何题目转换为 GeoGebra 原生命令 JSON 并导出 HTML。",
                arguments=[
                    {
                        "name": "geometry_problem",
                        "description": "几何题目描述",
                        "required": True,
                    }
                ],
            )
        )

    return prompts


async def handle_prompt_get(
    name: str,
    arguments: dict[str, Any],
    *,
    prompt_registry: PromptRegistry,
) -> Sequence[TextContent]:
    """读取指定 prompt 内容。"""
    geometry_problem = arguments.get("geometry_problem", "")
    builder = prompt_registry.get(name)

    if builder is None:
        return [TextContent(type="text", text=f"未知 prompt：{name}")]

    return [TextContent(type="text", text=builder(geometry_problem))]
