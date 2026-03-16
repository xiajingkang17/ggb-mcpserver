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


_CLEAR_PAGE_SCRIPT = """
async (options) => {
    try {
        const {
            mode = '',
            aggressive = false,
            restoreView = false,
            drop2dInitFlag = false,
            waitMs = 500,
            successMessage = '清除成功',
            residualMessage = '清除后仍有残留',
            invalidMessage = '无法验证清除结果',
            alreadyEmptyMessage = '画布已清空',
        } = options || {};

        const normalizedMode = String(mode || '').toLowerCase();
        const normalizedWaitMs = Number(waitMs);

        // 确保 GeoGebra 已加载。
        if (typeof ggbApplet === 'undefined' || !ggbApplet.evalCommand) {
            return {
                success: false,
                message: 'GeoGebra未初始化',
                objectCount: -1,
                needRetry: false,
                skipped: false,
            };
        }

        // 统一处理 GeoGebra 官方 API 的对象列表返回值。
        const normalizeObjectNames = (rawNames) => {
            if (Array.isArray(rawNames)) {
                return rawNames.map(name => String(name || '').trim()).filter(Boolean);
            }
            return String(rawNames || '')
                .split(',')
                .map(name => name.trim())
                .filter(Boolean);
        };

        // 统一统计当前构造中的对象数量。
        const countObjects = () => {
            const rawNames = ggbApplet.getAllObjectNames?.();
            return normalizeObjectNames(rawNames).length;
        };

        // 优先使用官方 newConstruction() 清空当前构造。
        const clearConstruction = () => {
            if (typeof ggbApplet.newConstruction === 'function') {
                ggbApplet.newConstruction();
            } else {
                ggbApplet.evalCommand('DeleteAll()');
            }
        };

        // 统一刷新视图，兼容不同页面上可用的 API。
        const refreshConstructionView = () => {
            if (typeof ggbApplet.refreshViews === 'function') {
                ggbApplet.refreshViews();
                return;
            }
            if (typeof ggbApplet.repaintView === 'function') {
                ggbApplet.repaintView();
            }
            if (typeof ggbApplet.updateConstruction === 'function') {
                ggbApplet.updateConstruction();
            }
        };

        // 仅在 newConstruction() 后仍有残留时，才退化到逐个删除。
        const deleteResidualObjects = () => {
            const objectNames = normalizeObjectNames(ggbApplet.getAllObjectNames?.());
            for (const objectName of objectNames) {
                try {
                    ggbApplet.deleteObject?.(objectName);
                } catch (error) {}
            }
        };

        // 导出页面需要恢复基础视图状态，避免旧页面状态影响后续绘制。
        const restoreViewState = () => {
            if (!restoreView) {
                return;
            }

            try {
                if (normalizedMode === '2d') {
                    if (typeof ggbApplet.setAxesVisible === 'function') {
                        ggbApplet.setAxesVisible(true, true);
                    } else {
                        ggbApplet.evalCommand('ShowAxes(true)');
                    }

                    if (typeof ggbApplet.setGridVisible === 'function') {
                        ggbApplet.setGridVisible(true);
                    } else {
                        ggbApplet.evalCommand('ShowGrid(true)');
                    }

                    ggbApplet.evalCommand('SetCoordSystem(-10, 10, -10, 10)');
                    ggbApplet.setAxesRatio?.(1, 1);
                } else if (normalizedMode === '3d') {
                    ggbApplet.setStandardView?.();
                    ggbApplet.evalCommand('SetCoordSystem(-5, 5, -5, 5, -5, 5)');
                }

                ggbApplet.evalCommand('ZoomToFit()');
            } catch (error) {
                console.warn('坐标系重置失败:', error);
            }
        };

        // 统一等待 GeoGebra 完成一次构造和视图刷新。
        const sleep = async () => {
            const effectiveWaitMs = Number.isFinite(normalizedWaitMs) && normalizedWaitMs >= 0
                ? normalizedWaitMs
                : 500;
            await new Promise(resolve => setTimeout(resolve, effectiveWaitMs));
        };

        // 预检查：如果画布已经为空，则无需继续清理。
        try {
            if (countObjects() === 0) {
                return {
                    success: true,
                    message: alreadyEmptyMessage,
                    objectCount: 0,
                    needRetry: false,
                    skipped: true,
                };
            }
        } catch (error) {
            console.warn('预检查失败:', error);
        }

        clearConstruction();

        if (aggressive) {
            try {
                if (countObjects() > 0) {
                    deleteResidualObjects();
                    clearConstruction();
                }
            } catch (error) {
                console.warn('逐个删除失败:', error);
            }
        }

        refreshConstructionView();
        restoreViewState();

        // 仅清理当前 2D 页面对应的初始化标记。
        if (
            drop2dInitFlag &&
            normalizedMode === '2d' &&
            typeof window.__ggb2d_initialized__ !== 'undefined'
        ) {
            delete window.__ggb2d_initialized__;
        }

        await sleep();

        let objectCount = 0;
        try {
            objectCount = countObjects();
        } catch (error) {
            console.warn('无法获取对象数量:', error);
            objectCount = -1;
        }

        return {
            success: objectCount === 0,
            message: objectCount === 0
                ? successMessage
                : objectCount < 0
                    ? invalidMessage
                    : residualMessage,
            objectCount: objectCount,
            needRetry: aggressive && objectCount > 0,
            skipped: false,
        };
    } catch (error) {
        return {
            success: false,
            message: error?.message || String(error),
            objectCount: -1,
            needRetry: false,
            skipped: false,
        };
    }
}
"""


# ========== 页面清理内部函数 ==========
def _execute_clear(
    page,
    *,
    mode: str = "",
    aggressive: bool = False,
    restore_view: bool = False,
    drop_2d_init_flag: bool = False,
    wait_ms: int = 500,
    success_message: str = "清除成功",
    residual_message: str = "清除后仍有残留",
    invalid_message: str = "无法验证清除结果",
    already_empty_message: str = "画布已清空",
) -> dict[str, Any]:
    """执行一次统一的页面清理动作。

    设计目标：
    1. 将 GeoGebra API 调用收敛到一个 JS 执行器
    2. 将“是否激进清理 / 是否恢复视图 / 是否需要重试”参数化
    3. 避免多处复制同一套对象计数、清空和校验逻辑

    Args:
        page: 目标 Playwright page 对象
        mode: 当前页面模式，只能是 2d / 3d 或空字符串
        aggressive: 是否在基础清理后追加一次逐对象删除兜底
        restore_view: 是否在清理后恢复当前模式的基础视图状态
        drop_2d_init_flag: 是否清理 2D 页面初始化标记
        wait_ms: 清理后的等待时间
        success_message: 成功时返回的消息
        residual_message: 校验到残留对象时返回的消息
        invalid_message: 无法完成校验时返回的消息
        already_empty_message: 预检查发现画布为空时返回的消息

    Returns:
        包含 success / message / objectCount / needRetry 的结果字典
    """
    return page.evaluate(
        _CLEAR_PAGE_SCRIPT,
        {
            "mode": mode,
            "aggressive": aggressive,
            "restoreView": restore_view,
            "drop2dInitFlag": drop_2d_init_flag,
            "waitMs": wait_ms,
            "successMessage": success_message,
            "residualMessage": residual_message,
            "invalidMessage": invalid_message,
            "alreadyEmptyMessage": already_empty_message,
        },
    )


def _soft_clear_page(page) -> dict[str, Any]:
    """执行一次基础软清理。

    使用场景：
    - `clear_geogebra_canvas()` 汇总清理全部页面时
    - 只需要快速清空当前构造，不需要复杂重试时
    """
    return _execute_clear(page, wait_ms=500)


def _quick_clear_page(page) -> None:
    """对其他活跃页面执行快速清理。

    使用场景：
    - 当前页面准备导出时，需要先清理其他 2D / 3D 活跃实例
    - 这里不追求完整诊断，只需要尽量减少旧构造干扰
    """
    _execute_clear(page, wait_ms=200)


def _soft_clear_current_page(page, *, mode: str) -> dict[str, Any]:
    """对当前导出页面执行增强型软清理。

    核心步骤：
    1. 优先使用 newConstruction 清空当前构造
    2. 仅在必要时退化到逐个删除残留对象
    3. 恢复当前模式的基础视图状态
    4. 验证对象数，并决定是否需要重试

    Args:
        page: 当前导出页面
        mode: 当前导出模式，只能是 2d 或 3d

    Returns:
        包含 success / message / objectCount / needRetry 的结果字典
    """
    return _execute_clear(
        page,
        mode=mode,
        aggressive=True,
        restore_view=True,
        drop_2d_init_flag=True,
        wait_ms=1100,
        success_message="软清理成功",
        residual_message="软清理后仍有残留",
        invalid_message="无法验证软清理结果",
        already_empty_message="画布已清空",
    )


def _retry_soft_clear_current_page(page, *, mode: str) -> dict[str, Any]:
    """对当前页面执行第二次软清理重试。

    使用场景：
    - 第一次导出前软清理仍检测到残留对象时
    - 在不刷新页面的前提下，再执行一次保守的清理校验
    """
    return _execute_clear(
        page,
        mode=mode,
        restore_view=True,
        drop_2d_init_flag=True,
        wait_ms=1100,
        success_message="第二次软清理成功",
        residual_message="第二次软清理后仍有残留",
        invalid_message="无法验证第二次软清理结果",
        already_empty_message="画布已清空",
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
    skipped = clear_result.get("skipped", False)

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
    elif skipped:
        print("[SUCCESS] 画布本来为空，跳过清理")
    elif remaining == 0:
        print("[SUCCESS] 画布已完全清除（第一次清除成功）")
    else:
        print(f"[SUCCESS] 画布已清除（剩余对象数：{remaining}）")

    return clear_result
