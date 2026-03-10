"""
GeoGebra 浏览器 Session 层数据模型

本模块职责：
1. 定义 2D / 3D 页面槽位的数据结构
2. 为 manager 层提供统一的状态承载对象
3. 避免后续继续使用多个分散的全局变量维护浏览器状态
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from playwright.sync_api import Browser, Page


# ========== Session 空间类型 ==========
# 当前只维护 2D 与 3D 两类页面槽位。
SessionSpace = Literal["2d", "3d"]


# ========== 浏览器槽位模型 ==========
@dataclass
class BrowserSlot:
    """表示一个可复用的 GeoGebra 页面槽位。

    每个槽位固定对应一种空间类型：
    - 2d: GeoGebra Classic 页面
    - 3d: GeoGebra 3D 页面

    Args:
        space: 槽位类型，固定为 2d 或 3d
        instance_name: 用于日志输出的实例名称
        url: 该槽位对应的 GeoGebra 官方页面地址
        browser: 当前槽位持有的浏览器实例
        page: 当前槽位持有的页面实例
    """

    space: SessionSpace
    instance_name: str
    url: str
    browser: Browser | None = None
    page: Page | None = None


# ========== HTML 导出请求 / 结果 ==========
@dataclass
class ExportHtmlRequest:
    """表示一次 GeoGebra 可交互 HTML 导出请求。

    说明：
    - draw_type / params 与 steps 二选一
    - mode 允许上层显式指定，也允许由 exporter 自动推断

    Args:
        draw_type: 单个图形类型
        id: 单个图形创建对象的唯一标识
        params: 单个图形参数
        steps: 连续绘制步骤列表
        mode: 导出模式，支持 auto / 2d / 3d
        save_dir: 导出目录路径
    """

    draw_type: str | None = None
    id: str | None = None
    params: dict[str, Any] | None = None
    steps: list[dict[str, Any]] | None = None
    mode: str = "auto"
    save_dir: str | None = None


@dataclass
class ExportHtmlResult:
    """表示一次 GeoGebra 可交互 HTML 导出结果。

    Args:
        success: 是否成功
        message: 返回给上层的说明消息
        html: HTML 内容；当 save_dir 已保存文件时通常为空字符串
    """

    success: bool
    message: str
    html: str = ""

    def to_tuple(self) -> tuple[bool, str, str]:
        """转换为兼容旧接口的三元组返回值。"""
        return (self.success, self.message, self.html)
