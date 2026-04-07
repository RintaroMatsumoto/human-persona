---
title: "#03 A House with Nothing but a Skeleton"
emoji: "🏗️"
type: "idea"
topics: ["AI", "Metamorphosis", "Research Diary", "Turing Test"]
published: false
zenodo_doi: "10.5281/zenodo.19266071"
github_url: "https://github.com/RintaroMatsumoto/human-persona"
---

# #03 A House with Nothing but a Skeleton
I scored the first prototype and got 4.1 out of 10.

I had Claude Sonnet play the role of "an expert who distinguishes humans from AI" and evaluate my output. I call it the LLM Judge. It looks at three metrics.

1. **HL** (Human-Likeness)
2. **SV** (Stylistic Variance — lower is better)
3. **TN** (Timing Naturalness)

HL 4.1, SV 0.64, TN 4.1. **I built it myself, scored it myself, and these were the numbers.**

## You Can't Live in a Blueprint

The cause was immediately obvious. `process_message()` was only returning parameters — it wasn't generating any text. Emotional state, recommended style, response delay — it was producing blueprints, but the words reflecting them were nowhere to be found. It was a skeleton with no house built on it. **4 points was the natural ceiling.**

I integrated the Anthropic API. I passed the emotional state into the system prompt and had it generate text. HL jumped from 4.1 to 6.1. But **TN dropped from 4.1 to 3.5**.

The API response was too fast. A message comes back in 0.3 seconds, and I had a "2-minute delay" configured, but that information wasn't being reflected when passed to the judge. TimingController was just returning values — those values appeared nowhere in the output. A design oversight.

---

## Injecting Cultural Context

There's a parameter in the config file: `context_level: 0.85`. It represents the degree of high-context culture. I reflected this in the system prompt. A rule that says "avoid direct rejection; let the listener infer from context."

"I'm sorry, but that would be difficult" became "Let me think about that for a moment." HL 6.8. That +0.7 was the moment a parameter got mapped to actual linguistic behavior.

But SV stayed stuck at 0.50. Even after inserting fillers ("uhh," "oh,") and increasing structural variation, SV remained 0.50. Even with fillers added, the pattern was "inserting fillers at the same position every time." **It wasn't that randomness was lacking — the structure outside the fillers was identical.**

## The Discovery of Subtraction

The final +0.5 was the most interesting.

I was looking at the test outputs and noticed something. An overwhelming number of replies started with "Thank you for your message." Humans don't express gratitude every single time after the first exchange. LLMs almost always do. In English, "Thanks for reaching out" occupies the same slot.

I added these as banned phrases in the config file.

```json
"banned_phrases": [
  "ご連絡ありがとうございます",  // "Thank you for contacting us"
  "お気軽にお声がけください",    // "Please don't hesitate to reach out"
  "いつでもお気軽に"            // "Feel free anytime"
]
```

In the system prompt, I instructed: "Never use these." That alone gave HL +0.5.

Human-likeness can sometimes be improved more by **"what you stop doing"** than by "what you add." Subtraction, not addition. That was the biggest discovery this time.

---

## HL 7.7

From v1 to v5, I went through 5 versions in a single day.

| Version | Changes | HL | SV | TN |
|---|---|---|---|---|
| v1 | Returns parameters only | 4.1 | 0.64 | 4.1 |
| v2 | Text generation via API | 6.1 | 0.56 | 3.5 |
| v3 | Cultural context reflected | 6.8 | 0.50 | 4.5 |
| v4 | Fillers & structural variation | 7.2 | 0.50 | 4.5 |
| v5 | Banned phrases & tone mirroring | **7.7** | **0.36** | **5.5** |

The numbers improved. But there's something worth pausing to think about here.

Even if the LLM Judge score is 7.7, whether an actual human would feel the same way is a separate question. There's no guarantee that what an LLM judges as "human-like" will feel "human-like" to a human. **I haven't done Human Eval yet.** I'm aware that I'm just chasing numbers.

SV is also at 0.36, just barely missing the target of 0.35. With pipeline-style post-processing, this might be a structural limit.

---

<!-- metadata
event_date: 2026-03-18
notes: HL 4.1→7.7, SV 0.64→0.36, TN 4.1→5.5 confirmed via back_log(old_chat2.txt) and commit history. All 7 commits concentrate