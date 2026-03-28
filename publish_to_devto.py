#!/usr/bin/env python3
"""
dev.to に記事を投稿するスクリプト.

Usage:
    # 環境変数にAPIキーを設定
    set DEVTO_API_KEY=your_api_key_here

    # ドラフトとして投稿（デフォルト）
    python publish_to_devto.py articles/quiet-child-ai-safety-en.md

    # 公開状態で投稿
    python publish_to_devto.py articles/quiet-child-ai-safety-en.md --publish

    # シリーズ名を指定
    python publish_to_devto.py articles/quiet-child-ai-safety-en.md --series "HumanPersonaBase"

記事ファイルのフロントマター (YAML) から title, tags を読み取る。
published フラグは --publish オプションで上書き可能。
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error


DEVTO_API_URL = "https://dev.to/api/articles"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """YAML風フロントマターを簡易パースし、(metadata, body) を返す."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}, text
    meta_block = m.group(1)
    body = text[m.end():]
    meta = {}
    for line in meta_block.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            meta[key] = val
    return meta, body


def publish_article(
    filepath: str,
    api_key: str,
    publish: bool = False,
    series: str | None = None,
) -> dict:
    """dev.to APIで記事を投稿し、レスポンスを返す."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    meta, body = parse_frontmatter(content)
    title = meta.get("title", os.path.basename(filepath))
    tags_raw = meta.get("tags", "")
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()][:4]

    article_data = {
        "article": {
            "title": title,
            "body_markdown": body.strip(),
            "published": publish,
            "tags": tags,
        }
    }
    if series:
        article_data["article"]["series"] = series

    payload = json.dumps(article_data).encode("utf-8")
    req = urllib.request.Request(
        DEVTO_API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "publish_to_devto/1.0",
            "api-key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="dev.to に記事を投稿する"
    )
    parser.add_argument("file", help="投稿する記事ファイル (.md)")
    parser.add_argument(
        "--publish", action="store_true",
        help="公開状態で投稿（デフォルトはドラフト）"
    )
    parser.add_argument(
        "--series", default=None,
        help="シリーズ名（例: HumanPersonaBase）"
    )
    args = parser.parse_args()

    api_key = os.environ.get("DEVTO_API_KEY")
    if not api_key:
        print("Error: DEVTO_API_KEY 環境変数を設定してください", file=sys.stderr)
        print("  set DEVTO_API_KEY=your_key  (Windows)", file=sys.stderr)
        print("  export DEVTO_API_KEY=your_key  (Linux/Mac)", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(args.file):
        print(f"Error: ファイルが見つかりません: {args.file}", file=sys.stderr)
        sys.exit(1)

    print(f"Posting: {args.file}")
    print(f"  Mode: {'PUBLISH' if args.publish else 'DRAFT'}")
    if args.series:
        print(f"  Series: {args.series}")

    result = publish_article(
        args.file, api_key,
        publish=args.publish,
        series=args.series,
    )

    import io, sys as _sys
    out = io.TextIOWrapper(_sys.stdout.buffer, encoding="utf-8", errors="replace")
    out.write("\n")
    out.write("=" * 60 + "\n")
    out.write(f"  Title: {result.get('title', '?')}\n")
    out.write(f"  URL:   {result.get('url', '?')}\n")
    out.write(f"  ID:    {result.get('id', '?')}\n")
    out.write(f"  State: {'Published' if result.get('published') else 'Draft'}\n")
    out.write("=" * 60 + "\n")
    out.flush()


if __name__ == "__main__":
    main()
