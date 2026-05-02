"""简易登录页（演示：账号密码读环境变量，默认 demo / demo）。"""

import os
from datetime import datetime

import streamlit as st

from brand_assets import PRODUCT_SUITE_CN, logo_img_html


def _expected_credentials() -> tuple[str, str]:
    u = os.getenv("DEMO_USERNAME", "demo").strip()
    p = os.getenv("DEMO_PASSWORD", "demo").strip()
    return u, p


def verify_login(username: str, password: str) -> bool:
    eu, ep = _expected_credentials()
    return username.strip() == eu and password == ep


def render_login_page() -> None:
    st.markdown(
        """
<style>
  .login-wrap { max-width: 420px; margin: 3rem auto 2rem auto; padding: 0 1rem; }
  .login-card {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 2rem 1.75rem 1.75rem 1.75rem;
    box-shadow: 0 16px 48px rgba(15, 23, 42, 0.08);
  }
  .login-brand { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.25rem; }
  .login-title { font-size: 1.35rem; font-weight: 700; color: #0f172a; margin: 0; letter-spacing: -0.03em; }
  .login-sub { font-size: 0.88rem; color: #64748b; margin: 0.35rem 0 0 0; line-height: 1.45; }
  .login-foot { font-size: 0.75rem; color: #94a3b8; margin-top: 1.25rem; text-align: center; }
</style>
        """,
        unsafe_allow_html=True,
    )

    col_gap, col_main, col_gap2 = st.columns([1, 2.2, 1])
    with col_main:
        st.markdown('<div class="login-wrap"><div class="login-card">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="login-brand">{logo_img_html(52)}<div><p class="login-title">{PRODUCT_SUITE_CN}</p>'
            f'<p class="login-sub">企业知识库 · 智能问答与溯源</p></div></div>',
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
                st.error("账号或密码不正确（演示环境可在 .env 配置 DEMO_USERNAME / DEMO_PASSWORD）。")

        eu, _ = _expected_credentials()
        st.markdown(
            f'<p class="login-foot">演示默认账号与服务器配置一致 · 当前预设用户：<code>{eu}</code></p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div></div>", unsafe_allow_html=True)
