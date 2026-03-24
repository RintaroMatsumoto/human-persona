# DPO Benchmark Evaluation Report

**Date:** 2026-03-24 11:23 UTC
**Model:** local (DPO rejected)
**Sample Size:** 500
**Seed:** 42

---

## Results

| Metric | Raw API | +Pipeline | Human-Like Target | Score (Raw) | Score (+Pipeline) |
|--------|---------|-----------|-------------------|-------------|-------------------|
| Sentence Length CV | 0.4374 | 0.6195 | 0.6340 | 0.028 | 0.928 |
| Hedge Rate | 0.0175 | 0.0871 | 0.0817 | 0.003 | 0.916 |
| Self-Correction Rate | 0.0007 | 0.0450 | 0.0430 | 0.000 | 0.954 |
| Words/Sentence | 18.2546 | 13.5308 | 13.5262 | 0.009 | 0.999 |
| Cushion Rate | 0.0240 | 0.1780 | 0.1578 | 0.038 | 0.855 |
| Filler Rate | 0.0994 | 0.3654 | 0.3340 | 0.000 | 0.865 |

**Overall Score (Raw API):** 0.011
**Overall Score (+Pipeline):** 0.916
**Pipeline Improvement:** +0.904 (+7972.6%)

---

## Score Interpretation

- **1.0** = Matches Human-Like distribution perfectly
- **0.0** = Matches Formal (AI) distribution
- Score = |persona_mean - formal_mean| / |humanlike_mean - formal_mean|

## Weights

| Metric | Weight |
|--------|--------|
| Sentence Length CV | 1.0 |
| Hedge Rate | 1.5 |
| Self-Correction Rate | 1.0 |
| Words/Sentence | 1.0 |
| Cushion Rate | 1.0 |
| Filler Rate | 1.5 |

---

## Improvement Recommendations

- **Cushion Rate**: score=0.855, current=0.1780, target=0.1578
- **Filler Rate**: score=0.865, current=0.3654, target=0.3340
- **Hedge Rate**: score=0.916, current=0.0871, target=0.0817