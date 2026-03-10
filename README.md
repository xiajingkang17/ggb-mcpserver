# GeoGebra MCP Server

面向大模型与 MCP 客户端的 GeoGebra 绘图服务，基于官方网页版本 GeoGebra 与 Playwright 构建，提供标准化的 2D / 3D / 函数绘图能力，可将构图结果导出为可交互 HTML，并通过 MCP resources 暴露规则、规范与常见题型 recipe。

## 核心功能

- 标准化绘图协议 -- 统一使用 `type + id + params` 组织公共对象，支持单图形模式与多步骤模式
- 2D 几何构造 -- 支持点、线段、直线、圆、椭圆、抛物线、双曲线、弧、交点、垂线、角平分线、切线等标准能力
- 3D 基础绘图 -- 支持 3D 点、线段、对象上点、球、圆柱、圆锥
- 函数图像绘制 -- 使用单一 `function` 类型，直接通过表达式 `expr` 生成函数图像，可配置滑动条
- 可交互 HTML 导出 -- 将当前 GeoGebra 构图导出为可直接打开的交互式 HTML 文件
- MCP 规则知识库 -- 提供 `overview / rules / spec / recipe` 资源，便于 LLM 先读协议再调用工具
- Prompt 对齐 -- prompt 只定义行为约束，具体协议事实下沉到 resources

## 技术栈

| 类别 | 技术 |
| --- | --- |
| MCP 框架 | `mcp` |
| 浏览器自动化 | `Playwright` |
| 运行时 | Python `>=3.12` |
| 几何前端 | GeoGebra 官方网页 |
| HTML 导出 | 自定义 HTML 模板 + Base64 嵌入 |
| 依赖管理 | `uv` / `pip` |

## 项目结构

```text
geo/
├── geogebra_web_api.py          # MCP 服务入口，装配 registry / session / server
├── pyproject.toml               # 项目依赖与元数据
├── requirements.txt             # pip 安装依赖
├── README.md                    # 项目说明
│
├── drawing_tools/               # 标准绘图工具入口
│   ├── tool_catalog.py          # function / 2D / 3D 工具目录
│   ├── tool_2d.py               # 2D 调度入口
│   ├── tool_3d.py               # 3D 调度入口
│   ├── tool_function.py         # 函数调度入口
│   └── __init__.py
│
├── registry/                    # 工具注册表与输入 schema
│   ├── core.py                  # ToolRegistry 与 MCP 输入 schema 构建
│   ├── models.py                # ToolSpec 等模型
│   └── schemas/                 # function / 2D / 3D 精确 params_schema
│       ├── common.py
│       ├── function.py
│       ├── two_d.py
│       ├── three_d.py
│       └── __init__.py
│
├── mcp_server/                  # MCP server 层
│   ├── app.py                   # 注册 tools / prompts / resources / templates
│   ├── tools.py                 # tool 定义与调用分发
│   ├── prompts.py               # prompt 定义与读取
│   ├── resources.py             # resources / templates 定义与读取
│   ├── runner.py                # stdio MCP 运行入口
│   └── __init__.py
│
├── session/                     # Playwright 与 HTML 导出编排
│   ├── manager.py               # 2D / 3D 页面槽位管理
│   ├── exporter.py              # 导出主流程
│   ├── canvas.py                # 画布清理与实例回收
│   ├── page_ops.py              # GeoGebra ready / object 等待
│   ├── html_build.py            # 交互 HTML 构建
│   ├── models.py                # 导出请求与结果模型
│   └── __init__.py
│
├── shapes/                      # 具体绘图实现
│   ├── common/                  # CommandCollector / ShapeContext
│   ├── geometry_2d/             # 2D 标准 type handlers
│   ├── geometry_3d/             # 3D 标准 type handlers
│   ├── functions/               # 函数 handlers
│   ├── scene/                   # 2D / 3D / function 场景初始化
│   └── __init__.py
│
├── prompts/                     # MCP prompt 文本构建
│   └── prompts_unified.py       # 统一行为规则 prompt
│
├── mcp_knowledge/               # MCP 知识内容
│   ├── resources/               # rules 类 markdown
│   └── recipes/                 # 常见题型 recipe markdown
```

## 架构分层

项目采用分层结构，请求流如下：

```text
MCP Client
   |
   v
MCP Server  -->  Registry  -->  Shapes
   |               |            |
   |               |            +--> GeoGebra 命令生成
   |               |
   |               +--> 标准 type / schema / category
   |
   +--> Session  --> Playwright Page  --> GeoGebra Web
                      |
                      +--> HTML Export
```

- `mcp_server` -- 注册 tools / prompts / resources / templates，对外提供 MCP 能力
- `registry` -- 维护标准 `type`、handler 映射、精确 `params_schema`
- `drawing_tools` -- 汇总标准工具目录与分类调度入口
- `shapes` -- 按标准参数生成 GeoGebra 命令
- `session` -- 管理浏览器页面、画布清理、对象等待和 HTML 导出

## 标准能力集合

### Function

- `function`

### 2D

- `point`
- `segment`
- `line`
- `circle`
- `ellipse`
- `parabola`
- `hyperbola`
- `arc`
- `point_on`
- `intersection`
- `perpendicular_line`
- `angle_bisector`
- `tangent`

### 3D

- `point_3d`
- `segment_3d`
- `point_on_3d`
- `sphere`
- `cylinder`
- `cone`

## 核心协议规则

- 所有公共对象都必须显式提供 `id`
- 单图形模式必须提供：`draw_type + id + params`
- 多步骤模式每一步必须提供：`type + id + params`
- 后续引用对象时，只能引用对象 `id`
- 不允许依赖隐式名字，例如 `line_AP`、`seg_BC`
- 辅助对象使用稳定的派生命名，可按名称继续引用
- 对象引用不再支持原始 GeoGebra 表达式兜底

## MCP 能力概览

### Tools

| 名称 | 说明 |
| --- | --- |
| `export_interactive_html` | 绘制并导出可交互 GeoGebra HTML |
| `clear_canvas_web` | 清空当前 GeoGebra 画布 |

### Prompt

| 名称 | 说明 |
| --- | --- |
| `unified_geometry` | 行为规则 prompt，要求先读取 resources 再调用工具 |

### Resources

#### 固定 resources

- `ggb://catalog/overview`
- `ggb://rules/naming`
- `ggb://rules/references`
- `ggb://rules/arcs`
- `ggb://rules/intersection`

#### 参数化 templates

- `ggb://spec/type/{type}`
- `ggb://recipe/topic/{topic}`

## 快速开始

### 1. 安装依赖

#### 使用 `uv`

```bash
uv sync
playwright install chromium
```

#### 使用 `pip`

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 启动 MCP 服务

```bash
python geogebra_web_api.py
```

默认通过 stdio 方式运行，供 MCP 客户端接入。

### 3. MCP 客户端配置示例

```json
{
  "mcpServers": {
    "geogebra-web": {
      "command": "python",
      "args": ["E:/mcp/geo/geogebra_web_api.py"]
    }
  }
}
```

## 输入示例

### 单图形模式

```json
{
  "draw_type": "function",
  "id": "f",
  "params": {
    "expr": "x^2 - 3*x + 2"
  },
  "save_dir": "pic"
}
```

### 多步骤模式

```json
{
  "mode": "2d",
  "save_dir": "pic",
  "steps": [
    {
      "type": "point",
      "id": "A",
      "params": {
        "coords": [0, 0]
      }
    },
    {
      "type": "point",
      "id": "B",
      "params": {
        "coords": [4, 0]
      }
    },
    {
      "type": "line",
      "id": "line_ab",
      "params": {
        "through": ["A", "B"]
      }
    }
  ]
}
```

### 交点示例

```json
{
  "mode": "2d",
  "save_dir": "pic",
  "steps": [
    {
      "type": "point",
      "id": "A",
      "params": {
        "coords": [0, 0]
      }
    },
    {
      "type": "point",
      "id": "B",
      "params": {
        "coords": [4, 0]
      }
    },
    {
      "type": "point",
      "id": "O",
      "params": {
        "coords": [2, 0]
      }
    },
    {
      "type": "line",
      "id": "line_ab",
      "params": {
        "through": ["A", "B"]
      }
    },
    {
      "type": "circle",
      "id": "circ_o",
      "params": {
        "center": "O",
        "radius": 2
      }
    },
    {
      "type": "intersection",
      "id": "P",
      "params": {
        "objects": ["line_ab", "circ_o"],
        "pick": {
          "mode": "index",
          "value": 1
        }
      }
    }
  ]
}
```

## LLM 调用建议

- 先读 `ggb://catalog/overview`
- 再读 `ggb://rules/naming` 和 `ggb://rules/references`
- 涉及弧时读 `ggb://rules/arcs`
- 涉及交点时读 `ggb://rules/intersection`
- 不确定字段时读 `ggb://spec/type/{type}`
- 遇到常见题型时读 `ggb://recipe/topic/{topic}`
- 默认优先使用 `steps`
- 交点、切线、垂足、对象上点优先使用原生几何关系能力，不优先手算坐标

## 开发与验证

### 语法检查

```bash
python -m py_compile geogebra_web_api.py
```

### 协议一致性检查建议

- 检查 `registry/core.py` 是否仍与 `drawing_tools/tool_catalog.py` 一致
- 检查 `mcp_server/resources.py` 中的固定 resources 与 templates 是否可正常读取
- 修改标准 type 后，同时更新：
  - `drawing_tools/tool_catalog.py`
  - `registry/schemas/`
  - `mcp_server/resources.py`
  - `prompts/prompts_unified.py`

## 注意事项

- 运行时需要访问 GeoGebra 官方网页
- 首次运行前需要安装 Playwright Chromium
- `session/` 目录下的 HTML 文件属于运行产物，不属于协议本身
- 当前没有完善的自动化回归测试，建议结合真实 MCP 调用进行验证

## 致谢

- [GeoGebra](https://www.geogebra.org/)
- [Playwright](https://playwright.dev/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
