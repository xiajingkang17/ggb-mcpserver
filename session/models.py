"""
GeoGebra Session 层共享数据模型。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from playwright.sync_api import Browser, Page

SessionSpace = Literal["2d", "3d"]


@dataclass
class BrowserSlot:
    """表示一个可复用的 GeoGebra 页面槽位。"""

    space: SessionSpace
    instance_name: str
    url: str
    browser: Browser | None = None
    page: Page | None = None


@dataclass
class ExportHtmlResult:
    """表示一次 HTML 导出的结果。"""

    success: bool
    message: str
    output_path: str = ""

    def to_tuple(self) -> tuple[bool, str, str]:
        """转换为 server 层沿用的三元组返回值。"""
        return (self.success, self.message, self.output_path)
