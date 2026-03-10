"""
2D 图形 handler 导出。

本模块职责：
1. 对外统一暴露标准 2D handler 入口。
2. 保持标准 type 与实际导出入口一致。
"""

from .basic import handle_line, handle_point, handle_segment
from .conics import (
    handle_arc,
    handle_circle,
    handle_ellipse,
    handle_hyperbola,
    handle_parabola,
)
from .relations import (
    handle_angle_bisector,
    handle_intersection,
    handle_perpendicular_line,
    handle_point_on,
    handle_tangent,
)

__all__ = [
    "handle_point",
    "handle_segment",
    "handle_line",
    "handle_circle",
    "handle_ellipse",
    "handle_parabola",
    "handle_hyperbola",
    "handle_arc",
    "handle_point_on",
    "handle_intersection",
    "handle_perpendicular_line",
    "handle_angle_bisector",
    "handle_tangent",
]
