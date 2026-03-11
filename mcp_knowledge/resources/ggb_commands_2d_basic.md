# GeoGebra 命令白名单：2D 基础对象与路径动点

同类对象只推荐下面这一种标准写法。能用白名单就不要改写成别的等价命令。

## 标准写法

- 点：`A=(0,0)`
- 直线：`lineAB=Line(A,B)`
- 圆：`circO=Circle(O,A)`
- 圆弧：`arcBC=CircularArc(O,B,C)`
- 2D 路径动点：`P=Point(path,t)`

## 使用说明

- 已知坐标点优先直接创建，不要改写成后续推导对象
- 如果题目要求显示圆，就显式创建圆对象
- 如果题目要求 2D 弧上动点或路径动点，先创建路径对象，再创建滑动条 `t`，最后写 `P=Point(path,t)`
- `t` 的声明统一读取 `ggb://rules/ggb-commands-sliders`
- 如果题目要求延长线交点，后续求交应引用 `Line(...)`
