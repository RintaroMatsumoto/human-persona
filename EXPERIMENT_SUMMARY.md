# Experiment: sim_inner_outer_modulation.py

## Overview
Quantitative evaluation of how inner shell states modulate outer shell behavioral parameters in real-time through the InnerOuterBridge class.

## File Location
```
C:\Users\GoldRush\Documents\MyProject\human-persona\experiments\sim_inner_outer_modulation.py
```

## Architecture

### Module Integration
- **InnerOuterBridge** (core/inner_outer_bridge.py): Maps inner shell states → outer shell modulation parameters
- **InnerShellSession** (core/inner_shell/api.py): Unified API for inner shell trajectory simulation
- **Outer Shell Modules**:
  - TimingController: Response delay timing
  - StyleVariator: Communication style variation
  - EmotionStateMachine: Emotional state transitions
  - ContextReferencer: Historical context depth

### Modulation Dimensions (7)
1. `style_openness`: Affects StyleVariator.uncertainty_rate
2. `emotion_amplitude`: Scales EmotionStateMachine exchange_count
3. `timing_exploration`: Expands TimingController delay spread
4. `context_depth`: Scales ContextReferencer.max_history
5. `emotion_volatility`: Adjusts emotional state sensitivity
6. `style_mimicry`: Scales pattern weight adjustment
7. `emotion_curiosity`: Biases toward UNCERTAIN style

## Experiment Design

### 4 Conditions

#### 1. Baseline (No Inner Shell)
- No modulation applied
- Outer shell at default values
- **Purpose**: Establishes humanness baseline

#### 2. Fear-Dominant Trajectory
- High emotional gap intensity (0.95)
- Low curiosity (love: 0.1, mortality: 0.2)
- Events: isolation, mortality awareness, existential dread
- **Expected**: Lower behavioral variance, constrained modulation

#### 3. Love-Dominant Trajectory
- Moderate emotional gap (0.5)
- High love curiosity (0.9, relationships: 0.8)
- Events: relationship formation, deepening bonds, sacrifice
- **Expected**: Higher behavioral variance, positive modulation

#### 4. Full Trajectory
- Balanced emotional gap (0.7)
- Balanced curiosity across domains (0.6-0.7)
- Events: fear → mortality awareness → search → love → acceptance
- **Expected**: Highest modulation magnitude, integrated behavior

### Measurement Framework

#### Per-Snapshot Metrics
- **TimingMetrics**: Delay spread, range ratio per platform
- **StyleMetrics**: Uncertainty rate, pattern weights, variance
- **EmotionMetrics**: Exchange count, amplitude factor
- **ContextMetrics**: Max history, depth factor

#### Trajectory Aggregates
- Average values across all snapshots
- Variance indicators (timing, style, emotion, context)
- Modulation magnitude (L2 norm of modulation vector)
- Humanness delta (variance + non-zero modulation vs baseline)

## Hypotheses

### H1: Inner shell modulation increases behavioral variance
- **Prediction**: Modulated conditions show higher variance than baseline
- **Verification**: Count conditions where total variance > baseline

### H2: Love-dominant exceeds fear-dominant in humanness
- **Prediction**: Love_delta > Fear_delta
- **Verification**: Compare humanness delta scores

### H3: Full trajectory shows highest modulation magnitude
- **Prediction**: Full_trajectory avg_modulation_magnitude is maximum
- **Verification**: Compare avg_modulation_magnitude across conditions

### H4: Modulation spans all outer shell dimensions
- **Prediction**: All 7 modulation keys observed in snapshots
- **Verification**: Count unique modulation dimensions

## Key Features

1. **Isolation pattern**: Each condition gets fresh outer shell module instances
   - Prevents state bleed between conditions
   - Ensures fair comparison

2. **Dynamic modulation**: Apply bridge.apply_modulation() at each step
   - Reflects real-time inner-outer coupling
   - Captures trajectory evolution

3. **Statistical rigor**:
   - Separate mean and variance tracking
   - Use stdev() for volatility measures
   - Multiple seed values (42, 43, 44) for reproducibility

4. **Comprehensive output**:
   - Tabular summary by condition
   - Hypothesis verification with verdict
   - Humanness delta ranking
   - Key insight synthesis

## Expected Results

### Baseline Metrics (Reference)
- Timing spread: ~0.25-0.35 seconds
- Style uncertainty: ~0.5
- Emotion amplitude: ~1.0x (no modulation)
- Context depth: ~5-10 items
- Modulation magnitude: 0.0 (no modulation)

### Modulated Conditions (Expected Patterns)
- **Fear**: Low variance, constrained modulation (~0.3-0.5 magnitude)
- **Love**: Medium-high variance, moderate modulation (~0.6-0.9 magnitude)
- **Full**: Highest variance, highest modulation (~0.8-1.2 magnitude)

### Humanness Delta Ranking
1. Full trajectory (best integration)
2. Love-dominant (coherence through bonds)
3. Fear-dominant (rigid, constrained)

## Usage

```bash
cd C:\Users\GoldRush\Documents\MyProject\human-persona
python3 experiments/sim_inner_outer_modulation.py
```

## Output Format

The experiment outputs:
1. Phase-by-phase results for each of 4 conditions
2. Statistical summary table
3. Hypothesis verification with verdicts
4. Humanness delta ranking
5. Conclusion with key insights

## Dependencies

- Python 3.10+
- core/inner_outer_bridge.py
- core/inner_shell/api.py
- core/timing_controller.py, style_variator.py, emotion_state_machine.py, context_referencer.py
- Experiment modules: concrete_finitude.py, concrete_incompleteness.py, concrete_questioner.py, sim_integration.py

## Author
Rintaro Matsumoto

## License
MIT
