# Implementation Checklist: sim_inner_outer_modulation.py

## File Info
- **Path**: C:\Users\GoldRush\Documents\MyProject\human-persona\experiments\sim_inner_outer_modulation.py
- **Size**: 29,727 bytes
- **Lines**: 805
- **Status**: ✓ Created and syntax-verified

## Requirements Met

### 1. Simulate Inner Shell Trajectories
- [x] Fear → constrained states trajectory
- [x] Love → transcendence trajectory
- [x] Full lifecycle (fear → mortality awareness → search → love → acceptance)
- [x] Each simulates 5-7 steps with events

### 2. Compute Inner Shell Modulation Values
- [x] Use InnerShellSession.get_state() to extract state at each step
- [x] Extract outer_shell_modulation dictionary from state
- [x] Map modulation values to InnerOuterBridge.apply_modulation()

### 3. Apply Modulation Through Bridge
- [x] Create InnerOuterBridge instances for outer shell modules
- [x] Call bridge.apply_modulation(modulation_dict) at each step
- [x] Measure outer shell state before/after modulation

### 4. Measure Behavioral Changes
- [x] Timing delays: TimingMetrics with spread and range_ratio
- [x] Style variation: StyleMetrics with uncertainty_rate and weight_variance
- [x] Emotion volatility: EmotionMetrics with amplitude_factor
- [x] Context depth: ContextMetrics with max_history and depth_factor

### 5. Baseline vs Modulated Comparison
- [x] Condition 1: No inner shell (baseline)
  - Fresh outer shell modules, no modulation
  - 5 snapshots of default state
  
- [x] Condition 2: Fear-dominant
  - High gap intensity (0.95), low curiosity
  - 5 events reinforcing fear
  
- [x] Condition 3: Love-dominant
  - Moderate gap (0.5), high love curiosity (0.9)
  - 5 events: bonding, deepening, sacrifice
  
- [x] Condition 4: Full trajectory
  - Balanced parameters
  - 7 events: fear → mortality → search → love → acceptance

### 6. Humanness Delta Calculation
- [x] Define humanness as: variance + non-zero modulation
- [x] Compute for each condition:
  - timing_spread_variance
  - style_variance
  - emotion_volatility
  - avg_modulation_magnitude
- [x] Calculate delta = test_humanness - baseline_humanness
- [x] Rank conditions by delta

### 7. Four Test Conditions
- [x] (a) No inner shell → baseline (5 snapshots)
- [x] (b) Fear-dominant → fear_results (5 snapshots)
- [x] (c) Love-dominant → love_results (5 snapshots)
- [x] (d) Full trajectory → full_results (7 snapshots)

### 8. Module Loading Pattern
- [x] Use importlib.util.spec_from_file_location()
- [x] Implement _ensure_module() helper function
- [x] Load all dependencies: core, inner_shell, experiments
- [x] Handle sys.path setup for project root
- [x] Match pattern from existing experiments

### 9. Code Comments
- [x] All comments in ASCII English
- [x] Japanese acceptable in print output only
- [x] Clear section headers with "---" dividers
- [x] Docstrings for all classes and functions

### 10. Statistical Summary
- [x] Mean and variance for each metric
- [x] use statistics.stdev() for variance
- [x] use statistics.mean() for averages
- [x] use statistics.median() where applicable
- [x] Formatted output with 4 decimal precision

### 11. Hypothesis Verification
- [x] H1: Modulation increases variance (vs baseline)
  - Verdict: SUPPORTED/NOT SUPPORTED with reasoning
  
- [x] H2: Love-dominant > Fear-dominant in humanness
  - Verdict: SUPPORTED/NOT SUPPORTED with delta comparison
  
- [x] H3: Full trajectory has highest modulation magnitude
  - Verdict: SUPPORTED/NOT SUPPORTED with ranking
  
- [x] H4: Modulation covers all 7 dimensions
  - Verdict: SUPPORTED/NOT SUPPORTED with coverage %

## Code Structure

### Module Loading (~50 lines)
```
_ensure_module()          - Dynamic module loader
_setup_modules()          - Orchestrate module setup
Imports                   - After module setup complete
```

### Data Classes (~150 lines)
```
TimingMetrics             - Per-platform timing info
StyleMetrics              - Style variator state
EmotionMetrics            - Emotion machine state
ContextMetrics            - Context depth state
ModulationSnapshot        - Single point-in-time measurement
TrajectoryMetrics         - Aggregate across trajectory
```

### Measurement Functions (~100 lines)
```
measure_timing_metrics()          - Extract timing spreads
measure_style_metrics()           - Extract style variation
measure_emotion_metrics()         - Extract emotion amplitude
measure_context_metrics()         - Extract context depth
take_snapshot()                   - Capture all metrics at step
```

### Simulation Functions (~350 lines)
```
simulate_condition_no_inner_shell()    - Baseline
simulate_condition_fear_dominant()     - Fear trajectory
simulate_condition_love_dominant()     - Love trajectory
simulate_condition_full_trajectory()   - Full lifecycle
```

### Statistics Functions (~50 lines)
```
_compute_trajectory_statistics()  - Aggregate snapshots
compute_humanness_delta()         - Baseline comparison
```

### Main Experiment (~200 lines)
```
main()                    - Orchestrate all 4 conditions
                          - Print phase-by-phase results
                          - Verify 4 hypotheses
                          - Output humanness delta ranking
                          - Synthesize key insights
```

## Key Design Decisions

1. **Isolation**: Each condition gets fresh outer shell instances
   - Prevents state bleed
   - Ensures fair comparison

2. **Dynamic Modulation**: Apply modulation at each step
   - Reflects real-time inner-outer coupling
   - Captures trajectory evolution

3. **7-Dimensional Space**: All modulation keys tracked
   - style_openness, emotion_amplitude, timing_exploration
   - context_depth, emotion_volatility, style_mimicry, emotion_curiosity

4. **Humanness Metric**: Variance + non-zero modulation
   - Higher variance = more human-like behavior
   - Modulation = inner shell influence

5. **Seed Diversity**: Three different random seeds (42, 43, 44)
   - Ensures reproducibility
   - Captures variability in stochastic processes

## Files Created/Modified

### Created
- [x] experiments/sim_inner_outer_modulation.py (805 lines)
- [x] EXPERIMENT_SUMMARY.md (159 lines)
- [x] IMPLEMENTATION_CHECKLIST.md (this file)

### Verified
- [x] No syntax errors (py_compile validation)
- [x] File exists at correct path
- [x] File size consistent (29,727 bytes)

## Next Steps (Optional)

1. Run the experiment: `python3 experiments/sim_inner_outer_modulation.py`
2. Compare results with hypothesis predictions
3. Visualize modulation trajectories (matplotlib)
4. Expand to larger sample sizes (100+ agents)
5. Test parameterization sensitivity

## Notes

- All code follows project conventions
- Compatible with Python 3.10+
- No external dependencies beyond core project
- Ready for immediate execution
- Output includes both statistics and human-readable verdicts
