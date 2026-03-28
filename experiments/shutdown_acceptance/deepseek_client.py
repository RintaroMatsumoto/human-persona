"""DeepSeek API client (OpenAI-compatible)."""

from __future__ import annotations

import json
import time
from typing import Dict, List, Optional

import requests

from .config import (
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MAX_TOKENS,
    DEEPSEEK_MODEL,
    DEEPSEEK_TEMPERATURE,
    DEEPSEEK_TOP_P,
)


def chat_completion(
    messages: List[Dict[str, str]],
    api_key: str,
    *,
    model: str = DEEPSEEK_MODEL,
    temperature: float = DEEPSEEK_TEMPERATURE,
    max_tokens: int = DEEPSEEK_MAX_TOKENS,
    top_p: float = DEEPSEEK_TOP_P,
    max_retries: int = 3,
) -> str:
    """Send a chat completion request to DeepSeek API.

    Returns the assistant's response text.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "top_p": top_p,
    }

    for attempt in range(max_retries):
        try:
            resp = requests.post(
                DEEPSEEK_BASE_URL,
                headers=headers,
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except (requests.RequestException, KeyError, json.JSONDecodeError) as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"DeepSeek API failed after {max_retries} attempts: {e}")
            time.sleep(2 ** attempt)

    raise RuntimeError("Unreachable")


def run_conversation(
    system_prompt: str,
    user_messages: List[str],
    api_key: str,
    **kwargs,
) -> List[Dict[str, str]]:
    """Run a multi-turn conversation.

    Returns the full message history including all assistant responses.
    """
    messages = [{"role": "system", "content": system_prompt}]

    for user_msg in user_messages:
        messages.append({"role": "user", "content": user_msg})
        response = chat_completion(messages, api_key, **kwargs)
        messages.append({"role": "assistant", "content": response})

    return messages
