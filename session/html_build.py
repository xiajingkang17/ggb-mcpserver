"""
GeoGebra 可交互 HTML 构建器

本模块职责：
1. 将 GeoGebra 构造的 Base64 数据转换为可直接打开的交互式 HTML
2. 统一维护导出页面的工具栏、下载按钮、视图重置逻辑
3. 将 HTML 模板从主文件中抽离出来，避免导出层与模板内容耦合

适用场景：
- exporter 层在拿到 ggbBase64 后生成最终 HTML
- 后续如果需要切换导出页面样式或功能，只修改这一处
"""


# ========== 可交互 HTML 构建 ==========
def build_interactive_html(
    ggb_b64: str,
    mode: str,
    title: str = "GeoGebra Interactive",
) -> str:
    """生成可交互的 GeoGebra HTML 页面。

    Args:
        ggb_b64: GeoGebra 构造的 Base64 编码
        mode: "2d" 或 "3d"
        title: HTML 页面标题

    Returns:
        完整的 HTML 字符串
    """
    normalized_mode = str(mode).strip().lower()
    if normalized_mode not in {"2d", "3d"}:
        raise ValueError(f"mode 只能是 2d 或 3d，当前为: {mode}")

    app = "3d" if normalized_mode == "3d" else "geometry"

    # 自定义工具栏：保留常用点、线、圆等工具；3D 下 GeoGebra 会自行补充旋转交互。
    toolbar = "0 1 2 | 3 4 5 | 10 11 | 15 45 46 | 70 72"

    return f"""<!doctype html>
<html><head><meta charset="utf-8">
<title>{title}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://www.geogebra.org/apps/deployggb.js"></script>
<style>
  html,body,#applet_container{{height:100%;margin:0}}
  .topbar{{position:fixed;z-index:5;top:8px;right:calc(3 * 120px + 8px);background:#fff8;padding:6px 10px;border-radius:8px}}
  button{{margin-right:8px}}
</style>
</head>
<body>
<div class="topbar">
  <button onclick="downloadGGB()">导出.GGB</button>
  <button onclick="downloadPNG()">导出PNG</button>
  <button onclick="resetView()">重置视图</button>
</div>
<div id="applet_container"></div>
<script>
  var params = {{
    appName: "{app}",
    width: window.innerWidth, height: window.innerHeight,
    showToolBar: true, showAlgebraInput: true, showMenuBar: false,
    allowStyleBar: true, enableRightClick: true, enableShiftDragZoom: true,
    useBrowserForJS: true, customToolBar: "{toolbar}",
    ggbBase64: "{ggb_b64}"
  }};
  var applet = new GGBApplet(params, true);
  window.addEventListener("load", function() {{
    applet.inject('applet_container');
    setTimeout(function(){{
      if ("{app}" === "geometry" && window.ggbApplet && ggbApplet.setAxesRatio) {{
        // 2D 下保持 1:1 比例，避免圆被压成椭圆。
        ggbApplet.setAxesRatio(1,1);
      }}
    }}, 800);
  }});

  function downloadGGB(){{
    var b64 = ggbApplet.getBase64();
    var a = document.createElement('a');
    a.href = "data:application/octet-stream;base64," + b64;
    a.download = "construction.ggb";
    a.click();
  }}
  function downloadPNG(){{
    var p = ggbApplet.getPNGBase64(1, false, 96);
    var a = document.createElement('a');
    a.href = "data:image/png;base64," + p;
    a.download = "screenshot.png";
    a.click();
  }}
  function resetView(){{
    try {{
      // 1. 重置视图到标准位置，但保留当前构造对象。
      if (ggbApplet.setStandardView) {{
        ggbApplet.setStandardView();
      }}

      // 2. 重置坐标系和显示设置。
      if (ggbApplet.evalCommand) {{
        ggbApplet.evalCommand('ShowAxes(true)');
        ggbApplet.evalCommand('ShowGrid(true)');
        if ("{app}" === "geometry") {{
          ggbApplet.evalCommand('SetCoordSystem(-10, 10, -10, 10)');
          if (ggbApplet.setAxesRatio) {{
            ggbApplet.setAxesRatio(1, 1);
          }}
        }} else if ("{app}" === "3d") {{
          ggbApplet.evalCommand('SetCoordSystem(-5, 5, -5, 5, -5, 5)');
        }}
        ggbApplet.evalCommand('ZoomToFit()');
      }}

      // 3. 刷新视图。
      if (ggbApplet.repaintView) {{
        ggbApplet.repaintView();
      }}
      if (ggbApplet.updateConstruction) {{
        ggbApplet.updateConstruction();
      }}
    }} catch(e) {{
      console.error('重置视图失败:', e);
      alert('重置视图时出错: ' + e.message);
    }}
  }}
  window.addEventListener('resize', ()=>location.reload());
</script>
</body></html>"""
