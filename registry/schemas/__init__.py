"""
GeoGebra 标准参数 schema 定义。

本模块职责：
1. 汇总标准 function / 2D / 3D type 的精确 `params_schema`。
2. 为 registry 层提供统一的 schema 访问入口。
3. 避免上层直接关心各类别 schema 文件拆分细节。
"""

from __future__ import annotations

from typing import Any

from .function import build_standard_function_params_schema_map
from .three_d import build_standard_3d_params_schema_map
from .two_d import build_standard_2d_params_schema_map


def build_standard_params_schema_map() -> dict[str, dict[str, Any]]:
    """返回标准 function / 2D / 3D type 的统一 params_schema 映射。"""
    return {
        **build_standard_function_params_schema_map(),
        **build_standard_2d_params_schema_map(),
        **build_standard_3d_params_schema_map(),
    }
