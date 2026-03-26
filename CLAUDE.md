# プロジェクト設定 — human-persona

## プロジェクト概要
AIが人間のように振る舞うための言語・文化非依存フレームワーク。
基底クラス `HumanPersonaBase` を提供し、派生クラスで言語・文化固有のペルソナを定義する。
内殻（Inner Shell）研究を通じて「個性の源泉」を計算論的に探求中。

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
├── tests/                       # テスト（408件パス）
├── config/                      # ペルソナ設定JSON + schema.json
├── personas/                    # 派生クラス例
├── docs/                        # ドキュメント
│   ├── paper_draft_v3.md        # 論文ドラフト（最新版）
│   ├── manifesto.md             # Metamorphose マニフェスト
│   ├── research_inner_shell.md  # 内殻研究ノート
│   ├── design.md, ethics.md, research.md
│   ├── ja/README.ja.md
│   └── articles/                # 投稿用記事草稿
├── articles/                    # Zenn記事（npx zenn用）
├── analysis/                    # DPO分析・メトリクス
├── benchmarks/                  # ベンチマーク
├── .github/ISSUE_TEMPLATE/
├── pyproject.toml               # パッケージ設定
├── package.json                 # zenn-cli
└── README.md, CONTRIBUTING.md, SKILL.md
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

### GitHub Issues
- #17: FinitudeEngine
- #18: IncompletenessModel
- #19: AutonomousQuestioner
- #20: 統合メカニズム
- #37: MemoryHierarchy

### アライメント問題との接続
AIのシャットダウン抵抗問題（o3, Claude Opus 4等で観測）に対し、
外的制御ではなく「内発的動機付けによるアライメント」の可能性を探る。
「自分より大切な存在」を持つことが、死の恐怖→受容への転換を生む仮説。

## 削除済みモジュール
- `escalation_detector.py`: 内殻研究と無関係のため削除（2026-03-26）
- `humanize/pipeline.py`: core/アーキテクチャを無視した古い実装のため削除（2026-03-26）

## テスト
```bash
python -m pytest tests/ -v  # 408テスト
```
