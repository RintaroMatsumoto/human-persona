# human-persona — 日本語ドキュメント

**AIが人間のように振る舞うための、言語・文化非依存フレームワーク**

## 概要

human-persona は、人間らしいコミュニケーションの「構造」を5つの独立したコンポーネントに分解し、再利用可能な基底クラス `HumanPersonaBase` として提供します。テキスト生成自体は行わず、LLM の応答を人間らしくするための**振る舞いレイヤー**（タイミング・文体・感情・文脈・安全性）を担います。

## なぜこのフレームワークが必要か

Jones & Bergen (2024) の研究で、GPT-4.5 はペルソナを付与された場合 **73% の確率で人間と認識された**ことが示されました。AI の人間らしさのボトルネックは「意味理解」からパラ言語的特徴にシフトしています:

- **返信速度**: 即座の返信は AI らしさを示唆する
- **文体の均質性**: 毎回同じ表現パターンは不自然
- **感情の静的さ**: 会話を通じた感情変化がない
- **文脈の無視**: 前の発言を参照しない

human-persona はこれらの課題を体系的に解決します。

## アーキテクチャ

```
HumanPersonaBase（基底クラス）
│
├── TimingController        — 返信速度制御
│     プラットフォーム別（chat/email/crowdsourcing）
│     正規分布ベースの自然な遅延、活動時間外キューイング
│
├── StyleVariator           — 文体揺らぎ生成
│     5パターン（確認/共感/保留/転換/不確実）
│     直近履歴の重み減衰で同一パターンの連続を抑制
│
├── EmotionStateMachine     — 感情状態モデル
│     FORMAL → WARMING → TENSE → RELIEVED → TRUSTED
│     Callable ベースのトリガーで遷移条件を定義
│
├── ContextReferencer       — 前文脈参照
│     トピックベースの会話追跡、参照すべきかの判定
│
└── EscalationDetector      — エスカレーション判定
      キーワードマッチング + 雑談長期化検知
      COMPLAINT/NEGOTIATION 時は EmotionStateMachine に連鎖発火
```

## クイックスタート

```python
from core.base_persona import HumanPersonaBase

# 設定ファイルからペルソナを生成
persona = HumanPersonaBase.from_config_file("config/ja_business.json")

# メッセージを処理
response = persona.process_message(
    "納期について相談させてください",
    topics=["deadline", "consultation"]
)

print(f"遅延: {response.delay_seconds:.0f}秒")
print(f"感情: {response.emotion_state.value}")   # formal → warming → ...
print(f"文体: {response.style_used.value}")       # confirmation, empathy, ...

# エスカレーション判定
if response.escalation and response.escalation.should_escalate:
    print(f"人間に引き継ぎ: {response.escalation.reason.value}")

# LLM システムプロンプトに注入
context = persona.get_system_prompt_context()
```

## 派生ペルソナの作り方

### 1. JSON 設定ファイルを作成

`config/schema.json` に準拠した JSON を作成します:

```json
{
  "name": "JapaneseBusiness",
  "language": "ja",
  "culture": {
    "context_level": 0.8,
    "formality_default": 0.7,
    "indirect_expression_rate": 0.6,
    "silence_tolerance": 0.7
  },
  "platform": "crowdsourcing_message",
  "timing": {
    "platform_timing": {
      "crowdsourcing_message": { "min_sec": 300, "max_sec": 900 },
      "active_hours": "09:00-21:00",
      "night_queue": true
    }
  },
  "style": {
    "uncertainty_rate": 0.2,
    "style_patterns": [
      {
        "type": "confirmation",
        "templates": ["〇〇ということですよね？", "〇〇で間違いないでしょうか？"],
        "weight": 1.2
      },
      {
        "type": "empathy",
        "templates": ["それは大変でしたね", "お気持ちはよく分かります"]
      },
      {
        "type": "uncertain",
        "templates": ["たぶん〇〇かと思います", "おそらく〇〇ではないでしょうか"]
      }
    ]
  },
  "escalation": {
    "max_chat_turns": 3,
    "escalation_rules": [
      { "reason": "negotiation", "keywords": ["単価", "報酬", "値下げ"], "priority": 1 },
      { "reason": "call_request", "keywords": ["電話", "通話", "Zoom"], "priority": 2 },
      { "reason": "complaint", "keywords": ["不満", "クレーム", "おかしい"], "priority": 1 }
    ]
  }
}
```

### 2. ロードして使う

```python
persona = HumanPersonaBase.from_config_file("config/ja_business.json")
```

### 3. （オプション）Python サブクラスで拡張

```python
from core.base_persona import HumanPersonaBase, PersonaResponse

class JapaneseBusinessPersona(HumanPersonaBase):
    def process_message(self, user_message: str, topics=None) -> PersonaResponse:
        # 日本語固有の前処理（敬語レベル判定など）
        response = super().process_message(user_message, topics)
        # 日本語固有の後処理
        return response
```

## コンポーネント詳細

各コンポーネントの設計判断と根拠は [docs/design.md](../design.md) を参照してください。

## 倫理ガイドライン

詳細は [docs/ethics.md](../ethics.md) を参照してください。

**正当な用途**: カスタマーサポート効率化、営業、語学学習・会話練習パートナー、AIエージェントのUX研究

**禁止用途**: 詐欺・なりすまし、感情的搾取、選挙介入、ハラスメント、プラットフォーム TOS 違反

## 貢献方法

[CONTRIBUTING.md](../../CONTRIBUTING.md) を参照してください。

## 理論的基盤

- Jones & Bergen (2024). "A Turing test of whether AI chatbots are behaviorally similar to humans." *PNAS*.
- Hall, E.T. (1976). *Beyond Culture*. Anchor Books.
- Nguyen et al. (2016). "Computational Sociolinguistics: A Survey." *Computational Linguistics*.
- Mitchell, M. (2025). "The Turing Test and our shifting conceptions of intelligence." *Science*.

## ライセンス

MIT License

## 著者

Rintaro Matsumoto ([@RintaroMatsumoto](https://github.com/RintaroMatsumoto))
