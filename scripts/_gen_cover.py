#!/usr/bin/env python3
"""Generate cover PNG for an article: 1000x420 deep-blue canvas, centered 280x280 Twemoji."""
import sys
import io
import urllib.request
from pathlib import Path

def _ensure(pkg_import: str, pkg_install: str = None):
    try:
        return __import__(pkg_import)
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_install or pkg_import, "-q"])
        return __import__(pkg_import)


_ensure("PIL", "Pillow")
from PIL import Image

BG = (26, 26, 58)
W, H = 1000, 420
EMOJI = 280


def fetch_png(codepoint_hex: str) -> bytes:
    # Use Noto Color Emoji (128px) from googlefonts/noto-emoji, upscaled.
    # Fallback: twemoji 72x72 PNG.
    urls = [
        f"https://cdn.jsdelivr.net/gh/googlefonts/noto-emoji/png/128/emoji_u{codepoint_hex}.png",
        f"https://raw.githubusercontent.com/googlefonts/noto-emoji/main/png/128/emoji_u{codepoint_hex}.png",
        f"https://cdn.jsdelivr.net/gh/jdecked/twemoji@latest/assets/72x72/{codepoint_hex}.png",
        f"https://raw.githubusercontent.com/jdecked/twemoji/main/assets/72x72/{codepoint_hex}.png",
    ]
    last = None
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=20).read()
            print(f"OK: {u}")
            return data
        except Exception as e:
            last = e
            print(f"FAIL: {u} {e}")
    raise RuntimeError(f"could not fetch {codepoint_hex}: {last}")


def make(codepoint_hex: str, out_path: str) -> None:
    png = fetch_png(codepoint_hex)
    emoji_img = Image.open(io.BytesIO(png)).convert("RGBA")
    emoji_img = emoji_img.resize((EMOJI, EMOJI), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), BG)
    canvas.paste(emoji_img, ((W - EMOJI) // 2, (H - EMOJI) // 2), emoji_img)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, "PNG")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    # args: <codepoint_hex> <out_path>  (repeatable in pairs)
    args = sys.argv[1:]
    if len(args) % 2 != 0 or not args:
        print("usage: _gen_cover.py <hex> <path> [<hex> <path> ...]")
        sys.exit(2)
    for i in range(0, len(args), 2):
        make(args[i], args[i + 1])
