# GeoGebra MCP 交点规则

- 当前 `intersection.pick` 只支持：

```json
{
  "mode": "index",
  "value": 1
}
```

- `value` 从 `1` 开始
- 当前阶段仍然使用 GeoGebra 的 `Intersect[..., index]` 机制
- 如果题目要求“再交于另一点”，需要根据题意选择合适的 `index`
- `objects` 中只能写已存在对象的 `id`
- `intersection` 自身必须显式提供 `id`
- 当前交点选择规则仍然属于实现约束，不应依赖隐式对象命名

## 注意

- 后续如需增强交点选择，将优先扩展 `pick` 语义，而不是继续依赖隐式命名
- 常见题型的标准 steps 组织方式，请查 `ggb://recipe/topic/{topic}`
