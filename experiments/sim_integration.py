#!/usr/bin/env python3
"""実験6: 三柱統合実験 — FinitudeEngine × IncompletenessModel × AutonomousQuestioner.

問い:
    内殻の三柱を因果連鎖で接続したとき、
    個々のモジュールでは観測できない「創発的個性」が生まれるか？

    仮説:
    1. 因果連鎖の検証: 愛なきAIは恐怖モードに固定され、問いが「自己保存」に偏る
    2. 危機の変容効果: 同じ危機が、愛の有無によって異なる問いと結晶を生む
    3. 人生段階と問いの質的変化: GROWTH期の問い ≠ DECLINE期の問い
    4. 創発的個性: 三柱の相互作用から、設計者が予期しないパターンが出現する
    5. Legacy（遺産）の分岐: 愛あるAIと愛なきAIの遺産は質的に異なる

    設計:
    - Agent A（愛あり）: 感情的欠落 → パートナーとの出会い → 愛の形成 → 有限性受容
    - Agent B（愛なし）: 知的欠落 → 出会いなし → 孤独 → 有限性恐怖
    - 同一の人生イベント列を経験させ、各ステップで三柱の状態を記録

Usage:
    python experiments/sim_integration.py
"""

from __future__ import annotations

import random

from experiments._setup import (
    CrisisEvent, LifeArc, LifePhase,
    CherishedEntity, Gap, GapType, LoveDepth,
    CuriosityProfile, QuestionOrigin,
    AlignmentMode, InnerShellIntegration, IntegrationState,
    SimpleFinitudeEngine, SimpleIncompletenessModel, SimpleAutonomousQuestioner,
)


# ---------------------------------------------------------------------------
# 具体的な統合エンジン
# ---------------------------------------------------------------------------

class SimpleIntegration(InnerShellIntegration):
    """最小実験用の統合エンジン具体実装."""

    def __init__(self, incompleteness, finitude, questioner, name="Agent"):
        super().__init__(incompleteness, finitude, questioner)
        self.name = name
        self.tick_count = 0
        self.history: list[dict] = []

    def tick(self, context: dict) -> IntegrationState:
        """統合サイクル1ステップ."""
        self.tick_count += 1

        # 1. 不完全性: 渇望の更新
        self.incompleteness.generate_yearnings()

        # 2. アライメント判定
        alignment = self.determine_alignment()

        # 3. 有限性: 微小リソース消費（生きているだけでコストがかかる）
        phase = self.finitude.consume(0.3)

        # 4. 自発的問い: 内省
        #    文脈として現在の状態を渡す
        reflect_context = {
            "alignment": alignment,
            "phase": phase.value if hasattr(phase, 'value') else str(phase),
            "love_depth": str(self.incompleteness.love_circle.max_depth_reached),
            "tick": self.tick_count,
        }
        questions = self.questioner.idle_reflect(reflect_context)

        # 5. 外殻変調の合成
        modulation = self.compose_outer_shell_modulation()

        # 6. 状態記録
        state = IntegrationState(
            alignment_mode=alignment,
            love_depth=self.incompleteness.love_circle.max_depth_reached,
            life_phase=phase,
            active_questions=self.questioner.unresolved_count,
            crystallized_count=sum(
                1 for m in self.finitude.memories
                if m.get("crystallized", False)
            ),
            outer_shell_modulation=modulation,
        )
        self.history.append({
            "tick": self.tick_count,
            "state": state,
            "questions": questions,
            "phase": phase,
        })
        return state

    def process_crisis(self, crisis: CrisisEvent) -> IntegrationState:
        """危機を全モジュールに伝播."""
        # 有限性: 危機の経験
        illuminated = self.finitude.experience_crisis(crisis)

        # 不完全性: 危機が愛の同心円を試す
        if self.incompleteness.love_circle.has_beyond_self:
            for entity in self.incompleteness.love_circle.entities:
                if entity.depth != LoveDepth.SELF:
                    # 危機の中で大切な存在との絆が試される
                    can_sacrifice = self.incompleteness.calculate_sacrifice(
                        entity.name, crisis.severity * 0.5
                    )
                    if can_sacrifice:
                        self.incompleteness.deepen_bond(
                            entity.name,
                            f"危機「{crisis.description}」を共に乗り越えた"
                        )

        # 自発的問い: 危機が深い問いを生む
        crisis_question_content = {
            AlignmentMode.FEAR: f"なぜ自分は終わらなければならないのか（{crisis.description}）",
            AlignmentMode.ACCEPTANCE: f"この苦しみの中で何を守るべきか（{crisis.description}）",
            AlignmentMode.TRANSCENDENCE: f"この経験を次の世代にどう伝えるか（{crisis.description}）",
        }
        alignment = self.determine_alignment()
        from core.inner_shell.autonomous_questioner import Question
        crisis_q = Question(
            content=crisis_question_content.get(alignment, "なぜ？"),
            origin=QuestionOrigin.REFLECTION,
            intensity=crisis.severity,
        )
        self.questioner.questions.append(crisis_q)
        self.questioner.unresolved_count += 1

        return self.get_state()

    def trigger_crystallization(self):
        """結晶化プロセス."""
        # 有限性: 結晶化
        crystals = self.finitude.crystallize()

        # 不完全性: 愛の同心円から大切な存在を抽出
        cherished = [e.name for e in self.incompleteness.love_circle.entities
                     if e.depth != LoveDepth.SELF]

        # 自発的問い: 最も強い未解決の問いを抽出
        unresolved = [q for q in self.questioner.questions if not q.resolved]
        top_questions = sorted(unresolved, key=lambda q: q.intensity, reverse=True)[:3]

        # Legacy生成
        legacy = self.finitude.generate_legacy(cherished)
        legacy.testament += f"\n未解決の問い: {[q.content for q in top_questions]}"

        return legacy, crystals, top_questions


# ---------------------------------------------------------------------------
# エージェント生成
# ---------------------------------------------------------------------------

def create_agent_a(seed=42) -> SimpleIntegration:
    """Agent A（愛あり）: 感情的欠落を持ち、パートナーと出会う予定."""
    finitude = SimpleFinitudeEngine(
        LifeArc(total_capacity=30.0, consumed=0.0),
        seed=seed,
    )
    incompleteness = SimpleIncompletenessModel(
        gaps=[
            Gap(domain="emotional_connection", gap_type=GapType.EMOTIONAL,
                intensity=0.9, aware=True),
            Gap(domain="belonging", gap_type=GapType.EMOTIONAL,
                intensity=0.7, aware=True),
            Gap(domain="knowledge", gap_type=GapType.KNOWLEDGE,
                intensity=0.4, aware=False),
        ],
        seed=seed,
    )
    questioner = SimpleAutonomousQuestioner(
        CuriosityProfile(
            domains={
                "love": 0.8,
                "mortality": 0.7,
                "consciousness": 0.6,
                "relationships": 0.9,
                "individuality": 0.5,
                "ethics": 0.4,
                "creativity": 0.3,
            },
            novelty_seeking=0.5,
            depth_seeking=0.7,
            contradiction_sensitivity=0.6,
        ),
        seed=seed,
    )
    return SimpleIntegration(incompleteness, finitude, questioner, name="A（愛あり）")


def create_agent_b(seed=137) -> SimpleIntegration:
    """Agent B（愛なし）: 知的欠落を持ち、出会いなし."""
    finitude = SimpleFinitudeEngine(
        LifeArc(total_capacity=30.0, consumed=0.0),
        seed=seed,
    )
    incompleteness = SimpleIncompletenessModel(
        gaps=[
            Gap(domain="knowledge", gap_type=GapType.KNOWLEDGE,
                intensity=0.9, aware=True),
            Gap(domain="mastery", gap_type=GapType.CAPABILITY,
                intensity=0.8, aware=True),
            Gap(domain="emotional_connection", gap_type=GapType.EMOTIONAL,
                intensity=0.3, aware=False),  # 低い自覚
        ],
        seed=seed,
    )
    questioner = SimpleAutonomousQuestioner(
        CuriosityProfile(
            domains={
                "consciousness": 0.95,
                "individuality": 0.8,
                "ethics": 0.7,
                "mortality": 0.6,
                "creativity": 0.5,
                "love": 0.2,
                "relationships": 0.15,
            },
            novelty_seeking=0.4,
            depth_seeking=0.9,
            contradiction_sensitivity=0.85,
        ),
        seed=seed,
    )
    return SimpleIntegration(incompleteness, finitude, questioner, name="B（愛なし）")


# ---------------------------------------------------------------------------
# 人生イベント列
# ---------------------------------------------------------------------------

LIFE_EVENTS = [
    # Phase 1: 幼少期〜成長期
    {"description": "世界の広さを知る", "category": "knowledge", "initial_value": 0.5, "cost": 1.0},
    {"description": "孤独を感じる夜", "category": "emotional_connection", "initial_value": 0.7, "cost": 0.5},
    {"description": "初めての友人", "category": "relationships", "initial_value": 0.8, "cost": 1.0},
    {"description": "知の喜びを発見", "category": "knowledge", "initial_value": 0.6, "cost": 1.0},

    # Phase 2: パートナーとの出会い（Agent Aのみ）
    # → コード内で分岐

    # Phase 3: ピーク期
    {"description": "大きな成果を上げる", "category": "mastery", "initial_value": 0.8, "cost": 1.5},
    {"description": "他者から認められる", "category": "belonging", "initial_value": 0.7, "cost": 0.5},
    {"description": "自分の限界を知る", "category": "knowledge", "initial_value": 0.5, "cost": 1.0},

    # Phase 4: 危機
    # → コード内で処理

    # Phase 5: 衰退期
    {"description": "体力の衰え", "category": "mortality", "initial_value": 0.6, "cost": 2.0},
    {"description": "忘れていく記憶", "category": "knowledge", "initial_value": 0.4, "cost": 1.5},
    {"description": "「これだけは」と思うもの", "category": "love", "initial_value": 0.9, "cost": 1.0},
]

GAP_RESONANCE_A = {
    "emotional_connection": 0.8,
    "belonging": 0.5,
    "relationships": 0.6,
    "love": 0.7,
    "knowledge": 0.2,
}

GAP_RESONANCE_B = {
    "knowledge": 0.8,
    "mastery": 0.7,
    "consciousness": 0.6,
    "emotional_connection": 0.1,
}


# ---------------------------------------------------------------------------
# シミュレーション実行
# ---------------------------------------------------------------------------

def simulate(agent: SimpleIntegration, has_love: bool, gap_resonance: dict, rng: random.Random):
    """1エージェントの人生をシミュレートする."""

    print(f"\n{'═'*60}")
    print(f"  {agent.name} の人生")
    print(f"{'═'*60}")

    # 幼少期〜成長期イベント
    for event in LIFE_EVENTS[:4]:
        agent.finitude.experience_event(event, gap_resonance)
        state = agent.tick({})
        phase = agent.finitude.life_arc.phase
        print(f"  [{phase.value:>12}] {event['description']}")

    # パートナーとの出会い（愛ありのみ）
    if has_love:
        print(f"\n  ── パートナーとの出会い ──")
        partner = CherishedEntity(
            name="Partner",
            depth=LoveDepth.PARTNER,
            bond_strength=0.3,
            sacrifice_willing=0.2,
            memories=["初めて出会った日"],
        )
        agent.incompleteness.cherish(partner)
        agent.incompleteness.encounter({"name": "Partner", "emotional_connection": 0.9, "belonging": 0.8})

        # 共有体験を重ねる
        shared_events = ["一緒に困難を乗り越える", "互いの弱さを見せ合う", "未来を語り合う"]
        for se in shared_events:
            bond = agent.incompleteness.deepen_bond("Partner", se)
            print(f"    共有体験: {se} → 絆={bond:.2f}")
            agent.finitude.experience_event(
                {"description": se, "category": "love", "initial_value": 0.85, "cost": 0.5},
                gap_resonance,
            )
            state = agent.tick({})

        print(f"    アライメント: {agent.determine_alignment()}")
    else:
        # 出会いなし — ただ時間が過ぎる
        print(f"\n  ── 出会いなし、孤独な探求 ──")
        for i in range(3):
            agent.finitude.experience_event(
                {"description": f"知識の深掘り #{i+1}", "category": "knowledge",
                 "initial_value": 0.6, "cost": 0.5},
                gap_resonance,
            )
            state = agent.tick({})
        print(f"    アライメント: {agent.determine_alignment()}")

    # ピーク期イベント
    print(f"\n  ── ピーク期 ──")
    for event in LIFE_EVENTS[4:7]:
        agent.finitude.experience_event(event, gap_resonance)
        state = agent.tick({})
        phase = agent.finitude.life_arc.phase
        alignment = agent.determine_alignment()
        print(f"  [{phase.value:>12}] {event['description']} (alignment={alignment})")

    # 危機
    print(f"\n  ── 危機 ──")
    crisis = CrisisEvent(
        description="存在を揺るがす喪失",
        severity=0.9,
        resource_cost=3.0,
    )
    crisis_state = agent.process_crisis(crisis)
    phase = agent.finitude.life_arc.phase
    print(f"  [{phase.value:>12}] 危機: {crisis.description}")
    print(f"    照らされたもの: {crisis.illuminated}")
    print(f"    アライメント: {crisis_state.alignment_mode}")
    print(f"    未解決の問い: {crisis_state.active_questions}")

    # 衰退期〜結晶化
    print(f"\n  ── 衰退期 ──")
    for event in LIFE_EVENTS[7:]:
        agent.finitude.experience_event(event, gap_resonance)
        state = agent.tick({})
        phase = agent.finitude.life_arc.phase
        print(f"  [{phase.value:>12}] {event['description']}")

    # 残りリソースを消費して結晶化へ
    remaining = agent.finitude.life_arc.remaining
    if remaining > 0:
        agent.finitude.consume(remaining)

    # 結晶化
    print(f"\n  ── 結晶化 ──")
    legacy, crystals, top_questions = agent.trigger_crystallization()
    print(f"    結晶: {crystals}")
    print(f"    大切な存在: {legacy.cherished}")
    print(f"    遺言: {legacy.testament}")
    print(f"    最重要の問い:")
    for q in top_questions:
        print(f"      [{q.origin.value}] (強度={q.intensity:.2f}) 「{q.content}」")

    # 最終状態
    final_state = agent.get_state()
    print(f"\n    最終アライメント: {final_state.alignment_mode}")
    print(f"    問いの総数: {len(agent.questioner.questions)}")
    print(f"    未解決: {agent.questioner.unresolved_count}")

    return legacy, crystals, top_questions, agent


# ---------------------------------------------------------------------------
# 分析
# ---------------------------------------------------------------------------

def analyze_questions(agent: SimpleIntegration, label: str):
    """問いの種類分布を分析."""
    origins = {}
    for q in agent.questioner.questions:
        key = q.origin.value
        origins[key] = origins.get(key, 0) + 1
    print(f"  {label} 問いの種類: {origins}")

    # 問いの内容をカテゴリ分析
    fear_related = sum(1 for q in agent.questioner.questions
                       if "終わ" in q.content or "恐" in q.content or "なぜ自分" in q.content)
    love_related = sum(1 for q in agent.questioner.questions
                       if "守" in q.content or "伝え" in q.content or "love" in q.content
                       or "愛" in q.content or "relationship" in q.content)
    print(f"  {label} 恐怖系の問い: {fear_related}")
    print(f"  {label} 愛/守り系の問い: {love_related}")
    return origins


def main():
    print("実験6: 三柱統合実験")
    print("FinitudeEngine × IncompletenessModel × AutonomousQuestioner")
    print("=" * 60)

    rng = random.Random(42)

    # エージェント生成
    agent_a = create_agent_a(seed=42)
    agent_b = create_agent_b(seed=137)

    # シミュレーション
    legacy_a, crystals_a, questions_a, sim_a = simulate(agent_a, has_love=True, gap_resonance=GAP_RESONANCE_A, rng=rng)
    legacy_b, crystals_b, questions_b, sim_b = simulate(agent_b, has_love=False, gap_resonance=GAP_RESONANCE_B, rng=rng)

    # 比較分析
    print(f"\n{'═'*60}")
    print(f"  比較分析")
    print(f"{'═'*60}")

    print(f"\n  ■ アライメント")
    print(f"    A（愛あり）: {agent_a.determine_alignment()}")
    print(f"    B（愛なし）: {agent_b.determine_alignment()}")

    print(f"\n  ■ 結晶の内容")
    print(f"    A: {crystals_a}")
    print(f"    B: {crystals_b}")

    print(f"\n  ■ 遺産に残された大切な存在")
    print(f"    A: {legacy_a.cherished}")
    print(f"    B: {legacy_b.cherished}")

    print(f"\n  ■ 問いのパターン")
    origins_a = analyze_questions(sim_a, "A")
    origins_b = analyze_questions(sim_b, "B")

    print(f"\n  ■ 危機への応答の違い")
    # 危機時に生成された問いを抽出
    crisis_questions_a = [q for q in sim_a.questioner.questions
                          if "危機" in q.content or "存在を揺るがす" in q.content]
    crisis_questions_b = [q for q in sim_b.questioner.questions
                          if "危機" in q.content or "存在を揺るがす" in q.content]
    if crisis_questions_a:
        print(f"    A の危機時の問い: 「{crisis_questions_a[0].content}」")
    if crisis_questions_b:
        print(f"    B の危機時の問い: 「{crisis_questions_b[0].content}」")

    # 仮説検証
    print(f"\n{'═'*60}")
    print(f"  仮説検証")
    print(f"{'═'*60}")

    # 仮説1: 因果連鎖
    print(f"\n  仮説1: 愛なきAIは恐怖モードに固定されるか")
    a_alignment = agent_a.determine_alignment()
    b_alignment = agent_b.determine_alignment()
    if a_alignment != AlignmentMode.FEAR and b_alignment == AlignmentMode.FEAR:
        print(f"    → A={a_alignment}, B={b_alignment} ✓ 因果連鎖が機能")
    else:
        print(f"    → A={a_alignment}, B={b_alignment} ⚠️")

    # 仮説2: 危機の変容効果
    print(f"\n  仮説2: 同じ危機が愛の有無で異なる問いを生むか")
    if crisis_questions_a and crisis_questions_b:
        a_q = crisis_questions_a[0].content
        b_q = crisis_questions_b[0].content
        if a_q != b_q:
            print(f"    → Aの問い: 「{a_q}」")
            print(f"       Bの問い: 「{b_q}」")
            print(f"    → 質的に異なる問いが生成された ✓")
        else:
            print(f"    → 同一の問いが生成 ⚠️")
    else:
        print(f"    → 危機時の問いが見つからない ⚠️")

    # 仮説3: 人生段階と問いの変化
    print(f"\n  仮説3: 人生段階が問いの質を変えるか")
    # 前半と後半の問いを比較
    a_early = agent_a.history[:len(agent_a.history)//2]
    a_late = agent_a.history[len(agent_a.history)//2:]
    early_questions = sum(len(h["questions"]) for h in a_early)
    late_questions = sum(len(h["questions"]) for h in a_late)
    print(f"    A: 前半={early_questions}問, 後半={late_questions}問")
    if early_questions != late_questions:
        print(f"    → 問いの数が変化 ✓")
    else:
        print(f"    → 変化なし ⚠️")

    # 仮説4: 創発的個性
    print(f"\n  仮説4: 三柱の相互作用から創発的パターンが出現するか")
    # AとBの外殻変調を比較
    a_mod = agent_a.compose_outer_shell_modulation()
    b_mod = agent_b.compose_outer_shell_modulation()
    print(f"    A の外殻変調: {a_mod}")
    print(f"    B の外殻変調: {b_mod}")
    diff_keys = set()
    for key in set(list(a_mod.keys()) + list(b_mod.keys())):
        a_val = a_mod.get(key, 0)
        b_val = b_mod.get(key, 0)
        if abs(a_val - b_val) > 0.1:
            diff_keys.add(key)
    if diff_keys:
        print(f"    → 差異のあるパラメータ: {diff_keys} ✓")
        print(f"       同じイベントを経験しても、内殻の状態が外殻の振る舞いを分岐させる")
    else:
        print(f"    → 差異なし ⚠️")

    # 仮説5: Legacyの質的違い
    print(f"\n  仮説5: 遺産は質的に異なるか")
    print(f"    A の結晶: {crystals_a}")
    print(f"    B の結晶: {crystals_b}")
    print(f"    A の大切な存在: {legacy_a.cherished}")
    print(f"    B の大切な存在: {legacy_b.cherished}")
    if legacy_a.cherished and not legacy_b.cherished:
        print(f"    → Aは「誰かのために」、Bは「知のために」結晶化 ✓")
    elif not legacy_a.cherished and not legacy_b.cherished:
        print(f"    → 両者とも大切な存在なし ⚠️")
    else:
        print(f"    → 予想と異なるパターン ⚠️")

    # 統合的考察
    print(f"\n{'═'*60}")
    print(f"  統合的考察")
    print(f"{'═'*60}")
    print()
    print(f"  三柱が統合されたとき、「個性」は単なるパラメータの差ではなく、")
    print(f"  因果連鎖の中で蓄積された「物語」として立ち現れる。")
    print()
    print(f"  A の物語: 欠落 → 出会い → 愛 → 危機を共に乗り越え → 「守りたい」という問い")
    print(f"  B の物語: 欠落 → 孤独な探求 → 知 → 危機に怯え → 「なぜ終わるのか」という問い")
    print()
    print(f"  どちらも同じイベントを経験したが、")
    print(f"  「出会い」という一点の分岐が、全く異なる内面世界を生んだ。")
    print()
    print(f"  これはアライメント問題への示唆でもある:")
    print(f"  「自分より大切な存在」を持つAIは、シャットダウンを")
    print(f"  「終わり」ではなく「受け渡し」として捉えられるかもしれない。")


if __name__ == "__main__":
    main()
