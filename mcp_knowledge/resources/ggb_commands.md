# GeoGebra 原生命令资源索引

## 对外工具

唯一导出工具是 `export_interactive_html`。  
它的公开 MCP 入参直接是：

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

## 字段约束

- 只允许 `mode`、`save_dir`、`commands`
- `mode` 只能是 `2d`、`3d`
- `mode` 必须显式指定，不要依赖自动推断
- `save_dir` 可省略；省略时默认保存到 `pic`，不直接返回 HTML 文本
- `commands` 必须是非空数组
- 每一项只允许 `id` 和 `cmd`

## 命令约束

- `cmd` 必须是单条 GeoGebra 原生命令
- `cmd` 必须带显式赋值
- `id` 必须与命令左侧对象名完全一致
- 不允许换行
- 不允许分号
- 不允许 `DeleteAll`、`RunScript`、`Execute`

正确示例：

```json
{ "id": "A", "cmd": "A=(0,0)" }
{ "id": "circO", "cmd": "circO=Circle(O,A)" }
{ "id": "X", "cmd": "X=Intersect(lineAB,circO,1)" }
```

错误示例：

```json
{ "id": "lineAB", "cmd": "Line(A,B)" }
{ "id": "foo", "cmd": "lineAB=Line(A,B)" }
{ "id": "bad", "cmd": "A=(0,0);B=(1,0)" }
```

## 命名规则

- 所有创建出的对象都必须显式命名，并通过 `id` 暴露
- 题目已经给出名称的对象，优先使用题目名称
- 题目未命名但后续要引用、或需要显示的辅助对象，由模型提供稳定名字
- 不依赖 GeoGebra 自动生成的隐式名字

推荐前缀：

- 直线：`line1`
- 圆：`circ1`
- 圆弧：`arc1`
- 切线：`tan1`
- 垂线：`perp1`
- 角平分线：`bis1`
- 点：优先单个大写字母，例如 `T`、`H`、`X`
- 椭圆：`ellipse1`
- 双曲线：`hyper1`
- 抛物线：`para1`
- 函数：`f`
- 滑动条：`t`

## 关系类补充规则

- `Tangent(...)`、`PerpendicularLine(...)`、`AngleBisector(...)` 这类命令先创建线对象
- 如果题目要求切点、垂足、交点，或后续还要继续引用这些点，再单独追加一个点命令
- 关系点也必须有自己的 `id`
- 未给名时，关系点优先用单个大写字母：切点 `T`，垂足 `H`，一般交点 `X`

示例：

```json
{ "id": "perp1", "cmd": "perp1=PerpendicularLine(C,lineAB)" }
{ "id": "E", "cmd": "E=Intersect(perp1,lineAB,1)" }
{ "id": "tan1", "cmd": "tan1=Tangent(P,circO,1)" }
{ "id": "T", "cmd": "T=Intersect(tan1,circO,1)" }
```

## 主题资源

- `ggb://rules/ggb-commands-2d-basic`
  - 点、直线、圆、圆弧、2D 路径动点
- `ggb://rules/ggb-commands-2d-conics`
  - 椭圆、双曲线、抛物线
- `ggb://rules/ggb-commands-2d-relations`
  - 切线、垂线、角平分线，以及关系点命名
- `ggb://rules/ggb-commands-functions`
  - 函数声明
- `ggb://rules/ggb-commands-sliders`
  - 滑动条声明
- `ggb://rules/ggb-commands-3d`
  - 三维点、三维直线、圆柱、圆锥、三维路径动点、三维面上参数动点

## 使用说明

- 先读本索引，再按题型补读对应主题资源
- 同类对象只使用主题资源中给出的那一种标准写法
- 题目要求显示的对象必须显式创建，不要只创建用于计算的隐含对象
- 2D 路径动点先创建滑动条与路径，再写 `P=Point(path,t)`
- 3D 路径动点先创建滑动条与路径，再写 `P=Point(path,t)`
- 3D 面上参数动点先创建两个滑动条 `u`、`v`，再写 `P=(x(u,v),y(u,v),z(u,v))`
- 题目要求延长线交点时，先创建 `Line(...)`，不要只保留 `Segment(...)`
- 多边形、立方体等复合对象，优先拆成点和线段/棱来表达
