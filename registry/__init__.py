"""
GeoGebra 绘图 registry 层对外导出。

负责统一暴露：
1. ToolSpec：单个图形工具的注册模型
2. ToolRegistry：注册表核心对象
3. create_default_registry：基于当前仓库已有实现构建默认注册表
"""

from .core import ToolRegistry, create_default_registry
from .models import ToolCategory, ToolHandler, ToolSpec

__all__ = [
    "ToolCategory",
    "ToolHandler",
    "ToolSpec",
    "ToolRegistry",
    "create_default_registry",
]
