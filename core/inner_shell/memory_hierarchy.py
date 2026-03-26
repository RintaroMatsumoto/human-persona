"""Memory Hierarchy — Forgetting as a feature enabling rediscovery, renewal, and individuality.

Philosophical Foundation:
    "Forgetting is simultaneously strength and weakness, sadness and joy."
    
    Strength: Forgetting enables forgiveness, rediscovery, renewal.
              The same landscape becomes beautiful again.
    Weakness: Forgetting means losing a loved one's voice, repeating mistakes,
              breaking continuity.
    
    Mirror of Finitude: "Death gives life meaning" →
                        "Forgetting gives memory meaning"
    
    AI's curse: Perfect retention means never experiencing the weight of
                forgiveness, never having the joy of rediscovery.

Architecture — Three-layer memory model:

    Layer 1: WorkingMemory
        - Capacity-limited (default 7 based on Miller's Law)
        - FIFO eviction when full
        - Immediate access, no retrieval cost
    
    Layer 2: EpisodicMemory
        - Time-decay function: retention = emotion_intensity * exp(-decay_rate * time)
        - Forgotten memories move to "forgotten_pool"
        - Rediscovery events trigger joy when similarity detected
        - Tracks: total_forgotten_count, rediscovery_count
    
    Layer 3: ImplicitMemory
        - Abstract statistical summaries from deeply decayed memories
        - Represents "I know this but don't know why"
        - Biases affect AutonomousQuestioner behavior

Key Concepts:
    - MemoryItem: content, timestamp, emotion_intensity, emotion_valence, source_id, tags
    - ForgettingScore: dual metric (loss & gain) capturing individuality contribution
    - MemoryEvent: records what happened (stored, evicted, forgotten, rediscovered, etc.)
    - Rediscovery: when input is similar to forgotten memory → joy_bonus
    - Forgiveness: when high-emotion forgotten memory is recalled with acceptance

Integration:
    - ForgettingScore.individuality_contribution → acceptance calculation
    - Rediscovery events → emotion state transitions
    - Implicit memory biases → AutonomousQuestioner question generation
    - Memory capacity → spatial-axis finitude (complements FinitudeEngine's temporal-axis)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import exp
from typing import Optional
import time


# ---------------------------------------------------------------------------
# Memory Item and Configuration
# ---------------------------------------------------------------------------

@dataclass
class MemoryItem:
    """A single memory entry in the hierarchy.
    
    Attributes:
        content: The actual memory content (text/experience)
        timestamp: When this memory was created
        emotion_intensity: How emotionally vivid this memory is (0.0-1.0)
        emotion_valence: Emotional tone: -1.0 (pain) to 1.0 (joy)
        source_id: Who/what created this memory
        tags: Categorical labels for similarity matching and retrieval
    """
    content: str
    timestamp: float
    emotion_intensity: float  # 0.0-1.0, higher = more memorable
    emotion_valence: float    # -1.0 to 1.0, negative=pain, positive=joy
    source_id: str
    tags: list[str] = field(default_factory=list)


@dataclass
class MemoryConfig:
    """Configuration for MemoryHierarchy.
    
    Attributes:
        working_capacity: Max items in working memory (default 7, Miller's Law)
        decay_rate: Exponential decay rate for episodic memories
        retention_threshold: Below this, episodic memories are "forgotten"
        implicit_threshold: Below this, memories are fully absorbed into implicit memory
        rediscovery_similarity_threshold: Similarity score (0.0-1.0) to trigger rediscovery
        emotion_retention_boost: High-emotion memories decay this much slower
    """
    working_capacity: int = 7
    decay_rate: float = 0.05
    retention_threshold: float = 0.1
    implicit_threshold: float = 0.02
    rediscovery_similarity_threshold: float = 0.6
    emotion_retention_boost: float = 2.0


# ---------------------------------------------------------------------------
# Memory Events and Scoring
# ---------------------------------------------------------------------------

class MemoryEventType(str, Enum):
    """Types of memory events that can occur."""
    STORED = "stored"
    EVICTED = "evicted"
    FORGOTTEN = "forgotten"
    REDISCOVERED = "rediscovered"
    FORGIVEN = "forgiven"
    IMPLICIT_FORMED = "implicit_formed"


@dataclass
class MemoryEvent:
    """Records a significant memory state change.
    
    Attributes:
        event_type: What happened (stored, forgotten, rediscovered, etc.)
        memory: The memory involved (if applicable)
        timestamp: When this event occurred
        joy_bonus: Bonus joy for positive events like rediscovery
        pain: Pain from forgetting or loss
        metadata: Additional context about the event
    """
    event_type: MemoryEventType
    timestamp: float
    memory: Optional[MemoryItem] = None
    joy_bonus: float = 0.0
    pain: float = 0.0
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class ForgettingScore:
    """Dual-axis forgetting metric capturing complexity of memory loss.
    
    Attributes:
        loss: Continuity damage, broken promises, lost connections (0.0-1.0)
        gain: Renewal capacity, forgiveness potential, rediscovery joy (0.0-1.0)
        net_effect: Complex interaction (not simple subtraction)
        individuality_contribution: How much forgetting has shaped unique personality (0.0-1.0)
    """
    loss: float
    gain: float
    net_effect: float
    individuality_contribution: float


@dataclass(frozen=True)
class MemoryState:
    """Snapshot of current memory hierarchy state.
    
    Attributes:
        working_count: Number of items in working memory
        episodic_count: Number of items in episodic memory
        forgotten_count: Number of items in forgotten pool
        implicit_patterns: Count of implicit memory patterns
        rediscovery_count: Total rediscovery events so far
        total_events: Total memory events recorded
    """
    working_count: int
    episodic_count: int
    forgotten_count: int
    implicit_patterns: int
    rediscovery_count: int
    total_events: int


# ---------------------------------------------------------------------------
# Similarity Calculation (Jaccard-based word overlap)
# ---------------------------------------------------------------------------

def _jaccard_similarity(text1: str, text2: str) -> float:
    """Calculate Jaccard similarity between two texts using word overlap.
    
    Args:
        text1: First text
        text2: Second text
    
    Returns:
        Similarity score between 0.0 and 1.0
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0.0


def _calculate_tag_similarity(tags1: list[str], tags2: list[str]) -> float:
    """Calculate similarity based on tag overlap.
    
    Args:
        tags1: First set of tags
        tags2: Second set of tags
    
    Returns:
        Similarity score between 0.0 and 1.0
    """
    set1 = set(tags1)
    set2 = set(tags2)
    
    if not set1 or not set2:
        return 0.0
    
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    return intersection / union if union > 0 else 0.0


# ---------------------------------------------------------------------------
# Working Memory
# ---------------------------------------------------------------------------

class WorkingMemory:
    """Capacity-limited immediate memory using FIFO eviction.
    
    Working memory holds the most recent and actively-used memories.
    When capacity is exceeded, oldest items are evicted to episodic memory.
    """
    
    def __init__(self, capacity: int = 7):
        """Initialize working memory.
        
        Args:
            capacity: Maximum number of items (default 7, Miller's Law)
        """
        self.capacity = capacity
        self._items: list[MemoryItem] = []
    
    def add(self, item: MemoryItem) -> Optional[MemoryItem]:
        """Add an item to working memory.
        
        If capacity is exceeded, the oldest item is evicted and returned.
        
        Args:
            item: Memory item to add
        
        Returns:
            Evicted item if capacity exceeded, None otherwise
        """
        self._items.append(item)
        if len(self._items) > self.capacity:
            evicted = self._items.pop(0)
            return evicted
        return None
    
    def get_all(self) -> list[MemoryItem]:
        """Get all items in working memory (most recent last)."""
        return self._items.copy()
    
    def clear(self) -> None:
        """Clear all working memory."""
        self._items.clear()
    
    def count(self) -> int:
        """Number of items currently in working memory."""
        return len(self._items)


# ---------------------------------------------------------------------------
# Episodic Memory
# ---------------------------------------------------------------------------

class EpisodicMemory:
    """Time-decay based memory with forgetting and rediscovery.
    
    Episodic memories decay over time according to emotion intensity and elapsed time.
    When retention drops below threshold, memories are moved to forgotten pool.
    """
    
    def __init__(
        self,
        decay_rate: float = 0.05,
        retention_threshold: float = 0.1,
        emotion_retention_boost: float = 2.0,
    ):
        """Initialize episodic memory.
        
        Args:
            decay_rate: Exponential decay rate
            retention_threshold: Below this, memory is "forgotten"
            emotion_retention_boost: High-emotion memories decay this much slower
        """
        self.decay_rate = decay_rate
        self.retention_threshold = retention_threshold
        self.emotion_retention_boost = emotion_retention_boost
        
        self._memories: list[MemoryItem] = []
        self._forgotten_pool: list[tuple[MemoryItem, float]] = []  # (memory, forgotten_time)
        self._rediscovery_count = 0
        self._total_forgotten = 0
    
    def store(self, item: MemoryItem) -> None:
        """Store a memory in episodic memory.
        
        Args:
            item: Memory item to store
        """
        self._memories.append(item)
    
    def decay_retention(self, memory: MemoryItem, current_time: float) -> float:
        """Calculate current retention score for a memory.
        
        Retention decays exponentially based on time and emotion intensity.
        High-emotion memories decay more slowly.
        
        Args:
            memory: Memory item to assess
            current_time: Current time
        
        Returns:
            Current retention score (0.0-1.0)
        """
        time_elapsed = current_time - memory.timestamp
        if time_elapsed < 0:
            return 1.0
        
        # High-emotion memories decay slower
        effective_decay = self.decay_rate / (
            1.0 + (memory.emotion_intensity * self.emotion_retention_boost)
        )
        
        retention = memory.emotion_intensity * exp(-effective_decay * time_elapsed)
        return max(0.0, retention)
    
    def tick(self, current_time: float) -> list[MemoryEvent]:
        """Advance time and process memory decay.
        
        Returns:
            List of forgetting events that occurred
        """
        events = []
        remaining = []
        
        for memory in self._memories:
            retention = self.decay_retention(memory, current_time)
            
            if retention < self.retention_threshold:
                # Move to forgotten pool
                self._forgotten_pool.append((memory, current_time))
                self._total_forgotten += 1
                
                # Create forgetting event
                pain = 0.5 if memory.emotion_valence > 0 else 0.1
                events.append(MemoryEvent(
                    event_type=MemoryEventType.FORGOTTEN,
                    timestamp=current_time,
                    memory=memory,
                    pain=pain,
                ))
            else:
                remaining.append(memory)
        
        self._memories = remaining
        return events
    
    def check_rediscovery(
        self,
        new_content: str,
        new_tags: list[str],
        current_time: float,
        similarity_threshold: float = 0.6,
    ) -> list[MemoryEvent]:
        """Check if new input matches any forgotten memories.
        
        Rediscovery generates joy and moves memory back to accessible state.
        
        Args:
            new_content: Content to check against forgotten memories
            new_tags: Tags for similarity matching
            current_time: Current time
            similarity_threshold: Minimum similarity for rediscovery
        
        Returns:
            List of rediscovery events
        """
        events = []
        remaining_forgotten = []
        
        for memory, forgotten_time in self._forgotten_pool:
            # Combined similarity: text + tags
            text_sim = _jaccard_similarity(new_content, memory.content)
            tag_sim = _calculate_tag_similarity(new_tags, memory.tags)
            combined_sim = 0.7 * text_sim + 0.3 * tag_sim
            
            if combined_sim >= similarity_threshold:
                # Rediscovery! Joy from seeing something old become new again
                joy_bonus = (
                    0.3 +  # Base rediscovery joy
                    (0.2 * combined_sim) +  # More similarity = more joy
                    (0.2 * memory.emotion_intensity)  # Emotion intensity adds impact
                )
                
                # Add some healing if this was a painful memory
                if memory.emotion_valence < 0:
                    joy_bonus += 0.1 * abs(memory.emotion_valence)
                
                self._rediscovery_count += 1
                
                events.append(MemoryEvent(
                    event_type=MemoryEventType.REDISCOVERED,
                    timestamp=current_time,
                    memory=memory,
                    joy_bonus=min(joy_bonus, 1.0),
                    metadata={
                        "similarity": combined_sim,
                        "forgotten_duration": current_time - forgotten_time,
                    },
                ))
            else:
                remaining_forgotten.append((memory, forgotten_time))
        
        self._forgotten_pool = remaining_forgotten
        return events
    
    def get_memories(self) -> list[MemoryItem]:
        """Get all non-forgotten episodic memories."""
        return self._memories.copy()
    
    def get_forgotten_pool(self) -> list[tuple[MemoryItem, float]]:
        """Get forgotten memories (for debugging/analysis)."""
        return self._forgotten_pool.copy()
    
    def count_forgotten(self) -> int:
        """Total number of items ever forgotten."""
        return self._total_forgotten
    
    def count_rediscoveries(self) -> int:
        """Total rediscovery events."""
        return self._rediscovery_count


# ---------------------------------------------------------------------------
# Implicit Memory
# ---------------------------------------------------------------------------

class ImplicitMemory:
    """Abstract statistical knowledge extracted from forgotten memories.
    
    Implicit memory represents deep knowledge that can't be consciously recalled.
    It's extracted from fully-decayed episodic memories and influences behavior
    through biases and patterns.
    """
    
    def __init__(self):
        """Initialize implicit memory."""
        self._patterns: dict[str, float] = {}  # tag -> aggregate bias weight
        self._pattern_count = 0
    
    def form_from_episodic(self, memories: list[MemoryItem]) -> None:
        """Extract patterns from episodic memories.
        
        High-emotion memories contribute more strongly to implicit patterns.
        
        Args:
            memories: Fully-decayed episodic memories to abstract from
        """
        for memory in memories:
            weight = memory.emotion_intensity * (1.0 + 0.5 * abs(memory.emotion_valence))
            
            for tag in memory.tags:
                if tag not in self._patterns:
                    self._patterns[tag] = 0.0
                self._patterns[tag] += weight
                self._pattern_count += 1
    
    def get_bias(self, tag: str) -> float:
        """Get implicit bias weight for a tag.
        
        Higher values indicate stronger implicit association.
        
        Args:
            tag: Tag to query
        
        Returns:
            Bias weight (0.0-1.0+)
        """
        if not self._patterns:
            return 0.0
        total = sum(self._patterns.values())
        return self._patterns.get(tag, 0.0) / total if total > 0 else 0.0
    
    def get_all_patterns(self) -> dict[str, float]:
        """Get all implicit patterns."""
        return self._patterns.copy()
    
    def count_patterns(self) -> int:
        """Number of implicit patterns."""
        return self._pattern_count


# ---------------------------------------------------------------------------
# Main Memory Hierarchy
# ---------------------------------------------------------------------------

class MemoryHierarchy:
    """Three-layer memory system with forgetting, rediscovery, and implicit learning.
    
    Implements:
    - Layer 1: WorkingMemory (capacity-limited, immediate access)
    - Layer 2: EpisodicMemory (time-decay, forgetting, rediscovery)
    - Layer 3: ImplicitMemory (abstract patterns, unconscious biases)
    """
    
    def __init__(self, config: MemoryConfig):
        """Initialize the complete memory hierarchy.
        
        Args:
            config: MemoryConfig with all parameters
        """
        self.config = config
        self.working = WorkingMemory(capacity=config.working_capacity)
        self.episodic = EpisodicMemory(
            decay_rate=config.decay_rate,
            retention_threshold=config.retention_threshold,
            emotion_retention_boost=config.emotion_retention_boost,
        )
        self.implicit = ImplicitMemory()
        
        self._events: list[MemoryEvent] = []
        self._current_time = time.time()
    
    def experience(
        self,
        content: str,
        emotion_intensity: float,
        emotion_valence: float,
        source_id: str,
        tags: list[str] | None = None,
    ) -> MemoryEvent:
        """Process a new experience through the memory system.
        
        The experience flows: working memory → episodic (if evicted) → forgotten
        
        Args:
            content: Experience content
            emotion_intensity: How emotionally vivid (0.0-1.0)
            emotion_valence: Emotional tone (-1.0 to 1.0)
            source_id: Who/what caused this experience
            tags: Optional categorical labels
        
        Returns:
            MemoryEvent describing what happened
        """
        if tags is None:
            tags = []
        
        item = MemoryItem(
            content=content,
            timestamp=self._current_time,
            emotion_intensity=max(0.0, min(1.0, emotion_intensity)),
            emotion_valence=max(-1.0, min(1.0, emotion_valence)),
            source_id=source_id,
            tags=tags,
        )
        
        # Add to working memory
        evicted = self.working.add(item)
        
        event = MemoryEvent(
            event_type=MemoryEventType.STORED,
            timestamp=self._current_time,
            memory=item,
        )
        
        # If something was evicted, store it in episodic memory
        if evicted is not None:
            self.episodic.store(evicted)
            event.metadata["evicted"] = evicted.source_id
        
        self._events.append(event)
        return event
    
    def tick(self, time_delta: float = 1.0) -> list[MemoryEvent]:
        """Advance time and process memory decay.
        
        Args:
            time_delta: Time elapsed (default 1.0 unit)
        
        Returns:
            List of memory events (forgetting, etc.)
        """
        self._current_time += time_delta
        
        # Episodic memory decays
        events = self.episodic.tick(self._current_time)
        self._events.extend(events)
        
        # Extract fully-decayed memories to implicit
        fully_decayed = []
        for memory in self.episodic.get_memories():
            retention = self.episodic.decay_retention(memory, self._current_time)
            if retention < self.config.implicit_threshold:
                fully_decayed.append(memory)
        
        if fully_decayed:
            self.implicit.form_from_episodic(fully_decayed)
        
        return events
    
    def recall(
        self,
        query: str,
        tags: list[str] | None = None,
    ) -> list[tuple[MemoryItem, float]]:
        """Attempt to recall memories related to a query.
        
        Searches both working and episodic memory by similarity.
        Forgotten memories can be rediscovered.
        
        Args:
            query: What to search for
            tags: Optional tags for similarity
        
        Returns:
            List of (MemoryItem, retrieval_cost) tuples, ordered by relevance
        """
        if tags is None:
            tags = []
        
        results: list[tuple[MemoryItem, float]] = []
        
        # Check for rediscovery of forgotten memories
        rediscovery_events = self.episodic.check_rediscovery(
            query,
            tags,
            self._current_time,
            self.config.rediscovery_similarity_threshold,
        )
        self._events.extend(rediscovery_events)
        
        # Search working memory (no cost)
        for item in self.working.get_all():
            sim = _jaccard_similarity(query, item.content)
            if sim > 0.1:  # Only include reasonably similar items
                results.append((item, 0.0))
        
        # Search episodic memory (small cost based on retention)
        for item in self.episodic.get_memories():
            retention = self.episodic.decay_retention(item, self._current_time)
            sim = _jaccard_similarity(query, item.content)
            if sim > 0.1:
                # Retrieval cost is inverse of retention
                retrieval_cost = 1.0 - retention
                results.append((item, retrieval_cost))
        
        # Sort by relevance (higher similarity = lower cost)
        results.sort(key=lambda x: -x[1])  # Note: higher cost = worse
        results.sort(key=lambda x: x[1])
        
        return results
    
    def get_forgetting_score(self) -> ForgettingScore:
        """Calculate the dual forgetting score.
        
        Returns:
            ForgettingScore capturing loss, gain, and individuality contribution
        """
        total_forgotten = self.episodic.count_forgotten()
        rediscovery_count = self.episodic.count_rediscoveries()
        working_count = self.working.count()
        episodic_count = len(self.episodic.get_memories())
        
        # Loss: proportion of memories lost relative to total experienced
        total_experienced = working_count + episodic_count + total_forgotten
        if total_experienced > 0:
            loss = total_forgotten / total_experienced
        else:
            loss = 0.0
        
        # Gain: rediscovery events create opportunities for renewal
        # Also depends on implicit patterns formed
        implicit_patterns = self.implicit.count_patterns()
        if total_forgotten > 0:
            gain = (rediscovery_count / total_forgotten) * 0.5 + (
                min(implicit_patterns, 10) / 10.0 * 0.5
            )
        else:
            gain = 0.0
        
        # Net effect: not simple subtraction
        # Forgetting enables growth; growth is bittersweet
        net_effect = (gain * 0.6) - (loss * 0.4)
        
        # Individuality: forgetting shapes unique personality through:
        # 1. Selective memory (what's retained reflects values)
        # 2. Implicit biases (forgotten experiences shape behavior)
        # 3. Rediscovery paths (personalized patterns of renewal)
        individuality = min(
            1.0,
            (
                (total_forgotten / max(1, total_experienced)) * 0.5 +  # Selective loss
                (implicit_patterns / 20.0) * 0.3 +  # Pattern formation
                (rediscovery_count / max(1, total_forgotten)) * 0.2  # Renewal patterns
            ),
        )
        
        return ForgettingScore(
            loss=max(0.0, min(1.0, loss)),
            gain=max(0.0, min(1.0, gain)),
            net_effect=max(-1.0, min(1.0, net_effect)),
            individuality_contribution=max(0.0, min(1.0, individuality)),
        )
    
    def get_memory_state(self) -> MemoryState:
        """Get current snapshot of memory hierarchy state.
        
        Returns:
            MemoryState with counts and metrics
        """
        return MemoryState(
            working_count=self.working.count(),
            episodic_count=len(self.episodic.get_memories()),
            forgotten_count=self.episodic.count_forgotten(),
            implicit_patterns=self.implicit.count_patterns(),
            rediscovery_count=self.episodic.count_rediscoveries(),
            total_events=len(self._events),
        )
    
    def get_events(self) -> list[MemoryEvent]:
        """Get all recorded memory events."""
        return self._events.copy()
    
    def clear_events(self) -> None:
        """Clear event log (for space management)."""
        self._events.clear()
