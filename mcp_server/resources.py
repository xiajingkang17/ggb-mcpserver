"""
MCP Resource 注册与读取。
"""

from pathlib import Path

from mcp.server.lowlevel.helper_types import ReadResourceContents
from mcp.types import Resource

RESOURCE_ROOT = Path(__file__).resolve().parent.parent / "mcp_knowledge" / "resources"

OVERVIEW_URI = "ggb://catalog/overview"
GGB_COMMANDS_URI = "ggb://rules/ggb-commands"
GGB_COMMANDS_2D_BASIC_URI = "ggb://rules/ggb-commands-2d-basic"
GGB_COMMANDS_2D_CONICS_URI = "ggb://rules/ggb-commands-2d-conics"
GGB_COMMANDS_2D_RELATIONS_URI = "ggb://rules/ggb-commands-2d-relations"
GGB_COMMANDS_FUNCTIONS_URI = "ggb://rules/ggb-commands-functions"
GGB_COMMANDS_SLIDERS_URI = "ggb://rules/ggb-commands-sliders"
GGB_COMMANDS_3D_URI = "ggb://rules/ggb-commands-3d"

FIXED_RESOURCE_FILES = {
    GGB_COMMANDS_URI: RESOURCE_ROOT / "ggb_commands.md",
    GGB_COMMANDS_2D_BASIC_URI: RESOURCE_ROOT / "ggb_commands_2d_basic.md",
    GGB_COMMANDS_2D_CONICS_URI: RESOURCE_ROOT / "ggb_commands_2d_conics.md",
    GGB_COMMANDS_2D_RELATIONS_URI: RESOURCE_ROOT / "ggb_commands_2d_relations.md",
    GGB_COMMANDS_FUNCTIONS_URI: RESOURCE_ROOT / "ggb_commands_functions.md",
    GGB_COMMANDS_SLIDERS_URI: RESOURCE_ROOT / "ggb_commands_sliders.md",
    GGB_COMMANDS_3D_URI: RESOURCE_ROOT / "ggb_commands_3d.md",
}

OVERVIEW_MARKDOWN = """# GeoGebra MCP 总览

## 对外工具

- `clear_canvas_web()`
- `export_interactive_html({ mode, save_dir, commands })`

## 唯一导出协议

公开入参固定为：

```json
{
  "mode": "2d",
  "save_dir": "pic",
  "commands": [
    { "id": "A", "cmd": "A=(0,0)" },
    { "id": "B", "cmd": "B=(4,0)" },
    { "id": "lineAB", "cmd": "lineAB=Line(A,B)" }
  ]
}
```

## 通用规则

- 只允许 `mode`、`save_dir`、`commands`
- `mode` 只能是 `2d` 或 `3d`，必须显式指定
- `commands` 必须是非空数组
- 每一项只允许 `{id, cmd}`
- `cmd` 必须是单条带显式赋值的 GeoGebra 原生命令
- `id` 必须与命令左侧对象名完全一致
- 所有要显示或后续要引用的对象，都必须显式命名
- 不要依赖 GeoGebra 自动命名
- 不要在一条 `cmd` 里拼接多条命令，不要使用分号和换行

## 命令资源

- `ggb://rules/ggb-commands`
- `ggb://rules/ggb-commands-2d-basic`
- `ggb://rules/ggb-commands-2d-conics`
- `ggb://rules/ggb-commands-2d-relations`
- `ggb://rules/ggb-commands-functions`
- `ggb://rules/ggb-commands-sliders`
- `ggb://rules/ggb-commands-3d`

## 建议工作流

1. 先读 `ggb://catalog/overview`
2. 再读 `ggb://rules/ggb-commands`
3. 按题型补读相关子资源
4. 最后调用 `export_interactive_html`
"""


def build_resource_definitions() -> list[Resource]:
    """构建固定 resource 定义。"""
    return [
        Resource(
            name="ggb_overview",
            title="GeoGebra 命令协议总览",
            uri=OVERVIEW_URI,
            description="单轨命令 JSON 协议、命名规则与资源导航",
            mimeType="text/markdown",
        ),
        Resource(
            name="ggb_command_rules",
            title="GeoGebra 原生命令总索引",
            uri=GGB_COMMANDS_URI,
            description="公开入参结构、通用约束、命名规则与命令资源索引",
            mimeType="text/markdown",
        ),
        Resource(
            name="ggb_command_rules_2d_basic",
            title="GeoGebra 2D 基础对象命令",
            uri=GGB_COMMANDS_2D_BASIC_URI,
            description="点、直线、圆、圆弧、2D 路径动点的标准写法",
            mimeType="text/markdown",
        ),
        Resource(
            name="ggb_command_rules_2d_conics",
            title="GeoGebra 2D 圆锥曲线命令",
            uri=GGB_COMMANDS_2D_CONICS_URI,
            description="椭圆、双曲线、抛物线及其依赖对象的标准写法",
            mimeType="text/markdown",
        ),
        Resource(
            name="ggb_command_rules_2d_relations",
            title="GeoGebra 2D 几何关系命令",
            uri=GGB_COMMANDS_2D_RELATIONS_URI,
            description="切线、垂线、角平分线，以及关系点显式命名规则",
            mimeType="text/markdown",
        ),
        Resource(
            name="ggb_command_rules_functions",
            title="GeoGebra 函数命令",
            uri=GGB_COMMANDS_FUNCTIONS_URI,
            description="函数声明的标准写法",
            mimeType="text/markdown",
        ),
        Resource(
            name="ggb_command_rules_sliders",
            title="GeoGebra 滑动条命令",
            uri=GGB_COMMANDS_SLIDERS_URI,
            description="滑动条声明与参数驱动对象的标准写法",
            mimeType="text/markdown",
        ),
        Resource(
            name="ggb_command_rules_3d",
            title="GeoGebra 3D 基础命令",
            uri=GGB_COMMANDS_3D_URI,
            description="三维点、直线、圆柱、圆锥、三维路径动点、三维面上参数动点的标准写法",
            mimeType="text/markdown",
        ),
    ]

def _read_static_markdown(path: Path) -> str:
    """读取静态 markdown 资源。"""
    return path.read_text(encoding="utf-8")


def read_resource_content(uri: str) -> list[ReadResourceContents]:
    """根据 URI 读取资源内容。"""
    if uri == OVERVIEW_URI:
        return [
            ReadResourceContents(
                content=OVERVIEW_MARKDOWN,
                mime_type="text/markdown",
            )
        ]

    static_file = FIXED_RESOURCE_FILES.get(uri)
    if static_file is not None:
        return [
            ReadResourceContents(
                content=_read_static_markdown(static_file),
                mime_type="text/markdown",
            )
        ]

    raise ValueError(f"未知资源 URI：{uri}")
