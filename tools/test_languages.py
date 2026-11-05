"""The language plugin, and what each language ships in the tool plugin.

Run:  python -m pytest tools/test_languages.py

Languages arrive one branch at a time, so nothing here names one. Every test finds the guides and
rulesets on disk, which means a language's branch adds its files and no line in this module.

Checks:

* the plugin's own `plugin.json`: the tool plugin's version, no server, no dependency;
* each guide's shape (`tools/languages_check.py`), and its `layout` block;
* the id rule: one string in the folder, `SKILL.md`, `language.yaml`, `ea.yaml`, the ruleset's folder
  and file name, and the ruleset's `meta.language`;
* each ruleset rule's `implements` resolves to a rule in that guide's `references/rules.md`;
* `ea-validation` states the server floor, and `ea-ruleset-author` shows the prefixed selector.

The checks are shown failing on planted files at the end of this module. The publish and gate halves
of the plugin are in `tools/test_publish_plugin.py` and `tools/test_gate.py`.
"""
from __future__ import annotations

# Designed behavior, no filed defect (the language-plugin workstream's items are not defects).
PINS = ()

COVERS = (
    "asset:plugins/ai-power-tools/rulesets/*",
    "asset:plugins/ai-power-tools-languages/skills/_languages/layout-standard.yaml",
)

import importlib.util
import json
import re
import sys
import zipfile
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _layout  # noqa: E402
import languages_check as check  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SHELF = _layout.plugin_root(_layout.LANGUAGES_PLUGIN, ROOT)
EA = _layout.plugin_root(_layout.EA_PLUGIN, ROOT)
RULESETS = EA / "rulesets"
EA_LANGUAGES = EA / "skills" / "_shared" / "languages"
STANDARD = SHELF / "skills" / "_languages" / "layout-standard.yaml"

GUIDES = check.guides()
RULESET_FOLDERS = sorted(p for p in RULESETS.iterdir() if p.is_dir()) if RULESETS.is_dir() else []
#: A pack's own structural rule, which no rule of the standard stands behind.
PACK_RULE = "pack"


def _ids(paths):
    return [p.name for p in paths]


def _yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _frontmatter_name(skill_md: Path) -> str | None:
    m = re.search(r"^name:\s*(\S+)\s*$", skill_md.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else None


def _rules_of(ruleset: dict) -> list[dict]:
    """Every rule in a ruleset, however it groups them."""
    found: list[dict] = []
    for key, value in ruleset.items():
        if key in ("meta", "tables"):
            continue
        if isinstance(value, list):
            found += [r for r in value if isinstance(r, dict) and "id" in r]
        elif isinstance(value, dict):
            found += _rules_of(value)
    return found


def _implements_faults(ruleset: dict, rules_md: str) -> list[str]:
    faults = []
    for rule in _rules_of(ruleset):
        implements = rule.get("implements")
        if implements is None:
            faults.append(f"{rule['id']}: no implements")
            continue
        for target in implements if isinstance(implements, list) else [implements]:
            if target != PACK_RULE and not re.search(rf"(?<![\w-]){re.escape(str(target))}(?![\w-])", rules_md):
                faults.append(f"{rule['id']}: implements {target}, which rules.md does not hold")
    return faults


# --- the plugin ---------------------------------------------------------------------------------

def test_the_plugin_ships_no_server_no_dependency_and_the_tool_plugins_version():
    ours = json.loads((SHELF / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    theirs = json.loads((EA / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert ours["name"] == "ai-power-tools-languages"
    assert ours["version"] == theirs["version"]
    assert ours["license"] == "MIT"
    assert "mcpServers" not in ours and "dependencies" not in ours
    assert not check.tool_word_hits(ours["description"])


def test_the_reader_page_ships_and_names_no_tool():
    page = (SHELF / "skills" / "_languages" / "language-file.md").read_text(encoding="utf-8")
    assert "`layout`" in page
    assert not check.tool_word_hits(page)


def test_the_marketplace_has_no_language_entry_before_a_release_tag_exists():
    """Customers follow this file on `main`, and the release adds the entry with
    `--pin-marketplace`. Remove this test in that same change."""
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    if json.loads((EA / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"] == "3.6.4":
        assert [p["name"] for p in market["plugins"]] == ["ai-power-tools"]


def test_language_files_stay_out_of_the_manifest():
    """Nineteen branches add files under `_shared/languages/`. If the manifest listed them, each
    branch would rewrite it."""
    spec = importlib.util.spec_from_file_location("regen_manifest", ROOT / "tools" / "regen-manifest.py")
    regen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(regen)
    assert not regen._in_manifest("_shared/languages/bmm-1/ea.yaml")
    assert regen._in_manifest("_shared/references/operations.md")
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    assert not [f for s in manifest["skills"] for f in s["files"]
                if f.startswith("_shared/languages/")]


def test_the_build_writes_both_archives_the_same_way_each_time(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("build_plugin_here", ROOT / "tools" / "build-plugin.py")
    build = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build)
    assert [name for name, _ in build.PLUGIN_DIRS] == list(_layout.PLUGINS)
    monkeypatch.setattr(build, "DIST", tmp_path)
    first = tmp_path / "first.plugin"
    second = tmp_path / "second.plugin"
    assert build.write_archive(SHELF, first)[0] == len(build.plugin_files(SHELF))
    build.write_archive(SHELF, second)
    assert first.read_bytes() == second.read_bytes()
    with zipfile.ZipFile(first) as zf:
        assert ".claude-plugin/plugin.json" in zf.namelist()


def test_plugin_root_refuses_an_unknown_plugin(tmp_path):
    assert _layout.plugin_root("ai-power-tools", tmp_path) == tmp_path / "plugins" / "ai-power-tools"
    assert _layout.plugin_skills(tmp_path) == tmp_path / "plugins" / "ai-power-tools" / "skills"
    with pytest.raises(ValueError):
        _layout.plugin_root("something-else", tmp_path)


# --- each guide, as it arrives ------------------------------------------------------------------

@pytest.mark.parametrize("folder", GUIDES, ids=_ids(GUIDES))
def test_each_guide_has_the_shared_shape(folder):
    assert check.check(folder) == []


@pytest.mark.parametrize("folder", GUIDES, ids=_ids(GUIDES))
def test_each_guide_holds_its_id_everywhere(folder):
    data = _yaml(folder / "language.yaml")
    assert data["id"] == folder.name
    if check.is_stub(data):
        return
    assert _frontmatter_name(folder / "SKILL.md") == folder.name
    ea_yaml = EA_LANGUAGES / folder.name / "ea.yaml"
    if ea_yaml.is_file():
        assert _yaml(ea_yaml)["language"] == folder.name


@pytest.mark.parametrize("folder", RULESET_FOLDERS, ids=_ids(RULESET_FOLDERS))
def test_each_ruleset_holds_its_id_and_every_rule_resolves(folder):
    path = folder / f"{folder.name}_rules.yaml"
    assert path.is_file(), f"the published ruleset file is <id>_rules.yaml, in {folder}"
    assert [p.name for p in folder.iterdir() if p.is_file()] == [path.name]
    ruleset = _yaml(path)
    assert ruleset["meta"]["language"] == folder.name
    rules_md = SHELF / "skills" / folder.name / "references" / "rules.md"
    assert rules_md.is_file(), f"no guide on the language plugin for {folder.name}"
    assert _rules_of(ruleset), "a ruleset with no rules this test can read"
    assert _implements_faults(ruleset, rules_md.read_text(encoding="utf-8")) == []


def test_ea_validation_states_the_server_floor_and_the_old_rulesets_tagged_address():
    """A customer on an older server gets no error from a ruleset, only silence, so this text is the warning."""
    text = (EA / "skills" / "ea-validation" / "SKILL.md").read_text(encoding="utf-8")
    flat = " ".join(text.replace(">", " ").replace("*", "").split())
    for sentence in (
        "Every ruleset in this package needs server 3.6.5 or later.",
        "Check `update.server_version` from `ping` first.",
        "On an older server, don't run them: between 1 of 8 and all of a ruleset's rules report nothing "
        "or don't run as written, by language (each how-to gives its count), and that reads like a clean model.",
        "Tell the user to update the server.",
    ):
        assert sentence in flat
    assert ("https://raw.githubusercontent.com/NovoCircle/ai-power-tools-skills/v3.6.4/"
            "ruleset-archimate31/archimate31_rules.yaml") in flat


def test_the_authoring_guide_does_not_teach_the_bare_form():
    """Stereotypes are stored with the prefix, so a bare name in a selector matches nothing and reports no fault."""
    text = (EA / "skills" / "ea-ruleset-author" / "SKILL.md").read_text(encoding="utf-8")
    assert "bare names without namespace prefix" not in text
    assert "connector_stereotypes: [ArchiMate_Assignment]" in text


def test_the_layout_standard_names_no_tool_once_it_is_there():
    if not STANDARD.is_file():
        pytest.skip("the layout standard has not landed yet")
    assert _yaml(STANDARD)
    assert not check.tool_word_hits(STANDARD.read_text(encoding="utf-8"))


# --- the checks above must be able to fail ------------------------------------------------------

GOOD_LANGUAGE = {
    "id": "demo-1",
    "name": "Demo",
    "concepts": {"elements": {"Thing": {"section": "1"}}},
    "data_types": {"coverage": "none", "note": "None defined.", "attributes": {"coverage": "none"}},
    "notation": {"coverage": "none", "note": "None defined.", "not_specified": "all"},
    "layout": {"basis": "Our conventions.", "element_types": {}, "exceptions": {}, "diagram_types": {}},
}
GOOD_SKILL = ("---\nname: demo-1\ndescription: A guide.\n---\n\n"
              "## Data types and attributes\n\nNone.\n\n## How it is drawn\n\nNot stated.\n")


def _planted(tmp_path, language=None, skill=GOOD_SKILL) -> Path:
    folder = tmp_path / "skills" / "demo-1"
    (folder / "references").mkdir(parents=True)
    (folder / "language.yaml").write_text(yaml.safe_dump(language or GOOD_LANGUAGE), encoding="utf-8")
    (folder / "SKILL.md").write_text(skill, encoding="utf-8")
    (folder / "references" / "standard.md").write_text("# Standard\n", encoding="utf-8")
    (folder / "references" / "rules.md").write_text("| DEMO-001 | must |\n", encoding="utf-8")
    return folder


def test_a_good_guide_passes(tmp_path):
    assert check.check(_planted(tmp_path)) == []


def test_a_stub_needs_only_its_id_name_and_layout(tmp_path):
    stub = {"id": "demo-1", "name": "Demo", "stub": True, "layout": {"basis": "Ours."}}
    folder = tmp_path / "demo-1"
    folder.mkdir()
    (folder / "language.yaml").write_text(yaml.safe_dump(stub), encoding="utf-8")
    assert check.check(folder) == []


@pytest.mark.parametrize("change, expected", [
    ({"layout": None}, "layout block missing"),
    ({"layout": {"element_types": {}}}, "layout.basis"),
    ({"layout": {"basis": "x", "exceptions": {"Thing": {"reason": "why"}}}}, "needs a reason and a source"),
    ({"layout": {"basis": "x", "element_types": ["Thing"]}}, "layout.element_types is not a mapping"),
    ({"id": "other"}, "is not the folder name"),
    ({"data_types": None}, "data_types missing"),
    ({"notation": None}, "notation missing"),
    ({"name": "Drawn in Sparx", "notation": {"coverage": "informative", "note": "n", "section": "1",
                                             "elements": {"Thing": {"shape": "box"}}, "default": {"shape": "box"}}},
     "entries with no section"),
])
def test_a_planted_fault_in_language_yaml_fails(tmp_path, change, expected):
    language = {**GOOD_LANGUAGE, **change}
    assert expected in " | ".join(check.check(_planted(tmp_path, language)))


@pytest.mark.parametrize("skill, expected", [
    (GOOD_SKILL.replace("## How it is drawn", "## Drawing"), "lacks '## How it is drawn'"),
    (GOOD_SKILL + "\nOpen it in EA.\n", "tool words in SKILL.md"),
    (GOOD_SKILL + "\nBuild it in Visio.\n", "tool words in SKILL.md"),
])
def test_a_planted_fault_in_skill_md_fails(tmp_path, skill, expected):
    assert expected in " | ".join(check.check(_planted(tmp_path, skill=skill)))


def test_a_missing_reference_fails(tmp_path):
    folder = _planted(tmp_path)
    (folder / "references" / "rules.md").unlink()
    assert "references/rules.md missing" in check.check(folder)


def test_implements_is_read_however_a_ruleset_groups_its_rules():
    ruleset = {"meta": {"language": "demo-1"}, "tables": {"t": [{"id": "not-a-rule"}]},
               "rules": {"cat": [{"id": "A", "implements": "DEMO-001"}],
                         "other": [{"id": "B", "implements": ["DEMO-002"]}]},
               "more": [{"id": "C", "implements": PACK_RULE}]}
    assert {r["id"] for r in _rules_of(ruleset)} == {"A", "B", "C"}
    assert _implements_faults(ruleset, "DEMO-001 and DEMO-002") == []


def test_an_implements_that_names_no_rule_fails_and_so_does_none():
    ruleset = {"rules": [{"id": "A", "implements": "DEMO-001"}, {"id": "B"}]}
    faults = " | ".join(_implements_faults(ruleset, "DEMO-0011 is a longer id"))
    assert "A: implements DEMO-001" in faults and "B: no implements" in faults
