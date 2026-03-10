# GeoGebra MCP 弧规则

- `arc` 使用圆心与两个端点定义圆弧
- `arc.kind` 目前支持：
  - `minor`：劣弧
  - `major`：优弧
- 标准弧对象必须先通过 `arc` step 创建，并显式提供 `id`
- `arc` 本身就是公共对象，可以单独显示，不需要额外暴露一个整圆对象
- 当前实现直接走 GeoGebra `CircularArc` 主路径，不再依赖辅助圆对象
- 后续若要在弧上取点，必须在 `point_on.params.object` 中引用弧对象 `id`
- `point_on` 不负责临时构造弧对象，只负责引用已存在的弧对象
- 劣弧 / 优弧只是 `arc.kind` 的取值差异，不应通过对象命名约定表达

## 禁止写法

- 不要依赖隐式弧名
- 不要把原始 GeoGebra 弧表达式直接塞进对象引用
- 不要在 `point_on.object` 中写点、圆心或其他非弧对象来“间接表示弧”
