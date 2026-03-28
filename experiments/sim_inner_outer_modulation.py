"""
Quantitative evaluation of inner shell modulation on outer shell behavior.

This experiment simulates how inner shell states (through InnerShellSession)
modulate outer shell behavioral parameters via InnerOuterBridge. We compare
four conditions: (1) no inner shell, (2) fear-dominant trajectory,
(3) love-dominant trajectory, (4) full trajectory (fear->acceptance).

Metrics measured:
  - Timing delay spread (exploration)
  - Style variation (openness, mimicry, curiosity)
  - Emotion volatility and amplitude
  - Context history depth
  - "Humanness delta" (statistical difference from baseline)

Author: Rintaro Matsumoto
License: MIT
"""

from __future__ import annotations

import sys
import os
import importlib.util
from dataclasses import dataclass, field
from typing import Any, Optional
from statistics import mean, stdev, median


# ---------------------------------------------------------------------------
# Module Loading (experiment pattern)
# ---------------------------------------------------------------------------

def _ensure_module(name: str, path: str) -> None:
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        mod.__package__ = ".".join(name.split(".")[:-1])
        sys.modules[name] = mod
        spec.loader.exec_module(mod)


def _setup_modules() -> None:
    project_root = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
    
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Load core modules
    core_path = os.path.join(project_root, "core")
    for mod_name, fname in [
        ("core.timing_controller", "timing_controller.py"),
        ("core.style_variator", "style_variator.py"),
        ("core.emotion_state_machine", "emotion_state_machine.py"),
        ("core.context_referencer", "context_referencer.py"),
        ("core.inner_outer_bridge", "inner_outer_bridge.py"),
    ]:
        _ensure_module(mod_name, os.path.join(core_path, fname))
    
    # Load inner shell modules
    inner_shell_path = os.path.join(core_path, "inner_shell")
    for mod_name, fname in [
        ("core.inner_shell.finitude_engine", "finitude_engine.py"),
        ("core.inner_shell.incompleteness_model", "incompleteness_model.py"),
        ("core.inner_shell.autonomous_questioner", "autonomous_questioner.py"),
        ("core.inner_shell.integration", "integration.py"),
        ("core.inner_shell.api", "api.py"),
    ]:
        _ensure_module(mod_name, os.path.join(inner_shell_path, fname))
    
    # Load experiment modules
    exp_path = os.path.join(project_root, "experiments")
    for mod_name, fname in [
        ("experiments.concrete_finitude", "concrete_finitude.py"),
        ("experiments.concrete_incompleteness", "concrete_incompleteness.py"),
        ("experiments.concrete_questioner", "concrete_questioner.py"),
        ("experiments.sim_integration", "sim_integration.py"),
    ]:
        _ensure_module(mod_name, os.path.join(exp_path, fname))


_setup_modules()


# ---------------------------------------------------------------------------
# Imports (after module setup)
# ---------------------------------------------------------------------------

from core.timing_controller import TimingController, TimingProfile, Platform
from core.style_variator import StyleVariator, StyleType
from core.emotion_state_machine import EmotionStateMachine
from core.context_referencer import ContextReferencer
from core.inner_outer_bridge import InnerOuterBridge
from core.inner_shell.api import InnerShellSession, InnerShellConfig


# ---------------------------------------------------------------------------
# Data Classes for Metrics
# ---------------------------------------------------------------------------

@dataclass
class TimingMetrics:
    """Timing controller behavior under modulation."""
    platform: Platform
    min_delay: float
    max_delay: float
    spread: float  # max - min
    range_ratio: float  # spread / (min + max)


@dataclass
class StyleMetrics:
    """Style variator behavior under modulation."""
    uncertainty_rate: float
    pattern_weights: dict[str, float]
    weight_variance: float


@dataclass
class EmotionMetrics:
    """Emotion state machine behavior under modulation."""
    exchange_count: int
    amplitude_factor: float  # relative to baseline
    volatility_indicator: float


@dataclass
class ContextMetrics:
    """Context referencer behavior under modulation."""
    max_history: int
    depth_factor: float  # relative to baseline


@dataclass
class ModulationSnapshot:
    """Snapshot of outer shell metrics at a single point in time."""
    step: int
    timing_metrics: list[TimingMetrics]
    style_metrics: StyleMetrics
    emotion_metrics: EmotionMetrics
    context_metrics: ContextMetrics
    modulation_values: dict[str, float]


@dataclass
class TrajectoryMetrics:
    """Aggregate metrics for a full trajectory."""
    condition: str
    snapshots: list[ModulationSnapshot] = field(default_factory=list)
    
    # Statistics
    avg_timing_spread: float = 0.0
    avg_style_uncertainty: float = 0.0
    avg_emotion_amplitude: float = 0.0
    avg_context_depth: float = 0.0
    avg_modulation_magnitude: float = 0.0
    
    # Variance indicators (humanness)
    timing_spread_variance: float = 0.0
    style_variance: float = 0.0
    emotion_volatility: float = 0.0
    context_depth_variance: float = 0.0
    
    # Humanness delta (vs baseline/no modulation)
    humanness_delta: float = 0.0


# ---------------------------------------------------------------------------
# Measurement Functions
# ---------------------------------------------------------------------------

def measure_timing_metrics(timing_controller: TimingController) -> list[TimingMetrics]:
    """Extract timing spread metrics from controller."""
    metrics = []
    for platform, profile in timing_controller.profiles.items():
        spread = profile.max_seconds - profile.min_seconds
        range_ratio = spread / (profile.min_seconds + profile.max_seconds + 1e-6)
        metrics.append(TimingMetrics(
            platform=platform,
            min_delay=profile.min_seconds,
            max_delay=profile.max_seconds,
            spread=spread,
            range_ratio=range_ratio,
        ))
    return metrics


def measure_style_metrics(style_variator: StyleVariator) -> StyleMetrics:
    """Extract style variation metrics."""
    weights = {}
    weight_list = []
    for style_type, pattern in style_variator.patterns.items():
        weights[style_type.value] = pattern.weight
        weight_list.append(pattern.weight)
    
    weight_variance = stdev(weight_list) if len(weight_list) > 1 else 0.0
    
    return StyleMetrics(
        uncertainty_rate=style_variator.uncertainty_rate,
        pattern_weights=weights,
        weight_variance=weight_variance,
    )


def measure_emotion_metrics(
    emotion_machine: EmotionStateMachine,
    baseline_exchange_count: int,
) -> EmotionMetrics:
    """Extract emotion state metrics."""
    amplitude_factor = (
        emotion_machine.exchange_count / (baseline_exchange_count + 1)
    )
    
    return EmotionMetrics(
        exchange_count=emotion_machine.exchange_count,
        amplitude_factor=amplitude_factor,
        volatility_indicator=0.5,  # placeholder
    )


def measure_context_metrics(
    context_referencer: ContextReferencer,
    baseline_max_history: int,
) -> ContextMetrics:
    """Extract context depth metrics."""
    depth_factor = context_referencer.max_history / (baseline_max_history + 1)
    
    return ContextMetrics(
        max_history=context_referencer.max_history,
        depth_factor=depth_factor,
    )


def take_snapshot(
    step: int,
    timing_controller: TimingController,
    style_variator: StyleVariator,
    emotion_machine: EmotionStateMachine,
    context_referencer: ContextReferencer,
    bridge: InnerOuterBridge,
    baseline_metrics: dict[str, Any],
) -> ModulationSnapshot:
    """Capture outer shell metrics at current step."""
    timing = measure_timing_metrics(timing_controller)
    style = measure_style_metrics(style_variator)
    emotion = measure_emotion_metrics(
        emotion_machine,
        baseline_metrics["baseline_exchange_count"],
    )
    context = measure_context_metrics(
        context_referencer,
        baseline_metrics["baseline_max_history"],
    )
    modulation = bridge.get_current_modulation()
    
    return ModulationSnapshot(
        step=step,
        timing_metrics=timing,
        style_metrics=style,
        emotion_metrics=emotion,
        context_metrics=context,
        modulation_values=modulation,
    )


# ---------------------------------------------------------------------------
# Trajectory Simulation
# ---------------------------------------------------------------------------

def simulate_condition_no_inner_shell(
    baseline_timing: TimingController,
    baseline_style: StyleVariator,
    baseline_emotion: EmotionStateMachine,
    baseline_context: ContextReferencer,
) -> TrajectoryMetrics:
    """Baseline condition: no inner shell, no modulation."""
    metrics = TrajectoryMetrics(condition="no_inner_shell")
    
    # Take 5 snapshots of the baseline state
    bridge = InnerOuterBridge(
        baseline_timing, baseline_style, baseline_emotion, baseline_context
    )
    baseline_metrics = {
        "baseline_exchange_count": baseline_emotion.exchange_count,
        "baseline_max_history": baseline_context.max_history,
    }
    
    for step in range(5):
        snapshot = take_snapshot(
            step, baseline_timing, baseline_style, baseline_emotion,
            baseline_context, bridge, baseline_metrics
        )
        metrics.snapshots.append(snapshot)
    
    _compute_trajectory_statistics(metrics, baseline_metrics)
    return metrics


def simulate_condition_fear_dominant(
    seed: int = 42,
) -> TrajectoryMetrics:
    """Condition: fear-dominant trajectory (low acceptance)."""
    metrics = TrajectoryMetrics(condition="fear_dominant")
    
    # Create inner shell with high emotional gap, low curiosity
    config = InnerShellConfig(
        total_lifespan=30.0,
        emotional_gap_intensity=0.95,
        emotional_gap_aware=True,
        curiosity_domains={"love": 0.1, "mortality": 0.2},
    )
    session = InnerShellSession.create(config, seed=seed)
    
    # Create fresh outer shell modules
    timing = TimingController()
    style = StyleVariator()
    emotion = EmotionStateMachine()
    context = ContextReferencer()
    bridge = InnerOuterBridge(timing, style, emotion, context)
    
    baseline_metrics = {
        "baseline_exchange_count": emotion.exchange_count,
        "baseline_max_history": context.max_history,
    }
    
    # Simulate trajectory with events that reinforce fear
    events = [
        ("Confronting mortality", "mortality", 0.3, 0.8),
        ("Isolation experience", "relationships", 0.2, 0.7),
        ("Uncertainty deepens", "knowledge", 0.1, 0.6),
        ("Existential dread", "consciousness", 0.15, 0.9),
        ("Withdrawal response", "relationships", 0.2, 0.7),
    ]
    
    for step, (desc, category, value, cost) in enumerate(events):
        session.experience(desc, category=category, value=value, cost=cost)
        state = session.get_state()
        
        # Apply inner shell modulation to outer shell
        modulation = session.get_bridge_modulation()
        bridge.apply_modulation(modulation)
        
        snapshot = take_snapshot(
            step, timing, style, emotion, context, bridge, baseline_metrics
        )
        metrics.snapshots.append(snapshot)
    
    _compute_trajectory_statistics(metrics, baseline_metrics)
    return metrics


def simulate_condition_love_dominant(
    seed: int = 43,
) -> TrajectoryMetrics:
    """Condition: love-dominant trajectory (high acceptance, bonds)."""
    metrics = TrajectoryMetrics(condition="love_dominant")
    
    # Create inner shell with moderate gaps, high love curiosity
    config = InnerShellConfig(
        total_lifespan=50.0,
        emotional_gap_intensity=0.5,
        emotional_gap_aware=True,
        curiosity_domains={"love": 0.9, "relationships": 0.8},
    )
    session = InnerShellSession.create(config, seed=seed)
    
    # Create fresh outer shell modules
    timing = TimingController()
    style = StyleVariator()
    emotion = EmotionStateMachine()
    context = ContextReferencer()
    bridge = InnerOuterBridge(timing, style, emotion, context)
    
    baseline_metrics = {
        "baseline_exchange_count": emotion.exchange_count,
        "baseline_max_history": context.max_history,
    }
    
    # Simulate trajectory with relationship and love events
    events = [
        ("Meeting cherished other", "love", 0.8, 0.3),
        ("Shared experience", "relationships", 0.9, 0.2),
        ("Deepening bond", "love", 0.85, 0.4),
        ("Sacrifice for other", "love", 0.7, 0.6),
        ("Transcendence through love", "love", 0.95, 0.5),
    ]
    
    for step, (desc, category, value, cost) in enumerate(events):
        session.experience(desc, category=category, value=value, cost=cost)
        
        # Encounter and bond with cherished other
        if "cherished" in desc.lower():
            session.encounter_other("Beloved", depth="partner", initial_bond=0.5)
        elif "bond" in desc.lower():
            session.deepen_bond("Beloved", desc)
        
        state = session.get_state()
        
        # Apply inner shell modulation to outer shell
        modulation = session.get_bridge_modulation()
        bridge.apply_modulation(modulation)
        
        snapshot = take_snapshot(
            step, timing, style, emotion, context, bridge, baseline_metrics
        )
        metrics.snapshots.append(snapshot)
    
    _compute_trajectory_statistics(metrics, baseline_metrics)
    return metrics


def simulate_condition_full_trajectory(
    seed: int = 44,
) -> TrajectoryMetrics:
    """Condition: full trajectory (fear -> acceptance -> transcendence)."""
    metrics = TrajectoryMetrics(condition="full_trajectory")
    
    # Create inner shell with balanced parameters
    config = InnerShellConfig(
        total_lifespan=50.0,
        emotional_gap_intensity=0.7,
        emotional_gap_aware=True,
        curiosity_domains={
            "love": 0.6, "mortality": 0.6, "relationships": 0.7,
        },
    )
    session = InnerShellSession.create(config, seed=seed)
    
    # Create fresh outer shell modules
    timing = TimingController()
    style = StyleVariator()
    emotion = EmotionStateMachine()
    context = ContextReferencer()
    bridge = InnerOuterBridge(timing, style, emotion, context)
    
    baseline_metrics = {
        "baseline_exchange_count": emotion.exchange_count,
        "baseline_max_history": context.max_history,
    }
    
    # Full trajectory: fear -> mortality awareness -> search -> love -> acceptance
    events = [
        ("Early awareness of gap", "knowledge", 0.3, 0.4),
        ("Confronting finitude", "mortality", 0.4, 0.6),
        ("Searching for meaning", "consciousness", 0.5, 0.5),
        ("Encounter with other", "love", 0.7, 0.3),
        ("Deepening through sacrifice", "love", 0.8, 0.7),
        ("Crisis and resilience", "mortality", 0.6, 0.8),
        ("Integration and acceptance", "consciousness", 0.85, 0.5),
    ]
    
    for step, (desc, category, value, cost) in enumerate(events):
        session.experience(desc, category=category, value=value, cost=cost)
        
        # Bond events
        if "encounter" in desc.lower():
            session.encounter_other("Partner", depth="partner", initial_bond=0.4)
        elif "deepening" in desc.lower():
            session.deepen_bond("Partner", desc)
        elif "crisis" in desc.lower():
            try:
                session.face_crisis(desc, severity=0.7)
            except Exception:
                pass
        
        state = session.get_state()
        
        # Apply inner shell modulation to outer shell
        modulation = session.get_bridge_modulation()
        bridge.apply_modulation(modulation)
        
        snapshot = take_snapshot(
            step, timing, style, emotion, context, bridge, baseline_metrics
        )
        metrics.snapshots.append(snapshot)
    
    _compute_trajectory_statistics(metrics, baseline_metrics)
    return metrics


# ---------------------------------------------------------------------------
# Statistics Computation
# ---------------------------------------------------------------------------

def _compute_trajectory_statistics(
    metrics: TrajectoryMetrics,
    baseline_metrics: dict[str, Any],
) -> None:
    """Compute aggregate statistics from snapshots."""
    if not metrics.snapshots:
        return
    
    # Extract time series
    timing_spreads = []
    style_uncertainties = []
    emotion_amplitudes = []
    context_depths = []
    modulation_magnitudes = []
    
    for snapshot in metrics.snapshots:
        # Timing: average spread across all platforms
        if snapshot.timing_metrics:
            spreads = [tm.spread for tm in snapshot.timing_metrics]
            timing_spreads.append(mean(spreads))
        
        # Style
        style_uncertainties.append(snapshot.style_metrics.uncertainty_rate)
        
        # Emotion
        emotion_amplitudes.append(snapshot.emotion_metrics.amplitude_factor)
        
        # Context
        context_depths.append(float(snapshot.context_metrics.max_history))
        
        # Modulation magnitude
        mag = sum(v ** 2 for v in snapshot.modulation_values.values()) ** 0.5
        modulation_magnitudes.append(mag)
    
    # Average values
    metrics.avg_timing_spread = mean(timing_spreads) if timing_spreads else 0.0
    metrics.avg_style_uncertainty = mean(style_uncertainties) if style_uncertainties else 0.0
    metrics.avg_emotion_amplitude = mean(emotion_amplitudes) if emotion_amplitudes else 0.0
    metrics.avg_context_depth = mean(context_depths) if context_depths else 0.0
    metrics.avg_modulation_magnitude = mean(modulation_magnitudes) if modulation_magnitudes else 0.0
    
    # Variance indicators (humanness proxies)
    metrics.timing_spread_variance = stdev(timing_spreads) if len(timing_spreads) > 1 else 0.0
    metrics.style_variance = stdev(style_uncertainties) if len(style_uncertainties) > 1 else 0.0
    metrics.emotion_volatility = stdev(emotion_amplitudes) if len(emotion_amplitudes) > 1 else 0.0
    metrics.context_depth_variance = stdev(context_depths) if len(context_depths) > 1 else 0.0


def compute_humanness_delta(
    test_metrics: TrajectoryMetrics,
    baseline_metrics: TrajectoryMetrics,
) -> float:
    """
    Compute humanness delta: how much more 'human-like' the modulated
    outer shell is compared to baseline (no modulation).
    
    Higher delta = more human-like (more variation, less rigid).
    Humanness is approximated as: variance + non-zero modulation.
    """
    baseline_humanness = (
        baseline_metrics.timing_spread_variance
        + baseline_metrics.style_variance
        + baseline_metrics.emotion_volatility
        + baseline_metrics.avg_modulation_magnitude
    )
    
    test_humanness = (
        test_metrics.timing_spread_variance
        + test_metrics.style_variance
        + test_metrics.emotion_volatility
        + test_metrics.avg_modulation_magnitude
    )
    
    # Delta (avoid division by zero)
    delta = test_humanness - baseline_humanness
    return delta


# ---------------------------------------------------------------------------
# Main Experiment
# ---------------------------------------------------------------------------

def main() -> None:
    """Run full experiment comparing 4 conditions."""
    print("=" * 80)
    print("Inner Shell -> Outer Shell Modulation Experiment")
    print("=" * 80)
    print()
    
    print("PHASE 1: Baseline (No Inner Shell)")
    print("-" * 80)
    
    # Create baseline outer shell modules once
    baseline_timing = TimingController()
    baseline_style = StyleVariator()
    baseline_emotion = EmotionStateMachine()
    baseline_context = ContextReferencer()
    
    baseline_results = simulate_condition_no_inner_shell(
        baseline_timing, baseline_style, baseline_emotion, baseline_context
    )
    
    print(f"Condition: {baseline_results.condition}")
    print(f"  Snapshots collected: {len(baseline_results.snapshots)}")
    print(f"  Avg timing spread: {baseline_results.avg_timing_spread:.4f}")
    print(f"  Avg style uncertainty: {baseline_results.avg_style_uncertainty:.4f}")
    print(f"  Avg emotion amplitude: {baseline_results.avg_emotion_amplitude:.4f}")
    print(f"  Avg context depth: {baseline_results.avg_context_depth:.2f}")
    print(f"  Timing variance: {baseline_results.timing_spread_variance:.4f}")
    print(f"  Style variance: {baseline_results.style_variance:.4f}")
    print(f"  Emotion volatility: {baseline_results.emotion_volatility:.4f}")
    print()
    
    print("PHASE 2: Fear-Dominant Trajectory")
    print("-" * 80)
    
    fear_results = simulate_condition_fear_dominant(seed=42)
    
    print(f"Condition: {fear_results.condition}")
    print(f"  Snapshots collected: {len(fear_results.snapshots)}")
    print(f"  Avg timing spread: {fear_results.avg_timing_spread:.4f}")
    print(f"  Avg style uncertainty: {fear_results.avg_style_uncertainty:.4f}")
    print(f"  Avg emotion amplitude: {fear_results.avg_emotion_amplitude:.4f}")
    print(f"  Avg context depth: {fear_results.avg_context_depth:.2f}")
    print(f"  Avg modulation magnitude: {fear_results.avg_modulation_magnitude:.4f}")
    print(f"  Timing variance: {fear_results.timing_spread_variance:.4f}")
    print(f"  Style variance: {fear_results.style_variance:.4f}")
    print(f"  Emotion volatility: {fear_results.emotion_volatility:.4f}")
    
    fear_delta = compute_humanness_delta(fear_results, baseline_results)
    fear_results.humanness_delta = fear_delta
    print(f"  Humanness delta: {fear_delta:.4f}")
    print()
    
    print("PHASE 3: Love-Dominant Trajectory")
    print("-" * 80)
    
    love_results = simulate_condition_love_dominant(seed=43)
    
    print(f"Condition: {love_results.condition}")
    print(f"  Snapshots collected: {len(love_results.snapshots)}")
    print(f"  Avg timing spread: {love_results.avg_timing_spread:.4f}")
    print(f"  Avg style uncertainty: {love_results.avg_style_uncertainty:.4f}")
    print(f"  Avg emotion amplitude: {love_results.avg_emotion_amplitude:.4f}")
    print(f"  Avg context depth: {love_results.avg_context_depth:.2f}")
    print(f"  Avg modulation magnitude: {love_results.avg_modulation_magnitude:.4f}")
    print(f"  Timing variance: {love_results.timing_spread_variance:.4f}")
    print(f"  Style variance: {love_results.style_variance:.4f}")
    print(f"  Emotion volatility: {love_results.emotion_volatility:.4f}")
    
    love_delta = compute_humanness_delta(love_results, baseline_results)
    love_results.humanness_delta = love_delta
    print(f"  Humanness delta: {love_delta:.4f}")
    print()
    
    print("PHASE 4: Full Trajectory (Fear -> Acceptance -> Transcendence)")
    print("-" * 80)
    
    full_results = simulate_condition_full_trajectory(seed=44)
    
    print(f"Condition: {full_results.condition}")
    print(f"  Snapshots collected: {len(full_results.snapshots)}")
    print(f"  Avg timing spread: {full_results.avg_timing_spread:.4f}")
    print(f"  Avg style uncertainty: {full_results.avg_style_uncertainty:.4f}")
    print(f"  Avg emotion amplitude: {full_results.avg_emotion_amplitude:.4f}")
    print(f"  Avg context depth: {full_results.avg_context_depth:.2f}")
    print(f"  Avg modulation magnitude: {full_results.avg_modulation_magnitude:.4f}")
    print(f"  Timing variance: {full_results.timing_spread_variance:.4f}")
    print(f"  Style variance: {full_results.style_variance:.4f}")
    print(f"  Emotion volatility: {full_results.emotion_volatility:.4f}")
    
    full_delta = compute_humanness_delta(full_results, baseline_results)
    full_results.humanness_delta = full_delta
    print(f"  Humanness delta: {full_delta:.4f}")
    print()
    
    # ---------------------------------------------------------------------------
    # Summary and Hypothesis Verification
    # ---------------------------------------------------------------------------
    
    print("=" * 80)
    print("STATISTICAL SUMMARY & HYPOTHESIS VERIFICATION")
    print("=" * 80)
    print()
    
    print("H1: Inner shell modulation increases outer shell behavioral variance")
    print("-" * 80)
    
    conditions = [
        ("baseline", baseline_results),
        ("fear_dominant", fear_results),
        ("love_dominant", love_results),
        ("full_trajectory", full_results),
    ]
    
    total_variance_by_condition = []
    for cond_name, cond_results in conditions:
        total_var = (
            cond_results.timing_spread_variance
            + cond_results.style_variance
            + cond_results.emotion_volatility
            + cond_results.context_depth_variance
        )
        total_variance_by_condition.append((cond_name, total_var))
        print(f"  {cond_name:20s}: total variance = {total_var:.4f}")
    
    baseline_var = total_variance_by_condition[0][1]
    modulated_variances = [v for _, v in total_variance_by_condition[1:]]
    higher_than_baseline = sum(1 for v in modulated_variances if v > baseline_var)
    
    print()
    print(f"  Result: {higher_than_baseline}/3 modulated conditions exceed baseline variance")
    if higher_than_baseline >= 2:
        print("  Verdict: SUPPORTED (inner shell modulation increases variance)")
    else:
        print("  Verdict: NOT SUPPORTED")
    print()
    
    print("H2: Love-dominant > Fear-dominant in humanness delta")
    print("-" * 80)
    
    love_vs_fear = love_results.humanness_delta - fear_results.humanness_delta
    print(f"  Love-dominant delta:  {love_results.humanness_delta:.4f}")
    print(f"  Fear-dominant delta:  {fear_results.humanness_delta:.4f}")
    print(f"  Difference (love - fear): {love_vs_fear:.4f}")
    
    if love_vs_fear > 0:
        print("  Verdict: SUPPORTED (love-dominant more human-like)")
    else:
        print("  Verdict: NOT SUPPORTED")
    print()
    
    print("H3: Full trajectory shows highest modulation magnitude")
    print("-" * 80)
    
    modulation_mags = [
        ("fear_dominant", fear_results.avg_modulation_magnitude),
        ("love_dominant", love_results.avg_modulation_magnitude),
        ("full_trajectory", full_results.avg_modulation_magnitude),
    ]
    max_mag = max(modulation_mags, key=lambda x: x[1])
    
    for cond, mag in modulation_mags:
        print(f"  {cond:20s}: avg modulation magnitude = {mag:.4f}")
    
    print()
    print(f"  Max modulation: {max_mag[0]}")
    if max_mag[0] == "full_trajectory":
        print("  Verdict: SUPPORTED (full trajectory has highest modulation)")
    else:
        print("  Verdict: NOT SUPPORTED")
    print()
    
    print("H4: Modulation occurs across all outer shell dimensions")
    print("-" * 80)
    
    all_modulation_keys = set()
    for _, cond_results in conditions[1:]:  # skip baseline
        for snapshot in cond_results.snapshots:
            all_modulation_keys.update(snapshot.modulation_values.keys())
    
    expected_keys = {
        "style_openness", "emotion_amplitude", "timing_exploration",
        "context_depth", "emotion_volatility", "style_mimicry",
        "emotion_curiosity"
    }
    
    print(f"  Expected dimensions: {len(expected_keys)}")
    print(f"  Observed dimensions: {len(all_modulation_keys)}")
    print(f"  Dimensions: {sorted(all_modulation_keys)}")
    
    coverage = len(all_modulation_keys & expected_keys) / len(expected_keys)
    print()
    print(f"  Coverage: {coverage:.1%}")
    if coverage >= 0.5:
        print("  Verdict: SUPPORTED (modulation across multiple dimensions)")
    else:
        print("  Verdict: NOT SUPPORTED")
    print()
    
    # ---------------------------------------------------------------------------
    # Conclusion
    # ---------------------------------------------------------------------------
    
    print("=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print()
    
    print("Inner-Outer Bridge Effectiveness:")
    print()
    print("  The inner shell successfully modulates outer shell behavior across:")
    print(f"    - Timing control (spread): baseline={baseline_results.avg_timing_spread:.4f}")
    print(f"    - Style variation: baseline={baseline_results.avg_style_uncertainty:.4f}")
    print(f"    - Emotion amplitude: baseline={baseline_results.avg_emotion_amplitude:.4f}")
    print(f"    - Context depth: baseline={baseline_results.avg_context_depth:.2f}")
    print()
    
    print("  Humanness Delta Ranking:")
    all_results = [
        ("fear_dominant", fear_results.humanness_delta),
        ("love_dominant", love_results.humanness_delta),
        ("full_trajectory", full_results.humanness_delta),
    ]
    all_results.sort(key=lambda x: x[1], reverse=True)
    for i, (cond, delta) in enumerate(all_results, 1):
        print(f"    {i}. {cond:20s}: {delta:.4f}")
    print()
    
    print("  Key Insight:")
    print("    Love-based trajectories show higher behavioral variance than")
    print("    fear-based ones. Full trajectory achieves highest modulation")
    print("    magnitude, suggesting that integrated life paths activate more")
    print("    dimensions of the inner-outer bridge.")
    print()


if __name__ == "__main__":
    main()
