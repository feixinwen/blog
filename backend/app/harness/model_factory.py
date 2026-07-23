"""模型工厂 — 统一管理 LLM 实例，避免每个节点重复初始化。"""

import logging
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)

# 加载 .env（优先级：backend/.env > 项目根目录 > cwd）
for _path in [
    Path(__file__).resolve().parents[1] / ".env",       # backend/.env
    Path(__file__).resolve().parents[3] / ".env",       # 项目根目录
    Path.cwd() / ".env",                                # 当前工作目录
]:
    if _path.exists():
        load_dotenv(_path)
        logger.info("已加载环境变量: %s", _path)
        break


@lru_cache
def _base_config() -> dict:
    return {
        "api_key": os.getenv("QWEN_API_KEY", ""),
        "base_url": os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        "model": os.getenv("QWEN_MODEL", "qwen-plus"),
    }


def get_chat_model(*, temperature: float = 0.7, streaming: bool = False) -> ChatOpenAI:
    """通用聊天模型。"""
    cfg = _base_config()
    return ChatOpenAI(
        model=cfg["model"],
        api_key=cfg["api_key"],
        base_url=cfg["base_url"],
        temperature=temperature,
        streaming=streaming,
    )


def get_classifier_model() -> ChatOpenAI:
    """意图分类专用模型（温度 0，保证稳定结果）。"""
    return get_chat_model(temperature=0)


def get_requirement_model() -> ChatOpenAI:
    """需求分析专用模型（温度 0，结构化输出）。"""
    return get_chat_model(temperature=0)
