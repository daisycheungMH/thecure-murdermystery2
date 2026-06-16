#!/usr/bin/env python3
"""Regenerate content.js from player-facing markdown sources."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "content.js"

NAV_BANNER = re.compile(
    r"^> (\*\*)?Back to files:(\*\*)?[^\n]*\n\n",
    re.MULTILINE,
)
HRULE_LINE = re.compile(r"^---\s*$", re.MULTILINE)
EM_DASH = "\u2014"
EN_DASH = "\u2013"


def ensure_markdown():
    try:
        import markdown  # noqa: PLC0415

        return markdown
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "markdown", "-q"],
            stdout=subprocess.DEVNULL,
        )
        import markdown  # noqa: PLC0415

        return markdown


def strip_hrules(text: str) -> str:
    return HRULE_LINE.sub("", text)


def substitute_dashes(text: str) -> str:
    text = text.replace(EM_DASH, ", ")
    text = text.replace(EN_DASH, " to ")
    text = re.sub(r",\s+,", ", ", text)
    return text


def ensure_list_blocks(text: str) -> str:
    """Markdown needs a blank line before lists following a label paragraph."""
    return re.sub(
        r"^(\*\*(?:Likes|Dislikes|History|Plan)\*\*)\n(- )",
        r"\1\n\n\2",
        text,
        flags=re.MULTILINE,
    )


def fix_inline_markdown(html: str) -> str:
    """Bold/italic left literal when the converter skips inline markup."""
    html = re.sub(r"\*\*([^*]+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", html)
    html = re.sub(r"`([^`]+?)`", r"<code>\1</code>", html)
    return html


def postprocess_html(html: str) -> str:
    html = re.sub(r"<hr\s*/?>\s*", "", html)
    html = fix_inline_markdown(html)
    return html


DOSSIERS = {
    "curie": "01-dr-curie.md",
    "ray": "02-officer-ray.md",
    "pepper": "03-nurse-pepper.md",
    "homes": "04-dr-homes.md",
    "lacey": "05-lacey-lovely.md",
    "jetski": "06-dr-jetski.md",
    "sachs": "07-swastika-sachs.md",
    "alfie": "08-alfie-austin.md",
    "melody": "09-melody.md",
    "vance": "10-cd-vance.md",
    "diamond": "11-officer-diamond.md",
}

SHARED_DOCS = {
    "performance-script": ROOT / "player-performance-script.md",
    "actor-personas": ROOT / "14-actor-personas.md",
    "storm-containment": ROOT / "09-storm-containment-logic.md",
}


def md_to_html(text: str) -> str:
    text = NAV_BANNER.sub("", text)
    text = strip_hrules(text)
    text = substitute_dashes(text)
    text = ensure_list_blocks(text)
    md = ensure_markdown()
    html = md.markdown(
        text,
        extensions=["tables", "fenced_code", "sane_lists"],
    )
    return postprocess_html(html)


def load_doc(path: Path) -> str:
    return md_to_html(path.read_text(encoding="utf-8"))


def dossier_resource(dossier_file: str) -> dict:
    doc_id = dossier_file.replace(".md", "")
    return {
        "id": doc_id,
        "label": "Character dossier",
        "hint": "Private briefing: secrets, alibi, objectives",
    }


def with_dossier(dossier_file: str, extras: list[dict]) -> list[dict]:
    base = [
        dossier_resource(dossier_file),
        {
            "id": "performance-script",
            "label": "Player performance script",
            "hint": "Spoken lines and scenes: read only your current act",
        },
        {
            "id": "actor-personas",
            "label": "Actor personas",
            "hint": "How to play your character big and fun",
        },
    ]
    return base + extras


CHARACTERS = [
    {
        "id": "homes",
        "name": "Dr. Homes",
        "role": "Lead Attending Surgeon",
        "resources": with_dossier("04-dr-homes.md", []),
    },
    {
        "id": "pepper",
        "name": "Nurse Pepper",
        "role": "Head Nurse, VIP Wing",
        "resources": with_dossier("03-nurse-pepper.md", []),
    },
    {
        "id": "jetski",
        "name": "Dr. Jetski",
        "role": "Anesthesiologist",
        "resources": with_dossier("06-dr-jetski.md", []),
    },
    {
        "id": "ray",
        "name": "Officer Ray",
        "role": "Security Chief",
        "resources": with_dossier(
            "02-officer-ray.md",
            [
                {
                    "id": "storm-containment",
                    "label": "Storm and containment FAQ",
                    "hint": "Player facing answers: why no police, why you investigate",
                }
            ],
        ),
    },
    {
        "id": "diamond",
        "name": "Officer Diamond",
        "role": "Junior Security",
        "resources": with_dossier(
            "11-officer-diamond.md",
            [
                {
                    "id": "storm-containment",
                    "label": "Storm and containment FAQ",
                    "hint": "Player facing answers: why no police, why you investigate",
                }
            ],
        ),
    },
    {
        "id": "curie",
        "name": "Dr. Curie",
        "role": "Chief of Surgery",
        "resources": with_dossier("01-dr-curie.md", []),
    },
    {
        "id": "lacey",
        "name": "Lacey Lovely",
        "role": "Hospital Director",
        "resources": with_dossier("05-lacey-lovely.md", []),
    },
    {
        "id": "sachs",
        "name": "Swastika Sachs",
        "role": "Enforcer",
        "resources": with_dossier("07-swastika-sachs.md", []),
    },
    {
        "id": "alfie",
        "name": "Alfie Austin",
        "role": "Alex's brother",
        "resources": with_dossier("08-alfie-austin.md", []),
    },
    {
        "id": "melody",
        "name": "Melody",
        "role": "Night Receptionist",
        "resources": with_dossier("09-melody.md", []),
    },
    {
        "id": "vance",
        "name": "CD Vance",
        "role": "IT Contractor",
        "resources": with_dossier("10-cd-vance.md", []),
    },
]


HOST_RESOURCES = [
    {"id": "00-host-blueprint", "label": "Host blueprint", "path": "00-host-blueprint.md", "hint": "Truth, murder plan, endings"},
    {"id": "01-character-roster", "label": "Character roster", "path": "01-character-roster.md", "hint": "Abilities and objectives summary"},
    {"id": "02-character-timelines", "label": "Character timelines", "path": "02-character-timelines.md", "hint": "Minute-by-minute night of murder"},
    {"id": "03-motivations-alliances", "label": "Motivations and alliances", "path": "03-motivations-alliances.md", "hint": "Factions and secrets"},
    {"id": "04-evidence-index", "label": "Evidence index", "path": "04-evidence-index.md", "hint": "When each clue drops"},
    {"id": "15-evidence-materials", "label": "Evidence materials (player text)", "path": "15-evidence-materials.md", "hint": "Printable clue copy and props"},
    {"id": "05-episode-scripts", "label": "Episode scripts (host)", "path": "05-episode-scripts.md", "hint": "Cutscenes, narrator, endings"},
    {"id": "06-act2-crime-scene", "label": "Act 2 crime scene", "path": "06-act2-crime-scene.md", "hint": "OR search and live investigation"},
    {"id": "storm-containment", "label": "Storm and containment logic", "path": "09-storm-containment-logic.md", "hint": "Why suspects investigate"},
    {"id": "10-the-gathering", "label": "The gathering", "path": "10-the-gathering.md", "hint": "All eleven players briefed"},
    {"id": "11-genevieve-backstory", "label": "Genevieve backstory", "path": "11-genevieve-backstory.md", "hint": "Lacey / Genevieve truth"},
    {"id": "12-alex-revelation-arc", "label": "Alex revelation arc", "path": "12-alex-revelation-arc.md", "hint": "Episode reveal map"},
    {"id": "13-curie-charm-playbook", "label": "Curie charm playbook", "path": "13-curie-charm-playbook.md", "hint": "Ray flirt, Pepper ahem"},
    {"id": "actor-personas", "label": "Actor personas", "path": "14-actor-personas.md", "hint": "Performance guide for all eleven"},
    {"id": "performance-script", "label": "Player performance script", "path": "player-performance-script.md", "hint": "Distribute to players"},
    {"id": "readme", "label": "Project README", "path": "README.md", "hint": "File index"},
    {"id": "01-dr-curie", "label": "Dossier: Dr. Curie", "path": "player-dossiers/01-dr-curie.md"},
    {"id": "02-officer-ray", "label": "Dossier: Officer Ray", "path": "player-dossiers/02-officer-ray.md"},
    {"id": "11-officer-diamond", "label": "Dossier: Officer Diamond", "path": "player-dossiers/11-officer-diamond.md"},
    {"id": "03-nurse-pepper", "label": "Dossier: Nurse Pepper", "path": "player-dossiers/03-nurse-pepper.md"},
    {"id": "04-dr-homes", "label": "Dossier: Dr. Homes", "path": "player-dossiers/04-dr-homes.md"},
    {"id": "05-lacey-lovely", "label": "Dossier: Lacey Lovely", "path": "player-dossiers/05-lacey-lovely.md"},
    {"id": "06-dr-jetski", "label": "Dossier: Dr. Jetski", "path": "player-dossiers/06-dr-jetski.md"},
    {"id": "07-swastika-sachs", "label": "Dossier: Swastika Sachs", "path": "player-dossiers/07-swastika-sachs.md"},
    {"id": "08-alfie-austin", "label": "Dossier: Alfie Austin", "path": "player-dossiers/08-alfie-austin.md"},
    {"id": "09-melody", "label": "Dossier: Melody", "path": "player-dossiers/09-melody.md"},
    {"id": "10-cd-vance", "label": "Dossier: CD Vance", "path": "player-dossiers/10-cd-vance.md"},
    {"id": "dossiers-readme", "label": "Dossiers README", "path": "player-dossiers/README.md"},
]


def main() -> None:
    documents: dict[str, str] = {}

    for shared_id, path in SHARED_DOCS.items():
        documents[shared_id] = load_doc(path)

    dossier_dir = ROOT / "player-dossiers"
    for char_id, filename in DOSSIERS.items():
        doc_id = filename.replace(".md", "")
        documents[doc_id] = load_doc(dossier_dir / filename)

    for resource in HOST_RESOURCES:
        doc_id = resource["id"]
        if doc_id in documents:
            continue
        rel = resource["path"]
        path = ROOT / rel
        if path.exists():
            documents[doc_id] = load_doc(path)

    payload = {
        "characters": CHARACTERS,
        "hostResources": HOST_RESOURCES,
        "documents": documents,
    }
    OUT.write_text(
        "window.THE_CURE_PACK = " + json.dumps(payload, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    print(
        f"Wrote {OUT} ({len(documents)} documents, {len(CHARACTERS)} characters, "
        f"{len(HOST_RESOURCES)} host resources)"
    )


if __name__ == "__main__":
    main()
