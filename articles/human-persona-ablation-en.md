---
title: "Dissecting the Humanization Pipeline for AI Text: A 6-Step Ablation Study"
emoji: "🔬"
type: "tech"
topics: ["AI", "research", "machine-learning", "LLM", "open-source"]
published: false
---

## The scores are good. But what's actually working?

In the previous article, I built a pipeline to transform AI text to feel more human-like and reported benchmark results of Mean Alignment 0.945 and Distribution Alignment 0.864.

Not bad. But I had my own doubts. **Among the six transformation steps, which ones are truly effective, and which are just noise?** High scores alone don't inform design decisions.

So I conducted an Ablation Study (removal experiment). I disabled one step at a time and observed what happened.

To cut to the chase, there were **two surprises and one failure**.

## Method

Using a held-out test set of 500 samples (80/20 split), I re-evaluated the pipeline by disabling each of the 6 steps one at a time.

| Metric | Meaning |
|---|---|
| **Mean Alignment** | How close the average feature vector of the pipeline output is to human text |
| **Distribution Alignment** | Overall distribution similarity based on Wasserstein distance |

## Results: The Most Critical Step and the Completely Useless One

| Disabled Step | Mean Align. | Dist. Align. | Mean Drop | Dist. Drop |
|---|:---:|:---:|:---:|:---:|
| None (Full Pipeline) | 0.945 | 0.864 | — | — |
| **Filler Insertion** | 0.622 | 0.569 | **-0.323** | **-0.296** |
| Long Sentence Splitting | 0.751 | 0.720 | -0.194 | -0.144 |
| Short Sentence Insertion (interjection) | 0.763 | 0.742 | -0.182 | -0.122 |
| Hedge Injection | 0.808 | 0.740 | -0.137 | -0.125 |
| Cushion Injection | 0.851 | 0.779 | -0.094 | -0.085 |
| **Self-Correction Injection** | **0.944** | **0.866** | **-0.001** | **+0.001** |
| No Pipeline | 0.003 | 0.000 | -0.942 | -0.864 |

The moment I saw this table, two things shocked me.

## Surprise 1: Removing Fillers Alone Causes Collapse

Removing filler insertion causes the score to plummet from 0.945 to 0.622. **34% of the total contribution is concentrated in this single step.**

Analyzing the DPO dataset revealed why:

```
Human Text: Filler Rate 0.165 / sentence
AI Text:   Filler Rate 0.001 / sentence
Cohen's d = 1.755 (very large effect size)
```

AI almost never uses "Well,", "You know,", "Basically,". Humans use them about once every six sentences. This difference is the **biggest clue for human detection**.

However, this is where my first failure happened.

The initial implementation used `\blike\b` for filler detection. It counted the "like" in "I like pizza," pushing the filler rate above 0.3. I almost drew the completely wrong conclusion that "humans use too many fillers."

The corrected version switched to position-dependent detection:

```python
# NG: Full of false positives
FILLER_PATTERNS = [r"\blike\b", r"\bso\b", r"\bwell\b"]

# OK: Detects only filler usage at sentence start + comma
FILLER_START_PATTERNS = [r"^(?:well|so|like)\s*,"]
FILLER_ALWAYS = [r"\byou know\b", r"\bi mean\b", r"\bbasically\b"]
```

I wasted time on unnecessary analysis until I noticed this false positive. Lesson: **In quantitative analysis of natural language, eliminate regex false positives first.**

## Surprise 2: Self-Correction Contributes Absolutely Nothing

Self-correction markers like "wait, I mean..." or "sorry, what I meant was...". Enabling or disabling this step made no difference to the score (-0.001).

At first, I suspected a bug in the implementation. I checked, but there was no bug.

The reason was simple. **They are hardly used in human text either** (0.19%/sentence). They are too rare, with a statistical weight of only 0.097. With 500 samples, the result isn't stable, and the CI is wide [0.001, 0.004], buried in noise.

My intuition was, "Self-correction feels human, right?" Looking at the actual data, at least in the context of business communication, it's almost never used. Data beat intuition.

I omitted this step in the final integrated module. The decision to "remove it because it doesn't work" was the most practical outcome of the Ablation Study.

## Another Discovery: Sentence Structure Transformations Work in Combination

Long sentence splitting (-0.194) and short sentence insertion (-0.182) **affect different metrics**:

| Step | Primarily Affects | Mechanism |
|---|---|---|
| Long Sentence Splitting | Words/Sentence | Reduces from 18→13 words |
| Short Sentence Insertion | Sentence Length CV | Increases coefficient of variation with "Hmm.", "Got it." |

AI writes uniformly long sentences. Humans mix short acknowledgments with long explanations. This **variation** is a key component of human-like writing, and the combined contribution of these two steps (-0.376) exceeds that of fillers (-0.323).

In other words, "adding fillers makes it human-like" is half true, but **if you ignore sentence length variation, fillers alone aren't enough**.

## Basis for Weights: Based on Cohen's d, Not Arbitrary

The weight for each metric is automatically calculated from "how well it discriminates between human and AI text" (Cohen's d):

| Metric | Cohen's d | Weight |
|---|:---:|:---:|
| Filler Rate | 1.755 | 1.88 |
| Words/Sentence | 1.356 | 1.45 |
| Sentence Length CV | 1.086 | 1.16 |
| Hedge Rate | 0.818 | 0.87 |
| Cushion Rate | 0.506 | 0.54 |
| Self-Correction Rate | 0.091 | 0.10 |

d > 0.8 indicates a "large effect". Filler rate, words/sentence, and sentence length CV are the main battlegrounds for human/AI discrimination.

## Limitations of This Experiment (To Be Honest)

### 1. The Wall of Fixed-Probability Injection

The current pipeline injects all fillers and hedges at a fixed probability. Humans don't do that. More fillers in casual topics, fewer in technical ones. This failure to replicate **context dependence** is the root cause of two metrics failing the KS test.

### 2. The Limits of Automated Evaluation

This is the most important limitation, which I realized later.

This Ablation Study is measured using the DPO benchmark (automated evaluation). If there are fillers, it scores as "human-like"; if there are typos, it scores as "human-like". But that's **superficial feature matching**, which is a separate issue from whether a human reading it would feel "this was written by a human."

In fact, subsequent verification revealed that **design decisions are precarious without Human Eval (human visual assessment)**. I detail this in the [next article](./human-persona-pivot.md).

## Summary

| Rank | Step | Contribution | In a Nutshell |
|:---:|---|:---:|---|
| 1 | Filler Insertion | -0.323 | **Most critical. But watch for false positives.** |
| 2 | Long Sentence Splitting | -0.194 | Brings words/sentence to human level |
| 3 | Short Sentence Insertion | -0.182 | Brings variation to human level |
| 4 | Hedge Injection | -0.137 | Adds ambiguity |
| 5 | Cushion Injection | -0.094 | "Sure,", "Of course," |
| 6 | Self-Correction Injection | -0.001 | **Unnecessary. Contrary to intuition, zero contribution.** |

All data and code are open.

**→ [github.com/RintaroMatsumoto/human-persona](https://github.com/RintaroMatsumoto/human-persona)**

---

> 📄 **The research in this article is formally published as a preprint**
> **HumanPersonaBase: A Language-Agnostic Framework for Human-Like AI Communication**
> DOI: [10.5281/zenodo.19273577](https://doi.org/10.5281/zenodo.19273577)
