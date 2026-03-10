# 再次交点 recipe

目标：已知某条线与某对象已经有一个已知交点，再求“另一交点”。

## 常见做法

- 先创建线对象，并显式提供 `id`
- 再使用 `intersection`
- `pick.value` 根据题意填写为另一个交点对应的 index

## 标准示例

```json
[
  {
    "type": "line",
    "id": "line_be",
    "params": {
      "through": ["B", "E"]
    }
  },
  {
    "type": "intersection",
    "id": "F",
    "params": {
      "objects": ["line_be", "circ_o"],
      "pick": {
        "mode": "index",
        "value": 2
      }
    }
  }
]
```
