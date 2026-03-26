# 設計原則とアーキテクチャ

## 1. 基底クラス設計の思想

### なぜ言語・文化非依存なのか

人間らしいコミュニケーションの「構造」は文化を超えて共通する。
返信に時間がかかること、感情が変化すること、文脈を参照すること——
これらは日本語でもスペイン語でも変わらない。

変わるのは「表現」である。敬語の使い方、曖昧さの許容度、
沈黙の意味——これらは文化に依存する。

この観察から、設計は2層に分離される:

```
基底クラス (HumanPersonaBase)
  → 構造を定義する: いつ返信するか、感情がどう遷移するか

派生クラス (設定ファイル + サブクラス)
  → 表現を定義する: どの言語で、どんなトーンで、
    どの程度曖昧に話すか
```

この分離により:
- 新しい言語・文化への対応は設定ファイルの追加だけで可能
- 基底クラスの改善はすべての派生クラスに自動的に波及する
- 研究成果（基底クラス）と実用成果（派生クラス）を独立に評価できる

### OOP としての設計判断

Python の dataclass を採用した理由:
- **透明性**: すべての状態が明示的に定義される
- **テスト容易性**: 各コンポーネントを独立にテストできる
- **設定駆動**: `from_config()` パターンで JSON からインスタンス化可能
- **継承よりコンポジション**: 各コンポーネントは独立した dataclass として設計し、HumanPersonaBase がそれらを組み合わせる

---

## 2. 各コンポーネントの責務と設計判断

### TimingController — 返信速度制御

**責務**: プラットフォームと時間帯に応じた自然な返信遅延を計算する。

**設計判断**:
- 正規分布ベースの遅延生成（均一分布は不自然）
- プラットフォーム別のプロファイル（chat: 秒単位, email: 時間単位）
- 活動時間外のキューイング（深夜の即レスは AI を示唆する）

**なぜこのコンポーネントが独立しているか**:
返信速度の制御は他のすべてのコンポーネントから独立している。
感情状態が変わっても返信速度の基本パラメータは変わらない
（慌てて即レスするのは別の問題で、将来の拡張ポイント）。

### StyleVariator — 文体揺らぎ生成

**責務**: 同じ意味を毎回異なる表現で伝えるための文体パターン選択。

**設計判断**:
- 5 パターン（確認/共感/保留/転換/不確実）は会話分析の知見に基づく
- 直近履歴の重み減衰（同じパターンの連続を抑制）
- 不確実表現の確率的挿入（過度な確実性は AI らしさの原因）

**なぜキーワードではなくパターン種別か**:
キーワードマッチングは言語依存になる。
「パターン種別」として抽象化することで、
具体的なテンプレートは派生クラスに委ねられる。

### EmotionStateMachine — 感情状態モデル

**責務**: 会話を通じた感情の動的変化を再現する。

**設計判断**:
- 5 状態（FORMAL → WARMING → TENSE → RELIEVED → TRUSTED）は
  ビジネスコミュニケーションの典型的な感情フローをモデル化
- トリガーは `Callable[[EmotionStateMachine], bool]` で定義
  （文字列パースは脆弱なため却下）
- `_last_event` パターンでイベント名と閾値条件の両方を統一的に扱う

**なぜ状態機械か**:
感情をスカラー値（0.0-1.0）でモデル化する方法もあるが、
状態機械は「現在どのフェーズにいるか」を明示的に表現でき、
デバッグ・テスト・説明が容易である。

### ContextReferencer — 前文脈参照

**責務**: 会話履歴を追跡し、前文脈参照のための情報を提供する。

**設計判断**:
- トピックベースの追跡（全文保持は不要でコストが高い）
- `should_reference_previous()` で参照すべきかの判定を提供
- 基底クラスはテンプレートを持たない（言語依存のため）

---

## 3. 派生クラスの作り方

### ステップ 1: 設定ファイルを作成する

`config/schema.json` に準拠した JSON を作成する:

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
        "templates": [
          "〇〇ということですよね？",
          "〇〇で間違いないでしょうか？",
          "〇〇という認識でよろしいですか？"
        ],
        "weight": 1.2
      },
      {
        "type": "empathy",
        "templates": [
          "それは大変でしたね",
          "お気持ちはよく分かります",
          "ご不便をおかけして申し訳ありません"
        ]
      },
      {
        "type": "uncertain",
        "templates": [
          "たぶん〇〇かと思います",
          "おそらく〇〇ではないでしょうか",
          "〇〇かもしれません"
        ]
      }
    ]
  }
}
```

### ステップ 2: ロードして使う

```python
from core.base_persona import HumanPersonaBase

persona = HumanPersonaBase.from_config_file("config/ja_business.json")
response = persona.process_message("納期を前倒しできますか？")
```

### ステップ 3: （オプション）サブクラスで拡張する

設定ファイルだけでは不十分な場合、Python でサブクラスを作成する:

```python
from core.base_persona import HumanPersonaBase, PersonaResponse

class JapaneseBusinessPersona(HumanPersonaBase):
    """日本語ビジネス向け拡張ペルソナ."""

    def process_message(self, user_message: str, topics=None) -> PersonaResponse:
        # 日本語固有の前処理
        response = super().process_message(user_message, topics)
        # 日本語固有の後処理
        return response
```

---

## 4. 今後の拡張ポイント

### 短期（v0.2）
- **感情状態による返信速度変動**: TENSE 時は返信が速くなる（慎重に確認する）
- **雑談分類器**: `track_chat()` の `is_chitchat` を自動判定する
- **problem_resolved の自動発火**: 解決パターンの検知

### 中期（v0.3-0.5）
- **学習ループ**: 対話ログから文体パターンを自動抽出
- **A/B テスト基盤**: 異なるペルソナ設定の効果を定量比較
- **マルチモーダル対応**: 音声のプロソディ（抑揚・間）のモデル化

### 長期（v1.0）
- **自動ペルソナ生成**: 対話ログからペルソナ設定を自動推論
- **文化適応モデル**: context_level を動的に調整する機構
- **倫理的制約の形式検証**: ペルソナ設定が倫理ガイドラインに違反しないことを静的に検証
