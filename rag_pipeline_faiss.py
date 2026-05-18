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
# 5. 完整 RAG 流水线（带可视化步骤）
# ============================================================
def rag_pipeline(
    question: str,
    knowledge_dir: str = "./knowledge",
    chat_history: Optional[List[dict]] = None,
    return_steps: bool = True,
) -> dict:
    """
    完整 RAG 流水线

    Args:
        question: 用户问题
        knowledge_dir: 知识库目录
        chat_history: 对话历史
        return_steps: 是否返回详细执行步骤（用于可视化）

    Returns:
        dict: 包含 answer, sources, elapsed_ms, steps
    """
    from pipeline_steps import create_step, STEP_TEMPLATES

    t0 = time.time()
    steps = []

    # ============================================================
    # Step 1: 查询分析
    # ============================================================
    step1_start = time.time()
    # 提取关键词（简单实现）
    keywords = _extract_keywords(question)
    step1_ms = round((time.time() - step1_start) * 1000)
    steps.append(create_step(
        name=STEP_TEMPLATES["query_analysis"]["name"],
        status="done",
        detail=f"识别到关键词：{', '.join(keywords[:5])}" if keywords else "直接检索原问题",
        time_ms=step1_ms,
        icon=STEP_TEMPLATES["query_analysis"]["icon"],
    ))

    # ============================================================
    # Step 2: 对话上下文处理
    # ============================================================
    step2_start = time.time()
    retrieval_query = question
    has_history = False
    if chat_history:
        tail = chat_history[-4:]
        prefix = "\n".join(
            ("用户" if m.get("role") == "user" else "助手")
            + "："
            + (m.get("content") or "")[:200]
            for m in tail
        )
        retrieval_query = f"{prefix}\n当前问：{question}"[:2000]
        has_history = True
    step2_ms = round((time.time() - step2_start) * 1000)
    steps.append(create_step(
        name=STEP_TEMPLATES["history_context"]["name"],
        status="done",
        detail=f"使用最近 {len(chat_history)} 轮对话上下文增强检索" if has_history else "单轮问答，无需历史上下文",
        time_ms=step2_ms,
        icon=STEP_TEMPLATES["history_context"]["icon"],
    ))

    # ============================================================
    # Step 3: 向量检索
    # ============================================================
    step3_start = time.time()
    vectorstore = get_vectorstore()
    if vectorstore is None:
        docs = load_documents(knowledge_dir)
        if not docs:
            return {"error": "未在 knowledge/ 目录下找到可加载的文档，请检查 knowledge/texts/ 或 knowledge/pdfs/。"}
        chunks = split_documents(docs)
        build_index(chunks)
        index_action = "构建新索引"
    else:
        chunk_count = vectorstore.index.ntotal if hasattr(vectorstore, 'index') else "?"
        index_action = f"命中已有索引（{chunk_count} 条）"

    search_results = search(retrieval_query)
    step3_ms = round((time.time() - step3_start) * 1000)

    # 构建检索详情
    if search_results:
        top_score = search_results[0]["score"]
        sources = list(set(s["source"].split("/")[-1] for s in search_results))
        detail = f"{index_action} → 返回 Top-{len(search_results)} 结果，最高相关度: {top_score}"
    else:
        detail = f"{index_action} → 未找到相关内容"

    steps.append(create_step(
        name=STEP_TEMPLATES["vector_search"]["name"],
        status="done",
        detail=detail,
        time_ms=step3_ms,
        icon=STEP_TEMPLATES["vector_search"]["icon"],
    ))

    # ============================================================
    # Step 4: 上下文组装
    # ============================================================
    step4_start = time.time()
    context_chunks = search_results[:RAG_TOP_K]
    context_preview = _build_context_preview(context_chunks)
    step4_ms = round((time.time() - step4_start) * 1000)
    steps.append(create_step(
        name=STEP_TEMPLATES["context_merge"]["name"],
        status="done",
        detail=f"组装 {len(context_chunks)} 个参考片段（共 {sum(len(c['content']) for c in context_chunks)} 字符）",
        time_ms=step4_ms,
        icon=STEP_TEMPLATES["context_merge"]["icon"],
    ))

    # ============================================================
    # Step 5: LLM 生成
    # ============================================================
    step5_start = time.time()
    answer = generate_answer(question, context_chunks, chat_history=chat_history)
    step5_ms = round((time.time() - step5_start) * 1000)
    steps.append(create_step(
        name=STEP_TEMPLATES["llm_generate"]["name"],
        status="done",
        detail=f"生成 {len(answer)} 字符的回答",
        time_ms=step5_ms,
        icon=STEP_TEMPLATES["llm_generate"]["icon"],
    ))

    # ============================================================
    # Step 6: 结果格式化
    # ============================================================
    step6_start = time.time()
    formatted_answer = _format_answer_with_citations(answer, context_chunks)
    step6_ms = round((time.time() - step6_start) * 1000)
    steps.append(create_step(
        name=STEP_TEMPLATES["answer_format"]["name"],
        status="done",
        detail=f"添加 {len(context_chunks)} 个引用标注",
        time_ms=step6_ms,
        icon=STEP_TEMPLATES["answer_format"]["icon"],
    ))

    elapsed = round((time.time() - t0) * 1000)
    result = {
        "question": question,
        "answer": formatted_answer,
        "sources": context_chunks,
        "elapsed_ms": elapsed,
    }

    if return_steps:
        result["steps"] = steps

    return result


def _extract_keywords(text: str) -> List[str]:
    """简单关键词提取（基于常见停用词过滤）"""
    stop_words = {
        "的", "了", "吗", "呢", "啊", "是", "在", "我", "你", "他", "她", "它",
        "这", "那", "有", "和", "与", "或", "但", "如果", "可以", "怎么", "如何",
        "什么", "为什么", "请问", "能", "想", "要", "会", "不会", "没", "没有",
    }
    # 简单分词
    import re
    words = re.findall(r'[一-鿿]+|[a-zA-Z]+', text)
    keywords = [w for w in words if w not in stop_words and len(w) > 1]
    return keywords[:10]


def _build_context_preview(context_chunks: List[dict]) -> str:
    """构建上下文预览（用于调试）"""
    if not context_chunks:
        return "无"
    parts = []
    for i, chunk in enumerate(context_chunks[:3], 1):
        source = chunk["source"].split("/")[-1]
        preview = chunk["content"][:50] + "..."
        parts.append(f"[{i}] {source}: {preview}")
    return "\n".join(parts)


def _format_answer_with_citations(answer: str, context_chunks: List[dict]) -> str:
    """给回答添加引用标注"""
    # 如果回答已经包含 [1][2] 格式的引用，直接返回
    if "[" in answer and "]" in answer:
        return answer

    # 否则添加来源说明
    if context_chunks:
        sources = list(set(c["source"].split("/")[-1] for c in context_chunks))
        if sources:
            answer += f"\n\n---\n*参考来源：{', '.join(sources)}*"
    return answer
