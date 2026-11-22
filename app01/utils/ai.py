# ============================================================
# 模块：大模型统一封装（LLMClient）
# 作用：把大模型封装成"会写字的函数"——传入提示词，返回文字结果。
# ============================================================
from openai import OpenAI
from django.conf import settings


class LLMClient:
    """大模型客户端封装：chat(提示词) -> 文本。"""

    _client = None

    @classmethod
    def _get_client(cls):
        """懒加载：首次调用时才创建客户端，之后复用。"""
        if cls._client is None:
            cls._client = OpenAI(
                api_key=settings.AI_API_KEY,
                base_url=settings.AI_BASE_URL,
            )
        return cls._client

    @classmethod
    def chat(cls, prompt, system=None):
        """单轮对话：发送一条提示词，返回模型回答。"""
        client = cls._get_client()
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        resp = client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=messages,
            temperature=0.7,
        )
        return resp.choices[0].message.content

    @classmethod
    def chat_messages(cls, messages, temperature=0.7):
        """多轮对话：直接传入完整 messages 列表（含历史），返回回答。"""
        client = cls._get_client()
        resp = client.chat.completions.create(
            model=settings.AI_MODEL,
            messages=messages,
            temperature=temperature,
        )
        return resp.choices[0].message.content