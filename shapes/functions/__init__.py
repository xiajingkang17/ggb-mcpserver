"""
函数图像 handler 导出。

当前先暴露第一批基础函数：
1. handle_linear_general
2. handle_quadratic_standard
3. handle_cubic_standard
4. handle_polynomial_function
5. handle_sin_function
6. handle_cos_function
7. handle_tan_function
8. handle_exponential_function
9. handle_logarithmic_function
10. handle_linear_general_slider
11. handle_quadratic_standard_slider
12. handle_cubic_standard_slider
13. handle_sin_function_slider
14. handle_cos_function_slider
15. handle_tan_function_slider
16. handle_exponential_function_slider
17. handle_logarithmic_function_slider
"""

from .advanced import (
    handle_cos_function,
    handle_exponential_function,
    handle_logarithmic_function,
    handle_sin_function,
    handle_tan_function,
)
from .basic import handle_linear_general, handle_quadratic_standard
from .polynomials import handle_cubic_standard, handle_polynomial_function
from .sliders import (
    handle_cubic_standard_slider,
    handle_cos_function_slider,
    handle_exponential_function_slider,
    handle_linear_general_slider,
    handle_logarithmic_function_slider,
    handle_quadratic_standard_slider,
    handle_sin_function_slider,
    handle_tan_function_slider,
)

__all__ = [
    "handle_linear_general",
    "handle_quadratic_standard",
    "handle_cubic_standard",
    "handle_polynomial_function",
    "handle_sin_function",
    "handle_cos_function",
    "handle_tan_function",
    "handle_exponential_function",
    "handle_logarithmic_function",
    "handle_linear_general_slider",
    "handle_quadratic_standard_slider",
    "handle_cubic_standard_slider",
    "handle_sin_function_slider",
    "handle_cos_function_slider",
    "handle_tan_function_slider",
    "handle_exponential_function_slider",
    "handle_logarithmic_function_slider",
]
