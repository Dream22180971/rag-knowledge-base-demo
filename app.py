"""
企业级电商知识库问答助手 — 登录 / 多会话 / 深浅色 / 侧栏分区
"""
from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from auth_ui import render_login_page
from config import KB_BRAND_NAME, KB_SCENE_DESC, PAGE_ICON, PAGE_TITLE
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
    st.session_state.theme = "light"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=_PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_enterprise_theme(st.session_state.theme)

if not st.session_state.authenticated:
    render_login_page()
    st.stop()

# 登录后：加载会话树
if not st.session_state.get("chat_bootstrapped"):
    bootstrap_sessions(st.session_state, st.session_state.username)
    st.session_state.chat_bootstrapped = True

debug = render_sidebar(KNOWLEDGE_DIR, UPLOAD_DIR)

# ============================================================
# Main
# ============================================================
meta_main = get_index_meta()
_idx_ok = meta_main is not None and meta_main.get("chunk_count", 0) > 0

_badge_list = [
    ("RAG", "primary"),
    ("多轮对话", "muted"),
    ("DashScope 向量", "muted"),
]
if meta_main:
    _badge_list.insert(0, (f"{meta_main['chunk_count']} 条索引", "primary"))
else:
    _badge_list.insert(0, ("待构建索引", "muted"))
_status_hint = "索引就绪 · 可直接提问" if _idx_ok else "请先于侧栏「重建索引」"
st.markdown(
    hero_html(
        PAGE_ICON,
        PAGE_TITLE,
        KB_BRAND_NAME,
        f"{_status_hint} · 左侧切换「历史会话」· 底部连续追问",
        _badge_list,
    ),
    unsafe_allow_html=True,
)

with st.expander("使用指南（必读）", expanded=False):
    st.markdown(
        f"""
**三步开始**：① 侧栏 **重建索引** → ② 在下方提问或点示例 → ③ 需要新话题时点 **新对话**。  
**当前知识域**：{KB_BRAND_NAME}（{KB_SCENE_DESC}）。事实以检索片段为准，超出范围请转人工。

租户切换、审计等企业能力为后续规划；本环境为演示配置。
        """
    )

example_questions = [
    "满多少元可以包邮？",
    "签收后发现商品破损该怎么处理？",
    "售后单状态「待寄回」是什么意思？",
    "支持哪些支付方式？",
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
        '<p class="ek-section-title">快速发起问询</p>',
        unsafe_allow_html=True,
    )
    cols = st.columns(len(example_questions))
    for col, q in zip(cols, example_questions):
        if col.button(q, key=f"ex_{q}"):
            st.session_state.messages.append({"role": "user", "content": q})
            persist_from_streamlit(st.session_state, st.session_state.username)
            st.rerun()
