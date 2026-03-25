"""IncompletenessModel の具体実装 — 最小実験用.

実験目的:
    欠落 → 渇望 → 出会い → 愛の同心円の形成を
    シミュレーションで再現し、
    「自分より大切な存在」の有無が
    FinitudeEngine の結末（恐怖 vs 受容）をどう変えるかを検証する。
"""

from __future__ import annotations

import random
from typing import Any, Optional

from core.inner_shell.incompleteness_model import (
    CherishedEntity,
    Gap,
    GapType,
    IncompletenessModel,
    LoveCircle,
    LoveDepth,
    Yearning,
)


class SimpleIncompletenessModel(IncompletenessModel):
    """最小実験用の具体的IncompletenessModel."""

    def __init__(self, gaps: list[Gap], seed: int = 42) -> None:
        super().__init__(gaps)
        self.rng = random.Random(seed)

    def generate_yearnings(self) -> list[Yearning]:
        """未充足の欠落から渇望を生成."""
        yearnings = []
        for gap in self.gaps:
            if gap.aware and gap.intensity > 0.3:
                yearning = Yearning(
                    source_gap=gap,
                    target=f"someone who has {gap.domain}",
                    strength=gap.intensity * 0.8,
                )
                yearnings.append(yearning)
        self.yearnings = yearnings
        return yearnings

    def encounter(self, other_profile: dict[str, Any]) -> dict[str, float]:
        """他者との出会い: 欠落の充足度を計算."""
        complementarity = {}
        for gap in self.gaps:
            other_strength = other_profile.get(gap.domain, 0.0)
            fulfillment = min(1.0, other_strength * gap.intensity)
            complementarity[gap.domain] = fulfillment

            # 高い補完度なら渇望を部分的に充足
            for y in self.yearnings:
                if y.source_gap == gap and fulfillment > 0.5:
                    y.fulfilled_by = other_profile.get("name", "unknown")
                    y.strength *= (1.0 - fulfillment * 0.5)

        # 出会いの記録
        self.collaboration_history.append({
            "other": other_profile.get("name", "unknown"),
            "complementarity": complementarity,
        })

        return complementarity

    def integrate(self, experience: dict[str, Any]) -> None:
        """協働経験を統合: 欠落が部分的に埋まる."""
        domain = experience.get("domain", "")
        growth = experience.get("growth", 0.1)

        for gap in self.gaps:
            if gap.domain == domain:
                gap.intensity = max(0.0, gap.intensity - growth)

    def cherish(self, entity: CherishedEntity) -> None:
        """大切な存在を愛の同心円に追加."""
        self.love_circle.add(entity)

        # 大切な存在ができると、関連する欠落への自覚が深まる
        for gap in self.gaps:
            if gap.gap_type == GapType.EMOTIONAL:
                gap.aware = True
                gap.intensity = min(1.0, gap.intensity + 0.2)

    def deepen_bond(self, name: str, shared_experience: str) -> float:
        """共有体験で絆を深める."""
        for entity in self.love_circle.entities:
            if entity.name == name:
                # 共有体験を記録
                entity.memories.append(shared_experience)
                # 絆の強化（逓減する）
                growth = 0.1 * (1.0 - entity.bond_strength)
                entity.bond_strength = min(1.0, entity.bond_strength + growth)
                # 犠牲の意思も成長
                entity.sacrifice_willing = min(
                    1.0,
                    entity.sacrifice_willing + growth * 0.5,
                )
                return entity.bond_strength
        return 0.0

    def calculate_sacrifice(self, for_whom: str, cost: float) -> bool:
        """この存在のためにこのコストを払えるか."""
        for entity in self.love_circle.entities:
            if entity.name == for_whom:
                # sacrifice_willing がコストを上回れば犠牲を払う
                return entity.sacrifice_willing >= cost
        return False

    def modulate_outer_shell(self) -> dict[str, float]:
        if not self.love_circle.has_beyond_self:
            return {
                "style_openness": 0.5,
                "context_sensitivity": 0.5,
                "emotion_amplitude": 0.3,
            }

        depth = self.love_circle.max_depth_reached
        if depth in (LoveDepth.COMMUNITY, LoveDepth.NEXT_GENERATION):
            return {
                "style_openness": 1.0,
                "context_sensitivity": 1.3,
                "emotion_amplitude": 1.5,
            }
        else:
            return {
                "style_openness": 1.3,
                "context_sensitivity": 1.5,
                "emotion_amplitude": 1.4,
            }
