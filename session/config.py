"""
GeoGebra 浏览器 Session 层配置

本模块职责：
1. 统一维护 GeoGebra 网页版地址
2. 统一维护 Playwright 浏览器启动参数
3. 统一维护页面视口、超时、初始化等待等基础配置

这样做的目的：
- 避免浏览器配置散落在业务代码里
- 后续切换浏览器策略时只需要修改这一处
- 让 manager / page_ops 模块只关注行为，不关注常量定义
"""

# ========== GeoGebra 网页地址 ==========
GEOGEBRA_2D_URL = "https://www.geogebra.org/classic?lang=zh_CN"
GEOGEBRA_3D_URL = "https://www.geogebra.org/3d?lang=zh_CN"


# ========== 页面基础配置 ==========
# 强制使用 1:1 视口，避免圆形被压缩成椭圆。
VIEWPORT_WIDTH = 800
VIEWPORT_HEIGHT = 800

# 页面超时配置。
PAGE_DEFAULT_TIMEOUT_MS = 60000
PAGE_NAVIGATION_TIMEOUT_MS = 60000
BODY_SELECTOR_TIMEOUT_MS = 30000


# ========== GeoGebra 初始化配置 ==========
# 网页刚加载完成后，需要额外等待 GeoGebra Applet 初始化。
APP_BOOTSTRAP_SLEEP_SECONDS = 8

# 为了兼容 GeoGebra 官方页面初始化较慢的情况，保留多次重试机制。
APP_READY_MAX_RETRIES = 8
APP_READY_RETRY_SLEEP_SECONDS = 5


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
