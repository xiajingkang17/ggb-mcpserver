"""
GeoGebra 页面级操作

本模块职责：
1. 封装单个 Playwright page 上的通用检测逻辑
2. 封装 GeoGebra Applet 的就绪判断与对象等待逻辑
3. 为 manager / exporter / canvas 等上层模块提供可复用的页面操作函数

注意：
这里不管理浏览器生命周期，只处理“页面已经存在之后”的动作。
"""

from __future__ import annotations


# ========== 页面基础检测 ==========
def is_page_alive(page) -> bool:
    """检测页面上下文是否仍然可用。

    Args:
        page: Playwright page 对象

    Returns:
        页面仍可执行 JavaScript 时返回 True，否则返回 False
    """
    try:
        page.evaluate("() => true")
        return True
    except Exception:
        return False


def probe_ggb_ready(page) -> bool:
    """执行一次 GeoGebra 就绪探测。

    这是一个“单次检测”函数，用于 manager 在初始化阶段做重试。

    Args:
        page: Playwright page 对象

    Returns:
        当前页面存在可用 ggbApplet 时返回 True
    """
    return page.evaluate(
        """
        () => {
            try {
                if (typeof ggbApplet !== 'undefined' && ggbApplet && ggbApplet.evalCommand) {
                    return true;
                }
                if (typeof window.ggbApplet !== 'undefined' && window.ggbApplet) {
                    return true;
                }
                return false;
            } catch (e) {
                return false;
            }
        }
        """
    )


def force_square_container(page, width: int, height: int) -> None:
    """从 DOM 层面强制 GeoGebra 主容器为正方形。

    使用场景：
    - 页面首次初始化成功后
    - 需要确保 2D 画布仍保持 1:1 像素比例时

    Args:
        page: Playwright page 对象
        width: 宽度
        height: 高度
    """
    page.evaluate(
        f"""
        () => {{
            const containers = [
                document.getElementById('ggb-element'),
                document.querySelector('.geogebra'),
                document.querySelector('[data-param-app]'),
                document.body
            ];

            for (const container of containers) {{
                if (container) {{
                    container.style.width = '{width}px';
                    container.style.height = '{height}px';
                    console.log('[CSS强制] 设置容器尺寸为正方形:', container);
                    break;
                }}
            }}
        }}
        """
    )


# ========== GeoGebra 就绪 / 对象等待 ==========
def wait_for_ggb_ready(page, timeout_ms: int = 8000) -> bool:
    """等待 GeoGebra Applet 完全就绪。

    Args:
        page: Playwright page 对象
        timeout_ms: 最长等待时间（毫秒）

    Returns:
        在超时前检测到可用 ggbApplet 时返回 True，否则返回 False
    """
    return page.evaluate(
        f"""
        () => new Promise(async resolve => {{
            const end = Date.now() + {timeout_ms};
            while (Date.now() < end) {{
                try {{
                    if (typeof ggbApplet !== 'undefined' && ggbApplet && ggbApplet.evalCommand) {{
                        resolve(true);
                        return;
                    }}
                }} catch (e) {{}}
                await new Promise(r => setTimeout(r, 120));
            }}
            resolve(false);
        }})
        """
    )


def wait_for_objects(page, min_count: int = 1, timeout_ms: int = 8000) -> int:
    """等待页面中至少生成指定数量的 GeoGebra 对象。

    Args:
        page: Playwright page 对象
        min_count: 最少对象数量
        timeout_ms: 最长等待时间（毫秒）

    Returns:
        等待结束时检测到的对象数量
    """
    return page.evaluate(
        f"""
        () => new Promise(async resolve => {{
            function count() {{
                try {{
                    const allNames = ggbApplet.getAllObjectNames?.();
                    if (Array.isArray(allNames)) {{
                        return allNames.length;
                    }}
                    return String(allNames || '')
                        .split(',')
                        .filter(name => name.trim())
                        .length;
                }} catch (e) {{
                    return 0;
                }}
            }}

            const end = Date.now() + {timeout_ms};
            while (Date.now() < end) {{
                if (typeof ggbApplet !== 'undefined' && ggbApplet && ggbApplet.evalCommand) {{
                    const objectCount = count();
                    if (objectCount >= {min_count}) {{
                        resolve(objectCount);
                        return;
                    }}
                }}
                await new Promise(r => setTimeout(r, 120));
            }}

            resolve(count());
        }})
        """
    )
