"""
3D 几何场景初始化。

本模块职责：
1. 统一初始化 GeoGebra 3D 页面显示选项。
2. 把旧 3D 绘图文件中的视图准备逻辑抽离到 scene 层。
3. 为后续 3D shapes handler 细拆提供稳定入口。
"""


# ========== 3D 场景初始化 ==========
def initialize_geometry_3d_scene(page) -> None:
    """初始化 3D 几何绘图场景。

    说明：
    这里沿用旧实现策略，只在首次进入时设置坐标轴和网格显示，
    不额外改动当前 3D 视图的相机状态。
    """
    page.evaluate(
        """
        () => {
            try {
                if (typeof ggbApplet !== 'undefined' && ggbApplet.evalCommand) {
                    if (!window.__ggb3d_initialized__) {
                        // 3D 视图已经由页面提供，这里只补显示选项。
                        ggbApplet.evalCommand('ShowAxes(true)');
                        ggbApplet.evalCommand('ShowGrid(true)');
                        window.__ggb3d_initialized__ = true;
                        console.log("GeoGebra 3D 场景初始化完成");
                    }
                }
            } catch (e) {
                console.error('3D View setup error:', e);
            }
        }
        """
    )
