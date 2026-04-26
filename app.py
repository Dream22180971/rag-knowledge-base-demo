"""
RAG Knowledge Base QA - Streamlit UI (FAISS)
"""
import os
import streamlit as st
from rag_pipeline_faiss import (
    rag_pipeline, load_documents, split_documents, 
    build_index, get_index_meta, get_vectorstore
)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_DIR = os.path.join(PROJECT_ROOT, "knowledge")

st.set_page_config(
    page_title="RAG 知识库问答",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ============================================================
# Sidebar
# ============================================================
with st.sidebar:
    st.header("📚 知识库管理")
    
    # Show index status
    meta = get_index_meta()
    if meta:
        st.success(f"✅ 索引已就绪 | {meta['chunk_count']} chunks | 构建于 {meta.get('built_at','')}")
    else:
        st.info("⏳ 尚未构建索引，请点击下方按钮")
    
    # Count source files
    import glob
    files = (glob.glob(os.path.join(KNOWLEDGE_DIR, "**/*.md"), recursive=True) +
             glob.glob(os.path.join(KNOWLEDGE_DIR, "**/*.txt"), recursive=True) +
             glob.glob(os.path.join(KNOWLEDGE_DIR, "**/*.pdf"), recursive=True))
    st.caption(f"知识库文件: {len(files)} 个")
    
    st.divider()
    
    if st.button("🔄 重新构建索引", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(msg, pct):
            progress_bar.progress(min(int(pct * 100), 100))
            status_text.text(msg)
        
        try:
            with st.spinner(""):
                update_progress("正在扫描文档...", 0)
                docs = load_documents(KNOWLEDGE_DIR, progress_callback=update_progress)
                
                if not docs:
                    st.warning(f"未找到文档! 路径: {KNOWLEDGE_DIR}")
                else:
                    chunks = split_documents(docs, progress_callback=update_progress)
                    build_index(chunks, progress_callback=update_progress)
                    st.success(f"✅ 完成! {len(chunks)} 个文本块已索引")
                    st.rerun()
        except Exception as e:
            st.error(f"构建失败: {e}")
    
    st.divider()
    st.markdown("""
    ### 使用说明
    1. 放文件到 `knowledge/` 目录
    2. 点「重新构建索引」
    3. 输入问题即可问答
    
    **首次构建较慢** (需调用API算向量)
    之后秒加载
    """)

# ============================================================
# Main
# ============================================================
st.title("📚 RAG 智能知识库问答")
st.caption("LangChain + FAISS + DashScope | 检索增强生成 Demo")

example_questions = [
    "这个产品的核心功能是什么?",
    "退换货政策是怎样的?",
    "如何联系客服?",
    "支持哪些支付方式?",
]

if "messages" not in st.session_state:
    st.session_state.messages = []

# Auto-answer: if last message is from user with no assistant reply, generate one
need_auto_answer = (
    len(st.session_state.messages) > 0 and 
    st.session_state.messages[-1]["role"] == "user" and
    (len(st.session_state.messages) == 1 or st.session_state.messages[-2]["role"] == "assistant")
)
prompt = None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# If the last msg is user and has no assistant reply yet, auto-generate
if need_auto_answer:
    prompt = st.session_state.messages[-1]["content"]
else:
    input_prompt = st.chat_input("请输入你的问题...")
    if input_prompt:
        prompt = input_prompt
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

# Generate answer (from chat_input or example button auto-answer)
if prompt:
    with st.chat_message("assistant"):
        with st.spinner("检索中..."):
            try:
                result = rag_pipeline(prompt, knowledge_dir=KNOWLEDGE_DIR)
            except Exception as e:
                import traceback
                st.error(f"Error: {e}\n\n````\n{traceback.format_exc()}\n````")
                response_text = f"ERROR: {e}"
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                raise  # re-raise so streamlit shows it too
        
        if "error" in result:
            st.error(result["error"])
            response_text = result["error"]
        else:
            st.markdown(result["answer"])
            response_text = result["answer"]
            
            with st.expander(f"Reference ({len(result['sources'])} sources)"):
                for i, src in enumerate(result["sources"], 1):
                    st.markdown(f"**Source {i}** | score: `{src['score']}` | `{src['source']}`\n\n> {src['content'][:300]}")
                    st.divider()
            
            st.caption(f"Time: {result['elapsed_ms']}ms")
    
    st.session_state.messages.append({"role": "assistant", "content": response_text})

if not st.session_state.messages:
    st.divider()
    cols = st.columns(len(example_questions))
    for col, q in zip(cols, example_questions):
        if col.button(q, key=q):
            st.session_state.messages.append({"role": "user", "content": q})
            st.rerun()
