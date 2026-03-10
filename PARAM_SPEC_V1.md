# GeoGebra MCP 参数规范草案 v1

## 1. 目标

本规范的目标不是立即替换现有后端实现，而是先定义一套**给 LLM 使用的唯一标准输入格式**。

核心原则：

- LLM 只学习一套参数写法
- 后端负责把这套写法映射到现有 `draw_type + params`
- 避免 LLM 直接依赖隐式对象命名规则
- 避免同一语义出现多种参数写法


## 2. 适用范围

本规范适用于 MCP 工具 `export_interactive_html` 的 `steps` 模式。

标准调用格式：

```json
{
  "mode": "2d",
  "save_dir": "session",
  "steps": [
    {
      "type": "point",
      "id": "A",
      "params": {
        "coords": [0, 4]
      }
    }
  ]
}
```

约束：

- 优先使用 `steps`
- 不建议 LLM 使用 `draw_type + params` 单步模式
- 每个步骤只允许出现 `type`、`id`、`params`


## 3. 统一规则

### 3.1 步骤结构

每一步统一为：

```json
{
  "type": "对象类型",
  "id": "对象唯一标识",
  "params": { ... }
}
```

字段含义：

- `type`：标准对象类型名
- `id`：该步骤创建出的对象名，必须全局唯一
- `params`：该对象的参数

### 3.2 引用规则

- 引用已创建对象时，一律直接使用其 `id`
- 不再让 LLM 猜测隐式对象名，如 `line_AP`、`seg_BC`
- 不再要求 LLM 传入 `{ "name": "A" }` 这种包装结构

示例：

```json
{ "type": "line", "id": "line_ap", "params": { "through": ["A", "P"] } }
```

这里的 `A`、`P` 都是之前步骤里定义的 `id`。

### 3.3 命名规则

建议采用以下命名约定：

- 点：几何题常规大写字母，如 `A`、`B`、`C`、`D`、`O`、`P`
- 非点对象：`lower_snake_case`
- 推荐类型前缀：
  - `seg_bc`
  - `line_ap`
  - `circ_o`
  - `arc_bc_minor`
  - `perp_c_ap`

### 3.4 原始表达式兜底

当标准参数暂时无法描述某对象时，允许使用：

```json
{ "expr": "CircularArc[O, B, C]" }
```

但约束如下：

- `expr` 只能作为兜底方案
- 不能作为常规主路径
- 如果某能力已有标准字段，就禁止混用 `expr`


## 4. 通用参数字段

建议在所有标准类型中优先复用以下字段名：

- `coords`：点坐标
- `endpoints`：线段两个端点
- `through`：直线经过的点，或关系线经过的点
- `center`：圆心、弧心
- `radius`：半径
- `start`：弧起点
- `end`：弧终点
- `kind`：对象类型细分，如 `minor`
- `object`：单个目标对象
- `objects`：多个目标对象
- `target`：关系对象的目标
- `placement`：点在对象上的定位方式
- `pick`：多解选择方式
- `expr`：GeoGebra 原始表达式兜底
- `visible`：是否显示对象
- `label`：是否显示标签


## 5. 标准子结构

### 5.1 placement

用于描述点在某个对象上的位置。

#### 固定位置

```json
{
  "mode": "fixed",
  "value": 0.3
}
```

#### 滑动条控制

```json
{
  "mode": "slider",
  "name": "t_p",
  "min": 0,
  "max": 1,
  "step": 0.001,
  "init": 0.45
}
```

建议：

- 线段、弧、圆、曲线上的点统一使用 `placement`
- `mode` 先支持 `fixed`、`slider`

### 5.2 pick

用于描述交点、切线等多解对象的选取方式。

当前 v1 先只定义最简单形式：

```json
{
  "mode": "index",
  "value": 2
}
```

后续可扩展：

- `exclude`
- `near`
- `far`
- `along_ray`


## 6. 标准对象类型

v1 核心集合统一为 12 个标准 `type`：

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
- `tangent`

说明：

- 这 12 个 `type` 是内部和外部共享的标准对象语言
- `type` 表示“对象是什么”
- 构造方式放到 `params.form` 中表达，而不是写进 `type` 名称里
- `foot`、`extend_to_circle` 这类高阶语义不属于 v1 核心 `type`，应由基础 `type` 组合得到

### 6.1 point

固定点。

```json
{
  "type": "point",
  "id": "A",
  "params": {
    "coords": [0, 4]
  }
}
```

### 6.2 segment

线段。

```json
{
  "type": "segment",
  "id": "seg_bc",
  "params": {
    "endpoints": ["B", "C"]
  }
}
```

### 6.3 line

直线。

```json
{
  "type": "line",
  "id": "line_ap",
  "params": {
    "through": ["A", "P"]
  }
}
```

### 6.4 circle

圆。

```json
{
  "type": "circle",
  "id": "circ_o",
  "params": {
    "form": "center_radius",
    "center": "O",
    "radius": 3.125
  }
}
```

### 6.5 ellipse

椭圆。

```json
{
  "type": "ellipse",
  "id": "ell_o",
  "params": {
    "form": "center_axes",
    "center": "O",
    "a": 4,
    "b": 2
  }
}
```

说明：

- v1 推荐先支持 `form = "center_axes"`
- 后续如需支持焦点式、标准方程式，可继续扩展 `form`

### 6.6 parabola

抛物线。

```json
{
  "type": "parabola",
  "id": "para_vf",
  "params": {
    "form": "vertex_focus",
    "vertex": "V",
    "focus": "F"
  }
}
```

说明：

- v1 推荐先支持 `form = "vertex_focus"`

### 6.7 hyperbola

双曲线。

```json
{
  "type": "hyperbola",
  "id": "hyp_o",
  "params": {
    "form": "center_axes",
    "center": "O",
    "a": 3,
    "b": 2
  }
}
```

说明：

- v1 推荐先支持 `form = "center_axes"`

### 6.8 arc

弧。

```json
{
  "type": "arc",
  "id": "arc_bc_minor",
  "params": {
    "kind": "minor",
    "center": "O",
    "start": "B",
    "end": "C"
  }
}
```

说明：

- `kind` 当前推荐支持：`minor`、`major`
- 如果现阶段后端尚无正式弧对象，可先降级映射到 `expr`

### 6.9 point_on

对象上的点。

```json
{
  "type": "point_on",
  "id": "P",
  "params": {
    "object": "arc_bc_minor",
    "placement": {
      "mode": "slider",
      "name": "t_p",
      "min": 0,
      "max": 1,
      "step": 0.001,
      "init": 0.45
    }
  }
}
```

### 6.10 intersection

两个对象的交点。

```json
{
  "type": "intersection",
  "id": "D",
  "params": {
    "objects": ["line_ap", "seg_bc"],
    "pick": {
      "mode": "index",
      "value": 1
    }
  }
}
```

### 6.11 perpendicular_line

过一点作某对象的垂线。

```json
{
  "type": "perpendicular_line",
  "id": "perp_c_ap",
  "params": {
    "through": "C",
    "target": "line_ap"
  }
}
```

### 6.12 tangent

切线。

```json
{
  "type": "tangent",
  "id": "tan_p",
  "params": {
    "through": "P",
    "target": "circ_o",
    "pick": {
      "mode": "index",
      "value": 1
    }
  }
}
```

## 7. v1 到现有后端的映射表

本节只定义**规范输入**到**当前实现**的兼容映射，不要求立刻改动现有 handler。

| v1 type | 现有 draw_type | 映射说明 |
|---|---|---|
| `point` | `point_2d` | `coords -> point.coordinates` |
| `segment` | `segment` | `endpoints -> point1/point2.name` |
| `line` | `line` | `through -> point1/point2.name` |
| `circle` | `circle_center_radius` | `form=center_radius` 时，`center -> center.name`，`radius -> radius` |
| `ellipse` | `ellipse_equation` | `form=center_axes` 时，`center -> center`，`a -> a`，`b -> b` |
| `parabola` | `parabola_equation` | `form=vertex_focus` 时，`vertex -> vertex`，`focus -> focus` |
| `hyperbola` | `hyperbola_equation` | `form=center_axes` 时，`center -> center`，`a -> a`，`b -> b` |
| `arc` | 无正式类型 | 先转为 `expr`，如 `CircularArc[O, B, C]` |
| `point_on` | `point_on_object` | `object` 直接引用对象名；若对象为弧则可先降级为表达式 |
| `intersection` | `intersect_2d` | `objects -> object1/object2`，`pick.index -> index` |
| `perpendicular_line` | `perpendicular_line` | `through -> point.name`，`target -> line` |
| `tangent` | `tangent` | `through -> point.name`，`target -> conic.name` |

### 7.1 非核心派生语义

以下语义很常见，但不建议放入 v1 核心 `type`：

- `foot`：用 `perpendicular_line + intersection` 组合
- `extend_to_circle`：用 `line + intersection` 组合

这样可以保持 `type` 集合稳定，并让高阶语义留在后续宏层或题型层中。


## 8. normalize 层建议

建议在真正进入现有 registry / shapes 之前，加一层 `normalize`：

1. 校验 `type/id/params` 是否满足 v1 规范
2. 将标准字段映射为当前后端所需字段
3. 将旧格式输入转换为标准 12 个 `type`
4. 为非核心派生语义预留展开能力
5. 生成当前实现所需的对象名与参数结构

建议新增两个阶段：

- `validate_v1_step(step)`
- `normalize_v1_steps(steps)`
- `adapt_legacy_steps(steps)`

推荐职责：

- `validate_v1_step`：只做输入规范校验
- `normalize_v1_steps`：只做标准字段翻译
- `adapt_legacy_steps`：只负责旧 `draw_type` 到标准 `type` 的兼容转换


## 9. 对 LLM 的强约束

当 LLM 按本规范调用时，应遵守以下限制：

- 只使用本规范定义的 `type`
- 只使用 `id` 引用对象
- 不直接使用隐式对象名
- 不混用旧字段名与新字段名
- 非必要不使用 `expr`
- 涉及多解时必须显式给出 `pick`


## 10. 示例：等腰三角形外接圆题

```json
{
  "mode": "2d",
  "save_dir": "session",
  "steps": [
    { "type": "point", "id": "A", "params": { "coords": [0, 4] } },
    { "type": "point", "id": "B", "params": { "coords": [-3, 0] } },
    { "type": "point", "id": "C", "params": { "coords": [3, 0] } },
    { "type": "point", "id": "O", "params": { "coords": [0, 0.875] } },
    { "type": "segment", "id": "seg_bc", "params": { "endpoints": ["B", "C"] } },
    { "type": "circle", "id": "circ_o", "params": { "center": "O", "radius": 3.125 } },
    { "type": "arc", "id": "arc_bc_minor", "params": { "kind": "minor", "center": "O", "start": "B", "end": "C" } },
    {
      "type": "point_on",
      "id": "P",
      "params": {
        "object": "arc_bc_minor",
        "placement": {
          "mode": "slider",
          "name": "t_p",
          "min": 0,
          "max": 1,
          "step": 0.001,
          "init": 0.45
        }
      }
    },
    { "type": "line", "id": "line_ap", "params": { "through": ["A", "P"] } },
    { "type": "intersection", "id": "D", "params": { "objects": ["line_ap", "seg_bc"], "pick": { "mode": "index", "value": 1 } } },
    { "type": "perpendicular_line", "id": "perp_c_ap", "params": { "through": "C", "target": "line_ap" } },
    { "type": "intersection", "id": "E", "params": { "objects": ["line_ap", "perp_c_ap"], "pick": { "mode": "index", "value": 1 } } },
    { "type": "line", "id": "line_be", "params": { "through": ["B", "E"] } },
    { "type": "intersection", "id": "F", "params": { "objects": ["line_be", "circ_o"], "pick": { "mode": "index", "value": 2 } } },
    { "type": "segment", "id": "seg_pf", "params": { "endpoints": ["P", "F"] } },
    { "type": "segment", "id": "seg_cf", "params": { "endpoints": ["C", "F"] } }
  ]
}
```


## 11. 后续建议

建议按以下顺序演进：

1. 先冻结本规范作为 LLM 唯一输入协议
2. 实现 `normalize` 层和 `legacy adapter`
3. 给 12 个标准 `type` 补精确 schema
4. 将 `arc` 变成正式原生能力
5. 再决定是否增加宏层语义，如 `foot`
6. 逐步弱化旧参数风格
