---
name: human-persona
description: A language-agnostic framework for human-like AI communication. Provides timing control, style variation, emotion state management, context referencing, and escalation detection as a composable base class.
version: 0.1.0
author: The Author (RintaroMatsumoto)
license: MIT
tags:
  - persona
  - human-like
  - communication
  - agent-skill
  - turing-test
---

# human-persona

AIが人間のように振る舞うための汎用Agent Skill。
言語・文化・属性に依存しない基底クラス `HumanPersonaBase` を提供する。

## 使い方

### 1. 基底クラスを直接使用する

```python
from core.base_persona import HumanPersonaBase

persona = HumanPersonaBase.from_config_file("config/ja.json")
response = persona.process_message("納期について相談させてください")

# response.delay_seconds  → 返信までの遅延
# response.emotion_state  → 現在の感情状態
# response.style_used     → 選択された文体パターン
# response.escalation     → エスカレーション判定
# response.metadata       → LLMプロンプトに注入する文脈情報
```

### 2. 設定ファイルで派生ペルソナを定義する

`config/schema.json` に準拠したJSONファイルを作成し、
言語・文化・タイミングパラメータを外部定義する。

```json
{
  "name": "JapaneseFreelancer",
  "language": "ja",
  "culture": {
    "context_level": 0.8,
    "formality_default": 0.7,
    "indirect_expression_rate": 0.6
  }
}
```

### 3. LLMシステムプロンプトに統合する

```python
context = persona.get_system_prompt_context()
# → {"emotion_state": "warming", "tone": {...}, "recent_topics": [...]}
# この情報をLLMのシステムプロンプトに注入して応答を生成させる
```

## コンポーネント

| コンポーネント | 役割 |
|---|---|
| `TimingController` | プラットフォーム別の返信速度制御 |
| `StyleVariator` | 文体揺らぎの生成（均質性の回避） |
| `EmotionStateMachine` | 感情の時系列変化モデル |
| `ContextReferencer` | 前文脈の参照・一貫性維持 |
| `EscalationDetector` | 人間への引き継ぎ判定 |

## 設計原則

- **基底クラスは文化にも言語にも依存しない**
- 言語・人種・性別・年齢はすべて派生クラス（設定ファイル）で定義する
- チューリングテスト研究を理論的基盤とする
- 倫理的使用を前提とする（詐欺・なりすまし禁止）
