"""
企业级电商知识库 RAG 核心模块（FAISS + DashScope）
文档加载、切片、向量缓存、检索与带引用回答。
"""
import os
import json
import time
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

from config import RAG_TOP_K
from document_cleaning import clean_document_pages
from llm_providers import create_chat_model

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
INDEX_DIR = os.path.join(PROJECT_ROOT, "faiss_store")
META_PATH = os.path.join(INDEX_DIR, "meta.json")

# ============================================================
# 1. 文档加载
# ============================================================
def load_documents(directory: str = "./knowledge", progress_callback=None):
    from langchain_community.document_loaders import TextLoader
    from langchain_core.documents import Document
    import glob

    from text_extract import extract_docx_bytes, extract_pdf_bytes

    documents = []

    # PDF（PyMuPDF + pypdf，优于单一 PyPDFLoader）
    pdf_dir = os.path.join(directory, "pdfs")
    if os.path.exists(pdf_dir):
        pdf_files = glob.glob(os.path.join(pdf_dir, "**/*.pdf"), recursive=True)
        for i, f in enumerate(pdf_files):
            try:
                if progress_callback:
                    progress_callback(f"加载 PDF: {os.path.basename(f)}", i / max(len(pdf_files), 1) * 0.25)
                with open(f, "rb") as fp:
                    raw = fp.read()
                txt = extract_pdf_bytes(raw).strip()
                if txt:
                    documents.append(Document(page_content=txt, metadata={"source": f}))
                else:
                    print(f"[!] PDF 无文本（可能为扫描件）: {f}")
            except Exception as e:
                print(f"[!] PDF load failed {f}: {e}")

    # MD + TXT + DOCX
    text_dir = os.path.join(directory, "texts")
    if os.path.exists(text_dir):
        md_files = glob.glob(os.path.join(text_dir, "**/*.md"), recursive=True)
        txt_files = glob.glob(os.path.join(text_dir, "**/*.txt"), recursive=True)
        docx_files = glob.glob(os.path.join(text_dir, "**/*.docx"), recursive=True)
        all_text_files = md_files + txt_files
        n_txt = len(all_text_files)
        for i, f in enumerate(all_text_files):
            try:
                if progress_callback:
                    progress_callback(
                        f"加载文本: {os.path.basename(f)}",
                        0.28 + i / max(n_txt, 1) * 0.12,
                    )
                documents.extend(TextLoader(f, encoding="utf-8").load())
            except Exception as e:
                print(f"[!] Text load failed {f}: {e}")
        for i, f in enumerate(docx_files):
            try:
                if progress_callback:
                    progress_callback(
                        f"加载 Word: {os.path.basename(f)}",
                        0.4 + i / max(len(docx_files), 1) * 0.1,
                    )
                with open(f, "rb") as fp:
                    txt = extract_docx_bytes(fp.read()).strip()
                if txt:
                    documents.append(Document(page_content=txt, metadata={"source": f}))
            except Exception as e:
                print(f"[!] DOCX load failed {f}: {e}")
    
    if os.getenv("CLEAN_DOCUMENTS_ON_LOAD", "1").strip() not in ("0", "false", "False"):
        documents = clean_document_pages(documents)

    if progress_callback:
        progress_callback(f"已加载 {len(documents)} 个文档（含清洗）", 0.5)
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


def reset_vectorstore_cache():
    """上传新文档后若需丢弃内存中的旧向量实例，可调用（仍需重新构建索引才能入库）。"""
    global _vectorstore
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
        "build_time_sec": round(elapsed, 1),
        "knowledge_profile": "enterprise_ecommerce_demo",
        "llm_provider": os.getenv("LLM_PROVIDER", "aliyun"),
        "clean_documents_on_load": os.getenv("CLEAN_DOCUMENTS_ON_LOAD", "1"),
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


def search(query: str, top_k: int = RAG_TOP_K) -> List[dict]:
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
def generate_answer(
    question: str,
    context_chunks: List[dict],
    chat_history: Optional[List[dict]] = None,
) -> str:
    from langchain_core.messages import HumanMessage, SystemMessage

    context_text = ""
    for i, chunk in enumerate(context_chunks, 1):
        context_text += f"\n[source {i}] ({chunk['source']}):\n{chunk['content']}\n"

    history_block = ""
    if chat_history:
        lines = []
        for m in chat_history[-10:]:
            label = "用户" if m.get("role") == "user" else "助手"
            lines.append(f"{label}：{(m.get('content') or '')[:700]}")
        history_block = "【对话上文（仅用于理解指代与追问，事实必须以参考信息为准）】\n" + "\n".join(lines) + "\n\n"

    system_prompt = """你是企业电商客服知识库助手。请仅根据下方「参考信息」回答「当前用户问题」，不得编造未在参考中出现的价格、时效、电话、链接或政策。
若用户追问中出现「它、上面、刚才」等指代，可结合「对话上文」理解意图，但具体政策与数字只能来自参考信息。
要求：
- 用清晰、专业、礼貌的中文；适当分点说明。
- 在句末或关键结论处用 [1][2] 等形式标注参考来源编号。
- 若参考信息不足以回答，请直接说明「知识库中未找到相关说明」，并建议用户联系人工客服或查看订单页，不要猜测。"""

    llm = create_chat_model()

    human_body = (
        f"{history_block}参考信息：\n{context_text}\n\n当前用户问题：{question}"
    )

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_body),
    ])
    return response.content


# ============================================================
# 5. 完整 RAG 流水线
# ============================================================
def rag_pipeline(
    question: str,
    knowledge_dir: str = "./knowledge",
    chat_history: Optional[List[dict]] = None,
) -> dict:
    t0 = time.time()

    # 1. Get or build index
    vectorstore = get_vectorstore()
    if vectorstore is None:
        docs = load_documents(knowledge_dir)
        if not docs:
            return {"error": "未在 knowledge/ 目录下找到可加载的文档，请检查 knowledge/texts/ 或 knowledge/pdfs/。"}
        chunks = split_documents(docs)
        build_index(chunks)

    # 2. Search（多轮时用「上文摘要 + 当前问」增强检索，便于指代类追问命中）
    retrieval_query = question
    if chat_history:
        tail = chat_history[-4:]
        prefix = "\n".join(
            ("用户" if m.get("role") == "user" else "助手")
            + "："
            + (m.get("content") or "")[:200]
            for m in tail
        )
        retrieval_query = f"{prefix}\n当前问：{question}"[:2000]

    search_results = search(retrieval_query)

    # 3. Generate
    answer = generate_answer(question, search_results, chat_history=chat_history)
    
    elapsed = round((time.time() - t0) * 1000)
    return {
        "question": question,
        "answer": answer,
        "sources": search_results,
        "elapsed_ms": elapsed
    }
