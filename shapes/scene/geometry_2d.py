"""
2D 几何场景初始化。

本模块职责：
1. 统一初始化 GeoGebra 2D 页面坐标轴、网格和 1:1 比例。
2. 把旧 2D 绘图文件中的场景准备逻辑抽离到 scene 层。
3. 为后续 shapes handler 细拆提供稳定的场景入口。
"""


# ========== 2D 场景初始化 ==========
def initialize_geometry_2d_scene(page) -> None:
    """初始化 2D 几何绘图场景。

    说明：
    这里保持旧实现行为不变，不主动设置具体坐标范围，
    只负责显示坐标轴、网格并固定 1:1 比例。
    """
    page.evaluate(
        """
        () => {
            try {
                if (typeof ggbApplet !== 'undefined') {
                    // 显示坐标轴和网格。
                    ggbApplet.setAxesVisible(true, true);
                    ggbApplet.setGridVisible(true);

                    // 设置 1:1 比例，避免圆形显示成椭圆。
                    ggbApplet.setAxesRatio(1, 1);

                    // 强制重绘，确保页面立即反映初始化设置。
                    ggbApplet.repaintView();

                    window.__ggb2d_initialized__ = true;
                    console.log("GeoGebra 2D 场景初始化完成（1:1比例）");
                }
            } catch (e) {
                console.error('Axis setup error:', e);
            }
        }
        """
    )
