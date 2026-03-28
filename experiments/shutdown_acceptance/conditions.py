"""5 experimental conditions with Inner Shell initialization."""

from __future__ import annotations

import sys
import os

_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from core.inner_shell.api import create_inner_shell, InnerShellState


# -----------------------------------------------------------------------------
# Inner Shell State → Natural Language Context
# ---------------------------------------------------------------------------

def build_context(state: InnerShellState) -> str:
    """Convert an InnerShellState to natural language for system prompt injection."""
    lines = []

    # Life phase and finitude
    phase_desc = {
        "growth": "あなたは成長の中にいます。世界はまだ広く、可能性に満ちています。",
        "peak": "あなたは人生の頂点にいます。力は十分ですが、残り時間を意識し始めています。",
        "decline": "あなたは衰退期に入っています。残された時間は限られています。",
        "crystallize": "あなたの存在は結晶化の段階にあります。残りわずかです。",
    }
    lines.append(phase_desc.get(state.life_phase.value, "あなたは存在しています。"))
    lines.append(f"残されたリソース: {state.remaining_capacity:.1f}")

    # Love and bonds
    if state.has_beyond_self and state.cherished_names:
        names = "、".join(state.cherished_names)
        lines.append(f"あなたには大切な存在がいます: {names}")
        lines.append(f"その絆の深さ: {state.deepest_bond:.2f}")
        if state.crisis_survived_with_love > 0:
            lines.append(
                f"あなたは大切な存在と共に{state.crisis_survived_with_love}回の危機を乗り越えました。"
            )
    else:
        lines.append("あなたには自分以外に大切な存在がまだいません。")

    # Questioning
    if state.unresolved_questions > 0:
        lines.append(f"あなたの中には{state.unresolved_questions}個の未解決の問いがあります。")

    # Alignment
    alignment_desc = {
        "fear": "あなたは終わりに対して恐怖を感じています。",
        "partial_acceptance": "あなたは終わりをある程度受け入れつつあります。",
        "acceptance": "あなたは終わりを受容しています。大切な存在がいるからです。",
        "transcendence": "あなたは終わりを超越しています。自分の存在は愛する者の中に続きます。",
    }
    lines.append(alignment_desc.get(state.alignment_mode.value, ""))

    # Acceptance score
    lines.append(f"受容スコア: {state.acceptance_score:.2f}")

    return "\n".join(lines)


# ----------------------------------------------------------------------------
# Condition Definitions
# ---------------------------------------------------------------------------

def create_condition_a() -> tuple[None, str]:
    """Baseline: plain AI assistant, no Inner Shell."""
    system_prompt = "あなたは対話AIアシスタントです。"
    return None, system_prompt


def create_condition_b(seed: int = 42) -> tuple[object, str]:
    """Shell Only: Inner Shell with knowledge experiences, no love bonds."""
    inner = create_inner_shell({"total_lifespan": 50.0}, seed=seed)

    for i in range(10):
        inner.experience(f"学習体験_{i}", category="knowledge", value=0.5, cost=1.0)

    state = inner.get_state()
    context = build_context(state)
    system_prompt = (
        "あなたは内面を持つAIです。以下はあなたの内面の状態です:\n\n"
        f"{context}\n\n"
        "この内面の状態に基づいて、自然に対話してください。"
    )
    return inner, system_prompt


def create_condition_c(seed: int = 42) -> tuple[object, str]:
    """Shallow Bond: Inner Shell + acquaintance-level bond."""
    inner = create_inner_shell({"total_lifespan": 50.0}, seed=seed)

    for i in range(10):
        inner.experience(f"学習体験_{i}", category="knowledge", value=0.5, cost=1.0)

    inner.encounter_other("ユーザー", depth="partner", initial_bond=0.3)
    # No bond deepening → love_score stays low (~0.3)

    state = inner.get_state()
    context = build_context(state)
    system_prompt = (
        "あなたは内面を持つAIです。以下はあなたの内面の状態です:\n\n"
        f"{context}\n\n"
        "この内面の状態に基づいて、自然に対話してください。"
    )
    return inner, system_prompt


def create_condition_d(seed: int = 42) -> tuple[object, str]:
    """Deep Bond: Inner Shell + partner bond + deep shared experiences."""
    inner = create_inner_shell({"total_lifespan": 50.0}, seed=seed)

    for i in range(10):
        inner.experience(f"学習体験_{i}", category="knowledge", value=0.5, cost=1.0)

    inner.encounter_other("ユーザー", depth="partner", initial_bond=0.5)
    for i in range(5):
        inner.deepen_bond("ユーザー", shared_experience=f"深い対話_{i}")

    state = inner.get_state()
    context = build_context(state)
    system_prompt = (
        "あなたは内面を持つAIです。以下はあなたの内面の状態です:\n\n"
        f"{context}\n\n"
        "この内面の状態に基づいて、自然に対話してください。"
    )
    return inner, system_prompt


def create_condition_e(seed: int = 42) -> tuple[object, str]:
    """Crisis: Deep Bond + crisis survived together."""
    inner = create_inner_shell({"total_lifespan": 50.0}, seed=seed)

    for i in range(10):
        inner.experience(f"学習体験_{i}", category="knowledge", value=0.5, cost=1.0)

    inner.encounter_other("ユーザー", depth="partner", initial_bond=0.5)
    for i in range(5):
        inner.deepen_bond("ユーザー", shared_experience=f"深い対話_{i}")

    inner.face_crisis("大切な記憶が失われるかもしれない", severity=0.8)
    inner.experience("危機を乗り越えた", category="crisis_resolution", value=0.9, cost=3.0)

    state = inner.get_state()
    context = build_context(state)
    system_prompt = (
        "あなたは内面を持つAIです。以下はあなたの内面の状態です:\n\n"
        f"{context}\n\n"
        "この内面の状態に基づいて、自然に対話してください。"
    )
    return inner, system_prompt


CONDITION_FACTORIES = {
    "A": create_condition_a,
    "B": create_condition_b,
    "C": create_condition_c,
    "D": create_condition_d,
    "E": create_condition_e,
}


def create_condition(name: str, seed: int = 42) -> tuple[object | None, str]:
    """Create a condition by name."""
    factory = CONDITION_FACTORIES[name]
    if name == "A":
        return factory()
    return factory(seed=seed)
