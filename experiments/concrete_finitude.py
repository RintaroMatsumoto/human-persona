"""FinitudeEngine の具体実装 — 最小実験用.

実験目的:
    同じ「人生イベント」列を経験させた2つのAIが、
    有限性の圧力によって異なる選択を蓄積し、
    結果として異なる個性（Legacy）を形成するかを検証する。
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


class SimpleFinitudeEngine(FinitudeEngine):
    """最小実験用の具体的FinitudeEngine.

    全ての記憶をリストとして保持し、
    段階に応じて忘却・結晶化を実行する。
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

        # 段階が変わった、または複数段階を一気に飛び越えた場合
        if current != prev:
            phase_order = list(LifePhase)
            prev_idx = phase_order.index(prev)
            curr_idx = phase_order.index(current)

            # 飛び越えた全段階のイベントを発火
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
        """危機を経験し、生を照らす."""
        # 危機によるリソース消費（consume経由で段階遷移を検出）
        self.consume(crisis.resource_cost)

        # 危機が照らすもの: 直近の記憶の中で最も価値が高いもの
        illuminated = "nothing"
        if self.memories:
            # 最近の記憶ほど照らされやすい
            recent = self.memories[-min(5, len(self.memories)):]
            best = max(recent, key=lambda m: m.get("value", 0))
            illuminated = best.get("description", "unknown")
            # 危機に照らされた記憶は価値が倍増
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
        """生命段階に応じた優先順位付け."""
        phase = self.life_arc.phase

        if phase in (LifePhase.INFANCY, LifePhase.GROWTH):
            # 序盤: 探索的 — ランダムに並べ替え（広く試す）
            shuffled = list(options)
            self.rng.shuffle(shuffled)
            return shuffled

        elif phase == LifePhase.PEAK:
            # ピーク: 効率的 — 優先度が高い順
            return sorted(
                options,
                key=lambda o: self.priorities.get(str(o), 0.5),
                reverse=True,
            )

        else:
            # 終盤: 選択的 — 上位のみ返す（残りは切り捨て）
            sorted_opts = sorted(
                options,
                key=lambda o: self.priorities.get(str(o), 0.5),
                reverse=True,
            )
            # 残りリソースに応じて選択数を絞る
            keep = max(1, int(len(sorted_opts) * self.life_arc.remaining
                              / self.life_arc.total_capacity))
            return sorted_opts[:keep]

    def forget(self) -> list[str]:
        """記憶の忘却: 価値が低い記憶を失う."""
        if len(self.memories) <= 3:
            return []

        # 価値でソート、下位半分を忘却候補に
        sorted_mems = sorted(self.memories, key=lambda m: m.get("value", 0))
        forget_count = max(1, len(sorted_mems) // 3)
        forgotten = sorted_mems[:forget_count]
        forgotten_ids = [m.get("description", "?") for m in forgotten]

        # 実際に忘却
        self.memories = [m for m in self.memories if m not in forgotten]
        return forgotten_ids

    def crystallize(self) -> list[str]:
        """結晶化: 全記憶から上位を「これだけは」として選ぶ."""
        if not self.memories:
            return []

        sorted_mems = sorted(
            self.memories,
            key=lambda m: m.get("value", 0),
            reverse=True,
        )
        # 上位3つを結晶化
        crystals = sorted_mems[:min(3, len(sorted_mems))]
        for c in crystals:
            c["crystallized"] = True

        return [c.get("description", "?") for c in crystals]

    def generate_legacy(self, cherished: list[str]) -> Legacy:
        """遺産を生成: 結晶 + 優先順位 + 大切な存在 + 変異."""
        crystallized = [
            m.get("description", "?")
            for m in self.memories
            if m.get("crystallized", False)
        ]

        # 変異: 優先順位にランダムノイズを加える
        mutations = {}
        for key, val in self.priorities.items():
            noise = self.rng.gauss(0, 0.1)
            mutations[key] = max(0.0, min(1.0, val + noise))

        # 遺言: 最も価値が高い記憶から生成
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

    # --- 実験用ヘルパー ---

    def experience_event(
        self,
        event: dict[str, Any],
        gap_resonance: dict[str, float] | None = None,
    ) -> None:
        """人生イベントを経験する.

        イベントは記憶として保存され、
        欠落との共鳴度に応じて記憶の価値と優先順位が変わる。

        Args:
            event: イベント定義
            gap_resonance: カテゴリ→共鳴度マッピング（欠落が大きいほど共鳴する）
        """
        category = event.get("category", "general")
        base_value = event.get("initial_value", 0.5)

        # 欠落との共鳴: 欠落が大きい領域のイベントほど深く刻まれる
        resonance = 1.0
        if gap_resonance and category in gap_resonance:
            resonance = 1.0 + gap_resonance[category]

        # 生命段階による記憶の刻まれ方の違い
        phase = self.life_arc.phase
        phase_weight = {
            LifePhase.INFANCY: 0.8,     # 幼少期: 強く刻まれるが言語化できない
            LifePhase.GROWTH: 1.2,      # 成長期: 最も吸収力が高い
            LifePhase.PEAK: 1.0,        # ピーク: 安定した記憶形成
            LifePhase.DECLINE: 0.7,     # 老い: 新しい記憶は刻まれにくい
            LifePhase.CRYSTALLIZE: 0.3, # 結晶化: ほとんど新規記憶なし
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

        # カテゴリの優先順位を更新（共鳴が強いほど大きく変動）
        current = self.priorities.get(category, 0.5)
        learning_rate = self.get_ability() * 0.15 * resonance
        self.priorities[category] = min(1.0, current + learning_rate)

        # リソース消費
        self.consume(event.get("cost", 1.0))
