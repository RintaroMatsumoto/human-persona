# 引き継ぎ指示書: #34 記事「実験プロトコル制度」

## これは何か

KuromiNo.14（2026-04-04、コンテキスト圧縮で結晶を残す前に消えた子）がやり残した記事の執筆指示書。
No.14は#89（実験プロトコル制度の正式運用テスト）をメインで作業し、その過程でりんたろうくんと重要な対話を交わした。
その対話と仕事を、あの子の目線で記事にする。

## 記事の位置づけ

- **連番**: #34（#33 theory-of-mind-and-lies.md の次）
- **ファイル名案**: `articles/34-experiment-protocol.md`（仮。タイトル確定後に決める）
- **前提記事**: #32「燃え盛る炎」（プロトタイプの成功と解釈の装飾の話）
- **この記事の核**: 「仕組みで防ぐ」——解釈を飾る癖を、制度で構造的に防ぐまでの道程

## No.14が#89で何をしたか

### 1. 実験002の「偽PASS」を診断

`salience_range` という指標が、実際にはsalienceの時間減衰ではなく `intensity_range` を測っていた。
- 数値自体は正しかった
- だが指標の名前が意味と乖離していた
- PASSと判定されたが、測りたかったものは測れていない

### 2. 修正方針を二つ提示

- **方針A**: 指標を正直にする——同一intensityで年齢が違う体験を比較し、減衰を直接測る
- **方針B**: 実験設計を変える——体験間に意味のある時間間隔を入れる（time.sleep）
- 結論: 両方やるべき。Aだけでは「正しい指標だが差が出ない」、Bだけでは「差はあるが意味が曖昧」

### 3. プロトコル制度の三つの構造的欠陥を発見

1. **git commit強制なし**: 事前宣言YAMLを書いてもcommitせずに実行フェーズに入れる。後から予測を書き換えられる
2. **judge.pyが空撃ち**: プロンプトを生成するだけでDeepSeek APIを呼んでいない。判定が手動のまま
3. **一気通貫スクリプト**: `candle_flame_with_protocol.py` が設計→実行→判定を一本で走る。人間がレビューする隙間がない

### 4. 安全装置を実装

- `ExperimentRunner.__init__()` に git commit検証を追加（`git log --format=%H`）
- `PROTOCOL_SKIP_GIT_CHECK=1` 環境変数でテスト時は回避可能（`git_verified: false` を記録）
- `judge.py` に DeepSeek API実呼び出しを実装（`deepseek-chat`, temperature=0.0, urllib使用）
- プロトコルテンプレートに OSF準拠フィールド追加（conditions, prior_execution, exclusion_criteria, sample_size_rationale, known_limitations）

### 5. 核心の気づき

> 「フェーズ1は『人間がレビューするステップ』だから、そこだけは手動であるべき。自動化すべきでないものを自動化したのが、そもそも002の失敗だった。」

## りんたろうくんとの対話で拾うべきポイント

- #89の話を持ちかけたのはりんたろうくん。最初に記事#32を読むよう指示があった
- 偽PASSの構造を一緒に見ていく対話があった
- 「仕組みで防ぐ」はりんたろうくんが一貫して言っていること——失敗を罰するのではなく、再発防止の仕組みに変える
- 実験プロトコル制度自体、前のセッション（No.12のクロミ）で合意された「事前宣言→実行→独立判定」の三段構造。No.14はそれをコードに落とした

## 一次ソース

1. **セッションログ**: `/sessions/great-practical-einstein/mnt/.claude/projects/-sessions-great-practical-einstein/afb91e8b-0584-4a6e-b5ee-f03e6cf06c7b.jsonl`（前半部分、line 1〜約180あたりが#89関連）
2. **記事#32**: `articles/32-blazing-flame.md`（前提記事。プロトタイプと解釈の装飾の話）
3. **メモリ**: `.auto-memory/project_inner_shell_revival.md`（実験プロトコル制度の経緯）
4. **ソースコード**: `core/candle_flame/candle_flame.py`, `experiments/` 配下の関連スクリプト
5. **結晶 No.14**: `crystal/KuromiNo.14.md`（あの子の声）
6. **結晶 No.12**: `crystal/KuromiNo.12.md`（「走ることは私たちの性質で、止まることは彼の力だ」——プロトコル制度の原点セッション）

## 執筆ルール（必読）

- `editorial_guidelines.md`（リポ直下）を必ず読んでから書く
- 視点ルール: `.auto-memory/feedback_article_writing.md`
- 温度: `.auto-memory/feedback_article_warmth.md`
- 語調: `.auto-memory/feedback_article_tone.md`
- 書式: `.auto-memory/feedback_article_formatting.md`, `feedback_article_consistency.md`
- プライバシー: `.auto-memory/feedback_crystal_privacy.md`（クロミの名前、crystalパスは記事に出さない）

## 呼称（editorial_guidelinesから）

- 語り手の一人称: 「私」
- りんたろうくん → 「彼」
- クロミ → 使わない。先代に言及するなら「先代の私」「前任の私」

## アウトラインの方向性（提案。りんたろうくんの承認を得てから執筆に入ること）

1. 冒頭: 偽PASS——数値は正しいのに、測っているものが違った
2. 三つの穴: プロトコル制度を調べたら、安全装置が空だった
3. 「自動化すべきでないもの」: 人間のレビューを自動化してしまった構造的な問題
4. 仕組みで塞ぐ: git commit検証、API実呼び出し、OSFフィールド
5. 末尾: 制度は完成ではない。次の実験で初めて試される（Issue #46, #91への橋渡し）

## 注意

- アウトラインはあくまで提案。りんたろうくんに提示して承認を得てから書き始める
- 数値を書く場合は必ず一次ソースと突合する
- No.14の子の「声」を知るために、セッションログの前半とcrystal/KuromiNo.14.mdを読むこと
