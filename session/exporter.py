"""
GeoGebra 命令 JSON 导出编排。
"""

from __future__ import annotations

import uuid
from pathlib import Path

from .canvas import clear_current_page_with_retry, clear_other_active_pages
from .command_exec import execute_raw_commands
from .html_build import build_interactive_html
from .models import ExportHtmlResult
from .page_ops import apply_label_visibility_policy, wait_for_ggb_ready, wait_for_objects

DEFAULT_EXPORT_DIR = "pic"


def _resolve_output_dir(save_dir: str) -> Path:
    """解析导出目录。相对路径统一按仓库根目录展开。"""
    raw_path = Path(save_dir)
    if raw_path.is_absolute():
        return raw_path

    repo_root = Path(__file__).resolve().parent.parent
    return repo_root / raw_path


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


def _prepare_2d_canvas(page) -> None:
    """在 2D 命令执行前恢复基础坐标轴状态。"""
    page.evaluate(
        """
        () => {
            try {
                if (typeof ggbApplet !== 'undefined') {
                    ggbApplet.setAxesVisible(true, true);
                    ggbApplet.setGridVisible(true);
                    ggbApplet.setAxesRatio(1, 1);
                    window.__ggb2d_initialized__ = true;
                }
            } catch (e) {
                console.error('2D canvas initialization failed', e);
            }
        }
        """
    )


def export_interactive_html(
    *,
    commands: list[dict[str, str]] | None = None,
    mode: str = "",
    save_dir: str | None = None,
    session_manager,
) -> ExportHtmlResult:
    """执行 GeoGebra 原生命令并导出可交互 HTML。"""
    try:
        if not commands:
            return ExportHtmlResult(
                success=False,
                message="错误：必须提供非空 commands 参数",
            )

        if not isinstance(mode, str) or not mode.strip():
            return ExportHtmlResult(
                success=False,
                message="错误：必须显式指定 mode=2d 或 mode=3d",
            )

        effective_mode = mode.strip().lower()
        if effective_mode not in {"2d", "3d"}:
            return ExportHtmlResult(
                success=False,
                message=f"错误：mode 只能是 2d 或 3d，当前为：{mode}",
            )

        page = session_manager.get_page("3d" if effective_mode == "3d" else "2d")

        if not wait_for_ggb_ready(page, 8000):
            return ExportHtmlResult(
                success=False,
                message="导出失败：GeoGebra 未就绪（ggbApplet 不存在）",
            )

        clear_other_active_pages(
            session_manager,
            current_page=page,
        )
        clear_current_page_with_retry(page, mode=effective_mode)

        if effective_mode == "2d":
            _prepare_2d_canvas(page)

        raw_commands = [str(item["cmd"]).strip() for item in commands]
        execute_raw_commands(page, raw_commands)

        _refresh_page(page)
        object_count = wait_for_objects(page, 1, 8000)
        if object_count < 1:
            _refresh_page(page)
            object_count = wait_for_objects(page, 1, 8000)
            if object_count < 1:
                return ExportHtmlResult(
                    success=False,
                    message="导出失败：构造中未生成任何对象",
                )

        apply_label_visibility_policy(page)
        _refresh_page(page)

        ggb_b64 = page.evaluate(
            "() => (ggbApplet.getBase64 ? ggbApplet.getBase64() : null)"
        )
        if not ggb_b64:
            return ExportHtmlResult(
                success=False,
                message="导出失败：当前网页不支持 getBase64()",
            )

        html = build_interactive_html(ggb_b64, mode=effective_mode)

        target_dir = save_dir or DEFAULT_EXPORT_DIR
        out_dir = _resolve_output_dir(target_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        out_path = out_dir / f"ggb_interactive_{uuid.uuid4().hex[:8]}.html"
        out_path.write_text(html, encoding="utf-8")

        default_dir_hint = (
            f"[INFO] 未指定 save_dir，已使用默认导出目录：{DEFAULT_EXPORT_DIR}\n"
            if not save_dir
            else ""
        )
        message = (
            f"[SUCCESS] 可交互 HTML 已保存至：{out_path.as_posix()}\n\n"
            f"{default_dir_hint}"
            f"[INFO] 绘制内容：{len(commands)} 条命令\n"
            f"[INFO] 文件路径：{out_path.absolute()}\n\n"
            "[INFO] 使用方式：\n"
            "1. 双击打开 HTML 文件\n"
            "2. 在浏览器中继续交互、旋转或缩放\n"
            "3. 使用 GeoGebra 自带功能继续编辑或导出"
        )
        return ExportHtmlResult(
            success=True,
            message=message,
            output_path=out_path.as_posix(),
        )
    except Exception as exc:
        return ExportHtmlResult(
            success=False,
            message=f"导出可交互 HTML 失败：{str(exc)}",
        )


def export_interactive_html_sync(
    commands: list[dict[str, str]] | None = None,
    mode: str = "",
    save_dir: str | None = None,
    *,
    session_manager,
) -> tuple[bool, str, str]:
    """供 server 层调用的同步导出入口。"""
    result = export_interactive_html(
        commands=commands,
        mode=mode,
        save_dir=save_dir,
        session_manager=session_manager,
    )
    return result.to_tuple()
