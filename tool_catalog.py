#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GeoGebra 工具目录清单。

职责：
1. 统一维护当前仓库支持的工具名称清单。
2. 同时维护标准 type 与旧 draw_type 的过渡映射。
3. 为 registry、schema、兼容层提供稳定的目录来源。
"""

# ========== 函数工具清单 ==========
FUNCTION_TOOLS = (
    "linear_general",
    "linear_general_slider",
    "quadratic_standard",
    "quadratic_standard_slider",
    "cubic_standard",
    "cubic_standard_slider",
    "polynomial_function",
    "sin_function",
    "sin_function_slider",
    "cos_function",
    "cos_function_slider",
    "tan_function",
    "tan_function_slider",
    "exponential_function",
    "exponential_function_slider",
    "logarithmic_function",
    "logarithmic_function_slider",
)


# ========== 2D 标准工具清单 ==========
# 这 12 个 type 是参数规范 v1 中统一的核心几何语言。
STANDARD_TOOLS_2D = (
    "point",
    "segment",
    "line",
    "circle",
    "ellipse",
    "parabola",
    "hyperbola",
    "arc",
    "point_on",
    "intersection",
    "perpendicular_line",
    "tangent",
)


# ========== 2D 标准 -> 旧实现映射 ==========
# 过渡期内保留旧 draw_type，避免当前 registry / handler 立即失效。
# value 为 None 表示该标准 type 还没有对应旧实现，需要后续补原生 handler。
STANDARD_TO_LEGACY_2D = {
    "point": "point_2d",
    "segment": "segment",
    "line": "line",
    "circle": "circle_center_radius",
    "ellipse": "ellipse_equation",
    "parabola": "parabola_equation",
    "hyperbola": "hyperbola_equation",
    "arc": None,
    "point_on": "point_on_object",
    "intersection": "intersect_2d",
    "perpendicular_line": "perpendicular_line",
    "tangent": "tangent",
}


# ========== 2D 旧版独有工具 ==========
# 这些能力仍然可用，但不属于参数规范 v1 的核心 type。
LEGACY_ONLY_TOOLS_2D = (
    "triangle_points",
    "polygon_points",
    "angle_bisector",
)


# ========== 2D 旧实现工具清单 ==========
# 在 registry 彻底迁移到标准 type 前，运行时仍使用旧 draw_type 清单。
LEGACY_TOOLS_2D = tuple(
    legacy_name
    for legacy_name in (
        *STANDARD_TO_LEGACY_2D.values(),
        *LEGACY_ONLY_TOOLS_2D,
    )
    if legacy_name is not None
)


# ========== 2D 运行时兼容别名 ==========
# 继续保留 TOOLS_2D，避免现有导入点立刻失效。
TOOLS_2D = LEGACY_TOOLS_2D


# ========== 3D 工具清单 ==========
TOOLS_3D = (
    "point_3d",
    "segment_3d",
    "point_on_segment_3d",
    "polygon_3d",
    "sphere_center_radius",
    "cylinder_radius_height",
    "cone_radius_height",
    "pyramid_all_vertices",
    "prism_all_vertices",
)


# ========== 全量工具清单 ==========
# 当前运行时仍保持 函数 -> 2D(旧实现) -> 3D 的顺序。
ALL_TOOLS = FUNCTION_TOOLS + TOOLS_2D + TOOLS_3D


# ========== 标准 2D 视角下的全量清单 ==========
# 供后续 schema / normalize / registry 迁移使用。
ALL_STANDARD_TOOLS = FUNCTION_TOOLS + STANDARD_TOOLS_2D + TOOLS_3D
