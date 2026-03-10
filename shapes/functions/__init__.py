"""
函数图像 handler 导出。

本模块职责：
1. 统一暴露函数类标准 type 的 handler。
2. 将函数绘图能力收敛到表达式驱动的单一入口。
3. 为 registry 和调度层提供稳定导出路径。
"""

from .core import handle_function

__all__ = [
    "handle_function",
]
