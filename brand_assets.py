"""品牌图形：内联 SVG，便于登录页与侧栏直接嵌入（无需静态服务器）。"""

# 简洁几何标：对话气泡 + 书页，蓝紫渐变（Knowledge Studio）
LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120" fill="none">
<defs>
  <linearGradient id="kg" x1="0" y1="0" x2="120" y2="120" gradientUnits="userSpaceOnUse">
    <stop stop-color="#2563eb"/><stop offset="1" stop-color="#7c3aed"/>
  </linearGradient>
</defs>
<rect width="120" height="120" rx="28" fill="url(#kg)"/>
<path d="M35 38h22c8 0 14 6 14 14v36H48c-7 0-13-6-13-13V38z" fill="white" fill-opacity=".95"/>
<path d="M63 38h22v39c0 7-6 13-13 13H63V52c0-8 6-14 14-14h8" fill="white" fill-opacity=".75"/>
<circle cx="78" cy="72" r="6" fill="#2563eb"/>
</svg>"""

PRODUCT_SUITE_NAME = "Knowledge Studio"
PRODUCT_SUITE_CN = "知识工作台"


def login_brand_visual_html(svg_display_size: int = 80) -> str:
    """登录页专用：直接嵌入 SVG（避免 data URI 在部分环境不显示）。"""
    svg = LOGO_SVG.replace(
        'width="120" height="120"',
        f'width="{svg_display_size}" height="{svg_display_size}"',
    )
    return f"""
<div class="ek-login-brand">
  <div class="ek-login-brand-ring">{svg}</div>
  <div class="ek-login-brand-text">
    <div class="ek-login-brand-cn">{PRODUCT_SUITE_CN}</div>
    <div class="ek-login-brand-en">{PRODUCT_SUITE_NAME}</div>
  </div>
</div>
"""


def logo_img_html(size_px: int = 44) -> str:
    """返回可直接放入 `st.markdown(..., unsafe_allow_html=True)` 的 img 标签。"""
    import urllib.parse

    uri = "data:image/svg+xml;charset=utf-8," + urllib.parse.quote(LOGO_SVG)
    return (
        f'<img src="{uri}" width="{size_px}" height="{size_px}" '
        f'alt="{PRODUCT_SUITE_CN}" style="display:block;border-radius:12px;object-fit:contain;"/>'
    )
