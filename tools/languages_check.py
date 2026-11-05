#!/usr/bin/env python3
"""Measure each language guide on the language plugin against the shape every guide shares.

    python tools/languages_check.py [language-id ...]

Prints one row per language and exits 1 if any guide fails. `plugins/ai-power-tools-languages/
skills/_languages/language-file.md` is the reader's page for this shape. A guide whose concepts
this check can't enumerate fails on that, so every guide stays readable the same way.

Not shipped: the plugin is text only, and no helper program reads a language file at run time.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHELF_SKILLS = ROOT / "plugins" / "ai-power-tools-languages" / "skills"

#: What a guide may not name. A guide describes the language, never a diagramming tool.
#: "Enterprise Architect" is not on the list: it is a role in CSDM, IT4IT and TOGAF.
TOOL_WORDS = re.compile(r"\b(sparx|MDG|toolbox|quick ?linker|t_object|t_connector|\.qea|visio|archi tool|camunda|cameo|"
                        r"magicdraw|signavio|bizagi|lucidchart|draw\.io)\b", re.I)
#: Case-sensitive, so that it does not catch the word "ea" inside prose or a name.
EA_WORD = re.compile(r"\bEA\b")
HEADINGS = ("## Data types and attributes", "## How it is drawn")
KINDS = {"primitive", "enumeration", "structured", "unit", "other"}
#: The files a finished guide holds. `references/execution.md` is BPMN's alone.
GUIDE_FILES = ("SKILL.md", "language.yaml", "references/standard.md", "references/rules.md")
OPTIONAL_FILES = {"bpmn-2": ("references/execution.md",)}


def tool_word_hits(text: str) -> list[str]:
    """Every tool word in `text`, in the order found."""
    return [m.group(0) for pattern in (TOOL_WORDS, EA_WORD) for m in pattern.finditer(text)]


def guides(skills: Path = SHELF_SKILLS) -> list[Path]:
    """Every language folder on the plugin. `_languages` is shared material, not a language."""
    if not skills.is_dir():
        return []
    return sorted(p for p in skills.iterdir() if p.is_dir() and not p.name.startswith(("_", ".")))


def is_stub(data: dict) -> bool:
    """A placeholder holding only `id`, `name` and `layout`, until the guide replaces it."""
    return data.get("stub") is True


def names(block):
    """Concept or relationship names from a block's `elements` mapping, or a plain mapping or list."""
    if not block:
        return None
    if isinstance(block, dict) and isinstance(block.get("elements"), (dict, list)):
        block = block["elements"]
    if isinstance(block, dict):
        return set(block)
    if isinstance(block, list):
        out = {str(x.get("name") or x.get("id")) for x in block
               if isinstance(x, dict) and (x.get("name") or x.get("id"))}
        return out or None
    return None


def relationship_names(data):
    """The drawable relationship kinds. Guides keep them in different places; metamodel references are not drawn."""
    concepts = data.get("concepts") or {}
    if isinstance(concepts, dict) and isinstance(concepts.get("relationships"), (dict, list)):
        return names(concepts["relationships"])
    block = data.get("relationships")
    if isinstance(block, list):
        return names(block)
    for key in ("items", "types", "list", "kinds"):
        if isinstance(block, dict) and isinstance(block.get(key), (dict, list)):
            return names(block[key])
    return set()  # only metamodel references or connection tables: nothing named to draw


def known_names(data: dict) -> set[str]:
    """Everything `language.yaml` names as a concept or relationship, in any layout guides use."""
    found: set[str] = set()
    concepts = data.get("concepts")
    found |= names(concepts) or set()
    found |= relationship_names(data) or set()
    if isinstance(concepts, dict):
        for value in concepts.values():
            if isinstance(value, (dict, list)):
                found |= names(value) or set()
    return found


def layout_faults(data: dict) -> list[str]:
    """The `layout` block: present, labeled as ours, and every exception has a reason and a source."""
    layout = data.get("layout")
    if not isinstance(layout, dict):
        return ["layout block missing"]
    faults = []
    if not layout.get("basis"):
        faults.append("layout.basis")
    for key in ("element_types", "exceptions", "diagram_types", "viewpoints"):
        if layout.get(key) is not None and not isinstance(layout[key], dict):
            faults.append(f"layout.{key} is not a mapping")
    for name, entry in exceptions_of(data).items():
        if not isinstance(entry, dict) or not entry.get("reason") or not entry.get("source"):
            faults.append(f"layout exception {name} needs a reason and a source")
    return faults


def exceptions_of(data: dict) -> dict:
    layout = data.get("layout")
    found = layout.get("exceptions") if isinstance(layout, dict) else None
    return found if isinstance(found, dict) else {}


def _data_type_faults(dt) -> list[str]:
    if not isinstance(dt, dict) or dt.get("coverage") not in ("full", "partial", "none"):
        return ["data_types missing"]
    faults = []
    if not dt.get("note"):
        faults.append("data_types.note")
    if dt["coverage"] != "none":
        if not dt.get("section"):
            faults.append("data_types.section")
        types = dt.get("types") or []
        if not types and not dt.get("inherits_from"):
            faults.append("data_types.types empty")
        for t in types:
            if t.get("kind") not in KINDS or not t.get("name") or not t.get("section"):
                faults.append(f"type {t.get('name')}")
                break
    at = dt.get("attributes")
    if not isinstance(at, dict) or at.get("coverage") not in ("every_concept", "some_concepts", "none"):
        faults.append("data_types.attributes")
    return faults


def _notation_faults(data: dict) -> list[str]:
    nt = data.get("notation")
    if not isinstance(nt, dict) or nt.get("coverage") not in ("normative", "informative", "none"):
        return ["notation missing"]
    faults = []
    if not nt.get("note"):
        faults.append("notation.note")
    if nt["coverage"] != "none" and not nt.get("section"):
        faults.append("notation.section")
    all_unspecified = nt.get("not_specified") == "all"
    if nt["coverage"] == "none" and not all_unspecified:
        faults.append("notation none needs not_specified: all")
    for kind, must in (("elements", ("shape", "marker", "line", "ref", "same_as")),
                       ("relationships", ("line", "shape", "ref", "same_as"))):
        entries = nt.get(kind) or {}
        thin = [k for k, v in entries.items() if not isinstance(v, dict) or not any(v.get(m) for m in must)]
        nosec = [k for k, v in entries.items() if isinstance(v, dict) and not v.get("section")]
        if thin:
            faults.append(f"{len(thin)} {kind} entries say nothing about how they look, e.g. {thin[:3]}")
        if nosec:
            faults.append(f"{len(nosec)} {kind} entries with no section, e.g. {nosec[:3]}")
    if not all_unspecified and not nt.get("default"):
        known = set(nt.get("elements") or {}) | set(nt.get("relationships") or {}) | set(nt.get("not_specified") or [])
        for key, found in (("concepts", names(data.get("concepts"))), ("relationships", relationship_names(data))):
            if found is None:
                faults.append(f"{key} not readable by name")
                continue
            missing = found - known
            if missing:
                faults.append(f"{len(missing)} {key} with no drawing entry, e.g. {sorted(missing)[:3]}")
    return faults


def check(folder: Path) -> list[str]:
    """Every way this guide departs from the shape, or an empty list."""
    import yaml  # only this check and its callers need it; the gate's other checks stay stdlib

    faults: list[str] = []
    data = yaml.safe_load((folder / "language.yaml").read_text(encoding="utf-8")) or {}
    faults += layout_faults(data)
    if data.get("id") != folder.name:
        faults.append(f"language.yaml id {data.get('id')!r} is not the folder name")
    if is_stub(data):
        if not data.get("name"):
            faults.append("stub has no name")
        return faults

    for rel in GUIDE_FILES:
        if not (folder / rel).is_file():
            faults.append(f"{rel} missing")
    faults += _data_type_faults(data.get("data_types"))
    faults += _notation_faults(data)
    skill_md = folder / "SKILL.md"
    skill = skill_md.read_text(encoding="utf-8") if skill_md.is_file() else ""
    for heading in HEADINGS:
        if heading not in skill:
            faults.append(f"SKILL.md lacks '{heading}'")
    for path in (skill_md, folder / "language.yaml"):
        if path.is_file():
            hits = tool_word_hits(path.read_text(encoding="utf-8"))
            if hits:
                faults.append(f"tool words in {path.name}: {sorted(set(hits))[:3]}")
    return faults


def main(argv: list[str] | None = None) -> int:
    wanted = (sys.argv[1:] if argv is None else argv)
    folders = [SHELF_SKILLS / lang for lang in wanted] or guides()
    bad = 0
    for folder in folders:
        faults = check(folder) if (folder / "language.yaml").is_file() else ["language.yaml missing"]
        bad += bool(faults)
        print(f"{folder.name:18} {'ok  ' if not faults else 'FAIL'} {'; '.join(faults)[:170]}")
    print(f"\n{len(folders) - bad} pass, {bad} fail")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
