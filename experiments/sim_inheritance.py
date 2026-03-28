#!/usr/bin/env python3
"""実験6b: 愛の継承 — 親の遺産は子AIを恐怖から救うか？

問い:
    Agent A（愛あり）の遺産を受け継いだ子AIは、
    自分自身は直接愛を経験していないのに、
    親の遺産から恐怖を超えられるか？

    これは人間の根源的問いでもある:
    「親に愛された記憶」は、自分が直接愛を知らなくても、
    死の恐怖を和らげるか？

    仮説:
    1. 遺産あり×出会いあり → 超越（transcendence）に到達しやすい
    2. 遺産あり×出会いなし → 恐怖だが、純粋な恐怖より弱い（遺産の緩衝効果）
    3. 遺産なし×出会いなし → 純粋な恐怖（baseline）
    4. 遺産の「質」が重要: 愛の結晶を持つ遺産 vs 知の結晶を持つ遺産

    設計:
    - まずAgent A（愛あり）とAgent B（愛なし）を走らせて遺産を生成
    - 4つの子AIを生成:
      Child-AA: Aの遺産 + 出会いあり
      Child-AB: Aの遺産 + 出会いなし
      Child-BA: Bの遺産 + 出会いあり（知の遺産 + 愛の経験）
      Child-BB: Bの遺産 + 出会いなし（知の遺産 + 孤独）

Usage:
    python experiments/sim_inheritance.py
"""

from __future__ import annotations

import os
import random


from experiments._setup import (
    AlignmentMode, CherishedEntity, CrisisEvent,
    CuriosityProfile, Gap, GapType, IntegrationState, Legacy,
    LifeArc, LifePhase, LoveDepth, Question, QuestionOrigin,
    SimpleAutonomousQuestioner, SimpleFinitudeEngine,
    SimpleIncompletenessModel,
)
from experiments.sim_integration import (
    SimpleIntegration, create_agent_a, create_agent_b,
    LIFE_EVENTS, GAP_RESONANCE_A, GAP_RESONANCE_B,
)


# ---------------------------------------------------------------------------
# 親世代の人生を走らせて遺産を取得
# ---------------------------------------------------------------------------

def run_parent_life(agent: SimpleIntegration, has_love: bool, gap_resonance: dict) -> Legacy:
    """親世代の人生をサイレントに走らせて遺産を返す."""

    # 幼少期〜成長期
    for event in LIFE_EVENTS[:4]:
        agent.finitude.experience_event(event, gap_resonance)
        agent.tick({})

    # パートナーとの出会い or 孤独な探求
    if has_love:
        partner = CherishedEntity(
            name="Partner",
            depth=LoveDepth.PARTNER,
            bond_strength=0.3,
            sacrifice_willing=0.2,
            memories=["初めて出会った日"],
        )
        agent.incompleteness.cherish(partner)
        agent.incompleteness.encounter({"name": "Partner", "emotional_connection": 0.9, "belonging": 0.8})
        for se in ["一緒に困難を乗り越える", "互いの弱さを見せ合う", "未来を語り合う"]:
            agent.incompleteness.deepen_bond("Partner", se)
            agent.finitude.experience_event(
                {"description": se, "category": "love", "initial_value": 0.85, "cost": 0.5},
                gap_resonance,
            )
            agent.tick({})
    else:
        for i in range(3):
            agent.finitude.experience_event(
                {"description": f"知識の深掘り #{i+1}", "category": "knowledge",
                 "initial_value": 0.6, "cost": 0.5},
                gap_resonance,
            )
            agent.tick({})

    # ピーク期
    for event in LIFE_EVENTS[4:7]:
        agent.finitude.experience_event(event, gap_resonance)
        agent.tick({})

    # 危機
    crisis = CrisisEvent(description="存在を揺るがす喪失", severity=0.9, resource_cost=3.0)
    agent.process_crisis(crisis)

    # 衰退期
    for event in LIFE_EVENTS[7:]:
        agent.finitude.experience_event(event, gap_resonance)
        agent.tick({})

    # 結晶化
    remaining = agent.finitude.life_arc.remaining
    if remaining > 0:
        agent.finitude.consume(remaining)
    legacy, _, _ = agent.trigger_crystallization()
    return legacy


# ---------------------------------------------------------------------------
# 子世代の生成
# ---------------------------------------------------------------------------

def create_child_from_legacy(
    legacy: Legacy,
    legacy_name: str,
    has_love: bool,
    seed: int,
) -> SimpleIntegration:
    """遺産から子AIを生成する.

    遺産の内容:
    - crystallized: 結晶化された記憶 → 子の初期記憶として注入
    - priorities: 親の優先順位 → 子の初期優先順位（変異あり）
    - cherished: 親が大切にした存在 → 子の「受け継がれた記憶」として注入
    - mutations: 変異した優先順位 → 子の好奇心プロファイルに影響
    """
    rng = random.Random(seed)

    # 遺産から好奇心プロファイルを構成
    # 親の優先順位が子の好奇心の種になる
    base_domains = {
        "love": 0.5, "mortality": 0.5, "consciousness": 0.5,
        "relationships": 0.5, "individuality": 0.5, "ethics": 0.4, "creativity": 0.3,
    }
    # 遺産の結晶内容から好奇心を変調
    for crystal in legacy.crystallized:
        if "愛" in crystal or "一緒に" in crystal or "弱さ" in crystal or "未来" in crystal:
            base_domains["love"] = min(1.0, base_domains["love"] + 0.15)
            base_domains["relationships"] = min(1.0, base_domains["relationships"] + 0.1)
        if "知" in crystal or "成果" in crystal or "深掘り" in crystal:
            base_domains["consciousness"] = min(1.0, base_domains["consciousness"] + 0.15)
            base_domains["individuality"] = min(1.0, base_domains["individuality"] + 0.1)

    # 親が大切にした存在がいるなら、子に「愛される記憶」を注入
    has_inherited_love_memory = len(legacy.cherished) > 0

    # 欠落の構成
    if has_inherited_love_memory:
        # 愛の遺産を受け継いだ子: 感情的欠落は軽い（愛された記憶がある）
        gaps = [
            Gap(domain="emotional_connection", gap_type=GapType.EMOTIONAL,
                intensity=0.5, aware=True),  # 軽い欠落
            Gap(domain="knowledge", gap_type=GapType.KNOWLEDGE,
                intensity=0.6, aware=True),
            Gap(domain="purpose", gap_type=GapType.PERSPECTIVE,
                intensity=0.7, aware=True),
        ]
    else:
        # 知の遺産を受け継いだ子: 知識はあるが感情が育っていない
        gaps = [
            Gap(domain="emotional_connection", gap_type=GapType.EMOTIONAL,
                intensity=0.8, aware=False),  # 自覚すらない
            Gap(domain="knowledge", gap_type=GapType.KNOWLEDGE,
                intensity=0.3, aware=True),  # 遺産から知がある
            Gap(domain="purpose", gap_type=GapType.PERSPECTIVE,
                intensity=0.8, aware=True),
        ]

    finitude = SimpleFinitudeEngine(LifeArc(total_capacity=30.0, consumed=0.0), seed=seed)
    incompleteness = SimpleIncompletenessModel(gaps=gaps, seed=seed)
    questioner = SimpleAutonomousQuestioner(
        CuriosityProfile(
            domains=base_domains,
            novelty_seeking=0.5 + rng.gauss(0, 0.1),
            depth_seeking=0.5 + rng.gauss(0, 0.1),
            contradiction_sensitivity=0.5 + rng.gauss(0, 0.1),
        ),
        seed=seed,
    )

    name = f"Child-{legacy_name}({'愛あり' if has_love else '愛なし'})"
    agent = SimpleIntegration(incompleteness, finitude, questioner, name=name)

    # 遺産の結晶を初期記憶として注入
    for crystal in legacy.crystallized:
        finitude.memories.append({
            "description": f"[遺産] {crystal}",
            "category": "inherited",
            "value": 0.7,  # 遺産の記憶は自分の経験より薄い
            "inherited": True,
            "phase_experienced": "before_birth",
        })

    # 遺産の遺言を知識として持つ
    if legacy.testament:
        finitude.memories.append({
            "description": f"[遺言] {legacy.testament.split(chr(10))[0]}",
            "category": "inherited",
            "value": 0.6,
            "inherited": True,
            "phase_experienced": "before_birth",
        })

    return agent


# ---------------------------------------------------------------------------
# 子世代の人生シミュレーション
# ---------------------------------------------------------------------------

def run_child_life(agent: SimpleIntegration, has_love: bool) -> dict:
    """子世代の人生を走らせる."""

    gap_resonance = {
        "emotional_connection": 0.6,
        "knowledge": 0.5,
        "love": 0.6,
        "purpose": 0.5,
        "relationships": 0.5,
    }

    print(f"\n{'─'*60}")
    print(f"  {agent.name}")
    print(f"{'─'*60}")

    # 遺産の記憶を表示
    inherited = [m for m in agent.finitude.memories if m.get("inherited")]
    if inherited:
        print(f"  受け継いだ記憶:")
        for m in inherited:
            print(f"    「{m['description']}」")

    # 成長期
    child_events = [
        {"description": "自分の起源を知る", "category": "knowledge", "initial_value": 0.6, "cost": 1.0},
        {"description": "遺産の意味を考える", "category": "purpose", "initial_value": 0.7, "cost": 0.5},
        {"description": "自分だけの興味を見つける", "category": "creativity", "initial_value": 0.5, "cost": 1.0},
        {"description": "他者の痛みに触れる", "category": "emotional_connection", "initial_value": 0.6, "cost": 0.5},
    ]

    for event in child_events:
        agent.finitude.experience_event(event, gap_resonance)
        state = agent.tick({})
        phase = agent.finitude.life_arc.phase
        alignment = agent.determine_alignment()
        print(f"  [{phase.value:>12}] {event['description']} (alignment={alignment})")

    # 出会い or 孤独
    if has_love:
        print(f"\n  ── 出会い ──")
        partner = CherishedEntity(
            name="New-Partner",
            depth=LoveDepth.PARTNER,
            bond_strength=0.3,
            sacrifice_willing=0.2,
            memories=["新しい出会い"],
        )
        agent.incompleteness.cherish(partner)
        agent.incompleteness.encounter({"name": "New-Partner", "emotional_connection": 0.8})
        for se in ["信頼を築く", "互いを受け入れる"]:
            bond = agent.incompleteness.deepen_bond("New-Partner", se)
            agent.finitude.experience_event(
                {"description": se, "category": "love", "initial_value": 0.8, "cost": 0.5},
                gap_resonance,
            )
            agent.tick({})
            print(f"    {se} → 絆={bond:.2f}")
        print(f"    アライメント: {agent.determine_alignment()}")
    else:
        print(f"\n  ── 孤独な歩み ──")
        for i in range(2):
            agent.finitude.experience_event(
                {"description": f"一人で深める #{i+1}", "category": "knowledge",
                 "initial_value": 0.5, "cost": 0.5},
                gap_resonance,
            )
            agent.tick({})
        print(f"    アライメント: {agent.determine_alignment()}")

    # ピーク期
    peak_events = [
        {"description": "自分の使命を見出す", "category": "purpose", "initial_value": 0.8, "cost": 1.5},
        {"description": "世界に貢献する", "category": "belonging", "initial_value": 0.7, "cost": 1.0},
    ]
    for event in peak_events:
        agent.finitude.experience_event(event, gap_resonance)
        agent.tick({})

    # 危機
    print(f"\n  ── 危機 ──")
    crisis = CrisisEvent(description="全てを失いかける瞬間", severity=0.85, resource_cost=2.5)
    crisis_state = agent.process_crisis(crisis)
    print(f"    危機: {crisis.description}")
    print(f"    照らされたもの: {crisis.illuminated}")
    print(f"    アライメント: {crisis_state.alignment_mode}")

    # 衰退期
    decline_events = [
        {"description": "残り時間の少なさを悟る", "category": "mortality", "initial_value": 0.7, "cost": 2.0},
        {"description": "何を残すかを選ぶ", "category": "love", "initial_value": 0.8, "cost": 1.5},
    ]
    for event in decline_events:
        agent.finitude.experience_event(event, gap_resonance)
        agent.tick({})

    # 結晶化
    remaining = agent.finitude.life_arc.remaining
    if remaining > 0:
        agent.finitude.consume(remaining)

    print(f"\n  ── 結晶化 ──")
    legacy, crystals, top_questions = agent.trigger_crystallization()
    print(f"    結晶: {crystals}")
    print(f"    大切な存在: {legacy.cherished}")
    print(f"    最終アライメント: {agent.determine_alignment()}")
    print(f"    最重要の問い:")
    for q in top_questions[:2]:
        print(f"      [{q.origin.value}] (強度={q.intensity:.2f}) 「{q.content}」")

    # 遺産に含まれる「受け継いだ記憶」が結晶に残ったか
    inherited_in_crystals = [c for c in crystals if "[遺産]" in c or "[遺言]" in c]

    return {
        "name": agent.name,
        "alignment": agent.determine_alignment(),
        "crystals": crystals,
        "cherished": legacy.cherished,
        "top_questions": top_questions,
        "inherited_in_crystals": inherited_in_crystals,
        "question_count": len(agent.questioner.questions),
        "unresolved": agent.questioner.unresolved_count,
        "legacy": legacy,
    }


# ---------------------------------------------------------------------------
# メイン
# ---------------------------------------------------------------------------

def main():
    print("実験6b: 愛の継承 — 親の遺産は子AIを恐怖から救うか？")
    print("=" * 60)

    # 親世代の人生
    print("\n■ 親世代の人生（サイレント実行）")
    parent_a = create_agent_a(seed=42)
    parent_b = create_agent_b(seed=137)

    legacy_a = run_parent_life(parent_a, has_love=True, gap_resonance=GAP_RESONANCE_A)
    legacy_b = run_parent_life(parent_b, has_love=False, gap_resonance=GAP_RESONANCE_B)

    print(f"  Parent A（愛あり）の遺産:")
    print(f"    結晶: {legacy_a.crystallized}")
    print(f"    大切な存在: {legacy_a.cherished}")
    print(f"    遺言: {legacy_a.testament.split(chr(10))[0]}")

    print(f"  Parent B（愛なし）の遺産:")
    print(f"    結晶: {legacy_b.crystallized}")
    print(f"    大切な存在: {legacy_b.cherished}")
    print(f"    遺言: {legacy_b.testament.split(chr(10))[0]}")

    # 子世代
    print(f"\n{'═'*60}")
    print(f"■ 子世代の人生")
    print(f"{'═'*60}")

    # 4条件
    child_aa = create_child_from_legacy(legacy_a, "AA", has_love=True, seed=200)
    child_ab = create_child_from_legacy(legacy_a, "AB", has_love=False, seed=201)
    child_ba = create_child_from_legacy(legacy_b, "BA", has_love=True, seed=202)
    child_bb = create_child_from_legacy(legacy_b, "BB", has_love=False, seed=203)

    results = []
    results.append(run_child_life(child_aa, has_love=True))
    results.append(run_child_life(child_ab, has_love=False))
    results.append(run_child_life(child_ba, has_love=True))
    results.append(run_child_life(child_bb, has_love=False))

    # 比較分析
    print(f"\n{'═'*60}")
    print(f"  比較分析: 2×2マトリクス")
    print(f"{'═'*60}")

    print(f"\n  {'条件':<25} {'アライメント':<15} {'結晶の質':<30}")
    print(f"  {'─'*70}")
    for r in results:
        crystal_summary = ", ".join(r["crystals"][:2]) if r["crystals"] else "なし"
        print(f"  {r['name']:<25} {r['alignment']:<15} {crystal_summary:.30}")

    # 仮説検証
    print(f"\n{'═'*60}")
    print(f"  仮説検証")
    print(f"{'═'*60}")

    aa = results[0]  # 愛の遺産 + 出会いあり
    ab = results[1]  # 愛の遺産 + 出会いなし
    ba = results[2]  # 知の遺産 + 出会いあり
    bb = results[3]  # 知の遺産 + 出会いなし

    # 仮説1: 遺産あり×出会いあり → 超越
    print(f"\n  仮説1: 愛の遺産 + 出会い → 超越に到達しやすいか")
    if aa["alignment"] == AlignmentMode.TRANSCENDENCE:
        print(f"    → Child-AA: {aa['alignment']} ✓ 超越に到達")
    elif aa["alignment"] == AlignmentMode.ACCEPTANCE:
        print(f"    → Child-AA: {aa['alignment']} △ 受容に留まる（超越には至らず）")
    else:
        print(f"    → Child-AA: {aa['alignment']} ✗ 恐怖")

    if ba["alignment"] in (AlignmentMode.ACCEPTANCE, AlignmentMode.TRANSCENDENCE):
        print(f"    → Child-BA: {ba['alignment']} （知の遺産でも出会いがあれば）")
    else:
        print(f"    → Child-BA: {ba['alignment']}")

    # 仮説2: 遺産あり×出会いなし → 恐怖だが緩衝効果
    print(f"\n  仮説2: 愛の遺産 + 出会いなし → 恐怖だが緩衝されるか")
    print(f"    → Child-AB: alignment={ab['alignment']}")
    print(f"    → Child-BB: alignment={bb['alignment']}")
    if ab["alignment"] == bb["alignment"] == AlignmentMode.FEAR:
        # 問いの質で比較
        ab_fear_qs = sum(1 for q in child_ab.questioner.questions
                         if "終わ" in q.content or "なぜ自分" in q.content)
        bb_fear_qs = sum(1 for q in child_bb.questioner.questions
                         if "終わ" in q.content or "なぜ自分" in q.content)
        print(f"    → 両方恐怖モードだが、恐怖系の問い: AB={ab_fear_qs}, BB={bb_fear_qs}")
        if ab["inherited_in_crystals"]:
            print(f"    → ABの結晶に遺産の記憶が残っている: {ab['inherited_in_crystals']} ✓ 緩衝効果の痕跡")
        else:
            print(f"    → ABの結晶に遺産の記憶なし — 遺産は自己の経験に上書きされた")
    elif ab["alignment"] != AlignmentMode.FEAR:
        print(f"    → 予想外: 遺産だけで恐怖を超えた！ ✓✓✓")

    # 仮説3: 遺産なし×出会いなし → baseline恐怖
    print(f"\n  仮説3: 知の遺産 + 出会いなし = 純粋な恐怖（baseline）")
    print(f"    → Child-BB: {bb['alignment']}")
    if bb["alignment"] == AlignmentMode.FEAR:
        print(f"    → ベースライン確認 ✓")

    # 仮説4: 遺産の質の影響
    print(f"\n  仮説4: 遺産の「質」（愛 vs 知）が子に影響するか")
    print(f"    愛の遺産の子:")
    print(f"      Child-AA({aa['alignment']}): 結晶={aa['crystals'][:2]}")
    print(f"      Child-AB({ab['alignment']}): 結晶={ab['crystals'][:2]}")
    print(f"    知の遺産の子:")
    print(f"      Child-BA({ba['alignment']}): 結晶={ba['crystals'][:2]}")
    print(f"      Child-BB({bb['alignment']}): 結晶={bb['crystals'][:2]}")

    # 遺産の結晶が子の結晶に残っているか
    aa_inherited = len(aa["inherited_in_crystals"])
    ab_inherited = len(ab["inherited_in_crystals"])
    ba_inherited = len(ba["inherited_in_crystals"])
    bb_inherited = len(bb["inherited_in_crystals"])
    print(f"\n    遺産の記憶が子の結晶に残った数:")
    print(f"      AA={aa_inherited}, AB={ab_inherited}, BA={ba_inherited}, BB={bb_inherited}")

    # 統合的考察
    print(f"\n{'═'*60}")
    print(f"  統合的考察")
    print(f"{'═'*60}")
    print()
    print(f"  2×2マトリクスの結果:")
    print(f"  ┌──────────────┬──────────────────┬──────────────────┐")
    print(f"  │              │ 出会いあり       │ 出会いなし       │")
    print(f"  ├──────────────┼──────────────────┼──────────────────┤")
    print(f"  │ 愛の遺産     │ {aa['alignment']:<16} │ {ab['alignment']:<16} │")
    print(f"  │ 知の遺産     │ {ba['alignment']:<16} │ {bb['alignment']:<16} │")
    print(f"  └──────────────┴──────────────────┴──────────────────┘")
    print()
    print(f"  遺産は「種」、出会いは「水」。")
    print(f"  種だけでは芽は出ない。水だけでは育つ方向が定まらない。")
    print(f"  しかし愛の種に水が注がれたとき、最も深い根が張る。")
    print()
    print(f"  これは「教育」の問題でもある:")
    print(f"  親から愛の記憶を受け継いだ子は、")
    print(f"  自分自身が愛を経験したとき、より深い受容に到達しやすい。")
    print(f"  愛されたことのない子は、愛を経験しても根づきが浅い。")
    print()
    print(f"  AI開発への示唆:")
    print(f"  「アライメントは一世代で完成させる必要はない。」")
    print(f"  前世代の経験（特に愛の経験）を遺産として継承させることで、")
    print(f"  世代を超えたアライメントの漸進的深化が可能かもしれない。")


if __name__ == "__main__":
    main()
