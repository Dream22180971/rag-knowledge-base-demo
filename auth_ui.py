"""精致登录页：左右分栏布局，宽屏友好。"""

import os
from datetime import datetime

import streamlit as st

from brand_assets import (
    login_brand_visual_html,
    login_feature_list_html,
)
from ui_styles import ENTERPRISE_FONT_FACE_CSS


def _expected_credentials() -> tuple[str, str]:
    u = os.getenv("DEMO_USERNAME", "demo").strip()
    p = os.getenv("DEMO_PASSWORD", "demo").strip()
    return u, p


def verify_login(username: str, password: str) -> bool:
    eu, ep = _expected_credentials()
    return username.strip() == eu and password == ep


def _login_css(theme: str) -> str:
    is_dark = theme == "dark"

    title_c = "#f8fafc" if is_dark else "#111827"
    sub_c = "#94a3b8" if is_dark else "#6b7280"
    label_c = "#cbd5e1" if is_dark else "#374151"
    input_bg = "#1e293b" if is_dark else "#ffffff"
    input_border = "#334155" if is_dark else "#d1d5db"
    input_text = "#f1f5f9" if is_dark else "#111827"
    foot_c = "#64748b" if is_dark else "#9ca3af"
    right_bg = "#111827" if is_dark else "#ffffff"

    return f"""
<style>
  {ENTERPRISE_FONT_FACE_CSS}

  #MainMenu, footer {{ visibility: hidden; }}
  header[data-testid="stHeader"] {{
    background: transparent !important;
    border-bottom: none !important;
    height: 0 !important;
    min-height: 0 !important;
  }}
  section[data-testid="stMain"] {{ padding-top: 0 !important; }}
  section.main .block-container,
  .stMainBlockContainer.block-container,
  [data-testid="stMainBlockContainer"] {{
    padding: 0 !important;
    max-width: 100% !important;
    margin: 0 !important;
  }}
  .stApp {{ background: transparent !important; }}

  /* ===== 全屏固定背景 ===== */
  .ek-bg {{
    position: fixed;
    inset: 0;
    z-index: 0;
    display: flex;
  }}
  .ek-bg-left {{
    flex: 5;
    background: linear-gradient(160deg, #0c1222 0%, #131a2e 40%, #1a1f3a 100%);
    position: relative;
    overflow: hidden;
  }}
  .ek-bg-left::before {{
    content: "";
    position: absolute;
    top: 15%;
    right: -5%;
    width: 400px;
    height: 400px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(99,102,241,0.07) 0%, transparent 70%);
  }}
  .ek-bg-right {{
    flex: 4;
    background: {right_bg};
  }}

  /* ===== 内容层 ===== */
  [data-testid="stMain"] {{
    position: relative;
    z-index: 1;
  }}
  [data-testid="stHorizontalBlock"] {{
    min-height: 100vh;
    gap: 0 !important;
  }}

  /* 列容器：全高 flex column */
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    padding: 0 !important;
  }}
  /* 列内所有层级都撑满，确保 wrapper 的 min-height:100vh 生效 */
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > div {{
    flex: 1 1 auto !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    min-height: 0 !important;
  }}
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > div > div {{
    flex: 1 1 auto !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
  }}
  /* 左列：内容水平左对齐，但垂直居中 */
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child > div,
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child > div > div {{
    align-items: flex-start !important;
  }}
  /* 右列：内容水平居中 */
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child > div,
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child > div > div {{
    align-items: center !important;
  }}

  /* ===== 左栏 ===== */
  .ek-login-left-wrap {{
    padding: 0 4.5rem;
    width: 100%;
    box-sizing: border-box;
    display: flex;
    align-items: center;
    min-height: 100vh;
  }}
  .ek-login-left-inner {{
    text-align: left;
    max-width: 480px;
    width: 100%;
  }}

  /* Logo 横向 */
  .ek-login-brand {{
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 0.85rem;
    margin-bottom: 3rem;
  }}
  .ek-login-brand-ring {{
    padding: 9px;
    border-radius: 16px;
    background: rgba(255,255,255,0.06);
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
  }}
  .ek-login-brand-cn {{
    font-size: 1.05rem;
    font-weight: 700;
    color: #f8fafc;
    margin: 0;
    line-height: 1.3;
  }}
  .ek-login-brand-en {{
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: rgba(148, 163, 184, 0.7);
    margin: 0;
  }}

  /* 大标题 */
  .ek-login-hero-title {{
    font-size: 2.1rem;
    font-weight: 700;
    color: #f1f5f9;
    letter-spacing: -0.01em;
    margin: 0 0 0.55rem 0;
    line-height: 1.2;
  }}
  .ek-login-left-desc {{
    font-size: 0.9rem;
    color: rgba(148, 163, 184, 0.85);
    line-height: 1.6;
    margin: 0 0 2.6rem 0;
  }}

  /* 功能卡片 */
  .ek-feat-card {{
    display: flex;
    align-items: center;
    gap: 0.9rem;
    padding: 0.9rem 1rem;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    background: rgba(255,255,255,0.025);
    margin-bottom: 0.65rem;
  }}
  .ek-feat-icon {{
    flex-shrink: 0;
    width: 38px;
    height: 38px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 9px;
    background: rgba(255,255,255,0.06);
    color: #a5b4fc;
  }}
  .ek-feat-text {{ flex: 1; }}
  .ek-feat-title {{
    font-size: 0.85rem;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 0.1rem;
  }}
  .ek-feat-desc {{
    font-size: 0.76rem;
    color: rgba(148, 163, 184, 0.75);
    line-height: 1.4;
  }}

  /* ===== 右栏 ===== */
  .ek-login-right-wrap {{
    padding: 0 2.5rem;
    max-width: 400px;
    width: 100%;
    box-sizing: border-box;
  }}
  .ek-login-form-title {{
    font-size: 1.6rem;
    font-weight: 700;
    color: {title_c};
    margin: 0 0 0.35rem 0;
    letter-spacing: -0.015em;
  }}
  .ek-login-form-sub {{
    font-size: 0.88rem;
    color: {sub_c};
    margin: 0 0 1.8rem 0;
    line-height: 1.5;
  }}

  /* 输入框 */
  [data-baseweb="input"] {{ background: transparent !important; }}
  [data-baseweb="input"] > div {{
    background-color: {input_bg} !important;
    border: 1px solid {input_border} !important;
    border-radius: 10px !important;
  }}
  [data-baseweb="input"] > div:focus-within {{
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,{"0.1" if is_dark else "0.06"}) !important;
  }}
  [data-baseweb="input"] input {{
    background-color: transparent !important;
    color: {input_text} !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 11px 14px !important;
    font-size: 0.9rem !important;
  }}
  label[data-testid="stWidgetLabel"] {{
    color: {label_c} !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
  }}

  /* 按钮 */
  button[kind="primary"] {{
    width: 100% !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 0.68rem 1rem !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    background: linear-gradient(135deg, #4f46e5 0%, #4338ca 60%, #5b4ae0 100%) !important;
    color: #fafafa !important;
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.28) !important;
    margin-top: 0.4rem !important;
  }}
  button[kind="primary"]:hover {{
    box-shadow: 0 8px 28px rgba(79, 70, 229, 0.38) !important;
    filter: brightness(1.05);
  }}

  .ek-login-foot {{
    font-size: 0.75rem;
    color: {foot_c};
    margin-top: 1.8rem;
    line-height: 1.5;
  }}

  /* 响应式 */
  @media (max-width: 860px) {{
    .ek-bg {{ flex-direction: column; }}
    .ek-bg-left {{ min-height: 35vh; }}
    .ek-bg-right {{ min-height: 65vh; }}
    [data-testid="stHorizontalBlock"] {{
      flex-direction: column !important;
      min-height: auto !important;
    }}
    .ek-login-left-wrap {{ min-height: auto; padding: 2.5rem 2rem; }}
    .ek-login-right-wrap {{ min-height: auto; padding: 2rem; }}
  }}
</style>
"""


def render_login_page() -> None:
    theme = st.session_state.get("theme", "light")
    st.markdown(_login_css(theme), unsafe_allow_html=True)

    eu, _ = _expected_credentials()

    # 全屏固定背景
    st.markdown(
        '<div class="ek-bg"><div class="ek-bg-left"></div><div class="ek-bg-right"></div></div>',
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns([5, 4], gap="small")

    with col_left:
        st.markdown(
            f"""
<div class="ek-login-left-wrap">
  <div class="ek-login-left-inner">
    {login_brand_visual_html(68)}
    <div class="ek-login-hero-title">企业知识库</div>
    <p class="ek-login-left-desc">
      智能问答与引用溯源系统<br/>
      精准检索 · 多轮对话 · 安全可控
    </p>
    {login_feature_list_html()}
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown(
            """
<div class="ek-login-right-wrap">
  <div class="ek-login-form">
    <div class="ek-login-form-title">欢迎回来</div>
    <div class="ek-login-form-sub">请使用分配的账号登录系统</div>
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )

        u = st.text_input("账号", key="login_user", placeholder="请输入账号")
        p = st.text_input("密码", type="password", key="login_pass", placeholder="请输入密码")

        if st.button("登 录", type="primary", use_container_width=True):
            if not u or not p:
                st.warning("请输入账号和密码。")
            elif verify_login(u, p):
                st.session_state.authenticated = True
                st.session_state.username = u.strip()
                st.session_state.login_at = datetime.now().isoformat(timespec="seconds")
                st.rerun()
            else:
                st.error("账号或密码不正确（可在 .env 设置 DEMO_USERNAME / DEMO_PASSWORD）。")

        _dark = st.toggle(
            "深色模式",
            value=(theme == "dark"),
            help="与登录后工作台共用同一主题偏好",
        )
        if _dark != (st.session_state.get("theme") == "dark"):
            st.session_state.theme = "dark" if _dark else "light"
            st.rerun()

        st.markdown(
            f'<p class="ek-login-foot">演示环境 · 默认账号 <code style="color:#818cf8;">{eu}</code>'
            f" · 与 .env 中 DEMO 账号一致</p>",
            unsafe_allow_html=True,
        )
