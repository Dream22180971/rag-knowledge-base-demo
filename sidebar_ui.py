"""侧栏：品牌、外观、账户、会话、知识库、帮助（功能分区）。"""

import glob
import html
import os

import streamlit as st

from brand_assets import PRODUCT_SUITE_CN, logo_img_html
from config import KB_BRAND_NAME, KB_SCENE_DESC
from llm_providers import describe_active_provider
from rag_pipeline_faiss import (
    build_index,
    get_index_meta,
    load_documents,
    reset_vectorstore_cache,
    split_documents,
)
from session_manager import (
    new_conversation,
    ordered_session_ids,
    persist_from_streamlit,
    session_label,
    switch_session,
)
from upload_handler import persist_uploaded_document


def render_sidebar(
    knowledge_dir: str,
    upload_dir: str,
) -> bool:
    """
    渲染侧栏。返回 debug 开关（是否开启调试模式）。
    """
    meta = get_index_meta()
    files = (
        glob.glob(os.path.join(knowledge_dir, "**/*.md"), recursive=True)
        + glob.glob(os.path.join(knowledge_dir, "**/*.txt"), recursive=True)
        + glob.glob(os.path.join(knowledge_dir, "**/*.pdf"), recursive=True)
        + glob.glob(os.path.join(knowledge_dir, "**/*.docx"), recursive=True)
    )

    with st.sidebar:
        # —— 品牌区 ——
        st.markdown(
            f"""
<div style="display:flex;align-items:center;gap:12px;margin-bottom:0.5rem;">
  {logo_img_html(44)}
  <div>
    <p style="margin:0;font-size:0.65rem;font-weight:800;letter-spacing:0.12em;text-transform:uppercase;color:#64748b;">{PRODUCT_SUITE_CN}</p>
    <p style="margin:0.1rem 0 0 0;font-size:1.02rem;font-weight:700;color:#0f172a;letter-spacing:-0.02em;">知识库控制台</p>
  </div>
</div>
<p class="ek-hint" style="margin:0 0 0.8rem 0;">文档 · 索引 · 对话 · 一体化</p>
            """,
            unsafe_allow_html=True,
        )

        st.divider()
        st.markdown("##### 外观")
        if "theme" not in st.session_state:
            st.session_state.theme = "light"
        dark_on = st.toggle(
            "深色模式",
            value=st.session_state.theme == "dark",
            help="切换浅色 / 深色界面",
        )
        if dark_on != (st.session_state.theme == "dark"):
            st.session_state.theme = "dark" if dark_on else "light"
            st.rerun()

        st.divider()
        st.markdown("##### 账户与组织")
        with st.expander("个人信息", expanded=False):
            st.markdown(f"**登录账号**：`{html.escape(st.session_state.username)}`")
            st.caption(f"登录时间：{st.session_state.get('login_at', '—')}")
        st.selectbox(
            "当前租户",
            ["默认租户（演示）"],
            index=0,
            disabled=True,
            help="多租户切换与鉴权将在后续版本接入；当前为单租户演示。",
        )
        if st.button("退出登录", use_container_width=True):
            persist_from_streamlit(st.session_state, st.session_state.username)
            _theme_keep = st.session_state.get("theme", "light")
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.session_state.theme = _theme_keep
            st.session_state.authenticated = False
            st.rerun()

        st.divider()
        st.markdown("##### 会话")
        st.caption("新开会话会保留在下方「历史」中，可随时切回。")
        if st.button("＋ 新对话", type="primary", use_container_width=True):
            new_conversation(st.session_state)
            st.rerun()

        _ids = ordered_session_ids(st.session_state)
        if _ids:
            _cur = st.session_state.current_session_id
            _idx = _ids.index(_cur) if _cur in _ids else 0
            # 勿与 key 同时使用 index，否则会触发 session_state 与默认值的策略警告
            _choice = st.selectbox(
                "历史会话",
                _ids,
                index=_idx,
                format_func=lambda sid: session_label(st.session_state, sid),
            )
            if _choice != st.session_state.current_session_id:
                persist_from_streamlit(st.session_state, st.session_state.username)
                switch_session(st.session_state, st.session_state.username, _choice)
                st.rerun()

        if st.button("清空当前会话", use_container_width=True):
            st.session_state.messages = []
            _sid = st.session_state.current_session_id
            if _sid in st.session_state.chat_sessions:
                st.session_state.chat_sessions[_sid]["messages"] = []
            persist_from_streamlit(st.session_state, st.session_state.username)
            st.rerun()

        st.divider()
        st.markdown("##### 知识域与索引")
        st.caption("当前知识域")
        st.markdown(
            f'<p class="ek-sidebar-product" style="font-size:0.95rem;">{html.escape(KB_BRAND_NAME)}</p>',
            unsafe_allow_html=True,
        )
        st.caption(f"场景：{KB_SCENE_DESC}")
        if meta:
            st.success(
                f"**索引正常** · {meta['chunk_count']} 条  \n`{meta.get('built_at', '')}`"
            )
        else:
            st.warning("尚未构建索引。")
        st.caption(f"知识库文件 {len(files)} 个 · {describe_active_provider()}")
        st.caption("嵌入：DashScope（换模型需重建）")

        st.divider()
        st.markdown("##### 文档接入")
        st.caption("PDF / Word / MD / TXT，清洗后导入；随后需 **重建索引**。")
        _up = st.file_uploader(
            "上传",
            type=["pdf", "docx", "md", "txt", "markdown"],
            label_visibility="collapsed",
        )
        if _up is not None and st.button("导入并清洗", use_container_width=True, key="btn_import"):
            try:
                _path = persist_uploaded_document(
                    _up.getvalue(), _up.name, upload_dir
                )
                reset_vectorstore_cache()
                st.success(f"已保存，请 **重建索引** 后生效。")
            except Exception as e:
                st.error(f"导入失败：{e}")

        if st.button("重建索引", use_container_width=True, key="btn_reindex"):
            _bar = st.progress(0)
            _tx = st.empty()

            def _pg(m, p):
                _bar.progress(min(int(p * 100), 100))
                _tx.text(m)

            try:
                with st.spinner("构建中…"):
                    _pg("扫描…", 0)
                    _docs = load_documents(knowledge_dir, progress_callback=_pg)
                    if not _docs:
                        st.warning("未找到可加载文档。")
                    else:
                        _ch = split_documents(_docs, progress_callback=_pg)
                        build_index(_ch, progress_callback=_pg)
                        st.success(f"完成，**{len(_ch)}** 段。")
                        st.rerun()
            except Exception as e:
                st.error(str(e))

        st.divider()
        st.markdown("##### 帮助与调试")
        with st.expander("使用说明", expanded=False):
            st.markdown(
                """
1. 先 **重建索引** 再提问  
2. 支持多轮追问，历史在侧栏切换  
3. 账号在 `.env` 中 `DEMO_USERNAME` / `DEMO_PASSWORD` 配置（默认 demo / demo）
                """
            )
        _debug = st.checkbox("调试模式", value=False, key="ek_debug")
        if _debug:
            st.code(f"KNOWLEDGE_DIR =\n{knowledge_dir}", language="text")
            if meta:
                st.json(meta)

    return _debug
