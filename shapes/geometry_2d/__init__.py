"""
2D 图形 handler 导出。

当前先暴露第一批基础图形：
1. handle_point_2d
2. handle_segment
3. handle_line
4. handle_circle_center_radius
5. handle_triangle_points
6. handle_polygon_points
7. handle_point_on_object
8. handle_intersect_2d
9. handle_tangent
10. handle_angle_bisector
11. handle_perpendicular_line
12. handle_ellipse_equation
13. handle_parabola_equation
14. handle_hyperbola_equation
"""

from .basic import handle_line, handle_point_2d, handle_segment
from .conics import (
    handle_circle_center_radius,
    handle_ellipse_equation,
    handle_hyperbola_equation,
    handle_parabola_equation,
)
from .polygons import handle_polygon_points, handle_triangle_points
from .relations import (
    handle_angle_bisector,
    handle_intersect_2d,
    handle_perpendicular_line,
    handle_point_on_object,
    handle_tangent,
)

__all__ = [
    "handle_point_2d",
    "handle_segment",
    "handle_line",
    "handle_circle_center_radius",
    "handle_triangle_points",
    "handle_polygon_points",
    "handle_point_on_object",
    "handle_intersect_2d",
    "handle_tangent",
    "handle_angle_bisector",
    "handle_perpendicular_line",
    "handle_ellipse_equation",
    "handle_parabola_equation",
    "handle_hyperbola_equation",
]
