"""企业级控制台视觉样式：注入自定义 CSS（与 Streamlit 默认主题叠加）。"""

import html
from typing import List, Tuple

import streamlit as st


def inject_enterprise_theme() -> None:
    st.markdown(
        """
<style>
  /* —— 全局 —— */
  .main .block-container {
    padding-top: 1.25rem;
    padding-bottom: 3rem;
    max-width: 1080px;
  }
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }
  header[data-testid="stHeader"] {
    background: rgba(255,255,255,0.85);
    backdrop-filter: blur(8px);
  }

  /* —— 主区背景 —— */
  .stApp {
    background: linear-gradient(165deg, #eef2f7 0%, #f8fafc 45%, #f1f5f9 100%);
  }

  /* —— 侧栏：深色控制台风 —— */
  [data-testid="stSidebar"] {
    background: linear-gradient(195deg, #0f172a 0%, #1e293b 52%, #0f172a 100%) !important;
    border-right: 1px solid rgba(148, 163, 184, 0.15);
  }
  [data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
    color: #e2e8f0;
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
  [data-testid="stSidebar"] h1,
  [data-testid="stSidebar"] h2,
  [data-testid="stSidebar"] h3 {
    color: #f8fafc !important;
    font-weight: 600;
    letter-spacing: -0.02em;
  }
  [data-testid="stSidebar"] hr {
    border-color: rgba(148, 163, 184, 0.25);
  }
  [data-testid="stSidebar"] [data-baseweb="textarea"],
  [data-testid="stSidebar"] input {
    background-color: rgba(15, 23, 42, 0.6) !important;
    color: #f1f5f9 !important;
    border-radius: 8px !important;
  }
  [data-testid="stSidebar"] .stAlert {
    background-color: rgba(30, 41, 59, 0.85) !important;
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 10px;
  }
  [data-testid="stSidebar"] .stSuccess {
    background: rgba(22, 101, 52, 0.35) !important;
    border: 1px solid rgba(74, 222, 128, 0.35);
  }
  [data-testid="stSidebar"] .stWarning {
    background: rgba(120, 53, 15, 0.35) !important;
    border: 1px solid rgba(251, 191, 36, 0.35);
  }

  /* 侧栏主按钮 */
  [data-testid="stSidebar"] button[kind="primary"] {
    background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
  }
  [data-testid="stSidebar"] button[kind="secondary"] {
    background: rgba(51, 65, 85, 0.6) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(148, 163, 184, 0.25) !important;
    border-radius: 10px !important;
  }

  /* —— 自定义 HTML 块 —— */
  .ek-hero {
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.35rem 1.5rem 1.15rem 1.5rem;
    margin-bottom: 1.15rem;
    box-shadow: 0 4px 24px rgba(15, 23, 42, 0.06);
  }
  .ek-hero-top {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
  }
  .ek-hero-title {
    font-size: 1.55rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.03em;
    line-height: 1.25;
    margin: 0;
  }
  .ek-hero-sub {
    color: #64748b;
    font-size: 0.92rem;
    margin: 0.4rem 0 0 0;
    line-height: 1.5;
  }
  .ek-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
    justify-content: flex-end;
  }
  .ek-badge {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 0.28rem 0.55rem;
    border-radius: 6px;
    background: #eff6ff;
    color: #1d4ed8;
    border: 1px solid #bfdbfe;
  }
  .ek-badge-muted {
    background: #f1f5f9;
    color: #475569;
    border-color: #e2e8f0;
  }

  .ek-panel {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1rem 1.15rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 12px rgba(15, 23, 42, 0.04);
  }
  .ek-section-title {
    font-size: 0.78rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0 0 0.65rem 0;
  }
  .ek-sidebar-brand {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #64748b !important;
    margin-bottom: 0.35rem;
  }
  .ek-sidebar-product {
    font-size: 1.05rem;
    font-weight: 700;
    color: #f8fafc !important;
    margin: 0 0 0.15rem 0;
    letter-spacing: -0.02em;
  }
  .ek-hint {
    font-size: 0.8rem;
    color: #94a3b8;
    line-height: 1.45;
  }

  /* 主区 expander */
  .streamlit-expanderHeader {
    font-weight: 600 !important;
    color: #334155 !important;
  }

  /* 聊天气泡区域微调 */
  [data-testid="stChatMessage"] {
    background-color: rgba(255, 255, 255, 0.92) !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    margin-bottom: 0.65rem !important;
    box-shadow: 0 1px 8px rgba(15, 23, 42, 0.04);
  }

  /* Chat input 圆角 */
  [data-testid="stChatInput"] textarea {
    border-radius: 12px !important;
    border: 1px solid #cbd5e1 !important;
  }

  /* 快捷问题按钮：次级轮廓风 */
  div[data-testid="column"] button {
    border-radius: 10px !important;
    font-weight: 500 !important;
    border: 1px solid #cbd5e1 !important;
    background: #ffffff !important;
    color: #334155 !important;
    transition: border-color 0.15s, box-shadow 0.15s;
  }
  div[data-testid="column"] button:hover {
    border-color: #3b82f6 !important;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
    color: #1e40af !important;
  }
</style>
        """,
        unsafe_allow_html=True,
    )


def hero_html(
    page_icon: str,
    page_title: str,
    brand_name: str,
    tagline: str,
    badges: List[Tuple[str, str]],
) -> str:
    """badges: (label, variant) variant: primary | muted"""
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
