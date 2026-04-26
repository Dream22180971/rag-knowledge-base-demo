"""
RAG 知识库核心模块
实现：文档加载 → 切片 → 向量化存储 → 检索 → 生成回答
"""
import os
from typing import List, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ============================================================
# 1. 文档加载器 - 支持多种格式
# ============================================================
def load_documents(directory: str = "./knowledge"):
    """
    从指定目录加载所有文档（PDF / Markdown / TXT）
    返回 Document 对象列表
    """
    from langchain_community.document_loaders import PyPDFLoader, TextLoader
    from langchain_core.documents import Document
    import glob
    
    documents = []
    
    # 加载 PDF 文件
    pdf_dir = os.path.join(directory, "pdfs")
    if os.path.exists(pdf_dir):
        pdf_files = glob.glob(os.path.join(pdf_dir, "**/*.pdf"), recursive=True)
        for pdf_file in pdf_files:
            try:
                loader = PyPDFLoader(pdf_file)
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"[!] 加载 PDF 失败 {pdf_file}: {e}")
    
    # 加载 Markdown 文件
    text_dir = os.path.join(directory, "texts")
    if os.path.exists(text_dir):
        md_files = glob.glob(os.path.join(text_dir, "**/*.md"), recursive=True)
        for md_file in md_files:
            try:
                loader = TextLoader(md_file, encoding="utf-8")
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"[!] 加载 MD 失败 {md_file}: {e}")
        
        # 加载 TXT 文件
        txt_files = glob.glob(os.path.join(text_dir, "**/*.txt"), recursive=True)
        for txt_file in txt_files:
            try:
                loader = TextLoader(txt_file, encoding="utf-8")
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"[!] 加载 TXT 失败 {txt_file}: {e}")
    
    print(f"[OK] 已加载 {len(documents)} 个文档片段")
    return documents


# ============================================================
# 2. 文档切片 - 智能分块
# ============================================================
def split_documents(documents, chunk_size: int = 500, chunk_overlap: int = 100):
    """
    将文档切分为固定大小的块，保留上下文重叠
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", " ", ""]
    )
    
    chunks = splitter.split_documents(documents)
    print(f"[OK] 已切分为 {len(chunks)} 个文本块")
    return chunks


# ============================================================
# 3. 向量数据库 - 存储与检索
# ============================================================

_vectorstore = None

def get_vectorstore(persist_directory: str = "./chroma_db"):
    """获取或创建向量数据库（单例模式）"""
    global _vectorstore
    
    if _vectorstore is not None:
        return _vectorstore
    
    from langchain_community.embeddings import DashScopeEmbeddings
    from langchain_chroma import Chroma
    
    embeddings = DashScopeEmbeddings(
        model=os.getenv("EMBEDDING_MODEL", "text-embedding-v2"),
        dashscope_api_key=os.getenv("DASHSCOPE_API_KEY", "")
    )
    
    _vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    
    return _vectorstore


def build_index(chunks, persist_directory: str = "./chroma_db"):
    """将文本块构建为向量索引"""
    vectorstore = get_vectorstore(persist_directory)
    vectorstore.add_documents(chunks)
    vectorstore.persist()
    print(f"[OK] 索引构建完成，共 {len(chunks)} 个向量")


def search(query: str, top_k: int = 4) -> List[dict]:
    """
    语义搜索：返回最相关的 k 个文档片段
    每个结果包含：内容、来源文件、相似度分数
    """
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search_with_score(query, k=top_k)
    
    formatted = []
    for doc, score in results:
        formatted.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "未知"),
            "score": round(float(score), 4)
        })
    
    return formatted


# ============================================================
# 4. RAG 回答生成
# ============================================================
def generate_answer(question: str, context_chunks: List[dict]) -> str:
    """
    基于检索到的上下文，调用 LLM 生成回答
    """
    from langchain_community.chat_models import ChatTongyi
    from langchain_core.messages import HumanMessage, SystemMessage
    
    # 构建带引用的 Prompt
    context_text = ""
    for i, chunk in enumerate(context_chunks, 1):
        context_text += f"\n【参考来源 {i}】({chunk['source']}, 相关度: {chunk['score']}):\n{chunk['content']}\n"
    
    system_prompt = """你是一个专业的知识库问答助手。
请根据以下参考信息回答用户的问题。

规则：
1. 只基于提供的参考信息回答，不要编造内容
2. 如果参考信息不足以回答问题，请明确说明
3. 回答时标注引用来源，如 [来源1][来源2]
4. 使用简洁清晰的中文回答
5. 如果是技术问题，尽量给出具体步骤或代码示例"""

    llm = ChatTongyi(
        model=os.getenv("MODEL_NAME", "qwen-turbo"),
        dashscope_api_key=os.getenv("DASHSCOPE_API_KEY", ""),
        temperature=0.3,
    )
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"参考信息：\n{context_text}\n\n用户问题：{question}")
    ]
    
    response = llm.invoke(messages)
    return response.content


# ============================================================
# 5. 完整 RAG 流水线（一键调用）
# ============================================================
def rag_pipeline(question: str, knowledge_dir: str = "./knowledge") -> dict:
    """
    完整 RAG 流程：加载 → 切片 → 检索 → 生成
    返回完整结果字典
    """
    import time
    start_time = time.time()
    
    # 1. 确保索引存在
    vectorstore = get_vectorstore()
    collection_count = vectorstore._collection.count()
    
    if collection_count == 0:
        print("[!] 知识库为空，正在构建索引...")
        docs = load_documents(knowledge_dir)
        if not docs:
            return {"error": "知识库中没有找到任何文档，请在 knowledge/ 目录下放入 PDF 或 MD 文件"}
        chunks = split_documents(docs)
        build_index(chunks)
    
    # 2. 检索相关片段
    search_results = search(question)
    
    # 3. 生成回答
    answer = generate_answer(question, search_results)
    
    elapsed = round((time.time() - start_time) * 1000)
    
    return {
        "question": question,
        "answer": answer,
        "sources": search_results,
        "elapsed_ms": elapsed
    }
