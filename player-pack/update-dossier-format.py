#!/usr/bin/env python3
"""Bulletize Likes/Dislikes and remove inline bold from dossier body text."""

from __future__ import annotations

import re
from pathlib import Path

DOSSIER_DIR = Path(__file__).resolve().parent.parent / "player-dossiers"

LIKES_DISLIKES: dict[str, dict[str, list[str]]] = {
    "01-dr-curie.md": {
        "likes": [
            "violent scalpel work that still lands",
            "competent partners",
            "Ray's instincts (even when they get close)",
            "being the calm anchor in a panicked room",
        ],
        "dislikes": [
            "Homes's ego",
            "De Worsti",
            "sloppy investigations into Lacey (you quietly steer those away)",
            "cruelty that serves no purpose",
        ],
    },
    "02-officer-ray.md": {
        "likes": [
            "clean evidence",
            "calm partners",
            "Curie's surgical skill (you hate that you like him)",
            "the idea of arresting Sachs someday",
        ],
        "dislikes": [
            "De Worsti",
            "criminal debt",
            "storm nights",
            "anyone touching the crime scene without logging it",
        ],
    },
    "03-nurse-pepper.md": {
        "likes": [
            "clean data",
            "accurate timestamps",
            "Homes's skill (not his personality)",
            "people who survive the night",
        ],
        "dislikes": [
            "hospital politics",
            "Lacey's perfume",
            "Ray and Curie flirting mid crisis",
            "liars",
        ],
    },
    "04-dr-homes.md": {
        "likes": [
            "perfect technique",
            "obedience in the OR",
            "Lacey's attention",
            "being right in front of witnesses",
        ],
        "dislikes": [
            "Curie's charm",
            "De Worsti's wallet ethics",
            "wasted OR time",
            "accusations without proof",
        ],
    },
    "05-lacey-lovely.md": {
        "likes": [
            "control",
            "clean audits",
            "Curie",
            "crisis protocols",
            "being underestimated",
        ],
        "dislikes": [
            "De Worsti",
            "Melody snooping",
            "Pepper near her ex",
            "unlogged admin searches",
        ],
    },
    "06-dr-jetski.md": {
        "likes": [
            "clean math",
            "dawn surf when the schedule allows",
            "the nickname Jet not being used",
            "poker with Alfie (a bad idea you keep repeating)",
        ],
        "dislikes": [
            "your nickname",
            "blame",
            "syndicate collectors",
            "OR drama you did not sign up for",
            'anyone who calls you a "beach bum who wandered into a hospital"',
        ],
    },
    "07-uvula-sachs.md": {
        "likes": [
            "codes",
            "loyalty",
            "paid debts",
            "Vance obeying orders",
            "baiting Ray",
        ],
        "dislikes": [
            "jokes about your name",
            "De Worsti (even dead)",
            "loose ends",
            "lawyers",
        ],
    },
    "08-alfie-de-worsti.md": {
        "likes": [
            "insurance payouts",
            "Pepper (from afar)",
            "your brother's money (not your brother)",
            "surviving the night",
        ],
        "dislikes": [
            "De Worsti",
            "Homes flirting with Pepper",
            "shouting",
            "being backed into corners",
        ],
    },
    "09-melody.md": {
        "likes": [
            "tea",
            "scandal",
            "Officer Diamond (crush)",
            "Vance doing favors",
            "archival binders",
            "watching powerful people squirm",
        ],
        "dislikes": [
            "Lacey treating you like furniture",
            "boring visitors who do not tip or talk",
        ],
    },
    "10-cd-vance.md": {
        "likes": [
            "uptime",
            "Melody (crush)",
            "Officer Diamond (Diamond likes you back, badly, and you are oblivious)",
            "keychains",
            "being helpful (when it is survivable)",
        ],
        "dislikes": [
            "Sachs in elevators",
            "Alfie's threats",
            "prison",
            "the 11:42 p.m. overrides in the logs",
        ],
    },
    "11-officer-diamond.md": {
        "likes": [
            "painting your nails to fidget",
            "CD Vance (you will not say it plainly)",
            "sweet tea",
            "a good theory",
            "people who answer honestly when you ask kind questions",
        ],
        "dislikes": [
            'being told to "stay decorative"',
            "Sachs breathing near your junior badge",
            "when Melody flirts too loud in front of Vance",
        ],
    },
}

SECTION_HEADER = re.compile(r"^\*\*[^*]+\*\*\s*$")
RULE_LINE = re.compile(r"^- \*\*[✓✗]\*\*")


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def replace_likes_dislikes(content: str, likes: list[str], dislikes: list[str]) -> str:
    content = re.sub(
        r"\*\*Likes\*\*\s*\n\s*\n.*?(?=\n\*\*Dislikes\*\*)",
        f"**Likes**\n{bullets(likes)}\n",
        content,
        count=1,
        flags=re.DOTALL,
    )
    content = re.sub(
        r"\*\*Dislikes\*\*\s*\n\s*\n.*?(?=\n\*\*Vibe\*\*)",
        f"**Dislikes**\n{bullets(dislikes)}\n",
        content,
        count=1,
        flags=re.DOTALL,
    )
    return content


def strip_inline_bold(content: str) -> str:
    lines = content.splitlines()
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if SECTION_HEADER.match(stripped):
            out.append(line)
            continue
        rule = re.match(r"^(- \*\*[✓✗]\*\*)(.*)$", line)
        if rule:
            prefix, body = rule.group(1), rule.group(2)
            out.append(prefix + re.sub(r"\*\*([^*]+)\*\*", r"\1", body))
            continue
        out.append(re.sub(r"\*\*([^*]+)\*\*", r"\1", line))
    return "\n".join(out)


def main() -> None:
    for filename, sections in LIKES_DISLIKES.items():
        path = DOSSIER_DIR / filename
        content = path.read_text(encoding="utf-8")
        content = replace_likes_dislikes(
            content, sections["likes"], sections["dislikes"]
        )
        content = strip_inline_bold(content)
        path.write_text(content, encoding="utf-8")
        print(f"updated {filename}")


if __name__ == "__main__":
    main()
