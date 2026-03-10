# GeoGebra MCP 引用规则

## 点引用

- 直接引用已存在点：`"A"`
- 或内联补点：

```json
{ "id": "A", "coords": [0, 1] }
```

## 对象引用

- 只允许写已存在对象的 `id`

```json
"line_ab"
```

- 不允许使用原始 GeoGebra 表达式作为对象引用

## 单图形模式

- 结构：

```json
{
  "draw_type": "line",
  "id": "line_ab",
  "params": {
    "through": ["A", "B"]
  }
}
```

## 连续步骤模式

- 结构：

```json
{
  "steps": [
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
