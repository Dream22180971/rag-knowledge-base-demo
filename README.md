# RAG 智能知识库问答

> 把文档扔进去，AI 自动从你的知识库里找答案——支持 PDF、Markdown、TXT，3 步跑起来。

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![LangChain](https://img.shields.io/badge/LangChain-0.3-1C3C3C?style=flat)](https://langchain.com)
[![FAISS](https://img.shields.io/badge/FAISS-Facebook-blue?style=flat)](https://faiss.ai/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=flat&logo=streamlit)](https://streamlit.io)

<img width="1920" height="911" alt="RAG Demo 主界面" src="https://github.com/user-attachments/assets/1a199acc-8c4d-4692-9cf8-d0858d9cf4a7" />

---

## 目录

- [它是什么](#它是什么)
- [为什么做](#为什么做)
- [核心功能](#核心功能)
- [快速开始](#快速开始)
- [使用流程](#使用流程)
- [技术架构](#技术架构)
- [技术难点](#技术难点)
- [Roadmap](#roadmap)
- [FAQ](#faq)
- [谁适合用](#谁适合用)
- [关于我](#关于我)

---

## 它是什么

一个**基于 RAG 技术的知识库问答系统**，帮你做三件事：

1. **上传文档**：PDF、Markdown、TXT，扔进去就行
2. **智能问答**：问它任何问题，AI 从文档里找到相关内容再回答
3. **查看来源**：每条回答都标注参考文档和置信度，不怕 AI 胡说

不需要训练模型，不需要写代码，3 步就能跑起来。

---

## 为什么做

ChatGPT 很强，但它不知道你公司的内部文档、你写的笔记、你的知识库。

用大模型做知识库问答，核心问题是：**怎么让 AI 基于你的文档回答，而不是瞎编？**

RAG（检索增强生成）就是解决这个问题的——先从文档里找到相关内容，再让 AI 基于这些内容回答。

这个项目把 RAG 的完整链路跑通了：文档加载 → 切片 → 向量化 → 检索 → 生成，还加了可视化执行步骤，让你看到每一步在干什么。

---

## 核心功能

| 你能做什么 | 说明 |
|-----------|------|
| **多格式文档** | PDF、Markdown、TXT 自动加载 |
| **智能切片** | 按语义递归切割，保留上下文 |
| **向量检索** | FAISS 语义搜索，精确匹配相关内容 |
| **引用标注** | 每条回答标注参考文档和置信度 |
| **可视化流水线** | 实时展示 RAG 每步执行状态和耗时 |
| **索引缓存** | 首次构建后持久化，后续秒级启动 |

---

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key
copy .env.example .env
# 编辑 .env，填入 DashScope API Key
# 获取地址：https://dashscope.console.aliyun.com/

# 3. 启动
streamlit run app.py
```

浏览器自动打开 `http://localhost:8501`，即可体验。

---

## 使用流程

1. **放入文档**：将知识文档放到 `knowledge/texts/`（支持 MD、TXT）或 `knowledge/pdfs/`
2. **构建索引**：点击侧边栏「重新构建索引」
3. **开始问答**：在聊天框输入问题，系统自动检索 + 生成回答
4. **查看来源**：展开「参考来源」查看检索到的原文片段

---

## 技术架构

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

### 可视化执行步骤

每次问答都会展示 RAG 流水线的完整执行过程：

```
🔄 执行流程                          ✓ 全部 6 步完成          总耗时 3200ms
─────────────────────────────────────────────────────────────────────────
🔍 查询分析                          2ms
   识别到关键词：如何, 退货, 申请
─────────────────────────────────────────────────────────────────────────
🎯 向量检索                          450ms
   命中已有索引（32 条） → 返回 Top-4 结果
─────────────────────────────────────────────────────────────────────────
🤖 LLM 生成                          2800ms
   生成 256 字符的回答
```

---

## 技术难点

### 1. 向量数据库选型

ChromaDB 在 Windows 环境不稳定，切换到 FAISS 后问题解决。FAISS 跨平台兼容性好，支持本地持久化，性能满足需求。

### 2. 文档切片策略

切太大会丢失精度，切太小会丢失上下文。用 `RecursiveCharacterTextSplitter` 按段落→句子→词递归切割，10% 重叠保证连续性。

### 3. 索引缓存

首次构建索引后自动保存到 `faiss_index.pkl`，下次启动自动加载，避免重复调用 Embedding API。

```python
# 强制重新构建索引
rag = RAGPipeline(force_rebuild=True)
```

---

## Roadmap

- [x] 多格式文档支持（PDF/MD/TXT）
- [x] FAISS 向量检索
- [x] 可视化执行流水线
- [x] 索引缓存机制
- [ ] 支持 Word/Excel 文档解析
- [ ] 多轮对话 + 上下文记忆
- [ ] 对接企业微信/钉钉 Bot
- [ ] 支持多知识库切换
- [ ] 部署到云服务器（Docker）

---

## FAQ

**Q: 需要 GPU 吗？**
A: 不需要。Embedding 和 LLM 都通过 DashScope API 调用，本地只跑 Streamlit 和 FAISS。

**Q: 支持多少文档？**
A: FAISS 本地存储适合百万级以下向量。量级更大可以迁移到 Milvus、Pinecone 等分布式向量数据库。

**Q: 没有 DashScope API Key 能用吗？**
A: 不能。这个项目依赖 DashScope 的 Embedding 和 Chat 模型。

**Q: 回答不准怎么办？**
A: 检查文档切片是否合理，调整 `chunk_size` 和 `top_k` 参数。可视化流水线能帮你定位问题。

---

## 谁适合用

- **想学 RAG 的人**：从文档加载到向量检索的完整链路，适合入门
- **面试准备者**：RAG + LangChain + FAISS 的实战项目，有面试话术
- **需要内部知识库的团队**：直接拿去改，接入自己的文档
- **Python 开发者**：Streamlit + LangChain 的集成参考

---

## 关于我

我是**肖恩沃尔特**（Sean Walter），一个从测试工程师正在转型为 AI 独立开发者的程序员。

这个项目是我学习 RAG 技术的练兵场——把"文档加载 → 切片 → 向量化 → 检索 → 生成"的完整链路跑通，还加了可视化方便调试和演示。

- GitHub: [Dream22180971](https://github.com/Dream22180971)
- Twitter/X: [@sean_walter0717](https://x.com/sean_walter0717)
- 博客: [seanwalter.top](https://seanwalter.top)

---

## License

[MIT](./LICENSE)
