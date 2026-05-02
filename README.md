# 🛒 企业级电商知识库问答助手

> 基于 **LangChain + FAISS + DashScope（通义）+ Streamlit** 的检索增强生成（RAG）演示  
> 场景：**电商售前 / 订单支付 / 配送退换 / 售后客诉**（当前知识库为虚构品牌「云栖杂货铺」政策文档，仅供学习与演示）

## ✨ 功能特性

- **多格式文档**：`knowledge/texts/` 下 Markdown、TXT；`knowledge/pdfs/` 下 PDF（可选）
- **上传 + 自动清洗**：侧栏上传 PDF/MD/TXT，经规则清洗后写入 `knowledge/texts/uploads/`（无 OCR，复杂版式不还原）
- **加载时清洗**：`load_documents` 默认对正文做与上传一致的轻量清洗（`CLEAN_DOCUMENTS_ON_LOAD=0` 可关）
- **多厂商对话模型**：`llm_providers` 统一入口，默认 **阿里通义**；可切换智谱、月之暗面（OpenAI 兼容）、**字节方舟/豆包等**（`LLM_PROVIDER=openai_compatible` + 兼容 Base URL）。**向量嵌入仍固定 DashScope**，换嵌入须重建索引
- **递归切片**：`RecursiveCharacterTextSplitter`，控制块大小与重叠以平衡召回
- **语义检索**：FAISS 本地向量库，Top-K 可调；多轮追问时对检索 query 做上文拼接
- **带引用回答**：中文客服话术 + 来源编号，多轮指代
- **运维侧栏**：索引状态、上传、一键重建、调试模式
- **索引持久化**：`faiss_store/` 已加入 `.gitignore`；本地上传 md 默认不提交（`uploads/*` 已忽略，保留 `.gitkeep`）

## 🏗 技术架构

```
顾客/坐席提问 → DashScope 嵌入 → FAISS 检索 Top-K → 拼上下文 → 可配置 LLM（默认通义）→ 带引用回答
```

| 模块 | 技术 | 说明 |
|------|------|------|
| 配置 | `config.py`、`.env` | 品牌、`RAG_TOP_K`、`LLM_PROVIDER` |
| 清洗 | `document_cleaning.py` | NFKC、空白与换行规范化 |
| 上传 | `upload_handler.py` | 写入 `texts/uploads/` |
| 文档加载 | `TextLoader` / `PyPDFLoader` | 扫描 `texts/`、`pdfs/` |
| 切片 | `RecursiveCharacterTextSplitter` | 默认 500 字 / 50 字重叠 |
| 向量 | DashScope `text-embedding-v3` | **当前固定**；换模型须重建索引 |
| 向量库 | FAISS | `faiss_store/` |
| 生成 | `llm_providers.create_chat_model()` | 默认 `ChatTongyi`；见 `.env.example` |

## 🚀 本地启动与调试

### 1. 环境与依赖

```bash
cd rag-knowledge-base-demo
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
copy .env.example .env
```

编辑 `.env`，**索引与嵌入**至少填写：

```env
DASHSCOPE_API_KEY=你的_KEY
```

对话模型默认走阿里通义（同上 Key）；若改用智谱 / Moonshot / 方舟等，见 `.env.example` 内注释。

获取 DashScope Key：[阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/)

### 3. 启动应用

```bash
streamlit run app.py
```

Windows 可双击 `start_app.bat`。浏览器访问 `http://localhost:8501`。

### 4. 首次索引

打开侧栏，点击 **「重新构建索引」**（会调用 Embedding API，产生少量费用）。之后同一目录下启动将直接加载 `faiss_store/`，无需重复构建。

### 5. 调试建议

- 勾选侧栏 **「调试模式」**：查看 `KNOWLEDGE_DIR`、`meta.json` 内容、已扫描文件名。
- 修改 `knowledge/` 内文档后，务必 **重新构建索引**。
- 更换 `EMBEDDING_MODEL` 后，旧索引与新模型维度不一致，请删除本地 `faiss_store/` 目录后再构建。
- **上传新文档后**必须再次点击 **「重新构建索引」**，否则检索仍用旧向量。

## 📁 项目结构

```
rag-knowledge-base-demo/
├── app.py                  # Streamlit 主界面
├── config.py               # 品牌与检索参数
├── document_cleaning.py    # 文本清洗
├── upload_handler.py       # 上传落盘
├── ui_styles.py            # 企业级界面 CSS 与顶栏 HTML
├── llm_providers.py        # 对话模型工厂（默认通义）
├── rag_pipeline_faiss.py   # RAG 流水线
├── requirements.txt
├── .env.example
├── .gitignore
├── start_app.bat
├── knowledge/
│   └── texts/
│       ├── *.md            # 内置「云栖杂货铺」三篇
│       └── uploads/        # 侧栏上传生成（默认 git 忽略内容）
└── README.md
```

## 💡 代码调用示例

```python
from rag_pipeline_faiss import rag_pipeline

result = rag_pipeline("满多少元包邮？", knowledge_dir="./knowledge")
print(result["answer"])
print(result["sources"])
print(result["elapsed_ms"])
```

## 🎨 界面预览

主界面为宽屏聊天布局；侧栏提供索引运维与调试开关。若仓库中含 `screenshot.png`，可作为演示配图更新截图。

## 🔧 技术说明摘要

- **为何 FAISS**：轻量、本地持久化友好，适合 Windows 开发与单体部署原型。
- **幻觉控制**：系统提示要求仅依据检索片段作答，并标注 `[1][2]`；不足时明确说明。
- **扩展**：更大规模可换 Milvus / pgvector；生产环境需接入权限、审计与工单，而非本演示范围。

## 🔜 扩展方向（招聘 JD 里较重、本仓库刻意未做）

- [ ] 混合检索（BM25 + 向量）、Cross-Encoder Rerank
- [ ] 系统化评测集与命中率 / 幻觉率报表
- [ ] Word / Excel / OCR、图谱与多租户
- [ ] 对接 IM / 工单、Docker 生产部署

---

**作者**：seanwalter (Dream22180971)  
**日期**：2026年5月  
**GitHub**：https://github.com/Dream22180971/rag-knowledge-base-demo
