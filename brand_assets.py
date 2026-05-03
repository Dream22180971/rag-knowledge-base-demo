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
    <div class="ek-login-brand-en">{PRODUCT_SUITE_NAME}</div>
    <div class="ek-login-brand-cn">{PRODUCT_SUITE_CN}</div>
  </div>
</div>
"""


def login_feature_list_html() -> str:
    """登录页左侧功能亮点列表（图标 + 标题 + 描述）。"""
    features = [
        (
            '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
            "智能问答",
            "基于知识库的精准检索与多轮对话",
        ),
        (
            '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
            "引用溯源",
            "每条回答附带原文出处，可追溯验证",
        ),
        (
            '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>',
            "私有部署",
            "本地运行，数据不出内网，安全可控",
        ),
    ]
    items = []
    for icon, title, desc in features:
        items.append(f"""
<div class="ek-feat-card">
  <div class="ek-feat-icon">{icon}</div>
  <div class="ek-feat-text">
    <div class="ek-feat-title">{title}</div>
    <div class="ek-feat-desc">{desc}</div>
  </div>
</div>""")
    return "\n".join(items)


def logo_img_html(size_px: int = 44) -> str:
    """返回可直接放入 `st.markdown(..., unsafe_allow_html=True)` 的 img 标签。"""
    import urllib.parse

    uri = "data:image/svg+xml;charset=utf-8," + urllib.parse.quote(LOGO_SVG)
    return (
        f'<img src="{uri}" width="{size_px}" height="{size_px}" '
        f'alt="{PRODUCT_SUITE_CN}" style="display:block;border-radius:12px;object-fit:contain;"/>'
    )
