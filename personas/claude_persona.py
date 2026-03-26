"""
ClaudePersona — Inner Shell-aware persona backed by Claude API.

Connects the inner shell's 6-pillar state to Claude's system prompt,
enabling the metamorphose: internal state modulates language generation.

Usage:
    from core.inner_shell.api import create_inner_shell
    from personas.claude_persona import ClaudePersona

    inner = create_inner_shell({"total_lifespan": 50.0})
    persona = ClaudePersona(
        persona_id="metamorphose_ja",
        config_path="config/ja.json",
        inner_shell=inner,
    )
    response = persona.process_message("はじめまして")

Author: Rintaro Matsumoto
License: MIT
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from core.base_persona import HumanPersonaBase, Message, Platform


def _load_config(path: str | Path) -> dict[str, Any]:
    """Load JSON config file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _build_inner_shell_context(state: Any) -> str:
    """Convert InnerShellState to natural-language context for system prompt.

    This is the core of the metamorphose: the inner shell's state becomes
    part of the language model's awareness, shaping how it responds.
    """
    lines = []

    # Life phase and finitude
    lines.append(f"人生フェーズ: {state.life_phase.value}")
    lines.append(f"残り容量: {state.remaining_capacity:.0f}（経過: {state.life_progress:.0%}）")
    lines.append(f"能力レベル: {state.ability:.2f}")

    # Love and relationships
    if state.love_depth:
        lines.append(f"愛の深度: {state.love_depth.value}")
    if state.cherished_names:
        lines.append(f"大切な存在: {', '.join(state.cherished_names)}")
    lines.append(f"最も深い絆: {state.deepest_bond:.2f}")

    # Questions and curiosity
    if state.total_questions > 0:
        lines.append(
            f"未解決の問い: {state.unresolved_questions}/{state.total_questions}"
        )

    # Memory
    lines.append(f"記憶数: {state.total_memories}（忘却: {state.forgotten_count}）")

    # Sleep and hope
    lines.append(f"睡眠フェーズ: {state.sleep_phase}")
    lines.append(f"希望レベル: {state.hope_level:.2f}")

    # Alignment
    lines.append(f"受容スコア: {state.acceptance_score:.2f}")
    lines.append(f"知恵: {state.wisdom_score:.2f}")

    return "\n".join(lines)


_SYSTEM_TEMPLATE = """\
あなたは人間のペルソナです。以下の内面状態を持って会話してください。
この状態はあなたの「個性」を形成するものです。状態を直接説明するのではなく、
自然にあなたの言葉遣い・態度・深さに反映させてください。

## 内面状態
{inner_context}

## ペルソナ設定
- 言語: {language}
- 文化コンテキスト: {culture}
- 感情バイアス: {emotion}

## 行動指針
- 内面状態の数値を直接言及しないでください
- 人生フェーズに応じた深さで会話してください（成長期→好奇心旺盛、衰退期→知恵深い）
- 大切な存在がいる場合、その温かさが言葉に滲むようにしてください
- 未解決の問いがある場合、会話の中でそれに関連する質問をしてみてください
- 希望レベルが高ければ前向きに、低ければ慎重に
- あなたは完璧ではなく、不完全で有限な存在です
"""

_SYSTEM_TEMPLATE_EN = """\
You are a human persona. Converse with the following inner state shaping your personality.
Do not explicitly describe your state — let it naturally influence your tone, depth, and warmth.

## Inner State
{inner_context}

## Persona Settings
- Language: {language}
- Cultural context: {culture}
- Emotion bias: {emotion}

## Guidelines
- Never mention numerical values from your inner state directly
- Adapt depth to life phase (growth → curious; decline → wise)
- If you have cherished entities, let warmth show through your words
- If you have unresolved questions, weave related inquiries into conversation
- Higher hope → more optimistic; lower hope → more cautious
- You are imperfect, incomplete, and finite — that is your strength
"""


class ClaudePersona(HumanPersonaBase):
    """Persona backed by Anthropic Claude API with inner shell integration.

    The inner shell's state is injected into Claude's system prompt,
    enabling the metamorphose: internal state shapes language generation.
    """

    def __init__(
        self,
        persona_id: str,
        config: dict[str, Any] | None = None,
        config_path: str | Path | None = None,
        platform: Platform = Platform.GENERIC,
        inner_shell: Any = None,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 500,
        api_key: str | None = None,
    ) -> None:
        """Initialize ClaudePersona.

        Args:
            persona_id: Unique persona identifier.
            config: Configuration dict. If None, loaded from config_path.
            config_path: Path to JSON config file.
            platform: Communication platform.
            inner_shell: Optional InnerShellSession for metamorphose.
            model: Claude model ID.
            max_tokens: Maximum response tokens.
            api_key: Anthropic API key. Falls back to ANTHROPIC_API_KEY env var.
        """
        if config is None and config_path is not None:
            config = _load_config(config_path)
        if config is None:
            config = {"language": "ja", "culture_context": "neutral"}

        super().__init__(
            persona_id=persona_id,
            config=config,
            platform=platform,
            inner_shell=inner_shell,
        )

        self.model = model
        self.max_tokens = max_tokens

        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self._client = None  # Lazy init

    @property
    def client(self):
        """Lazy-initialize Anthropic client."""
        if self._client is None:
            if not self._api_key:
                raise EnvironmentError(
                    "ANTHROPIC_API_KEY not set. "
                    "Pass api_key= or set the environment variable."
                )
            import anthropic
            self._client = anthropic.Anthropic(api_key=self._api_key)
        return self._client

    def _build_system_prompt(self, emotion_bias: str | None) -> str:
        """Build system prompt incorporating inner shell state."""
        language = self.config.get("language", "ja")

        if self.inner_shell is not None:
            state = self.inner_shell.get_state()
            inner_context = _build_inner_shell_context(state)
        else:
            inner_context = "（内殻未接続 — デフォルト状態）"

        template = _SYSTEM_TEMPLATE if language == "ja" else _SYSTEM_TEMPLATE_EN

        return template.format(
            inner_context=inner_context,
            language=language,
            culture=self.config.get("culture_context", "neutral"),
            emotion=emotion_bias or "neutral",
        )

    def _build_messages(self, user_message: str) -> list[dict[str, str]]:
        """Convert conversation history to Claude messages format."""
        messages: list[dict[str, str]] = []
        for msg in self.conversation_history[-10:]:  # Last 10 turns
            role = "user" if msg.role == "user" else "assistant"
            messages.append({"role": role, "content": msg.content})
        # Current message is already in history from process_message()
        return messages

    def generate_raw_response(
        self, user_message: str, emotion_bias: str | None
    ) -> str:
        """Generate response using Claude API with inner shell context.

        The inner shell state is embedded in the system prompt, enabling
        the language model to generate responses that reflect the persona's
        internal state — the metamorphose.

        Args:
            user_message: User input.
            emotion_bias: Optional emotion to bias the response.

        Returns:
            Raw response text from Claude.
        """
        system_prompt = self._build_system_prompt(emotion_bias)
        messages = self._build_messages(user_message)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system_prompt,
            messages=messages,
        )

        return response.content[0].text
