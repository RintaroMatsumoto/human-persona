#!/usr/bin/env python3
"""
dev.to に記事を投稿・更新するスクリプト.

Usage:
    # APIキーは環境変数 DEVTO_API_KEY、または key_token/dev_to_2.txt から自動読み込み

    # 新規投稿（ドラフト）
    python scripts/publish_to_devto.py post articles-en/40-dusty-toolbox.md
    # 新規投稿（公開）
    python scripts/publish_to_devto.py post articles-en/40-dusty-toolbox.md --publish

    # 既存記事を更新（記事IDを直接指定）
    python scripts/publish_to_devto.py update articles-en/40-dusty-toolbox.md --id 1234567
    # 既存記事を更新（slug自動マッチ：自分の記事一覧から title 一致で探す）
    python scripts/publish_to_devto.py update articles-en/40-dusty-toolbox.md

    # 全記事を一括更新（articles-en/*.md をローカル → DEV.to title 一致でマッチ）
    python scripts/publish_to_devto.py update-all
    # ドライラン（実際の PUT は送らずマッチ結果だけ表示）
    python scripts/publish_to_devto.py update-all --dry-run

読み取るフロントマターフィールド:
    title, published, tags, series, canonical_url, description, cover_image (→ main_image)
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error


DEVTO_API_URL = "https://dev.to/api/articles"
DEVTO_ME_URL = "https://dev.to/api/articles/me/all"


# ---------- frontmatter ----------

def parse_frontmatter(text: str) -> tuple[dict, str]:
    """YAML風フロントマターを簡易パースして (metadata, body) を返す."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}, text
    meta_block = m.group(1)
    body = text[m.end():]
    meta: dict = {}
    for line in meta_block.splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()
        # 両端の引用符を剥がす
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        meta[key] = val
    return meta, body


def build_article_payload(meta: dict, body: str, publish_override: bool | None = None) -> dict:
    """frontmatter から DEV.to API ペイロードを組む."""
    title = meta.get("title", "").strip()

    # tags: カンマ区切り → list[str]、最大4個、空白除去・小文字化
    tags_raw = meta.get("tags", "")
    tags = [t.strip().lower() for t in tags_raw.split(",") if t.strip()][:4]

    # published: frontmatter の "true"/"false" をそのまま尊重、--publish 上書きあり
    if publish_override is not None:
        published = publish_override
    else:
        published = str(meta.get("published", "false")).strip().lower() == "true"

    article: dict = {
        "title": title,
        "body_markdown": body.strip(),
        "published": published,
    }
    if tags:
        article["tags"] = tags
    if meta.get("series"):
        article["series"] = meta["series"]
    if meta.get("canonical_url"):
        article["canonical_url"] = meta["canonical_url"]
    if meta.get("description"):
        article["description"] = meta["description"]
    # DEV.to API のフィールド名は main_image。frontmatter は cover_image で書く
    cover = meta.get("main_image") or meta.get("cover_image")
    if cover:
        article["main_image"] = cover

    return {"article": article}


# ---------- HTTP ----------

def _request(url: str, method: str, api_key: str, payload: dict | None = None, max_retries: int = 3) -> dict | list:
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    backoff = 5  # 初回 429 後の待機秒数
    for attempt in range(max_retries + 1):
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "publish_to_devto/2.0",
                "api-key": api_key,
            },
            method=method,
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if e.code == 429 and attempt < max_retries:
                retry_after = e.headers.get("Retry-After")
                wait = int(retry_after) if retry_after and retry_after.isdigit() else backoff
                print(f"  429 received, sleeping {wait}s then retrying (attempt {attempt+2}/{max_retries+1})", file=sys.stderr)
                time.sleep(wait)
                backoff *= 3  # 5 → 15 → 45
                continue
            print(f"HTTP {e.code} on {method} {url}: {body}", file=sys.stderr)
            raise


def post_article(filepath: str, api_key: str, publish_override: bool | None) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    meta, body = parse_frontmatter(content)
    payload = build_article_payload(meta, body, publish_override)
    return _request(DEVTO_API_URL, "POST", api_key, payload)  # type: ignore[return-value]


def put_article(filepath: str, article_id: int, api_key: str, publish_override: bool | None) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    meta, body = parse_frontmatter(content)
    payload = build_article_payload(meta, body, publish_override)
    return _request(f"{DEVTO_API_URL}/{article_id}", "PUT", api_key, payload)  # type: ignore[return-value]


def fetch_my_articles(api_key: str) -> list[dict]:
    """自分の全記事（公開＋下書き）をページング取得."""
    out: list[dict] = []
    page = 1
    while True:
        url = f"{DEVTO_ME_URL}?page={page}&per_page=100"
        data = _request(url, "GET", api_key)
        if not isinstance(data, list) or not data:
            break
        out.extend(data)
        if len(data) < 100:
            break
        page += 1
    return out


def find_article_id_by_title(title: str, my_articles: list[dict]) -> int | None:
    for a in my_articles:
        if a.get("title", "").strip() == title.strip():
            return a.get("id")
    return None


# ---------- subcommands ----------

def cmd_post(args, api_key: str):
    publish_override = True if args.publish else None
    result = post_article(args.file, api_key, publish_override)
    _print_result("POST", result)


def cmd_update(args, api_key: str):
    article_id = args.id
    if not article_id:
        # ローカル frontmatter の title でマッチ
        with open(args.file, "r", encoding="utf-8") as f:
            meta, _ = parse_frontmatter(f.read())
        title = meta.get("title", "").strip()
        if not title:
            print("Error: title が読み取れない。--id で指定してください", file=sys.stderr)
            sys.exit(1)
        print(f"Looking up article by title: {title!r}")
        my_articles = fetch_my_articles(api_key)
        article_id = find_article_id_by_title(title, my_articles)
        if not article_id:
            print(f"Error: title 一致の記事が見つかりません: {title!r}", file=sys.stderr)
            sys.exit(1)
        print(f"  → matched id={article_id}")

    publish_override = None
    if args.publish:
        publish_override = True
    elif args.unpublish:
        publish_override = False

    result = put_article(args.file, article_id, api_key, publish_override)
    _print_result("PUT", result)


def cmd_update_all(args, api_key: str):
    articles_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "articles-en",
    )
    files = sorted(
        os.path.join(articles_dir, f)
        for f in os.listdir(articles_dir)
        if f.endswith(".md")
    )
    print(f"Local articles: {len(files)} files")

    print("Fetching DEV.to article list...")
    my_articles = fetch_my_articles(api_key)
    print(f"DEV.to articles: {len(my_articles)}")

    plan: list[tuple[str, int, str]] = []  # (filepath, id, title)
    misses: list[str] = []
    for fp in files:
        with open(fp, "r", encoding="utf-8") as f:
            meta, _ = parse_frontmatter(f.read())
        title = meta.get("title", "").strip()
        if not title:
            misses.append(f"{os.path.basename(fp)} (no title)")
            continue
        aid = find_article_id_by_title(title, my_articles)
        if aid is None:
            misses.append(f"{os.path.basename(fp)} → {title!r} (no match)")
            continue
        plan.append((fp, aid, title))

    print(f"\nMatched: {len(plan)}")
    for fp, aid, title in plan:
        print(f"  [{aid}] {os.path.basename(fp)}  →  {title}")

    if misses:
        print(f"\nUnmatched ({len(misses)}):")
        for m in misses:
            print(f"  - {m}")

    if args.dry_run:
        print("\n[dry-run] No PUT requests sent.")
        return

    if not plan:
        print("\nNothing to update.")
        return

    print(f"\nSending PUT for {len(plan)} articles (5s interval, 429 retry enabled)...")
    ok = 0
    failed: list[tuple[int, str]] = []
    for fp, aid, title in plan:
        try:
            put_article(fp, aid, api_key, publish_override=None)
            print(f"  OK   [{aid}] {os.path.basename(fp)}")
            ok += 1
        except Exception as e:
            print(f"  FAIL [{aid}] {os.path.basename(fp)}: {e}")
            failed.append((aid, os.path.basename(fp)))
        time.sleep(5)  # DEV.to レート制限への配慮。429 は _request 側でリトライする
    print(f"\nDone. OK={ok}, FAIL={len(failed)}")
    if failed:
        print("Failed articles (re-run individually):")
        for aid, name in failed:
            print(f"  python scripts/publish_to_devto.py update articles-en/{name} --id {aid}")


def _print_result(verb: str, result: dict):
    import io, sys as _sys
    out = io.TextIOWrapper(_sys.stdout.buffer, encoding="utf-8", errors="replace")
    out.write("\n" + "=" * 60 + "\n")
    out.write(f"  {verb}\n")
    out.write(f"  Title: {result.get('title', '?')}\n")
    out.write(f"  URL:   {result.get('url', '?')}\n")
    out.write(f"  ID:    {result.get('id', '?')}\n")
    out.write(f"  State: {'Published' if result.get('published') else 'Draft'}\n")
    out.write("=" * 60 + "\n")
    out.flush()


# ---------- entry ----------

def load_api_key() -> str:
    key = os.environ.get("DEVTO_API_KEY", "").strip()
    if key:
        return key
    # フォールバック: key_token/dev_to_2.txt
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    key_path = os.path.join(repo_root, "key_token", "dev_to_2.txt")
    if os.path.exists(key_path):
        with open(key_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    print("Error: DEVTO_API_KEY が見つかりません。環境変数か key_token/dev_to_2.txt に設定してください", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="dev.to に記事を投稿・更新する")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_post = sub.add_parser("post", help="新規投稿")
    p_post.add_argument("file", help="記事ファイル (.md)")
    p_post.add_argument("--publish", action="store_true", help="公開状態で投稿（デフォルトはfrontmatterに従う）")

    p_upd = sub.add_parser("update", help="既存記事を更新")
    p_upd.add_argument("file", help="記事ファイル (.md)")
    p_upd.add_argument("--id", type=int, default=None, help="DEV.to article ID（指定なければ title でマッチ）")
    p_upd.add_argument("--publish", action="store_true", help="公開状態に切り替え")
    p_upd.add_argument("--unpublish", action="store_true", help="ドラフトに戻す")

    p_all = sub.add_parser("update-all", help="articles-en/*.md を一括 PUT")
    p_all.add_argument("--dry-run", action="store_true", help="マッチ結果だけ表示し PUT は送らない")

    args = parser.parse_args()
    api_key = load_api_key()

    if args.cmd == "post":
        cmd_post(args, api_key)
    elif args.cmd == "update":
        cmd_update(args, api_key)
    elif args.cmd == "update-all":
        cmd_update_all(args, api_key)


if __name__ == "__main__":
    main()
