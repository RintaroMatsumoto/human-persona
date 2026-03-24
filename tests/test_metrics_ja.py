"""
Tests for analysis/metrics_ja.py and analysis/ja_keywords.py

Validates Japanese-specific metric functions with known test data.
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from analysis.metrics_ja import (
    measure_sentence_length_cv_ja,
    measure_hedge_rate_ja,
    measure_self_correction_rate_ja,
    measure_morphemes_per_sentence_ja,
    measure_kanji_ratio_ja,
    measure_cushion_rate_ja,
    measure_filler_rate_ja,
    split_sentences_ja,
    count_keywords,
    count_morphemes,
    HAS_MECAB,
)
from analysis.ja_keywords import (
    HEDGE_KEYWORDS_JA,
    SELF_CORRECTION_JA,
    CUSHION_JA,
    FILLER_JA,
)


# ===========================================================================
# split_sentences_ja
# ===========================================================================

class TestSplitSentencesJa:
    def test_basic_split(self):
        text = "これはテストです。二つ目の文です。三つ目。"
        result = split_sentences_ja(text)
        assert len(result) == 3

    def test_exclamation_and_question(self):
        text = "すごい！本当ですか？はい。"
        result = split_sentences_ja(text)
        assert len(result) == 3

    def test_newline_split(self):
        text = "一行目\n二行目\n三行目"
        result = split_sentences_ja(text)
        assert len(result) == 3

    def test_empty(self):
        assert split_sentences_ja("") == []

    def test_single_sentence(self):
        result = split_sentences_ja("これだけ")
        assert len(result) == 1


# ===========================================================================
# count_keywords
# ===========================================================================

class TestCountKeywords:
    def test_basic(self):
        text = "たぶんこれでいいと思います"
        count = count_keywords(text, HEDGE_KEYWORDS_JA)
        # "たぶん" + "と思います" = 2
        assert count == 2

    def test_no_match(self):
        text = "東京タワーは高い建物です"
        count = count_keywords(text, HEDGE_KEYWORDS_JA)
        assert count == 0


# ===========================================================================
# measure_sentence_length_cv_ja
# ===========================================================================

class TestSentenceLengthCvJa:
    def test_uniform(self):
        text = "短い文。短い文。短い文。"
        cv = measure_sentence_length_cv_ja(text)
        assert cv is not None
        assert cv < 0.1

    def test_varied(self):
        text = "短い。これは非常に長い文で文字数がかなり異なるはずの文になっています。"
        cv = measure_sentence_length_cv_ja(text)
        assert cv is not None
        assert cv > 0.5

    def test_single_returns_none(self):
        assert measure_sentence_length_cv_ja("一文だけ") is None

    def test_empty_returns_none(self):
        assert measure_sentence_length_cv_ja("") is None


# ===========================================================================
# measure_hedge_rate_ja
# ===========================================================================

class TestHedgeRateJa:
    def test_with_hedges(self):
        text = "たぶんこれでいいと思います。おそらく大丈夫でしょう。"
        rate = measure_hedge_rate_ja(text)
        assert rate > 0.5  # multiple hedges

    def test_no_hedges(self):
        text = "報告書を提出しました。完了です。"
        rate = measure_hedge_rate_ja(text)
        assert rate == 0.0

    def test_empty(self):
        assert measure_hedge_rate_ja("") == 0.0


# ===========================================================================
# measure_self_correction_rate_ja
# ===========================================================================

class TestSelfCorrectionRateJa:
    def test_with_corrections(self):
        text = "というかそれは違いますね。いや、正確には別の話です。"
        rate = measure_self_correction_rate_ja(text)
        assert rate > 0.0

    def test_no_corrections(self):
        text = "これで完了しました。問題ありません。"
        assert measure_self_correction_rate_ja(text) == 0.0


# ===========================================================================
# measure_morphemes_per_sentence_ja
# ===========================================================================

class TestMorphemesPerSentenceJa:
    def test_basic(self):
        text = "今日は天気がいいです。明日も晴れるでしょう。"
        mps = measure_morphemes_per_sentence_ja(text)
        assert mps > 0

    def test_empty(self):
        assert measure_morphemes_per_sentence_ja("") == 0.0

    def test_mecab_produces_more_than_one(self):
        text = "東京タワーに行きました。"
        mps = measure_morphemes_per_sentence_ja(text)
        assert mps > 1  # should have multiple morphemes


class TestMorphemesFallback:
    """Test character-based fallback when MeCab is unavailable."""

    def test_fallback_returns_positive(self):
        import analysis.metrics_ja as mod
        original = mod.HAS_MECAB
        try:
            mod.HAS_MECAB = False
            # count_morphemes with fallback
            from analysis.metrics_ja import count_morphemes
            result = count_morphemes("テスト文です")
            assert result > 0
        finally:
            mod.HAS_MECAB = original


# ===========================================================================
# measure_kanji_ratio_ja
# ===========================================================================

class TestKanjiRatioJa:
    def test_kanji_heavy(self):
        text = "経済産業省の報告書によると日本経済は回復基調"
        ratio = measure_kanji_ratio_ja(text)
        assert ratio > 0.3

    def test_hiragana_only(self):
        text = "これはひらがなだけのぶんです"
        ratio = measure_kanji_ratio_ja(text)
        assert ratio == 0.0

    def test_empty(self):
        assert measure_kanji_ratio_ja("") == 0.0


# ===========================================================================
# measure_cushion_rate_ja
# ===========================================================================

class TestCushionRateJa:
    def test_with_cushion(self):
        text = "お世話になっております。本日の件についてご連絡です。"
        assert measure_cushion_rate_ja(text) is True

    def test_without_cushion(self):
        text = "報告書を添付します。ご確認ください。"
        assert measure_cushion_rate_ja(text) is False

    def test_arigatou(self):
        text = "ありがとうございます。助かりました。"
        assert measure_cushion_rate_ja(text) is True

    def test_empty(self):
        assert measure_cushion_rate_ja("") is False


# ===========================================================================
# measure_filler_rate_ja
# ===========================================================================

class TestFillerRateJa:
    def test_with_fillers(self):
        text = "えーと、まあ、そうですね。なんかちょっと違う気がします。"
        rate = measure_filler_rate_ja(text)
        assert rate > 1.0  # multiple fillers per sentence

    def test_no_fillers(self):
        text = "報告書を作成しました。添付いたします。"
        assert measure_filler_rate_ja(text) == 0.0


# ===========================================================================
# Keyword lists
# ===========================================================================

class TestKeywordLists:
    def test_hedge_not_empty(self):
        assert len(HEDGE_KEYWORDS_JA) > 0

    def test_self_correction_not_empty(self):
        assert len(SELF_CORRECTION_JA) > 0

    def test_cushion_not_empty(self):
        assert len(CUSHION_JA) > 0

    def test_filler_not_empty(self):
        assert len(FILLER_JA) > 0

    def test_no_duplicates_in_hedge(self):
        assert len(HEDGE_KEYWORDS_JA) == len(set(HEDGE_KEYWORDS_JA))

    def test_no_duplicates_in_filler(self):
        assert len(FILLER_JA) == len(set(FILLER_JA))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
