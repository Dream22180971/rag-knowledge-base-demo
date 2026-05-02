"""
处理 Streamlit 上传：解析 PDF/MD/TXT，经清洗后写入 knowledge/texts/uploads/。
"""
import os
import re
from datetime import datetime

from document_cleaning import clean_text


def _safe_stem(name: str, max_len: int = 80) -> str:
    base = os.path.basename(name)
    stem, _ = os.path.splitext(base)
    stem = re.sub(r"[^\w\u4e00-\u9fff._-]", "_", stem).strip("_")
    return (stem or "upload")[:max_len]


def persist_uploaded_document(file_bytes: bytes, original_name: str, dest_dir: str) -> str:
    """
    将上传内容清洗后保存为 UTF-8 Markdown。
    返回写入的文件绝对路径。
    """
    from langchain_community.document_loaders import PyPDFLoader

    os.makedirs(dest_dir, exist_ok=True)
    _, ext = os.path.splitext(original_name)
    ext = ext.lower()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = _safe_stem(original_name)

    if ext == ".pdf":
        tmp = os.path.join(dest_dir, f"_tmp_{ts}.pdf")
        try:
            with open(tmp, "wb") as f:
                f.write(file_bytes)
            docs = PyPDFLoader(tmp).load()
        finally:
            if os.path.isfile(tmp):
                os.remove(tmp)
        parts = [clean_text(d.page_content) for d in docs]
        text = "\n\n".join(p for p in parts if p)
    elif ext in (".md", ".txt", ".markdown"):
        text = file_bytes.decode("utf-8", errors="replace")
        text = clean_text(text)
    else:
        raise ValueError("仅支持扩展名：.pdf .md .txt .markdown")

    if not text:
        raise ValueError("清洗后正文为空，请检查文件是否损坏或仅含图片（当前不支持 OCR）。")

    out_name = f"{ts}_{stem}.md"
    out_path = os.path.join(dest_dir, out_name)
    header = f"<!-- uploaded_from:{original_name} | cleaned_at:{ts} -->\n\n"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(text)

    return out_path
