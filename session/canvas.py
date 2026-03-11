"""
GeoGebra 画布清理逻辑

本模块职责：
1. 统一封装页面清理相关的 JavaScript 操作
2. 提供“清理全部活跃页面”和“清理当前导出页面”的公共能力
3. 将主文件中的清理策略下沉到 session 层，避免继续与导出流程耦合

设计原则：
- manager 层负责提供页面
- page_ops 层负责判断页面是否就绪
- canvas 层负责真正的画布清理与结果汇总
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .page_ops import wait_for_ggb_ready

if TYPE_CHECKING:
    from .manager import GeoGebraSessionManager


# ========== 页面清理内部函数 ==========
def _soft_clear_page(page) -> dict[str, Any]:
    """执行一次基础软清理。

    使用场景：
    - `clear_geogebra_canvas()` 汇总清理全部页面时
    - 只需要快速清空当前构造，不需要复杂重试时

    Args:
        page: Playwright page 对象

    Returns:
        包含 success / message / objectCount 的清理结果字典
    """
    return page.evaluate(
        """
        async () => {
            try {
                if (typeof ggbApplet === 'undefined' || !ggbApplet.evalCommand) {
                    return { success: false, message: "GeoGebra未初始化", objectCount: -1 };
                }

                // 预检查：如果当前没有对象，则直接返回。
                let preCheckCount = 0;
                try {
                    const preObjects = ggbApplet.getAllObjectNames();
                    preCheckCount = preObjects
                        ? preObjects.split(',').filter(name => name.trim()).length
                        : 0;
                    if (preCheckCount === 0) {
                        return { success: true, message: "画布已清空", objectCount: 0 };
                    }
                } catch (e) {
                    console.warn('预检查失败:', e);
                }

                // 执行基础清理。
                ggbApplet.evalCommand('DeleteAll()');
                if (typeof ggbApplet.reset === 'function') {
                    ggbApplet.reset();
                }
                if (ggbApplet.repaintView) {
                    ggbApplet.repaintView();
                }

                // 等待渲染后再验证结果。
                await new Promise(r => setTimeout(r, 500));

                let objectCount = 0;
                try {
                    const allObjects = ggbApplet.getAllObjectNames();
                    objectCount = allObjects
                        ? allObjects.split(',').filter(name => name.trim()).length
                        : 0;
                } catch (e) {
                    objectCount = -1;
                }

                return {
                    success: objectCount === 0,
                    message: objectCount === 0 ? "清除成功" : "清除后仍有残留",
                    objectCount: objectCount
                };
            } catch (e) {
                return { success: false, message: e.message, objectCount: -1 };
            }
        }
        """
    )


def _quick_clear_page(page) -> None:
    """对其他活跃页面执行快速清理。

    使用场景：
    - 当前页面准备导出时，需要先清理其他 2D / 3D 活跃实例
    - 这里不追求完整诊断，只需要尽量减少旧构造干扰

    Args:
        page: 目标 Playwright page 对象
    """
    page.evaluate(
        """
        async () => {
            try {
                if (typeof ggbApplet !== 'undefined' && ggbApplet.evalCommand) {
                    ggbApplet.evalCommand('DeleteAll()');
                    if (typeof ggbApplet.reset === 'function') {
                        ggbApplet.reset();
                    }
                    await new Promise(r => setTimeout(r, 200));
                }
            } catch (e) {
                console.warn('清除其他实例失败:', e);
            }
        }
        """
    )


def _soft_clear_current_page(page, *, mode: str) -> dict[str, Any]:
    """对当前导出页面执行增强型软清理。

    这套逻辑沿用主文件原来的策略：
    1. DeleteAll
    2. 尝试逐个删除残留对象
    3. reset + repaint + updateConstruction
    4. 重置坐标系与显示状态
    5. 验证对象数，并决定是否需要重试

    Args:
        page: 当前导出页面
        mode: 当前导出模式，只能是 2d 或 3d

    Returns:
        包含 success / message / objectCount / needRetry 的结果字典
    """
    return page.evaluate(
        """
        async (mode) => {
            try {
                const normalizedMode = String(mode || '').toLowerCase();

                // 确保 GeoGebra 已加载。
                if (typeof ggbApplet === 'undefined' || !ggbApplet.evalCommand) {
                    return { success: false, message: "GeoGebra未初始化", objectCount: -1, needRetry: false };
                }

                // 预检查：如果画布已经为空，则无需继续清理。
                let preCheckCount = 0;
                try {
                    const preObjects = ggbApplet.getAllObjectNames();
                    preCheckCount = preObjects
                        ? preObjects.split(',').filter(name => name.trim()).length
                        : 0;
                    if (preCheckCount === 0) {
                        console.log("[SUCCESS] 画布已清空，跳过清理");
                        return { success: true, message: "画布已清空", objectCount: 0, needRetry: false };
                    }
                } catch (e) {
                    console.warn('预检查失败:', e);
                }

                // 第一次软清理：优先清掉全部对象，再补一轮逐个删除。
                ggbApplet.evalCommand('DeleteAll()');

                try {
                    const allObjNames = ggbApplet.getAllObjectNames();
                    if (allObjNames) {
                        const objArray = allObjNames.split(',').filter(name => name.trim());
                        for (let i = 0; i < objArray.length; i++) {
                            try {
                                ggbApplet.deleteObject(objArray[i]);
                            } catch (e) {}
                        }
                    }
                } catch (e) {
                    console.warn('逐个删除失败:', e);
                }

                ggbApplet.evalCommand('DeleteAll()');

                if (typeof ggbApplet.reset === 'function') {
                    ggbApplet.reset();
                }
                if (ggbApplet.repaintView) {
                    ggbApplet.repaintView();
                }
                if (ggbApplet.updateConstruction) {
                    ggbApplet.updateConstruction();
                }

                // 按当前模式重置视图状态，避免把 2D 命令误打到 3D 页面。
                try {
                    if (normalizedMode === '2d') {
                        ggbApplet.evalCommand('ShowAxes(true)');
                        ggbApplet.evalCommand('ShowGrid(true)');
                        ggbApplet.evalCommand('SetCoordSystem(-10, 10, -10, 10)');
                    } else if (normalizedMode === '3d') {
                        if (ggbApplet.setStandardView) {
                            ggbApplet.setStandardView();
                        }
                        ggbApplet.evalCommand('SetCoordSystem(-5, 5, -5, 5, -5, 5)');
                    }
                    ggbApplet.evalCommand('ZoomToFit()');
                } catch (e) {
                    console.warn('坐标系重置失败:', e);
                }

                // 仅清理当前模式对应的页面级初始化标记。
                if (
                    normalizedMode === '2d' &&
                    typeof window.__ggb2d_initialized__ !== 'undefined'
                ) {
                    delete window.__ggb2d_initialized__;
                }

                await new Promise(r => setTimeout(r, 800));
                await new Promise(r => setTimeout(r, 300));

                let objectCount = 0;
                try {
                    const allObjects = ggbApplet.getAllObjectNames();
                    objectCount = allObjects
                        ? allObjects.split(',').filter(name => name.trim()).length
                        : 0;
                } catch (e) {
                    console.warn('无法获取对象数量:', e);
                    objectCount = -1;
                }

                console.log(`✅ 第一次软清理完成，剩余对象数：${objectCount}`);
                return {
                    success: objectCount === 0,
                    message: objectCount === 0 ? "软清理成功" : "软清理后仍有残留",
                    objectCount: objectCount,
                    needRetry: objectCount > 0
                };
            } catch (e) {
                console.error("软清理异常:", e);
                return {
                    success: false,
                    message: e.message,
                    objectCount: -1,
                    needRetry: true
                };
            }
        }
        """,
        mode,
    )


def _retry_soft_clear_current_page(page, *, mode: str) -> dict[str, Any]:
    """对当前页面执行第二次软清理重试。

    Args:
        page: 当前导出页面
        mode: 当前导出模式，只能是 2d 或 3d

    Returns:
        包含 success / objectCount 的结果字典
    """
    return page.evaluate(
        """
        async (mode) => {
            try {
                const normalizedMode = String(mode || '').toLowerCase();

                if (typeof ggbApplet === 'undefined' || !ggbApplet.evalCommand) {
                    return { success: false, objectCount: -1 };
                }

                ggbApplet.evalCommand('DeleteAll()');
                if (typeof ggbApplet.reset === 'function') {
                    ggbApplet.reset();
                }
                if (ggbApplet.repaintView) {
                    ggbApplet.repaintView();
                }

                try {
                    if (normalizedMode === '2d') {
                        ggbApplet.evalCommand('ShowAxes(true)');
                        ggbApplet.evalCommand('ShowGrid(true)');
                        ggbApplet.evalCommand('SetCoordSystem(-10, 10, -10, 10)');
                    } else if (normalizedMode === '3d') {
                        if (ggbApplet.setStandardView) {
                            ggbApplet.setStandardView();
                        }
                        ggbApplet.evalCommand('SetCoordSystem(-5, 5, -5, 5, -5, 5)');
                    }
                    ggbApplet.evalCommand('ZoomToFit()');
                } catch (e) {}

                await new Promise(r => setTimeout(r, 800));
                await new Promise(r => setTimeout(r, 300));

                let objectCount = 0;
                try {
                    const allObjects = ggbApplet.getAllObjectNames();
                    objectCount = allObjects
                        ? allObjects.split(',').filter(name => name.trim()).length
                        : 0;
                } catch (e) {
                    objectCount = -1;
                }

                console.log(`✅ 第二次软清理完成，剩余对象数：${objectCount}`);
                return { success: objectCount === 0, objectCount: objectCount };
            } catch (e) {
                return { success: false, objectCount: -1 };
            }
        }
        """,
        mode,
    )


# ========== 对外清理接口 ==========
def clear_geogebra_canvas(session_manager: "GeoGebraSessionManager") -> str:
    """清理所有活跃的 GeoGebra 页面画布。

    Args:
        session_manager: Session 管理器

    Returns:
        汇总后的清理结果字符串
    """
    try:
        results: list[str] = []

        clear_pages = session_manager.list_active_pages()
        if len(clear_pages) == 0:
            return "[INFO] 没有活动的GeoGebra页面实例需要清除"

        for page_name, page in clear_pages:
            try:
                if not wait_for_ggb_ready(page, 2000):
                    results.append(f"[WARNING] {page_name}页面未就绪，跳过清除")
                    continue

                clear_result = _soft_clear_page(page)
                if clear_result.get("success", False):
                    results.append(f"[SUCCESS] {page_name}页面已清除")
                else:
                    results.append(
                        f"[WARNING] {page_name}页面清除："
                        f"{clear_result.get('message', '未知错误')}"
                    )
            except Exception as exc:
                results.append(f"[ERROR] {page_name}页面清除失败：{str(exc)}")

        if len(results) == 0:
            return "[INFO] 没有页面需要清除"
        return "\n".join(results)
    except Exception as exc:
        return f"[ERROR] 清除失败：{str(exc)}"


def clear_other_active_pages(
    session_manager: "GeoGebraSessionManager",
    *,
    current_page,
) -> None:
    """清理除当前页面之外的其他活跃实例。

    这个动作主要用于导出流程，目的是在当前页面导出前先清掉其他实例，
    避免残留构造影响 GeoGebra 全局状态。

    Args:
        session_manager: Session 管理器
        current_page: 当前正在导出的页面
    """
    clear_pages = session_manager.list_active_pages(exclude_page=current_page)

    for page_name, other_page in clear_pages:
        try:
            if wait_for_ggb_ready(other_page, 2000):
                _quick_clear_page(other_page)
                print(f"[SUCCESS] 已清除{page_name}实例的画布")
        except Exception as exc:
            print(f"[WARNING] 清除{page_name}实例时出错: {exc}")


def clear_current_page_with_retry(page, *, mode: str) -> dict[str, Any]:
    """清理当前导出页面，并在必要时自动执行一次重试。

    这里保留主文件原来的清理策略和日志输出方式，确保导出行为尽量稳定。

    Args:
        page: 当前导出页面
        mode: 当前导出模式，只能是 2d 或 3d

    Returns:
        最终清理结果字典
    """
    clear_result = _soft_clear_current_page(page, mode=mode)

    need_retry = clear_result.get("needRetry", False)
    remaining = clear_result.get("objectCount", -1)

    if need_retry and remaining > 0:
        print(f"[WARNING] 第一次清除后仍有 {remaining} 个对象，尝试第二次清除...")
        retry_result = _retry_soft_clear_current_page(page, mode=mode)
        remaining = retry_result.get("objectCount", -1)

        if remaining == 0:
            print("[SUCCESS] 第二次清除成功，画布已完全清空")
        elif remaining > 0:
            print(f"[WARNING] 第二次清除后仍有 {remaining} 个对象，但继续绘制（避免刷新页面）")
        else:
            print("[WARNING] 无法验证清除效果，但继续绘制")

        return {
            "success": remaining == 0,
            "message": "第二次清理完成",
            "objectCount": remaining,
            "needRetry": False,
        }

    if not clear_result.get("success", False):
        print(f"[WARNING] 清除画布警告：{clear_result.get('message', '未知错误')}")
    elif remaining == 0:
        print("[SUCCESS] 画布已完全清除（第一次清除成功）")
    else:
        print(f"[SUCCESS] 画布已清除（剩余对象数：{remaining}）")

    return clear_result
