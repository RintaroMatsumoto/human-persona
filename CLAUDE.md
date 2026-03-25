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
│   └── human-persona-oss.md # published: true
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

### 本採用（2025-03-25 検証完了）
- DeepSeek API による実出力 Before/After 比較を実施（scripts/compare_persona.py）。
- Human Eval（りんたろう目視）で方向性の有効性を確認。本採用決定。
- FreelanceAutoPilot commits: abe6af1（ペルソナプロンプト適用）、e51d364（数値制約+プラットフォーム別トーン）。

### M3-M4チャット/メッセージングへの非推奨
- **プロンプトレベルのペルソナ制御はチャットには推奨しない。**
- 理由: 継続的な会話では、感情の一貫性・前発言への参照・応答タイミングの揺らぎ・トーンの自然な変遷が必要。システムプロンプトだけでは5往復を超えたあたりで破綻する。
- M3-M4では core/ アーキテクチャ（EmotionStateMachine, ContextReferencer, TimingController）を本格統合すること。

## 次回やること
1. dev.to記事の公開確認（ダッシュボードから手動公開が必要かも）
2. Hacker News投稿（docs/articles/hackernews_en.md の内容をSubmitページに貼る）
3. Reddit投稿（docs/articles/reddit_en.md を r/MachineLearning に投稿）
4. tests/ にテストを実装（turing_test.py, consistency_test.py, platform_timing_test.py）
5. config/ja_business.json の実設定ファイル作成
6. dev.to APIキーの再生成（会話履歴に露出したため）
7. M3-M4 開始時: humanize/pipeline.py を core/ ベースで再設計（レジスター・敬語体系対応）
8. Human Eval の実施（DPO ベンチマーク補完）
