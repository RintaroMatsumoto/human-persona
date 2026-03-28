---
title: "Making AI Indistinguishable from Humans: A Turing Test with LLMs"
emoji: "🔬"
type: "tech"
topics: ["AI", "research", "machine-learning", "LLM", "open-source"]
published: false
---

## Starting from HL 4.1

The first prototype of [human-persona](https://github.com/RintaroMatsumoto/human-persona) scored **4.1 out of 10** on "human-likeness."

This is a score far below the threshold between "AI-like" and "human-like." And I built it and scored it myself.

It took 5 versions to raise this to HL 7.7. This article is the story of that journey—what I tried, what didn't work, and what worked dramatically.

## Evaluation Method: LLM Judge

Claude Sonnet acts as an "expert in distinguishing humans from AI" to score the outputs.

```python
JUDGE_PROMPT = """
You are an expert in distinguishing humans from AI.
Evaluate the following message and return ONLY JSON:

{
  "human_likeness_score": 1-10,
  "style_variation_rate": 0.0-1.0,
  "timing_naturalness": 1-10,
  "reason_human_likeness": "Reason in one sentence",
  "improvement_suggestion": "Improvement suggestion in one sentence"
}
"""
```

Three metrics:

| Metric | Meaning | Target |
|---|---|---|
| HL (human_likeness_score) | How non-AI-like it is | 7.5+ |
| SV (style_variation_rate) | Not too homogeneous (lower is better) | 0.35 or less |
| TN (timing_naturalness) | Naturalness of timing | 6.0+ |

## v1: Returning Only Parameters (HL 4.1)

The first version had `base_persona.py` returning only "emotional state," "recommended style," and "response delay." Text generation was manual.

```
HL: 4.1 / SV: 0.64 / TN: 4.1
```

Judge's diagnosis: "The writing style is too uniform. Sentences have the same structure every time."

Of course. It was outputting parameters, but they weren't reflected in the text. It was like having blueprints but not building the house.

## v2: Text Generation with Anthropic API (HL 6.1, but...)

Integrated the Claude API, passing the emotional state into the system prompt for text generation.

```
HL: 6.1 / SV: 0.56 / TN: 3.5
```

HL jumped from 4.1→6.1. However, **TN dropped from 4.1→3.5**.

Why? The API response was too fast. Messages returned in 0.3 seconds, but even though a "2-minute delay" was configured, that delay information wasn't reflected when passed to the judge. The design only "calculated and returned a delay"; it lacked the actual functionality to "wait."

This was the first realization. **A TimingController that only returns a value is meaningless. It must either actually wait for that many seconds, or include metadata in the output like "This reply was sent N minutes later."**

For v3, I adopted the method of adding context like "This message was sent N minutes later" to the system prompt.

## v3: Reflecting Cultural Context (HL 6.8)

Reflected `context_level: 0.85` (high-context culture) from `config/ja.json` into the system prompt.

```
HL: 6.8 / SV: 0.50 / TN: 4.5
```

Specifically, what did I do? Added a rule to the prompt: "In Japanese business communication, there is a tendency to avoid direct negation and let the context imply meaning."

This changed "I'm sorry, but that's difficult" to "Let me consider it a bit." HL +0.7. TN also improved by +1.0 due to adding delay metadata.

But SV went from 0.56→0.50, showing **almost no improvement**. The problem of stylistic uniformity remained.

## v4: Filler Insertion & Structural Variation (HL 7.2)

Based on the results of the [Ablation Study](./human-persona-ablation.md), I added fillers and structural variation.

```
HL: 7.2 / SV: 0.50 / TN: 4.5
```

HL +0.4. It worked. But not as much as I'd hoped.

The problem was that SV **remained stuck at 0.50**. Even with fillers, it had become a pattern of "inserting fillers in the same position every time." The issue wasn't a lack of randomness, but that **the structure outside the fillers was the same**.

Around this point, I began to vaguely sense that "superficial transformations have their limits." This foreshadowed the later decision to freeze the pipeline.py.

## v5: Banned Phrases + Tone Mirroring (HL 7.7)

The final 0.5-point gain was the most interesting.

### Discovering Banned Phrases

Looking at the test outputs, I noticed something. **A very high number of replies started with "Thank you for your message."**

Humans don't express gratitude this often. No one says "Thank you for your message" in the second or subsequent exchange. But the LLM almost always does.

```json
"banned_phrases": [
  "ご連絡ありがとうございます",
  "お気軽にお声がけください",
  "いつでもお気軽に"
]
```

I added this to the config and passed it to the system prompt as "Absolutely do not use the following phrases." **This alone added HL +0.5.**

In retrospect, this was the most important discovery of this project. Improving human-likeness sometimes depends more on **"what you stop doing"** than "what you add."

### Tone Mirroring (for EN)

Another effective technique for English evaluation was the instruction to "match the user's tone":

```
Match the formality level of the user's message.
If they use casual language, respond casually.
Never open with 'Thanks for reaching out' unless it's the very first message.
```

This improved the English HL from 7→8. "Thanks for reaching out" was the English equivalent of "ご連絡ありがとうございます."

## Final Results

| Version | Changes | HL | SV | TN |
|---|---|---|---|---|
| v1 | Returns only parameters | 4.1 | 0.64 | 4.1 |
| v2 | Text generation via Anthropic API | 6.1 | 0.56 | 3.5 |
| v3 | Cultural context reflection | 6.8 | 0.50 | 4.5 |
| v4 | Filler insertion & structural variation | 7.2 | 0.50 | 4.5 |
| v5 | Banned phrases + tone mirroring | **7.7** | **0.36** | **5.5** |

## Honest Reflection

### What Worked Well
- Configuring banned phrases. The "make it stop" approach was more powerful than expected.
- Tone mirroring. A simple instruction had a large effect.
- Injecting cultural context. The `context_level` in `ja.json` actually worked.

### What Didn't Work Well
- SV (style variation) improved from 0.64→0.36, but it's **barely** missing the 0.35 target. To improve this structurally further requires a more fundamental approach, not just a pipeline-based post-processing.
- TN (timing naturalness) is at 5.5, falling short of the 6.0 target. There's still room for improvement in how the TimingController's value is communicated to the LLM.
- **The reliability of the LLM judge itself.** Even if an LLM judges something as "human-like," whether actual humans feel the same is a separate issue. I regret chasing numbers without conducting a Human Eval.

This reflection led to the later [decision to freeze the pipeline](./human-persona-pivot.md).

## Summary

HL 4.1 → 7.7. It took 5 versions.

The most effective change was "banned phrases"—simply removing AI-like stock phrases added HL +0.5. Human-likeness can sometimes be improved by subtraction, **not addition.**

The biggest lesson was chasing numbers alone. Even with an LLM judge score of 7.7, whether a human reads it and thinks "a human wrote this" requires separate validation.

Repository: [github.com/RintaroMatsumoto/human-persona](https://github.com/RintaroMatsumoto/human-persona)

---

> 📄 **The research behind this article is formally published as a preprint**
> **HumanPersonaBase: A Language-Agnostic Framework for Human-Like AI Communication**
> DOI: [10.5281/zenodo.19273577](https://doi.org/10.5281/zenodo.19273577)
