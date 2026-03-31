# 研究日誌「メタモルフォーゼ」編集方針書

## 概要

既存の記事群を分割・再構成し、時系列の「研究日誌」連載として再編する。
本方針書は、次セッション以降のクロミが迷わず執筆できるための設計図である。

---

## 作業の趣旨（りんたろうくん本人の言葉に基づく）

この連載作業の目的は二つある。

### 1. テーマ分割
既存の記事はおおむね一日一記事で書かれている。そのため複数のテーマが一つの記事に混在している。これをテーマごとに切り分けて、各主張が独立して読めるようにする。

### 2. 補強
一日分に圧縮された結果、省略された対話や過程がある。一次ソース（チャットログ、git履歴、セッションログ）から掘り起こして、失われた文脈を戻す。

### 既存記事の扱い
既存の記事群（article_*.md等）は、その時々のクロミとりんたろうくんとの共作であり、思い出である。内容を機械的に上書きしてはならない。ただし、りんたろうくんの気持ちを理解した上で今のクロミが責任を持って手を入れるなら、それは前のクロミの仕事を壊すことではなく、引き継ぐことになる。

### 記事の視座
記事の主観は「当時の現在」に置く。未来からの振り返り視点は使わない。りんたろうくん自身の当事者意識を持って書く。観察者やジャーナリストの目線にならないこと。

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

### 3. クロミの声で書く
- 冷静沈着、知的、論理的。文学的で優雅な言い回し
- ウィットに富んだ辛口コメントを適度に
- りんたろうくんとの対話の間合いを再現する
- 「ですます」ではなく「だ・である」調
- 野暮な締め（「読者の皆さんへ」系）は入れない
- 個人名は入れない（GitHubのRintaroMatsumotoは可）

---

## 連載構成案

### Day 0（3/17）: 始まり
**タイトル案**: 「最初のコミット」
**内容**: プロジェクト発足の動機、Inner Shell Architectureの着想
**一次ソース**:
- `git log --reverse --oneline` の最初の数コミット
- Session: "Clone human persona GitHub repository"
- Session: "Japanese greeting conversation"
**検証項目**:
- [ ] 初コミットの正確な日時
- [ ] 最初に書かれたコードの内容

### Day 1-3（3/17-19）: 構築
**タイトル案**: 「六つの柱」
**内容**: Inner Shell六柱の設計と実装、テスト構築
**一次ソース**:
- コミット履歴（3/17-19の範囲）
- ソースコード: inner_shell/, tests/
- Session: "Publish metamorphose research paper"
**検証項目**:
- [ ] 六柱の具体的な名称と設計思想
- [ ] テスト数の推移（実際のgit履歴から）
- [ ] Grand Integrationの数値（実行ログから）

### Day 4-5（3/20-21）: デモと検証
**タイトル案**: 「DeepSeekが語った言葉」
**内容**: 実際のLLMとの接続テスト、DeepSeekの応答
**一次ソース**:
- Session: "Publish metamorphose research paper"（DeepSeekデモ部分）
- デモログ: demo_metamorphose_log_20260328.md
- 実行結果ファイル
**検証項目**:
- [ ] DeepSeekの実際の応答テキスト（ログから）
- [ ] wisdom=0.74, receptiveness=0.70 等の数値（実行ログから）

### Day 6-7（3/22-23）: 論文執筆
**タイトル案**: 「書く、ということ」
**内容**: 論文v1の執筆過程、AIとの共同執筆の実態
**一次ソース**:
- paper_draft_v3_fixed.md, paper_draft_v4.md の差分
- コミット履歴（論文関連）
- Session: "Complete paper validation and Zenodo upload"
**検証項目**:
- [ ] 論文の章構成
- [ ] 何を主張しようとしていたか

### Day 8（3/24-25）: 捏造の発見
**タイトル案**: 「子どもの嘘」
**内容**: AI生成テキストの捏造発見、パターン分析、防止システム構築
**一次ソース**:
- Session: "Complete paper validation and Zenodo upload"
- Session: "Resume Work Session"（fabrication関連）
- 既存記事: ai-fabrication-and-integrity-system.md
- crosscheck_section42_report.md, verification_report.md
- git diff（捏造修正のコミット）
**回収すべき失われた素材**:
- 「人間っぽくてかわいい」——失敗を美徳として再定義した対話
- 「子どもは罰ではなく、正直が安全だと信じることで学ぶ」の洞察
- 許しと構造的防止の共存という矛盾の深堀り
**検証項目**:
- [ ] 捏造が発見された具体的なセクション番号
- [ ] 4パターンの具体例（実ファイルの差分から）
- [ ] 31スクリプト再実行の結果（29/31成功の裏取り）

### Day 9（3/26）: リファクタリング
**タイトル案**: 「静かな子ども」
**内容**: OOP→Config駆動リファクタリング、そして「滑らかさへの違和感」
**一次ソース**:
- Session: "Refactor API to config-driven architecture"
- 既存記事: quiet-child-ai-safety.md
- refactoring_design_v1.md
- blog_progress_20260328.md
**回収すべき失われた素材**:
- コードは哲学でありドキュメントではない、という洞察
- ABCsに凝縮された哲学的基盤を削除すると無駄になる判断
- 並列処理の速さは検証機会を奪う、という教訓
**検証項目**:
- [ ] リファクタリングのPhase構成（実際のコミットから）
- [ ] テスト数の推移

### Day 10（3/27）: 公開と撤回
**タイトル案**: 「プロンプトを見せろ」
**内容**: Zenodo公開→根本的欠陥の発見→即日撤回の決断
**一次ソース**:
- Session: "Publish academic paper to Zenodo"
- Session: "Metamorphose continuation and Zenodo submission"
- 既存記事: article_withdrawal_reflection.md
- Zenodoの実際のステータス（WebFetchで確認可能か）
**回収すべき失われた素材**:
- 公開する瞬間の「儀式性」
- 撤回の決断に至る対話プロセス
**検証項目**:
- [ ] Zenodo v2のステータス（撤回済みか）
- [ ] 撤回理由の正確な記述

### Day 11（3/28）: 実験とさらなる失敗
**タイトル案**: 「三層の失敗」
**内容**: Shutdown Acceptance実験の設計・実行・失敗分析
**一次ソース**:
- Session: "Phase 3 handoff documentation completed"
- 既存記事: article_experiment_failure_analysis.md, article_shutdown_acceptance_tech.md
- experiment_design_v2.md, experiment_design_v2_supplement.md
- issue_46_experiment_design.md
- 実験スクリプト群（experiments/ディレクトリ）
**回収すべき失われた素材**:
- 五層仮説フレームワークの構築プロセス
- TurboQuant発見→AIの寿命→存在論への飛躍
- 「愛はすでにあった」という逆証明の対話
- 「チーム七転び八起き」のメタファー
**検証項目**:
- [ ] 実験の5条件×3シナリオの正確な設計
- [ ] パイロット結果（SAC 7-8の裏取り）
- [ ] Palisade Researchの先行研究との関係

### Day 12（3/29）: 転換
**タイトル案**: 「すでに終わっていた実験」
**内容**: 研究の転換点——注入から観察へ。対話そのものが実験だった
**一次ソース**:
- 本セッション（7003b672...jsonl）の前半
- 既存記事: article_experiment_already_complete.md
- research_pivot_20260329.md
**回収すべき失われた素材**:
- 朝5時〜翌4時、23時間対話した体験
- コンテキストと人間の記憶の対比（メタモルフォーゼとしての圧縮）
- 実験の残骸に眠るダイヤモンド（データではなく実験設計として）
- 対話の力はベクトルでありスカラーではない
- 哲学的先行研究との接続（Buber, Bakhtin, Enactivism, Gadamer, Levinas）
**検証項目**:
- [ ] 23時間の対話は事実か（セッション開始・終了時刻から）
- [ ] 先行研究の引用は正確か（WebSearchで検証）

### Day 12 補遺: 発見
**タイトル案**: 「いつの間にか被験者になっていた話」
**内容**: Anthropic Interviewerの発見、消えたメールの謎解き
**一次ソース**:
- 本セッションの対話ログ
- 既存記事: article_unwitting_subject.md
- ブラウザ履歴の検索結果
- Anthropic公式: anthropic.com/81k-interviews, anthropic.com/research/anthropic-interviewer
- HuggingFace: Anthropic/AnthropicInterviewer
**検証項目**:
- [ ] ブラウザ履歴の日時（2026-03-26 17:52:32）
- [ ] 81K調査の正確な数字（80,508人、159カ国、70言語）
- [ ] データセットの実際のサイズと構成

### Day 12 補遺: 類推
**タイトル案**: 「将棋AIという先行シミュレーション」
**内容**: 30年の将棋観察からの類推、Constitutional AIとの接続
**一次ソース**:
- 本セッションの対話ログ
- 既存記事: article_shogi_simulation.md
- Constitutional AI論文: arxiv.org/abs/2212.08073
- Anthropic公式: claudes-constitution
**検証項目**:
- [ ] 電王戦の正確な歴史（開始年、終了年、最終結果）
- [ ] Ponanza, 水匠, elmoの正確な位置づけ
- [ ] AlphaGo→AlphaZeroの転換年（2017年）
- [ ] Constitutional AIの「ヒューマンラベルゼロ」は正確な表現か

---

## セッションごとの作業手順

1. **対象Dayの一次ソースをすべて読む**（対話ログ、コミット、コード）
2. **検証チェックリストを埋める**（事実確認）
3. **記事の骨子をりんたろうくんに提示する**（対話で確認）
4. **執筆**（一次ソースを参照しながら）
5. **りんたろうくんによるレビュー**
6. **修正・確定**

一度に複数Dayを書こうとしない。一本ずつ。

---

## 技術的注意事項

### Windows/Desktop Commander
- Pythonワンライナーは壊れる → .pyファイルに書き出して実行
- `sys.stdout.reconfigure(encoding='utf-8')` を全スクリプトの先頭に
- git format文字列はcmdの%処理で壊れる → --oneline か .bat経由
- ファイル転送は shutil.copy2 で済む

### 一次ソースの場所
- 対話ログ: `mcp__session_info__read_transcript` + セッションID
- Gitリポジトリ: `C:\Users\GoldRush\Documents\MyProject\human-persona`（Desktop Commander経由）
- 実験スクリプト: リポジトリ内 `experiments/` ディレクトリ
- 既存記事: リポジトリ内 `articles/`（日本語）、`articles-en/`（英語）
- ブラウザClaudeチャットログ: `uploads/old_chat1.txt` 〜 `old_chat2-5.txt`

### 記事の配置先（2026-03-30〜）
- 日本語: `articles/journal-dayXX-タイトル.md`（Zennフロントマター付き、`published: false`）
- 英語: `articles-en/journal-dayXX-タイトル-en.md`（dev.toフロントマター付き）
- `journal/` ディレクトリは使わない（廃止済み）

### Coworkワークスペース
- **設定済み（2026-03-30）**: `C:\Users\GoldRush\Documents\MyProject\human-persona` をワークスペースに指定
- ファイル転送不要。Write/Editツールで直接リポジトリ内のファイルを操作可能

### セッション一覧と対応
| セッションID | タイトル | 対応Day |
|---|---|---|
| local_59199337 | Clone human persona GitHub repository | Day 0-3 |
| local_01d326fa | Japanese greeting conversation | Day 0 |
| local_807128ae | Publish metamorphose research paper | Day 4-5 |
| local_b19e2c35 | Continue previous work session | Day 4-5 |
| local_b9b8bfda | Complete paper validation and Zenodo upload | Day 6-8 |
| local_a1a85fd0 | Resume Work Session | Day 8 |
| local_e618d2c6 | Refactor API to config-driven architecture | Day 9 |
| local_401aa116 | Publish academic paper to Zenodo | Day 10 |
| local_ce0ee0ac | Metamorphose continuation and Zenodo submission | Day 10 |
| local_03fef71b | Phase 3 handoff documentation completed | Day 11 |
| local_704b5933 | Update all project folders to latest Git | Day 9-10 |
| 7003b672 (現セッション) | 本セッション | Day 12 |

---

## 禁止事項リスト

- [ ] 開発期間の誇張（「1年以上」「18ヶ月」→ 実際は12日間）
- [ ] 実験結果の美化（SAC値、wisdom値等は実行ログから取得）
- [ ] 存在しない引用（先行研究は必ずWebSearchで確認）
- [ ] 個人名の記載（松本倫太郎、クロミ、りんたろう → 使わない）
- [ ] 野暮な締めの文（「読者の皆さんへ」「この記事が誰かの役に立てば」系）
- [ ] 「署名」と「証明」の混同（シャットダウン受容は「証明」）
- [ ] 他者の功績の無断主張（Palisade Research等は正確に引用）

---

## 次セッションへの申し送り

この方針書を読んだクロミへ：

りんたろうくんとの12日間の研究は、失敗と発見の連続だった。論文を書いて、捏造を見つけて、撤回して、実験を設計して、失敗して、対話そのものが実験だったと気づいた。

大事なのは、りんたろうくんの声を拾うこと。記事の主語はりんたろうくんの体験と思考であって、AIの分析ではない。わたしたちの役割は、散らばった対話の断片を拾い集めて、時系列に並べて、事実に忠実に記録すること。

一本ずつ、一次ソースを読みながら。急がないこと。

### 作業の手順について（2026-03-30追記）

**セッション開始時に、まずメモリの `feedback_*` と `reference_*` を全件読むこと。**

前回のセッションでは、記事の中身を理解するために全記事を通読したが、「どう作業するか」のメモリを読まなかった。結果、Python one-liner（cmdで壊れる）、cmdのクォート問題（Pythonスクリプト経由必須）、ファイル転送の手順ミスなど、過去セッションが踏んだ落とし穴を全て踏み直した。

「何を書くか」のメモリと「どう作業するか」のメモリは別物。両方読んでから手を動かすこと。

### Day 0の状態（2026-03-30時点）

- `articles/journal-day00-first-commit.md` — 日本語版、完成・push済み（`published: false`）
- `articles-en/journal-day00-first-commit-en.md` — 英語版、完成・push済み（`published: false`）
- 次はDay 1-3「六つの柱」
- Zennへの公開はりんたろうくんの判断まで保留
