"""
JapaneseFreelancerPersona — A concrete persona implementation for Japanese freelancers.

This module implements a HumanPersonaBase subclass tailored to the communication
patterns of Japanese freelancers (フリーランス) in client interactions.

Japanese freelancers typically:
1. Start with formal keigo (敬語: honorific language) to show respect
2. Gradually warm up as trust builds
3. Respond faster on chat platforms, slower on email (platform awareness)
4. Acknowledge requests thoroughly before committing
5. Escalate on negotiation, legal, or payment-related matters

Configuration:
    Loads from config/ja_freelancer.json (created alongside this module)
    or falls back to config/ja_business.json with freelancer-specific overrides.

Author: Rintaro Matsumoto (RintaroMatsumoto)
License: MIT
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.base_persona import HumanPersonaBase, Message, PersonaResponse, Platform


def load_config(config_path: str | Path) -> dict:
    """Load JSON configuration from file.
    
    Args:
        config_path: Path to JSON config file.
    
    Returns:
        Parsed configuration dictionary.
    
    Raises:
        FileNotFoundError: If config file not found.
        json.JSONDecodeError: If JSON is invalid.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_japanese_topics(message: str) -> list[str]:
    """Extract key topics from Japanese text using simple heuristics.
    
    This is a basic implementation using keyword detection.
    In production, consider using MeCab or Janome for proper tokenization.
    
    Args:
        message: Japanese message text.
    
    Returns:
        List of topic keywords found.
    """
    # Simple Japanese topic markers and keywords
    topic_markers = {
        "プロジェクト": "project",
        "案件": "project",
        "業務": "task",
        "タスク": "task",
        "ファイル": "file",
        "ドキュメント": "document",
        "締め切り": "deadline",
        "納期": "deadline",
        "単価": "rate",
        "報酬": "payment",
        "予算": "budget",
        "修正": "revision",
        "変更": "change",
        "確認": "confirmation",
        "質問": "question",
    }
    
    topics = []
    for jp_term, en_term in topic_markers.items():
        if jp_term in message:
            topics.append(en_term)
    
    return topics


class JapaneseFreelancerPersona(HumanPersonaBase):
    """Concrete persona for Japanese freelancers.
    
    Implements human-like communication for freelancers responding to
    client inquiries, project discussions, and negotiations.
    
    Key behaviors:
        - Starts formal (敬語), warms over time
        - Fast on chat (60–300s), slow on email (1–12 hours)
        - Acknowledges client concerns explicitly
        - Escalates on rate/payment discussions, legal terms, or complaints
        - Uses context references to show active listening
    """
    
    def __init__(self, config_path: str | Path | None = None):
        """Initialize Japanese freelancer persona.
        
        Args:
            config_path: Path to persona config JSON. If None, looks for
                        config/ja_freelancer.json, then config/ja_business.json.
        """
        # Try to load ja_freelancer.json, fall back to ja_business.json
        if config_path is None:
            base_dir = Path(__file__).parent.parent
            freelancer_config = base_dir / "config" / "ja_freelancer.json"
            business_config = base_dir / "config" / "ja_business.json"
            
            if freelancer_config.exists():
                config_path = freelancer_config
            else:
                config_path = business_config
        
        config = load_config(config_path)
        
        # Extract persona_id from config
        persona_id = config.get("meta", {}).get("persona_id", "ja_freelancer_professional")
        
        # Initialize parent with persona_id, config, and platform
        super().__init__(persona_id=persona_id, config=config, platform=Platform.SLACK)
    
    def generate_raw_response(
        self,
        message: str,
        context: list[Message],
    ) -> str:
        """Generate core response content for Japanese freelancer context.
        
        This is a template-based implementation. In real usage, you'd call
        an LLM (Claude, GPT, etc.) here. This demo uses canned responses.
        
        Args:
            message: Incoming user message.
            context: Conversation history.
        
        Returns:
            Raw response text (before style/ambiguity processing).
        """
        # Simple keyword-based response selection
        if any(kw in message for kw in ["単価", "報酬", "値下げ", "予算", "コスト"]):
            return (
                "いただいたご質問についてでございますが、"
                "金額面のお話は重要な項目でございますため、"
                "詳細なお見積もりを改めてお送りさせていただきたく存じます。"
            )
        elif any(kw in message for kw in ["お会い", "対面", "電話", "通話", "Zoom"]):
            return (
                "貴重なお誘いをいただき、ありがとうございます。"
                "オンライン会議でしたら対応させていただけますが、"
                "具体的なご日程をお聞きできますでしょうか。"
            )
        elif any(kw in message for kw in ["修正", "変更", "修正版"]):
            return (
                "ご指摘の点につきましては理解いたしました。"
                "修正版を準備させていただき、"
                "明日中にはお納めできるものと考えております。"
            )
        elif any(kw in message for kw in ["質問", "確認", "教えて"]):
            return (
                "ご質問をいただきありがとうございます。"
                "その点についてでございますが、"
                "以下のようにお考えいただくとよろしいかと存じます。"
            )
        else:
            return (
                "かしこまりました。ご指示をいただき、"
                "ありがとうございます。"
            )
    
    def extract_topics(self, message: str) -> list[str]:
        """Extract topics from a Japanese message.
        
        Args:
            message: Japanese message text.
        
        Returns:
            List of identified topics.
        """
        return extract_japanese_topics(message)
    
    def post_process(self, response: str) -> str:
        """Apply Japanese-specific post-processing.
        
        Currently a pass-through, but can add:
        - Character width normalization (全角 ↔ 半角)
        - Punctuation style enforcement
        - Ruby annotation for difficult kanji
        
        Args:
            response: Processed response text.
        
        Returns:
            Final response text.
        """
        return response


def demo():
    """Run a simple demo to showcase the persona initialization.
    
    This demonstrates loading and initializing the persona.
    """
    print("=" * 70)
    print("Japanese Freelancer Persona - Initialization Demo")
    print("=" * 70)
    print()
    
    try:
        # Initialize persona
        persona = JapaneseFreelancerPersona()
        
        print(f"[OK] Persona initialized successfully")
        print(f"  ID: {persona.persona_id}")
        print(f"  Language: {persona.language}")
        print(f"  Culture context: {persona.culture_context}")
        print()
        
        # Show configuration summary
        print("Configuration loaded:")
        # Try to access config - try both possible attribute names
        config_attr = getattr(persona, '_config', None) or getattr(persona, 'config', None)
        if config_attr:
            timing_config = config_attr.get("timing", {}).get("platforms", {})
            if "slack" in timing_config:
                slack_timing = timing_config["slack"]
                print(f"  Slack platform delays:")
                print(f"    Min: {slack_timing.get('min_delay', '?')}s")
                print(f"    Max: {slack_timing.get('max_delay', '?')}s")
            else:
                print(f"  Available platforms: {list(timing_config.keys())}")
        else:
            print("  (Config not directly accessible)")
        print()
        
        # Demonstrate response generation
        print("Sample responses for typical freelancer queries:")
        print()
        
        test_queries = [
            "こんにちは。プロジェクトについてご相談したいのですが。",
            "単価についても相談してもいいですか？",
            "ドキュメントを見直して、修正版をお願いしたいです。",
            "来週の木曜日に対面でお会いできますか？",
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"Query {i}: {query}")
            # Call generate_raw_response directly (no full pipeline)
            response_text = persona.generate_raw_response(query, [])
            print(f"Response: {response_text}")
            print()
        
        print("-" * 70)
        print("Demo completed successfully!")
        print()
        
    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo()
