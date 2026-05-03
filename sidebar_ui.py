"""侧栏：精简版 — 对话 + 设置折叠区。"""

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
        # ── 品牌区 ──
        st.markdown(
            f"""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:0.3rem;">
  {logo_img_html(38)}
  <div>
    <p class="ek-sidebar-brand">{PRODUCT_SUITE_CN}</p>
    <p class="ek-sidebar-product">智能客服助手</p>
  </div>
</div>
<p class="ek-hint" style="margin:0 0 0.6rem 0;">{html.escape(KB_BRAND_NAME)} · {html.escape(KB_SCENE_DESC)}</p>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # ── 对话 ──
        if st.button("＋ 新对话", type="primary", use_container_width=True):
            new_conversation(st.session_state)
            st.rerun()

        _ids = ordered_session_ids(st.session_state)
        if _ids:
            _cur = st.session_state.current_session_id
            _idx = _ids.index(_cur) if _cur in _ids else 0
            _choice = st.selectbox(
                "历史会话",
                _ids,
                index=_idx,
                format_func=lambda sid: session_label(st.session_state, sid),
                label_visibility="collapsed",
            )
            if _choice != st.session_state.current_session_id:
                persist_from_streamlit(st.session_state, st.session_state.username)
                switch_session(st.session_state, st.session_state.username, _choice)
                st.rerun()

        if st.button("清空当前对话", use_container_width=True):
            st.session_state.messages = []
            _sid = st.session_state.current_session_id
            if _sid in st.session_state.chat_sessions:
                st.session_state.chat_sessions[_sid]["messages"] = []
            persist_from_streamlit(st.session_state, st.session_state.username)
            st.rerun()

        # ── 设置（折叠区） ──
        st.divider()
        with st.expander("⚙ 设置", expanded=False):

            # 账户
            st.markdown("**账户**")
            st.caption(f"账号：`{html.escape(st.session_state.username)}`")
            if st.button("退出登录", use_container_width=True):
                persist_from_streamlit(st.session_state, st.session_state.username)
                _theme_keep = st.session_state.get("theme", "light")
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.session_state.theme = _theme_keep
                st.session_state.authenticated = False
                st.rerun()

            st.divider()

            # 知识库状态
            st.markdown("**知识库**")
            if meta:
                st.success(f"索引正常 · {meta['chunk_count']} 条")
            else:
                st.warning("尚未构建索引")
            st.caption(f"文件 {len(files)} 个 · {describe_active_provider()}")

            st.divider()

            # 文档管理
            st.markdown("**文档管理**")
            st.caption("上传 PDF / Word / MD / TXT，随后重建索引。")
            _up = st.file_uploader(
                "上传文档",
                type=["pdf", "docx", "md", "txt", "markdown"],
                label_visibility="collapsed",
            )
            if _up is not None and st.button("导入并清洗", use_container_width=True, key="btn_import"):
                try:
                    _path = persist_uploaded_document(
                        _up.getvalue(), _up.name, upload_dir
                    )
                    reset_vectorstore_cache()
                    st.success("已保存，请重建索引后生效。")
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
                            st.success(f"完成，{len(_ch)} 段。")
                            st.rerun()
                except Exception as e:
                    st.error(str(e))

            st.divider()

            # 调试
            _debug = st.checkbox("调试模式", value=False, key="ek_debug")
            if _debug:
                st.code(f"KNOWLEDGE_DIR =\n{knowledge_dir}", language="text")
                if meta:
                    st.json(meta)

    return _debug
