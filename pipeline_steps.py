"""
RAG 流水线可视化执行步骤组件
在界面上展示 RAG 每一步的执行过程和耗时
"""
import html
from typing import List, Dict, Optional
import streamlit as st


def render_pipeline_steps(steps: List[Dict], total_time_ms: int) -> None:
    """
    渲染 RAG 流水线执行步骤

    steps 格式：
    [
        {
            "name": "步骤名称",
            "status": "done" | "running" | "error",
            "detail": "详细信息",
            "time_ms": 123,
            "icon": "📄"
        }
    ]
    """
    if not steps:
        return

    # 统计信息
    completed = sum(1 for s in steps if s["status"] == "done")
    errors = sum(1 for s in steps if s["status"] == "error")

    # 构建 HTML
    step_items = []
    for i, step in enumerate(steps):
        status = step.get("status", "done")
        name = step.get("name", f"步骤 {i + 1}")
        detail = step.get("detail", "")
        time_ms = step.get("time_ms")
        icon = step.get("icon", "⚙️")

        # 状态样式
        if status == "done":
            status_color = "#10b981"
            status_icon = "✓"
            status_class = "step-done"
        elif status == "running":
            status_color = "#3b82f6"
            status_icon = "⟳"
            status_class = "step-running"
        else:  # error
            status_color = "#ef4444"
            status_icon = "✗"
            status_class = "step-error"

        # 耗时显示
        time_html = ""
        if time_ms is not None:
            if time_ms >= 1000:
                time_text = f"{time_ms / 1000:.1f}s"
            else:
                time_text = f"{time_ms}ms"
            time_html = f'<span class="step-time">{time_text}</span>'

        # 详情显示
        detail_html = ""
        if detail:
            # 截断过长内容
            if len(detail) > 200:
                detail = detail[:200] + "..."
            detail_html = f'<div class="step-detail">{html.escape(detail)}</div>'

        step_items.append(f"""
<div class="step-item {status_class}">
  <div class="step-indicator">
    <span class="step-icon">{icon}</span>
    <span class="step-status-badge" style="background:{status_color}">{status_icon}</span>
  </div>
  <div class="step-content">
    <div class="step-header">
      <span class="step-name">{html.escape(name)}</span>
      {time_html}
    </div>
    {detail_html}
  </div>
</div>
""")

    steps_html = "\n".join(step_items)

    # 耗时颜色
    time_color = "#10b981" if total_time_ms < 3000 else "#f59e0b" if total_time_ms < 5000 else "#ef4444"

    # 状态总结
    if errors > 0:
        summary_text = f"完成 {completed}/{len(steps)} 步 · {errors} 步失败"
        summary_color = "#ef4444"
    else:
        summary_text = f"✓ 全部 {len(steps)} 步完成"
        summary_color = "#10b981"

    full_html = f"""
<style>
.pipeline-steps {{
  background: linear-gradient(145deg, #ffffff 0%, #fafcff 100%);
  border: 1px solid #e8ecf2;
  border-radius: 14px;
  padding: 1rem;
  margin: 0.5rem 0 1rem 0;
  box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
}}
.pipeline-steps-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e8ecf2;
}}
.pipeline-steps-title {{
  font-size: 0.85rem;
  font-weight: 700;
  color: #334155;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}}
.pipeline-steps-summary {{
  font-size: 0.75rem;
  font-weight: 600;
  color: {summary_color};
}}
.pipeline-steps-time {{
  font-size: 0.72rem;
  color: {time_color};
  font-weight: 600;
  padding: 0.25rem 0.6rem;
  background: {time_color}15;
  border-radius: 6px;
}}
.step-item {{
  display: flex;
  gap: 0.75rem;
  padding: 0.6rem 0;
  border-bottom: 1px solid #f1f5f9;
  transition: background 0.15s;
}}
.step-item:last-child {{
  border-bottom: none;
}}
.step-item:hover {{
  background: #f8fafc;
}}
.step-indicator {{
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  width: 32px;
}}
.step-icon {{
  font-size: 1rem;
}}
.step-status-badge {{
  position: absolute;
  top: -4px;
  right: -4px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  color: white;
  font-size: 0.6rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}}
.step-content {{
  flex: 1;
  min-width: 0;
}}
.step-header {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}}
.step-name {{
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e293b;
}}
.step-time {{
  font-size: 0.7rem;
  color: #64748b;
  font-weight: 500;
  background: #f1f5f9;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  flex-shrink: 0;
}}
.step-detail {{
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.3rem;
  line-height: 1.5;
  word-break: break-word;
}}
.step-error .step-name {{
  color: #dc2626;
}}
.step-error .step-detail {{
  color: #dc2626;
  background: #fef2f2;
  padding: 0.4rem;
  border-radius: 6px;
}}
/* 流程图连接线 */
.step-item:not(:last-child) .step-indicator::after {{
  content: '';
  position: absolute;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  width: 2px;
  height: calc(100% - 12px);
  background: linear-gradient(180deg, #e2e8f0 0%, #f1f5f9 100%);
}}
.step-done .step-indicator::after {{
  background: linear-gradient(180deg, #10b981 0%, #d1fae5 100%);
}}
</style>

<div class="pipeline-steps">
  <div class="pipeline-steps-header">
    <span class="pipeline-steps-title">
      <span>🔄</span> 执行流程
    </span>
    <span class="pipeline-steps-summary">{summary_text}</span>
    <span class="pipeline-steps-time">总耗时 {total_time_ms}ms</span>
  </div>
  {steps_html}
</div>
"""
    st.markdown(full_html, unsafe_allow_html=True)


def create_step(
    name: str,
    status: str = "done",
    detail: str = "",
    time_ms: Optional[int] = None,
    icon: str = "⚙️"
) -> Dict:
    """创建步骤对象"""
    return {
        "name": name,
        "status": status,
        "detail": detail,
        "time_ms": time_ms,
        "icon": icon,
    }


# 步骤模板 - RAG 标准流程
STEP_TEMPLATES = {
    "query_analysis": {"name": "查询分析", "icon": "🔍", "detail": "分析用户意图，提取关键词"},
    "history_context": {"name": "对话上下文", "icon": "💬", "detail": "结合历史对话增强检索"},
    "vector_search": {"name": "向量检索", "icon": "🎯", "detail": "在 FAISS 索引中匹配相关文档"},
    "context_merge": {"name": "上下文组装", "icon": "📝", "detail": "整合检索结果，构建 Prompt"},
    "llm_generate": {"name": "LLM 生成", "icon": "🤖", "detail": "调用大模型生成回答"},
    "answer_format": {"name": "结果格式化", "icon": "📋", "detail": "添加引用标注和来源信息"},
}


def render_rag_flow_diagram(current_step: int = 0, total_steps: int = 5) -> None:
    """
    渲染 RAG 流程简图（步骤进度条）

    current_step: 当前执行到第几步 (0-based)
    total_steps: 总步骤数
    """
    steps_html = []
    for i in range(total_steps):
        if i < current_step:
            status = "completed"
            bg = "#10b981"
            icon = "✓"
        elif i == current_step:
            status = "active"
            bg = "#3b82f6"
            icon = "●"
        else:
            status = "pending"
            bg = "#e2e8f0"
            icon = "○"

        steps_html.append(f"""
<div class="flow-step">
  <div class="flow-step-circle" style="background:{bg};box-shadow:0 2px 8px {bg}40">{icon}</div>
  <div class="flow-step-label">{["检索", "分析", "组装", "生成", "格式化"][i] if i < 5 else f"步骤{i+1}"}</div>
</div>
{"" if i == total_steps - 1 else '<div class="flow-step-line" style="background:' + ('#10b981' if i < current_step else '#e2e8f0') + '"></div>'}
""")

    html_content = f"""
<style>
.flow-diagram {{
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem;
  margin: 0.5rem 0;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e8ecf2;
}}
.flow-step {{
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
}}
.flow-step-circle {{
  width: 28px;
  height: 28px;
  border-radius: 50%;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  transition: all 0.3s;
}}
.flow-step-label {{
  font-size: 0.65rem;
  color: #64748b;
  font-weight: 500;
}}
.flow-step-line {{
  width: 40px;
  height: 2px;
  margin: 0 0.2rem;
  margin-bottom: 1rem;
}}
@keyframes pulse {{
  0%, 100% {{ transform: scale(1); }}
  50% {{ transform: scale(1.15); }}
}}
.flow-step:nth-child(1) .flow-step-circle[style*="#3b82f6"] {{
  animation: pulse 1.5s infinite;
}}
</style>

<div class="flow-diagram">
  {"".join(steps_html)}
</div>
"""
    st.markdown(html_content, unsafe_allow_html=True)
