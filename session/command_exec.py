"""
GeoGebra 原生命令执行辅助。
"""

from __future__ import annotations

import time


def execute_raw_commands(page, commands: list[str]) -> None:
    """批量执行单行 GeoGebra 原生命令。"""
    if not commands:
        return

    page.evaluate(
        """
        (commands) => {
            if (typeof ggbApplet === 'undefined' || !ggbApplet.evalCommand) {
                return;
            }

            for (const rawCommand of commands) {
                const command = String(rawCommand || '').trim();
                if (!command) continue;
                ggbApplet.evalCommand(command);
            }
        }
        """,
        commands,
    )

    time.sleep(0.1)
