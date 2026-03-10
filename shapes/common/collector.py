"""
GeoGebra 命令收集与批量执行工具。

本模块职责：
1. 提供公共的 CommandCollector，统一收集 GeoGebra 命令并批量提交。
2. 统一封装 stderr 输出与编码处理，避免各绘图模块重复实现。
3. 作为 shapes 层的公共基础设施，供 2D / 3D / 函数绘图模块复用。
"""

from __future__ import annotations

import sys
import time


# ========== stderr 编码兜底 ==========
# 统一在公共层处理 stderr 编码，避免每个绘图文件重复配置。
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def stderr_print(*args, **kwargs):
    """向 stderr 输出调试信息。

    这里保留容错处理，避免在某些宿主环境下因为标准错误流不可用而中断绘图流程。
    """
    try:
        print(*args, file=sys.stderr, **kwargs)
    except (OSError, ValueError):
        pass


class CommandCollector:
    """命令收集器：收集所有 GeoGebra 命令，然后批量执行。

    设计目的：
    - 减少 Python 与页面之间的通信次数
    - 保持现有批量执行行为不变
    - 作为 shapes 层所有图形 handler 的公共执行器
    """

    def __init__(self):
        self.commands: list[str] = []

    def add(self, command: str):
        """添加命令到队列。"""
        self.commands.append(command)

    def execute_batch(self, page):
        """批量执行所有收集的命令。"""
        if not self.commands:
            return

        # 将所有命令拼接成一个 JavaScript 代码块，一次性发给 GeoGebra 页面执行。
        commands_js = "\n                    ".join(
            [f"ggbApplet.evalCommand('{cmd}');" for cmd in self.commands]
        )

        page.evaluate(
            f"""
            () => {{
                try {{
                    if (typeof ggbApplet !== 'undefined' && ggbApplet.evalCommand) {{
                        {commands_js}

                        // 【统一标签策略】只显示点标签，隐藏非点对象标签。
                        var allObjects = ggbApplet.getAllObjectNames?.();
                        if (allObjects) {{
                            var objects = Array.isArray(allObjects)
                                ? allObjects
                                : String(allObjects)
                                    .split(',')
                                    .map(name => name.trim())
                                    .filter(Boolean);

                            for (var i = 0; i < objects.length; i++) {{
                                var objName = String(objects[i] || '').trim();
                                if (!objName) continue;

                                try {{
                                    var objectType = String(
                                        ggbApplet.getObjectType?.(objName) || ''
                                    ).toLowerCase();
                                    var isPoint = objectType.indexOf('point') !== -1;
                                    ggbApplet.setLabelVisible(objName, isPoint);
                                }} catch (e) {{}}
                            }}
                        }}

                        console.log('批量执行完成：执行了 {len(self.commands)} 条命令');
                    }}
                }} catch (e) {{
                    console.error('批量命令执行错误:', e);
                }}
            }}
            """
        )

        # 保持旧实现中的短暂等待，确保批量命令有时间落到页面中。
        time.sleep(0.1)

        # 执行后立即清空队列，避免后续图形复用旧命令。
        self.commands = []
