"""一貫性テストスイート.

各モジュールが単独で正しく動作するだけでなく、
モジュール間の状態が矛盾なく連携することを検証する。

テスト対象:
    - EmotionStateMachine: 感情遷移の正当性・状態履歴の一貫性
    - ContextReferencer: 会話履歴の追跡・トピック参照の正確性
    - StyleVariator: パターン選択の偏り抑制・履歴の反映
    - EscalationDetector: キーワード検知・雑談追跡の整合性
    - モジュール間連携: 感情状態がトーン修飾に正しく反映されるか
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.emotion_state_machine import (
    EmotionState,
    EmotionStateMachine,
)
from core.context_referencer import ContextReferencer
from core.style_variator import StyleType, StyleVariator
from core.escalation_detector import (
    EscalationDetector,
    EscalationReason,
    EscalationResult,
)


# ──────────────────────────────────────────────
# 1. EmotionStateMachine の一貫性テスト
# ──────────────────────────────────────────────

class TestEmotionStateConsistency(unittest.TestCase):
    """感情状態機械の遷移一貫性を検証する."""

    def setUp(self) -> None:
        self.sm = EmotionStateMachine()

    def test_initial_state_is_formal(self) -> None:
        """初期状態が FORMAL であること."""
        self.assertEqual(self.sm.current_state, EmotionState.FORMAL)

    def test_history_starts_with_initial(self) -> None:
        """履歴が初期状態から始まること."""
        self.assertEqual(self.sm.state_history, [EmotionState.FORMAL])

    def test_exchange_count_increments(self) -> None:
        """exchange イベントでカウントが増加すること."""
        for i in range(5):
            self.sm.process_event("exchange")
        self.assertEqual(self.sm.exchange_count, 5)

    def test_formal_to_warming_after_3_exchanges(self) -> None:
        """3回の exchange で FORMAL → WARMING に遷移すること."""
        for _ in range(3):
            self.sm.process_event("exchange")
        self.assertEqual(self.sm.current_state, EmotionState.WARMING)

    def test_warming_to_trusted_after_10_exchanges(self) -> None:
        """10回の exchange で WARMING → TRUSTED に遷移すること."""
        for _ in range(10):
            self.sm.process_event("exchange")
        self.assertEqual(self.sm.current_state, EmotionState.TRUSTED)

    def test_problem_causes_tense_from_warming(self) -> None:
        """WARMING 状態で problem_detected → TENSE に遷移すること."""
        for _ in range(3):
            self.sm.process_event("exchange")
        self.assertEqual(self.sm.current_state, EmotionState.WARMING)
        self.sm.process_event("problem_detected")
        self.assertEqual(self.sm.current_state, EmotionState.TENSE)

    def test_problem_resolved_causes_relieved(self) -> None:
        """TENSE 状態で problem_resolved → RELIEVED に遷移すること."""
        # FORMAL → WARMING → TENSE → RELIEVED
        for _ in range(3):
            self.sm.process_event("exchange")
        self.sm.process_event("problem_detected")
        self.sm.process_event("problem_resolved")
        self.assertEqual(self.sm.current_state, EmotionState.RELIEVED)

    def test_history_records_all_transitions(self) -> None:
        """全遷移が履歴に記録されること."""
        # FORMAL → WARMING → TENSE → RELIEVED
        for _ in range(3):
            self.sm.process_event("exchange")
        self.sm.process_event("problem_detected")
        self.sm.process_event("problem_resolved")
        expected = [
            EmotionState.FORMAL,
            EmotionState.WARMING,
            EmotionState.TENSE,
            EmotionState.RELIEVED,
        ]
        self.assertEqual(self.sm.state_history, expected)

    def test_no_transition_on_irrelevant_event(self) -> None:
        """定義外のイベントでは遷移しないこと."""
        state_before = self.sm.current_state
        self.sm.process_event("random_noise")
        self.assertEqual(self.sm.current_state, state_before)

    def test_reset_restores_initial(self) -> None:
        """reset() で初期状態に完全復帰すること."""
        for _ in range(5):
            self.sm.process_event("exchange")
        self.sm.process_event("problem_detected")
        self.sm.reset()
        self.assertEqual(self.sm.current_state, EmotionState.FORMAL)
        self.assertEqual(self.sm.exchange_count, 0)
        self.assertEqual(self.sm.state_history, [EmotionState.FORMAL])

    def test_tone_modifier_matches_state(self) -> None:
        """get_tone_modifier() が現在の状態に一致する値を返すこと."""
        # FORMAL: high formality, low warmth
        mod = self.sm.get_tone_modifier()
        self.assertGreater(mod["formality"], 0.7)
        self.assertLess(mod["warmth"], 0.4)

        # WARMING に遷移
        for _ in range(3):
            self.sm.process_event("exchange")
        mod = self.sm.get_tone_modifier()
        self.assertLess(mod["formality"], 0.7)
        self.assertGreater(mod["warmth"], 0.4)

    def test_trusted_state_has_low_caution(self) -> None:
        """TRUSTED 状態では caution が低いこと."""
        for _ in range(10):
            self.sm.process_event("exchange")
        mod = self.sm.get_tone_modifier()
        self.assertLess(mod["caution"], 0.3)

    def test_tense_state_has_high_caution(self) -> None:
        """TENSE 状態では caution が高いこと."""
        for _ in range(3):
            self.sm.process_event("exchange")
        self.sm.process_event("problem_detected")
        mod = self.sm.get_tone_modifier()
        self.assertGreater(mod["caution"], 0.8)

    def test_problem_from_trusted_goes_tense(self) -> None:
        """TRUSTED 状態でも problem_detected で TENSE に遷移すること."""
        for _ in range(10):
            self.sm.process_event("exchange")
        self.assertEqual(self.sm.current_state, EmotionState.TRUSTED)
        self.sm.process_event("problem_detected")
        self.assertEqual(self.sm.current_state, EmotionState.TENSE)


class TestEmotionFromConfig(unittest.TestCase):
    """設定ファイルからの EmotionStateMachine 構築を検証する."""

    def test_from_ja_config(self) -> None:
        """日本語設定ファイルから正しく構築されること."""
        config_path = Path(__file__).parent.parent / "config" / "ja.json"
        with open(config_path) as f:
            config = json.load(f)
        sm = EmotionStateMachine.from_config(config["emotion"])
        self.assertEqual(sm.current_state, EmotionState.FORMAL)
        # 3 exchanges で warming
        for _ in range(3):
            sm.process_event("exchange")
        self.assertEqual(sm.current_state, EmotionState.WARMING)

    def test_from_en_config(self) -> None:
        """英語設定ファイルから正しく構築されること."""
        config_path = Path(__file__).parent.parent / "config" / "en.json"
        with open(config_path) as f:
            config = json.load(f)
        sm = EmotionStateMachine.from_config(config["emotion"])
        self.assertEqual(sm.current_state, EmotionState.FORMAL)
        # en は 2 exchanges で warming
        for _ in range(2):
            sm.process_event("exchange")
        self.assertEqual(sm.current_state, EmotionState.WARMING)

    def test_wildcard_transition_expands(self) -> None:
        """ワイルドカード遷移が全状態から展開されること."""
        config = {
            "initial_state": "formal",
            "transitions": [
                {"from": "*", "to": "tense", "trigger": "problem_detected"},
            ],
        }
        sm = EmotionStateMachine.from_config(config)
        # FORMAL → TENSE (wildcard)
        sm.process_event("problem_detected")
        self.assertEqual(sm.current_state, EmotionState.TENSE)


# ──────────────────────────────────────────────
# 2. ContextReferencer の一貫性テスト
# ──────────────────────────────────────────────

class TestContextReferencerConsistency(unittest.TestCase):
    """会話履歴・文脈参照の一貫性を検証する."""

    def setUp(self) -> None:
        self.cr = ContextReferencer()

    def test_empty_history(self) -> None:
        """初期状態では履歴が空であること."""
        self.assertEqual(len(self.cr.history), 0)
        self.assertIsNone(self.cr.get_user_last_message())

    def test_add_turn_increments_index(self) -> None:
        """ターン追加でインデックスが正しく振られること."""
        self.cr.add_turn("user", "Hello", ["greeting"])
        self.cr.add_turn("assistant", "Hi there", ["greeting"])
        self.assertEqual(self.cr.history[0].turn_index, 0)
        self.assertEqual(self.cr.history[1].turn_index, 1)

    def test_get_user_last_message(self) -> None:
        """ユーザーの最終メッセージが正しく取得されること."""
        self.cr.add_turn("user", "First message")
        self.cr.add_turn("assistant", "Reply")
        self.cr.add_turn("user", "Second message")
        self.assertEqual(self.cr.get_user_last_message(), "Second message")

    def test_recent_topics_deduplication(self) -> None:
        """get_recent_topics() がトピックを重複除去すること."""
        self.cr.add_turn("user", "msg1", ["design", "ux"])
        self.cr.add_turn("assistant", "msg2", ["design"])
        self.cr.add_turn("user", "msg3", ["design", "budget"])
        topics = self.cr.get_recent_topics(3)
        # 重複除去されているか
        self.assertEqual(len(topics), len(set(topics)))
        self.assertIn("design", topics)
        self.assertIn("budget", topics)

    def test_find_topic_history(self) -> None:
        """特定トピックの出現履歴が正しく検索されること."""
        self.cr.add_turn("user", "msg1", ["design"])
        self.cr.add_turn("assistant", "msg2", ["timeline"])
        self.cr.add_turn("user", "msg3", ["design", "revision"])
        results = self.cr.find_topic_history("design")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].turn_index, 0)
        self.assertEqual(results[1].turn_index, 2)

    def test_max_history_truncation(self) -> None:
        """max_history を超えた場合に古いターンが切り捨てられること."""
        cr = ContextReferencer(max_history=5)
        for i in range(10):
            cr.add_turn("user", f"msg{i}", [f"topic{i}"])
        self.assertEqual(len(cr.history), 5)
        # 最も古いのは msg5（0-4 が切り捨てられている）
        self.assertEqual(cr.history[0].content, "msg5")

    def test_should_reference_previous_false_initially(self) -> None:
        """履歴が2未満の場合は参照不要と判定されること."""
        self.assertFalse(self.cr.should_reference_previous())
        self.cr.add_turn("user", "msg1", ["topic"])
        self.assertFalse(self.cr.should_reference_previous())

    def test_should_reference_previous_true_with_history(self) -> None:
        """履歴が3以上で参照すべきと判定されること."""
        for i in range(3):
            self.cr.add_turn("user", f"msg{i}", [f"topic{i}"])
        self.assertTrue(self.cr.should_reference_previous())

    def test_consistency_context_structure(self) -> None:
        """get_consistency_context() が正しい構造を返すこと."""
        self.cr.add_turn("user", "Hello", ["greeting"])
        self.cr.add_turn("assistant", "Hi", ["greeting"])
        ctx = self.cr.get_consistency_context()
        self.assertIn("recent_topics", ctx)
        self.assertIn("total_turns", ctx)
        self.assertIn("user_last_message", ctx)
        self.assertEqual(ctx["total_turns"], 2)
        self.assertEqual(ctx["user_last_message"], "Hello")


# ──────────────────────────────────────────────
# 3. StyleVariator の一貫性テスト
# ──────────────────────────────────────────────

class TestStyleVariatorConsistency(unittest.TestCase):
    """文体揺らぎの一貫性・偏り抑制を検証する."""

    def setUp(self) -> None:
        config_path = Path(__file__).parent.parent / "config" / "ja.json"
        with open(config_path) as f:
            config = json.load(f)
        self.sv = StyleVariator.from_config(config["style"])

    def test_all_style_types_selectable(self) -> None:
        """十分な試行で全StyleTypeが少なくとも1回は選択されること."""
        seen: set[StyleType] = set()
        for _ in range(200):
            style = self.sv.select_style()
            seen.add(style)
        self.assertEqual(seen, set(StyleType))

    def test_history_prevents_repetition(self) -> None:
        """同一パターンの連続選択率が十分低いこと."""
        consecutive_repeats = 0
        prev = None
        for _ in range(100):
            style = self.sv.select_style()
            if style == prev:
                consecutive_repeats += 1
            prev = style
        # 連続使用率は30%未満であるべき（重み減衰あり）
        self.assertLess(consecutive_repeats / 100, 0.30)

    def test_history_max_length(self) -> None:
        """履歴が max_history を超えないこと."""
        for _ in range(50):
            self.sv.select_style()
        self.assertLessEqual(len(self.sv.history), self.sv.max_history)

    def test_get_template_returns_string_or_none(self) -> None:
        """get_template() が str か None を返すこと."""
        for style in StyleType:
            result = self.sv.get_template(style)
            self.assertTrue(result is None or isinstance(result, str))

    def test_configured_patterns_have_templates(self) -> None:
        """設定ファイルから読み込まれたパターンにテンプレートが存在すること."""
        for style_type, pattern in self.sv.patterns.items():
            self.assertGreater(len(pattern.templates), 0,
                               f"{style_type.value} のテンプレートが空")

    def test_filler_words_per_language(self) -> None:
        """各言語のフィラーが取得可能であること."""
        for lang in ["ja", "en", "es"]:
            filler = self.sv.get_filler(lang)
            self.assertIsInstance(filler, str)

    def test_structure_patterns_per_language(self) -> None:
        """各言語の構造パターンが取得可能であること."""
        for lang in ["ja", "en", "es"]:
            structure = self.sv.get_structure_pattern(lang)
            self.assertIsInstance(structure, str)
            self.assertGreater(len(structure), 0)

    def test_uncertainty_rate_from_config(self) -> None:
        """設定ファイルの uncertainty_rate が反映されること."""
        self.assertAlmostEqual(self.sv.uncertainty_rate, 0.18)

    def test_add_variation_passthrough(self) -> None:
        """基底実装の add_variation がパススルーであること."""
        text = "テスト文章です。"
        self.assertEqual(self.sv.add_variation(text), text)


# ──────────────────────────────────────────────
# 4. EscalationDetector の一貫性テスト
# ──────────────────────────────────────────────

class TestEscalationDetectorConsistency(unittest.TestCase):
    """エスカレーション検知の一貫性を検証する."""

    def setUp(self) -> None:
        config_path = Path(__file__).parent.parent / "config" / "ja.json"
        with open(config_path) as f:
            config = json.load(f)
        self.detector = EscalationDetector.from_config(config["escalation"])

    def test_no_escalation_for_normal_message(self) -> None:
        """通常メッセージではエスカレーションされないこと."""
        result = self.detector.evaluate("お疲れ様です。進捗報告です。")
        self.assertFalse(result.should_escalate)

    def test_negotiation_keywords_trigger(self) -> None:
        """金額関連キーワードでエスカレーションされること."""
        result = self.detector.evaluate("単価を少し下げてもらえますか？")
        self.assertTrue(result.should_escalate)
        self.assertEqual(result.reason, EscalationReason.NEGOTIATION)

    def test_call_request_triggers(self) -> None:
        """通話要求でエスカレーションされること."""
        result = self.detector.evaluate("一度Zoomで打ち合わせしませんか？")
        self.assertTrue(result.should_escalate)
        self.assertEqual(result.reason, EscalationReason.CALL_REQUEST)

    def test_complaint_triggers(self) -> None:
        """クレームでエスカレーションされること."""
        result = self.detector.evaluate("これは最悪の対応です。返金してください。")
        self.assertTrue(result.should_escalate)
        self.assertEqual(result.reason, EscalationReason.COMPLAINT)

    def test_highest_priority_wins(self) -> None:
        """複数ルールにマッチした場合、最高優先度が返ること."""
        # "最悪"(complaint, priority=5) + "Zoom"(call_request, priority=4)
        result = self.detector.evaluate("最悪です、Zoomで話しましょう")
        self.assertTrue(result.should_escalate)
        # priority が小さい方が高優先度
        self.assertEqual(result.reason, EscalationReason.CALL_REQUEST)

    def test_chat_tracking_escalation(self) -> None:
        """雑談が max_chat_turns を超えるとエスカレーションされること."""
        for i in range(self.detector.max_chat_turns - 1):
            result = self.detector.track_chat(is_chitchat=True)
            self.assertFalse(result.should_escalate)
        result = self.detector.track_chat(is_chitchat=True)
        self.assertTrue(result.should_escalate)
        self.assertEqual(result.reason, EscalationReason.EXTENDED_CHAT)

    def test_chat_counter_resets_on_non_chitchat(self) -> None:
        """業務メッセージで雑談カウンターがリセットされること."""
        self.detector.track_chat(is_chitchat=True)
        self.detector.track_chat(is_chitchat=True)
        self.detector.track_chat(is_chitchat=False)
        self.assertEqual(self.detector.chat_count, 0)

    def test_reset_chat_counter(self) -> None:
        """reset_chat_counter() で明示的リセットできること."""
        self.detector.track_chat(is_chitchat=True)
        self.detector.track_chat(is_chitchat=True)
        self.detector.reset_chat_counter()
        self.assertEqual(self.detector.chat_count, 0)

    def test_en_config_keywords(self) -> None:
        """英語設定ファイルのキーワードが正しく検知されること."""
        config_path = Path(__file__).parent.parent / "config" / "en.json"
        with open(config_path) as f:
            config = json.load(f)
        detector = EscalationDetector.from_config(config["escalation"])
        result = detector.evaluate("Can we discuss the price?")
        self.assertTrue(result.should_escalate)
        self.assertEqual(result.reason, EscalationReason.NEGOTIATION)


# ──────────────────────────────────────────────
# 5. モジュール間連携の一貫性テスト
# ──────────────────────────────────────────────

class TestCrossModuleConsistency(unittest.TestCase):
    """複数モジュールの連携における一貫性を検証する."""

    def test_emotion_affects_style_context(self) -> None:
        """感情状態の変化がスタイル選択の文脈に反映可能であること.

        EmotionStateMachine の get_tone_modifier() 出力を
        StyleVariator の select_style() の context に渡す想定のフロー。
        """
        sm = EmotionStateMachine()
        sv = StyleVariator()

        # FORMAL 状態での tone modifier
        formal_mod = sm.get_tone_modifier()
        style_formal = sv.select_style(context=formal_mod)
        self.assertIsInstance(style_formal, StyleType)

        # WARMING に遷移後
        for _ in range(3):
            sm.process_event("exchange")
        warming_mod = sm.get_tone_modifier()
        # 値が変化していること
        self.assertNotEqual(formal_mod, warming_mod)

    def test_context_tracks_escalation_scenario(self) -> None:
        """エスカレーション発生時の会話履歴が正しく追跡されること."""
        cr = ContextReferencer()
        detector = EscalationDetector.from_config({
            "escalation_rules": [
                {
                    "reason": "negotiation",
                    "keywords": ["budget", "price"],
                    "threshold": 1,
                    "priority": 5,
                }
            ],
            "max_chat_turns": 3,
        })

        # 通常の会話
        cr.add_turn("user", "Hi, I need a website built", ["project"])
        result = detector.evaluate("Hi, I need a website built")
        self.assertFalse(result.should_escalate)

        # エスカレーション発生
        cr.add_turn("user", "What's your budget for this?", ["budget"])
        result = detector.evaluate("What's your budget for this?")
        self.assertTrue(result.should_escalate)

        # 履歴にはエスカレーション前後のメッセージが両方残っている
        self.assertEqual(len(cr.history), 2)
        self.assertIn("budget", cr.history[1].topics)

    def test_emotion_context_consistency_through_conversation(self) -> None:
        """会話進行に伴い、感情・文脈・スタイルが矛盾なく変化すること."""
        sm = EmotionStateMachine()
        cr = ContextReferencer()
        sv = StyleVariator()

        # ターン 1-3: FORMAL → WARMING
        for i in range(3):
            cr.add_turn("user", f"Message {i}", [f"topic_{i}"])
            cr.add_turn("assistant", f"Reply {i}", [f"topic_{i}"])
            sm.process_event("exchange")
        self.assertEqual(sm.current_state, EmotionState.WARMING)
        self.assertEqual(len(cr.history), 6)
        self.assertTrue(cr.should_reference_previous())

        # 問題発生: WARMING → TENSE
        sm.process_event("problem_detected")
        self.assertEqual(sm.current_state, EmotionState.TENSE)
        mod = sm.get_tone_modifier()
        self.assertGreater(mod["caution"], 0.8)

        # 解決: TENSE → RELIEVED
        sm.process_event("problem_resolved")
        self.assertEqual(sm.current_state, EmotionState.RELIEVED)
        mod = sm.get_tone_modifier()
        self.assertGreater(mod["warmth"], 0.7)

    def test_config_cross_loading(self) -> None:
        """同一configから全モジュールが矛盾なく構築できること."""
        config_path = Path(__file__).parent.parent / "config" / "ja.json"
        with open(config_path) as f:
            config = json.load(f)

        sm = EmotionStateMachine.from_config(config["emotion"])
        sv = StyleVariator.from_config(config["style"])
        ed = EscalationDetector.from_config(config["escalation"])

        # 各モジュールが独立して正しく動作
        self.assertEqual(sm.current_state, EmotionState.FORMAL)
        self.assertEqual(len(sv.patterns), 5)
        self.assertGreater(len(ed.rules), 0)

        # 連携: 感情遷移 → スタイル選択
        for _ in range(3):
            sm.process_event("exchange")
        mod = sm.get_tone_modifier()
        style = sv.select_style(context=mod)
        self.assertIsInstance(style, StyleType)


if __name__ == "__main__":
    unittest.main()
