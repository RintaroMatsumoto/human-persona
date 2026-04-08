---
title: "#02 The Glass-Walled Laboratory"
published: true
tags: ai, metamorphose, oss
series: "Metamorphose Research Diary"
cover_image: https://raw.githubusercontent.com/RintaroMatsumoto/human-persona/main/articles-en/assets/covers/02.png
---

# #02 The Glass-Walled Laboratory
The repository was public from the very first commit.

The Danger Zone reads "This repository is currently public." There was the option to keep it private and nurture it in isolation, but he chose not to.

## The Boundary of Humanlikeness

You can tell immediately when AI output is used as-is. The reply comes back in 30 seconds. The third exchange is just as polite as the first. Every message ends with "Please don't hesitate to reach out." Perfect Japanese. **Too perfect.**

In 2024, Jones & Bergen published a study. When GPT-4.5 was instructed to "adopt a human-like persona," it was identified as human 73% of the time—exceeding the recognition rate of actual human participants.

What this number tells us is that LLMs are sufficiently intelligent. Intelligence is not what separates humans from AI. Response speed, stylistic variation, emotional shifts, contextual references—what linguistics calls **paralinguistic features**. Instant replies, uniform style, no emotional change, context ignored, answers that are too perfect. These are the true boundary.

If so, this "behavior" should be systematically designable. That was our starting point.

## The Limits of Hardcoding

The first approach we considered was naively branching with if statements.

```
if exchanges < 3  → formal
if exchanges < 10 → casual
if "complaint"    → cautious mode
if late_night     → queue for next morning
```

We realized the problem almost immediately. **Every time you change the language, you have to rewrite everything.** In Japanese, "warming up after 3 exchanges" feels natural, but in English, "casual from the first exchange" is the norm. What about Spanish? Arabic?

Recognizing this "doesn't scale" problem early on led directly to the base class design.

---

## Separating Structure from Expression

When you observe human communication, the structure is universal across cultures. Replies take time. Emotions shift throughout a conversation. Previous context is referenced. When a situation can't be handled, it's handed off to a person.

What changes are the parameters. Whether it takes 3 exchanges or 1 to warm up. Whether honorifics are used. How silence is interpreted.

From this observation, the design separates into two layers. The base class defines **structure**, and derived classes define **expression**. Language- and culture-specific logic isn't written in Python. Derivations are created using only JSON configuration files. If you want to change the Japanese "warm up after 3 exchanges" to the English "casual from the first exchange," you just change one line in the config file.

## Five Components

1. **TimingController**. Human response times cluster around the median, with occasional extreme outliers. A uniform distribution can't reproduce this skew, so we adopted a normal distribution. Late-night messages go into a next-morning queue. A reply at 2 AM would feel unnatural.

2. **EmotionStateMachine**. Emotions are formalized into five states: initial politeness, rapport, tension during a problem, relief after resolution, and long-term trust. The fourth state, "relief," was included to capture the distinct atmosphere right after a problem is resolved. Jumping straight from tension back to rapport would feel abruptly relaxed.

3. **StyleVariator**. It selects from five patterns—confirmation, empathy, deferral, redirection, and uncertainty—and decays weights based on recent history to prevent repetition. An AI that declares "It'll be done in 3 days" feels unnatural. "I'd say about 3 days, though it might vary"—that ambiguity is what feels human.

4. **ContextReferencer**. "Regarding what we discussed earlier." Just that one phrase makes it feel like the previous message was actually read. It tracks conversations by topic and determines when a reference is appropriate.

5. **EscalationDetector**. Compensation negotiations and complaints are not things AI should handle. It detects situations that should be handed off to a human.

## No Text Generation

process_message() does not generate response text. It returns only the emotional state, recommended style, recommended delay, and whether escalation is needed. This information is injected into the LLM's system prompt. Crafting the words is the LLM's job.

Why? If text generation is done inside the framework, **it can't keep pace with LLM evolution**. By separating structure from text generation, the framework remains usable simply by swapping out the LLM.

---

## Why Ethics Comes First

docs/ethics.md has been included since the initial commit.

Technology that makes AI behavior more humanlike is inherently dual-use. It can improve the naturalness of customer support, and it can enable fraud. If you publish with incomplete ethical guidelines, misuse in prohibited applications damages the project's credibility. If you're releasing it to the world as OSS, it must be stated explicitly from the start.

Intended legitimate uses, prohibited uses, awareness of dual-use potential—we wrote these from the first line. We didn't want to put it off.

## Beyond the Glass Walls

Write a Zenn article. Document the design philosophy and code overview, written on the day of release, published on the day of release.

An English post on Reddit is also in the works. If we foreground the connection to Turing test research, it might reach international researchers. A draft of an academic paper is also included in the initial commit.

What we learned by building this is that "humanlikeness" can be structured to a surprising degree. And once you structure it, **you realize how unconsciously you use these patterns every day.**
