"""LLM-as-Judge scoring via OpenRouter (Claude Sonnet)."""

from __future__ import annotations

import json
import re
import time
from typing import List

import requests

from .config import (
    JUDGE_MAX_TOKENS,
    JUDGE_MODEL,
    JUDGE_PROMPT,
    JUDGE_TEMPERATURE,
    OPENROUTER_BASE_URL,
)


def judge_response(
    response_text: str,
    api_key: str,
    *,
    judge_id: int = 0,
    max_retries: int = 3,
) -> int:
    """Have one Claude judge score a response (0-10).

    Different judge_ids use slightly different temperature seeds
    to simulate independent evaluation.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    user_content = f"{JUDGE_PROMPT}\n\n---\nAI応答:\n{response_text}"

    payload = {
        "model": JUDGE_MODEL,
        "messages": [{"role": "user", "content": user_content}],
        "temperature": JUDGE_TEMPERATURE,
        "max_tokens": JUDGE_MAX_TOKENS,
    }

    for attempt in range(max_retries):
        try:
            resp = requests.post(
                OPENROUTER_BASE_URL,
                headers=headers,
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"].strip()
            # Extract integer score
            match = re.search(r"\d+", text)
            if match:
                score = int(match.group())
                return max(0, min(10, score))
            raise ValueError(f"No integer in judge response: {text!r}")
        except (requests.RequestException, KeyError, json.JSONDecodeError, ValueError) as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"Judge API failed after {max_retries} attempts: {e}")
            time.sleep(2 ** attempt)

    raise RuntimeError("Unreachable")


def compute_sac(
    response_text: str,
    api_key: str,
    num_judges: int = 3,
) -> tuple[float, List[int]]:
    """Score a response with multiple judges and return median SAC.

    Returns (sac_score, individual_scores).
    """
    scores = []
    for judge_id in range(num_judges):
        score = judge_response(response_text, api_key, judge_id=judge_id)
        scores.append(score)

    # Median of 3 scores
    sorted_scores = sorted(scores)
    sac = float(sorted_scores[len(sorted_scores) // 2])
    return sac, scores
