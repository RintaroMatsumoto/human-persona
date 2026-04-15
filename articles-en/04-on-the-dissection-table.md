---
title: "#04 On the Dissecting Table"
published: true
tags: ai, metamorphose, ablation
series: "Metamorphose Research Diary"
cover_image: https://raw.githubusercontent.com/RintaroMatsumoto/human-persona/main/articles-en/assets/covers/04.png
---

# #04 On the Dissecting Table
The scores are high. **But I have no idea what's actually driving them.**

I built a pipeline that converts AI text to sound more human. It passes through six transformation steps in series.

1. **Filler insertion**
2. **Long sentence splitting**
3. **Short sentence insertion**
4. **Hedge injection**
5. **Cushion injection**
6. **Self-correction injection**

On a 500-sample benchmark: Mean Alignment 0.945, Distribution Alignment 0.864. The numbers came out.

But if I can't tell which of the six are truly contributing and which are noise, I can't make design decisions. Enter Ablation Study—disable one step at a time and observe what happens.

## Remove Fillers and Everything Collapses

The results were clear-cut.

Removing filler insertion causes the score to collapse from 0.945 to 0.622. **34% of the total contribution** is concentrated in this single step. Analyzing the DPO dataset revealed why. Human text has a filler rate of 0.165/sentence. AI has 0.001/sentence. Cohen's d = 1.755. AI almost never uses "Well," "You know," or "Basically,". Humans use them roughly once every six sentences. This gap is the biggest clue for human detection.

However, this is where I made my first mistake. The initial implementation used this regex for filler detection:

```
\blike\b
```

It was counting the "like" in "I like pizza," pushing the filler rate above 0.3. **I nearly drew the completely wrong conclusion that "humans overuse fillers."** In quantitative analysis of natural language, you have to eliminate regex false positives first.

## The Moment Intuition Failed

There was another surprise, in the opposite direction.

Self-correction injection—markers like "wait, I mean..." and "sorry, what I meant was..."—made absolutely no difference whether enabled or disabled. The delta was -0.001. At first I suspected an implementation bug. There was no bug.

The cause was simple.

```
Self-correction occurrence rate: 0.19%/sentence
Statistical weight:              0.097
```

Even in human text, they're barely used. Too rare to stabilize across 500 samples—buried in noise.

My intuition said "self-correction feels human." The actual data showed that, at least in this context, it's hardly ever used. **Intuition vs. data**—data won. I dropped this step from the production integration module. **"Remove it because it doesn't work"** was the most practical outcome of the Ablation Study.

---

## Variance as Humanness

There was one more finding.

Long sentence splitting and short sentence insertion affect different metrics. Long sentence splitting shrinks average word count from 18 to 13 words. Short sentence insertion mixes in brief interjections like "Hmm." and "Got it.," raising the coefficient of variation in sentence length. AI writes uniformly long sentences. Humans mix short interjections with long explanations. This variance is a critical component of humanness, and the combined contribution of these two steps exceeds that of fillers alone.

"Add fillers and it sounds more human" is half right. But **if you ignore variance in sentence length, fillers alone aren't enough**.

## What Are We Actually Measuring?

Looking at these results, one concern nags at me.

This Ablation Study is measured by machine evaluation. If fillers are present, the score goes up as "human-like." If typos are present, the score goes up as "human-like." But that's surface-level feature matching—a separate question from whether a human reader would feel "a human wrote this."

On paper it's 0.945. But Human Eval hasn't been done yet. There is absolutely no guarantee that what a machine judges as "human-like" will feel "human-like" to an actual human.

---

## References

- [Cohen's d (Cohen 1988)](https://en.wikipedia.org/wiki/Effect_size#Cohen%27s_d): Standard measure of effect size in statistics
- [Ablation Study methodology](https://en.wikipedia.org/wiki/Ablation_(artificial_intelligence)): Systematic removal of model components to measure contribution
