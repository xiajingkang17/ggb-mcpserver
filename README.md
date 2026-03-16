# GeoGebra MCP Server

GeoGebra MCP Server 是一个面向 MCP 客户端和大模型的 GeoGebra 绘图服务。服务端通过 Playwright 驱动 GeoGebra Web applet，接收统一的 GeoGebra 原生命令 JSON，生成可交互 HTML 文件，并通过 MCP resources / prompt 暴露受控的命令知识。

适用场景：

- 几何题自动出图
- 面向 LLM 的 GeoGebra MCP 工具接入
- 需要把题目描述转成可交互几何图的工作流

## 核心功能

`画布清理`
清理 2D / 3D 画布，减少连续导出时的残留对象干扰。

`交互导出`
基于统一的 `{ mode, save_dir, commands }` 协议执行 GeoGebra 原生命令，导出可交互 HTML。

`2D / 3D 页面复用`
内部维护 2D 与 3D 两个浏览器页面槽位，避免每次导出都重新启动浏览器。

`知识资源驱动`
通过 `ggb://catalog/overview` 与一组 `ggb://rules/...` resources 暴露命令白名单、命名规则和构图约束。

`统一 Prompt`
提供 `unified_geometry` prompt，引导模型先读资源，再生成命令，最后调用导出工具。

`stdio / Streamable HTTP 双入口`
同时支持标准 stdio MCP 与 Streamable HTTP MCP。

## 技术栈

| 类别 | 技术 |
| --- | --- |
| 语言 | Python 3.12+ |
| MCP | `mcp>=1.17.0` |
| 浏览器自动化 | `playwright>=1.40.0` |
| HTTP 服务 | `starlette>=0.37.2`, `uvicorn>=0.30.0` |
| 几何引擎 | GeoGebra Web 2D / 3D |
| LLM 集成 | `langchain`, `langchain-openai`, `langchain-mcp-adapters`（可选） |

## 快速开始

### 环境要求

- Python >= 3.12
- 已安装 Playwright Chromium
- 运行时可访问 GeoGebra 静态资源

### 安装依赖

使用 `uv`：

```bash
uv sync
playwright install chromium
```

使用 `pip`：

```bash
pip install -r requirements.txt
playwright install chromium
```

如需运行 LangChain HTTP 示例，再额外安装：

```bash
pip install -r requirements-langchain.txt
```

### 启动服务

stdio 模式：

```bash
python geogebra_web_api.py
```

HTTP 模式：

```bash
python geogebra_web_api_http.py --host 127.0.0.1 --port 8000
```

默认 MCP endpoint：

```text
http://127.0.0.1:8000/mcp
```

## 常用命令

| 命令 | 说明 |
| --- | --- |
| `python geogebra_web_api.py` | 启动 stdio MCP 服务 |
| `python geogebra_web_api_http.py --host 127.0.0.1 --port 8000` | 启动 Streamable HTTP MCP 服务 |
| `python langchain_http_demo.py --mcp-url http://127.0.0.1:8000/mcp` | 列出 LangChain 可见工具 |
| `python -m py_compile mcp_server/tools.py` | 检查 MCP tool 层 |
| `python -m py_compile mcp_server/resources.py` | 检查 resources 层 |
| `python -m py_compile prompts/prompts_unified.py` | 检查 prompt 层 |
| `python -m py_compile langchain_http_demo.py` | 检查 LangChain 示例 |

## MCP 能力

### Tools

- `clear_canvas_web()`
- `export_interactive_html({ mode, save_dir, commands })`

### Resources

- `ggb://catalog/overview`
- `ggb://rules/ggb-commands`
- `ggb://rules/ggb-commands-2d-basic`
- `ggb://rules/ggb-commands-2d-conics`
- `ggb://rules/ggb-commands-2d-relations`
- `ggb://rules/ggb-commands-functions`
- `ggb://rules/ggb-commands-sliders`
- `ggb://rules/ggb-commands-3d`

### Prompt

- `unified_geometry`

## 导出协议

`export_interactive_html` 的公开入参固定为：

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

### 字段说明

| 字段 | 说明 |
| --- | --- |
| `mode` | 必填，只能是 `2d` 或 `3d` |
| `save_dir` | 可选，HTML 输出目录；省略时默认写到 `pic/` |
| `commands` | 必填，GeoGebra 原生命令数组 |

### 命令约束

- 每条命令都必须是 `{ "id": "...", "cmd": "..." }`
- `cmd` 必须是单条带显式赋值的 GeoGebra 原生命令
- `id` 必须与命令左侧对象名完全一致
- 单条 `cmd` 内不允许分号、换行或多条命令
- 不允许 `DeleteAll`、`RunScript`、`Execute`

正确示例：

```json
[
  { "id": "A", "cmd": "A=(0,0)" },
  { "id": "B", "cmd": "B=(4,0)" },
  { "id": "lineAB", "cmd": "lineAB=Line(A,B)" }
]
```

错误示例：

```json
[
  { "id": "foo", "cmd": "lineAB=Line(A,B)" },
  { "id": "lineAB", "cmd": "Line(A,B)" },
  { "id": "bad", "cmd": "A=(0,0);B=(1,0)" }
]
```

### 返回结果

- 导出成功时返回输出文件路径
- 服务端统一先落盘，不直接返回整份 HTML 文本
- 省略 `save_dir` 时默认输出到 `pic/`

## 推荐使用流程

对接 LLM 时，推荐按以下顺序工作：

1. 读取 `ggb://catalog/overview`
2. 读取 `ggb://rules/ggb-commands`
3. 按题型补读对应子资源
4. 生成满足约束的 `{ mode, save_dir, commands }`
5. 调用 `export_interactive_html`
6. 使用返回的输出路径打开 HTML 文件

## 项目结构

```text
.
├── geogebra_runtime.py        # 运行时装配：session manager、tool handler、server
├── geogebra_web_api.py        # stdio MCP 入口
├── geogebra_web_api_http.py   # Streamable HTTP MCP 入口
├── langchain_http_demo.py     # LangChain HTTP 集成示例
├── mcp_server/
│   ├── __init__.py            # Server 层统一导出
│   ├── app.py                 # MCP server 注册：tools/resources/prompts
│   ├── runner.py              # stdio 运行入口封装
│   ├── http_runner.py         # Streamable HTTP ASGI / uvicorn 封装
│   ├── tools.py               # tool schema、参数校验、调用分发
│   ├── resources.py           # 固定 resources 注册与读取
│   └── prompts.py             # MCP prompt 注册与读取
├── prompts/
│   └── prompts_unified.py     # 统一 prompt 文本
├── session/
│   ├── __init__.py            # Session 层统一导出
│   ├── manager.py             # Playwright 2D / 3D 页面槽位管理
│   ├── config.py              # 浏览器、超时、页面入口配置
│   ├── canvas.py              # 画布清理、跨页面清理
│   ├── page_ops.py            # 页面就绪判断、对象等待、标签策略
│   ├── command_exec.py        # GeoGebra 原生命令批量执行
│   ├── exporter.py            # 导出主流程：清屏、执行命令、生成 HTML
│   ├── html_build.py          # 可交互 HTML 模板构建
│   └── models.py              # Session 层数据模型
├── mcp_knowledge/
│   └── resources/
│       ├── ggb_commands.md                 # 命令总索引
│       ├── ggb_commands_2d_basic.md        # 2D 基础对象与路径动点
│       ├── ggb_commands_2d_conics.md       # 圆锥曲线
│       ├── ggb_commands_2d_relations.md    # 切线、垂线、角平分线
│       ├── ggb_commands_functions.md       # 函数声明
│       ├── ggb_commands_sliders.md         # 滑动条
│       └── ggb_commands_3d.md              # 3D 基础对象与动点
├── web/
│   ├── ggb_2d_shell.html      # 本地 2D 最小 applet 壳页
│   └── ggb_3d_shell.html      # 本地 3D 最小 applet 壳页
├── pic/                       # 默认 HTML 导出目录
├── pyproject.toml             # 项目元信息与依赖
├── requirements.txt           # 基础依赖
└── requirements-langchain.txt # LangChain 示例依赖
```

## 核心模块

### Runtime

`geogebra_runtime.py` 负责把 MCP server、resources、prompt、session manager 和导出处理器组装在一起，并通过锁保证单次导出串行执行。

### Session

`session/` 目录负责浏览器页面复用与 GeoGebra 实际执行：

- `manager.py` 维护 2D / 3D 两个页面槽位
- `config.py` 指向本地最小 GeoGebra 壳页，减少整站 UI 带来的启动开销
- `canvas.py` 负责清理当前页面和其他活跃页面
- `command_exec.py` 只执行原生命令，不做低层图元协议转换
- `exporter.py` 串起清屏、执行命令、等待对象、导出 HTML 的完整流程
- `html_build.py` 生成最终可交互 HTML

### MCP Server

`mcp_server/` 目录负责对外暴露 MCP 能力：

- `tools.py` 负责公开 schema、参数校验和工具调度
- `resources.py` 负责固定 `ggb://...` 资源注册与读取
- `prompts.py` 负责 `unified_geometry` prompt 注册与读取
- `runner.py` 与 `http_runner.py` 分别对应 stdio 与 HTTP 运行方式

### Knowledge / Prompt

- `mcp_knowledge/resources/` 提供命令白名单、命名规则与题型化资源
- `prompts/prompts_unified.py` 约束模型先读资源，再出命令，最后调用工具

## LangChain HTTP 示例

先启动 HTTP MCP 服务：

```bash
python geogebra_web_api_http.py --host 127.0.0.1 --port 8000
```

列出工具：

```bash
python langchain_http_demo.py --mcp-url http://127.0.0.1:8000/mcp
```

直接调用工具：

```powershell
python langchain_http_demo.py `
  --mcp-url http://127.0.0.1:8000/mcp `
  --tool-name export_interactive_html `
  --tool-args-json "{\"mode\":\"2d\",\"save_dir\":\"pic\",\"commands\":[{\"id\":\"A\",\"cmd\":\"A=(0,0)\"},{\"id\":\"B\",\"cmd\":\"B=(4,0)\"},{\"id\":\"lineAB\",\"cmd\":\"lineAB=Line(A,B)\"}]}"
```

使用自然语言驱动 agent：

```powershell
python langchain_http_demo.py `
  --mcp-url http://127.0.0.1:8000/mcp `
  --query "如图，在四棱锥 P−ABCD 中，底面 ABCD 是直角梯形，AB∥CD，∠DAB=90∘，PD⊥ 底面 ABCD。
已知：PD=AD=2，AB=2CD=2。
点 M 是侧棱 PB 上的动点（不与 P,B 重合），设 PBPM​=λ。你必须调用mcptool把这个图通过html格式画出并导出来"
```

说明：

- 示例 agent 可主动读取 MCP resources / prompt
- 若模型未直接调用 `export_interactive_html`，但最终回复中给出了合法的导出 JSON，示例程序会自动补调一次导出

## 环境变量

`langchain_http_demo.py` 会从项目根目录的 `.env` 读取可选配置：

```env
KIMI_API_KEY=your_api_key
KIMI_MODEL=kimi-k2-0905-preview
KIMI_BASE_URL=https://api.moonshot.cn/v1
KIMI_TEMPERATURE=0.2
```

兼容变量：

- `MOONSHOT_API_KEY`

## MCP 客户端配置示例

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

## 数据流

```text
MCP Client / LLM
  -> tools / resources / prompts
  -> mcp_server/*
  -> geogebra_runtime.py
  -> session/*
  -> GeoGebra Web applet
  -> ggb base64
  -> interactive HTML file
```

## 校验

建议在改动后至少运行：

```bash
python -m py_compile geogebra_runtime.py
python -m py_compile geogebra_web_api.py
python -m py_compile geogebra_web_api_http.py
python -m py_compile mcp_server/app.py
python -m py_compile mcp_server/tools.py
python -m py_compile mcp_server/resources.py
python -m py_compile prompts/prompts_unified.py
python -m py_compile session/exporter.py
python -m py_compile langchain_http_demo.py
```

## 注意事项

- 首次运行前需要安装 Playwright Chromium
- 运行时仍需访问 GeoGebra 静态资源
- HTTP 模式下 `save_dir` 写入的是服务端磁盘，不是客户端本地磁盘
- 省略 `save_dir` 时默认输出到 `pic/`
- 当前导出协议只接受 GeoGebra 原生命令 JSON
