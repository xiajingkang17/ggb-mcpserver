"""
3D 图形 handler 导出。

当前先暴露第一批基础图形：
1. handle_point_3d
2. handle_segment_3d
3. handle_sphere_center_radius
4. handle_point_on_segment_3d
5. handle_polygon_3d
6. handle_cylinder_radius_height
7. handle_cone_radius_height
8. handle_pyramid_all_vertices
9. handle_prism_all_vertices
"""

from .basic import (
    handle_point_3d,
    handle_point_on_segment_3d,
    handle_polygon_3d,
    handle_segment_3d,
)
from .solids import (
    handle_cone_radius_height,
    handle_cylinder_radius_height,
    handle_prism_all_vertices,
    handle_pyramid_all_vertices,
    handle_sphere_center_radius,
)

__all__ = [
    "handle_point_3d",
    "handle_segment_3d",
    "handle_sphere_center_radius",
    "handle_point_on_segment_3d",
    "handle_polygon_3d",
    "handle_cylinder_radius_height",
    "handle_cone_radius_height",
    "handle_pyramid_all_vertices",
    "handle_prism_all_vertices",
]
