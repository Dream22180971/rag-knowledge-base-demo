# 🛒 企业级电商知识库问答助手

> 基于 **LangChain + FAISS + DashScope（通义）+ Streamlit** 的检索增强生成（RAG）演示  
> 场景：**电商售前 / 订单支付 / 配送退换 / 售后客诉**（当前知识库为虚构品牌「云栖杂货铺」政策文档，仅供学习与演示）

## ✨ 功能特性

- **品牌与导航**：内联 SVG 品牌标、顶栏状态、侧栏按 **外观 / 账户与组织 / 会话 / 知识域 / 文档 / 帮助** 分区
- **简易登录**：首屏登录（默认账号密码见 `.env.example` 的 `DEMO_USERNAME` / `DEMO_PASSWORD`，未配置时 `demo` / `demo`）
- **多会话与历史**：「新对话」、**历史会话**下拉切换；会话列表按用户持久化到本地 `data/sessions_*.json`（演示级，非多机同步）
- **深色 / 浅色**：侧栏一键切换主题（含主区、侧栏、聊天气泡联动样式）
- **多格式文档**：`knowledge/texts/` 下 Markdown、TXT、**Word docx**；`knowledge/pdfs/` 下 PDF（可选）
- **上传 + 自动清洗**：侧栏上传 **PDF / Word(docx) / MD / TXT**，规则清洗后写入 `texts/uploads/`。PDF 使用 **PyMuPDF + pypdf** 双引擎抽取（优于单一 PyPDF）；**扫描版整图 PDF 仍可能无文字层**，需 OCR 或先导出可复制文本的 PDF（本仓库不含 OCR）
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

### 2. 配置环境变量

```bash
copy .env.example .env
```

编辑 `.env`：

- **登录（演示）**：`DEMO_USERNAME` / `DEMO_PASSWORD`（可省略，默认 `demo` / `demo`）
- **索引与嵌入**（必需）：`DASHSCOPE_API_KEY=你的_KEY`

对话模型默认走阿里通义；若改用智谱 / Moonshot / 方舟等，见 `.env.example` 内注释。

获取 DashScope Key：[阿里云 DashScope 控制台](https://dashscope.console.aliyun.com/)

### 3. 启动应用

```bash
streamlit run app.py
```

Windows 可双击 `start_app.bat`。浏览器访问 `http://localhost:8501`，**先登录**再使用控制台。

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
├── app.py                  # 主入口：登录门闸 + 问答
├── auth_ui.py              # 登录页
├── session_manager.py      # 多会话与本地持久化
├── sidebar_ui.py           # 侧栏分区 UI
├── brand_assets.py         # 品牌 SVG 与内联图
├── assets/logo_icon.svg    # 页签图标
├── config.py               # 品牌与检索参数
├── document_cleaning.py
├── text_extract.py
├── upload_handler.py
├── ui_styles.py            # 主题（浅/深）
├── llm_providers.py
├── rag_pipeline_faiss.py
├── data/                   # 会话 JSON（.gitignore）
├── knowledge/
│   └── texts/ …
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

## 📋 面试高频问答（结合本项目）

以下为与本仓库实现强相关的问答，便于面试时结合项目说明「做了什么、为什么这么做、还能怎么改」。

### RAG 与整体流程

**Q：什么是 RAG？和直接用大模型有什么区别？**  
**A：** RAG（Retrieval-Augmented Generation）是「先检索相关知识，再让模型基于检索结果生成答案」。区别：纯 LLM 依赖训练记忆，易过时或幻觉；RAG 把企业文档切块入库，回答时先查库再生成，更可控、可溯源。本项目在 `rag_pipeline_faiss.py` 中完成嵌入检索 + 拼上下文 + 调用 `llm_providers.create_chat_model()` 生成带引用回答。

**Q：请描述用户提问后，系统内部大致经历了哪些步骤？**  
**A：** 用户问题 → DashScope 文本嵌入 → 本地 FAISS 相似度检索 Top-K → 将检索块与用户问题（及多轮历史）拼进提示词 → 配置的 Chat 模型生成回答 → 返回 `answer`、`sources`（含片段与分数）、耗时等。索引文件落在 `faiss_store/`，元数据见 `meta.json`。

**Q：检索用的向量是怎么来的？和对话模型是同一个吗？**  
**A：** 向量由 **DashScope Embedding**（如 `text-embedding-v3`）对切片文本计算；对话生成模型通过 `LLM_PROVIDER` 等环境变量在 `llm_providers.py` 中切换（通义 / 智谱 / OpenAI 兼容等）。两者职责不同：嵌入固定用于检索；**换嵌入模型必须重建索引**，否则维度不一致。

### 向量库与召回

**Q：为什么选 FAISS 而不是 Milvus / pgvector？**  
**A：** 本仓库面向单机演示与 Windows 友好部署：FAISS 轻量、无额外服务、易持久化到本地目录。规模化或多租户生产可再评估 Milvus、pgvector、云向量库等。

**Q：Top-K 在本项目里如何配置？调大调小有什么影响？**  
**A：** 环境变量 `RAG_TOP_K`（默认 4，见 `config.py`）。K 大：上下文更全，但噪声与 token 增加、延迟上升；K 小：更聚焦，可能漏召回。需结合文档粒度与业务评测调参。

**Q：文档切片用的是什么策略？`chunk_overlap` 有什么用？**  
**A：** `RecursiveCharacterTextSplitter`，默认约 500 字块长、50 字重叠，分隔符含中英文标点与换行。重叠是为了避免关键句恰好在切块边界被截断，提高相邻块连贯性。

### 幻觉、引用与提示词

**Q：如何减轻「胡说八道」？项目里具体做了什么？**  
**A：** 系统提示要求模型**仅依据检索到的片段**作答，并输出 `[1][2]` 类引用；检索不足或无关时要求明确说明。仍可能出现表述不当，需结合人工抽检与评测集（本仓库未建自动化评测）。

**Q：为什么要展示「参考来源」？**  
**A：** 便于客服/运营核对依据、排查错误召回，也是企业场景的可审计性与可信度的基础能力。

### 多轮对话与前后端

**Q：多轮追问如何实现？和单轮检索有什么不同？**  
**A：** `app.py` 将历史消息传入 `rag_pipeline(..., chat_history=history)`，检索阶段可把上文与当前问句拼接成检索 query，缓解指代不明（如「那包邮呢？」）。具体拼接逻辑见 `rag_pipeline_faiss.py`。

**Q：多会话、历史列表是如何保存的？**  
**A：** `session_manager.py` 将各会话消息树序列化到 `data/sessions_<用户名>.json`（目录已 gitignore），属于单机演示级持久化，非分布式会话存储。

**Q：Streamlit 在本项目中的角色？有什么局限？**  
**A：** 快速搭建登录门闸、侧栏运维（索引重建、上传）、聊天 UI。局限是单体脚本式模型、并发与自定义前端能力不如独立前后端分离方案；适合 Demo/MVP，不等于生产客服系统架构。

### 文档工程

**Q：支持哪些格式？PDF 为什么有时「抽不出字」？**  
**A：** 支持 MD、TXT、DOCX，PDF 经 **PyMuPDF + pypdf** 抽取。若为扫描版 PDF（整页图片、无文字层），无法直接抽取，需要 OCR 或先换成可复制文本的 PDF；本仓库不包含 OCR 流水线。

**Q：上传新文档后为什么要点「重建索引」？**  
**A：** 向量只在构建索引时写入 FAISS；仅保存文件不会自动增量更新向量库（未实现增量索引管线）。

### LangChain 与模块职责

**Q：本项目里 LangChain 具体用在哪些地方？**  
**A：** 典型用法包括：`Document` 承载页内容与 `metadata.source`；`TextLoader` 读 MD/TXT；`RecursiveCharacterTextSplitter` 切片；`DashScopeEmbeddings` 算向量；`FAISS.from_documents` / `load_local` 建库与持久化；`ChatTongyi` 等与 `SystemMessage`/`HumanMessage` 做带上下文的 `invoke`。业务编排主要在自写的 `rag_pipeline_faiss.py`，而非全套 Agent 框架。

**Q：`rag_pipeline.py` 和 `rag_pipeline_faiss.py` 是什么关系？**  
**A：** 主应用入口使用 **`rag_pipeline_faiss.py`**（FAISS + DashScope 嵌入 + 可切换对话模型）。若仓库中另有 `rag_pipeline.py`，多为早期或其它后端路径；面试说明以实际 `app.py` import 为准。

**Q：为什么要 `allow_dangerous_deserialization=True` 加载 FAISS？**  
**A：** LangChain 在反序列化本地向量库时为避免任意代码执行风险，默认较保守；信任本地自建的 `faiss_store/` 目录时可开启。生产应将索引文件权限收紧，且索引生成管线可信。

### 相似度、检索与典型失效

**Q：FAISS 返回的 `score` 数字越大越好还是越小越好？**  
**A：** 需看距离度量。本项目通过 `similarity_search_with_score` 取回分数，**具体单调性与向量实现相关**；排查召回时可对比同一 query 下多条结果的相对排序，而不是只看绝对值。面试可答：以「能否把正确段落排进 Top-K」为准，必要时做 Bad Case 分析。

**Q：纯向量检索有什么局限？**  
**A：** 语义相近≠业务上正确（领域术语、编号、条款号）；用户用词与文档用词不一致时可能漏召；长文档切块后单块信息不完整。改进方向：混合检索（BM25 + 向量）、同义词/别名表、Rerank、调整切块策略。

**Q：内存里的 `_vectorstore` 缓存什么时候要清？**  
**A：** `reset_vectorstore_cache()` 用于上传新文件后丢弃内存中的旧 `FAISS` 实例；**仍须重新构建索引**才能把新文档写入磁盘向量库，二者缺一不可。

### 提示词、温度与模型行为

**Q：`LLM_TEMPERATURE` 在本项目中如何影响回答？**  
**A：** `llm_providers.py` 将温度传给各 Chat 模型。温度**低**（如 0.3）回答更稳、更贴近检索表述；**高**则更发散，客服场景通常偏低以减少编造风险。

**Q：系统提示里为什么强调「事实只能来自参考信息」却还让模型读「对话上文」？**  
**A：** 上文用于**消解指代**（「刚才说的退货」指什么），不用于捏造事实；`generate_answer` 里把历史截断到最近若干条并限制长度，避免挤占参考片段上下文。

### 数据清洗、成本与安全

**Q：`document_cleaning.py` 大致做什么？为什么要清洗？**  
**A：** 对正文做 NFKC、空白与换行规范化等（与上传清洗一致），减少无意义字符对嵌入与检索的干扰。可通过 `CLEAN_DOCUMENTS_ON_LOAD=0` 关闭加载时清洗（见 `rag_pipeline_faiss` 与 `.env` 说明）。

**Q：调用 DashScope 会产生哪些费用？如何控制？**  
**A：** 构建索引时对**每个切片**做 Embedding API 调用；问答时对 **query 嵌入**（若走向量检索路径）+ **对话生成**计费。控制手段：减少文档冗余、合理切块 size、缓存索引、限流与配额、选合适模型档位；本仓库未实现服务端限流。

**Q：演示登录与 API Key 有什么安全风险？**  
**A：** 默认 `demo/demo` 仅适合本地/内网演示；**不要把真实 `.env` 提交到 Git**（应用 `.gitignore`）。生产需 SSO、RBAC、密钥托管（Vault/KMS）、审计日志；侧栏「租户」当前为占位，未做真正多租户隔离。

### 工程排错与运维意识

**Q：索引构建或问答时报 401 / InvalidApiKey 一般是什么问题？**  
**A：** `DASHSCOPE_API_KEY` 未配置、复制错误、或账号权限/欠费。对话模型若切到其它厂商，还需对应厂商的 Key 与 `LLM_PROVIDER` 配置一致。

**Q：「未找到文档」或检索始终为空，你会怎么查？**  
**A：** 检查 `knowledge/texts/`、`knowledge/pdfs/` 路径与格式；看侧栏调试模式与 `meta.json`；确认已重建索引；PDF 是否扫描件无文字层。

**Q：更换嵌入模型后旧索引还能用吗？**  
**A：** **不能直接用**。不同嵌入模型向量维度或空间不一致，应删除（或整体替换）`faiss_store/` 后重新构建。

### RAG 与其它范式对比

**Q：RAG 和 Fine-tuning 怎么选？**  
**A：** Fine-tuning 适合固化风格或领域表达；知识频繁变更时更适合 RAG 或「RAG + 轻量微调」。本项目走纯 RAG，知识更新靠换文档 + 重建索引。

**Q：为什么不做 Agent（工具调用 / ReAct）？**  
**A：** 当前场景是**封闭域文档问答**，检索 + 生成即可闭环。Agent 更适合需查 API、下单、多工具编排的流程；引入后复杂度和故障面上升，Demo 阶段未采用。

### 开放题（可结合「扩展方向」回答）

**Q：如果要把本项目推向生产，你会优先改哪三点？**  
**A：** 示例回答方向：混合检索（关键词 + 向量）与 Rerank；鉴权、多租户与审计；观测与评测（召回率、幻觉抽检、延迟与成本）。与 README 中「扩展方向」一节对应。

**Q：如何评测 RAG 效果？**  
**A：** 准备领域问答集；指标可包括：命中率（正确文档是否进 Top-K）、回答准确率、引用是否正确、拒答是否合理等；本仓库侧重工程串联，评测集与报表需自行补充。

**Q：如何做增量索引，避免每次全量重建？**  
**A：** 思路：对新文档单独切块嵌入后写入向量库（或按文档 ID 维护版本），删除过期 chunk；需处理一致性、失败回滚与元数据同步。本仓库为简化演示采用全量重建。

**Q：并发上来以后 Streamlit 单进程不够，怎么演进架构？**  
**A：** 将检索与生成做成 **无状态 API 服务**（FastAPI 等），向量库换共享存储（Milvus/pgvector），会话与鉴权走网关；前端可保留 Streamlit  prototype 或换 Web/桌面客户端。关键是把「索引读写」与「模型调用」从脚本中拆出。

---

**作者**：seanwalter (Dream22180971)  
**日期**：2026年5月  
**GitHub**：https://github.com/Dream22180971/rag-knowledge-base-demo
