"""
企业级电商知识库问答助手 — 登录 / 多会话 / 深浅色 / 侧栏分区
"""
from __future__ import annotations

import html
import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from config import KB_BRAND_NAME, KB_SCENE_DESC, KB_SIMPLE_DESC, PAGE_ICON, PAGE_TITLE
from rag_pipeline_faiss import get_index_meta, rag_pipeline
from session_manager import bootstrap_sessions, persist_from_streamlit
from sidebar_ui import render_sidebar
from ui_styles import hero_html, inject_enterprise_theme

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.path.join(PROJECT_ROOT, "knowledge")
UPLOAD_DIR = os.path.join(KNOWLEDGE_DIR, "texts", "uploads")
ICON_PATH = os.path.join(PROJECT_ROOT, "assets", "logo_icon.svg")
_PAGE_ICON = ICON_PATH if os.path.isfile(ICON_PATH) else PAGE_ICON

if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = True
    st.session_state.username = "demo"
    st.session_state.login_at = datetime.now().isoformat(timespec="seconds")

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=_PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_enterprise_theme(st.session_state.theme)

# 加载会话树
if not st.session_state.get("chat_bootstrapped"):
    bootstrap_sessions(st.session_state, st.session_state.username)
    st.session_state.chat_bootstrapped = True

debug = render_sidebar(KNOWLEDGE_DIR, UPLOAD_DIR)

# ============================================================
# Main
# ============================================================
meta_main = get_index_meta()
_idx_ok = meta_main is not None and meta_main.get("chunk_count", 0) > 0

# 欢迎区域（小白友好）
st.markdown(
    f"""
<div style="text-align:center;padding:2.5rem 0 1.5rem 0;">
  <div style="font-size:2.2rem;margin-bottom:0.5rem;">💬</div>
  <h2 style="margin:0 0 0.4rem 0;font-weight:700;letter-spacing:-0.02em;">
    你好，我是{html.escape(KB_BRAND_NAME)}的智能客服
  </h2>
  <p style="margin:0;font-size:1rem;color:#6b7280;">
    {html.escape(KB_SIMPLE_DESC)}
  </p>
</div>
    """,
    unsafe_allow_html=True,
)

if not _idx_ok:
    st.warning("知识库尚未就绪，请在左下角「设置」中点击「重建索引」后再提问。")

example_questions = [
    ("📦", "满多少元可以包邮？"),
    ("🔧", "签收后发现商品破损该怎么处理？"),
    ("📋", "售后单状态「待寄回」是什么意思？"),
    ("💳", "支持哪些支付方式？"),
]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_text = st.session_state.messages[-1]["content"]
    history = st.session_state.messages[:-1]

    with st.chat_message("assistant"):
        with st.spinner("正在检索知识库并生成回答…"):
            try:
                result = rag_pipeline(
                    user_text,
                    knowledge_dir=KNOWLEDGE_DIR,
                    chat_history=history,
                )
            except Exception as e:
                import traceback

                err_detail = traceback.format_exc()
                st.error(f"运行异常：{e}")
                if debug:
                    st.code(err_detail)
                err_text = f"系统错误：{e}"
                st.session_state.messages.append(
                    {"role": "assistant", "content": err_text}
                )
                persist_from_streamlit(st.session_state, st.session_state.username)
                st.stop()

        if "error" in result:
            st.error(result["error"])
            response_text = result["error"]
        else:
            st.markdown(result["answer"])
            response_text = result["answer"]

            with st.expander(f"参考来源 · {len(result['sources'])} 条"):
                for i, src in enumerate(result["sources"], 1):
                    preview = src["content"][:500] + (
                        "…" if len(src["content"]) > 500 else ""
                    )
                    st.markdown(
                        f"**[{i}]** `{src['source']}` · `{src['score']}`\n\n> {preview}"
                    )
                    st.divider()

            st.caption(f"响应耗时 {result['elapsed_ms']} ms")

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    persist_from_streamlit(st.session_state, st.session_state.username)

if prompt := st.chat_input("输入问题，支持连续追问…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    persist_from_streamlit(st.session_state, st.session_state.username)
    st.rerun()

if not st.session_state.messages:
    st.markdown(
        '<p class="ek-section-title" style="text-align:center;">试试问我</p>',
        unsafe_allow_html=True,
    )
    cols = st.columns(len(example_questions))
    for col, (icon, q) in zip(cols, example_questions):
        if col.button(f"{icon}  {q}", key=f"ex_{q}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": q})
            persist_from_streamlit(st.session_state, st.session_state.username)
            st.rerun()
