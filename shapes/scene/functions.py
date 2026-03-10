"""
函数绘图场景初始化。

本模块职责：
1. 统一初始化函数绘图页面的坐标系与显示选项。
2. 把旧函数绘图文件中的场景准备逻辑抽离到 scene 层。
3. 为后续函数 shapes handler 细拆提供稳定入口。
"""


# ========== 函数场景初始化 ==========
def initialize_function_scene(page) -> None:
    """初始化函数绘图场景。

    说明：
    这里保持旧实现不变，只在首次进入时设置默认坐标范围、坐标轴和网格。
    """
    page.evaluate(
        """
        () => {
            try {
                if (typeof ggbApplet !== 'undefined' && ggbApplet.evalCommand) {
                    if (!window.__ggbfunction_initialized__) {
                        ggbApplet.evalCommand('SetCoordSystem(-10, 10, -10, 10)');
                        ggbApplet.evalCommand('ShowAxes(true)');
                        ggbApplet.evalCommand('ShowGrid(true)');
                        window.__ggbfunction_initialized__ = true;
                        console.log("GeoGebra 函数绘制场景初始化完成");
                    }
                }
            } catch (e) {
                console.error('Function axis setup error:', e);
            }
        }
        """
    )
