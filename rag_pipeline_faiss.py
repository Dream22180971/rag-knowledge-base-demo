"""
RAG 知识库核心模块 (FAISS 优化版)
优化点：批量Embedding、索引缓存、跳过placeholder检查
"""
import os
import json
import time
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
INDEX_DIR = os.path.join(PROJECT_ROOT, "faiss_store")
META_PATH = os.path.join(INDEX_DIR, "meta.json")

# ============================================================
# 1. 文档加载
# ============================================================
def load_documents(directory: str = "./knowledge", progress_callback=None):
    from langchain_community.document_loaders import PyPDFLoader, TextLoader
    import glob
    
    documents = []
    
    # PDF
    pdf_dir = os.path.join(directory, "pdfs")
    if os.path.exists(pdf_dir):
        pdf_files = glob.glob(os.path.join(pdf_dir, "**/*.pdf"), recursive=True)
        for i, f in enumerate(pdf_files):
            try:
                if progress_callback:
                    progress_callback(f"加载 PDF: {os.path.basename(f)}", i/len(pdf_files)*0.3)
                documents.extend(PyPDFLoader(f).load())
            except Exception as e:
                print(f"[!] PDF load failed {f}: {e}")
    
    # MD + TXT
    text_dir = os.path.join(directory, "texts")
    if os.path.exists(text_dir):
        md_files = glob.glob(os.path.join(text_dir, "**/*.md"), recursive=True)
        txt_files = glob.glob(os.path.join(text_dir, "**/*.txt"), recursive=True)
        all_text_files = md_files + txt_files
        for i, f in enumerate(all_text_files):
            try:
                if progress_callback:
                    progress_callback(f"加载文本: {os.path.basename(f)}", 0.3 + i/len(all_text_files)*0.2)
                documents.extend(TextLoader(f, encoding="utf-8").load())
            except Exception as e:
                print(f"[!] Text load failed {f}: {e}")
    
    if progress_callback:
        progress_callback(f"已加载 {len(documents)} 个文档", 0.5)
    return documents


# ============================================================
# 2. 文档切片
# ============================================================
def split_documents(documents, chunk_size=500, chunk_overlap=50, progress_callback=None):
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    if progress_callback:
        progress_callback("正在切分文档...", 0.55)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    if progress_callback:
        progress_callback(f"已切分为 {len(chunks)} 个文本块", 0.6)
    return chunks


# ============================================================
# 3. 向量数据库 - FAISS (带磁盘缓存)
# ============================================================
_vectorstore = None

def _get_embeddings():
    from langchain_community.embeddings import DashScopeEmbeddings
    return DashScopeEmbeddings(
        model=os.getenv("EMBEDDING_MODEL", "text-embedding-v3"),
        dashscope_api_key=os.getenv("DASHSCOPE_API_KEY", "")
    )


def get_vectorstore():
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore
    
    # Try load from disk cache
    if os.path.exists(INDEX_DIR):
        try:
            from langchain_community.vectorstores import FAISS
            embeddings = _get_embeddings()
            _vectorstore = FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
            return _vectorstore
        except Exception as e:
            print(f"[!] cache load failed: {e}")
    
    return None


def build_index(chunks, progress_callback=None):
    global _vectorstore
    
    from langchain_community.vectorstores import FAISS
    embeddings = _get_embeddings()
    
    if progress_callback:
        progress_callback(f"正在计算 {len(chunks)} 个文本块的向量... (约需 {len(chunks)*0.5:.0f} 秒)", 0.65)
    
    t0 = time.time()
    _vectorstore = FAISS.from_documents(chunks, embeddings)
    elapsed = time.time() - t0
    
    if progress_callback:
        progress_callback(f"向量计算完成 ({elapsed:.1f}s)", 0.95)
    
    # Save to disk
    os.makedirs(INDEX_DIR, exist_ok=True)
    _vectorstore.save_local(INDEX_DIR)
    
    # Save metadata
    meta = {
        "chunk_count": len(chunks),
        "built_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "text-embedding-v3"),
        "build_time_sec": round(elapsed, 1)
    }
    with open(META_PATH, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    if progress_callback:
        progress_callback("索引已保存", 1.0)


def get_index_meta():
    if os.path.exists(META_PATH):
        with open(META_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def search(query: str, top_k: int = 4) -> List[dict]:
    vectorstore = get_vectorstore()
    if vectorstore is None:
        return []
    results = vectorstore.similarity_search_with_score(query, k=top_k)
    return [
        {
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
            "score": round(float(score), 4)
        }
        for doc, score in results
    ]


# ============================================================
# 4. RAG 回答生成
# ============================================================
def generate_answer(question: str, context_chunks: List[dict]) -> str:
    from langchain_community.chat_models import ChatTongyi
    from langchain_core.messages import HumanMessage, SystemMessage
    
    context_text = ""
    for i, chunk in enumerate(context_chunks, 1):
        context_text += f"\n[source {i}] ({chunk['source']}):\n{chunk['content']}\n"
    
    system_prompt = """You are a professional knowledge base QA assistant.
Answer based ONLY on the provided reference info. Cite sources like [1][2].
If info is insufficient, say so clearly. Be concise and precise."""

    llm = ChatTongyi(
        model=os.getenv("MODEL_NAME", "qwen-turbo"),
        dashscope_api_key=os.getenv("DASHSCOPE_API_KEY", ""),
        temperature=0.3,
    )
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"References:\n{context_text}\n\nQuestion: {question}")
    ])
    return response.content


# ============================================================
# 5. 完整 RAG 流水线
# ============================================================
def rag_pipeline(question: str, knowledge_dir: str = "./knowledge") -> dict:
    t0 = time.time()
    
    # 1. Get or build index
    vectorstore = get_vectorstore()
    if vectorstore is None:
        docs = load_documents(knowledge_dir)
        if not docs:
            return {"error": "No documents found in knowledge/ directory"}
        chunks = split_documents(docs)
        build_index(chunks)
    
    # 2. Search
    search_results = search(question)
    
    # 3. Generate
    answer = generate_answer(question, search_results)
    
    elapsed = round((time.time() - t0) * 1000)
    return {
        "question": question,
        "answer": answer,
        "sources": search_results,
        "elapsed_ms": elapsed
    }
