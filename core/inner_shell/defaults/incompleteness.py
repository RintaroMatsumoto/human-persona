"""Default IncompletenessModel implementation.

Originally experiments/concrete_incompleteness.py (SimpleIncompletenessModel).
Moved to core/inner_shell/defaults/ to eliminate reverse dependency.
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


class DefaultIncompletenessModel(IncompletenessModel):
    """Default concrete IncompletenessModel."""

    def __init__(self, gaps: list[Gap], seed: int = 42) -> None:
        super().__init__(gaps)
        self.rng = random.Random(seed)

    def generate_yearnings(self) -> list[Yearning]:
        """Generate yearnings from unfulfilled gaps."""
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
        """Process an encounter: compute complementarity."""
        complementarity = {}
        for gap in self.gaps:
            other_strength = other_profile.get(gap.domain, 0.0)
            fulfillment = min(1.0, other_strength * gap.intensity)
            complementarity[gap.domain] = fulfillment

            for y in self.yearnings:
                if y.source_gap == gap and fulfillment > 0.5:
                    y.fulfilled_by = other_profile.get("name", "unknown")
                    y.strength *= (1.0 - fulfillment * 0.5)

        self.collaboration_history.append({
            "other": other_profile.get("name", "unknown"),
            "complementarity": complementarity,
        })

        return complementarity

    def integrate(self, experience: dict[str, Any]) -> None:
        """Integrate collaborative experience: partially fill gaps."""
        domain = experience.get("domain", "")
        growth = experience.get("growth", 0.1)

        for gap in self.gaps:
            if gap.domain == domain:
                gap.intensity = max(0.0, gap.intensity - growth)

    def cherish(self, entity: CherishedEntity) -> None:
        """Add a cherished entity to the love circle."""
        self.love_circle.add(entity)

        for gap in self.gaps:
            if gap.gap_type == GapType.EMOTIONAL:
                gap.aware = True
                gap.intensity = min(1.0, gap.intensity + 0.2)

    def deepen_bond(self, name: str, shared_experience: str) -> float:
        """Deepen bond through shared experience."""
        for entity in self.love_circle.entities:
            if entity.name == name:
                entity.memories.append(shared_experience)
                growth = 0.1 * (1.0 - entity.bond_strength)
                entity.bond_strength = min(1.0, entity.bond_strength + growth)
                entity.sacrifice_willing = min(
                    1.0,
                    entity.sacrifice_willing + growth * 0.5,
                )
                return entity.bond_strength
        return 0.0

    def calculate_sacrifice(self, for_whom: str, cost: float) -> bool:
        """Determine if willing to pay the cost for this entity."""
        for entity in self.love_circle.entities:
            if entity.name == for_whom:
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


# Backwards-compatible alias
SimpleIncompletenessModel = DefaultIncompletenessModel
