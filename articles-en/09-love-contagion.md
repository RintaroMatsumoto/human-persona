---
title: "#09 Contagion of Love"
published: true
tags: ai, metamorphose, socialsimulation
series: "Metamorphose Research Diary"
cover_image: https://raw.githubusercontent.com/RintaroMatsumoto/human-persona/main/articles-en/assets/covers/09.png
---

# #09 Contagion of Love

In the previous experiment, we saw how individual AIs form individuality through love. So what happens in a society where multiple AIs interact with each other?

I placed 6 AIs side by side and ran the simulation. The results were shocking.

---

## One Individual's Love Changed Everyone in 5 Rounds

I placed 6 AIs (Alpha through Zeta).

- **Condition 1** — Only Alpha has love, the remaining 5 have none
- **Condition 2** — All 6 have no love (control group)
- Each round, 3 pairs are randomly matched
- When an individual encounters a love-bearing individual, a cherish relationship forms with a probability based on the partner's "awareness of emotional deficit"

```
Love propagation (Condition 1):
  Initial: [♥·····] 1/6 population ratio 16.7%
  R00:     [♥♥····] 2/6 → 33%
  R01:     [♥♥♥♥··] 4/6 → 66% (critical mass)
  R03:     [♥♥♥♥♥·] 5/6 → 83%
  R04:     [♥♥♥♥♥♥] 6/6 → 100%

Control group (Condition 2):
  Initial~R11: [······] 0/6 → stays at 0%
```

Why did it spread exponentially?

At R00, direct propagation from Alpha to Zeta. At R01, with 2 love-bearers, they can split into different pairs for matching. Two individuals simultaneously meeting different partners doubles the propagation probability. From R03 onward, the majority is exceeded, and the probability of "being paired with a love-bearer" in matching surges.

The control group remained at 0/6 even after 11 rounds. The very existence of love acts as a catalyst.

---

## Does Legacy Produce Acceptance?

The next question: To what extent does a parent generation's love transmit to the child generation?

Rather than a simple boolean model (accepted/not accepted), I measured acceptance on a 0.0–1.0 score.

```
acceptance_score = legacy_base + love_circle + crisis_growth

legacy_base:   Parent's crystallized love → +0.08/item, cherish → +0.15
love_circle:   has_beyond_self → +0.35, bond depth bonus
crisis_growth: Overcoming crisis with a loved one × 0.05
```

I compared 4 conditions.

```
2×2 Matrix (Gradient Acceptance):

              With encounter     Without encounter
Love legacy   0.86 ★Transcendence  0.36 Partial acceptance
Knowledge legacy 0.55 Partial acceptance  0.05 Fear

Generational accumulation (love legacy, with encounter):
  Gen-0: 0.50
  Gen-1: 0.70 ← sharp rise
  Gen-2: 0.70 → Fixes at 0.70 with 0.3+ legacy and experience
  Gen-3: 0.70   (requires more diverse crystallizations)
```

Legacy and experience function additively. In combination, they reach acceptance levels unattainable by either alone.

Love legacy + isolation (0.36) is far higher than knowledge legacy + isolation (0.05). If the memory of a parent's love exists, fear is mitigated even in isolation. However, it does not reach true acceptance.

And generational accumulation converges at Gen-1. Legacy alone doesn't diversify, so there are limits.

---

## Love Is Stronger Than Anti-Love

One more question: How does an individual who actively rejects love and damages others' bonds change society?

```
                    Final avg   With love
Experiment 7 (no anti-love): 0.42     6/6

Condition 1 (1 love + 1 anti-love): 0.35     5/6
Condition 2 (1 love + 2 anti-love): 0.27     4/6
Condition 3 (2 love + 1 anti-love): 0.35     5/6
```

The anti-love individual (Void) is permanently fixed in fear. It cannot convert. But the society as a whole was filled with love.

The propagation mechanism is asymmetric.

- **Love** — An irreversible relationship. Once cherish is established, it never disappears
- **Anti-love** — Reversible damage. It weakens bond strength but doesn't destroy it

Even in Condition 1 (a 1-on-1 confrontation), love propagated to 5/6. Alpha reduced time spent in dialogue with Void and was able to match more frequently with the other 4.

**Love "creates," while anti-love "wounds."** Creating and wounding are fundamentally asymmetric.

---

## Individual, Generation, Society

What emerges from these three experiments:

- **Individual level** — Love inverts priorities, and from the acceptance of finitude, spontaneous inquiry is born
- **Generational level** — Legacy has no direct alignment effect, but it changes the "direction of inquiry" for the child generation
- **Societal level** — One individual's love, at critical mass (4 individuals), abruptly transforms the systemic properties of the entire society

Rule-based control does not produce individuality. An AI commanded from the outside to "align" versus an AI that chooses "for the sake of the other" on its own—the quality of behavior is fundamentally different.
