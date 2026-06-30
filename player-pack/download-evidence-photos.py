#!/usr/bin/env python3
"""Cache evidence reference photos from Wikimedia Commons into player-pack/assets/evidence-photos/."""

from __future__ import annotations

import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets" / "evidence-photos"
DOC = ROOT.parent / "20-evidence-prop-reference.md"

UA = "Mozilla/5.0 (compatible; the-cure-prop-downloader/1.0)"


def commons_urls(markdown: str) -> list[tuple[str, str]]:
    """Return (evidence_id_hint, url) pairs from markdown image lines."""
    pairs: list[tuple[str, str]] = []
    current_id = "unknown"
    for line in markdown.splitlines():
        m = re.match(r"^### (E\d+-\w+)", line)
        if m:
            current_id = m.group(1).lower()
        img = re.search(r"!\[[^\]]*\]\(([^)]+)\)", line)
        if not img:
            continue
        src = img.group(1).strip()
        if src.startswith("http") and "wikimedia.org" in src:
            pairs.append((current_id, src))
    return pairs


def filename_for(evidence_id: str, url: str, index: int) -> str:
    parsed = urllib.parse.urlparse(url)
    if "Special:FilePath" in parsed.path:
        name = parsed.path.rsplit("/", 1)[-1]
    else:
        name = parsed.path.rsplit("/", 1)[-1]
    name = urllib.parse.unquote(name).replace(" ", "-")
    name = re.sub(r"[^\w.\-]", "", name, flags=re.ASCII)
    if not name.lower().endswith((".jpg", ".jpeg", ".png")):
        name += ".jpg"
    suffix = f"-{index}" if index else ""
    return f"{evidence_id}{suffix}-{name}"


def download(url: str, dest: Path) -> bool:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    if len(data) < 5000 or not data.startswith(b"\xff\xd8"):
        return False
    dest.write_bytes(data)
    return True


def main() -> int:
    if not DOC.exists():
        print(f"Missing {DOC}", file=sys.stderr)
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    text = DOC.read_text(encoding="utf-8")
    urls = commons_urls(text)
    if not urls:
        print("No Wikimedia URLs found in doc.")
        return 0
    ok = 0
    seen: dict[str, int] = {}
    for evidence_id, url in urls:
        idx = seen.get(evidence_id, 0)
        seen[evidence_id] = idx + 1
        dest = OUT / filename_for(evidence_id, url, idx)
        if dest.exists() and dest.stat().st_size > 5000:
            print(f"skip {dest.name}")
            ok += 1
            continue
        print(f"get  {dest.name} ...", end=" ", flush=True)
        try:
            if download(url, dest):
                print("ok")
                ok += 1
            else:
                print("fail (not a JPEG; check URL on Commons)")
                if dest.exists():
                    dest.unlink()
        except OSError as exc:
            print(f"error: {exc}")
        time.sleep(3)
    print(f"Done: {ok}/{len(urls)} cached under {OUT}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
