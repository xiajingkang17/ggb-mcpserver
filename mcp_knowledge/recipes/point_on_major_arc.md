# 优弧上点 recipe

目标：在圆心为 `O`、端点为 `B` 和 `C` 的优弧上创建动点 `P`。

## 标准步骤

```json
[
  {
    "type": "arc",
    "id": "arc_bc_major",
    "params": {
      "kind": "major",
      "center": "O",
      "start": "B",
      "end": "C"
    }
  },
  {
    "type": "point_on",
    "id": "P",
    "params": {
      "object": "arc_bc_major"
    }
  }
]
```
