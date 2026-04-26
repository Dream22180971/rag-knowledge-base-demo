# 📚 RAG 智能知识库问答系统

> 基于 **LangChain + FAISS + DashScope + Streamlit** 的检索增强生成（RAG）演示项目  
> 面试作品 — 对标「AI 智能体搭建 Agent」岗位 JD

## ✨ 功能特性

- 📄 **多格式文档支持**：PDF、Markdown、TXT 自动加载
- 🔪 **智能文档切片**：基于语义的递归分块，保留上下文
- 🔍 **语义向量检索**：FAISS 向量数据库，相似度精确匹配
- 💬 **引用来源标注**：每条回答标注参考文档和置信度
- 🌐 **Web 可视化界面**：Streamlit 聊天式 UI，手机端友好
- ⚡ **一键部署**：3 步启动，无需复杂配置
- 💾 **索引缓存**：首次构建后持久化，后续秒级启动

## 🏗 技术架构

```
用户提问 → 向量检索(FAISS) → 获取相关片段 → LLM生成回答(带引用)
```

| 模块 | 技术 | 说明 |
|------|------|------|
| 文档加载 | LangChain DirectoryLoader | PDF/MD/TXT 多格式 |
| 文本切片 | RecursiveCharacterTextSplitter | 500字符/块，50重叠 |
| 向量化 | DashScope Embeddings (text-embedding-v3) | 1536维语义向量 |
| 向量存储 | FAISS + pickle | 本地持久化缓存 |
| LLM | DashScope Chat (qwen-turbo) | 回答生成 |
| 前端 UI | Streamlit Chat Interface | 移动端适配 |

## 🚀 快速开始（3 步）

### 第 1 步：安装依赖

```bash
pip install -r requirements.txt
```

### 第 2 步：配置 API Key

```bash
# 复制环境变量模板
copy .env.example .env

# 编辑 .env，填入你的 DashScope API Key
DASHSCOPE_API_KEY=sk-your-api-key-here
```

> 💡 **DashScope 获取地址**：https://dashscope.console.aliyun.com/  
> 新用户赠送额度足够跑通 Demo

### 第 3 步：运行

```bash
streamlit run app.py
# 或双击 start_app.bat
```

浏览器自动打开 `http://localhost:8501`，即可体验！

## 📁 项目结构

```
rag-knowledge-base-demo/
├── app.py                  # Streamlit Web 主界面
├── rag_pipeline_faiss.py  # RAG 核心逻辑（加载/切片/检索/生成）
├── requirements.txt        # Python 依赖
├── .env                   # 环境变量（API Key）
├── .env.example           # 环境变量模板
├── .gitignore             # Git 忽略配置
├── start_app.bat          # Windows 一键启动脚本
├── knowledge/             # 📂 知识库文档目录
│   └── texts/             # Markdown / TXT 文件（放入即可）
│       ├── product_faq.md
│       ├── shipping_policy.md
│       └── ai_agent_intro.md
└── README.md              # 本文件
```

## 🎯 使用流程

1. **放入文档**：将你的知识文档放到 `knowledge/texts/`（支持 MD、TXT）
2. **构建索引**：点击侧边栏「🔄 重新构建索引」按钮
3. **开始问答**：在聊天框输入问题，系统自动检索 + 生成回答
4. **查看来源**：展开「📎 参考来源」查看检索到的原文片段

## 💡 核心代码说明

### RAG 流水线（rag_pipeline_faiss.py）

```python
from rag_pipeline_faiss import RAGPipeline

# 初始化（如有缓存则秒级加载）
rag = RAGPipeline()

# 一键调用完整 RAG 流程
result = rag.query("如何申请退货？")

print(result["answer"])       # 生成的回答
print(result["sources"])      # 参考来源列表
print(result["elapsed_ms"]) # 耗时（毫秒）
```

### 四个核心函数

| 函数 | 作用 |
|------|------|
| `load_documents()` | 从 knowledge/ 目录加载所有文档 |
| `split_documents()` | 智能切片为固定大小文本块 |
| `build_index()` | 构建 FAISS 向量索引 |
| `search(query)` | 语义向量搜索，返回 Top-K 相关片段 |
| `generate_answer(q, ctx)` | 基于 Prompt + 上下文调用 LLM 生成回答 |

### 索引缓存机制

首次构建索引后会自动保存到 `faiss_index.pkl`，下次启动自动加载，无需重新调用 Embedding API。

```python
# 强制重新构建索引
rag = RAGPipeline(force_rebuild=True)
```

## 🔧 技术难点与解决方案（面试话术）

### 1. 向量数据库选型

**问题**：ChromaDB 在 Windows 环境调用 `add_documents()` 时进程被 SIGKILL 终止

**排查过程**：
- 尝试不同版本的 langchain_chroma、chromadb
- 直接调用原始 chromadb 库同样崩溃
- 怀疑是 Windows 兼容性问题

**解决方案**：切换到 FAISS（Facebook AI Similarity Search）
- 纯 Python 实现，跨平台兼容性好
- 支持 `save_local()` / `load_local()` 持久化
- 性能相当，功能完全满足需求

### 2. Embedding 速度优化

**问题**：text-embedding-v2 API 调用慢（每个 chunk 1-2 秒）

**解决方案**：升级到 `text-embedding-v3`
- 速度提升约 3 倍
- 维度增加到 1536 维，语义表示更丰富

### 3. 文档切片策略

**问题**：切太大会丢失精度，切太小会丢失上下文

**解决方案**：RecursiveCharacterTextSplitter
- 按段落→句子→词的层级递归切割
- chunk_size=500, chunk_overlap=50（10% 重叠保证连续性）
- 保留原始文档的结构信息

### 4. Prompt 工程

**问题**：LLM 可能产生幻觉，回答超出知识库范围

**解决方案**：结构化 System Prompt
```
你是一个基于知识库的问答助手。请只根据以下参考信息回答用户问题，不要编造内容。

参考信息：
{context}

请在回答时标注来源。
```

## 🎨 界面预览

### 主界面 - 聊天问答

![RAG Demo UI](screenshot.png)

### 侧边栏 - 知识库管理

- 显示索引状态（已索引 xx 个文档块）
- 「🔄 重新构建索引」按钮
- 使用说明

## 📝 面试话术要点

> **Q: 为什么用 FAISS 而不是 Chroma？**
>
> A: 项目开发初期尝试了 ChromaDB，但在 Windows 环境稳定性存在问题的背景下，选择了更稳定且功能等价的 FAISS 作为替代。两个工具在向量检索的核心功能上是等价的，FAISS 在跨平台兼容性上更有优势。

> **Q: 项目的技术难点在哪里？**
>
> A: 主要有三个挑战：
> 1. **文档切片策略**：用 RecursiveCharacterTextSplitter 实现层级递归切割，设置 10% 重叠保证上下文连续性
> 2. **检索质量调优**：通过调整 chunk_size 和 top_k 参数平衡召回率和精确度
> 3. **索引缓存**：首次构建后持久化，避免重复调用 Embedding API

> **Q: 如果数据量大了怎么处理？**
>
> A: 当前用 FAISS 本地存储适合百万级以下向量。如果量级更大，可以迁移到 Milvus、Pinecone 等分布式向量数据库，或者使用 FAISS 的 GPU 加速版本。

## 🔜 扩展方向

- [ ] 支持 Word/Excel 文档解析
- [ ] 多轮对话 + 上下文记忆
- [ ] 对接企业微信/钉钉 Bot
- [ ] 添加文档权限管理
- [ ] 支持多知识库切换
- [ ] 添加对话日志与分析
- [ ] 部署到云服务器（Docker）

---

*本项目作为 AI Agent 岗位面试作品开发*

**作者**：seanwalter (Dream22180971)  
**日期**：2026年4月  
**GitHub**：https://github.com/Dream22180971/rag-knowledge-base-demo