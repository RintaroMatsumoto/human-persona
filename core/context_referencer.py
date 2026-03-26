"""
ContextReferencer — Conversation memory and contextual back-referencing.

This module tracks conversation context, enables back-references to earlier
messages, and allows contextual awareness of previous topics.

Author: Rintaro Matsumoto
License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContextRef:
    """A reference to earlier conversation context."""
    turn_number: int
    content: str
    topic: str | None = None
    sentiment: str | None = None


class ContextReferencer:
    """
    Manages conversation context and enables back-references.

    Allows AI to naturally reference earlier parts of conversation,
    creating continuity and human-like memory of discussion flow.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize ContextReferencer.

        Args:
            config: Configuration with context parameters.
        """
        self.config: dict[str, Any] = config
        self.max_context_depth: int = config.get('max_context_depth', 10)
        self.max_history: int = self.max_context_depth
        self.context_refs: list[ContextRef] = []
        self.topic_memory: dict[str, int] = {}  # topic -> turn_number

    def add_context(self, turn_number: int, content: str, topic: str | None = None) -> None:
        """
        Add a message to context memory.

        Args:
            turn_number: Conversation turn number.
            content: Message content.
            topic: Detected topic/entity (optional).
        """
        ref = ContextRef(
            turn_number=turn_number,
            content=content,
            topic=topic
        )
        self.context_refs.append(ref)

        # Trim old context
        if len(self.context_refs) > self.max_context_depth:
            self.context_refs.pop(0)

        # Track topic
        if topic:
            self.topic_memory[topic] = turn_number

    def find_context_by_topic(self, topic: str) -> ContextRef | None:
        """
        Find earlier message mentioning a specific topic.

        Args:
            topic: Topic to search for.

        Returns:
            ContextRef if found, else None.
        """
        if topic in self.topic_memory:
            turn = self.topic_memory[topic]
            for ref in self.context_refs:
                if ref.turn_number == turn:
                    return ref

        return None

    def get_recent_context(self, depth: int = 5) -> list[ContextRef]:
        """
        Get most recent context messages.

        Args:
            depth: Number of recent messages to return.

        Returns:
            List of recent ContextRef objects.
        """
        return self.context_refs[-depth:] if self.context_refs else []

    def generate_backref(self, turn_number: int) -> str | None:
        """
        Generate a natural back-reference to an earlier turn.

        Args:
            turn_number: Turn to reference.

        Returns:
            Back-reference phrase or None if not found.
        """
        for ref in self.context_refs:
            if ref.turn_number == turn_number:
                turns_ago = len(self.context_refs) - 1 - self.context_refs.index(ref)

                if turns_ago == 1:
                    return f"Like I mentioned, "
                elif turns_ago <= 3:
                    return f"Earlier, you said... "
                else:
                    return f"Going back to what you mentioned... "

        return None

    def get_topic_summary(self) -> dict[str, int]:
        """
        Get summary of topics discussed.

        Returns:
            Dict mapping topics to turn numbers.
        """
        return self.topic_memory.copy()

    def clear_context(self) -> None:
        """Clear all context memory."""
        self.context_refs = []
        self.topic_memory = {}

    def get_coherence_score(self, new_message: str, recent_depth: int = 3) -> float:
        """
        Score how coherent a new message is with recent context.

        Args:
            new_message: Proposed message.
            recent_depth: How many recent turns to consider.

        Returns:
            Coherence score from 0.0 to 1.0.
        """
        if not self.context_refs:
            return 0.5  # Neutral if no context

        recent = self.get_recent_context(recent_depth)
        if not recent:
            return 0.5

        # Simple overlap-based coherence
        new_words = set(new_message.lower().split())
        recent_words = set()

        for ref in recent:
            recent_words.update(ref.content.lower().split())

        if not recent_words:
            return 0.5

        overlap = len(new_words & recent_words)
        coherence = overlap / len(recent_words)

        return min(1.0, max(0.0, coherence))
