"""
GeoGebra 浏览器 Session 管理器

本模块职责：
1. 管理 Playwright 的生命周期
2. 分别维护 2D / 3D 两个可复用页面槽位
3. 提供页面获取、失效重建、活跃页面枚举、统一关闭等能力

设计目标：
- 主文件不再直接维护多个浏览器全局变量
- 将页面复用与创建逻辑集中到一个对象中
- 为后续拆分 canvas / exporter 层提供稳定依赖
"""

from __future__ import annotations

import time
from collections.abc import Callable

from playwright.sync_api import sync_playwright

from .config import (
    APP_BOOTSTRAP_SLEEP_SECONDS,
    APP_READY_MAX_RETRIES,
    APP_READY_RETRY_SLEEP_SECONDS,
    BODY_SELECTOR_TIMEOUT_MS,
    BROWSER_ARGS,
    GEOGEBRA_2D_URL,
    GEOGEBRA_3D_URL,
    PAGE_DEFAULT_TIMEOUT_MS,
    PAGE_NAVIGATION_TIMEOUT_MS,
    VIEWPORT_HEIGHT,
    VIEWPORT_WIDTH,
)
from .models import BrowserSlot, SessionSpace
from .page_ops import force_square_container, is_page_alive, probe_ggb_ready


# ========== GeoGebra Session 管理器 ==========
class GeoGebraSessionManager:
    """统一管理 GeoGebra 2D / 3D 浏览器页面。

    当前策略：
    1. 整个进程只维护一个 Playwright 实例
    2. 2D 与 3D 各自维护一个可复用页面槽位
    3. 页面失效时按槽位重建，而不是让主业务层处理细节

    Args:
        geogebra_2d_url: 2D GeoGebra 官方页面地址
        geogebra_3d_url: 3D GeoGebra 官方页面地址
    """

    def __init__(
        self,
        *,
        geogebra_2d_url: str = GEOGEBRA_2D_URL,
        geogebra_3d_url: str = GEOGEBRA_3D_URL,
    ) -> None:
        self._playwright = None
        self._slots: dict[SessionSpace, BrowserSlot] = {
            "2d": BrowserSlot(
                space="2d",
                instance_name="2D",
                url=geogebra_2d_url,
            ),
            "3d": BrowserSlot(
                space="3d",
                instance_name="3D",
                url=geogebra_3d_url,
            ),
        }

    def resolve_space_for_draw_type(
        self,
        draw_type: str,
        *,
        is_3d_tool: Callable[[str], bool],
    ) -> SessionSpace:
        """根据图形类型推断应使用的页面空间。

        Args:
            draw_type: 当前绘图类型
            is_3d_tool: 外部注入的 3D 判断函数

        Returns:
            "2d" 或 "3d"
        """
        return "3d" if is_3d_tool(draw_type) else "2d"

    def get_page_for_draw_type(
        self,
        draw_type: str,
        *,
        is_3d_tool: Callable[[str], bool],
    ):
        """根据图形类型获取可复用页面。

        Args:
            draw_type: 当前绘图类型
            is_3d_tool: 外部注入的 3D 判断函数

        Returns:
            已就绪的 Playwright page 对象
        """
        space = self.resolve_space_for_draw_type(
            draw_type,
            is_3d_tool=is_3d_tool,
        )
        return self.get_page(space)

    def get_page(self, space: SessionSpace):
        """获取指定空间的页面实例，不存在时自动创建。

        Args:
            space: 目标页面空间，2d 或 3d

        Returns:
            已就绪的 Playwright page 对象
        """
        slot = self._slots[space]

        # 先复用现有页面，只有在页面失效时才重建。
        if slot.browser is not None and slot.page is not None:
            if is_page_alive(slot.page):
                return slot.page

            print(f"{slot.instance_name}页面上下文已失效，重新创建浏览器")
            self._reset_slot(slot)

        return self._create_page(slot)

    def list_active_pages(self, exclude_page=None) -> list[tuple[str, object]]:
        """列出当前仍然有效的页面实例。

        Args:
            exclude_page: 可选的排除页面，常用于“清理除当前页之外的其他实例”

        Returns:
            [(实例名, page), ...]
        """
        active_pages: list[tuple[str, object]] = []

        for slot in self._slots.values():
            if slot.page is None:
                continue

            if exclude_page is not None and slot.page is exclude_page:
                continue

            # 这里只返回仍然有效的页面；失效页面由 manager 顺手回收。
            if is_page_alive(slot.page):
                active_pages.append((slot.instance_name, slot.page))
            else:
                print(f"{slot.instance_name}页面已失效，跳过并重置槽位")
                self._reset_slot(slot)

        return active_pages

    def close_all(self) -> None:
        """关闭全部浏览器槽位与 Playwright 实例。"""
        for slot in self._slots.values():
            self._reset_slot(slot)

        if self._playwright is not None:
            try:
                self._playwright.stop()
            except Exception:
                pass
            self._playwright = None

    def _create_page(self, slot: BrowserSlot):
        """创建并初始化一个新的 GeoGebra 页面槽位。

        Args:
            slot: 需要创建页面的槽位对象

        Returns:
            创建完成并尽量初始化好的 Playwright page 对象
        """
        self._ensure_playwright_started()

        browser = self._playwright.chromium.launch(
            headless=True,
            args=list(BROWSER_ARGS),
        )
        page = browser.new_page()

        # 先固定视口，再加载页面，确保 2D 画布比例稳定。
        page.set_viewport_size(
            {
                "width": VIEWPORT_WIDTH,
                "height": VIEWPORT_HEIGHT,
            }
        )
        print(
            f"[视口设置] {slot.instance_name}页面视口已设置为 "
            f"{VIEWPORT_WIDTH}x{VIEWPORT_HEIGHT} (1:1像素比例)"
        )

        page.set_default_timeout(PAGE_DEFAULT_TIMEOUT_MS)
        page.set_default_navigation_timeout(PAGE_NAVIGATION_TIMEOUT_MS)

        print(f"正在加载GeoGebra{slot.instance_name}网页版...")
        page.goto(slot.url, timeout=PAGE_NAVIGATION_TIMEOUT_MS)
        page.wait_for_selector("body", timeout=BODY_SELECTOR_TIMEOUT_MS)

        # 官方网页版通常还需要额外等待 Applet 初始化完成。
        time.sleep(APP_BOOTSTRAP_SLEEP_SECONDS)

        self._wait_until_ready(page, slot.instance_name)

        slot.browser = browser
        slot.page = page
        return page

    def _wait_until_ready(self, page, instance_name: str) -> None:
        """等待 GeoGebra 页面完成初始化。

        Args:
            page: Playwright page 对象
            instance_name: 当前实例名称，仅用于日志输出
        """
        retry_count = 0
        success = False

        while retry_count < APP_READY_MAX_RETRIES and not success:
            try:
                success = probe_ggb_ready(page)
                if success:
                    print(f"GeoGebra{instance_name}网页版加载成功！")

                    # 从 DOM 层面再强制一遍容器尺寸，避免页面样式覆盖视口配置。
                    try:
                        force_square_container(
                            page,
                            VIEWPORT_WIDTH,
                            VIEWPORT_HEIGHT,
                        )
                        print("[CSS强制] GeoGebra画布容器已设置为正方形")
                    except Exception as exc:
                        print(f"[CSS警告] 无法设置画布容器CSS: {exc}")
                    break

                retry_count += 1
                print(f"等待GeoGebra加载... ({retry_count}/{APP_READY_MAX_RETRIES})")
                time.sleep(APP_READY_RETRY_SLEEP_SECONDS)
            except Exception as exc:
                retry_count += 1
                print(f"GeoGebra加载检查失败: {exc}")
                time.sleep(APP_READY_RETRY_SLEEP_SECONDS)

        if not success:
            print(f"警告：GeoGebra{instance_name}网页版可能未完全加载，但继续尝试...")

    def _ensure_playwright_started(self) -> None:
        """确保 Playwright 已启动。"""
        if self._playwright is None:
            self._playwright = sync_playwright().start()

    def _reset_slot(self, slot: BrowserSlot) -> None:
        """关闭并清空一个槽位。

        Args:
            slot: 目标槽位
        """
        if slot.browser is not None:
            try:
                slot.browser.close()
            except Exception:
                pass

        slot.browser = None
        slot.page = None
