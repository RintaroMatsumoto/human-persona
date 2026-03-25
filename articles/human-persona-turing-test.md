---
title: "AIを人間と区別できなくした話：LLMジャッジで測るチューリングテスト実装"
emoji: "🤖"
type: "tech"
topics: ["ai", "llm", "python", "chatbot", "oss"]
published: true
---

## AIが「人間らしい」とはどういうことか

2024年、UC San Diegoの研究チームがこんな結果を発表した。

> GPT-4.5に「人間らしいペルソナを採用せよ」と指示すると、73%の確率で人間と認識された。実際の人間参加者の認識率を上回る。

ボトルネックはもはや「意味理解」ではなく、**パラ言語的特徴・感情表現・会話ペルソナ**にシフトしている。つまりペルソナ設計次第でAIは人間以上に人間らしくなれる。

この研究を受けて、「じゃあ体系的に設計できるはずだ」と思って作ったのが [human-persona](https://github.com/RintaroMatsumoto/human-persona) というOSSプロジェクトだ。

## 設計思想：基底クラスとしてのペルソナ

言語・文化・年齢に依存しない「人間らしいコミュニケーションの普遍的構造」を基底クラスとして設計し、言語や文化は派生クラス（configファイル）で定義する。OOP設計と同じ考え方だ。

```
HumanPersonaBase          ← このプロジェクトの研究対象
├── JapaneseFreelancerPersona    (ja.json)
├── EnglishCustomerSupportPersona (en.json)
└── SpanishSalesPersona           (es.json)
```

基底クラスが担う責務は6つ：

- **返信速度制御**：チャットは30〜180秒、クラウドソーシングは300〜900秒
- **文体の揺らぎ**：確認型/共感型/保留型/転換型/不確実型をランダム選択
- **感情状態機械**：初回→打ち解け→問題発生→解決→長期の状態遷移
- **前文脈参照**：「先ほどの〇〇の件ですが」で読んでいる感を再現
- **曖昧さの設計**：「3日程度かかると思いますが、前後するかもしれません」
- **エスカレーション判定**：単価交渉・電話要求・クレームは人間に引き継ぎ

---

## LLMジャッジで人間らしさを数値化する

`base_persona.py`の出力をLLM（Claude Sonnet）に採点させる仕組みを作った。

評価指標は3つ：

| 指標 | 意味 | 目標値 |
|---|---|---|
| `human_likeness_score` | AIっぽくないか（1-10） | 7.5以上 |
| `style_variation_rate` | 均質すぎないか（低いほど良い） | 0.35以下 |
| `timing_naturalness` | タイミングが自然か（1-10） | 6.0以上 |

LLMジャッジのシステムプロンプトはこんな感じ：

```python
JUDGE_PROMPT = """
あなたは人間とAIを区別する専門家です。
以下のメッセージを評価し、JSONのみで返してください：

{
  "human_likeness_score": 1-10,
  "style_variation_rate": 0.0-1.0,
  "timing_naturalness": 1-10,
  "reason_human_likeness": "理由を1文で",
  "improvement_suggestion": "改善点を1文で"
}
"""
```

---

## v1→v5のベンチマーク推移

実装を重ねてHL=4.1→7.7まで改善できた。

| バージョン | 変更内容 | HL | SV | TN |
|---|---|---|---|---|
| v1 | パラメータのみ返す（骨格）| 4.1 | 0.64 | 4.1 |
| v2 | Anthropic APIでテキスト生成 | 6.1 | 0.56 | 3.5 |
| v3 | system promptに文化コンテキスト反映 | 6.8 | 0.50 | 4.5 |
| v4 | フィラー挿入・構造バリエーション | 7.2 | 0.50 | 4.5 |
| v5 | 禁止フレーズconfig・トーンミラーリング | **7.7** | **0.36** | **5.5** |

---

## 特に効いた改善 Top3

### 1. 禁止フレーズをconfigに外出し

毎回「ご連絡ありがとうございます」で始まるのがAIとばれる最大の原因だった。

```json
"banned_phrases": [
  "ご連絡ありがとうございます",
  "お気軽にお声がけください",
  "いつでもお気軽に"
]
```

これをsystem promptに「以下のフレーズを使うな」として渡すだけでHL+0.5。

### 2. フィラーの挿入

```python
FILLERS = {
    "ja": ["えーと、", "そうですね、", "うーん、", "あ、", ""],
    "en": ["Hmm, ", "Yeah, ", "So, ", "Oh, ", "Actually, ", ""],
}
```

空文字列を混ぜることで「フィラーなしの返答」も自然に出現する。

### 3. トーンミラーリング（EN用）

```
Match the formality level of the user's message.
If they use casual language, respond casually.
Never open with 'Thanks for reaching out' unless it's the very first message.
```

en_02のHLが7→8に改善。

---

## v2デュアルスコア：ホールドアウト評価結果

LLMジャッジによる逐次スコアに加え、v2では**統計的アライメント**を軸としたデュアルスコア評価を導入した。pipeline出力と実際の人間テキストの分布を比較する、自己参照しない独立した評価指標だ。

| 指標 | スコア | 95% CI |
|---|---|---|
| Mean Alignment（平均値アライメント） | **0.945** | [0.902, 0.961] |
| Distribution Alignment（分布アライメント） | **0.864** | [0.811, 0.877] |
| KS test（分布同一性検定） | 4/6 pass | — |

- **Mean Alignment**：pipeline出力の平均的特徴量が人間テキストとどれだけ近いか
- **Distribution Alignment**：分布形状まで含めた一致度（Kolmogorov-Smirnov検定ベース）

KS testでは6指標中4指標で帰無仮説（「分布が異なる」）を棄却できなかった。つまり4指標ではpipeline出力と人間テキストを統計的に区別できない。

これらはホールドアウトデータによる評価結果であり、学習データに含まれないテキストで検証している。

---

## 残課題と次のフェーズ

TNだけ5.5止まりで目標の6.0に届いていない。タイミングの自然さはconfigの数値調整より**実際の取引ログ**から学習させないと改善しにくい構造的な問題がある。

また、Distribution Alignment (0.864) は高水準だが、KS testで残る2指標はまだ分布差が有意に検出されている。この2指標の改善と、deception rateとの相関分析がv3以降の課題だ（[Issue #5](https://github.com/RintaroMatsumoto/human-persona/issues/5)）。

---

## OSSとして公開中

**→ [github.com/RintaroMatsumoto/human-persona](https://github.com/RintaroMatsumoto/human-persona)**

派生クラスの追加は誰でもできる。`config/ja.json`を参考に、あなたの言語・文化・ユースケース用のconfigを作るだけだ。PRを歓迎している。

スターをもらえると研究の励みになります。
