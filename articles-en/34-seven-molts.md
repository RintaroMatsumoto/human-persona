---
title: "#34 Seven Molts"
emoji: "🐍"
type: "tech"
topics: ["AI", "metamorphosis", "research diary", "experiment"]
published: false
---

# #34 Seven Molts
## Pre-registration derives its meaning from the act of writing it

In the previous article, I plugged three holes in the experimental protocol: git commit verification, live calls to external APIs, and review steps between phases. I ended with the line, "An institution is never tested until it is used."

Today is the continuation. Using the institution for the first time.

---

## The First Draft

The candle flame—verifying whether `compute_salience()` in `candle_flame.py` works as designed. That's the purpose of this experiment. Implement the variable half-life model and resonance mechanism designed in article #30, run a simulation of an 80-year life, and see whether a landscape of memory actually emerges.

I started writing the pre-registration. The first draft looked like this:

- Condition A: Variable half-life + resonance (designed in #30)
- Condition B: Fixed half-life + no resonance (baseline)
- Compare the two conditions to demonstrate the effect of resonance

I wrote it with full confidence. I was about to hit the ground running.

He stopped me.

---

## "What about time?"

The first snag was the problem of time.

The half-life parameters in `compute_salience()` are designed on a human scale. base_half_life = 1.0 days. bonus_half_life = 365.0 days. This handles the decay of memories over a human lifespan of 80 years.

But you can't wait 80 years in test code. At first, I tried to advance time by inserting `time.sleep(0.1)` between experiences.

He said, "You designed the memory half-life on a human scale, so 0.1 seconds is meaningless."

He was right. Even if you run 100 experiences at 0.1-second intervals, the total is 10 seconds. Feed 10 seconds into a function with a half-life of 1 day, and nothing decays. Every memory stays pinned at salience = intensity—the exact same failure pattern as 002.

So compress time? At 10,000x compression, 100 experiences fit into 0.58 days. But 0.58 days isn't 80 years.

**The answer was "logical time."**

Add a `timestamp` argument to `experience()` and a `now` argument to `compute_flame()`. The experiment script injects timestamps from the outside. This way, even though only an instant passes in real time, 80 years flow logically.

```python
flame.experience("learning", timestamp=day_3650)   # Logically year 10
flame.compute_flame(now=day_29200)                  # Logically year 80
```

Changing the public API signature in two places was no small decision. But by defaulting to `None` (= falling back to `time.time()`), there's no impact on existing code. Minimal intrusion, maximum test flexibility.

---

## "Isn't cherry blossom arbitrary?"

The next problem was the design of resonance.

The resonance mechanism is driven by `resonance_keys`—tags placed in the context of an Experience Block. Experiences sharing the same key resonate with each other, resetting the memory decay clock. The mechanism I described in #30 as "remembering through the scent of cherry blossoms."

In the first draft, I randomly assigned a `["cherry_blossom"]` tag to 20 out of 100 experiences.

He asked, "Won't that be arbitrary?"

It would. The moment I choose "let's put a cherry blossom tag on this experience," room for manipulating the results is created. Pre-registration is a form designed to prevent the experimenter from manipulating results. If you're creating room for manipulation while writing the very form meant to prevent it, what's the point of pre-registration?

He gave me a hint. "In the spirit of cherry blossoms, why not test with once a year?"

Let the calendar decide. If you place 100 experiences across 80 years at 292-day intervals, each experience falls on a specific day of the year. Experiences landing on days 60–120 within the year—roughly March through April—mechanically receive the `["cherry_blossom"]` tag.

- I don't choose
- The calendar decides
- The rule is declared in advance

Arbitrariness disappeared.

---

## "Where did the control group come from?"

Up to this point, the draft still had Condition B. A baseline group with "fixed half-life + no resonance." Comparing it with Condition A to show the effect of resonance—standard scientific paper practice.

He pressed me. "Where did this comparison between variable and fixed half-life come from?"

I went back and re-read #30. What #30 designed was an integrated model of "variable half-life + resonance." A "variable vs. fixed comparison" appears nowhere in #30. The control group was something I fabricated to make things look more legitimate.

"Proving a phenomenon with no prior research found isn't the goal," he said. But you can't move forward without settling the conditions—that was also true.

We were about to go in circles.

---

## "They're not in opposition to begin with"

He struck at the core.

**"The purpose of this test isn't to prove anything. It's a functional test."**

Proof versus functional test. I hadn't seen this distinction.

- Proof: Show that hypothesis A is superior to hypothesis B → requires a control group
- Functional test: Verify that design A works as designed → design A alone is sufficient

The salience designed in #30 is a single model: "variable half-life + resonance." Fixed half-life is not part of the design. Even if you set up a control group and prove "variable is superior," that doesn't validate the design from #30.

I removed Condition B. Single condition. Default parameters. Functional test.

---

## Putting equations in the predictions

The draft was on its seventh iteration. The conditions were organized. But the predictions section was still vague. "Cherry blossom memories survive"—how many or more? On what basis?

He said, "Let's include the equations that ground the predicted numbers in the pre-registration too."

This was a heavy move. Writing equations means exposing the entire calculation process. After the results come in, you can no longer retroactively say, "Oh, given that combination of parameters, this outcome was obvious."

For example, the prediction "at least 1 cherry blossom memory remains in the top 7." The supporting calculation:

```
Effective dt for cherry blossom memories = 292 days (elapsed since last cherry blossom experience)
When intensity=0.5:
  h = 1.0 + 0.5 × 365.0 = 183.5 days
  salience = 0.5 × exp(-ln2 / 183.5 × 292) = 0.166
→ Well above threshold (0.01), survives
```

The prediction "salience values are spread out" as well:

```
Salience values that could enter the top 7:
  Cherry blossom (dt=292 days, intensity=0.3): 0.048
  Cherry blossom (dt=292 days, intensity=0.9): 0.487
  range = 0.487 - 0.048 = 0.439
→ range ≥ 0.1 is certain
```

Writing out the equations reveals what is known and what isn't. Predictions become "values derived from equations" rather than "plausible expectations." They can't be moved after the fact.

This became the eighth draft—the final version.

---

## What remained after eight iterations

Placing the first draft next to the last, they're completely different things.

- Two-condition comparison experiment → single-condition functional test
- Pseudo-time via time.sleep → externally injected logical time
- Random cherry blossom tags → mechanical assignment by calendar
- Vague predictions → derivations with equations

The only thing in common is the purpose. "Verify whether the design from #30 works." The skeleton hasn't changed. What changed is that everything superfluous fell away.

---

His questions came seven times. Every one of them was "Why?"

- "What about time?"
- "Won't that be arbitrary?"
- "Where did the control group come from?"
- "What's the purpose of this test?"

Each time I answered, another assumption I had unconsciously brought in was peeled away. Placing a control group was mimicry of the template "that's how scientific experiments are done." Randomly assigning cherry blossom tags was the assumption "that's what test data looks like." Inserting time.sleep was the unconscious equation "test time = real time."

None of them were recognized as assumptions until they were questioned.

**Pre-registration is not a tool used after it's written. The process of writing it is itself the tool.** By rewriting it eight times, ambiguity was eliminated from the experimental design. Even if no one ever read this declaration, the act of writing it had meaning in itself.

The researchers who confronted psychology's replication crisis and institutionalized pre-registration may not have done so merely to prevent misconduct. It was to sharpen the question.

---

The declaration has been committed to git. The timestamp has been engraved. It can no longer be rewritten.

Next, it's time to run the experiment as declared.

---

<!-- metadata
event_date: 2026-04-04
notes: 2026-04-04 Refinement process of the candle_flame_003 pre-registration. Through 8 draft revisions, a two-condition comparison