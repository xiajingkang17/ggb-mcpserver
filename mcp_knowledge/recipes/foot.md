# 垂足 recipe

目标：已知点 `C` 和直线 `line_ap`，构造点 `C` 到 `line_ap` 的垂足 `E`。

## 标准步骤

```json
[
  {
    "type": "perpendicular_line",
    "id": "perp_c_ap",
    "params": {
      "through": "C",
      "target": "line_ap"
    }
  },
  {
    "type": "intersection",
    "id": "E",
    "params": {
      "objects": ["perp_c_ap", "line_ap"],
      "pick": {
        "mode": "index",
        "value": 1
      }
    }
  }
]
```
