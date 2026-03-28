---
title: "AIが人間のように振る舞う基底クラスを設計・AGPL-3.0で公開した"
emoji: "🎭"
type: "tech"
topics: ["Python", "AI", "AGPL", "チューリングテスト", "NLP"]
published: true
---

## きっかけ：AIで書いた文章が、一発でバレた

ビジネスコミュニケーションをAIで自動化しようとして、最初に書いたプロトタイプの出力がこれだった:

> ご連絡ありがとうございます。本件につきまして、3日以内に納品可能です。詳細な要件をお知らせいただければ、すぐに着手いたします。何かご不明な点がございましたら、お気軽にお申し付けください。

完璧な日本語。文法的にも敬語的にも非の打ち所がない。そして、**誰が読んでもAIが書いたとわかる。**

なぜわかるのか。3つの致命的なパターンがある:

1. **30秒で返信が来る。** 人間なら考える時間がある
2. **毎回同じトーン。** 3往復目も初回と同じ丁寧さ
3. **「お気軽に」で終わる。** 人間はこんなに毎回お気軽に言わない

2024年、Jones & Bergen が PNAS に発表した論文がこの直感を裏付けた。GPT-4.5に「人間らしいペルソナ」を指示したところ、73%の確率で人間と認識された——実際の人間参加者の認識率を上回った。

つまり、LLMは十分に賢い。バレる原因は**知性ではなく振る舞い**にある。返信速度、文体のばらつき、感情の変化、文脈への参照——言語学で「パラ言語的特徴」と呼ばれるものだ。

じゃあ、この「振る舞い」を体系的に設計できないか？　そう思って作り始めた。

## 設計のスタートライン：ハードコードの限界を想像する

最初に考えたのは、素朴にif文で分岐するアプローチだった。

```python
if exchange_count < 3:
    tone = "formal"
elif exchange_count < 10:
    tone = "casual"
if "クレーム" in message:
    tone = "careful"
if time.hour >= 23:
    delay = 3600  # 翌朝返信
```

これを書き始めてすぐに気づいた。**言語を変えるたびに全部書き直しになる**。日本語なら「3往復で打ち解ける」が自然だが、英語だと「1往復目からカジュアル」が普通だったりする。スペイン語はどうなる？アラビア語は？

この「スケールしない」問題を最初に認識したことが、基底クラス設計につながった。

## なぜ「基底クラス」なのか

人間のコミュニケーションを観察すると、**構造**は文化を超えて共通している:

- 返信には時間がかかる（即レスは不自然）
- 感情は会話を通じて変化する（初回の緊張→徐々に打ち解け）
- 前の文脈を参照する（「先ほどの件ですが」）
- 対応できない状況では人に引き継ぐ（クレーム、法的リスク）

変わるのは**パラメータ**だ。「打ち解けるまでの往復数」が3回なのか1回なのか。敬語を使うかどうか。沈黙をどう解釈するか。

だからOOPの継承モデルで設計した:

```
HumanPersonaBase（基底クラス）← 構造を定義
│
├── JapaneseBusinessPersona      ← ja.json（3往復で打ち解け、敬語あり）
├── EnglishCustomerSupportPersona ← en.json（1往復目からカジュアル可）
└── SpanishSalesPersona           ← es.json（情熱的、感嘆符多め）
```

言語・文化固有のロジックは**1行もPythonに書かない**。JSONの設定ファイルだけで派生を作れる。ハードコードの問題を構造で解決した。

## 4つのコンポーネント、それぞれの設計判断

### 1. TimingController — なぜ正規分布なのか

人間の返信時間を観察すると、**中央値付近に集中し、たまに極端に長い**（電話が来た、席を外した、等）。均一分布（`random.uniform`）では「どの遅延も等確率」になってしまい、この分布を再現できない。そこで正規分布を採用した。

```python
def calculate_delay(self, platform: Platform) -> float:
    profile = self.profiles.get(platform)
    midpoint = (profile.min_seconds + profile.max_seconds) / 2
    spread = (profile.max_seconds - profile.min_seconds) / 4
    delay = random.gauss(midpoint, spread)
    return max(profile.min_seconds, min(delay, profile.max_seconds))
```

もう一つ。深夜2時に返信が来たら「この人、起きてるの？」と不安になる。`night_queue` フラグを付けて、営業時間外のメッセージは翌朝のキューに入れるようにした。

### 2. EmotionStateMachine — 状態遷移を設計する苦しみ

感情の状態遷移をどうモデル化するか。これが一番悩んだ。

最終的に5状態にした:

```python
class EmotionState(Enum):
    FORMAL   = "formal"     # 初回: 丁寧・慎重
    WARMING  = "warming"    # 打ち解け
    TENSE    = "tense"      # 問題発生
    RELIEVED = "relieved"   # 解決後
    TRUSTED  = "trusted"    # 長期取引
```

5つ目のRELIEVEDは、「問題が解決した直後」の独特の空気感を表現するために入れた。安堵と、でもまだちょっと緊張が残っている感じ。これがないと、TENSE→WARMINGへの直接遷移で「急に和んだ」感じになってしまう。

遷移トリガーは文字列マッチではなく**Callable**で定義している。「3往復後に打ち解ける」「問題が起きたら緊張する」をコードレベルで保証するため。

```python
DEFAULT_TRANSITIONS = [
    Transition(FORMAL, WARMING,
               lambda sm: sm.exchange_count >= 3,
               "3往復後に打ち解ける"),
    Transition(WARMING, TENSE,
               lambda sm: sm._last_event == "problem_detected",
               "問題発生で緊張"),
]
```

ここの「3」は日本語ビジネスコミュニケーションの観察値。英語なら「1」でもいい。だからJSONで上書きできるようにしてある。

### 3. StyleVariator — 同じことを毎回違う言い方で

5パターン（確認型・共感型・保留型・転換型・不確実型）をランダムに選択する。ただし直近の履歴で重みを減衰させ、同じパターンの連続を防ぐ。

不確実表現の確率的挿入もある。「3日で完成します」と言い切るAIは不自然だ。「3日程度かかると思いますが、前後するかもしれません」——この曖昧さが人間らしい。

### 4. ContextReferencer — 「読んでいる感」の再現

「先ほどの〇〇の件ですが」。この一言があるだけで、「この人はちゃんと前のメッセージを読んでいる」と感じる。トピックベースで会話を追跡し、参照情報をLLMに渡す。

## 重要な設計判断：テキスト生成をしない

`process_message()` は**テキストを生成しない**。返すのは「今の感情状態」「推奨する応答スタイル」「推奨する遅延時間」「エスカレーションの要否」だけ。

```python
response = persona.process_message("納期を前倒しできますか？")
context = persona.get_system_prompt_context()
# → {"emotion_state": "warming", "tone": {"formality": 0.6}, ...}
```

この情報をLLMのシステムプロンプトに注入する。テキスト生成はLLMに任せる。

なぜか。テキスト生成をフレームワーク内でやると、LLMの進化に追従できなくなる。GPT-4がGPT-5になっても、Claude 3がClaude 4になっても、「感情遷移」や「応答タイミング」の構造は変わらない。構造とテキスト生成を分離したことで、LLMを差し替えるだけでフレームワークが使い続けられる。

## まとめ

AIがバレる原因は「何を言うか」じゃなくて「どう言うか」。返信速度、文体の揺らぎ、感情の変化、文脈の参照——これらを基底クラスとして設計し、AGPL-3.0で公開した。

作って分かったのは、「人間らしさ」は驚くほど構造化できるということ。そして構造化してみると、**自分が普段いかに無意識にこれらのパターンを使っているか**に気づく。

リポジトリ: [github.com/RintaroMatsumoto/human-persona](https://github.com/RintaroMatsumoto/human-persona)

---

> 📄 **この記事の研究はプレプリントとして正式公開されています**
> **HumanPersonaBase: A Language-Agnostic Framework for Human-Like AI Communication**
> DOI: [10.5281/zenodo.19273577](https://doi.org/10.5281/zenodo.19273577)
