"""
GeoGebra 浏览器 Session 层配置

本模块职责：
1. 统一维护 GeoGebra 页面入口
2. 统一维护 Playwright 浏览器启动参数
3. 统一维护页面视口、超时、初始化等待等基础配置

这样做的目的：
- 避免浏览器配置散落在业务代码里
- 后续切换浏览器策略时只需要修改这一处
- 让 manager / page_ops 模块只关注行为，不关注常量定义
"""

from pathlib import Path


# ========== GeoGebra 页面入口 ==========
# 这里不再直接加载 geogebra.org 的完整产品页，而是加载本地最小壳页。
# 壳页只负责注入 GeoGebra applet，可明显减少站点级 UI 和脚本带来的冷启动开销。
PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEB_SHELL_ROOT = PROJECT_ROOT / "web"

GEOGEBRA_2D_URL = (WEB_SHELL_ROOT / "ggb_2d_shell.html").resolve().as_uri()
GEOGEBRA_3D_URL = (WEB_SHELL_ROOT / "ggb_3d_shell.html").resolve().as_uri()


# ========== 页面基础配置 ==========
# 强制使用 1:1 视口，避免圆形被压缩成椭圆。
VIEWPORT_WIDTH = 800
VIEWPORT_HEIGHT = 800

# 页面超时配置。
PAGE_DEFAULT_TIMEOUT_MS = 60000
PAGE_NAVIGATION_TIMEOUT_MS = 60000
BODY_SELECTOR_TIMEOUT_MS = 30000


# ========== GeoGebra 初始化配置 ==========
# 页面 body 就绪后立即开始主动探测 GeoGebra Applet，不再固定 sleep。
# 这里保留“总次数 + 探测间隔”的方式，兼顾冷启动速度和慢网场景。
APP_READY_MAX_RETRIES = 20
APP_READY_RETRY_SLEEP_SECONDS = 1


# ========== Browser 启动参数 ==========
# 这些参数沿用现有实现，优先保证在无头环境中的稳定性。
BROWSER_ARGS = (
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-web-security",
    "--disable-features=VizDisplayCompositor",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
    "--disable-extensions",
    "--disable-plugins",
    "--disable-default-apps",
    "--disable-sync",
    "--disable-translate",
    "--disable-background-networking",
    "--disable-component-extensions-with-background-pages",
    "--disable-ipc-flooding-protection",
    "--memory-pressure-off",
    "--max_old_space_size=4096",
)
