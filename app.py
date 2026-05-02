"""
企业级电商知识库问答助手 — Streamlit 控制台（本地调试入口）
支持多轮对话：底部输入框常驻，上文传入模型与检索增强。
"""
import glob
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

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.path.join(PROJECT_ROOT, "knowledge")
UPLOAD_DIR = os.path.join(KNOWLEDGE_DIR, "texts", "uploads")

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    st.header("运维与知识库")
    st.markdown(f"**品牌（演示）** · {KB_BRAND_NAME}")
    st.caption(f"覆盖场景：{KB_SCENE_DESC}")

    meta = get_index_meta()
    if meta:
        st.success(
            f"索引可用 · **{meta['chunk_count']}** 片段 · 构建于 `{meta.get('built_at', '')}`"
        )
    else:
        st.warning("尚未构建向量索引，请先点击下方按钮完成首次索引。")

    files = (
        glob.glob(os.path.join(KNOWLEDGE_DIR, "**/*.md"), recursive=True)
        + glob.glob(os.path.join(KNOWLEDGE_DIR, "**/*.txt"), recursive=True)
        + glob.glob(os.path.join(KNOWLEDGE_DIR, "**/*.pdf"), recursive=True)
    )
    st.caption(f"已扫描知识库文件：**{len(files)}** 个")
    st.caption(describe_active_provider() + " · 向量嵌入：DashScope（换嵌入模型须重建索引）")

    st.divider()
    st.subheader("文档上传（自动清洗）")
    st.caption(
        "支持 PDF / MD / TXT：抽取正文后规范化空白与换行，保存到 `knowledge/texts/uploads/`。"
        "PDF 无 OCR；上传后请 **重新构建索引**。"
    )
    uploaded_file = st.file_uploader(
        "选择文件",
        type=["pdf", "md", "txt", "markdown"],
        accept_multiple_files=False,
        label_visibility="collapsed",
    )
    if uploaded_file is not None and st.button("导入知识库（清洗并保存）", use_container_width=True):
        try:
            saved = persist_uploaded_document(
                uploaded_file.getvalue(),
                uploaded_file.name,
                UPLOAD_DIR,
            )
            reset_vectorstore_cache()
            st.success(
                f"已写入 `{os.path.basename(saved)}`。请点击下方 **重新构建索引** 后新知识方可被检索。"
            )
        except Exception as e:
            st.error(f"导入失败：{e}")

    st.divider()

    if st.button("重新构建索引", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(msg, pct):
            progress_bar.progress(min(int(pct * 100), 100))
            status_text.text(msg)

        try:
            with st.spinner("构建中…"):
                update_progress("扫描文档…", 0)
                docs = load_documents(KNOWLEDGE_DIR, progress_callback=update_progress)
                if not docs:
                    st.warning(f"未加载到任何文档，请检查目录：{KNOWLEDGE_DIR}")
                else:
                    chunks = split_documents(docs, progress_callback=update_progress)
                    build_index(chunks, progress_callback=update_progress)
                    st.success(f"索引完成，共 **{len(chunks)}** 个文本块。")
                    st.rerun()
        except Exception as e:
            st.error(f"构建失败：{e}")

    if st.button("清空会话", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.markdown(
        """
**本地调试步骤**
1. `copy .env.example .env` 并填写 `DASHSCOPE_API_KEY`
2. `pip install -r requirements.txt`
3. `streamlit run app.py` 或双击 `start_app.bat`
4. 首次使用点击 **重新构建索引**
        """
    )

    debug = st.checkbox("调试模式（显示路径与片段预览）", value=False)

    if debug:
        st.code(f"KNOWLEDGE_DIR =\n{KNOWLEDGE_DIR}", language="text")
        if meta:
            st.json(meta)
        if files:
            st.text("文件列表：\n" + "\n".join(os.path.basename(f) for f in sorted(files)))

# ============================================================
# Main
# ============================================================
st.title(f"{PAGE_ICON} {PAGE_TITLE}")
st.caption(
    f"{KB_BRAND_NAME} · LangChain · FAISS · {describe_active_provider()} · "
    f"向量 DashScope · RAG · 多轮对话 · 上传清洗"
)

with st.expander("关于本助手（企业级演示说明）", expanded=False):
    st.markdown(
        f"""
本助手面向 **企业电商客服知识库** 场景：基于 **{KB_BRAND_NAME}** 虚构政策文档进行问答演示，
知识范围限定为已入库的 Markdown（售前、配送退换、售后客诉）。回答须引用库内依据；超出范围时应提示用户转人工。

支持 **连续多轮提问**（如「那不满 99 元呢？」）：底部输入框会始终显示；模型会结合上文理解指代，检索亦会参考最近几轮以提升召回。

侧栏支持 **文档上传 + 自动清洗**（轻量规则，非 OCR）；招聘 JD 中较重的混合检索 / Rerank / 图谱 / 多租户等未在本演示实现，可作为扩展叙述。

**非生产环境**：无账号体系、无工单对接；上线前请替换为真实知识源并完成安全与合规评审。
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

# 先渲染已有对话（仅文本；来源展开仅在当轮生成时展示）
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 当最后一条来自用户、尚未生成助手回复时，在本轮完成 RAG
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_text = st.session_state.messages[-1]["content"]
    history = st.session_state.messages[:-1]

    with st.chat_message("assistant"):
        with st.spinner("检索知识库并生成回答…"):
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
                f"参考来源（{len(result['sources'])} 条）· 相似度分数越低通常越相关（内积/L2 依索引而定）"
            ):
                for i, src in enumerate(result["sources"], 1):
                    preview = src["content"][:500] + (
                        "…" if len(src["content"]) > 500 else ""
                    )
                    st.markdown(
                        f"**[{i}]** `{src['source']}` · score=`{src['score']}`\n\n> {preview}"
                    )
                    st.divider()

            st.caption(f"耗时：{result['elapsed_ms']} ms")

    st.session_state.messages.append({"role": "assistant", "content": response_text})

# 输入框每轮都渲染在底部，保证可连续提问
if prompt := st.chat_input("继续提问，或输入顾客/坐席的问题…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# 空会话时显示快捷示例
if not st.session_state.messages:
    st.divider()
    st.markdown("**示例问题（点击快捷填入）**")
    cols = st.columns(len(example_questions))
    for col, q in zip(cols, example_questions):
        if col.button(q, key=f"ex_{q}"):
            st.session_state.messages.append({"role": "user", "content": q})
            st.rerun()
