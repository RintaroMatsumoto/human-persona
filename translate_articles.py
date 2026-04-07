import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import anthropic

# APIキー読み込み: 環境変数が無ければ key_token/anthropic.key から取得
if not os.environ.get("ANTHROPIC_API_KEY"):
    key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "key_token", "anthropic.key")
    if os.path.exists(key_path):
        with open(key_path, "r", encoding="utf-8") as f:
            os.environ["ANTHROPIC_API_KEY"] = f.read().strip()

client = anthropic.Anthropic()

SRC_DIR = r"C:\Users\GoldRush\Documents\MyProject\human-persona\articles"
DST_DIR = r"C:\Users\GoldRush\Documents\MyProject\human-persona\articles-en"
MODEL = "claude-opus-4-6"
MAX_TOKENS = 16000
MAX_WORKERS = 3  # 並列ワーカー数。Opus 4.6 の 8,000 output TPM に配慮して 3 に抑制。

os.makedirs(DST_DIR, exist_ok=True)

# コマンドライン引数でファイル名フィルタを指定可能（試走用）
# 例: python translate_articles.py 38  → ファイル名に "38" を含むものだけ翻訳
filter_key = sys.argv[1] if len(sys.argv) > 1 else None

files = sorted([f for f in os.listdir(SRC_DIR) if f.endswith(".md")])
if filter_key:
    files = [f for f in files if filter_key in f]

SYSTEM_PROMPT = """You are a precise technical translator.
Translate the given Japanese Markdown article into natural English.
Rules:
- Translate frontmatter fields: title, topics. Keep emoji, type, published as-is.
- Translate all headings and body text into natural English.
- Inside code blocks: keep code as-is, translate comments.
- Inside JSON/YAML: translate descriptive string values, keep keys as-is.
- Translate the <!-- metadata ... --> block at the end if present.
- Keep all Markdown formatting (##, **, `, etc.) intact.
- Output only the translated Markdown. No explanation, no preamble."""


def translate_one(filename):
    src_path = os.path.join(SRC_DIR, filename)
    dst_path = os.path.join(DST_DIR, filename)

    if os.path.exists(dst_path):
        return filename, "SKIP", None

    with open(src_path, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"Translate the following article:\n\n{content}"}
            ]
        )
        translated = response.content[0].text
        with open(dst_path, "w", encoding="utf-8") as f:
            f.write(translated)
        return filename, "OK", (response.usage.input_tokens, response.usage.output_tokens)
    except Exception as e:
        return filename, "FAILED", f"{type(e).__name__}: {e}"


def main():
    print(f"Model: {MODEL}")
    print(f"Workers: {MAX_WORKERS}")
    print(f"{len(files)} files to translate.")
    start = time.time()

    total_in = 0
    total_out = 0
    ok = 0
    skip = 0
    failed = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_name = {executor.submit(translate_one, f): f for f in files}
        for i, future in enumerate(as_completed(future_to_name), 1):
            filename, status, info = future.result()
            if status == "OK":
                ok += 1
                total_in += info[0]
                total_out += info[1]
                print(f"[{i}/{len(files)}] OK   {filename}  ({info[0]} in, {info[1]} out)", flush=True)
            elif status == "SKIP":
                skip += 1
                print(f"[{i}/{len(files)}] SKIP {filename}", flush=True)
            else:
                failed.append((filename, info))
                print(f"[{i}/{len(files)}] FAIL {filename}  {info}", flush=True)

    elapsed = time.time() - start
    print("-" * 60)
    print(f"All done in {elapsed:.1f}s")
    print(f"OK: {ok}, SKIP: {skip}, FAILED: {len(failed)}")
    print(f"Total tokens: {total_in} in, {total_out} out")
    if failed:
        print("Failed files:")
        for name, err in failed:
            print(f"  - {name}: {err}")


if __name__ == "__main__":
    main()
