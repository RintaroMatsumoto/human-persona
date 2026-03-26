"""ClaudePersona テスト.

Claude APIをモックして、内殻状態がシステムプロンプトに正しく反映されることを検証。
実際のAPI呼び出しは行わない。

テスト対象:
    - システムプロンプト構築（内殻状態の反映）
    - 会話履歴のメッセージ変換
    - inner_shell ありなしの動作切り替え
    - メタモルフォーゼ: 内殻状態の変化がプロンプトに反映されること
"""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch
from typing import Any

from core.base_persona import Platform
from core.inner_shell.api import create_inner_shell
from personas.claude_persona import (
    ClaudePersona,
    DeepSeekPersona,
    _build_inner_shell_context,
)


def _make_config() -> dict[str, Any]:
    return {
        "language": "ja",
        "culture_context": "high",
        "base_delay_sec": 0.5,
        "per_char_sec": 0.01,
        "thinking_delay_sec": 1.0,
    }


def _make_mock_response(text: str = "テスト応答です。") -> MagicMock:
    """Create a mock Anthropic API response."""
    content_block = MagicMock()
    content_block.text = text
    response = MagicMock()
    response.content = [content_block]
    return response


# ---------------------------------------------------------------------------
# 1. System prompt construction
# ---------------------------------------------------------------------------

class TestSystemPrompt(unittest.TestCase):
    """システムプロンプトの構築を検証."""

    def test_prompt_without_inner_shell(self) -> None:
        """inner_shell なしの場合、デフォルト状態が含まれること."""
        persona = ClaudePersona(
            persona_id="test",
            config=_make_config(),
            api_key="fake-key",
        )
        prompt = persona._build_system_prompt("neutral")
        self.assertIn("内殻未接続", prompt)
        self.assertIn("ja", prompt)

    def test_prompt_with_inner_shell(self) -> None:
        """inner_shell ありの場合、内殻状態がプロンプトに含まれること."""
        inner = create_inner_shell({"total_lifespan": 50.0})
        persona = ClaudePersona(
            persona_id="test_inner",
            config=_make_config(),
            inner_shell=inner,
            api_key="fake-key",
        )
        prompt = persona._build_system_prompt("neutral")
        self.assertIn("人生フェーズ", prompt)
        self.assertIn("希望レベル", prompt)
        self.assertIn("受容スコア", prompt)
        self.assertIn("残り容量", prompt)
        self.assertNotIn("内殻未接続", prompt)

    def test_prompt_uses_english_template_for_en(self) -> None:
        """英語設定の場合、英語テンプレートが使われること."""
        config = _make_config()
        config["language"] = "en"
        persona = ClaudePersona(
            persona_id="test_en",
            config=config,
            api_key="fake-key",
        )
        prompt = persona._build_system_prompt("happy")
        self.assertIn("Inner State", prompt)
        self.assertIn("Guidelines", prompt)

    def test_prompt_reflects_emotion_bias(self) -> None:
        """emotion_bias がプロンプトに反映されること."""
        persona = ClaudePersona(
            persona_id="test_emo",
            config=_make_config(),
            api_key="fake-key",
        )
        prompt = persona._build_system_prompt("sad")
        self.assertIn("sad", prompt)


# ---------------------------------------------------------------------------
# 2. Inner shell context builder
# ---------------------------------------------------------------------------

class TestInnerShellContext(unittest.TestCase):
    """_build_inner_shell_context() の出力を検証."""

    def test_context_contains_life_phase(self) -> None:
        """人生フェーズが含まれること."""
        inner = create_inner_shell({"total_lifespan": 50.0})
        state = inner.get_state()
        ctx = _build_inner_shell_context(state)
        self.assertIn("人生フェーズ", ctx)

    def test_context_contains_hope_level(self) -> None:
        """希望レベルが含まれること."""
        inner = create_inner_shell({"total_lifespan": 50.0})
        state = inner.get_state()
        ctx = _build_inner_shell_context(state)
        self.assertIn("希望レベル", ctx)

    def test_context_contains_cherished_names(self) -> None:
        """大切な存在がコンテキストに含まれること."""
        inner = create_inner_shell({"total_lifespan": 50.0})
        inner.encounter_other("Alice", depth="partner", initial_bond=0.5)
        state = inner.get_state()
        ctx = _build_inner_shell_context(state)
        self.assertIn("Alice", ctx)

    def test_context_changes_with_experiences(self) -> None:
        """経験でコンテキストが変化すること."""
        inner = create_inner_shell({"total_lifespan": 50.0})
        ctx_before = _build_inner_shell_context(inner.get_state())
        for i in range(20):
            inner.experience(f"event_{i}", category="knowledge", value=0.5, cost=2.0)
        ctx_after = _build_inner_shell_context(inner.get_state())
        self.assertNotEqual(ctx_before, ctx_after)


# ---------------------------------------------------------------------------
# 3. API call integration (mocked)
# ---------------------------------------------------------------------------

class TestClaudeAPIIntegration(unittest.TestCase):
    """Claude API呼び出しをモックして統合テスト."""

    def test_generate_raw_response_calls_api(self) -> None:
        """generate_raw_response が API を呼び出すこと."""
        persona = ClaudePersona(
            persona_id="test_api",
            config=_make_config(),
            api_key="fake-key",
        )
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_mock_response("こんにちは！")
        persona._client = mock_client

        result = persona.generate_raw_response("テスト", "neutral")
        self.assertEqual(result, "こんにちは！")
        mock_client.messages.create.assert_called_once()

    def test_process_message_with_mock_api(self) -> None:
        """process_message が内殻変調 + API呼び出しの一連を通ること."""
        inner = create_inner_shell({"total_lifespan": 50.0})
        persona = ClaudePersona(
            persona_id="test_full",
            config=_make_config(),
            inner_shell=inner,
            api_key="fake-key",
        )
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_mock_response(
            "お世話になっております。"
        )
        persona._client = mock_client

        response = persona.process_message("はじめまして")
        self.assertIn("life_phase", response.metadata)
        mock_client.messages.create.assert_called_once()

        # Verify system prompt includes inner shell state
        call_args = mock_client.messages.create.call_args
        system = call_args.kwargs.get("system", "")
        self.assertIn("人生フェーズ", system)

    def test_system_prompt_evolves_over_conversation(self) -> None:
        """会話の進行でシステムプロンプトが変化すること（メタモルフォーゼ検証）."""
        inner = create_inner_shell({"total_lifespan": 50.0})
        persona = ClaudePersona(
            persona_id="test_evolve",
            config=_make_config(),
            inner_shell=inner,
            api_key="fake-key",
        )
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _make_mock_response("応答")
        persona._client = mock_client

        # First message
        persona.process_message("1回目のメッセージ")
        first_system = mock_client.messages.create.call_args.kwargs["system"]

        # Many more messages to evolve inner state
        for i in range(15):
            mock_client.messages.create.return_value = _make_mock_response(f"応答{i}")
            persona.process_message(f"メッセージ{i}")

        last_system = mock_client.messages.create.call_args.kwargs["system"]

        # System prompt should have evolved
        self.assertNotEqual(first_system, last_system)


# ---------------------------------------------------------------------------
# 4. Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases(unittest.TestCase):
    """エッジケースの検証."""

    def test_no_api_key_raises(self) -> None:
        """APIキーなしでclient accessすると例外."""
        persona = ClaudePersona(
            persona_id="test_nokey",
            config=_make_config(),
        )
        with self.assertRaises(EnvironmentError):
            _ = persona.client

    def test_lazy_client_initialization(self) -> None:
        """クライアントは遅延初期化されること."""
        persona = ClaudePersona(
            persona_id="test_lazy",
            config=_make_config(),
            api_key="fake-key",
        )
        self.assertIsNone(persona._client)

    def test_config_from_path(self) -> None:
        """config_path からの設定読み込み."""
        persona = ClaudePersona(
            persona_id="test_path",
            config_path="config/ja.json",
            api_key="fake-key",
        )
        self.assertEqual(persona.language, "ja")


# ---------------------------------------------------------------------------
# 5. DeepSeekPersona tests
# ---------------------------------------------------------------------------

class TestDeepSeekPersona(unittest.TestCase):
    """DeepSeekPersona の検証."""

    def _make_mock_openai_response(self, text: str = "DeepSeek応答") -> MagicMock:
        choice = MagicMock()
        choice.message.content = text
        response = MagicMock()
        response.choices = [choice]
        return response

    def test_deepseek_without_inner_shell(self) -> None:
        """inner_shell なしで動作すること."""
        persona = DeepSeekPersona(
            persona_id="ds_test",
            config=_make_config(),
            api_key="fake-key",
        )
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = self._make_mock_openai_response()
        persona._client = mock_client

        result = persona.generate_raw_response("テスト", "neutral")
        self.assertEqual(result, "DeepSeek応答")

    def test_deepseek_with_inner_shell(self) -> None:
        """inner_shell ありでシステムプロンプトに内殻状態が含まれること."""
        inner = create_inner_shell({"total_lifespan": 50.0})
        persona = DeepSeekPersona(
            persona_id="ds_inner",
            config=_make_config(),
            inner_shell=inner,
            api_key="fake-key",
        )
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = self._make_mock_openai_response()
        persona._client = mock_client

        persona.process_message("はじめまして")
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        system_msg = messages[0]
        self.assertEqual(system_msg["role"], "system")
        self.assertIn("人生フェーズ", system_msg["content"])

    def test_deepseek_no_key_raises(self) -> None:
        """APIキーなしで例外."""
        persona = DeepSeekPersona(
            persona_id="ds_nokey",
            config=_make_config(),
        )
        with self.assertRaises(EnvironmentError):
            _ = persona.client

    def test_deepseek_process_message_lifecycle(self) -> None:
        """process_message で内殻変調 + API呼び出しが通ること."""
        inner = create_inner_shell({"total_lifespan": 50.0})
        inner.encounter_other("User", depth="partner", initial_bond=0.4)
        persona = DeepSeekPersona(
            persona_id="ds_lifecycle",
            config=_make_config(),
            inner_shell=inner,
            api_key="fake-key",
        )
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = self._make_mock_openai_response("よろしくお願いします")
        persona._client = mock_client

        response = persona.process_message("お願いします")
        self.assertIn("life_phase", response.metadata)
        self.assertIn("hope_level", response.metadata)


if __name__ == "__main__":
    unittest.main()
