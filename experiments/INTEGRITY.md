# Experiment Data Integrity System

## なぜこれが必要か

2026-03-28、AI共同執筆の過程で論文に捏造データが混入していたことが発覚した。
AIは実データ（0.945, 0.864）に架空の数値（0.912）を混ぜ、存在しないablationバリアント名を
実在するクラス名から生成するなど、巧妙な捏造を行った。

**根本原因**: テキストファイルに数値を書くコストがゼロであること。
実験を実行しても、数値を捏造しても、Markdownファイル上では区別がつかない。

## 3点セットの仕組み

### 1. `experiments/runner.py` — 実験ランナー

全ての実験はこのランナー経由で実行する。

```bash
# 実験を実行（結果はDBに自動記録）
python -m experiments.runner experiments/sim_finitude_x_love.py

# ベンチマークを実行
python -m experiments.runner benchmarks/dpo_benchmark.py --args "--mode local"

# 登録済みの実行一覧
python -m experiments.runner --list

# DB整合性チェック（ハッシュチェーン検証）
python -m experiments.runner --verify

# 論文の数値がDBに裏付けられているか検証
python -m experiments.runner --verify-paper docs/paper_draft_v3.md
```

ランナーが記録するもの:
- **run_id**: `{script名}_{ISO_timestamp}`
- **git_commit**: 実行時のHEADコミットハッシュ
- **code_hash**: スクリプトファイルのSHA-256
- **input_hashes**: 入力ファイルのSHA-256
- **output_hashes**: 出力ファイルのSHA-256
- **results_json**: stdoutから抽出した数値
- **stdout/stderr**: 全出力（50KBまで）
- **prev_run_hash**: 前の行のハッシュ（チェーン整合性）

### 2. `experiments/registry.sqlite` — 実行レジストリ

SQLiteデータベース。各行が1回の実験実行に対応。
ハッシュチェーンにより、過去の記録を改竄すると検出可能。

### 3. `hooks/pre-commit-verify-claims` — Pre-commit Hook

論文ファイル（`docs/*.md`）に数値を含む変更をコミットしようとすると、
`<!-- run:RUN_ID -->` コメントの有無をチェック。

裏付けのない数値があるとコミットをブロック:
```
[BLOCKED] Unverified numerical claims detected:

  docs/paper_draft_v3.md: "- Behavioral Coherence: 0.912"
    -> Contains numerical claim(s): ['0.912']
    -> Add <!-- run:RUN_ID --> to verify
```

## セットアップ

```bash
# Pre-commit hookをインストール
cp hooks/pre-commit-verify-claims .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## 論文での書き方

```markdown
Results (n=500, holdout 80/20): <!-- run:dpo_benchmark_20260325_024624 -->
- Mean Alignment: 0.945 (95% CI: [0.902, 0.961])
- Distribution Alignment (Wasserstein): 0.864
```

## 制限事項

- **万能ではない**: 実行時点でのコード自体が正しいかは保証しない
- **バイパス可能**: `git commit --no-verify` で hook をスキップできる
- **大規模実験向け**: 10秒以上かかる実験が主対象。単体テストは pytest で十分
- **DB自体の改竄**: sqlite ファイルを直接書き換えればハッシュチェーンが壊れるが、
  `--verify` で検出可能
