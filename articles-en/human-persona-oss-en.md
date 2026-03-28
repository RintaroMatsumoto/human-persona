---
title: "Designing and Open-Sourcing a Base Class for AI to Behave Like Humans"
emoji: "🔬"
type: "tech"
topics: ["AI", "research", "machine-learning", "LLM", "open-source"]
published: false
---

## The Trigger: AI-Written Text Was Instantly Recognizable

When I first tried to automate business communication with AI, the prototype output was this:

> Thank you for your message. Regarding this matter, we can deliver within three days. If you could share the detailed requirements, we can start immediately. Should you have any questions, please do not hesitate to let us know.

Perfect Japanese. Flawless in both grammar and honorifics. And yet, **anyone could tell it was written by an AI.**

Why? There are three fatal patterns:

1.  **Replies come in 30 seconds.** A human would need time to think.
2.  **The same tone every time.** The third exchange is as polite as the first.
3.  **It always ends with "please do not hesitate."** A human wouldn't say it so readily every single time.

In 2024, a paper by Jones & Bergen published in PNAS backed up this intuition. When GPT-4.5 was instructed to adopt a "human-like persona," it was perceived as human 73% of the time—surpassing the recognition rate of actual human participants.

In other words, LLMs are smart enough. The reason they get caught is **behavior, not intelligence**. Reply speed, stylistic variation, emotional shifts, referencing context—what linguistics calls "paralinguistic features."

So, can we systematically design this "behavior"? That's what I started building.

## The Starting Point: Imagining the Limits of Hardcoding

My first thought was a naive approach using `if` statements.

```python
if exchange_count < 3:
    tone = "formal"
elif exchange_count < 10:
    tone = "casual"
if "complaint" in message:
    tone = "careful"
if time.hour >= 23:
    delay = 3600  # Reply the next morning
```

I realized immediately after starting to write this. **You'd have to rewrite everything for each language.** In Japanese, "warming up after 3 exchanges" feels natural, but in English, "casual from the 1st exchange" might be normal. What about Spanish? Arabic?

Recognizing this "doesn't scale" problem from the start led to the base class design.

## Why a "Base Class"?

Observing human communication reveals that the **structure** is common across cultures:

*   Replies take time (instant replies are unnatural).
*   Emotions shift through a conversation (initial tension → gradual warming up).
*   Previous context is referenced ("Regarding the earlier matter...").
*   Situations that can't be handled are escalated to a person (complaints, legal risks).

What changes are the **parameters**. Is it 3 exchanges or 1 to warm up? Whether to use honorifics. How to interpret silence.

That's why I designed it using an OOP inheritance model:

```
HumanPersonaBase (Base Class) ← Defines structure
│
├── JapaneseBusinessPersona      ← ja.json (warms up after 3 exchanges, uses honorifics)
├── EnglishCustomerSupportPersona ← en.json (can be casual from 1st exchange)
└── SpanishSalesPersona           ← es.json (passionate, more exclamation marks)
```

Language/culture-specific logic is **not written in Python at all**. Derived personas can be created using only JSON configuration files. The hardcoding problem was solved with structure.

## The 4 Components and Their Design Decisions

### 1. TimingController — Why a Normal Distribution?

Observing human reply times shows they **cluster around a median, with occasional extreme outliers** (a phone call, stepped away, etc.). A uniform distribution (`random.uniform`) makes "every delay equally probable" and can't reproduce this pattern. Hence, the normal distribution.

```python
def calculate_delay(self, platform: Platform) -> float:
    profile = self.profiles.get(platform)
    midpoint = (profile.min_seconds + profile.max_seconds) / 2
    spread = (profile.max_seconds - profile.min_seconds) / 4
    delay = random.gauss(midpoint, spread)
    return max(profile.min_seconds, min(delay, profile.max_seconds))
```

Another point. If a reply comes at 2 AM, you'd wonder, "Is this person awake?" I added a `night_queue` flag to queue messages received outside business hours for the next morning.

### 2. EmotionStateMachine — The Struggle of Designing State Transitions

How to model emotional state transitions was the hardest part.

I settled on 5 states:

```python
class EmotionState(Enum):
    FORMAL   = "formal"     # First contact: Polite, cautious
    WARMING  = "warming"    # Warming up
    TENSE    = "tense"      # Problem occurred
    RELIEVED = "relieved"   # After resolution
    TRUSTED  = "trusted"    # Long-term relationship
```

The fifth state, RELIEVED, was added to express the unique atmosphere "right after a problem is solved." A sense of relief, but with a bit of lingering tension. Without it, a direct TENSE→WARMING transition feels like "suddenly becoming friendly."

Transition triggers are defined not by string matching but by **Callable**. This ensures at the code level that "warming up after 3 exchanges" or "becoming tense when a problem occurs" is guaranteed.

```python
DEFAULT_TRANSITIONS = [
    Transition(FORMAL, WARMING,
               lambda sm: sm.exchange_count >= 3,
               "Warms up after 3 exchanges"),
    Transition(WARMING, TENSE,
               lambda sm: sm._last_event == "problem_detected",
               "Becomes tense upon problem detection"),
]
```

The "3" here is an observed value from Japanese business communication. For English, "1" might be fine. That's why it's designed to be overridable in JSON.

### 3. StyleVariator — Saying the Same Thing Differently Each Time

It randomly selects from 5 patterns (Confirming, Empathetic, Deferring, Redirecting, Uncertain). However, the weight of recently used patterns is decayed to prevent consecutive use of the same pattern.

There's also probabilistic insertion of uncertain expressions. An AI that definitively states "It will be done in 3 days" feels unnatural. "It should take about 3 days, but it might vary slightly"—this ambiguity is human-like.

### 4. ContextReferencer — Recreating the "Sense of Being Read"

"Regarding the earlier matter about ○○." Just this one phrase makes you feel, "This person is actually reading the previous messages." It tracks conversation topics and passes reference information to the LLM.

## A Key Design Decision: It Doesn't Generate Text

`process_message()` **does not generate text**. It only returns "current emotional state," "recommended response style," "recommended delay time," and "whether escalation is needed."

```python
response = persona.process_message("Can you move up the deadline?")
context = persona.get_system_prompt_context()
# → {"emotion_state": "warming", "tone": {"formality": 0.6}, ...}
```

This information is injected into the LLM's system prompt. Text generation is left to the LLM.

Why? If text generation is done inside the framework, it can't keep up with LLM evolution. Whether GPT-4 becomes GPT-5 or Claude 3 becomes Claude 4, the structure of "emotional transitions" or "response timing" doesn't change. By separating structure from text generation, the framework remains usable simply by swapping out the LLM.

## Summary

The reason AI gets caught isn't "what it says" but "how it says it." Reply speed, stylistic variation, emotional shifts, context referencing—I designed these as a base class and open-sourced it.

What I learned from building this is that "human-like behavior" is surprisingly structurable. And once you structure it, **you realize how unconsciously you use these patterns yourself in daily life.**

Repository: [github.com/RintaroMatsumoto/human-persona](https://github.com/RintaroMatsumoto/human-persona)

---

> 📄 **The research for this article is formally published as a preprint**
> **HumanPersonaBase: A Language-Agnostic Framework for Human-Like AI Communication**
> DOI: [10.5281/zenodo.19273577](https://doi.org/10.5281/zenodo.19273577)
