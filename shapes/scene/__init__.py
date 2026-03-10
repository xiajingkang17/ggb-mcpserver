"""
shapes 场景初始化模块导出。

当前统一暴露：
1. initialize_geometry_2d_scene
2. initialize_geometry_3d_scene
3. initialize_function_scene
"""

from .functions import initialize_function_scene
from .geometry_2d import initialize_geometry_2d_scene
from .geometry_3d import initialize_geometry_3d_scene

__all__ = [
    "initialize_geometry_2d_scene",
    "initialize_geometry_3d_scene",
    "initialize_function_scene",
]
