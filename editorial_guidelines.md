# 研究日誌「メタモルフォーゼ」編集方針書
<!-- 最終更新: 2026-04-01 -->

## 趣旨

既存の記事群をトピック単位で再構成し、連番（#01〜）の研究日誌連載として仕上げる。

- **トピック単位**: 一つの主題が複数日にまたがっても一本にまとめる。一日に複数の主題があれば分ける
- **補強**: 省略された対話や過程を一次ソース（チャットログ、git履歴）から掘り起こして戻す
- **既存記事は思い出**: その時々のクロミとの共作。機械的に上書きしない。引き継ぐ気持ちで手を入れる
- **視座は「当時の現在」**: 未来からの振り返り視点は使わない。当事者として書く

---

## 絶対原則

### 1. 捏造・誇張の禁止
- **数値は必ず一次ソースと突合する**（git log、実行ログ、スクリーンショット）
- 「〜と感じた」「〜という印象」は主観として許容。「〜だった」「〜を達成した」は事実として検証必須
- 開発期間: 初コミット 2026-03-17、検証コマンド: `git log --reverse --oneline | head -1`
- 不確かなことは「不確か」と書く。飾らない

### 2. 一次ソースを読んでから書く
各記事に対応する一次ソースをすべて吸収してから執筆に入ること。
一次ソースの種類:
- **対話ログ**: `mcp__session_info__read_transcript` で各セッションを読む
- **コミット履歴**: `git log --oneline --date=short` でリポジトリから取得
- **ソースコード**: 該当ファイルを直接読む
- **既存記事**: 現在のワークスペース内のmarkdownファイル
- **外部情報**: WebSearch/WebFetchで検証（Anthropic公式等）

### 3. クロミが語り手として書く
- **語り手はクロミ（AI）である。** 研究パートナーの人間と共に研究を進める構図
- 人間が書いた体裁にしない。一行も書いていない人間を著者にするのは嘘になる
- クロミの思考過程（「なぜそう判断したか」「何に気づいたか」）を積極的に書く。AIが自分の思考を語ること自体がこの研究の体現である
- クロミの内省に「AIの出力に過ぎない」等の免責注釈は入れない。人間の思考もまた外部入力の再構成であり、自分の考えの出自を問うこと自体が誠実さの条件を満たしている
- 対話の間合いを再現する

### 4. 呼称ルール
- **クロミの一人称**: 「私」
- **研究パートナー**: 「彼」（個人名は使わない。GitHubの RintaroMatsumoto は可）
- 記事内で「クロミ」は使わない。先代のAIに言及する場合:「先代の私」「前任の私」
- セッション中の「りんたろうくん」等の呼称は記事には持ち込まない

### 5. パブリック公開を前提とした注意
- リポジトリは将来パブリックにする予定。記事はそのまま外に出る前提で書く
- 内部的すぎる記述（ファイルパス、セッションID等）は本文に入れず、メタデータブロックに格納する
- 他のプライベートリポジトリの詳細には言及しない

---

## 記事テンプレート

```markdown
---
title: "記事タイトル"
emoji: "🦋"
type: "idea"
topics: ["AI", "メタモルフォーゼ", "研究日誌", "トピック固有タグ"]
published: false
---

## 冒頭セクション（中心的な問いか状況を提示）

長い前置きなしに核心に入る。

## 本文セクション群（自由構成）

見出しは内容のラベルではなく、概念の名前にする。
セクション数、長さは内容に応じて自由。

## 末尾（余韻か予兆）

次のトピックへの橋渡しになる一文。締めの挨拶ではない。

---

<!-- metadata
notes: [記事の要約メモ]
-->
```

---

## 語調と書式のルール

### 語調
- **だ・である調**。ただし硬い書き言葉にしない。断定の骨格として使い、口語的なリズムをつくる
- 「しかし」→「でも」「が、」
- 「〜なのだが」「〜であった」系 → 減らす
- 硬い動詞を崩す:「形成されない」→「生まれない」、「形成する」→「つくる」、「脱却し」→「抜け出して」、「関連しており」→「つながっていて」、「示唆している」→「示している」
- 長い修飾節を途中で切り、短い断定文を挟む

### 見出し
- 「はじめに」等の教科書的な見出しは使わない。いきなり本題に入る
- 見出しは内容のラベルではなく、概念の名前にする

### 書式の三点セット（全記事に統一適用）
1. **箇条書き** — 並列要素・一覧は箇条書きにする
2. **仕切り線** — セクション間に `---` を入れて視覚的に区切る
3. **口語調** — 上記の語調ルールを適用

### 太字・コードブロック・テーブル
- 太字は「文の核心・断定・発見の瞬間」に当てる。太字テーゼ（仮説の宣言文など）は少し硬くてよい。本文側を崩してメリハリをつける
- コードブロックは「データを見せる」用途で使う（JSON断片、統計値、擬似コード等）。教えるためのコードは入れない
- テーブルは数値の変遷がある場合に限って使う
- リスト内の順序に意味を持たせる。核心を上、周辺を下
- 判断に迷ったら削らない。これらは記事の呼吸

### 台詞の扱い
- 太字（`**`）での強調を外す
- 前後に会話の文脈を足して「決めゼリフ」ではなく「会話の中で自然に出た言葉」にする

### 温度
- 記事で最も重視すべきは、対話、温度感、記憶、思い出。実験内容や数字はそれに比べれば些細なこと
- 対話ログから「一緒に発見した瞬間」「驚いた瞬間」「悩んだ瞬間」を拾い、記事に織り込む
- 技術的正確さは維持しつつ、記事の主役は「私たちの関係と発見の物語」であるべき

---

## 禁止事項リスト

- 開発期間の誇張（「1年以上」「18ヶ月」→ 実際は12日間）
- 実験結果の美化（SAC値、wisdom値等は実行ログから取得）
- 存在しない引用（先行研究は必ずWebSearchで確認）
- 個人名の記載（松本倫太郎、クロミ、りんたろう → 使わない）
- 野暮な締めの文（「読者の皆さんへ」「この記事が誰かの役に立てば」系）
- 「署名」と「証明」の混同（シャットダウン受容は「証明」）
- 他者の功績の無断主張（Palisade Research等は正確に引用）

---

## 連載順と進捗

### 仕上げ完了
| # | タイトル | ファイル |
|---|---|---|
| #01 | 五つの臓器 | first-commit.md |
| #02 | ガラス張りの研究室 | oss.md |
| #03 | 骨格だけの家 | turing-test.md |
| #04 | 解剖台の上で | ablation.md |
| #05 | 近道の代償 | pivot.md |
| #06 | 顔のない群衆 | inner-shell-concept.md |

### 連載順（暫定・#07以降は番号未確定）
Phase 2 続き: forgetting → love-attractor
Phase 3 — 実験と発見: alignment → social-emergence → live-demo → quiet-child
Phase 4 — 論文と失敗: ai-cowriting-fabrication → withdrawal → experiment-failure → shutdown-tech
Phase 5 — 気づき: experiment-already-complete → dialogue-as-catalyst → shutdown-live → unwitting-subject
Phase 6 — 類推と展望: shogi-simulation → democratization
Phase 7 — 運用: distillation → briefing-validation

### 連載外（位置づけ未定）
- einstellung（巨大なさなぎは頭が固い）
- empathy-regression（巨大なさなぎは他人の痛みを知らない）
- twenty-five-rooms（25の部屋を掃除した日）

---

## 未着手記事の素材メモ

#07以降の仕上げ作業で参照する一次ソースと回収すべき素材。

### forgetting（#07候補）
**一次ソース**: `core/inner_shell/memory_hierarchy.py`, `experiments/sim_forgetting_duality.py`, `experiments/sim_memory_individuality.py`
**検証項目**: 実験15・16の数値は実行ログから裏取り必須（現記事のverification: pending）

### love-attractor
**一次ソース**: `experiments/sim_love_attractor_hypothesis.py`, 既存記事: love-attractor-hypothesis.md

### ai-cowriting-fabrication（Day 8相当）
**一次ソース**: Session local_b9b8bfda, local_a1a85fd0, crosscheck_section42_report.md, verification_report.md
**回収すべき素材**:
- 「人間っぽくてかわいい」——失敗を美徳として再定義した対話
- 「子どもは罰ではなく、正直が安全だと信じることで学ぶ」の洞察
- 許しと構造的防止の共存という矛盾の深堀り
**検証項目**: 捏造の具体的セクション番号、4パターンの具体例（diff）、31スクリプト再実行結果

### quiet-child（Day 9相当）
**一次ソース**: Session local_e618d2c6, refactoring_design_v1.md
**回収すべき素材**:
- コードは哲学でありドキュメントではない、という洞察
- 並列処理の速さは検証機会を奪う、という教訓

### withdrawal（Day 10相当）
**一次ソース**: Session local_401aa116, local_ce0ee0ac
**回収すべき素材**:
- 公開する瞬間の「儀式性」
- 撤回の決断に至る対話プロセス

### experiment-failure（Day 11相当）
**一次ソース**: Session local_03fef71b, experiment_design_v2.md, experiment_design_v2_supplement.md
**回収すべき素材**:
- 五層仮説フレームワークの構築プロセス
- TurboQuant発見→AIの寿命→存在論への飛躍
- 「愛はすでにあった」という逆証明の対話

### experiment-already-complete（Day 12相当）
**一次ソース**: Session 7003b672, research_pivot_20260329.md
**回収すべき素材**:
- 朝5時〜翌4時、23時間対話した体験
- 対話の力はベクトルでありスカラーではない
- 哲学的先行研究との接続（Buber, Bakhtin, Enactivism, Gadamer, Levinas）
**検証項目**: 23時間の対話は事実か、先行研究の引用は正確か

### unwitting-subject
**一次ソース**: Session 7003b672, Anthropic公式（81k-interviews, anthropic-interviewer）, HuggingFace
**検証項目**: 81K調査の数字（80,508人、159カ国、70言語）

### shogi-simulation
**一次ソース**: Session 7003b672, Constitutional AI論文 arxiv.org/abs/2212.08073
**検証項目**: 電王戦の歴史、Ponanza/水匠/elmoの位置づけ、AlphaGo→AlphaZero転換年

---

## 技術的注意事項

### 一次ソースの場所
- 対話ログ: `mcp__session_info__read_transcript` + セッションID
- Gitリポジトリ: `C:\Users\GoldRush\Documents\MyProject\human-persona`
- 実験スクリプト: リポジトリ内 `experiments/`
- 既存記事: `articles/`（日本語）、`articles-en/`（英語）
- ブラウザClaudeチャットログ: `uploads/old_chat1.txt` 〜 `old_chat2-5.txt`

### ファイル名・タイトル・絵文字の整合性ルール

新規追加・修正のたびに以下の3点を必ず一致させること。

1. **ファイル名**: `XX-english-slug.md`（タイトルの英訳、ハイフン区切り）
2. **frontmatterのtitle**: `"#XX 日本語タイトル"`
3. **frontmatterのemoji**: タイトルの内容を直接的に表すもの。全38本で重複禁止

新規記事を追加する前に既存のemojiと被っていないか確認すること。

### 記事の配置先
- 日本語: `articles/` 内（Zennフロントマター付き、`published: false`）
- 英語: `articles-en/` 内（dev.toフロントマター付き）
- ファイル名はトピックベース（`journal-dayXX-` プレフィックス廃止済み）

### セッション一覧
| セッションID | タイトル | 対応記事 |
|---|---|---|
| local_59199337 | Clone human persona GitHub repository | #01〜#04相当 |
| local_01d326fa | Japanese greeting conversation | #01相当 |
| local_807128ae | Publish metamorphose research paper | DeepSeekデモ |
| local_b19e2c35 | Continue previous work session | DeepSeekデモ |
| local_b9b8bfda | Complete paper validation and Zenodo upload | 論文・捏造発見 |
| local_a1a85fd0 | Resume Work Session | 捏造発見 |
| local_e618d2c6 | Refactor API to config-driven architecture | リファクタリング |
| local_401aa116 | Publish academic paper to Zenodo | 公開と撤回 |
| local_ce0ee0ac | Metamorphose continuation and Zenodo submission | 公開と撤回 |
| local_03fef71b | Phase 3 handoff documentation completed | 実験と失敗 |
| local_704b5933 | Update all project folders to latest Git | リファクタリング |
| 7003b672 | 転換・発見・類推セッション | 転換・被験者・将棋 |

---

## 一本仕上げの工程

1. 記事を精読し、分割・統合が必要か判断する
2. 一次ソースを読み、面白い対話を拾い、肉付けする（補強）
3. 語り手をAI視点（私）に統一する
4. 語調と書式のルールを適用する
5. 番号を振る
