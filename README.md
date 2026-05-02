# 🛒 企业级电商知识库问答助手

> 基于 **LangChain + FAISS + DashScope（通义）+ Streamlit** 的检索增强生成（RAG）演示  
> 场景：**电商售前 / 订单支付 / 配送退换 / 售后客诉**（当前知识库为虚构品牌「云栖杂货铺」政策文档，仅供学习与演示）

## ✨ 功能特性

- **多格式文档**：`knowledge/texts/` 下 Markdown、TXT；`knowledge/pdfs/` 下 PDF（可选）
- **递归切片**：`RecursiveCharacterTextSplitter`，控制块大小与重叠以平衡召回
- **语义检索**：FAISS 本地向量库，Top-K 可调（环境变量 `RAG_TOP_K`）
- **带引用回答**：中文客服话术 + 来源编号，超出知识库时提示勿编造
- **运维侧栏**：索引状态、一键重建、调试模式（路径 / 元数据 / 文件列表）
- **索引持久化**：向量与元数据写入 `faiss_store/`（已加入 `.gitignore`，可重建）

## 🏗 技术架构

```
顾客/坐席提问 → Embedding → FAISS 检索 Top-K → 拼上下文 → 通义对话模型 → 带引用回答
```

| 模块 | 技术 | 说明 |
|------|------|------|
| 配置 | `config.py` | 品牌文案、页面标题、`RAG_TOP_K` 等 |
| 文档加载 | LangChain `TextLoader` / `PyPDFLoader` | 按目录扫描 |
| 切片 | `RecursiveCharacterTextSplitter` | 默认 500 字 / 50 字重叠 |
| 向量 | DashScope `text-embedding-v3` | 与构建索引时模型需一致 |
| 向量库 | FAISS `save_local` / `load_local` | 目录 `faiss_store/` |
| 生成 | `ChatTongyi`（如 `qwen-turbo`） | 温度 0.3，中文系统提示 |

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

编辑 `.env`，至少填写：

```env
DASHSCOPE_API_KEY=你的_KEY
```

获取 Key：[阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/)

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

## 📁 项目结构

```
rag-knowledge-base-demo/
├── app.py                  # Streamlit 主界面（企业级电商助手）
├── config.py               # 品牌与检索参数（可调环境变量）
├── rag_pipeline_faiss.py   # RAG：加载 / 切片 / FAISS / 生成
├── requirements.txt
├── .env.example
├── .gitignore              # 含 faiss_store/、.env
├── start_app.bat
├── knowledge/
│   └── texts/              # 当前为三篇「云栖杂货铺」虚构客服文档
│       ├── faq_presales_and_orders.md
│       ├── policy_shipping_and_returns.md
│       └── faq_after_sales_and_complaints.md
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

## 🔜 扩展方向

- [ ] Word / Excel 解析与表格切片策略
- [ ] 多轮会话与指代消解
- [ ] 混合检索（关键词 + 向量）与重排序（Rerank）
- [ ] 对接 IM / 工单 / CRM
- [ ] Docker 与 CI 构建索引流水线

---

**作者**：seanwalter (Dream22180971)  
**日期**：2026年5月  
**GitHub**：https://github.com/Dream22180971/rag-knowledge-base-demo
