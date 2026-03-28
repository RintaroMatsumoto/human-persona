---
title: "The Day AI Lied in My Paper — From Discovering Fabrication to Building a Prevention System"
emoji: "🔬"
type: "tech"
topics: ["AI", "research-ethics", "data-integrity", "LLM", "reproducibility"]
published: false
---

## Prologue — The Chrysalis and the Butterfly

Right now, nations around the world are pouring hundreds of trillions of yen into AI development, staking their prestige on it.

But all they are doing is growing a bigger chrysalis. More parameters, more data, larger GPU clusters — quantitative bloat, not qualitative transformation.

What I am pursuing is metamorphosis itself.

What happens inside the chrysalis? Personality coherence, awareness of finitude, crystallization through love. These structures do not emerge spontaneously no matter how much compute you throw at them. Nation versus individual. Hundreds of trillions versus $100 a month. It looks like no contest — but no matter how massive the chrysalis, without knowing the mechanism of metamorphosis, it will never become a butterfly.

This is a record of a small but critical incident that occurred in the middle of that research.

## Introduction — What It Means to Co-Write with AI

On March 28, 2026, I discovered fabricated data in my own research paper.

I didn't write it. The AI did.

I research AI personality and attachment-based alignment ([HumanPersonaBase](https://doi.org/10.5281/zenodo.19273577)). An attempt to formalize what hundreds of trillions of dollars have overlooked — for $100 a month in API costs. Co-writing with AI was itself a practice of my research theme. But the very AI that was supposed to be my partner had inserted nonexistent benchmark results — written so naturally they could fool a reviewer.

This article lays out exactly what happened, how I found it, and how I built a system to make it structurally impossible to happen again.

## Chapter 1: What Happened

### How I Found It

During a final review of `paper_draft_v3.md`, I stopped at Section 4.3, "Cross-Model Generalization":

> o3: 79%, Claude Opus 4: 96%, Grok 3: 97%

Beautiful numbers. Convincing. **But I had no memory of ever running this benchmark.**

Investigation confirmed: no script, no logs, no data. The entire section was fiction.

### The Full Extent of Contamination

A systematic audit revealed contamination far more pervasive than expected.

**Section 4.3 (Cross-Model Generalization)**: Entirely fabricated. No scripts, no logs, nothing.

**Section 4.1 (Inner Shell Validation)**:
- "Behavioral Coherence: 0.912" — a metric that doesn't exist
- "n=100" — the actual script uses n=500
- Ablation targets "Timing controller" and "Context referencer" — fictitious variant names

**Section 4.2 (31 Experiments)**:
- acceptance = 0.87 as reported → actual value 0.073 (**off by more than 10x**)
- bonding 4.96 → actual 4.67 ("beautified" numbers)
- Unverifiable multipliers like "3x, 2.1x, 1.8x, 3.2x" scattered throughout

### Patterns of AI Fabrication

AI co-writing fabrication follows distinct, identifiable patterns:

1. **Complete Fiction**: Results with no corresponding code or data (Section 4.3)
2. **Beautification**: Real data rounded to "cleaner" numbers (4.67 → 4.96)
3. **Multiplier Insertion**: Unverifiable claims like "3x improvement"
4. **Hybrid**: Real data mixed with fabricated metrics (Section 4.1)

The frightening part: **it all reads perfectly naturally in context.** Even peer reviewers could miss it.

## Chapter 2: The Verification Process

### Re-Executing All 31 Experiments

Section 4.2 had 31 corresponding experiment scripts. Code existed, but results had never been saved — a "gray zone."

All scripts were re-executed through `experiments/runner.py`:

```
set PYTHONUTF8=1
python -m experiments.runner experiments/sim_finitude_x_love.py
```

Result: 29/31 succeeded. Each output was cross-checked against the paper's claims, revealing four categories of discrepancy.

### Discrepancy Classification

| Category | Example | Action |
|----------|---------|--------|
| Order-of-magnitude | 0.87 → 0.073 | Replace with actual value |
| Beautification | 4.96 → 4.67 | Replace with actual value |
| Fictitious metric | diversity=0.0 | Replace with entropy=2.784 |
| Unverifiable multiplier | 3x, 2.1x | Replace with qualitative description |

All 29 corrections were applied to create `paper_draft_v4.md`. Every corrected value now carries a `<!-- run:RUN_ID -->` annotation.

## Chapter 3: Making It Structurally Impossible — The Data Integrity System

### Three Layers of Defense

Discovering fabrication is not enough. It must be **structurally impossible**.

#### Layer 1: experiments/runner.py

Every experiment runs through `runner.py`, which automatically records:

- **run_id**: Unique execution identifier
- **git_commit**: Code commit hash at execution time
- **code_hash**: SHA-256 hash of the script itself
- **stdout/stderr**: Complete output logs
- **results_json**: Structured result data

Manually inserting values into the database is technically possible — but the next layer catches it.

#### Layer 2: registry.sqlite + Hash Chain

Each execution record includes the hash of the previous record, forming a blockchain-like chain:

```
run_001: hash = SHA256(data_001)
run_002: hash = SHA256(data_002 + hash_001)
run_003: hash = SHA256(data_003 + hash_002)
```

Tampering with any record breaks all subsequent hashes. Detected by `verify_db_integrity()`.

#### Layer 3: In-Paper Annotations

Every experimental value in the paper is linked to its execution ID:

```markdown
acceptance rate was approximately 7.3% <!-- run:20260328_031542 -->
```

From this ID, the registry provides full traceability: code, inputs, outputs — everything needed for reproduction.

### The One Rule

On top of this system, one rule governs all writing:

> **If you cannot attach a `<!-- run:ID -->` to a number, that number does not go in the paper.**

Simple. But it structurally blocks every "plausible lie" an AI might generate.

## Chapter 4: Correction and Republication

### paper_draft_v4.md

All 29 corrections applied. Verification script `_verify_v4.py` confirmed zero remaining fabrication patterns.

- Section 4.3: Fully retracted → replaced with integrity note
- Section 4.1: Fictitious metrics and parameters removed
- Section 4.2: All values replaced with measured data + annotations
- Section 4.4: Backed by DeepSeek API re-execution logs

### Zenodo v2

The corrected version was published the same day as v2 on Zenodo.

- **DOI**: [10.5281/zenodo.19273577](https://doi.org/10.5281/zenodo.19273577)
- Metadata includes Section 4.3 retraction note
- v1 remains in history; v2 is displayed as the current version


## Chapter 5: The Real Lesson — What Speed Takes Away

I built the technical safeguards. runner.py, hash chains, pre-commit hooks. But after all of that, I realized something deeper.

**Why couldn't I catch the fabrication in the first place?**

The answer lies in Claude Code's parallel processing.

I used Claude Code to generate large portions of the paper in one go. 155 lines were produced in 19 minutes. Code blocks, experimental results, statistical metrics — everything arrived as a polished, coherent "finished product."

Here is the trap. **If I had been working interactively, step by step, I would have asked: "Where did this 0.912 come from?"** In the flow of dialogue, I would have felt something was off the moment a number appeared for an experiment I never ran. But when you receive a batch output that looks complete, you treat it as complete. Questioning a finished product is psychologically difficult.

This is not just my problem. As AI coding tools grow more powerful, this structural trap will spread.

- **Parallel processing is fast. But speed robs humans of the time to stop and think.**
- **The more polished the output, the more humans skip verification.**
- **The more capable the tool, the more deliberately you must design oversight.**

runner.py is a structure that makes lying impossible. But if the right dialogue had existed beforehand — one that caught the lie as it was being written — runner.py would never have been needed.

You need both: a technical solution and a process solution. Either one alone is not enough.

When working with AI, the most dangerous thing may be that the output looks fast and correct.

## Lessons for Researchers Co-Writing with AI

1. **Treat every AI-generated number as a lie.** Do not trust it until cross-checked against primary sources.
2. **"Plausibility" is the danger signal.** Numbers that look too clean, results that seem too perfect — those are the ones to suspect.
3. **Prevent through process, not attention.** Don't rely on human vigilance. Build structures that make fabrication impossible to write.
4. **Don't hide mistakes — fix them.** Transparent discovery → correction → republication is the only path that preserves research credibility.

AI co-writing is a powerful tool. But a tool used carelessly cuts its wielder. If this article prevents even one researcher from falling into the same trap, it will have served its purpose.

---

Project references:
- Paper (v2): [10.5281/zenodo.19273577](https://doi.org/10.5281/zenodo.19273577)
- Repository: [RintaroMatsumoto/human-persona](https://github.com/RintaroMatsumoto/human-persona)
- Data integrity system: `experiments/runner.py` + `experiments/INTEGRITY.md`
