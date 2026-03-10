"""
shapes 公共基础设施导出。

当前统一暴露：
1. CommandCollector：批量命令收集器
2. stderr_print：统一调试输出
3. ShapeContext：shape 执行上下文
4. execute_context：统一批量执行入口
"""

from .collector import CommandCollector, stderr_print
from .context import ShapeContext, execute_context

__all__ = [
    "CommandCollector",
    "stderr_print",
    "ShapeContext",
    "execute_context",
]
