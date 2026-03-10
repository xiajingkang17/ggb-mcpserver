"""
3D 图形 handler 导出。

本模块职责：
1. 对外统一暴露标准 3D handler 入口。
2. 保持标准 type 与实际导出入口一致。
"""

from .basic import (
    handle_point_3d,
    handle_point_on_3d,
    handle_segment_3d,
)
from .solids import (
    handle_cone,
    handle_cylinder,
    handle_sphere,
)

__all__ = [
    "handle_point_3d",
    "handle_segment_3d",
    "handle_point_on_3d",
    "handle_sphere",
    "handle_cylinder",
    "handle_cone",
]
