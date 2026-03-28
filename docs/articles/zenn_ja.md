---
title: "AIが人間のように振る舞う基底クラスを設計・AGPL-3.0で公開した"
emoji: "🎭"
type: "tech"
topics: ["Python", "AI", "AGPL", "チューリングテスト", "NLP"]
published: false
---

## 背景：AIの人間らしさの「本当のボトルネック」

2024年、Jones & Bergen が PNAS に発表した論文が衝撃的だった。

> GPT-4.5 に「人間らしいペルソナ」を指示したところ、
> **73% の確率で人間と認識された**。実際の人間参加者の認識率を上回った。

つまり、もう「意味を理解しているかどうか」は問題じゃない。
AIが人間とばれる原因は別のところにある:

- **即レス**: 30秒で返すと AI 確定
- **文体の均質性**: 毎回同じパターンの丁寧な文章
- **感情が変わらない**: 3往復目も初回と同じトーン
- **文脈を無視**: 相手の前の発言を参照しない
- **完璧すぎる**: 「3日で完成します」と言い切る不自然さ

これらは**パラ言語的特徴**と呼ばれる。言語理解とは別レイヤーの問題だ。

自分は AI を使ったビジネスコミュニケーションの自動化を試みる中で、この問題に正面からぶつかった。LLM の出力は意味的に正しいが、「人間が書いたっぽくない」。そこで、人間らしさの構造を基底クラスとして設計することにした。

## 設計思想：なぜ「基底クラス」なのか

人間らしいコミュニケーションの「構造」は文化を超えて共通する:
- 返信には時間がかかる
- 感情は会話を通じて変化する
- 前の文脈を参照する
- 対応できない状況では人間に引き継ぐ

変わるのは「表現」だけだ。敬語の使い方、曖昧さの許容度、沈黙の意味——これらは文化依存。

だから OOP の継承モデルで設計した:

```
HumanPersonaBase（基底クラス）← 構造を定義
│
├── JapaneseBusinessPersona      ← 表現を定義（日本語・ハイコンテキスト）
├── EnglishCustomerSupportPersona ← 表現を定義（英語・ローコンテキスト）
└── SpanishSalesPersona           ← 表現を定義（スペイン語）
```

基底クラスは言語にも文化にも依存しない。派生は JSON 設定ファイルだけで作れる。

## コード解説：5つのコンポーネント

### 1. TimingController — 返信速度制御

```python
@dataclass
class TimingController:
    profiles: dict[Platform, TimingProfile]
    active_start: time
    active_end: time
    night_queue: bool = True

    def calculate_delay(self, platform: Platform) -> float:
        profile = self.profiles.get(platform)
        midpoint = (profile.min_seconds + profile.max_seconds) / 2
        spread = (profile.max_seconds - profile.min_seconds) / 4
        delay = random.gauss(midpoint, spread)
        return max(profile.min_seconds, min(delay, profile.max_seconds))
```

正規分布で遅延を生成する。均一分布だと不自然。深夜はキューに入れて翌朝返信する。

### 2. EmotionStateMachine — 感情の時系列変化

```python
class EmotionState(Enum):
    FORMAL   = "formal"     # 初回: 丁寧・慎重
    WARMING  = "warming"    # 打ち解け
    TENSE    = "tense"      # 問題発生
    RELIEVED = "relieved"   # 解決後
    TRUSTED  = "trusted"    # 長期取引

# トリガーは Callable で定義（文字列パースではない）
DEFAULT_TRANSITIONS = [
    Transition(FORMAL, WARMING,
               lambda sm: sm.exchange_count >= 3,
               "3往復後に打ち解ける"),
    Transition(WARMING, TENSE,
               lambda sm: sm._last_event == "problem_detected",
               "問題発生で緊張"),
    # ...
]
```

初回は丁寧に、3往復目から少し砕けて、問題が起きたら慎重になる。この動的変化が人間らしさの核心。

### 3. StyleVariator — 文体揺らぎ

5パターン（確認型・共感型・保留型・転換型・不確実型）をランダムに選択。直近の履歴で重みを減衰させ、同じパターンの連続を防ぐ。

不確実表現の確率的挿入もある。「3日で完成します」ではなく「3日程度かかると思いますが、前後するかもしれません」の方が人間らしい。

### 4. ContextReferencer — 前文脈参照

トピックベースで会話を追跡し、「先ほどの〇〇の件ですが」のような参照が自然に出るように情報を提供する。

## 使い方

```python
from core.base_persona import HumanPersonaBase

# JSON 設定ファイルからロード
persona = HumanPersonaBase.from_config_file("config/ja_business.json")

# メッセージ処理
response = persona.process_message("納期を前倒しできますか？")

# 結果を LLM のプロンプトに注入
context = persona.get_system_prompt_context()
# → {"emotion_state": "warming", "tone": {"formality": 0.6, ...}, ...}
```

`process_message()` はテキスト生成をしない。返信タイミング・文体・感情状態だけを返す。実際のテキスト生成は LLM に委ねる設計。

新しい言語・文化のペルソナは JSON を書くだけで追加できる:

```json
{
  "name": "JapaneseBusiness",
  "language": "ja",
  "culture": { "context_level": 0.8 }
}
```

## 今後の計画

**短期**
- テストスイートの整備（チューリングテスト自動化含む）
- A/Bブラインドテストによる人間評価

**中期**
- 論文化（arXiv 投稿予定）
  - タイトル: "HumanPersonaBase: A Language-Agnostic Framework for Human-like AI Communication in Professional Contexts"
  - 設計原則の理論的妥当性とベンチマーク結果を報告する

**長期**
- コミュニティからのフィードバックを反映した派生クラスの拡充
- 自動ペルソナ生成（対話ログから設定を推論）
- 音声対応（プロソディ・間のモデル化）

## まとめ

AIが人間とばれる原因は「何を言うか」じゃなくて「どう言うか」。
返信速度、文体の揺らぎ、感情の変化、文脈の参照——これらを基底クラスとして設計し、AGPL-3.0で公開した。

リポジトリ: [github.com/RintaroMatsumoto/human-like-ai](https://github.com/RintaroMatsumoto/human-like-ai)

スター・Issue・PR 歓迎。特に英語やスペイン語の派生ペルソナを作ってくれる人を募集中。
