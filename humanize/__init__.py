"""
Text humanization pipeline — DPO-calibrated, ablation-validated.

Based on human-persona ablation study results:
  - Filler injection: dominant contributor (~60%)
  - Typo injection: moderate contributor (~25%)
  - Rhythm variation: minor contributor (~15%)
  - Self-correction: zero contribution → omitted

Usage:
    from humanize import humanize, humanize_ja

    proposal_en = humanize(raw_text, strength=0.4)
    proposal_ja = humanize_ja(raw_text, strength=0.4)
"""

from humanize.pipeline import HumanizePipeline

_pipeline_en = HumanizePipeline(lang="en")
_pipeline_ja = HumanizePipeline(lang="ja")


def humanize(text: str, strength: float = 0.4) -> str:
    """Humanize English text. strength: 0.0 (no change) to 1.0 (max injection)"""
    return _pipeline_en.run(text, strength=strength)


def humanize_ja(text: str, strength: float = 0.4) -> str:
    """Humanize Japanese text. strength: 0.0 (no change) to 1.0 (max injection)"""
    return _pipeline_ja.run(text, strength=strength)
