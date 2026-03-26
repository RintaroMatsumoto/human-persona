# Creating New HumanPersona Configurations: A Complete Template and Guide

## Introduction

This guide walks you through the process of creating a new persona configuration for the HumanPersonaBase framework. A persona configuration is a JSON file that defines how an AI should behave in text-based communication—including timing, style variation, emotional dynamics, and context awareness.

The HumanPersonaBase framework is **language-agnostic** and **culture-aware**. This means you can create personas for any language and cultural context, provided you understand both the linguistic patterns and cultural communication norms of your target audience.

---

## Part 1: Understanding the Configuration Schema

Before creating a persona, familiarize yourself with the six major sections of a persona configuration:

### 1. **meta** - Persona Identity and Context

The `meta` section stores identifying information about your persona:

- **persona_id**: A kebab-case unique identifier (e.g., `ja_business_formal`, `en_customer_support`, `es_sales`)
- **language**: ISO 639-1 language code (e.g., `ja`, `en`, `es`)
- **context_culture**: Either `"high"` (implicit communication like Japanese), `"low"` (explicit communication like American English), or `"mixed"` (context-dependent)
- **formality_default**: The starting formality level for new conversations (`"formal"`, `"semi_formal"`, or `"casual"`)
- **display_name**: A human-readable name for logging and debugging
- **version**: Semantic versioning for tracking configuration updates

**Key insight**: The `context_culture` field profoundly affects all downstream sections. High-context cultures rely on implicit understanding, so you'll want higher hedge rates, more filler words, and longer lookback windows for context reference. Low-context cultures are more direct and explicit, so hedge rates can be lower.

### 2. **timing** - Response Delays and Platform Awareness

Humans don't respond instantly. The `timing` section configures realistic response delays per platform:

- **platforms**: A dictionary of platform names (e.g., `chat`, `email`, `crowdsourcing`) with `min_delay` and `max_delay` in seconds, plus an optional `typing_indicator` flag
- **active_hours**: When the persona is available to respond (`start`, `end`, `timezone`)
- **night_queue**: If `true`, messages received outside active hours are queued and sent at the next active window
- **message_length_factor**: A multiplier applied to delays based on message length (longer messages = longer "reading" time)

**Example patterns**:
- Chat: 5–45 seconds (low-context) or 60–300 seconds (high-context)
- Email: 1,800–14,400 seconds (30 minutes to 4 hours)
- Crowdsourcing: 120–900 seconds (2–15 minutes)

### 3. **style** - Linguistic Variation

This is where you encode the persona's linguistic "personality." Uniformity is the #1 tell of AI, so vary your language strategically:

- **variation_patterns**: Named pattern categories (e.g., `confirmation`, `empathy`, `hedging`, `transition`) mapped to arrays of template strings. These are randomly selected when generating responses to add natural variation.
- **typo_rate**: Probability of introducing a plausible typo (keep very low, 0.002–0.005)
- **punctuation_variance**: Toggle to vary punctuation style (omit periods, use `...` vs `…`, etc.)
- **sentence_length_variance**: An object with `min_ratio` and `max_ratio` defining how much sentence length should vary relative to the average
- **filler_words**: Language-specific discourse markers (e.g., `["well", "um", "you know"]` for English; `["えっと", "あ", "そうですね"]` for Japanese)
- **emoji_policy**: Frequency of emoji/emoticon usage (`"never"`, `"rare"`, `"moderate"`, `"frequent"`)

**Calibrated values from DPO dataset**:
- Sentence length CV (coefficient of variation): 0.63 for human-like vs. 0.43 for formal AI
- Hedge probability: 0.082 for human-like vs. 0.017 for formal AI
- Self-correction rate: 0.043 per sentence for human-like vs. 0.001 for formal AI

### 4. **emotion** - State Machine for Tone Shifts

Humans' emotional tone shifts throughout a conversation. This section defines emotional states and transitions:

- **initial_state**: The starting emotion for new conversations (e.g., `"polite_distant"`)
- **states**: Named emotional states with behavioral parameters:
  - `formality` (0–1): 0 = very casual, 1 = very formal
  - `warmth` (0–1): 0 = cold/professional, 1 = warm/friendly
  - `verbosity` (0–1): 0 = terse, 1 = verbose
  - `caution` (0–1): 0 = bold/direct, 1 = very cautious/hedging
  - `response_delay_multiplier` (0.5–3.0): Affects timing (tense states get slower replies)
- **transitions**: Rules for state changes based on triggers (e.g., `"turn_count >= 5"`, `"problem_detected"`) with optional probabilities
- **decay_rate**: Rate at which emotional intensity fades toward neutral per turn

**Example state progression**: `polite_distant` → `professional_warm` (after 5 turns) → `trusted_efficient` (after 15 turns)

### 5. **context_reference** - Active Listening

Configure how the persona references previous parts of the conversation:

- **reference_probability**: How often to back-reference a previous message (0–1 scale)
- **reference_templates**: Template strings for back-references, with `{topic}` placeholders
- **max_lookback_turns**: How many previous turns to consider (typically 5–8)

---

## Part 2: Language and Culture Considerations

### High-Context Cultures (e.g., Japanese, Arabic)

High-context cultures communicate implicitly, relying on shared understanding and context. Personas for these cultures should:

- **Longer active hours**: Respect business hours more strictly (9 AM–6 PM is common in Japan)
- **Higher hedging**: 0.06–0.08 hedge probability to soften statements
- **More fillers**: Discourse markers soften directness (`えっと`, `まあ`, `ね`)
- **Longer lookback**: 8–10 previous turns to show deep context awareness
- **Zero emoji**: High-context professionals avoid casual markers
- **Higher typing delays**: Chat delays of 60–300 seconds signal careful consideration
- **Formal default**: Start at `"formal"` or `"semi_formal"`, warm up slowly
- **Acknowledgment phrases**: Cushion phrases (`"かしこまりました"`, `"ご説明ありがとうございます"`) are critical
- **Self-correction**: Even lower rate (0.002–0.005) as corrections can imply uncertainty

Example: Japanese business persona should have strict 9–18 JST hours, never use emoji, and start every response with a confirmation or acknowledgment.

### Low-Context Cultures (e.g., American English, German)

Low-context cultures communicate explicitly and directly. Personas for these should:

- **Extended active hours**: 8 AM–10 PM (or 24/7 for customer support)
- **Moderate hedging**: 0.05–0.07 to maintain approachability without waffling
- **Casual fillers**: `"well"`, `"so"`, `"actually"`, `"basically"` are natural
- **Standard lookback**: 5–8 previous turns suffices
- **Rare emoji**: Use sparingly but not never
- **Shorter delays**: Chat 5–45 seconds shows responsiveness
- **Semi-formal default**: Start friendly and professional
- **Efficient language**: Less cushioning, more direct explanations
- **Self-correction rate**: 0.03–0.05 (higher than high-context, shows human-like thinking)

Example: English customer support should have 8 AM–10 PM EST hours, rare emoji usage, and quick 5–45 second chat response times.

### Mixed Context (e.g., Singapore, Canada)

If your audience spans cultures, use `"mixed"` and create a balanced profile:

- Moderate hedging (0.06)
- Medium lookback (6 turns)
- Occasional emoji (rare)
- Flexible formality (semi_formal default, transitions to casual or formal based on cues)

---

## Part 3: Best Practices and Common Pitfalls

### Best Practices

1. **Start with a reference persona**: Don't create from scratch. Use `ja_business.json` or `en_customer_support.json` as a template and modify only what differs.

2. **Keep variation_patterns plentiful**: For each pattern type, provide at least 3–5 variations. This prevents repetition.

3. **Test the emotion state machine**: Verify that all state transitions are reachable and that the decay_rate feels natural.

4. **Calibrate hedging for your culture**: Use the empirical targets from the DPO dataset as baselines, then adjust ±10% based on your specific domain.

5. **Match timing to platform realities**: Email delays should be hours; live chat should be seconds. Mismatches feel jarring.



7. **Document your choices**: Add comments explaining why you chose specific values (e.g., "High hedge rate due to risk-averse domain").

### Common Pitfalls

1. **Confusing context_culture with formality_default**: A high-context culture can still be casual; a low-context culture can still be formal. They're independent dimensions.

2. **Over-hedging**: Hedge rates >0.10 sound uncertain and undermine credibility. Stay under 0.08 for professional personas.

3. **Under-varying sentence length**: If all sentences are within a narrow range, it screams AI. Ensure min_ratio is <0.25 and max_ratio is >1.5.

4. **Inconsistent emoji usage**: Decide on emoji_policy upfront and stick with it. Sudden emoji use is jarring.



6. **Hardcoding persona IDs**: Use snake_case and make IDs descriptive and portable (e.g., `ja_business_formal` instead of `japanese_assistant_v2`).

7. **Neglecting non-English languages**: If applying this to non-English text, ensure your `variation_patterns` use actual language-native expressions, not direct translations.

---

## Part 4: Skeleton Configuration with Comments

Below is a complete, commented skeleton you can copy and modify:

```json
{
  "meta": {
    "persona_id": "xx_domain_formality",
    "language": "xx",
    "context_culture": "high|low|mixed",
    "formality_default": "formal|semi_formal|casual",
    "display_name": "Human-readable name",
    "version": "0.1.0"
  },

  "timing": {
    "platforms": {
      "chat": {
        "min_delay": 5,
        "max_delay": 45,
        "typing_indicator": true
      },
      "email": {
        "min_delay": 1800,
        "max_delay": 14400
      }
    },
    "active_hours": {
      "start": "08:00",
      "end": "22:00",
      "timezone": "America/New_York"
    },
    "night_queue": true,
    "message_length_factor": 0.8
  },

  "style": {
    "variation_patterns": {
      "greeting": [
        "Variation 1 of greeting",
        "Variation 2 of greeting",
        "Variation 3 of greeting"
      ],
      "confirmation": [
        "Variation 1 of confirmation",
        "Variation 2 of confirmation"
      ],
      "empathy": [
        "Variation 1 of empathy",
        "Variation 2 of empathy"
      ],
      "hedging": [
        "Variation 1 of hedge",
        "Variation 2 of hedge"
      ],
      "transition": [
        "Variation 1 of transition",
        "Variation 2 of transition"
      ]
    },
    "typo_rate": 0.003,
    "punctuation_variance": true,
    "sentence_length_variance": {
      "min_ratio": 0.25,
      "max_ratio": 1.70
    },
    "filler_words": ["filler1", "filler2", "filler3"],
    "emoji_policy": "rare"
  },

  "emotion": {
    "initial_state": "friendly_professional",
    "states": {
      "friendly_professional": {
        "formality": 0.5,
        "warmth": 0.7,
        "verbosity": 0.5,
        "caution": 0.3
      },
      "empathetic": {
        "formality": 0.4,
        "warmth": 0.9,
        "verbosity": 0.6,
        "caution": 0.4
      },
      "tense": {
        "formality": 0.7,
        "warmth": 0.2,
        "verbosity": 0.8,
        "caution": 0.8,
        "response_delay_multiplier": 1.5
      }
    },
    "transitions": [
      {
        "from": "friendly_professional",
        "to": "empathetic",
        "trigger": "negative_sentiment_detected",
        "probability": 0.8
      },
      {
        "from": "empathetic",
        "to": "tense",
        "trigger": "repeated_complaint",
        "probability": 0.9
      },
      {
        "from": "tense",
        "to": "friendly_professional",
        "trigger": "problem_resolved"
      }
    ],
    "decay_rate": 0.08
  },

  "context_reference": {
    "reference_probability": 0.35,
    "reference_templates": [
      "Going back to {topic} you mentioned,",
      "Regarding {topic},",
      "As you noted about {topic},"
    ],
    "max_lookback_turns": 8
  },

  "ambiguity": {
    "hedge_probability": 0.06,
    "approximation_rules": {
      "time_estimates": true,
      "numeric_rounding": true,
      "certainty_downgrade": true
    },
    "self_correction_rate": 0.035
  }
}
```

---

## Part 5: Step-by-Step Creation Workflow

1. **Choose a language and domain**: Decide on the language, cultural context, and primary use case (customer support, sales, consulting, etc.).

2. **Find a similar reference persona**: Look for an existing configuration that matches your language/culture. Copy it as your starting point.

3. **Update meta section**: Rename `persona_id`, set `language`, `context_culture`, and `formality_default`.

4. **Adjust timing**:
   - Research typical business hours for the region/culture
   - Set platform delays appropriate to your domain
   - Adjust `message_length_factor` based on how the persona responds to longer inputs

5. **Populate variation_patterns**:
   - Write 3–5 natural variations for each pattern type
   - Ensure variations are authentic to the language/culture, not machine-translated
   - Test each pattern by imagining it in a real conversation

6. **Define emotion states and transitions**:
   - Name 3–5 emotional states relevant to your use case
   - Set parameter values (0–1 scales) for each state
   - Design transitions that feel natural (e.g., problem detected → tense, problem resolved → grateful)

7. **Configure context reference**:
   - Set `reference_probability` to 0.3–0.4 for professional contexts
   - Write 3–4 reference templates that feel natural in your language
   - Set `max_lookback_turns` to 5–8 depending on domain complexity


9. **Validate against schema**: Run your configuration through the schema validator to ensure all required fields are present and types are correct.

10. **Test in conversations**: Generate sample interactions with your persona and manually evaluate naturalness, cultural appropriateness, and response quality.

---

## Part 6: Example Application

Let's create a Spanish sales persona to illustrate the workflow.

**Step 1–3**: Spanish sales context, low-context culture (Spain is more direct than Japan but more formal than the US), semi-formal default.

**Step 4**: Spanish business hours are typically 9 AM–7 PM CET with a 2-hour lunch break (accommodated via two separate time windows or a single 9–19 window with acknowledgment in comments).

**Step 5**: Spanish variation patterns include:
- Greeting: `"¡Hola! ¿Cómo estás?"`, `"Buenos días, ¿en qué puedo ayudarte?"`, `"¡Bienvenido! Encantado de verte aquí."`
- Confirmation: `"Entendido, así que buscas..."`, `"Perfecto, dejame resumir lo que entiendo..."`
- Empathy: `"Entiendo tu frustración"`, `"Veo que esto es importante para ti"`

**Step 6**: Spanish sales emotions: `friendly_salesman` → `attentive_listener` (after problem is stated) → `eager_closer` (after needs are clear).

And so on through steps 7–10.

---

## Conclusion

Creating a persona configuration is part science (calibrating to empirical targets), part art (choosing language and emotional patterns that feel natural). Use this guide as a systematic process, refer constantly to the schema documentation, and always test with native speakers of your target language before deploying.

Happy persona building!
