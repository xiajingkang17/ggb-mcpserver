"""
GeoGebra 绘图工具注册模型。

本模块职责：
1. 定义 registry 层统一使用的工具规格对象。
2. 统一约束图形名称、工具类别、处理函数、参数 schema 等元数据字段。
3. 为后续 shapes 层拆分提供稳定的数据边界，避免 server/session 直接依赖底层实现细节。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal


# ========== 注册模型基础类型 ==========
ToolCategory = Literal["2d", "3d", "function"]
ToolHandler = Callable[..., Any]


def _default_params_schema() -> dict[str, Any]:
    """返回默认的图形参数 schema。

    当前阶段还没有细分到“每个图形独立 schema”。
    因此 registry 先统一维护通用 object schema，
    后续 shapes 层细化之后，可以在这里继续下沉为更精确的结构。
    """
    return {
        "type": "object",
        "description": "图形参数",
    }


@dataclass(frozen=True, slots=True)
class ToolSpec:
    """单个绘图工具的注册规格。

    Args:
        name: 图形类型名称，对应 draw_type
        category: 图形所属类别，区分 2d / 3d / function
        handler: 实际绘图处理函数
        params_schema: 当前图形参数的 schema 描述
        description: 当前图形的补充说明
    """

    name: str
    category: ToolCategory
    handler: ToolHandler
    params_schema: dict[str, Any] = field(default_factory=_default_params_schema)
    description: str = ""
