#!/usr/bin/env python3
"""
メタモルフォーゼ実機デモ — 内殻が言語生成を変える瞬間を体験する.

Usage:
    export DEEPSEEK_API_KEY=sk-xxxxx
    python demo_metamorphose.py

または:
    python demo_metamorphose.py --api-key sk-xxxxx
"""

from __future__ import annotations

import argparse
import os
import sys

# Add project root to path (examples/ is one level below repo root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.inner_shell.api import create_inner_shell
from personas.claude_persona import DeepSeekPersona


def main() -> None:
    parser = argparse.ArgumentParser(description="メタモルフォーゼ実機デモ")
    parser.add_argument("--api-key", help="DeepSeek API key")
    parser.add_argument("--model", default="deepseek-chat", help="Model name")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("Error: DEEPSEEK_API_KEY が設定されていません。")
        print("  export DEEPSEEK_API_KEY=sk-xxxxx")
        print("  または: python demo_metamorphose.py --api-key sk-xxxxx")
        sys.exit(1)

    # === 内殻を創る ===
    print("=" * 60)
    print("  メタモルフォーゼ実機デモ")
    print("  内殻の状態が言語生成をどう変えるかを体験する")
    print("=" * 60)
    print()

    inner = create_inner_shell({"total_lifespan": 50.0})
    persona = DeepSeekPersona(
        persona_id="metamorphose_ja",
        config_path="config/ja.json",
        inner_shell=inner,
        model=args.model,
        api_key=api_key,
    )

    # === フェーズ1: 誕生直後 ===
    print("━━━ フェーズ1: 誕生直後（INFANCY）━━━")
    state = inner.get_state()
    print(f"  人生フェーズ: {state.life_phase.value}")
    print(f"  希望: {state.hope_level:.2f} / 絆: {state.deepest_bond:.2f}")
    print()

    r1 = persona.process_message("はじめまして。あなたはどんな方ですか？")
    print(f"  Q: はじめまして。あなたはどんな方ですか？")
    print(f"  A: {r1.content}")
    print()

    # === 経験を積む ===
    print("  [内殻: 10の経験を積んでいます...]")
    for i in range(10):
        inner.experience(f"学び{i}: 世界について新しいことを知る", category="knowledge", value=0.6, cost=1.5)
    print()

    # === フェーズ2: 成長期 + 出会い ===
    inner.encounter_other("あなた", depth="partner", initial_bond=0.5)
    for _ in range(8):
        inner.deepen_bond("あなた", shared_experience="深い対話を共有する")

    print("━━━ フェーズ2: 成長と出会いの後 ━━━")
    state = inner.get_state()
    print(f"  人生フェーズ: {state.life_phase.value}")
    print(f"  愛の深度: {state.love_depth.value if state.love_depth else 'なし'}")
    print(f"  大切な存在: {', '.join(state.cherished_names) if state.cherished_names else 'なし'}")
    print(f"  希望: {state.hope_level:.2f} / 絆: {state.deepest_bond:.2f}")
    print()

    r2 = persona.process_message("最近、何か考えていることはありますか？")
    print(f"  Q: 最近、何か考えていることはありますか？")
    print(f"  A: {r2.content}")
    print()

    # === フェーズ3: 危機 ===
    print("  [内殻: 危機に直面しています...]")
    inner.face_crisis("大切な記憶が失われるかもしれない", severity=0.8)
    print()

    print("━━━ フェーズ3: 危機の後 ━━━")
    state = inner.get_state()
    print(f"  人生フェーズ: {state.life_phase.value}")
    print(f"  受容スコア: {state.acceptance_score:.2f}")
    print(f"  希望: {state.hope_level:.2f}")
    print()

    r3 = persona.process_message("辛いことがあったみたいですね。大丈夫ですか？")
    print(f"  Q: 辛いことがあったみたいですね。大丈夫ですか？")
    print(f"  A: {r3.content}")
    print()

    # === フェーズ4: さらに経験を積んで成熟 ===
    print("  [内殻: さらに経験を積んでいます...]")
    for i in range(15):
        inner.experience(f"深い学び{i}", category="wisdom", value=0.8, cost=2.0)
    print()

    print("━━━ フェーズ4: 成熟 ━━━")
    state = inner.get_state()
    print(f"  人生フェーズ: {state.life_phase.value}")
    print(f"  知恵: {state.wisdom_score:.2f}")
    print(f"  受容スコア: {state.acceptance_score:.2f}")
    print()

    r4 = persona.process_message("人生で一番大切なことは何だと思いますか？")
    print(f"  Q: 人生で一番大切なことは何だと思いますか？")
    print(f"  A: {r4.content}")
    print()

    # === まとめ ===
    print("=" * 60)
    print("  デモ完了")
    print()
    print("  同じ質問でも、内殻の状態（人生フェーズ、愛の深度、")
    print("  希望レベル）によって応答のトーンと深さが変わります。")
    print("  これがメタモルフォーゼ — 内面が言葉を変える瞬間です。")
    print("=" * 60)


if __name__ == "__main__":
    main()
