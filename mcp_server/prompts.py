"""
MCP Prompt 注册与获取处理

本模块职责：
1. 统一构建 prompt 元信息
2. 根据 prompt 注册表读取具体内容
3. 将 server 层与 prompt 业务逻辑解耦
"""

from typing import Any, Callable, Mapping, Sequence

from mcp.types import Prompt, TextContent


# ========== 类型约束 ==========
PromptBuilder = Callable[[str], str]
PromptRegistry = Mapping[str, PromptBuilder]


# ========== Prompt 定义构建 ==========
def build_prompt_definitions(prompt_registry: PromptRegistry) -> list[Prompt]:
    """根据 prompt 注册表构建 MCP prompt 定义。

    Args:
        prompt_registry: prompt 名称到构建函数的映射

    Returns:
        MCP Prompt 定义列表
    """
    prompts: list[Prompt] = []

    for prompt_name in prompt_registry:
        prompts.append(
            Prompt(
                name=prompt_name,
                description="将几何题目转换为GeoGebra绘图步骤参数。",
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


# ========== Prompt 内容读取 ==========
async def handle_prompt_get(
    name: str,
    arguments: dict[str, Any],
    *,
    prompt_registry: PromptRegistry,
) -> Sequence[TextContent]:
    """读取指定 prompt 内容。

    Args:
        name: prompt 名称
        arguments: prompt 参数
        prompt_registry: prompt 注册表

    Returns:
        MCP 文本内容列表
    """
    geometry_problem = arguments.get("geometry_problem", "")
    builder = prompt_registry.get(name)

    if builder is None:
        return [TextContent(type="text", text=f"未知prompt：{name}")]

    return [TextContent(type="text", text=builder(geometry_problem))]
