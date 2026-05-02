"""
对话模型工厂：默认阿里通义（DashScope），其余国产厂商通过配置接入。

约定：
- 向量嵌入当前仍固定 DashScope（与知识库索引一致）；换嵌入模型须重建索引。
- 「智谱 / 月之暗面 / 字节方舟」等：优先使用各厂商官方 LangChain 封装或 OpenAI 兼容网关；
  未填 Key 时请保持 LLM_PROVIDER=aliyun。
"""
import os
from typing import Any


def create_chat_model() -> Any:
    """返回 LangChain 风格的 Chat 模型（统一支持 invoke）。"""
    provider = os.getenv("LLM_PROVIDER", "aliyun").lower().strip()
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))

    if provider in ("aliyun", "dashscope", "tongyi", "qwen"):
        from langchain_community.chat_models import ChatTongyi

        return ChatTongyi(
            model=os.getenv("MODEL_NAME", "qwen-turbo"),
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY", ""),
            temperature=temperature,
        )

    if provider in ("zhipu", "glm", "chatglm"):
        try:
            from langchain_community.chat_models import ChatZhipuAI
        except ImportError as e:
            raise ImportError(
                "智谱模型需要当前版本的 langchain-community 包含 ChatZhipuAI；"
                "或改用 LLM_PROVIDER=openai_compatible 配合智谱 OpenAI 兼容地址。"
            ) from e
        return ChatZhipuAI(
            api_key=os.getenv("ZHIPU_API_KEY", ""),
            model=os.getenv("ZHIPU_MODEL", "glm-4"),
            temperature=temperature,
        )

    if provider in ("moonshot", "kimi"):
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            api_key=os.getenv("MOONSHOT_API_KEY", ""),
            base_url=os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.cn/v1"),
            model=os.getenv("MOONSHOT_MODEL", "moonshot-v1-8k"),
            temperature=temperature,
        )

    if provider in ("openai_compatible", "compatible", "custom", "ark", "doubao"):
        # 字节方舟 / 豆包 / 其它国产 OpenAI 兼容网关：在 .env 填 BASE_URL + KEY + MODEL
        from langchain_openai import ChatOpenAI

        base = os.getenv("OPENAI_COMPATIBLE_BASE_URL", "").strip()
        key = os.getenv("OPENAI_COMPATIBLE_API_KEY", "").strip()
        model = os.getenv("OPENAI_COMPATIBLE_MODEL", "").strip()
        if not base or not key or not model:
            raise ValueError(
                "LLM_PROVIDER=openai_compatible 时需配置 OPENAI_COMPATIBLE_BASE_URL、"
                "OPENAI_COMPATIBLE_API_KEY、OPENAI_COMPATIBLE_MODEL"
            )
        return ChatOpenAI(
            api_key=key,
            base_url=base,
            model=model,
            temperature=temperature,
        )

    raise ValueError(
        f"未知 LLM_PROVIDER={provider!r}。可选：aliyun | zhipu | moonshot | openai_compatible"
    )


def describe_active_provider() -> str:
    """侧栏展示用短文案。"""
    p = os.getenv("LLM_PROVIDER", "aliyun").lower().strip()
    if p in ("aliyun", "dashscope", "tongyi", "qwen"):
        return f"对话：阿里通义 ({os.getenv('MODEL_NAME', 'qwen-turbo')})"
    if p in ("zhipu", "glm", "chatglm"):
        return f"对话：智谱 ({os.getenv('ZHIPU_MODEL', 'glm-4')})"
    if p in ("moonshot", "kimi"):
        return f"对话：月之暗面 ({os.getenv('MOONSHOT_MODEL', 'moonshot-v1-8k')})"
    if p in ("openai_compatible", "compatible", "custom", "ark", "doubao"):
        return f"对话：OpenAI兼容 ({os.getenv('OPENAI_COMPATIBLE_MODEL', '')})"
    return f"对话：{p}"
