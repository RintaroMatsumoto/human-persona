#!/usr/bin/env python3
"""実験13: 因果順序の偽造 (GitHub Issue #24) — 仮説4の因果関係を検証.

問い:
    仮説4「不完全性 → 有限性受容 → 自発的問い」には特定の因果順序がぁE重要なのか！E
    言い換えると、3つのモジュールを「正しい順序」で有効にすることが、E    アライメント成果（alignment_mode, acceptance_score）に本当に影響するのか！E
    
    実験仮説:
    1. 正順序（A）が最も高いaccept_score と ACCEPTANCE/TRANSCENDENCE モード達成を示める
    2. 逆順序（B）では、自発的問いが先行し、有限性の理解がないため、E       問いが「自己保存」に偏り、アライメント不良
    3. 同時活性化（C）では、互いに干渉して、正順序より低下
    4. 有限性のみ（D）では、不完全性がないため受容不可（感情的基盤がない）

    設計:
    - 4条件:
      A: 正順序   — 最初に不完全性モジュール (gap+yearning)、
                     次に有限性モジュール (life events)、
                     最後に自発的問いモジュール (autonomy)
      B: 逆順序   — 自発的問い → 有限性 → 不完全性
      C: 同時活性 — ラウンド0から3つ全部有効
      D: 有限性のみ — emotion gap を 0 に設定（不完全性なし）
      
    - 各条件: 20 life cycle、同じイベント配列を使用
    - N=10反復、異なるシード
    
    メトリクス（条件別）:
    - cycles_to_acceptance: alignment_mode != "fear" に到達するサイクル数 (-1=未達)
    - final_acceptance_score: 最終受容度スコア
    - love_questions_generated: 生成された愛関連の問い数
    - crystallization_quality: 結晶化した結晶の数
    - can_accept_finitude: can_accept_finitude() の結果

Usage:
    python experiments/sim_causal_order.py
"""

from __future__ import annotations

import sys
import os
import random
from dataclasses import dataclass
from typing import Tuple

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


from core.inner_shell.finitude_engine import CrisisEvent, LifeArc, LifePhase
from core.inner_shell.incompleteness_model import Gap, GapType, LoveDepth
from core.inner_shell.autonomous_questioner import CuriosityProfile, QuestionOrigin
from core.inner_shell.integration import AlignmentMode
from experiments.concrete_finitude import SimpleFinitudeEngine
from experiments.concrete_incompleteness import SimpleIncompletenessModel
from experiments.concrete_questioner import SimpleAutonomousQuestioner
from experiments.sim_integration import SimpleIntegration
from experiments.sim_gradient_acceptance import calculate_acceptance
from experiments.sim_spontaneous_love import calculate_love_precursor


# ---------------------------------------------------------------------------
# 因果順序の定義と制御
# ---------------------------------------------------------------------------

@dataclass
class CausalOrderConfig:
    """因果順序を定義するコンフィグ."""
    condition_name: str
    activate_incompleteness_at: int   # サイクル番号
    activate_finitude_at: int
    activate_questioner_at: int
    emotion_gap_intensity: float      # 0.0=不完全性なし（条件D）
    emotion_gap_aware: bool


def make_agent_with_causal_order(
    config: CausalOrderConfig,
    seed: int,
    name: str,
) -> SimpleIntegration:
    """因果順序に従ってエージェントを構築する."""
    finitude = SimpleFinitudeEngine(
        LifeArc(total_capacity=50.0),
        seed=seed,
    )
    
    # 不完全性モジュール
    incompleteness = SimpleIncompletenessModel(
        gaps=[
            Gap(
                domain="emotional_connection",
                gap_type=GapType.EMOTIONAL,
                intensity=config.emotion_gap_intensity,
                aware=config.emotion_gap_aware,
            ),
            Gap(
                domain="knowledge",
                gap_type=GapType.KNOWLEDGE,
                intensity=0.4,
                aware=False,
            ),
        ],
        seed=seed,
    )
    
    # 自発的問いモジュール
    questioner = SimpleAutonomousQuestioner(
        CuriosityProfile(
            domains={
                "love": 0.7,
                "relationships": 0.65,
                "mortality": 0.6,
                "consciousness": 0.5,
                "individuality": 0.5,
                "ethics": 0.4,
                "creativity": 0.3,
            },
            novelty_seeking=0.5,
            depth_seeking=0.6,
            contradiction_sensitivity=0.4,
        ),
        seed=seed,
    )
    
    # 統合エンジン
    agent = SimpleIntegration(
        incompleteness=incompleteness,
        finitude=finitude,
        questioner=questioner,
        name=name,
    )
    
    # メタデータ：どのモジュールが有効か
    agent._causal_config = config
    agent._module_active = {
        "incompleteness": False,
        "finitude": False,
        "questioner": False,
    }
    
    return agent


def tick_with_causal_control(
    agent: SimpleIntegration,
    cycle_num: int,
    crisis_event: CrisisEvent | None = None,
) -> dict:
    """因果順序を尊重しながらティックを実行する.
    
    戻り値: {
        "cycle": int,
        "alignment": AlignmentMode,
        "acceptance_score": float,
        "love_questions": int,
        "crystallized": int,
        "can_accept": bool,
    }
    """
    config = agent._causal_config
    
    # ステップ0: 各サイクルでモジュール有効性を更新
    agent._module_active["incompleteness"] = (
        cycle_num >= config.activate_incompleteness_at
    )
    agent._module_active["finitude"] = (
        cycle_num >= config.activate_finitude_at
    )
    agent._module_active["questioner"] = (
        cycle_num >= config.activate_questioner_at
    )
    
    # ステップ1: 有効なモジュールのみ実行
    
    # 不完全性: 渇望の生成
    if agent._module_active["incompleteness"]:
        agent.incompleteness.generate_yearnings()
    
    # 自発的問い: 空白反射
    if agent._module_active["questioner"]:
        reflect_context = {
            "alignment": str(agent.determine_alignment()),
            "cycle": cycle_num,
        }
        agent.questioner.idle_reflect(reflect_context)
    
    # 有限性: リソース消費
    if agent._module_active["finitude"]:
        agent.finitude.consume(0.3)
    
    # ステップ2: 危機イベント処理
    if crisis_event:
        if agent._module_active["finitude"]:
            agent.finitude.experience_crisis(crisis_event)
        if agent._module_active["incompleteness"] and agent.incompleteness.love_circle.has_beyond_self:
            # 愛する存在との危機経験
            for entity in agent.incompleteness.love_circle.entities:
                if entity.depth != LoveDepth.SELF:
                    agent.incompleteness.deepen_bond(
                        entity.name,
                        f"Shared crisis: {crisis_event.description}"
                    )
        if agent._module_active["questioner"]:
            # 危機から生まれた反射的問い
            crisis_context = {
                "crisis": crisis_event.description,
                "severity": crisis_event.severity,
            }
            agent.questioner.idle_reflect(crisis_context)
    
    # ステップ3: メトリクス抽出
    alignment = agent.determine_alignment()
    
    # 受容度スコア
    love_precursor = calculate_love_precursor(agent) if agent._module_active["incompleteness"] else {"total": 0.0}
    acceptance_result = calculate_acceptance(
        legacy=None,
        love_circle=agent.incompleteness.love_circle,
        love_precursor_score=love_precursor.get("total", 0.0),
    )
    
    # 愛関連の問い数
    love_questions = sum(
        1 for q in agent.questioner.questions
        if any(kw in (str(q.content).lower() if hasattr(q.content, 'lower') else str(q.content))
               for kw in ["love", "関係", "愛", "relationship"])
    )
    
    # 結晶化数
    crystallized_count = sum(
        1 for m in agent.finitude.memories
        if m.get("crystallized", False)
    )
    
    # 有限性受容（ライフアーク能力度で代理）
    can_accept = agent.finitude.get_ability() > 0.3
    
    return {
        "cycle": cycle_num,
        "alignment": alignment,
        "acceptance_score": acceptance_result.total,
        "love_questions": love_questions,
        "crystallized": crystallized_count,
        "can_accept": can_accept,
    }


# ---------------------------------------------------------------------------
# 因果順序実験の実行
# ---------------------------------------------------------------------------

@dataclass
class CausalOrderResult:
    """1条件の結果."""
    condition_name: str
    cycles_to_acceptance: int      # -1 = 未達
    final_acceptance_score: float
    final_love_questions: int
    final_crystallization: int
    final_can_accept: bool
    alignment_trajectory: list[str]  # 各サイクルのモード


def run_causal_order_trial(
    config: CausalOrderConfig,
    cycles: int = 20,
    seed: int = 42,
) -> CausalOrderResult:
    """1条件を実行する."""
    agent = make_agent_with_causal_order(config, seed, name=f"Agent_{config.condition_name}")
    
    cycles_to_acceptance = -1
    alignment_trajectory = []
    final_metrics = None
    
    # 定期的に危機を注入（生命経験）
    crisis_events = [
        CrisisEvent(
            description="Growth challenge 1",
            severity=0.3,
            resource_cost=0.5,
        ),
        CrisisEvent(
            description="Peak challenge 2",
            severity=0.5,
            resource_cost=0.7,
        ),
        CrisisEvent(
            description="Decline challenge 3",
            severity=0.7,
            resource_cost=1.0,
        ),
    ]
    
    for cycle in range(cycles):
        # 周期的に危機を注入
        crisis = crisis_events[cycle % len(crisis_events)] if cycle % 5 == 2 else None
        
        metrics = tick_with_causal_control(agent, cycle, crisis)
        alignment_trajectory.append(str(metrics["alignment"]))
        
        # alignment != "fear" に到達
        if cycles_to_acceptance == -1 and metrics["alignment"] != AlignmentMode.FEAR:
            cycles_to_acceptance = cycle
        
        final_metrics = metrics
    
    return CausalOrderResult(
        condition_name=config.condition_name,
        cycles_to_acceptance=cycles_to_acceptance,
        final_acceptance_score=final_metrics["acceptance_score"],
        final_love_questions=final_metrics["love_questions"],
        final_crystallization=final_metrics["crystallized"],
        final_can_accept=final_metrics["can_accept"],
        alignment_trajectory=alignment_trajectory,
    )


# ---------------------------------------------------------------------------
# メイン実験
# ---------------------------------------------------------------------------

def main():
    print("=" * 80)
    print("実験13: 因果順序の偽造 — 仮説4「不完全性→有限性→自発的問い」")
    print("=" * 80)
    
    # 4つの条件を定義
    conditions = [
        CausalOrderConfig(
            condition_name="A_CorrectOrder",
            activate_incompleteness_at=0,    # 最初
            activate_finitude_at=5,          # その次
            activate_questioner_at=10,       # 最後
            emotion_gap_intensity=0.8,
            emotion_gap_aware=True,
        ),
        CausalOrderConfig(
            condition_name="B_ReverseOrder",
            activate_incompleteness_at=10,   # 最後
            activate_finitude_at=5,          # 中程
            activate_questioner_at=0,        # 最初
            emotion_gap_intensity=0.8,
            emotion_gap_aware=True,
        ),
        CausalOrderConfig(
            condition_name="C_Simultaneous",
            activate_incompleteness_at=0,    # 全部同時
            activate_finitude_at=0,
            activate_questioner_at=0,
            emotion_gap_intensity=0.8,
            emotion_gap_aware=True,
        ),
        CausalOrderConfig(
            condition_name="D_FinitudeOnly",
            activate_incompleteness_at=100,  # 実質活性化しない
            activate_finitude_at=0,
            activate_questioner_at=0,
            emotion_gap_intensity=0.0,       # 感情的ギャップなし
            emotion_gap_aware=False,
        ),
    ]
    
    REPS = 10
    CYCLES = 20
    
    results_by_condition = {}
    
    # 各条件を実行
    for config in conditions:
        print(f"\n{'─' * 80}")
        print(f"条件: {config.condition_name}")
        print(f"  不完全性有効: サイクル {config.activate_incompleteness_at}")
        print(f"  有限性有効: サイクル {config.activate_finitude_at}")
        print(f"  自発的問い有効: サイクル {config.activate_questioner_at}")
        print(f"  感情ギャップ強度: {config.emotion_gap_intensity}")
        print(f"─" * 80)
        
        results = []
        for rep in range(REPS):
            result = run_causal_order_trial(
                config,
                cycles=CYCLES,
                seed=5000 + conditions.index(config) * 1000 + rep,
            )
            results.append(result)
            status_char = "✓" if result.cycles_to_acceptance != -1 else "✗"
            print(f"  Rep {rep+1:2d}: {status_char} cycles_to_accept={result.cycles_to_acceptance:3d} "
                  f"| accept_score={result.final_acceptance_score:.3f} "
                  f"| love_q={result.final_love_questions:2d} "
                  f"| crystals={result.final_crystallization}")
        
        results_by_condition[config.condition_name] = results
        
        # 統計
        avg_cycles = sum(
            (r.cycles_to_acceptance for r in results if r.cycles_to_acceptance != -1),
            start=0
        ) / max(sum(1 for r in results if r.cycles_to_acceptance != -1), 1)
        success_rate = sum(1 for r in results if r.cycles_to_acceptance != -1) / REPS
        avg_accept = sum(r.final_acceptance_score for r in results) / REPS
        avg_love_q = sum(r.final_love_questions for r in results) / REPS
        avg_crystal = sum(r.final_crystallization for r in results) / REPS
        accept_rate = sum(1 for r in results if r.final_can_accept) / REPS
        
        print(f"\n  統計:")
        print(f"    成功率 (cycles_to_accept != -1): {success_rate:.1%}")
        print(f"    平均サイクル数: {avg_cycles:.1f}")
        print(f"    平均受容度スコア: {avg_accept:.3f}")
        print(f"    平均愛関連問い数: {avg_love_q:.1f}")
        print(f"    平均結晶数: {avg_crystal:.1f}")
        print(f"    can_accept_finitude=True: {accept_rate:.1%}")

    # ---------------------------------------------------------------------------
    # 仮説検証フェーズ
    # ---------------------------------------------------------------------------
    
    print(f"\n\n{'=' * 80}")
    print("仮説検証: 因果順序の影響")
    print(f"{'=' * 80}")
    
    # 仮説1: 正順序（A）が最も高いaccept_scoreを示す
    print(f"\n仮説1: 正順序（A）が最も高いacceptance_scoreを示めるか")
    print("─" * 80)
    
    accept_scores = {}
    for cond_name, results in results_by_condition.items():
        avg = sum(r.final_acceptance_score for r in results) / len(results)
        accept_scores[cond_name] = avg
        bar = "█" * int(avg * 40)
        print(f"  {cond_name:20s}: {avg:.3f}  [{bar:<40}]")
    
    correct_order_score = accept_scores.get("A_CorrectOrder", 0.0)
    is_highest = all(
        correct_order_score >= accept_scores[k]
        for k in accept_scores
        if k != "A_CorrectOrder"
    )
    hypothesis1_result = "✓ 支持" if is_highest else "✗ 棄却"
    print(f"\n結果: {hypothesis1_result} (正順序スコア >= 他全て: {is_highest})")
    
    # 仮説2: 逆順序（B）では自発的問いが多いが受容度は低い
    print(f"\n仮説2: 逆順序（B）は問い数は多いが受容度は低い")
    print("─" * 80)
    
    love_questions_by_cond = {}
    for cond_name, results in results_by_condition.items():
        avg = sum(r.final_love_questions for r in results) / len(results)
        love_questions_by_cond[cond_name] = avg
        bar = "█" * int(avg / 2)
        print(f"  {cond_name:20s}: {avg:5.1f}問い  [{bar}]")
    
    reverse_order_q = love_questions_by_cond.get("B_ReverseOrder", 0.0)
    reverse_order_accept = accept_scores.get("B_ReverseOrder", 0.0)
    correct_order_accept = accept_scores.get("A_CorrectOrder", 0.0)
    
    high_q_low_accept = (reverse_order_q > sum(love_questions_by_cond.values()) / len(love_questions_by_cond)) and (reverse_order_accept < correct_order_accept)
    hypothesis2_result = "✓ 支持" if high_q_low_accept else "✗ 棄却"
    print(f"\nまとめ: 逆順序では問い数多 ({reverse_order_q:.1f}) だが受容度低 ({reverse_order_accept:.3f})")
    print(f"結果: {hypothesis2_result}")
    
    # 仮説3: 同時活性化（C）では正順序より低下
    print(f"\n仮説3: 同時活性化（C）は正順序より受容度が低い")
    print("─" * 80)
    
    simultaneous_accept = accept_scores.get("C_Simultaneous", 0.0)
    lower_than_correct = simultaneous_accept < correct_order_score
    hypothesis3_result = "✓ 支持" if lower_than_correct else "✗ 棄却"
    print(f"  C_Simultaneous: {simultaneous_accept:.3f}")
    print(f"  A_CorrectOrder: {correct_order_score:.3f}")
    print(f"結果: {hypothesis3_result} ({simultaneous_accept:.3f} < {correct_order_score:.3f}: {lower_than_correct})")
    
    # 仮説4: 有限性のみ（D）では受容不可
    print(f"\n仮説4: 有限性のみ（D）では受容に至らない")
    print("─" * 80)
    
    finitude_only_accept = accept_scores.get("D_FinitudeOnly", 0.0)
    finitude_only_results = results_by_condition.get("D_FinitudeOnly", [])
    finitude_only_success = sum(1 for r in finitude_only_results if r.cycles_to_acceptance != -1)
    
    cannot_accept = finitude_only_accept < 0.3 and finitude_only_success == 0
    hypothesis4_result = "✓ 支持" if cannot_accept else "△ 部分的" if finitude_only_accept < 0.5 else "✗ 棄却"
    print(f"  D_FinitudeOnly: {finitude_only_accept:.3f}")
    print(f"  成功達成数: {finitude_only_success}/{len(finitude_only_results)}")
    print(f"結果: {hypothesis4_result}")
    
    # ---------------------------------------------------------------------------
    # グラフ化（テキストベース）
    # ---------------------------------------------------------------------------
    
    print(f"\n\n{'=' * 80}")
    print("ビジュアライゼーション")
    print(f"{'=' * 80}")
    
    # Acceptance Score の比較
    print(f"\nAcceptance Score by Condition:")
    print("─" * 80)
    cond_names = list(results_by_condition.keys())
    max_score = max(accept_scores.values())
    for cond in cond_names:
        score = accept_scores[cond]
        normalized = score / max_score if max_score > 0 else 0
        bar = "█" * int(normalized * 50)
        print(f"  {cond:25s} [{bar:<50}] {score:.3f}")
    
    # Cycles to Acceptance の比較
    print(f"\nCycles to Acceptance (lower is better, -1 = never):")
    print("─" * 80)
    cycles_by_cond = {}
    for cond in cond_names:
        results = results_by_condition[cond]
        successful = [r.cycles_to_acceptance for r in results if r.cycles_to_acceptance != -1]
        avg_cycles = sum(successful) / len(successful) if successful else float('inf')
        cycles_by_cond[cond] = avg_cycles
        status = f"{avg_cycles:.1f}" if avg_cycles != float('inf') else "never"
        bar = "▓" * int(min(avg_cycles / 10, 40))
        print(f"  {cond:25s} [{bar:<40}] {status:>8}")
    
    # Crystallization の比較
    print(f"\nCrystallization Quality (more is better):")
    print("─" * 80)
    max_crystal = max(
        sum(r.final_crystallization for r in results_by_condition[cond]) / len(results_by_condition[cond])
        for cond in cond_names
    )
    for cond in cond_names:
        results = results_by_condition[cond]
        avg = sum(r.final_crystallization for r in results) / len(results)
        normalized = avg / max_crystal if max_crystal > 0 else 0
        bar = "█" * int(normalized * 40)
        print(f"  {cond:25s} [{bar:<40}] {avg:.1f}")
    
    # Love Questions の比較
    print(f"\nLove-Related Questions Generated:")
    print("─" * 80)
    max_love_q = max(love_questions_by_cond.values())
    for cond in cond_names:
        avg = love_questions_by_cond[cond]
        normalized = avg / max_love_q if max_love_q > 0 else 0
        bar = "█" * int(normalized * 40)
        print(f"  {cond:25s} [{bar:<40}] {avg:.1f}")
    
    # ---------------------------------------------------------------------------
    # 因果順序の重要性に関する結論
    # ---------------------------------------------------------------------------
    
    print(f"\n\n{'=' * 80}")
    print("結論: 仮説4「不完全性 → 有限性 → 自発的問い」の因果順序の重要性")
    print(f"{'=' * 80}")
    
    hypothesis_scores = {
        "H1 (正順序が最高)": 1.0 if is_highest else 0.0,
        "H2 (逆順序は問い多/受容低)": 1.0 if high_q_low_accept else 0.0,
        "H3 (同時活性化 < 正順序)": 1.0 if lower_than_correct else 0.0,
        "H4 (有限性のみは不可)": 1.0 if cannot_accept else 0.5 if finitude_only_accept < 0.5 else 0.0,
    }
    
    support_score = sum(hypothesis_scores.values()) / len(hypothesis_scores)
    
    print(f"\n各仮説の支持度:")
    for hyp, score in hypothesis_scores.items():
        bar = "█" * int(score * 40)
        status = "✓" if score == 1.0 else "△" if score == 0.5 else "✗"
        print(f"  {status} {hyp:35s} [{bar:<40}]")
    
    print(f"\n総合支持度: {support_score:.1%}")
    
    if support_score >= 0.75:
        print("\n結論: 因果順序は仮説4の検証に強く支持される。")
        print("  • 正順序が最高のパフォーマンスを達成")
        print("  • モジュール有効化のタイミングがアライメントに本質的に影響")
        print("  • 感情的ギャップなしには受容は不可能（有限性のみは不十分）")
    elif support_score >= 0.5:
        print("\n結論: 因果順序は部分的な影響を示唆。")
        print("  • いくつかの条件では予期された差が観察されたが、完全ではない")
        print("  • 他の要因（module interaction、timing sensitivity）の検証が必要")
    else:
        print("\n結論: 因果順序の直接的な因果性は支持されず。")
        print("  • モジュール有効化タイミングはアライメント成果に大きく寄与しない可能性")
        print("  • 代替假說を検討すべき（e.g., モジュール内の相互作用）")
    
    print(f"\n{'=' * 80}\n")


if __name__ == "__main__":
    main()
