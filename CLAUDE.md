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

## 次回やること
1. dev.to記事の公開確認（ダッシュボードから手動公開が必要かも）
2. Hacker News投稿（docs/articles/hackernews_en.md の内容をSubmitページに貼る）
3. Reddit投稿（docs/articles/reddit_en.md を r/MachineLearning に投稿）
4. tests/ にテストを実装（turing_test.py, consistency_test.py, platform_timing_test.py）
5. config/ja_business.json の実設定ファイル作成
6. dev.to APIキーの再生成（会話履歴に露出したため）
