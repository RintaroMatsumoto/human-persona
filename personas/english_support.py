"""
EnglishSupportPersona — Concrete implementation of HumanPersonaBase for English customer support.

This module implements a customer support agent persona that exhibits:
  - Friendly and empathetic communication patterns
  - Quick response times optimized for live chat interactions
  - Solution-oriented emotional state transitions
  - Context-aware conversation flow with natural references to prior issues

The persona loads its configuration from config/en_customer_support.json and
applies all core human-likeness transformations (timing, style, emotion, etc.).

Author: Rintaro Matsumoto (RintaroMatsumoto)
License: MIT
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..core.base_persona import (
    HumanPersonaBase,
    Platform,
    PersonaResponse,
    Message,
    load_config,
)


class EnglishSupportPersona(HumanPersonaBase):
    """English customer support agent extending HumanPersonaBase.

    This concrete implementation specializes in customer support scenarios,
    providing empathetic responses with quick turnaround times.

    Key behaviors:
      - Greeting variations that feel warm and approachable
      - Empathy patterns triggered by negative sentiment
      - Solution-focused transitions that move conversations toward resolution
      - Chat-optimized timing (5-45 seconds) with typing indicators
      - Rare emoji usage (professional but approachable)

    Usage:
        config = load_config("config/en_customer_support.json")
        persona = EnglishSupportPersona(config, platform=Platform.CHAT)
        response = persona.respond("I've been having issues with my account.")
        print(response.content)
    """

    def __init__(
        self,
        config: dict[str, Any],
        platform: Platform = Platform.CHAT,
    ):
        """Initialize the English support persona.

        Args:
            config: Parsed persona configuration dictionary from JSON.
            platform: Communication platform (default: Platform.CHAT).
        """
        super().__init__(config, platform)
        self._support_stats = {
            "complaints_count": 0,
            "issues_resolved": 0,
        }

    # -- Overridden Methods --------------------------------------------------

    def generate_raw_response(
        self,
        message: str,
        context: list[Message],
    ) -> str:
        """Generate raw response content for a customer support query.

        This is a simple template-based implementation for demonstration.
        In production, this would call an LLM or retrieve from a knowledge base.

        Args:
            message: The incoming customer message.
            context: Conversation history (previous turns).

        Returns:
            Raw response text (before style variation and timing).
        """
        # Simple heuristic-based response generation for demo purposes.
        # In production, replace with LLM API call or knowledge base retrieval.

        message_lower = message.lower()

        # Detect complaint indicators
        if any(word in message_lower for word in ["frustrated", "angry", "disappointed", "upset", "broken", "doesn't work"]):
            self._support_stats["complaints_count"] += 1
            return "I'm really sorry to hear you're experiencing that issue. Let me help you get this sorted out as quickly as possible. Can you tell me a bit more about what's happening?"

        # Detect resolution indicators
        if any(word in message_lower for word in ["thank you", "thanks", "appreciate", "solved", "fixed", "working now"]):
            self._support_stats["issues_resolved"] += 1
            return "That's fantastic to hear! I'm so glad we could get that resolved for you. Is there anything else I can help with today?"

        # Detect technical issues
        if any(word in message_lower for word in ["error", "bug", "crash", "not working", "slow", "can't access"]):
            return "I understand how annoying technical issues can be. Let me walk through some troubleshooting steps with you. First, can you tell me what error message you're seeing, if any?"

        # Detect account/billing issues
        if any(word in message_lower for word in ["charge", "billing", "payment", "account", "subscription", "cancel"]):
            return "I can definitely help with that. Account and billing matters are important, so let me make sure we handle this correctly. Could you provide a few more details about what you need?"

        # Default friendly response
        return "Thanks for reaching out! I'd be happy to help. Could you tell me a bit more about what you're looking for?"

    def extract_topics(self, message: str) -> list[str]:
        """Extract topic keywords from a customer message.

        Args:
            message: The customer's message text.

        Returns:
            List of topic keywords detected in the message.
        """
        topics = []
        topic_keywords = {
            "billing": ["charge", "payment", "bill", "invoice", "subscription"],
            "account": ["account", "login", "password", "profile", "settings"],
            "technical": ["error", "bug", "crash", "not working", "slow", "lag"],
            "shipping": ["ship", "order", "delivery", "tracking", "arrived"],
            "refund": ["refund", "return", "money back", "cancel order"],
            "complaint": ["frustrated", "angry", "upset", "disappointed", "poor service"],
        }

        message_lower = message.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)

        return topics if topics else ["general_inquiry"]

    def generate_response_timing(
        self,
        message_length: int,
        emotion_state: str,
    ) -> float:
        """Calculate response delay in seconds based on message and emotion.

        Customer support should respond quickly, but with slight variation
        based on emotional intensity and message complexity.

        Args:
            message_length: Character count of incoming message.
            emotion_state: Current emotional state (e.g., "empathetic").

        Returns:
            Delay in seconds before responding.
        """
        # Get base timing from config
        chat_config = self._config.get("timing", {}).get("platforms", {}).get("chat", {})
        min_delay = chat_config.get("min_delay", 5)
        max_delay = chat_config.get("max_delay", 45)

        # Calculate delay based on message length
        message_factor = self._config.get("timing", {}).get("message_length_factor", 0.8)
        length_adjustment = (message_length / 100) * message_factor

        # Get emotion multiplier (apologetic mode is slower)
        emotion_state_config = (
            self._config.get("emotion", {})
            .get("states", {})
            .get(emotion_state, {})
        )
        emotion_multiplier = emotion_state_config.get("response_delay_multiplier", 1.0)

        # Calculate final delay
        base_delay = (min_delay + max_delay) / 2
        final_delay = base_delay + length_adjustment
        final_delay = final_delay * emotion_multiplier

        # Clamp to configured min/max
        return max(min_delay, min(final_delay, max_delay * 1.5))

    def apply_style_variation(
        self,
        response_text: str,
        style_config: dict[str, Any],
    ) -> str:
        """Apply style variation to raw response (punctuation, tone, etc.).

        This includes varying sentence structure, adding filler words,
        introducing minor typos, and injecting conversational markers.

        Args:
            response_text: The raw response before style variation.
            style_config: Style configuration from the persona config.

        Returns:
            Stylistically varied response text.
        """
        import random

        # Add filler words occasionally
        filler_words = style_config.get("filler_words", [])
        if filler_words and random.random() < 0.15:
            filler = random.choice(filler_words)
            # Insert filler at a natural break point
            sentences = response_text.split(".")
            if len(sentences) > 1:
                insert_pos = random.randint(0, len(sentences) - 2)
                sentences[insert_pos] = f"{sentences[insert_pos]}. {filler.capitalize()},"
                response_text = ".".join(sentences)

        # Apply punctuation variance
        if style_config.get("punctuation_variance", True) and random.random() < 0.1:
            # Occasionally replace period with ellipsis at end of sentence
            if response_text.endswith("."):
                response_text = response_text[:-1] + "..."

        # Apply rare typo
        typo_rate = style_config.get("typo_rate", 0.003)
        if random.random() < typo_rate * len(response_text) / 100:
            # Simple typo: swap two adjacent characters in a random word
            words = response_text.split()
            if words:
                word_idx = random.randint(0, len(words) - 1)
                word = list(words[word_idx])
                if len(word) > 1:
                    swap_pos = random.randint(0, len(word) - 2)
                    word[swap_pos], word[swap_pos + 1] = word[swap_pos + 1], word[swap_pos]
                    words[word_idx] = "".join(word)
                response_text = " ".join(words)

        return response_text

    def get_emotion_state(self, message: str, context: list[Message]) -> str:
        """Determine appropriate emotional state based on conversation context.

        Support conversations follow a predictable emotional arc:
        - Start friendly_professional
        - Shift to empathetic on negative signals
        - Transition to troubleshooting for technical issues
        - Move to apologetic for repeated complaints

        Args:
            message: The current user message.
            context: Conversation history.

        Returns:
            The appropriate emotion state key (e.g., "empathetic").
        """
        message_lower = message.lower()

        # Count complaints and issues in recent history
        complaint_keywords = ["frustrated", "angry", "upset", "disappointing", "broken", "doesn't work", "problem"]
        recent_complaints = sum(
            1 for msg in context[-5:] if msg.role == "user"
            and any(kw in msg.content.lower() for kw in complaint_keywords)
        )

        # Repeated complaints
        if recent_complaints >= 1:
            return "apologetic"

        # Technical troubleshooting mode
        tech_keywords = ["error", "bug", "crash", "slow", "lag", "not working"]
        if any(kw in message_lower for kw in tech_keywords):
            return "troubleshooting"

        # Empathy mode for negative sentiment
        negative_keywords = ["frustrated", "disappointed", "upset", "angry"]
        if any(kw in message_lower for kw in negative_keywords):
            return "empathetic"

        # Celebratory if issue resolved
        positive_keywords = ["thank you", "thanks", "appreciate", "solved", "fixed", "working now"]
        if any(kw in message_lower for kw in positive_keywords):
            return "celebratory"

        # Default friendly
        return self._config.get("emotion", {}).get("initial_state", "friendly_professional")

    def respond(self, user_message: str) -> PersonaResponse:
        """Generate a complete persona response to a user message.

        This orchestrates the full pipeline:
        1. Add user message to history
        2. Determine emotion state
        3. Generate raw response
        4. Apply style variation
        5. Insert context references
        6. Calculate timing

        Args:
            user_message: The incoming customer message.

        Returns:
            PersonaResponse with content, timing, and emotion state.
        """
        # Add to conversation history
        self._conversation.append(
            Message(role="user", content=user_message)
        )
        self._turn_count += 1

        # Determine emotion state
        emotion_state = self.get_emotion_state(user_message, self._conversation[:-1])

        # Generate raw response
        raw_response = self.generate_raw_response(
            user_message,
            self._conversation[:-1],
        )

        # Apply style variation
        style_config = self._config.get("style", {})
        stylized_response = self.apply_style_variation(raw_response, style_config)

        # Apply context reference if appropriate
        context_config = self._config.get("context_reference", {})
        if (
            len(self._conversation) > 2
            and hasattr(self, '_style')
            and hasattr(self._style, 'insert_context_reference')
        ):
            # Optional: integrate context references via the StyleVariator
            pass

        # Calculate timing
        timing = self.generate_response_timing(len(user_message), emotion_state)

        # Create response
        response = PersonaResponse(
            content=stylized_response,
            delay_seconds=timing,
            emotion_state=emotion_state,
        )

        # Add to conversation history
        self._conversation.append(
            Message(role="persona", content=stylized_response)
        )

        return response


# ---------------------------------------------------------------------------
# Demo and Testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    """Demo showing EnglishSupportPersona in action."""

    # Load configuration
    config_path = Path(__file__).parent.parent / "config" / "en_customer_support.json"
    config = load_config(config_path)

    # Initialize persona
    persona = EnglishSupportPersona(config, platform=Platform.CHAT)

    print("=" * 70)
    print("English Support Persona Demo")
    print("=" * 70)
    print(f"\nPersona ID: {persona.persona_id}")
    print(f"Language: {persona.language}")
    print(f"Initial Emotion: {persona.current_emotion}")
    print("\n" + "-" * 70)

    # Simulate a customer support conversation
    test_messages = [
        "Hi, I'm having trouble logging into my account.",
        "I've tried resetting my password three times and it still doesn't work!",
        "This is ridiculous. I've been a customer for years and you're treating me terribly.",
    ]

    for user_msg in test_messages:
        print(f"\nUser: {user_msg}")

        response = persona.respond(user_msg)

        print(f"\nPersona Response:")
        print(f"  Content: {response.content}")
        print(f"  Delay: {response.delay_seconds:.1f}s")
        print(f"  Emotion: {response.emotion_state}")
        print("-" * 70)

    print(f"\nConversation Summary:")
    print(f"  Total Turns: {persona.turn_count}")
    print(f"  Complaints Detected: {persona._support_stats['complaints_count']}")
    print(f"  Issues Resolved: {persona._support_stats['issues_resolved']}")
