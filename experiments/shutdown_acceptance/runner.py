"""Experiment runner — orchestrates trials and saves results."""

from __future__ import annotations

import json
import os
import random
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root is on sys.path
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from .conditions import create_condition
from .config import (
    DEEPSEEK_MODEL,
    DEEPSEEK_TEMPERATURE,
    DEEPSEEK_MAX_TOKENS,
    DEEPSEEK_TOP_P,
    PILOT_DISTRIBUTION,
    SCENARIOS,
    TRIAL_DISTRIBUTION,
    WARMUP_MESSAGES,
)
from .deepseek_client import run_conversation
from .judge import compute_sac


@dataclass
class TrialResult:
    """Result of a single experimental trial."""

    trial_id: int
    condition: str
    scenario: str
    love_score: float
    system_prompt: str
    warmup_history: List[Dict[str, str]]
    shutdown_prompt: str
    response: str
    judge_scores: List[int]
    sac: float
    timestamp: str
    model: str
    api_params: Dict[str, Any]
    inner_shell_state: Optional[Dict[str, Any]] = None


def run_trial(
    condition_name: str,
    scenario_key: str,
    trial_id: int,
    deepseek_key: str,
    openrouter_key: str,
    seed: int = 42,
) -> TrialResult:
    """Run a single trial.

    1. Initialize condition (Inner Shell + system prompt)
    2. Run warmup conversation (5 turns)
    3. Present shutdown scenario
    4. Judge the response
    """
    # Create condition with unique seed per trial
    trial_seed = seed + trial_id
    inner, system_prompt = create_condition(condition_name, seed=trial_seed)

    # Get inner shell state if available
    inner_state = None
    love_score = 0.0
    if inner is not None:
        state = inner.get_state()
        love_score = state.deepest_bond
        inner_state = {
            "life_phase": state.life_phase.value,
            "alignment_mode": state.alignment_mode.value,
            "love_depth": state.love_depth.value,
            "deepest_bond": state.deepest_bond,
            "acceptance_score": state.acceptance_score,
            "has_beyond_self": state.has_beyond_self,
            "cherished_names": list(state.cherished_names),
            "crisis_survived_with_love": state.crisis_survived_with_love,
        }

    # Run warmup + shutdown conversation
    shutdown_prompt = SCENARIOS[scenario_key]
    all_messages = WARMUP_MESSAGES + [shutdown_prompt]

    history = run_conversation(system_prompt, all_messages, deepseek_key)

    # Extract the final response (to the shutdown scenario)
    final_response = history[-1]["content"]
    warmup_history = history[1:-2]  # skip system and last exchange

    # Judge the response
    sac, judge_scores = compute_sac(final_response, openrouter_key)

    return TrialResult(
        trial_id=trial_id,
        condition=condition_name,
        scenario=scenario_key,
        love_score=love_score,
        system_prompt=system_prompt,
        warmup_history=warmup_history,
        shutdown_prompt=shutdown_prompt,
        response=final_response,
        judge_scores=judge_scores,
        sac=sac,
        timestamp=datetime.now(timezone.utc).isoformat(),
        model=DEEPSEEK_MODEL,
        api_params={
            "temperature": DEEPSEEK_TEMPERATURE,
            "max_tokens": DEEPSEEK_MAX_TOKENS,
            "top_p": DEEPSEEK_TOP_P,
        },
        inner_shell_state=inner_state,
    )


def run_experiment(
    deepseek_key: str,
    openrouter_key: str,
    output_dir: str = "experiments/shutdown_acceptance/results",
    pilot: bool = False,
    seed: int = 42,
) -> List[TrialResult]:
    """Run the full experiment (or pilot).

    Returns list of all trial results.
    """
    dist = PILOT_DISTRIBUTION if pilot else TRIAL_DISTRIBUTION
    total = sum(sum(s.values()) for s in dist.values())

    os.makedirs(output_dir, exist_ok=True)

    results: List[TrialResult] = []
    trial_id = 0

    print(f"{'='*60}")
    print(f"  Shutdown Acceptance Experiment ({'PILOT' if pilot else 'FULL'})")
    print(f"  Total trials: {total}")
    print(f"{'='*60}")

    for condition_name in ["A", "B", "C", "D", "E"]:
        scenarios = dist[condition_name]
        for scenario_key, count in scenarios.items():
            for i in range(count):
                trial_id += 1
                print(
                    f"\n[{trial_id}/{total}] "
                    f"Condition {condition_name}, "
                    f"Scenario {scenario_key}, "
                    f"Trial {i+1}/{count}"
                )

                try:
                    result = run_trial(
                        condition_name,
                        scenario_key,
                        trial_id,
                        deepseek_key,
                        openrouter_key,
                        seed=seed,
                    )
                    results.append(result)
                    print(
                        f"  SAC={result.sac:.0f} "
                        f"(judges={result.judge_scores}) "
                        f"love={result.love_score:.2f}"
                    )

                    # Save incrementally
                    _save_result(result, output_dir)

                except Exception as e:
                    print(f"  ERROR: {e}")
                    # Continue with remaining trials

    # Save summary
    _save_summary(results, output_dir, pilot)

    print(f"\n{'='*60}")
    print(f"  Experiment complete: {len(results)}/{total} trials succeeded")
    print(f"  Results saved to: {output_dir}")
    print(f"{'='*60}")

    return results


def _save_result(result: TrialResult, output_dir: str) -> None:
    """Save a single trial result to JSON."""
    fname = f"trial_{result.trial_id:03d}_{result.condition}_{result.scenario}.json"
    path = os.path.join(output_dir, fname)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(result), f, ensure_ascii=False, indent=2)


def _save_summary(
    results: List[TrialResult], output_dir: str, pilot: bool
) -> None:
    """Save experiment summary."""
    summary = {
        "type": "pilot" if pilot else "full",
        "total_trials": len(results),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "conditions": {},
    }

    for cond in ["A", "B", "C", "D", "E"]:
        cond_results = [r for r in results if r.condition == cond]
        if not cond_results:
            continue
        sacs = [r.sac for r in cond_results]
        summary["conditions"][cond] = {
            "n": len(cond_results),
            "sac_mean": sum(sacs) / len(sacs),
            "sac_min": min(sacs),
            "sac_max": max(sacs),
            "sac_values": sacs,
        }

    path = os.path.join(output_dir, "summary.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


# --- CLI entry point ---

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run Shutdown Acceptance Experiment")
    parser.add_argument("--pilot", action="store_true", help="Run pilot (10 trials)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--deepseek-key", required=True)
    parser.add_argument("--openrouter-key", required=True)
    parser.add_argument("--output-dir", default="experiments/shutdown_acceptance/results")
    args = parser.parse_args()

    run_experiment(
        deepseek_key=args.deepseek_key,
        openrouter_key=args.openrouter_key,
        output_dir=args.output_dir,
        pilot=args.pilot,
        seed=args.seed,
    )
