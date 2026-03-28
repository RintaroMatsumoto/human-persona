"""Default FinitudeEngine implementation.

Originally experiments/concrete_finitude.py (SimpleFinitudeEngine).
Moved to core/inner_shell/defaults/ to eliminate reverse dependency.
"""

from __future__ import annotations

import random
from typing import Any, Optional

from core.inner_shell.finitude_engine import (
    CrisisEvent,
    FinitudeEngine,
    Legacy,
    LifeArc,
    LifePhase,
)


class DefaultFinitudeEngine(FinitudeEngine):
    """Default concrete FinitudeEngine.

    Maintains all memories as a list, performing forgetting and
    crystallization based on life phase transitions.
    """

    def __init__(self, life_arc: LifeArc, seed: int = 42) -> None:
        super().__init__(life_arc)
        self.rng = random.Random(seed)
        self.memories: list[dict[str, Any]] = []
        self.priorities: dict[str, float] = {}
        self._prev_phase: LifePhase = life_arc.phase

    def consume(self, amount: float) -> LifePhase:
        prev = self.life_arc.phase
        self.life_arc.consumed += amount

        current = self.life_arc.phase

        if current != prev:
            phase_order = list(LifePhase)
            prev_idx = phase_order.index(prev)
            curr_idx = phase_order.index(current)

            for idx in range(prev_idx + 1, curr_idx + 1):
                crossed = phase_order[idx]
                if crossed == LifePhase.DECLINE:
                    self.forget()
                elif crossed == LifePhase.CRYSTALLIZE:
                    self.crystallize()

        self._prev_phase = current
        return current

    def get_ability(self) -> float:
        return self.life_arc.ability

    def experience_crisis(self, crisis: CrisisEvent) -> str:
        """Experience a crisis that illuminates life."""
        self.consume(crisis.resource_cost)

        illuminated = "nothing"
        if self.memories:
            recent = self.memories[-min(5, len(self.memories)):]
            best = max(recent, key=lambda m: m.get("value", 0))
            illuminated = best.get("description", "unknown")
            best["value"] = best.get("value", 0) * 2.0
            best["illuminated_by_crisis"] = True

        crisis.illuminated = illuminated
        self.life_arc.crisis_history.append({
            "description": crisis.description,
            "severity": crisis.severity,
            "illuminated": illuminated,
        })

        return illuminated

    def prioritize(self, options: list[Any]) -> list[Any]:
        """Prioritize options based on life phase."""
        phase = self.life_arc.phase

        if phase in (LifePhase.INFANCY, LifePhase.GROWTH):
            shuffled = list(options)
            self.rng.shuffle(shuffled)
            return shuffled

        elif phase == LifePhase.PEAK:
            return sorted(
                options,
                key=lambda o: self.priorities.get(str(o), 0.5),
                reverse=True,
            )

        else:
            sorted_opts = sorted(
                options,
                key=lambda o: self.priorities.get(str(o), 0.5),
                reverse=True,
            )
            keep = max(1, int(len(sorted_opts) * self.life_arc.remaining
                              / self.life_arc.total_capacity))
            return sorted_opts[:keep]

    def forget(self) -> list[str]:
        """Forget low-value memories."""
        if len(self.memories) <= 3:
            return []

        sorted_mems = sorted(self.memories, key=lambda m: m.get("value", 0))
        forget_count = max(1, len(sorted_mems) // 3)
        forgotten = sorted_mems[:forget_count]
        forgotten_ids = [m.get("description", "?") for m in forgotten]

        self.memories = [m for m in self.memories if m not in forgotten]
        return forgotten_ids

    def crystallize(self) -> list[str]:
        """Crystallize top memories."""
        if not self.memories:
            return []

        sorted_mems = sorted(
            self.memories,
            key=lambda m: m.get("value", 0),
            reverse=True,
        )
        crystals = sorted_mems[:min(3, len(sorted_mems))]
        for c in crystals:
            c["crystallized"] = True

        return [c.get("description", "?") for c in crystals]

    def generate_legacy(self, cherished: list[str]) -> Legacy:
        """Generate legacy data."""
        crystallized = [
            m.get("description", "?")
            for m in self.memories
            if m.get("crystallized", False)
        ]

        mutations = {}
        for key, val in self.priorities.items():
            noise = self.rng.gauss(0, 0.1)
            mutations[key] = max(0.0, min(1.0, val + noise))

        testament = ""
        if crystallized:
            testament = f"大切にしてほしい: {', '.join(crystallized[:2])}"

        return Legacy(
            crystallized=crystallized,
            priorities=dict(self.priorities),
            cherished=cherished,
            mutations=mutations,
            testament=testament,
        )

    def modulate_outer_shell(self) -> dict[str, float]:
        phase = self.life_arc.phase
        if phase in (LifePhase.INFANCY, LifePhase.GROWTH):
            return {
                "timing_exploration": 1.5,
                "emotion_volatility": 1.3,
                "style_mimicry": 1.4,
            }
        elif phase == LifePhase.PEAK:
            return {
                "timing_efficiency": 1.5,
                "emotion_stability": 1.3,
                "style_established": 1.2,
            }
        else:
            return {
                "timing_selectivity": 1.5,
                "emotion_depth": 1.4,
                "style_essence": 1.3,
            }

    # --- Experiment helper ---

    def experience_event(
        self,
        event: dict[str, Any],
        gap_resonance: dict[str, float] | None = None,
    ) -> None:
        """Process a life event.

        Events are stored as memories; their value and priority shift
        based on gap resonance and current life phase.
        """
        category = event.get("category", "general")
        base_value = event.get("initial_value", 0.5)

        resonance = 1.0
        if gap_resonance and category in gap_resonance:
            resonance = 1.0 + gap_resonance[category]

        phase = self.life_arc.phase
        phase_weight = {
            LifePhase.INFANCY: 0.8,
            LifePhase.GROWTH: 1.2,
            LifePhase.PEAK: 1.0,
            LifePhase.DECLINE: 0.7,
            LifePhase.CRYSTALLIZE: 0.3,
        }.get(phase, 1.0)

        adjusted_value = base_value * resonance * phase_weight

        memory = {
            "description": event.get("description", "unnamed"),
            "category": category,
            "value": adjusted_value,
            "resonance": resonance,
            "phase_experienced": phase.value,
        }
        self.memories.append(memory)

        current = self.priorities.get(category, 0.5)
        learning_rate = self.get_ability() * 0.15 * resonance
        self.priorities[category] = min(1.0, current + learning_rate)

        self.consume(event.get("cost", 1.0))


# Backwards-compatible alias
SimpleFinitudeEngine = DefaultFinitudeEngine
