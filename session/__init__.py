"""
GeoGebra 浏览器 / Session 层对外导出

负责统一暴露：
1. GeoGebraSessionManager：浏览器与页面生命周期管理
2. wait_for_ggb_ready：等待 GeoGebra 应用就绪
3. wait_for_objects：等待构造对象生成
4. clear_geogebra_canvas：清理全部活跃画布
5. export_interactive_html：执行导出编排
"""

from .canvas import clear_geogebra_canvas
from .exporter import export_interactive_html, export_interactive_html_sync
from .html_build import build_interactive_html
from .manager import GeoGebraSessionManager
from .models import ExportHtmlRequest, ExportHtmlResult
from .page_ops import wait_for_ggb_ready, wait_for_objects

__all__ = [
    "GeoGebraSessionManager",
    "ExportHtmlRequest",
    "ExportHtmlResult",
    "clear_geogebra_canvas",
    "export_interactive_html",
    "export_interactive_html_sync",
    "build_interactive_html",
    "wait_for_ggb_ready",
    "wait_for_objects",
]
