"""
GeoGebra 标准函数参数 schema。

本模块职责：
1. 定义标准函数 type 的精确 `params_schema`。
2. 将函数绘图能力收敛到表达式驱动的统一结构。
3. 为 registry 层提供可直接挂接的函数 schema 映射。
"""

from __future__ import annotations

from typing import Any

from .common import number_schema, strict_object, string_schema


# ========== 标准函数 params_schema ==========
def build_standard_function_params_schema_map() -> dict[str, dict[str, Any]]:
    """返回标准函数 type -> params_schema 映射。"""
    slider_schema = strict_object(
        properties={
            "name": string_schema("滑动条名称，可在 expr 中直接引用"),
            "min": number_schema("滑动条最小值"),
            "max": number_schema("滑动条最大值"),
            "step": number_schema("滑动条步长", positive_only=True),
            "init": number_schema("滑动条初始值"),
        },
        required=["name", "min", "max", "step", "init"],
        description="函数滑动条参数",
    )

    return {
        "function": strict_object(
            properties={
                "expr": string_schema("函数右侧表达式，例如 x^2 - 3*x + 2"),
                "sliders": {
                    "type": "array",
                    "description": "函数表达式所依赖的滑动条列表",
                    "items": slider_schema,
                },
            },
            required=["expr"],
            description="标准函数参数",
        ),
    }
