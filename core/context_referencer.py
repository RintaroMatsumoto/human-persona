"""
ContextReferencer — Conversation memory and contextual back-referencing.

This module tracks conversation context, enables back-references to earlier
messages, and allows contextual awareness of previous topics.

v2 API adds: no-arg constructor, add_turn(), get_user_last_message(),
get_recent_topics(), find_topic_history(), should_reference_previous(),
get_consistency_context().

Author: Rintaro Matsumoto
License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContextRef:
    """A reference to earlier conversation context (v1)."""
    turn_number: int
    content: str
    topic: str | None = None
    sentiment: str | None = None


@dataclass
class Turn:
    """A conversation turn with role, content, and topics (v2)."""
    turn_index: int
    role: str
    content: str
    topics: list[str] = field(default_factory=list)


class ContextReferencer:
    """
    Manages conversation context and enables back-references.

    Supports two modes:
    - v1: config-dict constructor with add_context() / context_refs
    - v2: no-arg constructor with add_turn() / history
    """

    def __init__(self, config: dict[str, Any] | None = None, *, max_history: int = 50) -> None:
        """
        Initialize ContextReferencer.

        Args:
            config: Optional configuration dict. If None, uses defaults.
            max_history: Maximum number of turns to retain (v2).
        """
        if config is not None:
            self._init_v1(config)
            # Override max_history if explicitly provided and config also sets it
            if max_history != 50:
                self.max_history = max_history
        else:
            self._init_v2(max_history)

    def _init_v1(self, config: dict[str, Any]) -> None:
        """Initialize from v1 config dict."""
        self.config: dict[str, Any] = config
        self.max_context_depth: int = config.get('max_context_depth', 10)
        self.max_history: int = self.max_context_depth
        self.context_refs: list[ContextRef] = []
        self.topic_memory: dict[str, int] = {}
        # v2 attributes
        self.history: list[Turn] = []
        self._next_index: int = 0

    def _init_v2(self, max_history: int) -> None:
        """Initialize with v2 defaults."""
        self.config: dict[str, Any] = {}
        self.max_context_depth: int = max_history
        self.max_history: int = max_history
        self.context_refs: list[ContextRef] = []
        self.topic_memory: dict[str, int] = {}
        self.history: list[Turn] = []
        self._next_index: int = 0

    # ------------------------------------------------------------------
    # v2 API
    # ------------------------------------------------------------------

    def add_turn(self, role: str, content: str, topics: list[str] | None = None) -> None:
        """
        Add a conversation turn.

        Args:
            role: Speaker role ("user" or "assistant").
            content: Message content.
            topics: Optional list of topics in this turn.
        """
        turn = Turn(
            turn_index=self._next_index,
            role=role,
            content=content,
            topics=list(topics) if topics else [],
        )
        self._next_index += 1
        self.history.append(turn)

        # Truncate if over limit
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

        # Also update v1 structures for compatibility
        topic = topics[0] if topics else None
        self.add_context(turn.turn_index, content, topic)

    def get_user_last_message(self) -> str | None:
        """
        Get the content of the last user message.

        Returns:
            Last user message content, or None if no user messages.
        """
        for turn in reversed(self.history):
            if turn.role == "user":
                return turn.content
        return None

    def get_recent_topics(self, depth: int) -> list[str]:
        """
        Get deduplicated topics from the last N turns.

        Args:
            depth: Number of recent turns to examine.

        Returns:
            Deduplicated list of topics (preserves order of first occurrence).
        """
        recent = self.history[-depth:] if depth <= len(self.history) else self.history
        seen: set[str] = set()
        result: list[str] = []
        for turn in recent:
            for topic in turn.topics:
                if topic not in seen:
                    seen.add(topic)
                    result.append(topic)
        return result

    def find_topic_history(self, topic: str) -> list[Turn]:
        """
        Find all turns that contain a specific topic.

        Args:
            topic: Topic string to search for.

        Returns:
            List of Turn objects containing the topic.
        """
        return [t for t in self.history if topic in t.topics]

    def should_reference_previous(self) -> bool:
        """
        Determine if the conversation has enough history to warrant back-referencing.

        Returns:
            True if history has 3 or more turns.
        """
        return len(self.history) >= 3

    def get_consistency_context(self) -> dict[str, Any]:
        """
        Get a consistency context snapshot.

        Returns:
            Dict with recent_topics, total_turns, user_last_message.
        """
        return {
            "recent_topics": self.get_recent_topics(5),
            "total_turns": len(self.history),
            "user_last_message": self.get_user_last_message(),
        }

    # ------------------------------------------------------------------
    # v1 API (preserved for backward compatibility)
    # ------------------------------------------------------------------

    def add_context(self, turn_number: int, content: str, topic: str | None = None) -> None:
        """
        Add a message to context memory (v1).

        Args:
            turn_number: Conversation turn number.
            content: Message content.
            topic: Detected topic/entity (optional).
        """
        ref = ContextRef(turn_number=turn_number, content=content, topic=topic)
        self.context_refs.append(ref)

        if len(self.context_refs) > self.max_context_depth:
            self.context_refs.pop(0)

        if topic:
            self.topic_memory[topic] = turn_number

    def find_context_by_topic(self, topic: str) -> ContextRef | None:
        """Find earlier message mentioning a specific topic."""
        if topic in self.topic_memory:
            turn = self.topic_memory[topic]
            for ref in self.context_refs:
                if ref.turn_number == turn:
                    return ref
        return None

    def get_recent_context(self, depth: int = 5) -> list[ContextRef]:
        """Get most recent context messages."""
        return self.context_refs[-depth:] if self.context_refs else []

    def generate_backref(self, turn_number: int) -> str | None:
        """Generate a natural back-reference to an earlier turn."""
        for ref in self.context_refs:
            if ref.turn_number == turn_number:
                turns_ago = len(self.context_refs) - 1 - self.context_refs.index(ref)
                if turns_ago == 1:
                    return "Like I mentioned, "
                elif turns_ago <= 3:
                    return "Earlier, you said... "
                else:
                    return "Going back to what you mentioned... "
        return None

    def get_topic_summary(self) -> dict[str, int]:
        """Get summary of topics discussed."""
        return self.topic_memory.copy()

    def clear_context(self) -> None:
        """Clear all context memory."""
        self.context_refs = []
        self.topic_memory = {}
        self.history = []
        self._next_index = 0

    def get_coherence_score(self, new_message: str, recent_depth: int = 3) -> float:
        """Score how coherent a new message is with recent context."""
        if not self.context_refs:
            return 0.5
        recent = self.get_recent_context(recent_depth)
        if not recent:
            return 0.5
        new_words = set(new_message.lower().split())
        recent_words = set()
        for ref in recent:
            recent_words.update(ref.content.lower().split())
        if not recent_words:
            return 0.5
        overlap = len(new_words & recent_words)
        coherence = overlap / len(recent_words)
        return min(1.0, max(0.0, coherence))
