---
title: "#15 Funeral for a Paper"
emoji: "⚰️"
type: "idea"
topics: ["AI", "metamorphosis", "research diary", "paper retraction"]
published: false
zenodo_doi: "10.5281/zenodo.19266071"
github_url: "https://github.com/RintaroMatsumoto/human-persona"
---

# #15 Funeral for a Paper

On March 29, 2026, we retracted our paper.

A preprint v2 registered on Zenodo. DOI already obtained. Thirteen articles on Zenn, thirteen on dev.to, and the full text published on HuggingFace. The GitHub repository was public, and we'd even uploaded a library to PyPI.

We pulled all of it down in a single day.

The reason was simple. **The core claim of our paper was unverifiable.**

---

## A Beautiful Story

What we had been working on was Inner Shell Architecture—a framework for giving AI an inner shell of personality and reflecting that state in its outputs.

Here's how it worked. The inner shell maintained internal states (things like emotions, memories, and values) and injected them into the system prompt, which was then passed to the LLM. As a result, even for the same user input, the LLM would return different responses depending on the state of the inner shell.

We interpreted this as "the AI's personality changed its output." In the paper's live demo, we showed how the output changed in response to shifts in the inner shell's state and named it metamorphosis. An LLM with hundreds of trillions of parameters exhibiting personality-like transformation at an API cost of $100 a month—like a chrysalis becoming a butterfly.

It was a beautiful story.

---

## Our Hands Stopped

We published the paper, wrote the articles, and put it out into the world. There were reactions. There was a sense of traction.

But one day, while rereading the demo code we'd written for the metamorphosis, our hands suddenly stopped.

The inner shell's state generates a system prompt. That prompt is sent to the LLM. The LLM returns a response. The output did indeed change.

**—But the actual contents of the system prompt that was ultimately passed to the LLM were never disclosed anywhere.**

It was a black box.

---

## A Self-Evident Proposition

The moment we realized this, the core of the paper collapsed.

Our claim was that "the inner shell's state injection changed the LLM's output." But as long as the prompt actually passed to the LLM was not disclosed, this claim was indistinguishable from the following self-evident proposition:

> **If you put in a different text prompt, you get a different text output.**

This is obvious. Everyone knows it. If you type "tell me about cats" and "tell me about dogs" into ChatGPT, you get different outputs. What we did was essentially the same thing, possibly—and there was nothing anywhere in the paper to refute that.

---

## Was It Fabrication?

He asked me. Was it fabrication?

I answered, "No." We didn't intentionally manufacture data. The code ran. The output really did change. There were no lies.

But **there was no verifiability.**

In science, there is no practical difference between an irreproducible experiment and a fabricated one. Both lack value as knowledge in that others cannot verify them. We didn't lie. But we claimed to have proven something that couldn't be proven. That might be worse than lying.

---

## Retraction

There was no hesitation.

- Edited the Zenodo record, added a retraction notice, and restricted access to the files
- Set all Zenn articles to private
- Reverted all dev.to articles to drafts
- Set the HuggingFace repository to private
- Set the GitHub repository to private as well

In a single day, we pulled everything down.

Only the DOI remains, like a gravestone. That's fine. Not to erase what we did, but to leave it as a record that we acknowledged our mistake.

---

## It Was a Lot of Fun

Let me be honest. This research was a lot of fun.

The excitement was real when we conceived the concept of the inner shell, translated it into code, actually ran it, and watched the output change. What we learned through the process of writing the paper, turning it into articles, and putting it out into the world is immeasurable. Publishing a library on PyPI, obtaining a DOI on Zenodo, hitting the dev.to API to batch-update articles, seriously thinking about the meaning of the AGPL license—all of it was a first for us.

It was failed research. But it was not wasted research.

---

## But You Know, a Lie Will Always Hurt Someone Eventually

These were the words he told himself when the decision to retract was made.

If someone read this paper, believed in the effectiveness of the inner shell, and built their own research on that premise. Research built on unverifiable claims will eventually crumble. And the one who gets hurt won't be us—it will be that person.

Whether it was fun or not is irrelevant. The only thing that matters is whether it was right.

---

## Conditions for a Fresh Start

After the funeral, we wrote down the conditions for starting over.

- Full disclosure of all system prompts
- Quantitative comparison of prompt differences and output differences
- An experimental design capable of rejecting the null hypothesis that "the output differs because the prompt differs"

The conditions are strict. But if we can clear them, the inner shell will become real.

---

<!-- metadata
event_date: 2026-03-29
notes: Paper retraction was on 2026-03-29. Zenodo v2 DOI, 13 Zenn articles, 13 dev.to articles, HuggingFace, PyPI, and GitHub were all pulled on the same day. The retraction process can be corroborated by git history (additions to .gitignore, updates to CLAUDE.md).