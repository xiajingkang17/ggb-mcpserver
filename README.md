# GeoGebra MCP Server

一个基于 GeoGebra 官方网页版的 MCP (Model Context Protocol) 服务器，支持 2D/3D 几何图形绘制、函数图像绘制和复杂几何题目的连续绘制。通过浏览器自动化技术，将几何题目转换为可交互的 GeoGebra HTML 文件。

## ✨ 核心特性

### 🎯 智能参数处理
- **多格式支持**：自动识别和处理大模型输出的各种参数格式
- **智能转换**：支持 `[x,y,z]`、`{"x":1,"y":2,"z":3}`、`{"name":"A","coordinates":[1,2,3]}` 等多种格式
- **变体参数名**：支持 `center/centre/圆心`、`radius/r/半径` 等不同参数名
- **自动补全**：缺少参数时自动生成合理的默认值

### 🎚️ 动态交互控制
- **自动滑动条**：动点自动创建滑动条，范围智能计算（初始值的 ±3 倍）
- **函数参数控制**：所有函数类型都支持滑动条版本，可实时调整参数观察图像变化
- **精确参数化**：支持定点、动点、自定义滑动条三种模式

### 🚀 性能优化
- **批量命令执行**：采用 CommandCollector 机制，性能提升 60-80%
- **防崩溃机制**：3D 连续绘制时智能截图，避免页面崩溃
- **统一接口**：支持单步绘制和连续绘制两种模式
- **智能画布清除**：多步骤清除机制，确保画布干净

### 🎨 全面图形支持
- **2D 图形**：点、线、圆、三角形、多边形、圆锥曲线等
- **3D 图形**：点、线、球体、圆柱、圆锥、棱锥、棱柱等
- **函数图像**：一次、二次、三次、多项式、三角函数、指数对数函数等
- **复杂图形**：支持多步构造的复杂几何图形

### 📤 可交互 HTML 导出
- **完整功能**：导出的 HTML 包含完整的 GeoGebra 工具栏
- **用户交互**：支持旋转、缩放、添加元素等操作
- **一键导出**：可在 HTML 中导出 .GGB 文件或 PNG 截图

## 🛠️ 安装和使用

### 环境要求
- Python 3.12+
- 网络连接（访问 GeoGebra 官方网页版）
- 浏览器环境（Playwright 自动管理）

### 安装依赖

#### 方式一：使用 pip
```bash
pip install -r requirements.txt
playwright install chromium
```

#### 方式二：使用 uv（推荐）
```bash
uv sync
playwright install chromium
```

### 启动 MCP 服务器
```bash
python geogebra_web_api.py
```

### 配置 MCP 客户端

在 MCP 客户端配置文件中添加：

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

## 📋 可用工具

### 1. `export_interactive_html` - 绘制并导出可交互 HTML

绘制几何图形并导出为可在浏览器中打开的 HTML 文件。

**参数格式（单个图形）：**
```json
{
  "draw_type": "图形类型",
  "params": {
    "参数名": "参数值"
  },
  "mode": "auto",
  "save_dir": "."
}
```

**参数格式（连续绘制）：**
```json
{
  "steps": [
    {
      "type": "图形类型",
      "params": {
        "参数名": "参数值"
      }
    }
  ],
  "mode": "auto",
  "save_dir": "."
}
```

**示例：**
```json
{
  "draw_type": "sphere_center_radius",
  "params": {
    "center": {"name": "O", "coordinates": [0, 0, 0]},
    "radius": 2
  },
  "save_dir": "."
}
```

### 2. `clear_canvas_web` - 清除画布

清空 GeoGebra 画布，准备绘制新图形。

## 🎯 支持的图形类型

### 2D 图形

#### 基础图形
- `point_2d` - 2D 点（固定坐标）
- `point_on_object` - 对象上的点（支持动点/定点/滑动条控制）⭐推荐
- `segment` - 线段（有限长度）
- `line` - 直线（无限延伸，通过两点）
- `circle_center_radius` - 圆（圆心和半径）
- `triangle_points` - 三角形（三点，自动创建所有边）
- `polygon_points` - 多边形（点列，自动创建所有边）

#### 圆锥曲线
- `ellipse_equation` - 椭圆（中心和 a、b 参数）
- `parabola_equation` - 抛物线（顶点和焦点，自动生成准线）
- `hyperbola_equation` - 双曲线（中心和 a、b 参数）

#### 精确几何计算
- `intersect_2d` - 两个几何对象的交点（精确计算）⚠️强制使用
- `tangent` - 切线（从点到圆锥曲线的切线）
- `angle_bisector` - 角平分线（通过三个点）
- `perpendicular_line` - 垂线（过点垂直于给定直线）

### 3D 图形

#### 基础 3D 图形
- `point_3d` - 3D 点
- `segment_3d` - 3D 线段（两个端点）⭐优先使用
- `point_on_segment_3d` - 3D 线段上的点（动点自动创建滑动条）
- `polygon_3d` - 3D 多边形（用于创建底面）

#### 3D 立体图形
- `sphere_center_radius` - 球体（球心和半径）
- `cylinder_radius_height` - 圆柱（底面圆半径和高度）
- `cone_radius_height` - 圆锥（底面圆半径和高度）
- `pyramid_all_vertices` - 棱锥（自动创建所有边）
- `prism_all_vertices` - 棱柱（自动创建所有边）

### 函数图像

#### 基础函数
- `linear_general` - 一次函数（ax + by + c = 0）
- `quadratic_standard` - 二次函数（ax² + bx + c）
- `cubic_standard` - 三次函数（ax³ + bx² + cx + d）
- `polynomial_function` - 多项式函数（通用）

#### 三角函数
- `sin_function` - 正弦函数（A*sin(B*x + C) + D）
- `cos_function` - 余弦函数（A*cos(B*x + C) + D）
- `tan_function` - 正切函数（A*tan(B*x + C) + D）

#### 指数对数函数
- `exponential_function` - 指数函数（a^(x + c) + b）
- `logarithmic_function` - 对数函数（b * log(a, x + c)）

#### 带滑动条的函数版本 🎚️

所有函数类型都提供滑动条版本，参数格式与普通版本相同，函数内部自动创建滑动条：

- `linear_general_slider` - 一次函数（3 个滑动条：a, b, c）
- `quadratic_standard_slider` - 二次函数（3 个滑动条：a, b, c）
- `cubic_standard_slider` - 三次函数（4 个滑动条：a, b, c, d）
- `sin_function_slider` - 正弦函数（4 个滑动条：A, B, C, D）
- `cos_function_slider` - 余弦函数（4 个滑动条：A, B, C, D）
- `tan_function_slider` - 正切函数（4 个滑动条：A, B, C, D）
- `exponential_function_slider` - 指数函数（3 个滑动条：a, b, c）
- `logarithmic_function_slider` - 对数函数（3 个滑动条：a, b, c）

**滑动条特性：**
- 范围自动计算：初始值的 -3 倍到 +3 倍
- 特殊限制：指数/对数函数的底数 > 0，三角函数的频率 ≥ 0
- 步长：默认 0.1，可调整

**使用示例：**
```json
{
  "draw_type": "cubic_standard_slider",
  "params": {
    "a": 1,
    "b": 1,
    "c": 1,
    "d": 1
  }
}
```

## 🔧 智能参数处理

### 支持的输入格式

#### 1. 数组格式
```json
{"point": [1, 2, 3]}
```

#### 2. 字典格式
```json
{"point": {"name": "A", "coordinates": [1, 2, 3]}}
```

#### 3. 直接坐标格式
```json
{"point": {"x": 1, "y": 2, "z": 3}}
```

#### 4. 变体参数名
```json
{"centre": [0, 0, 0], "r": 2}  // 自动识别为 center 和 radius
```

#### 5. 中文参数名
```json
{"圆心": [0, 0, 0], "半径": 2}  // 自动识别中文参数名
```

### 自动转换功能
- **类型转换**：字符串坐标自动转换为数字
- **默认值生成**：缺少参数时自动生成合理默认值
- **格式标准化**：所有输入格式统一转换为标准格式
- **错误处理**：提供清晰的错误信息和修复建议

## 📝 使用示例

### 单步绘制示例

#### 绘制一个球体
```json
{
  "draw_type": "sphere_center_radius",
  "params": {
    "center": {"name": "O", "coordinates": [0, 0, 0]},
    "radius": 2
  },
  "save_dir": "."
}
```

#### 绘制带滑动条的三次函数
```json
{
  "draw_type": "cubic_standard_slider",
  "params": {
    "a": 1,
    "b": -2,
    "c": 0,
    "d": 1
  },
  "save_dir": "."
}
```

### 连续绘制示例

#### 绘制一个直三棱柱
```json
{
  "steps": [
    {
      "type": "point_3d",
      "params": {"point": {"name": "A", "coordinates": [0, 0, 0]}}
    },
    {
      "type": "point_3d",
      "params": {"point": {"name": "B", "coordinates": [2, 0, 0]}}
    },
    {
      "type": "point_3d",
      "params": {"point": {"name": "C", "coordinates": [0, 2, 0]}}
    },
    {
      "type": "prism_all_vertices",
      "params": {
        "base_points": ["A", "B", "C"],
        "height": 2
      }
    }
  ],
  "save_dir": "."
}
```

## 🎨 动态点控制

### 动点自动创建滑动条

当创建对象上的点且不提供 `parameter` 和 `slider` 参数时，系统会自动创建默认滑动条：

- **线段上的点**：范围 0-1，步长 0.01，初始值 0.5
- **圆上的点**：范围 0-1，步长 0.01，初始值 0
- **其他对象**：范围 0-1，步长 0.01，初始值 0.5

**注意**：GeoGebra 的 `Point[Object, parameter]` 命令中，所有对象的 parameter 范围都是 0-1。

### 定点模式

提供 `parameter` 参数（0-1 之间）创建定点：
```json
{
  "type": "point_on_object",
  "params": {
    "point_name": "P",
    "object": "circ_O",
    "parameter": 0.3
  }
}
```

### 自定义滑动条模式

提供 `slider` 参数创建自定义滑动条：
```json
{
  "type": "point_on_object",
  "params": {
    "point_name": "P",
    "object": "circ_O",
    "slider": {
      "name": "angle_P",
      "min": 0,
      "max": 1,
      "step": 0.01,
      "init": 0
    }
  }
}
```

## 🚀 性能优化

### 批量命令执行
- **CommandCollector 机制**：收集所有命令后一次性执行
- **性能提升**：单个图形绘制速度提升 60-80%
- **减少通信**：大幅减少页面通信次数

### 浏览器实例管理
- **复用机制**：2D 和 3D 分别维护独立的浏览器实例
- **自动清理**：智能清理机制，避免资源泄漏
- **内存优化**：避免频繁创建和销毁浏览器实例

### 画布清除优化
- **多步骤清除**：软清除 → 验证 → 重试机制
- **快速响应**：优先使用软清除，避免页面重载
- **智能检测**：自动检测画布状态，跳过已清空的画布

## 🔍 故障排除

### 常见问题

#### 1. 页面崩溃
**原因**：3D 连续绘制时频繁截图导致页面崩溃  
**解决**：使用 `steps` 参数进行连续绘制，系统会自动优化截图时机

#### 2. 参数格式错误
**原因**：大模型输出的参数格式不符合预期  
**解决**：智能参数处理会自动转换各种格式，支持多种变体

#### 3. 滑动条不显示
**原因**：参数格式不正确或滑动条范围设置错误  
**解决**：检查参数格式，确保使用正确的参数名（如 `a`, `b`, `c` 而不是 `slider_a`）

#### 4. 画布清除不彻底
**原因**：画布清除机制可能遇到特殊情况  
**解决**：系统会自动重试清除，如仍有问题可手动调用 `clear_canvas_web`

### 调试技巧
- 使用测试文件验证参数格式
- 检查浏览器控制台错误信息
- 使用 `clear_canvas_web` 重置画布状态
- 查看生成的 HTML 文件中的 GeoGebra 控制台

## 📁 项目结构

```
geo/
├── geogebra_web_api.py          # MCP 服务器主文件
├── tools_2d_new.py               # 2D 图形绘制工具
├── tools_3d_new.py              # 3D 图形绘制工具
├── tools_function_new.py         # 函数图像绘制工具
├── prompts/
│   └── prompts_unified.py       # 统一几何图形 prompt
├── requirements.txt             # Python 依赖列表
├── pyproject.toml               # 项目配置文件
└── README.md                    # 项目说明文档
```

## 🎓 最佳实践

### 1. 交点计算
⚠️ **强制使用 `intersect_2d`**：任何涉及"交点"、"相交"的情况，必须使用 `intersect_2d` 而不是手动计算坐标。

### 2. 对象上的点
⭐ **优先使用 `point_on_object`**：当点需要在某个对象上时，优先使用 `point_on_object` 确保精确性和交互性。

### 3. 连续绘制
- 使用 `steps` 参数进行复杂图形的连续绘制
- 系统会自动优化性能，避免页面崩溃

### 4. 函数参数
- 使用滑动条版本时，参数格式与普通版本相同
- 系统会自动创建滑动条，范围智能计算

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

MIT License

## 🙏 致谢

- [GeoGebra](https://www.geogebra.org/) - 官方团队提供的优秀几何绘图工具
- [Playwright](https://playwright.dev/) - 浏览器自动化框架
- [MCP](https://modelcontextprotocol.io/) - AI 工具集成标准协议

---

**注意**：本服务器需要网络连接访问 GeoGebra 官方网页版。首次使用时会自动下载浏览器依赖。
