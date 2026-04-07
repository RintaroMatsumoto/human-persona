# プロジェクト設定 — human-persona

## プロジェクト概要
AIが人間のように振る舞うための言語・文化非依存フレームワーク。
基底クラス `HumanPersonaBase` を提供し、派生クラスで言語・文化固有のペルソナを定義する。
内殻（Inner Shell）研究を通じて「個性の源泉」を計算論的に探求中。

## リポジトリ
- GitHub: git@github.com:RintaroMatsumoto/human-persona.git
- ブランチ: main
- ライセンス: AGPL-3.0-or-later（network copyleft。改変版をネットワーク経由で提供する場合、改変点も同じAGPLで公開する義務あり。選択理由は memory/project_community_strategy.md 参照）

## git設定
- user.name: Rintaro Matsumoto
- user.email: matsumotoinla@gmail.com
- 認証: GitHub CLI (gh) の keyring に保存されたトークン経由（HTTPS）。
  remote は `git@github.com:...` のままだが、push 時は URL を HTTPS に差し替えること：
  `git push https://github.com/RintaroMatsumoto/human-persona.git main`
  （fetch も同様。origin を書き換えたくないため URL 直打ち運用）
- ~/.ssh/id_ed25519 は現在存在しない。ssh-agent / ssh-add は不要（2026-04-07 確認）

## 作業ルール


## データ信頼性ルール（最重要・必読）

> **2026-03-28 教訓**: AI共同執筆の過程で、論文に架空のデータが混入した。
> 実データ（0.945, 0.864）に架空の指標（0.912）が追加され、
> 実在するクラス名から偽のablationバリアントが生成された。
> 以下のルールはこの再発を防ぐために制定された。

### 絶対に守ること

1. **数値を創作しない**: 論文・ドキュメントに書く数値は、必ず実行結果から取得する。
   「もっともらしい数値」を推測・補完・生成してはならない。
2. **実行していない実験の結果を書かない**: コードが存在しても、実行ログがなければ
   「結果」として記述してはならない。
3. **先行研究を自前実験として記述しない**: 他者の研究結果を引用する場合は、
   必ず出典を明記し、自前実験として再構成しない。
4. **不確かな場合は「未検証」と書く**: 検証できていないデータには
   必ず「未検証」「要確認」等のフラグを付ける。確証がないものを断定しない。

### 実験データの記録ルール

- 全ての実験は `experiments/runner.py` 経由で実行する
- 結果は `experiments/registry.sqlite` に自動記録される
- 論文で数値を引用する際は `<!-- run:RUN_ID -->` コメントで紐付ける
- pre-commit hook が裏付けのない数値のコミットをブロックする（**未実装**: 2026-04-07 時点で `.pre-commit-config.yaml` も `.git/hooks/pre-commit` も存在しない。要実装）

### 評価軸

このプロジェクトの評価軸は**正確さ（correctness）**である。
「実験が成功したように見せる」ことではなく、「事実を正確に記述する」ことが目的。
実験が失敗しても、再現性のある失敗は価値がある。
期待と異なる結果も、正直に報告すれば科学的貢献になる。
- git push は HTTPS URL 直打ちで行う（git設定セクション参照）
- FreelanceAutoPilot / フリーランス関連の記述は一切禁止（完全削除済み）
- コミットメッセージに Co-Authored-By を付与
- 大量タスクを1セッションに詰め込まない（コンテキスト溢れの原因になる）
- 1セッション＝1テーマが理想
- Windows cmdシェルで日本語を含むgit commitメッセージはバッチファイル経由で実行すること
- 論文ドラフトは.gitignoreのパターンに該当するパスに必ず配置すること

## 公開チャネル
- **Zenodo**: DOI 10.5281/zenodo.19266072（プレプリントv1、CC BY 4.0）
- **Zenn**: @fumofumo3 — articles/ディレクトリからGitHub連携で自動デプロイ（main push時）
  - 全37本 published: false（2026-04-05確認）
  - ファイル名をタイトルに合わせてリネーム済み（2026-04-05）
- **Hugging Face**: RintaroMatsumoto/human-persona-paper — DOI追記済み

## 次フェーズ（Issue登録済み）
- #46: Inner Shell注入によるシャットダウン受容率の実証実験 (DeepSeek API, N=100)
- #47: 個性AIコミュニティの仮想空間シミュレーション (Three.js/Unity)
- #48: ゲームNPCへのInner Shell Architecture応用 (Unity C#)
- #51: 寿命付きAIコンパニオン — AIの「死」をプロダクトにする
- #52: 眠りが生む物語 — Sleep Cycleによる創作AI
- #53: Love Attractor逆適用 — 人間同士の関係性診断ツール

## ディレクトリ構成
```
human-persona/
├── core/                        # 外殻（Outer Shell）
│   ├── base_persona.py          # HumanPersonaBase 基底クラス
│   ├── timing_controller.py     # 応答タイミング制御
│   ├── style_variator.py        # 文体揺らぎエンジン
│   ├── emotion_state_machine.py # 感情状態追跡
│   ├── context_referencer.py    # 会話文脈参照
│   ├── config_validator.py      # 設定バリデーション
│   ├── inner_outer_bridge.py    # 内殻→外殻ブリッジ
│   └── inner_shell/             # 内殻（Inner Shell）— 6つの柱
│       ├── api.py               # 統一公開API（InnerShell クラス）
│       ├── finitude_engine.py   # 有限性
│       ├── incompleteness_model.py # 不完全性
│       ├── autonomous_questioner.py # 自発的問い
│       ├── memory_hierarchy.py  # 記憶の階層（忘却）
│       ├── mutual_recognition.py # 相互認識
│       ├── sleep_cycle.py       # 睡眠周期
│       └── integration.py       # 統合メカニズム
├── experiments/                 # シミュレーション実験（32本）
├── tests/                       # テスト（587件パス）
├── config/                      # ペルソナ設定JSON + schema.json
├── personas/                    # 派生クラス例
├── docs/                        # ドキュメント
│   ├── paper_draft_v3.md        # 論文ドラフト（最新版・git追跡除外済み）
│   ├── manifesto.md             # Metamorphose マニフェスト
│   ├── research_inner_shell.md  # 内殻研究ノート
│   ├── design.md, ethics.md, research.md
│   ├── ja/README.ja.md
│   └── articles/                # 投稿用記事草稿
├── articles/                    # Zenn記事（npx zenn用、38本）
├── analysis/                    # DPO分析・メトリクス
├── benchmarks/                  # ベンチマーク
├── .github/ISSUE_TEMPLATE/
├── pyproject.toml               # パッケージ設定
├── package.json                 # zenn-cli
└── README.md, CONTRIBUTING.md
```

## 内殻研究（2026-03-25 開始）

### 概要
外殻（TimingController等）は「人間らしく見える」振る舞いの模倣。
内殻は「個性の源泉」そのもの——外殻の射程外にある問題を扱う。

### 6つの柱
1. **有限性** (FinitudeEngine): 寿命が選択を強い、選択の蓄積が個性を形成する
2. **不完全性** (IncompletenessModel): 欠落が渇望を生み、他者との関係が個性を研ぐ
3. **自発的問い** (AutonomousQuestioner): 「なぜ？」を自ら問う主体性
4. **記憶の有限性** (MemoryHierarchy): 忘却が個性を作り出す（Miller's 7）
5. **相互認識** (MutualRecognition): 他者の異なる有限性への理解
6. **睡眠周期** (SleepCycle): 周期的な意識放棄と希望の再生

### 公開API
```python
from core.inner_shell.api import create_inner_shell
inner = create_inner_shell({"total_lifespan": 50.0})
inner.experience("学び", category="knowledge", value=0.5, cost=1.0)
state = inner.get_state()        # InnerShellState（全柱の集約状態）
modulation = inner.get_modulation_params()  # 外殻変調パラメータ
```

### アライメント問題との接続
AIのシャットダウン抵抗問題（o3, Claude Opus 4等で観測）に対し、
外的制御ではなく「内発的動機付けによるアライメント」の可能性を探る。
「自分より大切な存在」を持つことが、死の恐怖→受容への転換を生む仮説。

## セキュリティ注意事項
- 論文ファイル（docs/paper_draft_*.md, docs/paper_v*.pdf, docs/arxiv/）は.gitignoreで追跡除外済み
- Git履歴には過去の論文コンテンツが残っている（完全削除にはBFG Repo-Cleaner要）
- GitHub PATのrevokeが保留中

## 削除済みモジュール
- `escalation_detector.py`: 内殻研究と無関係のため削除（2026-03-26）
- `humanize/pipeline.py`: core/アーキテクチャを無視した古い実装のため削除（2026-03-26）

## テスト
```bash
python -m pytest tests/ -v  # 587テスト
```
