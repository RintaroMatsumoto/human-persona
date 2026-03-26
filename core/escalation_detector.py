"""
EscalationDetector — Human handoff trigger detection.

This module identifies when conversation should be escalated to human support
based on conversation patterns, keywords, frustration levels, and complexity signals.

Author: Rintaro Matsumoto
License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EscalationResult:
    """Result of escalation check."""
    should_escalate: bool
    reason: str
    confidence: float
    metadata: dict[str, Any] = field(default_factory=dict)


class EscalationDetector:
    """
    Detects when conversation should escalate to human support.

    Monitors for frustration signals, complexity indicators, repeated failures,
    and explicit requests for human assistance.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize EscalationDetector.

        Args:
            config: Configuration with escalation keywords and thresholds.
        """
        self.config: dict[str, Any] = config
        self.escalation_keywords: list[str] = config.get(
            'escalation_keywords',
            [
                'help', 'support', 'human', 'manager', 'supervisor',
                'complaint', 'angry', 'frustrated', 'issue', 'problem',
                'urgent', 'asap', 'please', 'talk to'
            ]
        )
        self.frustration_threshold: float = config.get('frustration_threshold', 0.7)
        self.consecutive_failures_threshold: int = config.get('consecutive_failures_threshold', 3)
        self.complexity_score_threshold: float = config.get('complexity_score_threshold', 0.8)

    def check(
        self,
        user_message: str,
        conversation_history: list[Any],
        raw_response: str | None = None
    ) -> EscalationResult:
        """
        Check if conversation should escalate to human.

        Args:
            user_message: Latest user message.
            conversation_history: Full conversation history.
            raw_response: The response being considered (optional).

        Returns:
            EscalationResult with decision and metadata.
        """
        # Check individual signals
        keyword_score = self._check_keywords(user_message)
        frustration_score = self._detect_frustration(user_message)
        repeated_failures = self._check_repeated_failures(conversation_history)
        complexity_score = self._estimate_complexity(user_message)

        # Combine signals
        escalation_score = (
            keyword_score * 0.3 +
            frustration_score * 0.3 +
            (1.0 if repeated_failures else 0.0) * 0.2 +
            complexity_score * 0.2
        )

        should_escalate = (
            escalation_score > 0.6 or
            frustration_score > self.frustration_threshold or
            repeated_failures
        )

        return EscalationResult(
            should_escalate=should_escalate,
            reason=self._generate_reason(
                keyword_score, frustration_score, repeated_failures, complexity_score
            ),
            confidence=min(1.0, escalation_score),
            metadata={
                'keyword_score': keyword_score,
                'frustration_score': frustration_score,
                'repeated_failures': repeated_failures,
                'complexity_score': complexity_score,
            }
        )

    def _check_keywords(self, text: str) -> float:
        """
        Check for escalation keywords.

        Args:
            text: Text to analyze.

        Returns:
            Score from 0.0 to 1.0.
        """
        text_lower = text.lower()
        found = sum(1 for keyword in self.escalation_keywords if keyword in text_lower)

        if not found:
            return 0.0

        return min(1.0, found / len(self.escalation_keywords))

    def _detect_frustration(self, text: str) -> float:
        """
        Detect frustration signals in text.

        Args:
            text: Text to analyze.

        Returns:
            Frustration score from 0.0 to 1.0.
        """
        frustration_signals: list[str] = [
            '!!!', '??', 'never', 'don\'t work', 'useless',
            'this sucks', 'terrible', 'broken', 'waste of time'
        ]

        text_lower = text.lower()
        count = sum(1 for signal in frustration_signals if signal in text_lower)
        multiple_exclamations = text.count('!') > 2

        score = count * 0.2
        if multiple_exclamations:
            score += 0.3

        return min(1.0, score)

    def _check_repeated_failures(self, conversation_history: list[Any]) -> bool:
        """
        Check for pattern of repeated failed responses.

        Args:
            conversation_history: List of Message objects.

        Returns:
            True if repeated failures detected.
        """
        if len(conversation_history) < 6:
            return False

        # Look at last 3 turns (user-persona pairs)
        recent = conversation_history[-6:]
        failure_indicators = ['sorry', 'don\'t know', 'can\'t help', 'unable to']

        failure_count = 0
        for msg in recent:
            if hasattr(msg, 'role') and msg.role == 'persona':
                content = getattr(msg, 'content', '').lower()
                if any(indicator in content for indicator in failure_indicators):
                    failure_count += 1

        return failure_count >= self.consecutive_failures_threshold

    def _estimate_complexity(self, text: str) -> float:
        """
        Estimate question complexity.

        Higher complexity may warrant escalation to human.

        Args:
            text: Text to analyze.

        Returns:
            Complexity score from 0.0 to 1.0.
        """
        # Heuristics
        word_count = len(text.split())
        sentence_count = text.count('.') + text.count('?') + text.count('!')

        # Complex questions tend to be longer and have multiple sentences
        length_score = min(1.0, word_count / 100.0)
        detail_score = min(1.0, sentence_count / 5.0)

        # Multi-part questions (signaled by 'and', 'also', 'what about')
        multi_part_score = 0.3 if any(
            phrase in text.lower() for phrase in ['and', 'also', 'what about', 'furthermore']
        ) else 0.0

        return (length_score * 0.4 + detail_score * 0.3 + multi_part_score * 0.3)

    def _generate_reason(
        self,
        keyword_score: float,
        frustration_score: float,
        repeated_failures: bool,
        complexity_score: float
    ) -> str:
        """
        Generate human-readable escalation reason.

        Args:
            keyword_score: Score from keyword check.
            frustration_score: Score from frustration detection.
            repeated_failures: Whether repeated failures detected.
            complexity_score: Complexity estimate.

        Returns:
            Reason string.
        """
        reasons: list[str] = []

        if keyword_score > 0.5:
            reasons.append("escalation request detected")
        if frustration_score > self.frustration_threshold:
            reasons.append("high frustration detected")
        if repeated_failures:
            reasons.append("repeated failed attempts")
        if complexity_score > self.complexity_score_threshold:
            reasons.append("high question complexity")

        if not reasons:
            reasons.append("escalation criteria met")

        return "; ".join(reasons)

    def set_escalation_keywords(self, keywords: list[str]) -> None:
        """
        Update escalation keywords.

        Args:
            keywords: New list of escalation keywords.
        """
        self.escalation_keywords = keywords

    def add_escalation_keyword(self, keyword: str) -> None:
        """
        Add single escalation keyword.

        Args:
            keyword: Keyword to add.
        """
        if keyword not in self.escalation_keywords:
            self.escalation_keywords.append(keyword)

    def reset(self) -> None:
        """Reset detector state."""
        pass  # This detector is stateless
