#!/usr/bin/env python3
"""One-off: reformat dossier bullets to label-on-own-line style."""

import re
from pathlib import Path

DOSSIER_DIR = Path(__file__).resolve().parent.parent / "player-dossiers"


def transform(content: str) -> str:
    content = re.sub(r"\n---\n", "\n\n", content)

    lines = content.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]

        m = re.match(r"^- \*\*([^*]+?):\*\* (.+)$", line)
        if m:
            label, body = m.group(1), m.group(2)
            if label in ("History", "Plan"):
                out.append(f"**{label}**")
                i += 1
                continue
            out.append(f"**{label}**")
            out.append(body)
            out.append("")
            i += 1
            continue

        m2 = re.match(r"^- \*\*(History|Plan):\*\*\s*$", line)
        if m2:
            out.append(f"**{m2.group(1)}**")
            i += 1
            continue

        out.append(line)
        i += 1

    text = "\n".join(out)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def main() -> None:
    for path in sorted(DOSSIER_DIR.glob("*.md")):
        if path.name == "README.md":
            continue
        original = path.read_text(encoding="utf-8")
        updated = transform(original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            print(f"updated {path.name}")


if __name__ == "__main__":
    main()
