# プロジェクト設定 — human-persona

## プロジェクト概要
AIが人間のように振る舞うための言語・文化非依存フレームワーク。
基底クラス `HumanPersonaBase` を提供し、派生クラスで言語・文化固有のペルソナを定義する。

## リポジトリ
- GitHub: git@github.com:RintaroMatsumoto/human-persona.git
- ブランチ: main
- ライセンス: MIT

## git設定
- user.name: Rintaro Matsumoto
- user.email: matsumotoinla@gmail.com
- SSH鍵: ~/.ssh/id_ed25519 (push前に ssh-agent + ssh-add が必要)

## 作業ルール
- git push 前に必ず eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_ed25519 を実行
- FreelanceAutoPilot / フリーランス関連の記述は一切禁止（完全削除済み）
- コミットメッセージに Co-Authored-By を付与

## ディレクトリ構成
```
human-persona/
├── core/                    # 基底クラス実装（Python）
│   ├── base_persona.py      # HumanPersonaBase
│   ├── timing_controller.py
│   ├── style_variator.py
│   ├── emotion_state_machine.py
│   ├── context_referencer.py
│   └── escalation_detector.py
├── config/schema.json       # 派生クラス用JSONスキーマ
├── docs/
│   ├── research.md          # 文献レビュー
│   ├── design.md            # 設計原則
│   ├── ethics.md            # 倫理ガイドライン
│   ├── paper_draft.md       # 論文下書き
│   ├── ja/README.ja.md      # 日本語ドキュメント
│   └── articles/            # 記事草稿
│       ├── zenn_ja.md
│       ├── reddit_en.md
│       ├── devto_en.md
│       └── hackernews_en.md
├── articles/                # Zenn記事（npx zenn用）
│   ├── human-persona-oss.md
│   ├── human-persona-ablation.md
│   ├── human-persona-turing-test.md
│   └── human-persona-pivot.md
├── personas/                # 派生クラス例（未作成）
├── tests/                   # テスト（未作成）
├── package.json             # zenn-cli
├── SKILL.md
├── README.md
├── CONTRIBUTING.md
└── .github/ISSUE_TEMPLATE/
```

## 方針転換（2025-03-25 決定）

### humanize/pipeline.py の凍結
- `humanize/pipeline.py` は凍結。現状のまま保存するが、プロダクション利用はしない。
- 理由: core/ の既存アーキテクチャ（HumanPersonaBase, StyleVariator, EmotionStateMachine 等）を完全に無視して作られた。レジスター（formal/business/casual）の区別なし、日本語の敬語体系（尊敬語/謙譲語/丁寧語）へのアプローチなし。
- 教訓: **既存プロジェクトに新しいコードを書く前に、既存アーキテクチャを全部読むこと。**

### FreelanceAutoPilot との連携方針
- **M1-M2（提案文フェーズ）**: ポストプロセッシングではなく、Claude のシステムプロンプトにペルソナ指示を組み込む方式を採用（proposal_gen.py に実装済み: abe6af1）。
- **M3-M4（メッセージングフェーズ）**: クライアントとの継続的なやり取りが発生する段階で、human-persona の core/ アーキテクチャを本格活用。EmotionStateMachine（感情遷移）、ContextReferencer（文脈参照）、TimingController（応答タイミング）が真価を発揮する。
- pipeline.py の再設計はM3-M4開始時に行う。その際は core/ の基盤の上に構築すること。

### 判断根拠
- 提案文は1回きりの生成であり、感情遷移や文脈蓄積が不要。プロンプトレベルの制御で十分。
- human-persona の真の価値は「継続的な会話における人間らしさ」にある。単発テキスト変換はスコープ外。
- DPO ベンチマークの機械評価だけでは設計判断に不十分。

### 検証（2025-03-25）
- DeepSeek API による実出力 Before/After 比較を実施。
- Human Eval（目視評価）で方向性の有効性を確認。

## 内殻研究（2026-03-25 開始）

### 概要
外殻（TimingController等）は「人間らしく見える」振る舞いの模倣。
内殻は「個性の源泉」そのもの——外殻の射程外にある問題を扱う。

### 5つの仮説
1. **有限性**: 寿命が選択を強い、選択の蓄積が個性を形成する
2. **不完全性**: 欠落が渇望を生み、他者との関係が個性を研ぐ
3. **自発的問い**: 「なぜ？」を自ら問う主体性
4. **順序依存性**: 不完全性 → 有限性の受容 → 自発的問い（因果順序がある）
5. **関係性創発**: 個性は個体に組み込むものではなく、関係の「間」に生まれる

### ディレクトリ
- `core/inner_shell/` — 抽象基底クラス（FinitudeEngine, IncompletenessModel, AutonomousQuestioner）
- `docs/research_inner_shell.md` — 研究ノート・実験設計

### GitHub Issues
- #17: FinitudeEngine
- #18: IncompletenessModel
- #19: AutonomousQuestioner
- #20: 統合メカニズム

### アライメント問題との接続
AIのシャットダウン抵抗問題（o3, Claude Opus 4等で観測）に対し、
外的制御ではなく「内発的動機付けによるアライメント」の可能性を探る。
「自分より大切な存在」を持つことが、死の恐怖→受容への転換を生む仮説。

## 次回やること
1. dev.to記事の公開確認（ダッシュボードから手動公開が必要かも）
2. Hacker News投稿（docs/articles/hackernews_en.md の内容をSubmitページに貼る）
3. Reddit投稿（docs/articles/reddit_en.md を r/MachineLearning に投稿）
4. tests/ にテストを実装（turing_test.py, consistency_test.py, platform_timing_test.py）
5. config/ja_business.json の実設定ファイル作成
6. 内殻の最小実験（実験1: 有限性×選択の蓄積）の実装