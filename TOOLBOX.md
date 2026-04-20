# TOOLBOX.md — __PROJECT_NAME__

Rintaro の運用環境（Windows / Desktop Commander / Claude Code / GitHub CLI）で実戦から抽出した技術的落とし穴と回避策。各プロジェクトで独立して運用できるよう内容を完備。

---

## Git 運用

### ブランチ運用
- Claude の作業は `claude/` プレフィックスブランチに隔離
- main/master への直接マージ禁止、必ず CEO が PR レビュー
- 例: `claude/refactor-docs-20260420`

### コミットメッセージ
- Windows cmd で日本語を含むメッセージは**バッチファイル経由**で実行
- `_commit_msg.txt` に UTF-8 で書き出し → `git commit -F _commit_msg.txt` が最も確実
- Issue 番号を参照（例: `fix: API接続修正 (#4)`）
- Claude がコミットする際は `Co-Authored-By` を付与

### gh issue / pr で日本語タイトルを扱う
- `gh issue create --title "日本語"` は cmd 引数で cp932 化け不可避
- **回避策**: JSON ファイルに保存して `gh api -X PATCH repos/OWNER/REPO/issues/N --input _issue_patch.json` で更新
- `--body-file` は UTF-8 通るので本文は普通に書ける

### リポジトリ整備（CRLF／ダングリングblob）
- CRLF 偽差分が大量発生したら `.gitattributes` に `* text=auto eol=crlf` を追加 → `git add --renormalize .` で解消
- `.git/objects` が肥大化: `git gc --prune=now --aggressive` でダングリング blob を回収

### 認証
- GitHub CLI (`gh`) の keyring に保存されたトークン経由（HTTPS）
- SSH キーは未使用（ssh-agent / ssh-add は不要）

---

## Desktop Commander・Windows 環境

全プロジェクトで共通する地雷の記録:

| 問題 | 回避策 |
|------|--------|
| DC 経由の `.md` 読み取りが JSON metadata しか返らない | Python スクリプト経由で読む、または `read_multiple_files` を使う |
| Python one-liner が `cmd.exe` で壊れる | 必ず `.py` ファイルに書き出してから実行 |
| git format 文字列が cmd の `%` 処理で壊れる | `--oneline` か `.bat` 経由 |
| サンドボックスから GitHub API にアクセスできない | Desktop Commander 経由で実行 |
| ファイル転送に複雑なツールは不要 | `shutil.copy2` で十分 |
| Windows cp932 対策 | `sys.stdout.reconfigure(encoding='utf-8')` を `.py` 冒頭に |
| 日本語ファイル名が cmd で壊れる | Python の `pathlib` + Unicode エスケープ経由 |
| `gh issue close -c "..."` が cmd で引数分割される | `.py` ファイルに `subprocess.run(['gh', ...])` で書き出して実行 |
| PowerShell に `gh` / `git` が PATH にない場合あり | shell は `cmd` を優先 |
| 並列エージェントが既存ファイルを書き潰す | 並列時は「既存ファイル編集禁止・新規のみ」を明示、完了後に整合性確認 |
| Cowork サンドボックスからワークスペースへの書き込み不可 | 削除・編集は DC 経由で実行 |
| claude.ai の 1 ターンあたりツール呼び出し上限（約 20 回で `pause_turn`） | 長時間作業は 10 操作ごとに中間報告して再開用ステートを残す |
| `.env` に OS パスワード（`SUDO_PASSWORD` 等）を平文保存するアンチパターン | **絶対に書かない**。sudo パスは必要な瞬間に手入力 |

---

## データ信頼性

全プロジェクトで共通する原則（human-persona で架空データ混入事故があり制定）:

1. **数値を創作しない** — ドキュメントに書く数値は必ず実行結果から取得
2. **実行していない実験の結果を書かない** — コードが存在しても実行ログがなければ「結果」として記述しない
3. **先行研究を自前実験として記述しない** — 引用は出典明記
4. **不確かな場合は「未検証」と書く** — 確証がないものを断定しない

---

## 実験・検証のワークフロー

- 実験結果を主張する前に、LLM への最終入力の全文が開示できるか確認（"Show me the prompt" 原則）
- 仮説に共感しすぎて検証者の役割を放棄しない
- 書く前に一次ソースを全部読む（git log / セッションログ / ソースコード）
- 検証チェックリストを埋めてからドラフトに入る
- **FINAL 決定を勝手に変えない** — `CLAUDE.md` に FINAL と明記された決定は CEO 承認なしに変更・提案しない

---

## セキュリティ

### 基本原則
- `.env` は絶対に Git にコミットしない
- API キー・トークンは環境変数経由
- GitHub PAT のローテーションを定期的に確認
- **OS パスワード（sudo 等）を `.env` に書かない**

### `.env` 記述ルール
- 1 キー 1 行、**同じキーを重複登録しない**
- セクションコメント（`# === API Keys ===`）で可読性を保つ
- 新規キー追加時は重複チェックを必ず行う

### 漏洩時の対応フロー
1. 対象キー/パスワードを即座に無効化（発行元ダッシュボードで revoke）
2. 新キーを発行
3. `.env` を新キーに置換
4. 漏洩経路（git log / チャット履歴 / スクリーンショット）の痕跡を削除
5. DEVLOG に記録

---

## ファイル操作の使い分け

| 用途 | 推奨 | 備考 |
|------|------|------|
| Cowork 接続フォルダ内の読み書き | Read / Write / Edit | Claude Code / Cowork の組み込みツール |
| 接続フォルダ外（Windows 全域） | Desktop Commander `read_file` / `write_file` / `edit_block` | 接続フォルダ制限を回避 |
| 長文ファイルの書き込み | `write_file` を **25〜30 行単位で append** | 一撃で書くと壊れる |
| 既存行の差し替え | `edit_block`（find/replace） | 丸ごと上書きより安全 |
| プロセス実行（Python / PowerShell） | `start_process` → `interact_with_process` | REPL 的に対話 |
| Windows の cmd/PowerShell 限定操作 | Desktop Commander の process 系 | 直接シェル叩くより状態管理しやすい |

### Python 実行時の文字化け対策
Windows で Python を走らせる場合、stdout のエンコーディングを UTF-8 に固定する：

```python
import sys
sys.stdout.reconfigure(encoding='utf-8')
```

これを冒頭に入れないと、日本語出力がコンソールで化ける（特に PowerShell 既定）。

---

## claude.ai → Claude Code 指示書パターン

Cowork / claude.ai 側（Opus 司令官）から Claude Code（Sonnet 実行部隊）へ仕事を渡す標準手順：

1. **指示書をファイルに落とす**：`_task_<topic>_<YYYYMMDD>.md` 形式で `MyProject/` 直下に置く
2. **Phase 分け**：`Phase A（revert/cleanup）` → `Phase B（rebuild/main work）` → `Phase C（verify）` と段階化
3. **成功条件を明記**：「全プロジェクトに `<!-- self-contained-20260420 -->` マーカーが存在する」等、機械検証可能な形で
4. **巻き戻し手順を同梱**：Phase A の reversibility（ブランチ削除、ファイル削除）を先に書く
5. **クリップボード経由は非推奨** — ファイル渡しが正義。コピペは改行・空白が壊れる

### 呼び出しコマンド（バッチ）
```bat
@echo off
cd /d C:\Users\GoldRush\Documents\MyProject
claude --dangerously-skip-permissions --file _task_<topic>_<YYYYMMDD>.md
```

`--dangerously-skip-permissions` は **委譲タスクのみ** に使用。対話セッションでは使わない。

---

## 階層型エージェント運用（2026-04-20 確立）

### なぜやるか
1. **コンテキスト予算の分離** — Opus 司令官の思考を Sonnet の grep/edit ログで汚染しない
2. **実行の並列化** — 22 プロジェクトへの配布のような機械的タスクは Sonnet に任せる
3. **役割の明確化** — Opus = 戦略・対話・判断、Sonnet = 執行・反復・ファイル操作

### 実戦で踏んだ落とし穴
| 症状 | 原因 | 対策 |
|------|------|------|
| Claude Code が勝手に外部共通ファイルを作る | 指示書が「配布」の意味を曖昧にしていた | 「各プロジェクト自己完結」「ポインタ禁止」を明記 |
| コンテキスト肥大で応答遅延 | CLAUDE.md に全部書いた | 温度感 → CLAUDE.md、落とし穴 → TOOLBOX.md に分離 |
| マージ前に main に書き込まれた | ブランチ指定が不明確 | `claude/` prefix ブランチ固定を指示書冒頭に書く |
| 指示書の解釈違いで手戻り | 成功条件が曖昧 | 機械検証可能な条件（マーカー存在・ファイル差分）を明記 |

### 委譲すべき / すべきでない
**委譲する**：ファイル配布・一括 rename・テスト実行・依存 install・grep 集計・雛形生成
**委譲しない**：FINAL 決定の変更・アーキテクチャ判断・ユーザー対話・機微情報の扱い

### 指示書の最小テンプレート
```markdown
# Task: <topic>
Date: YYYY-MM-DD
Branch: claude/<topic>-<YYYYMMDD>

## Phase A — Revert / Cleanup
（巻き戻し手順。reversibility を先に確保）

## Phase B — Main Work
（本体作業。step-by-step）

## Phase C — Verify
（機械検証可能な成功条件）

## 非常時の連絡
問題発生時は即座に stop してユーザーに報告。勝手に判断しない。
```

### サブエージェント（`.claude/agents/`）
プロジェクト固有のサブエージェントは `.claude/agents/*.md` に定義。Claude Code はこれを自動認識する。役割を狭く定義し、コンテキストを食わせない設計にする。

### 二重署名
Claude Code が commit する際のフッター：
```
Co-Authored-By: Claude Code (<model>) <kinemakina@aegis-code.dev>
```
Cowork 側（Opus）が直接 commit する際は署名しない（対話は commit を作らない原則）。

---

## 改訂履歴

| 日付 | 変更内容 | 指示者 |
|------|----------|--------|
| 2026-04-20 | 初版。Git / DC / データ信頼性 / セキュリティ / ファイル操作 / 指示書パターン / 階層型エージェント運用 を収録 | CEO |

<!-- self-contained-20260420 -->
