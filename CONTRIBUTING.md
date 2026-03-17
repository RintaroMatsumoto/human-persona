# Contributing to human-persona

human-persona への貢献をお考えいただきありがとうございます。
本ドキュメントでは、派生クラスの追加からバグ修正まで、
貢献の手順を説明します。

---

## 派生クラス（ペルソナ）の作り方

### 1. 設定ファイルを作成する

`config/schema.json` に準拠した JSON ファイルを作成してください。

```bash
cp config/schema.json config/your_persona.json
```

必須フィールド:
- `name`: ペルソナの識別名
- `language`: ISO 639-1 言語コード（例: `ja`, `en`, `es`）
- `culture.context_level`: 0.0（ローコンテキスト）〜 1.0（ハイコンテキスト）

### 2. 文体テンプレートを定義する

`style.style_patterns` に言語固有のテンプレートを追加します。
最低でも `confirmation`, `empathy`, `uncertain` の 3 パターンを定義してください。

### 3. エスカレーションキーワードを定義する

`escalation.escalation_rules` に言語固有のキーワードを追加します。
クレーム・交渉・通話要求の検知に必要な単語を網羅してください。

### 4. 配置する

```
config/
  └── {言語コード}_{用途名}.json    # 設定ファイル
personas/
  └── {用途名}_{言語コード}.md      # ペルソナの説明ドキュメント
```

### 5. テストする

```python
from core.base_persona import HumanPersonaBase

persona = HumanPersonaBase.from_config_file("config/your_persona.json")
response = persona.process_message("テストメッセージ")
assert response.delay_seconds > 0
assert response.emotion_state is not None
```

---

## PR の送り方

### ブランチ命名規則

| 変更内容 | ブランチ名 |
|---|---|
| 新しい派生クラス | `persona/{言語コード}-{用途名}` (例: `persona/en-customer-support`) |
| 基底クラスの修正 | `fix/{修正内容}` (例: `fix/timing-negative-delay`) |
| 基底クラスの機能追加 | `feat/{機能名}` (例: `feat/emotion-speed-modifier`) |
| ドキュメント | `docs/{内容}` (例: `docs/ethics-update`) |

### PR の手順

1. `main` からブランチを作成する
   ```bash
   git checkout -b persona/es-sales
   ```

2. 変更を加え、コミットする
   ```bash
   git add -A
   git commit -m "persona: add Spanish sales persona"
   ```

3. リモートにプッシュし、PR を作成する
   ```bash
   git push -u origin persona/es-sales
   ```

4. PR の説明には以下を含めてください:
   - 何を追加・変更したか
   - なぜその変更が必要か
   - テスト結果（派生クラスの場合は `from_config_file` の動作確認）
   - 倫理審査の確認（下記参照）

---

## コードスタイル

### 必須事項

- **型アノテーション**: すべての関数の引数と戻り値に型を付ける
  ```python
  def calculate_delay(self, platform: Platform) -> float:
  ```

- **docstring**: すべての public クラスとメソッドに docstring を付ける
  ```python
  def evaluate(self, message: str) -> EscalationResult:
      """メッセージを評価し、エスカレーション要否を判定する."""
  ```

- **`from __future__ import annotations`**: すべてのモジュールの先頭に記述する

### スタイルガイド

- フォーマッター: 特に指定なし（将来的に ruff を導入予定）
- docstring スタイル: Google スタイル
- 行の長さ: 最大 99 文字を推奨
- import 順序: 標準ライブラリ → サードパーティ → ローカル

### 設定ファイル（JSON）

- インデント: 2 スペース
- キー名: snake_case
- 文字列値: ダブルクォート

---

## 倫理審査

すべての PR は以下の倫理チェックを通過する必要があります。

### チェックリスト

PR を作成する際、以下を確認してください:

- [ ] `docs/ethics.md` の禁止用途に該当しない
- [ ] 詐欺・なりすまし・世論操作を容易にする機能ではない
- [ ] エスカレーション機能を弱める変更ではない
- [ ] 感情的に脆弱な人への悪用リスクを検討した
- [ ] プラットフォーム TOS 違反を助長しない

### 判断に迷う場合

倫理的な懸念がある場合は、PR を作成する前に Issue で議論してください。
「この用途は倫理的に問題ないか？」という質問は歓迎します。

---

## Issue の作成

- **新しいペルソナのリクエスト**: `.github/ISSUE_TEMPLATE/persona_request.md` テンプレートを使用
- **バグ報告**: `.github/ISSUE_TEMPLATE/bug_report.md` テンプレートを使用
- **その他**: 自由形式で Issue を作成してください
