"""简易登录页（演示账号；独立样式，与主控制台视觉区分）。"""

import os
from datetime import datetime

import streamlit as st

from brand_assets import login_brand_visual_html
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
    bg = (
        "linear-gradient(165deg, #0b1220 0%, #111827 45%, #0f172a 100%)"
        if is_dark
        else "linear-gradient(165deg, #eef2ff 0%, #f8fafc 40%, #f1f5f9 100%)"
    )
    card_bg = (
        "linear-gradient(180deg, #1e293b 0%, #172033 100%)"
        if is_dark
        else "linear-gradient(180deg, #ffffff 0%, #fafbff 100%)"
    )
    card_border = "#334155" if is_dark else "#e2e8f0"
    title_c = "#f8fafc" if is_dark else "#0f172a"
    sub_c = "#94a3b8" if is_dark else "#64748b"
    foot_c = "#64748b" if is_dark else "#94a3b8"
    input_bg = "#0f172a" if is_dark else "#ffffff"
    input_border = "#475569" if is_dark else "#e2e8f0"
    input_text = "#f1f5f9" if is_dark else "#0f172a"
    label_c = "#cbd5e1" if is_dark else "#475569"

    return f"""
<style>
  {ENTERPRISE_FONT_FACE_CSS}
  .stApp {{
    background: {bg} !important;
  }}
  header[data-testid="stHeader"] {{
    background: transparent !important;
    border-bottom: none !important;
  }}
  /* 整块主列为登录卡片，避免拆开的 <div> 在 Streamlit 里变成无效 DOM / 顶部怪异块 */
  section.main .block-container {{
    padding-top: 1.55rem !important;
    padding-bottom: 1.5rem !important;
    padding-left: 1.75rem !important;
    padding-right: 1.75rem !important;
    max-width: 420px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    margin-top: 0.15rem !important;
    background: {card_bg};
    border: 1px solid {card_border};
    border-radius: 22px;
    box-shadow: {"0 24px 64px rgba(0,0,0,0.45)" if is_dark else "0 20px 60px rgba(15, 23, 42, 0.08)"};
  }}
  section[data-testid="stMain"] {{
    padding-top: 0.25rem !important;
  }}
  .ek-login-brand {{
    display: flex;
    align-items: center;
    gap: 1.1rem;
    margin-bottom: 1.6rem;
  }}
  .ek-login-brand-ring {{
    flex-shrink: 0;
    padding: 10px;
    border-radius: 20px;
    background: {"linear-gradient(145deg, #312e81 0%, #1e1b4b 100%)" if is_dark else "linear-gradient(145deg, #eef2ff 0%, #e0e7ff 100%)"};
    box-shadow: {"inset 0 1px 0 rgba(255,255,255,0.06), 0 12px 36px rgba(0,0,0,0.35)" if is_dark else "0 12px 32px rgba(79, 70, 229, 0.18)"};
  }}
  .ek-login-brand-cn {{
    font-size: 1.35rem;
    font-weight: 700;
    color: {title_c};
    letter-spacing: -0.03em;
    margin: 0;
    line-height: 1.25;
  }}
  .ek-login-brand-en {{
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: {sub_c};
    margin: 0.35rem 0 0 0;
  }}
  .ek-login-sub {{
    font-size: 0.88rem;
    color: {sub_c};
    margin: 0 0 1.35rem 0;
    line-height: 1.55;
  }}
  .ek-login-foot {{
    font-size: 0.72rem;
    color: {foot_c};
    margin-top: 1.35rem;
    text-align: center;
    line-height: 1.45;
  }}
  /* BaseWeb 外层在深色下勿留白托 */
  section.main [data-baseweb="input"] {{
    background: transparent !important;
  }}
  section.main [data-baseweb="input"] > div {{
    background-color: {input_bg} !important;
    border: 1px solid {input_border} !important;
    border-radius: 12px !important;
  }}
  /* 登录表单控件（仅含 input，不影响对话 textarea） */
  section.main [data-baseweb="input"] input {{
    background-color: transparent !important;
    color: {input_text} !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 11px 14px !important;
    font-size: 0.95rem !important;
  }}
  section.main label[data-testid="stWidgetLabel"] {{
    color: {label_c} !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
  }}
  /* 主区唯一主按钮：登录（避免侧栏 primary） */
  section.main button[kind="primary"] {{
    width: 100% !important;
    border-radius: 12px !important;
    border: none !important;
    padding: 0.7rem 1rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    background: linear-gradient(135deg, #4f46e5 0%, #4338ca 55%, #6366f1 100%) !important;
    color: #fafafa !important;
    box-shadow: 0 10px 28px rgba(79, 70, 229, 0.35) !important;
  }}
  section.main button[kind="primary"]:hover {{
    box-shadow: 0 12px 36px rgba(79, 70, 229, 0.45) !important;
    filter: brightness(1.05);
  }}
</style>
    """


def render_login_page() -> None:
    theme = st.session_state.get("theme", "light")
    st.markdown(_login_css(theme), unsafe_allow_html=True)

    st.markdown(login_brand_visual_html(78), unsafe_allow_html=True)
    st.markdown(
        '<p class="ek-login-sub">企业知识库 · 智能问答与引用溯源<br/>请使用分配账号登录</p>',
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
        "深色登录界面",
        value=(theme == "dark"),
        help="与登录后工作台共用同一主题偏好",
    )
    if _dark != (st.session_state.get("theme") == "dark"):
        st.session_state.theme = "dark" if _dark else "light"
        st.rerun()

    eu, _ = _expected_credentials()
    st.markdown(
        f'<p class="ek-login-foot">演示环境 · 默认账号 <code style="color:#818cf8;">{eu}</code>'
        f" · 与 .env 中 DEMO 账号一致</p>",
        unsafe_allow_html=True,
    )
