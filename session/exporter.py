"""
GeoGebra 可交互 HTML 导出编排

本模块职责：
1. 统一串联页面获取、页面清理、绘图执行、对象等待、HTML 生成与文件保存
2. 将主文件中的导出流程下沉到 session 层
3. 通过回调方式复用主文件中的绘图函数，避免与 shapes 层产生循环依赖

说明：
这里仍然不负责图形类型注册与具体绘图分发。
导出层只做“流程编排”，HTML 构建统一下沉到 html_build 模块。
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .canvas import clear_current_page_with_retry, clear_other_active_pages
from .html_build import build_interactive_html
from .models import ExportHtmlRequest, ExportHtmlResult
from .page_ops import wait_for_ggb_ready, wait_for_objects


# ========== 页面刷新辅助函数 ==========
def _refresh_page(page) -> None:
    """强制刷新当前 GeoGebra 构造。"""
    page.evaluate(
        """
        () => {
            try {
                ggbApplet.updateConstruction?.();
                ggbApplet.repaintView?.();
            } catch (e) {}
        }
        """
    )


def _prepare_sequence_canvas(page) -> None:
    """为连续绘制模式准备基础坐标轴状态。

    使用场景：
    - `steps` 连续绘制模式
    - 当前页面已经完成清理，接下来准备依次执行多步绘图
    """
    page.evaluate(
        """
        () => {
            try {
                if (typeof ggbApplet !== 'undefined') {
                    ggbApplet.setAxesVisible(true, true);
                    ggbApplet.setGridVisible(true);
                    ggbApplet.setAxesRatio(1, 1);
                    window.__ggb2d_initialized__ = true;
                    console.log("连续绘制HTML导出：坐标轴已设置");
                }
            } catch (e) {
                console.error('坐标轴设置失败:', e);
            }
        }
        """
    )


# ========== 导出主流程 ==========
def export_interactive_html(
    request: ExportHtmlRequest,
    *,
    session_manager,
    draw_shape: Callable[[str, dict[str, Any], Any, bool], None],
    is_3d_tool: Callable[[str], bool],
) -> ExportHtmlResult:
    """执行一次可交互 HTML 导出。

    Args:
        request: 导出请求对象
        session_manager: Session 管理器
        draw_shape: 绘图回调，签名为 (draw_type, params, page, skip_coord_init)
        is_3d_tool: 判断图形类型是否属于 3D 的回调

    Returns:
        导出结果对象
    """
    try:
        steps = request.steps
        params = request.params or {}
        mode = request.mode
        is_sequence = steps is not None and len(steps) > 0

        if not is_sequence and (not request.draw_type or not params):
            return ExportHtmlResult(
                success=False,
                message="错误：必须提供 'draw_type'+'params' 或 'steps' 参数",
            )

        # 0) 获取页面，并等待 GeoGebra Applet 就绪。
        if is_sequence:
            first_type = steps[0].get("type")
            if not first_type:
                return ExportHtmlResult(False, "错误：steps[0] 缺少 type 参数")
            page = session_manager.get_page_for_draw_type(
                first_type,
                is_3d_tool=is_3d_tool,
            )
        else:
            first_type = request.draw_type
            page = session_manager.get_page_for_draw_type(
                request.draw_type,
                is_3d_tool=is_3d_tool,
            )

        if not wait_for_ggb_ready(page, 8000):
            return ExportHtmlResult(
                success=False,
                message="导出失败：GeoGebra 未就绪（ggbApplet 不存在）",
            )

        # 1) 先清理其他活跃实例，再清理当前导出页面。
        clear_other_active_pages(
            session_manager,
            current_page=page,
        )
        clear_current_page_with_retry(page)

        # 2) 执行绘制逻辑。
        if is_sequence:
            _prepare_sequence_canvas(page)

            for index, step in enumerate(steps):
                step_type = step.get("type")
                step_params = step.get("params", {})

                if not step_type:
                    raise Exception(f"步骤 {index + 1} 缺少 type 参数")

                draw_shape(
                    step_type,
                    step_params,
                    page,
                    True,
                )

                # 步骤之间保留极短暂停顿，保证命令发送顺序稳定。
                if index < len(steps) - 1:
                    time.sleep(0.1)

            if mode == "auto":
                mode = "3d" if is_3d_tool(first_type) else "2d"
        else:
            draw_shape(
                request.draw_type,
                params,
                page,
                False,
            )

            if mode == "auto":
                mode = "3d" if is_3d_tool(request.draw_type) else "2d"

        # 3) 强制刷新并等待对象真正出现在构造中。
        _refresh_page(page)
        object_count = wait_for_objects(page, 1, 8000)

        if object_count < 1:
            _refresh_page(page)
            object_count = wait_for_objects(page, 1, 8000)
            if object_count < 1:
                return ExportHtmlResult(
                    success=False,
                    message="导出失败：构造尚未生成任何对象",
                )

        # 4) 导出当前构造为 Base64，再交由 html_build 模块生成交互页面。
        ggb_b64 = page.evaluate(
            "() => (ggbApplet.getBase64 ? ggbApplet.getBase64() : null)"
        )
        if not ggb_b64:
            return ExportHtmlResult(
                success=False,
                message="导出失败：当前网页不支持 getBase64()",
            )

        html = build_interactive_html(ggb_b64, mode=mode)

        # 5) 根据是否提供保存目录，决定写文件还是直接返回 HTML 内容。
        if request.save_dir:
            out_dir = Path(request.save_dir)
            out_dir.mkdir(parents=True, exist_ok=True)

            out_path = out_dir / f"ggb_interactive_{uuid.uuid4().hex[:8]}.html"
            out_path.write_text(html, encoding="utf-8")

            step_info = (
                f"{len(steps)} 个步骤"
                if is_sequence
                else f"图形 {request.draw_type}"
            )
            message = (
                f"[SUCCESS] 可交互HTML已保存至：{out_path.as_posix()}\n\n"
                f"[INFO] 绘制内容：{step_info}\n"
                f"[INFO] 文件路径：{out_path.absolute()}\n\n"
                "[INFO] 使用方式：\n"
                "1. 双击打开文件在浏览器中查看\n"
                "2. 在浏览器中旋转、缩放、添加元素\n"
                "3. 使用顶部按钮导出.GGB文件或PNG截图\n"
                "4. 可以继续添加点、线、圆等几何元素"
            )
            return ExportHtmlResult(True, message, "")

        return ExportHtmlResult(
            success=True,
            message="[WARNING] 未指定保存目录，返回HTML内容。建议提供 save_dir 参数以保存为文件。",
            html=html,
        )
    except Exception as exc:
        return ExportHtmlResult(
            success=False,
            message=f"导出可交互HTML失败：{str(exc)}",
        )


# ========== 对外同步导出入口 ==========
def export_interactive_html_sync(
    draw_type=None,
    params=None,
    steps=None,
    mode: str = "auto",
    save_dir=None,
    *,
    session_manager,
    draw_shape: Callable[[str, dict[str, Any], Any, bool], None],
    is_3d_tool: Callable[[str], bool],
) -> tuple[bool, str, str]:
    """同步执行绘制并导出可交互 HTML。

    这个函数是给 server 层直接调用的薄编排入口。
    它负责把零散参数整理成 ExportHtmlRequest，
    再调用 session/exporter.py 中的主导出流程。

    Args:
        draw_type: 单个图形类型
        params: 单个图形参数
        steps: 连续绘制步骤列表
        mode: 导出模式，支持 auto / 2d / 3d
        save_dir: HTML 保存目录
        session_manager: Session 管理器
        draw_shape: 绘图回调
        is_3d_tool: 3D 图形判断回调

    Returns:
        (success, message, html) 三元组
    """
    request = ExportHtmlRequest(
        draw_type=draw_type,
        params=params,
        steps=steps,
        mode=mode,
        save_dir=save_dir,
    )
    result = export_interactive_html(
        request,
        session_manager=session_manager,
        draw_shape=draw_shape,
        is_3d_tool=is_3d_tool,
    )
    return result.to_tuple()
