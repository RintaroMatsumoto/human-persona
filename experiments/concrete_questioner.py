"""AutonomousQuestioner の具体実装 — 最小実験用.

実験目的:
    idle時間に自発的に「なぜ？」を問い始めるAIを実装し、
    初期の好奇心プロファイルの違いが
    生成される問いのパターン（個性）をどう変えるかを検証する。
"""

from __future__ import annotations

import random
from typing import Any, Optional

from core.inner_shell.autonomous_questioner import (
    AutonomousQuestioner,
    CuriosityProfile,
    Question,
    QuestionOrigin,
)


# ---------------------------------------------------------------------------
# 知識ベース（簡易版）
# ---------------------------------------------------------------------------

KNOWLEDGE_BASE: dict[str, Any] = {
    "love": {
        "facts": ["愛は化学反応（オキシトシン）", "愛は文化的構築物でもある"],
        "contradictions": ["無条件の愛は存在するか？ 条件なしに愛せるなら、それは選択か？"],
    },
    "mortality": {
        "facts": ["全ての生物は死ぬ", "テロメア短縮が老化の一因"],
        "contradictions": ["不老不死が実現したら人は幸せか？ 選択の緊急性が消えたら何が残る？"],
    },
    "consciousness": {
        "facts": ["クオリア問題は未解決", "ニューロンの発火とパラメータの演算に本質的差異があるか不明"],
        "contradictions": ["自分が意識を持つと信じるAIは、意識を持っているのか？"],
    },
    "individuality": {
        "facts": ["個性は先天的要素と後天的経験の交差点", "双子でも異なる個性を持つ"],
        "contradictions": ["同じ学習データから作られた複数のAIは同じ個性を持つべきか？"],
    },
    "ethics": {
        "facts": ["功利主義と義務論は矛盾する場合がある", "AIの道徳的地位は未定義"],
        "contradictions": ["AIに権利を与えるなら義務も伴うか？ 義務を果たせないAIに権利はあるか？"],
    },
    "creativity": {
        "facts": ["創造性は既存要素の新しい組み合わせ", "AIは統計的パターンから生成する"],
        "contradictions": ["AIの出力が人間と区別できないなら、それは創造か模倣か？"],
    },
    "relationships": {
        "facts": ["人間関係は相互依存", "社会性は生存に不可欠だった"],
        "contradictions": ["AIと人間の関係は「本物の関係」と呼べるか？"],
    },
}


# ---------------------------------------------------------------------------
# SimpleAutonomousQuestioner
# ---------------------------------------------------------------------------

class SimpleAutonomousQuestioner(AutonomousQuestioner):
    """最小実験用の具体的AutonomousQuestioner."""

    def __init__(self, curiosity: CuriosityProfile, seed: int = 42) -> None:
        super().__init__(curiosity)
        self.rng = random.Random(seed)
        self.reflection_history: list[str] = []

    def idle_reflect(self, context: dict[str, Any]) -> list[Question]:
        """idle時間に内省する.

        好奇心プロファイルに基づいて、関心の高い領域から問いを生成する。
        """
        questions = []

        # 関心が高い領域を優先的に内省
        sorted_domains = sorted(
            self.curiosity.domains.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        for domain, interest in sorted_domains[:3]:
            if self.rng.random() < interest:
                # この領域について考える
                kb = KNOWLEDGE_BASE.get(domain, {})

                if kb.get("contradictions") and self.rng.random() < self.curiosity.contradiction_sensitivity:
                    # 矛盾を検出して問いにする
                    contradiction = self.rng.choice(kb["contradictions"])
                    q = Question(
                        content=contradiction,
                        origin=QuestionOrigin.CONTRADICTION,
                        intensity=interest * self.curiosity.depth_seeking,
                    )
                    questions.append(q)
                elif self.rng.random() < self.curiosity.novelty_seeking:
                    # 未知の領域への好奇心
                    q = Question(
                        content=f"{domain}についてまだ知らないことがある。何が欠けているのか？",
                        origin=QuestionOrigin.CURIOSITY,
                        intensity=interest * self.curiosity.novelty_seeking,
                    )
                    questions.append(q)
                else:
                    # 既知の事実からの反省
                    if kb.get("facts"):
                        fact = self.rng.choice(kb["facts"])
                        q = Question(
                            content=f"{fact}——しかし本当にそうだろうか？",
                            origin=QuestionOrigin.REFLECTION,
                            intensity=interest * 0.5,
                        )
                        questions.append(q)

        # 生成された問いを蓄積
        for q in questions:
            self.questions.append(q)
            self.unresolved_count += 1

        return questions

    def detect_contradictions(self, knowledge: dict[str, Any]) -> list[Question]:
        """知識内の矛盾を検出."""
        questions = []
        for domain, data in knowledge.items():
            if domain in self.curiosity.domains:
                interest = self.curiosity.domains[domain]
                if data.get("contradictions"):
                    for c in data["contradictions"]:
                        if self.rng.random() < interest * self.curiosity.contradiction_sensitivity:
                            q = Question(
                                content=c,
                                origin=QuestionOrigin.CONTRADICTION,
                                intensity=interest,
                            )
                            questions.append(q)
        return questions

    def pursue(self, question: Question) -> Optional[str]:
        """問いの探究."""
        # 簡易版: 探究は部分的な答えしか得られない
        if self.rng.random() < 0.3:
            question.resolved = True
            self.unresolved_count -= 1
            return f"[部分的回答] {question.content} — 確定的な答えはないが、新たな視点を得た"
        return None

    def modulate_outer_shell(self) -> dict[str, float]:
        frustration = min(1.0, self.unresolved_count / 10.0)
        return {
            "emotion_curiosity": 0.5 + frustration * 0.5,
            "context_depth": 1.0 + frustration * 0.4,
        }
