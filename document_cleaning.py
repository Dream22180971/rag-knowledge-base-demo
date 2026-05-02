"""
文档自动清洗：规范化空白与换行、Unicode 标准化，提升切片与检索稳定性。
（不含 OCR / 复杂版面还原；招聘 JD 中「难做的」部分刻意不做。）
"""
import re
import unicodedata
from typing import List

from langchain_core.documents import Document


def clean_text(text: str) -> str:
    if not text:
        return ""
    t = unicodedata.normalize("NFKC", text)
    t = re.sub(r"\r\n?", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    t = re.sub(r"[ \t\u3000]+", " ", t)
    t = re.sub(r"\n[ \t]+", "\n", t)
    return t.strip()


def clean_document_pages(documents: List[Document]) -> List[Document]:
    """对 LangChain Document 列表逐页清洗，过滤空页。"""
    out: List[Document] = []
    for d in documents:
        c = clean_text(d.page_content)
        if not c:
            continue
        meta = dict(d.metadata) if d.metadata else {}
        meta["cleaned"] = True
        out.append(Document(page_content=c, metadata=meta))
    return out
