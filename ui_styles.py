"""浅色企业工作台视觉（参考 DocMind 信息层级，非暗黑主题）。"""

import html
from typing import List, Tuple

import streamlit as st

# 中文 + 拉丁混排（登录页与主应用共用，失败时回退到系统字体）
ENTERPRISE_FONT_LINK = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Noto+Sans+SC:wght@400;500;600;700&display=swap" rel="stylesheet">
"""

ENTERPRISE_FONT_FACE_CSS = """
  html, body, .stApp,
  button, input, textarea, select,
  [data-testid="stMarkdownContainer"] {
    font-family: "IBM Plex Sans", "Noto Sans SC", "PingFang SC", "Hiragino Sans GB",
      "Microsoft YaHei", ui-sans-serif, system-ui, sans-serif !important;
    font-feature-settings: "kern" 1, "liga" 1;
  }
  .ek-hero-title, .ek-login-brand-cn, .ek-sidebar-product {
    font-weight: 700;
    letter-spacing: -0.02em;
  }
  .ek-login-brand-en, .ek-sidebar-brand {
    letter-spacing: 0.12em;
  }
"""


# 深色模式：在浅色样式之上追加覆盖（减少重复维护）
DARK_THEME_EXTRA = """
<style>
  .stApp {
    background: linear-gradient(180deg, #0b1220 0%, #0f172a 40%, #111827 100%) !important;
  }
  header[data-testid="stHeader"] {
    background: rgba(15, 23, 42, 0.92) !important;
    border-bottom: 1px solid #1e293b !important;
  }
  section[data-testid="stMain"] {
    padding-top: 0.25rem !important;
  }
  section.main .block-container,
  section.main .stMarkdown,
  section.main p, section.main span,
  section.main .stCaption {
    color: #e2e8f0 !important;
  }
  section.main h1, section.main h2, section.main h3 {
    color: #f8fafc !important;
  }
  [data-testid="stSidebar"] {
    background: linear-gradient(195deg, #0f172a 0%, #111827 100%) !important;
    border-right: 1px solid #1e293b !important;
    box-shadow: 4px 0 32px rgba(0,0,0,0.35) !important;
  }
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] span,
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] .stMarkdown {
    color: #cbd5e1 !important;
  }
  [data-testid="stSidebar"] .stCaption {
    color: #94a3b8 !important;
  }
  [data-testid="stSidebar"] hr {
    border-color: #334155 !important;
  }
  [data-testid="stSidebar"] [data-baseweb="textarea"],
  [data-testid="stSidebar"] input {
    background-color: #1e293b !important;
    color: #f1f5f9 !important;
    border-color: #334155 !important;
  }
  /* 侧栏：租户/下拉与 primary 与整体融合 */
  [data-testid="stSidebar"] [data-baseweb="select"] > div,
  [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div {
    background-color: #1e293b !important;
    border-color: #334155 !important;
    color: #e2e8f0 !important;
  }
  [data-testid="stSidebar"] [data-baseweb="select"] svg {
    fill: #94a3b8 !important;
  }
  [data-testid="stSidebar"] button[kind="primary"] {
    background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
    color: #f8fafc !important;
    box-shadow: 0 4px 16px rgba(79, 70, 229, 0.22) !important;
  }
  [data-testid="stSidebar"] button[kind="primary"] *,
  [data-testid="stSidebar"] [data-testid^="stBaseButton-primary"] * {
    color: #f8fafc !important;
  }
  [data-testid="stSidebar"] button[kind="secondary"] {
    background: #1e293b !important;
    color: #e2e8f0 !important;
    border-color: #334155 !important;
  }
  [data-testid="stSidebar"] button[kind="secondary"] *,
  [data-testid="stSidebar"] [data-testid^="stBaseButton-secondary"] * {
    color: #e2e8f0 !important;
  }
  [data-testid="stSidebar"] [data-baseweb="switch"] {
    background-color: #334155 !important;
  }
  .ek-shell-bar {
    border-bottom-color: #334155 !important;
  }
  .ek-shell-logo { color: #94a3b8 !important; }
  .ek-shell-product { color: #f8fafc !important; }
  .ek-shell-tagline { color: #94a3b8 !important; }
  .ek-hero {
    background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%) !important;
    border-color: #334155 !important;
    box-shadow: 0 12px 40px rgba(0,0,0,0.35) !important;
  }
  .ek-hero-title { color: #f8fafc !important; }
  .ek-hero-sub { color: #94a3b8 !important; }
  .ek-badge {
    background: rgba(99, 102, 241, 0.22) !important;
    border-color: rgba(129, 140, 248, 0.45) !important;
    color: #c7d2fe !important;
  }
  .ek-badge-muted {
    background: #1e293b !important;
    border-color: #334155 !important;
    color: #cbd5e1 !important;
  }
  .ek-section-title { color: #94a3b8 !important; }
  /* 展开器：避免浅色灰条 */
  section.main .streamlit-expander {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
  }
  section.main .streamlit-expanderContent {
    background: #1e293b !important;
    color: #e2e8f0 !important;
  }
  .streamlit-expanderHeader {
    color: #e2e8f0 !important;
  }
  [data-testid="stChatMessage"] {
    background: #1e293b !important;
    border-color: #334155 !important;
    box-shadow: 0 8px 28px rgba(0,0,0,0.25) !important;
  }
  [data-testid="stChatMessage"] .stMarkdown,
  [data-testid="stChatMessage"] p,
  [data-testid="stChatMessage"] li {
    color: #e2e8f0 !important;
  }
  [data-testid="stChatMessage"] code {
    background: #0f172a !important;
    color: #93c5fd !important;
    border: 1px solid #334155 !important;
  }
  [data-testid="stChatInput"] textarea {
    background: #1e293b !important;
    color: #f1f5f9 !important;
    border-color: #475569 !important;
  }
  /* 底部固定输入条：去除大块白底（多版本结构兼容） */
  [data-testid="stBottom"] {
    background: #0f172a !important;
    border-top: 1px solid #1e293b !important;
  }
  [data-testid="stBottom"] > div {
    background: #0f172a !important;
  }
  [data-testid="stChatInput"] {
    background: transparent !important;
  }
  [data-testid="stChatInput"] > div {
    background: #1e293b !important;
    border-radius: 14px !important;
    border: 1px solid #475569 !important;
  }
  /* 深色模式按钮：通用覆盖 */
  section.main button[kind="secondary"],
  section.main [data-testid="stBaseButton-secondary"],
  section.main div[data-testid="stColumn"] button {
    background: #1e293b !important;
    color: #e2e8f0 !important;
    border-color: #334155 !important;
  }
  section.main button[kind="secondary"]:hover,
  section.main div[data-testid="stColumn"] button:hover {
    border-color: #6366f1 !important;
    color: #c7d2fe !important;
    background: #252f46 !important;
  }
  /* 深色模式：按钮内所有文字节点 */
  section.main button[kind="secondary"] *,
  section.main div[data-testid="stColumn"] button * {
    color: #e2e8f0 !important;
  }
  .ek-sidebar-brand { color: #64748b !important; }
  .ek-sidebar-product { color: #f8fafc !important; }
  .ek-hint { color: #94a3b8 !important; }
  [data-testid="stSidebar"] .ek-sidebar-brand { color: #64748b !important; }
  [data-testid="stSidebar"] .ek-sidebar-product { color: #f8fafc !important; }
  [data-testid="stSidebar"] .ek-hint { color: #94a3b8 !important; }
  /* 侧栏顶部品牌行（内联 flex）在深色下可读性 */
  [data-testid="stSidebar"] div[style*="display:flex"] p { color: #e2e8f0 !important; }
  [data-testid="stSidebar"] div[style*="display:flex"] p[style*="0.65rem"] { color: #94a3b8 !important; }
  /* 主区竖向块默认白底去除（示例问题列等） */
  [data-testid="stVerticalBlockBorderWrapper"] {
    background: transparent !important;
    border-color: #334155 !important;
  }
</style>
"""


def inject_enterprise_theme(theme: str = "light") -> None:
    st.markdown(ENTERPRISE_FONT_LINK, unsafe_allow_html=True)
    st.markdown(
        """
<style>
"""
        + ENTERPRISE_FONT_FACE_CSS
        + """
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }

  .main .block-container {
    padding-top: 0.35rem;
    padding-bottom: 3rem;
    max-width: 1120px;
  }
  section[data-testid="stMain"] {
    padding-top: 0.25rem !important;
  }

  /* 整体：浅灰画布 */
  .stApp {
    background: linear-gradient(180deg, #f5f7fb 0%, #f1f5f9 35%, #eef2f7 100%);
  }

  header[data-testid="stHeader"] {
    background: rgba(255,255,255,0.92);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid #e8ecf2;
  }

  /* —— 浅色侧栏（控制台） —— */
  [data-testid="stSidebar"] {
    background: #fafbfc !important;
    border-right: 1px solid #e5e7eb !important;
    box-shadow: 4px 0 24px rgba(15, 23, 42, 0.04);
  }
  [data-testid="stSidebar"] .block-container {
    padding-top: 0.75rem;
    color: #334155 !important;
  }
  [data-testid="stSidebar"] p,
  [data-testid="stSidebar"] span,
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] .stMarkdown {
    color: #475569 !important;
  }
  [data-testid="stSidebar"] .stCaption {
    color: #475569 !important;
  }
  [data-testid="stSidebar"] hr {
    border-color: #e5e7eb !important;
    margin: 1rem 0;
  }
  [data-testid="stSidebar"] section[data-testid="stSidebarNav"] {
    color: #1e293b;
  }
  [data-testid="stSidebar"] [data-baseweb="textarea"],
  [data-testid="stSidebar"] input {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important;
  }
  [data-testid="stSidebar"] .stAlert {
    border-radius: 12px !important;
    border-width: 1px !important;
  }

  [data-testid="stSidebar"] button[kind="primary"] {
    background: linear-gradient(135deg, #4f46e5 0%, #5b4ae0 50%, #6366f1 100%) !important;
    border: none !important;
    border-radius: 11px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 16px rgba(79, 70, 229, 0.2);
    color: #fafafa !important;
  }
  [data-testid="stSidebar"] button[kind="primary"]:hover {
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.28) !important;
    filter: brightness(1.03);
  }
  /* 侧栏 p/span 的通配字色会染到按钮内文（BaseWeb 多用 span 包字） */
  [data-testid="stSidebar"] button[kind="primary"] *,
  [data-testid="stSidebar"] [data-testid^="stBaseButton-primary"] * {
    color: #fafafa !important;
  }
  [data-testid="stSidebar"] button[kind="secondary"] {
    background: #ffffff !important;
    color: #334155 !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 11px !important;
    font-weight: 500 !important;
  }
  [data-testid="stSidebar"] button[kind="secondary"] *,
  [data-testid="stSidebar"] [data-testid^="stBaseButton-secondary"] * {
    color: #334155 !important;
  }
  [data-testid="stSidebar"] button[kind="secondary"]:hover {
    border-color: #93c5fd !important;
    background: #eff6ff !important;
  }

  /* —— 顶栏条（DocMind 式信息架构） —— */
  .ek-shell-wrap {
    margin-bottom: 1rem;
  }
  .ek-shell-bar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem 1rem;
    padding-bottom: 1rem;
    margin-bottom: 0.25rem;
    border-bottom: 1px solid #e8ecf2;
  }
  .ek-shell-left {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
  }
  .ek-shell-logo {
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #64748b;
    margin: 0;
  }
  .ek-shell-product {
    font-size: 1.05rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.02em;
    margin: 0;
  }
  .ek-shell-tagline {
    font-size: 0.8rem;
    color: #64748b;
    margin: 0;
  }
  .ek-shell-status {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 0.4rem 1rem;
    border-radius: 999px;
    border: 1px solid #bbf7d0;
    background: linear-gradient(180deg, #ecfdf5 0%, #d1fae5 100%);
    color: #047857;
    box-shadow: 0 1px 4px rgba(16, 185, 129, 0.12);
  }
  .ek-shell-status.warn {
    border-color: #fcd34d;
    background: linear-gradient(180deg, #fffbeb 0%, #fef3c7 100%);
    color: #b45309;
  }
  .ek-shell-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #10b981;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.25);
    animation: ek-pulse 2.5s ease-in-out infinite;
  }
  .ek-shell-status.warn .ek-shell-dot {
    background: #f59e0b;
    box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.25);
    animation: none;
  }
  @keyframes ek-pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.65; }
  }

  /* Hero 卡片 */
  .ek-hero {
    position: relative;
    background: linear-gradient(145deg, #ffffff 0%, #fafcff 50%, #ffffff 100%);
    border: 1px solid #e8ecf2;
    border-radius: 18px;
    padding: 1.25rem 1.45rem 1.15rem 1.45rem;
    margin-bottom: 1.1rem;
    box-shadow:
      0 1px 2px rgba(15, 23, 42, 0.04),
      0 12px 40px rgba(59, 130, 246, 0.06);
    overflow: hidden;
  }
  .ek-hero::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    border-radius: 18px 0 0 18px;
    background: linear-gradient(180deg, #3b82f6 0%, #6366f1 50%, #8b5cf6 100%);
  }
  .ek-hero-top {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
    padding-left: 0.35rem;
  }
  .ek-hero-title {
    font-size: 1.48rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.035em;
    line-height: 1.2;
    margin: 0;
  }
  .ek-hero-sub {
    color: #64748b;
    font-size: 0.93rem;
    margin: 0.38rem 0 0 0;
    line-height: 1.55;
    padding-left: 0.05rem;
  }
  .ek-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
    justify-content: flex-end;
    align-items: flex-start;
  }
  .ek-badge {
    display: inline-block;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    padding: 0.32rem 0.62rem;
    border-radius: 8px;
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
  }
  .ek-badge-muted {
    background: #f8fafc;
    color: #475569;
    border-color: #e2e8f0;
    font-weight: 600;
    letter-spacing: 0.03em;
  }

  .ek-section-title {
    font-size: 0.76rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 0 0 0.75rem 0;
  }

  .ek-sidebar-brand {
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #64748b !important;
    margin-bottom: 0.25rem;
  }
  .ek-sidebar-product {
    font-size: 1.06rem;
    font-weight: 700;
    color: #0f172a !important;
    margin: 0 0 0.2rem 0;
    letter-spacing: -0.02em;
  }
  .ek-hint {
    font-size: 0.8rem;
    color: #64748b !important;
    line-height: 1.5;
  }

  .streamlit-expanderHeader {
    font-weight: 600 !important;
    color: #334155 !important;
  }

  [data-testid="stChatMessage"] {
    background: #ffffff !important;
    border: 1px solid #e8ecf2 !important;
    border-radius: 14px !important;
    margin-bottom: 0.65rem !important;
    box-shadow: 0 4px 18px rgba(15, 23, 42, 0.045);
  }

  [data-testid="stChatInput"] textarea {
    border-radius: 14px !important;
    border: 1px solid #d8dee9 !important;
    box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.04);
  }

  div[data-testid="stColumn"] button {
    border-radius: 11px !important;
    font-weight: 500 !important;
    border: 1px solid #e2e8f0 !important;
    background: #ffffff !important;
    color: #334155 !important;
    padding-top: 0.65rem !important;
    padding-bottom: 0.65rem !important;
    transition: all 0.18s ease;
  }
  div[data-testid="stColumn"] button:hover {
    border-color: #3b82f6 !important;
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.14);
    color: #1e40af !important;
    transform: translateY(-1px);
  }
</style>
        """,
        unsafe_allow_html=True,
    )
    if theme == "dark":
        st.markdown(DARK_THEME_EXTRA, unsafe_allow_html=True)


def shell_header_html(
    suite_logo: str,
    suite_name: str,
    tagline: str,
    status_text: str,
    status_ok: bool,
) -> str:
    """顶栏：产品线 + 运行状态（浅色胶囊）。"""
    status_cls = "ek-shell-status" if status_ok else "ek-shell-status warn"
    return f"""
<div class="ek-shell-wrap">
  <div class="ek-shell-bar">
    <div class="ek-shell-left">
      <p class="ek-shell-logo">{html.escape(suite_logo)}</p>
      <p class="ek-shell-product">{html.escape(suite_name)}</p>
      <p class="ek-shell-tagline">{html.escape(tagline)}</p>
    </div>
    <div class="{status_cls}">
      <span class="ek-shell-dot"></span>
      <span>{html.escape(status_text)}</span>
    </div>
  </div>
</div>
"""


def hero_html(
    page_icon: str,
    page_title: str,
    brand_name: str,
    tagline: str,
    badges: List[Tuple[str, str]],
) -> str:
    parts = []
    for label, variant in badges:
        cls = "ek-badge" if variant == "primary" else "ek-badge ek-badge-muted"
        parts.append(f'<span class="{cls}">{html.escape(label)}</span>')
    badges_html = "".join(parts)
    return f"""
<div class="ek-hero">
  <div class="ek-hero-top">
    <div>
      <p class="ek-hero-title">{html.escape(page_icon)} {html.escape(page_title)}</p>
      <p class="ek-hero-sub">{html.escape(brand_name)} · {html.escape(tagline)}</p>
    </div>
    <div class="ek-badges">{badges_html}</div>
  </div>
</div>
"""
