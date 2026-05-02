"""
处理 Streamlit 上传：解析 PDF / Word / MD / TXT，经清洗后写入 knowledge/texts/uploads/。
PDF 使用 PyMuPDF + pypdf 双引擎；不含 OCR。
"""
import os
import re
from datetime import datetime

from document_cleaning import clean_text
from text_extract import extract_docx_bytes, extract_pdf_bytes


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
    os.makedirs(dest_dir, exist_ok=True)
    _, ext = os.path.splitext(original_name)
    ext = ext.lower()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = _safe_stem(original_name)

    if ext == ".pdf":
        raw = extract_pdf_bytes(file_bytes)
        text = clean_text(raw)
    elif ext in (".md", ".txt", ".markdown"):
        text = clean_text(file_bytes.decode("utf-8", errors="replace"))
    elif ext == ".docx":
        raw = extract_docx_bytes(file_bytes)
        text = clean_text(raw)
    else:
        raise ValueError("仅支持：.pdf .docx .md .txt .markdown")

    if not text.strip():
        raise ValueError(
            "未能从文件中抽取到可读正文。"
            "若为扫描版 PDF（整页图片）、加密 PDF 或损坏文件，请先导出为可复制文字的 PDF，"
            "或使用 Word/Markdown 文本；本系统不包含 OCR。"
        )

    out_name = f"{ts}_{stem}.md"
    out_path = os.path.join(dest_dir, out_name)
    header = f"<!-- uploaded_from:{original_name} | cleaned_at:{ts} -->\n\n"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(text)

    return out_path
