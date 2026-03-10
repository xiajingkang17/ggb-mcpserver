"""
shapes 执行上下文。

本模块职责：
1. 统一封装单次 shape handler 执行时共享的上下文对象。
2. 统一处理命令批量提交前后的日志输出。
3. 为后续把更多图形迁移到独立 handler 提供稳定基础设施。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .collector import CommandCollector, stderr_print


# ========== Shape 执行上下文 ==========
@dataclass(slots=True)
class ShapeContext:
    """单次 shape handler 执行时的上下文对象。

    Args:
        page: 当前 Playwright 页面对象
        collector: 当前图形专属的命令收集器
        skip_coord_init: 是否跳过坐标系初始化
    """

    page: Any
    collector: CommandCollector
    skip_coord_init: bool = False


def execute_context(ctx: ShapeContext) -> None:
    """统一提交当前上下文中收集的 GeoGebra 命令。

    这里保留旧实现中的批量执行日志，避免迁移过程中丢失已有调试信息。
    """
    stderr_print(f"[批量执行] 准备执行 {len(ctx.collector.commands)} 条命令")
    ctx.collector.execute_batch(ctx.page)
    stderr_print("[批量执行] 完成")
