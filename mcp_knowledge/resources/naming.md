# GeoGebra MCP 命名规则

- 所有公共对象必须显式提供 `id`
- 单图形模式必须提供：`draw_type + id + params`
- 连续步骤模式每一步必须提供：`type + id + params`
- 后续引用对象时，只能引用对象 `id`
- 不允许依赖隐式名称，例如：
  - `line_AP`
  - `seg_BC`
  - `perp_C_line_AP`
- 所有点对象都视为公共点
- 椭圆与双曲线必须显式提供 `focus_ids`
- 抛物线的 `focus` 本身就是公共点引用，必须显式提供点 `id`
- 非点对象标签统一隐藏，点对象标签统一显示
