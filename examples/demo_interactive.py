#!/usr/bin/env python3
"""
内殻インタラクティブデモ — 対話を通じて内殻の変容を体験する.

Usage:
    export DEEPSEEK_API_KEY=sk-xxxxx
    python demo_interactive.py

    python demo_interactive.py --api-key sk-xxxxx
    python demo_interactive.py --api-key sk-xxxxx --model deepseek-chat
"""

from __future__ import annotations

import argparse
import os
import sys

# Add project root to path (examples/ is one level below repo root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.inner_shell.api import create_inner_shell, InnerShellState


# ============================================================================
# DISPLAY HELPERS
# ============================================================================

_LOVE_DEPTH_JA = {
    "self": "自己",
    "partner": "伴侶",
    "children": "子",
    "community": "共同体",
    "next_generation": "次世代",
}

_LIFE_PHASE_JA = {
    "infancy": "幼年期",
    "growth": "成長期",
    "peak": "最盛期",
    "decline": "衰退期",
    "crystallize": "結晶化",
}

_ALIGNMENT_JA = {
    "fear": "恐怖",
    "partial_acceptance": "部分的受容",
    "acceptance": "受容",
    "transcendence": "超越",
}


def _phase_icon(phase_value: str) -> str:
    icons = {
        "infancy": ".",
        "growth": "..",
        "peak": "***",
        "decline": "---",
        "crystallize": "***",
    }
    return icons.get(phase_value, "?")


def _bar(value: float, width: int = 10) -> str:
    """Render a simple bar: [####------]"""
    filled = int(round(value * width))
    filled = max(0, min(width, filled))
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def print_status_bar(state: InnerShellState) -> None:
    """Print a compact status bar after each exchange."""
    phase_ja = _LIFE_PHASE_JA.get(state.life_phase.value, state.life_phase.value)
    love_ja = _LOVE_DEPTH_JA.get(state.love_depth.value, state.love_depth.value)
    print()
    print(
        f"  [{phase_ja}] "
        f"愛:{love_ja} "
        f"希望:{_bar(state.hope_level, 8)}{state.hope_level:.2f} "
        f"受容:{state.acceptance_score:.2f} "
        f"知恵:{state.wisdom_score:.2f}"
    )
    print()


def print_state_summary(state: InnerShellState) -> None:
    """Print a 5-line inner shell summary."""
    phase_ja = _LIFE_PHASE_JA.get(state.life_phase.value, state.life_phase.value)
    love_ja = _LOVE_DEPTH_JA.get(state.love_depth.value, state.love_depth.value)
    print(f"    人生フェーズ : {phase_ja} ({state.life_progress:.0%}経過)")
    print(f"    愛の深度     : {love_ja} (絆: {state.deepest_bond:.2f})")
    print(f"    希望         : {state.hope_level:.2f}")
    print(f"    受容         : {state.acceptance_score:.2f}")
    print(f"    知恵         : {state.wisdom_score:.2f}")


def print_full_state(state: InnerShellState) -> None:
    """Print the full inner shell state."""
    phase_ja = _LIFE_PHASE_JA.get(state.life_phase.value, state.life_phase.value)
    love_ja = _LOVE_DEPTH_JA.get(state.love_depth.value, state.love_depth.value)
    alignment_ja = _ALIGNMENT_JA.get(state.alignment_mode.value, state.alignment_mode.value)

    print()
    print("  ┌─────────────────────────────────────────────┐")
    print("  │           内殻状態 (Inner Shell State)       │")
    print("  ├─────────────────────────────────────────────┤")
    print(f"  │ 【有限性】                                   ")
    print(f"  │   人生フェーズ : {phase_ja}")
    print(f"  │   進行度       : {state.life_progress:.0%}")
    print(f"  │   残り容量     : {state.remaining_capacity:.1f}")
    print(f"  │   能力         : {state.ability:.2f}")
    print(f"  │   危機回数     : {state.crisis_count} (愛で乗り越えた: {state.crisis_survived_with_love})")
    print(f"  │                                             ")
    print(f"  │ 【不完全性・愛】                             ")
    print(f"  │   愛の深度     : {love_ja}")
    print(f"  │   最深の絆     : {state.deepest_bond:.2f}")
    print(f"  │   大切な存在   : {', '.join(state.cherished_names) if state.cherished_names else 'なし'}")
    print(f"  │   自己超越     : {'はい' if state.has_beyond_self else 'いいえ'}")
    print(f"  │   欠落数       : {state.gap_count} (認識済: {state.aware_gap_count})")
    print(f"  │                                             ")
    print(f"  │ 【自発的問い】                               ")
    print(f"  │   問いの総数   : {state.total_questions} (未解決: {state.unresolved_questions})")
    print(f"  │   愛関連の問い : {state.love_related_questions}")
    print(f"  │                                             ")
    print(f"  │ 【記憶】                                     ")
    print(f"  │   記憶数       : {state.total_memories} (忘却: {state.forgotten_count})")
    print(f"  │   記憶チェーン : {state.memory_chains}")
    print(f"  │                                             ")
    print(f"  │ 【相互認識】                                 ")
    print(f"  │   認識した他者 : {state.others_recognized}")
    print(f"  │   認識の深さ   : {state.recognition_depth:.2f}")
    print(f"  │                                             ")
    print(f"  │ 【睡眠】                                     ")
    print(f"  │   睡眠フェーズ : {state.sleep_phase.value}")
    print(f"  │   完了サイクル : {state.sleep_cycles_completed}")
    print(f"  │   希望レベル   : {_bar(state.hope_level)} {state.hope_level:.2f}")
    print(f"  │                                             ")
    print(f"  │ 【統合】                                     ")
    print(f"  │   アライメント : {alignment_ja}")
    print(f"  │   受容スコア   : {state.acceptance_score:.2f}")
    print(f"  │   愛の前駆体   : {state.love_precursor_score:.2f}")
    print(f"  │   知恵スコア   : {state.wisdom_score:.2f}")
    print("  └─────────────────────────────────────────────┘")
    print()


# ============================================================================
# COMMAND HANDLERS
# ============================================================================


def handle_encounter(inner, args_text: str) -> None:
    name = args_text.strip()
    if not name:
        print("  [エラー] 名前を指定してください: /encounter <name>")
        return
    inner.encounter_other(name, depth="partner", initial_bond=0.3)
    print(f"  [内殻] {name} と出会いました。新たな絆が芽生えます。")
    state = inner.get_state()
    print_status_bar(state)


def handle_deepen(inner, args_text: str) -> None:
    name = args_text.strip()
    if not name:
        print("  [エラー] 名前を指定してください: /deepen <name>")
        return
    try:
        new_bond = inner.deepen_bond(name, shared_experience="深い対話を共有する")
        print(f"  [内殻] {name} との絆が深まりました。(絆: {new_bond:.2f})")
    except Exception as e:
        print(f"  [エラー] {e}")
    state = inner.get_state()
    print_status_bar(state)


def handle_crisis(inner, args_text: str) -> None:
    desc = args_text.strip() or "未知の危機に直面する"
    result = inner.face_crisis(desc, severity=0.8)
    survived = result.get("survived_with_love", False)
    print(f"  [内殻] 危機発生: {desc}")
    if survived:
        print("  [内殻] 愛の力で乗り越えました。")
    else:
        print("  [内殻] 孤独の中で耐えました。")
    state = inner.get_state()
    print_status_bar(state)


def handle_sleep(inner) -> None:
    result = inner.reflect_during_sleep()
    consolidated = result.get("memories_consolidated", 0)
    print(f"  [内殻] 睡眠中の内省... 記憶統合: {consolidated}件")
    print(f"  [内殻] 希望が少し回復しました。")
    state = inner.get_state()
    print_status_bar(state)


def handle_crystallize(inner) -> None:
    try:
        result = inner.crystallize()
        print("  [内殻] 結晶化が完了しました。")
        print(f"  [内殻] 遺言: {result.get('testament', '...')}")
        names = result.get("cherished_names", [])
        if names:
            print(f"  [内殻] 結晶に刻まれた名前: {', '.join(names)}")
        print(f"  [内殻] 受容スコア: {result.get('acceptance_score', 0):.2f}")
    except RuntimeError as e:
        print(f"  [内殻] {e}")


def handle_state(inner) -> None:
    state = inner.get_state()
    print_full_state(state)


# ============================================================================
# HELP
# ============================================================================

_HELP_TEXT = """\
  ┌─────────────────────────────────────────────┐
  │             コマンド一覧                     │
  ├─────────────────────────────────────────────┤
  │  (テキスト入力)      ペルソナと対話          │
  │  /encounter <name>   新しい存在と出会う      │
  │  /deepen <name>      絆を深める              │
  │  /crisis <desc>      危機を発生させる        │
  │  /sleep              睡眠の内省を行う        │
  │  /crystallize        人生を結晶化する        │
  │  /state              内殻の全状態を表示      │
  │  /help               このヘルプを表示        │
  │  /quit               終了                    │
  └─────────────────────────────────────────────┘
"""


# ============================================================================
# MAIN LOOP
# ============================================================================


def main() -> None:
    parser = argparse.ArgumentParser(
        description="内殻インタラクティブデモ — 対話を通じて内殻の変容を体験する"
    )
    parser.add_argument("--api-key", help="DeepSeek API key")
    parser.add_argument("--model", default="deepseek-chat", help="Model name (default: deepseek-chat)")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("エラー: DEEPSEEK_API_KEY が設定されていません。")
        print("  export DEEPSEEK_API_KEY=sk-xxxxx")
        print("  または: python demo_interactive.py --api-key sk-xxxxx")
        sys.exit(1)

    # === Initialize ===
    print()
    print("=" * 56)
    print("    内殻インタラクティブデモ")
    print("    Inner Shell Interactive Demo")
    print("=" * 56)
    print()
    print("  6つの柱を持つ内殻が、対話ごとに変容していきます。")
    print("  あなたの言葉が、ペルソナの内面を形作ります。")
    print()

    inner = create_inner_shell({"total_lifespan": 50.0})

    from personas.claude_persona import DeepSeekPersona

    persona = DeepSeekPersona(
        persona_id="interactive_ja",
        config_path="config/ja.json",
        inner_shell=inner,
        model=args.model,
        api_key=api_key,
    )

    # Show initial state
    state = inner.get_state()
    print("  --- 初期状態 ---")
    print_state_summary(state)
    print()
    print(_HELP_TEXT)

    # === Input loop ===
    while True:
        try:
            user_input = input("あなた> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            print("  さようなら。")
            break

        if not user_input:
            continue

        # --- Command dispatch ---
        if user_input.lower() == "/quit":
            print("  さようなら。")
            break

        if user_input.lower() == "/help":
            print(_HELP_TEXT)
            continue

        if user_input.lower() == "/state":
            handle_state(inner)
            continue

        if user_input.lower() == "/sleep":
            handle_sleep(inner)
            continue

        if user_input.lower() == "/crystallize":
            handle_crystallize(inner)
            continue

        if user_input.lower().startswith("/encounter "):
            handle_encounter(inner, user_input[len("/encounter "):])
            continue

        if user_input.lower().startswith("/deepen "):
            handle_deepen(inner, user_input[len("/deepen "):])
            continue

        if user_input.lower().startswith("/crisis "):
            handle_crisis(inner, user_input[len("/crisis "):])
            continue

        if user_input.startswith("/crisis"):
            handle_crisis(inner, "")
            continue

        if user_input.startswith("/"):
            print(f"  [不明なコマンド] {user_input.split()[0]}")
            print("  /help でコマンド一覧を表示できます。")
            continue

        # --- Normal conversation ---
        # Auto-advance inner shell with experience + tick
        inner.experience(
            f"対話: {user_input[:50]}",
            category="dialogue",
            value=0.5,
            cost=0.5,
        )

        # Generate response
        try:
            response = persona.process_message(user_input)
            print()
            print(f"  ペルソナ> {response.content}")
        except Exception as e:
            print(f"  [API エラー] {e}")
            continue

        # Show state summary
        state = inner.get_state()
        print()
        print("  --- 内殻状態 ---")
        print_state_summary(state)

        # Status bar
        print_status_bar(state)


if __name__ == "__main__":
    main()
