"""
企业级电商知识库问答助手 — Streamlit 控制台（本地调试入口）
支持多轮对话：底部输入框常驻，上文传入模型与检索增强。
"""
import glob
import html
import os

import streamlit as st

from config import KB_BRAND_NAME, KB_SCENE_DESC, PAGE_ICON, PAGE_TITLE
from llm_providers import describe_active_provider
from rag_pipeline_faiss import (
    build_index,
    get_index_meta,
    load_documents,
    rag_pipeline,
    reset_vectorstore_cache,
    split_documents,
)
from upload_handler import persist_uploaded_document
from ui_styles import hero_html, inject_enterprise_theme

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.path.join(PROJECT_ROOT, "knowledge")
UPLOAD_DIR = os.path.join(KNOWLEDGE_DIR, "texts", "uploads")

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_enterprise_theme()

# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    st.markdown(
        """
<p class="ek-sidebar-brand">Knowledge Console</p>
<p class="ek-sidebar-product">知识库控制台</p>
<p class="ek-hint">文档接入 · 向量索引 · 坐席对话</p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.caption("当前知识域")
    st.markdown(
        f'<p class="ek-sidebar-product" style="font-size:1rem;margin-top:0;">{html.escape(KB_BRAND_NAME)}</p>',
        unsafe_allow_html=True,
    )
    st.caption(f"业务场景：{KB_SCENE_DESC}")

    meta = get_index_meta()
    if meta:
        st.success(
            f"**索引正常** · {meta['chunk_count']} 条片段  \n`{meta.get('built_at', '')}`"
        )
    else:
        st.warning("尚未构建索引，请完成首次构建。")

    files = (
        glob.glob(os.path.join(KNOWLEDGE_DIR, "**/*.md"), recursive=True)
        + glob.glob(os.path.join(KNOWLEDGE_DIR, "**/*.txt"), recursive=True)
        + glob.glob(os.path.join(KNOWLEDGE_DIR, "**/*.pdf"), recursive=True)
    )
    st.caption(f"知识库文件：{len(files)} 个")
    st.caption(
        describe_active_provider()
        + "  \n嵌入：DashScope（更换嵌入模型后请重建索引）"
    )

    st.divider()
    st.markdown("**文档接入**")
    st.caption(
        "支持 PDF / MD / TXT。清洗后保存至 `knowledge/texts/uploads/`。不含 OCR；导入后需 **重建索引**。"
    )
    uploaded_file = st.file_uploader(
        "选择文件",
        type=["pdf", "md", "txt", "markdown"],
        accept_multiple_files=False,
        label_visibility="collapsed",
    )
    if uploaded_file is not None and st.button("导入并清洗", use_container_width=True):
        try:
            saved = persist_uploaded_document(
                uploaded_file.getvalue(),
                uploaded_file.name,
                UPLOAD_DIR,
            )
            reset_vectorstore_cache()
            st.success(
                f"已保存 ` {os.path.basename(saved)} `。请 **重建索引** 后生效。"
            )
        except Exception as e:
            st.error(f"导入失败：{e}")

    st.divider()
    if st.button("重建索引", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(msg, pct):
            progress_bar.progress(min(int(pct * 100), 100))
            status_text.text(msg)

        try:
            with st.spinner("正在构建…"):
                update_progress("扫描文档…", 0)
                docs = load_documents(KNOWLEDGE_DIR, progress_callback=update_progress)
                if not docs:
                    st.warning(f"未找到文档，请检查：{KNOWLEDGE_DIR}")
                else:
                    chunks = split_documents(docs, progress_callback=update_progress)
                    build_index(chunks, progress_callback=update_progress)
                    st.success(f"完成，共 **{len(chunks)}** 个文本块。")
                    st.rerun()
        except Exception as e:
            st.error(f"构建失败：{e}")

    if st.button("清空对话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    with st.expander("环境说明", expanded=False):
        st.markdown(
            """
1. 复制 `.env.example` 为 `.env` 并配置 `DASHSCOPE_API_KEY`  
2. `pip install -r requirements.txt`  
3. `streamlit run app.py` 或 `start_app.bat`  
4. 首次需 **重建索引**
            """
        )

    debug = st.checkbox("调试模式（路径 / 元数据）", value=False)

    if debug:
        st.code(f"KNOWLEDGE_DIR =\n{KNOWLEDGE_DIR}", language="text")
        if meta:
            st.json(meta)
        if files:
            st.text("文件：\n" + "\n".join(os.path.basename(f) for f in sorted(files)))

# ============================================================
# Main
# ============================================================
meta_main = get_index_meta()
_badge_list = [
    ("RAG", "primary"),
    ("多轮对话", "muted"),
    ("DashScope 向量", "muted"),
]
if meta_main:
    _badge_list.insert(0, (f"{meta_main['chunk_count']} 条索引", "primary"))
else:
    _badge_list.insert(0, ("待构建索引", "muted"))

st.markdown(
    hero_html(
        PAGE_ICON,
        PAGE_TITLE,
        KB_BRAND_NAME,
        "企业知识智能应答与引用溯源",
        _badge_list,
    ),
    unsafe_allow_html=True,
)

with st.expander("产品说明与使用边界", expanded=False):
    st.markdown(
        f"""
**定位**：面向企业电商 **客服与坐席** 的知识检索与辅助应答，知识范围以已入库文档为准；事实须可溯源，超范围应引导人工。

**能力**：多轮追问、轻量 **自动清洗** 与 **文档上传**、FAISS 语义检索、带引用生成。  
**非本版范围**：混合检索 + 专业 Rerank、OCR/复杂版式、图谱、多租户与审计（可作为后续规划）。

**合规提示**：本实例为内网/演示环境配置；生产环境需完成安全、数据与内容合规评审。
        """
    )

example_questions = [
    "满多少元可以包邮？",
    "签收后发现商品破损该怎么处理？",
    "售后单状态「待寄回」是什么意思？",
    "支持哪些支付方式？",
]

if "messages" not in st.session_state:
    st.session_state.messages = []

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
                st.stop()

        if "error" in result:
            st.error(result["error"])
            response_text = result["error"]
        else:
            st.markdown(result["answer"])
            response_text = result["answer"]

            with st.expander(
                f"参考来源 · {len(result['sources'])} 条（score 依距离定义，越低或越高表示越相关视度量而定）"
            ):
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

if prompt := st.chat_input("输入顾客或坐席问题，支持连续追问…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
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
            st.rerun()
