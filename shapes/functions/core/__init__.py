"""
函数核心 handler 导出。

本模块职责：
1. 汇总函数类标准 type 的核心 handler。
2. 为上层 `shapes.functions` 提供稳定的子模块出口。
3. 给后续函数能力继续拆分预留清晰目录层级。
"""

from .expression import handle_function

__all__ = [
    "handle_function",
]
