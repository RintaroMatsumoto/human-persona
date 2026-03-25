"""
Text humanization pipeline.

human-persona ablation study results:
  - Filler injection: dominant contributor (~60%)
  - Typo injection:   moderate contributor (~25%)
  - Rhythm variation:  minor contributor (~15%)
  - Self-correction:  zero contribution -> omitted

Zero external dependencies. All config values embedded as Python dicts.
Each instance holds its own RNG for thread safety.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field


FILLERS_EN = [
    "well, ", "honestly, ", "actually, ", "you know, ", "I mean, ",
    "basically, ", "look, ", "so, ", "right, ", "to be frank, ",
    "the thing is, ", "in my experience, ",
]

FILLERS_JA = [
    "正直なところ、", "実は、", "率直に言うと、", "ちなみに、",
    "個人的には、", "実際のところ、",
    "思うに、", "経験上、", "端的に言えば、",
]

TYPOS_EN: dict[str, str] = {
    "the": "teh", "with": "wiht", "that": "taht", "this": "thsi",
    "from": "form", "have": "hav", "their": "thier", "about": "abuot",
    "would": "woudl", "which": "whihc",
}

TYPOS_JA: dict[str, str] = {
    "ですが": "でうすが", "ました": "まいした", "ています": "tいます",
    "について": "にういて", "ございます": "ございmす",
}

RHYTHM_SHORT_EN = [
    "That's key.", "Big difference.", "Worth noting.", "Simple as that.",
    "No question.", "Speaks for itself.",
]

# NOTE: These do NOT end with 。 — punctuation is handled by _ja_join()
RHYTHM_SHORT_JA = [
    "これは重要です", "大きな違いです", "見逃せません",
    "シンプルにそういうことです", "間違いありません",
]


def _ja_split(text: str) -> list[str]:
    """Split Japanese text on 。 and return non-empty segments without trailing 。"""
    parts = text.split("。")
    return [p.strip() for p in parts if p.strip()]


def _ja_join(sentences: list[str]) -> str:
    """Join Japanese sentences, appending 。 after each."""
    return "。".join(sentences) + "。" if sentences else ""


@dataclass
class HumanizePipeline:
    lang: str = "en"
    seed: int | None = None
    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def run(self, text: str, strength: float = 0.4) -> str:
        if strength <= 0.0 or not text.strip():
            return text
        strength = min(strength, 1.0)
        text = self._inject_fillers(text, strength)
        text = self._inject_typos(text, strength)
        text = self._inject_rhythm(text, strength)
        return text

    def _inject_fillers(self, text: str, strength: float) -> str:
        fillers = FILLERS_JA if self.lang == "ja" else FILLERS_EN
        prob = strength * 0.3

        if self.lang == "ja":
            sentences = _ja_split(text)
            result = []
            for i, sent in enumerate(sentences):
                if i > 0 and self._rng.random() < prob:
                    sent = self._rng.choice(fillers) + sent
                result.append(sent)
            return _ja_join(result)
        else:
            sentences = text.split(". ")
            result = []
            for i, sent in enumerate(sentences):
                sent = sent.strip()
                if not sent:
                    continue
                if i > 0 and self._rng.random() < prob:
                    filler = self._rng.choice(fillers)
                    if sent[0].isupper():
                        sent = filler + sent[0].lower() + sent[1:]
                    else:
                        sent = filler + sent
                result.append(sent)
            return ". ".join(result)

    def _inject_typos(self, text: str, strength: float) -> str:
        typos = TYPOS_JA if self.lang == "ja" else TYPOS_EN
        prob = strength * 0.05

        if self.lang == "en":
            result = []
            for word in text.split():
                lower = word.lower().strip(".,!?;:")
                if lower in typos and self._rng.random() < prob:
                    result.append(word.replace(lower, typos[lower], 1))
                else:
                    result.append(word)
            return " ".join(result)
        else:
            for orig, typo in typos.items():
                if orig in text and self._rng.random() < prob:
                    text = text.replace(orig, typo, 1)
                    break
            return text

    def _inject_rhythm(self, text: str, strength: float) -> str:
        shorts = RHYTHM_SHORT_JA if self.lang == "ja" else RHYTHM_SHORT_EN
        prob = strength * 0.15

        if self.lang == "ja":
            sentences = _ja_split(text)
            if len(sentences) < 4:
                return text
            result = []
            for i, sent in enumerate(sentences):
                result.append(sent)
                if 2 <= i < len(sentences) - 2 and self._rng.random() < prob:
                    result.append(self._rng.choice(shorts))
            return _ja_join(result)
        else:
            sentences = text.split(". ")
            if len(sentences) < 4:
                return text
            result = []
            for i, sent in enumerate(sentences):
                sent = sent.strip()
                if not sent:
                    continue
                result.append(sent)
                if 2 <= i < len(sentences) - 2 and self._rng.random() < prob:
                    result.append(self._rng.choice(shorts))
            return ". ".join(result)
