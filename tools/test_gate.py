"""Tests for the release gate.

The gate is what we accept releases on: if it stops catching something, every
later release passes silently and we find out from a customer. Until now it
was the one piece of code here with nothing proving it, while `regen-manifest`
— its sibling — had already shipped a release-breaking bug of exactly this
kind (it wrote CRLF, so every downloaded file failed its hash check).

So each test below feeds the gate something known-bad and asserts it complains,
and something known-good and asserts it does not. A gate that stops checking is
indistinguishable from a gate that passes, which is the whole problem.

Run:  python -m pytest tools/test_gate.py
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

_GATE_PATH = Path(__file__).resolve().parent / "gate.py"
_spec = importlib.util.spec_from_file_location("gate_under_test", _GATE_PATH)
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)


@pytest.fixture
def library(tmp_path, monkeypatch):
    """A throwaway library root the gate treats as its own."""
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    return tmp_path


def _write(root: Path, rel: str, text: str, *, encoding="utf-8", newline="\n") -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding=encoding, newline=newline) as fh:
        fh.write(text)
    return p


def _findings(path: Path) -> str:
    return " | ".join(gate.check_file(path))


# ---------------------------------------------------------------------------
# Rule 1 — identifiers that must never ship
# ---------------------------------------------------------------------------

class TestForbiddenIdentifiers:
    @pytest.mark.parametrize("line,expect", [
        ("The TVO model was the source.", "TVO"),
        ("Applied to the TEA repository.", "TEA"),
        ("Delivered for CA EDD last year.", "EDD"),
        ("TechVentures used this pattern.", "TechVentures"),
    ])
    def test_a_real_customer_identifier_is_caught(self, library, line, expect):
        f = _write(library, "s/SKILL.md", f"# s\n\n{line}\n")
        assert expect.lower() in _findings(f).lower()

    def test_a_personal_identifier_is_caught(self, library):
        f = _write(library, "s/SKILL.md", "# s\n\nAsk rschmierer about it.\n")
        assert "personal identifier" in _findings(f)

    @pytest.mark.parametrize("line", [
        r"Open C:\SparxServices\demos\model.qea",
        r"See C:\Users\Ryan\AppData\Roaming\Claude",
        "Run /c/SparxServices/tools/gate.py",
    ])
    def test_an_absolute_local_path_is_caught(self, library, line):
        f = _write(library, "s/SKILL.md", f"# s\n\n{line}\n")
        assert "absolute local path" in _findings(f)

    @pytest.mark.parametrize("line", [
        r"Open C:\Users\<you>\AppData\Roaming\Claude",
        r"Open C:\Users\%USERNAME%\AppData",
    ])
    def test_a_placeholder_path_is_not_a_false_positive(self, library, line):
        # The reader substitutes their own name; flagging this would train
        # people to ignore the gate.
        f = _write(library, "s/SKILL.md", f"# s\n\n{line}\n")
        assert "absolute local path" not in _findings(f)

    def test_westbrook_is_allowed(self, library):
        f = _write(library, "s/SKILL.md",
                   "# s\n\nUse WBA::WBABusinessApplication in WestbrookBank.qea\n")
        assert _findings(f) == ""


# ---------------------------------------------------------------------------
# Rule 2 — identifiers we do not recognize, which may be the next customer
# ---------------------------------------------------------------------------

class TestUnknownIdentifiers:
    def test_an_unrecognized_model_file_is_reported(self, library):
        f = _write(library, "s/SKILL.md", "# s\n\nOpen NorthWindBank.qea\n")
        assert "unrecognized model file" in _findings(f)

    def test_an_unrecognized_mdg_namespace_is_reported(self, library):
        f = _write(library, "s/SKILL.md", "# s\n\nUse ACME::AcmeThing here\n")
        assert "unrecognized MDG namespace" in _findings(f)

    def test_a_sparx_shipped_technology_is_not_reported(self, library):
        f = _write(library, "s/SKILL.md", "# s\n\nUse ArchiMate3::ArchiMate_Node\n")
        assert "unrecognized" not in _findings(f)


# ---------------------------------------------------------------------------
# Encoding — the class that broke v1.4.1
# ---------------------------------------------------------------------------

class TestEncoding:
    def test_a_utf8_bom_is_caught(self, library):
        p = library / "s" / "SKILL.md"
        p.parent.mkdir(parents=True)
        p.write_bytes(b"\xef\xbb\xbf# s\n\nplain\n")
        assert "BOM" in _findings(p)

    def test_mojibake_is_caught(self, library):
        p = library / "s" / "SKILL.md"
        p.parent.mkdir(parents=True)
        # An em dash written as cp1252 and read back as UTF-8.
        p.write_bytes("# s\n\nbroken \u00e2\u20ac\u201d dash\n".encode("utf-8"))
        assert "mojibake" in _findings(p)

    def test_curly_quotes_inside_a_code_fence_are_caught(self, library):
        f = _write(library, "s/SKILL.md",
                   '# s\n\n```python\nx = \u201chello\u201d\n```\n')
        assert "curly quotes" in _findings(f)

    def test_curly_quotes_in_prose_are_allowed(self, library):
        # Prose is read, not pasted into a shell.
        f = _write(library, "s/SKILL.md", '# s\n\nHe said \u201chello\u201d to her.\n')
        assert "curly quotes" not in _findings(f)


# ---------------------------------------------------------------------------
# Size limit
# ---------------------------------------------------------------------------

class TestSkillLineLimit:
    def test_an_oversized_skill_is_caught(self, library):
        body = "\n".join(f"line {i}" for i in range(gate.MAX_SKILL_LINES + 5))
        f = _write(library, "s/SKILL.md", body + "\n")
        assert "over the" in _findings(f)

    def test_a_skill_at_the_limit_passes(self, library):
        body = "\n".join(f"line {i}" for i in range(gate.MAX_SKILL_LINES - 1))
        f = _write(library, "s/SKILL.md", body + "\n")
        assert "over the" not in _findings(f)

    def test_the_limit_applies_only_to_skill_md(self, library):
        body = "\n".join(f"line {i}" for i in range(gate.MAX_SKILL_LINES + 50))
        f = _write(library, "s/references/long.md", body + "\n")
        assert "over the" not in _findings(f)


# ---------------------------------------------------------------------------
# Manifest integrity — the check that caught the v1.4.1 CRLF bug
# ---------------------------------------------------------------------------

class TestManifest:
    def _manifest(self, root: Path, sha: str) -> None:
        payload = {
            "manifest_version": 1, "bundle_version": "9.9.9",
            "skills": [{"name": "s", "files": ["s/SKILL.md"], "sha256": {"s/SKILL.md": sha}}],
        }
        with (root / "manifest.json").open("w", encoding="utf-8", newline="") as fh:
            fh.write(json.dumps(payload, indent=2))

    def test_a_stale_hash_is_caught(self, library):
        _write(library, "s/SKILL.md", "# s\n\nreal content\n")
        self._manifest(library, "0" * 64)
        assert any("stale sha256" in f for f in gate.check_manifest())

    def test_a_matching_hash_passes(self, library):
        import hashlib
        p = _write(library, "s/SKILL.md", "# s\n\nreal content\n")
        self._manifest(library, hashlib.sha256(p.read_bytes()).hexdigest())
        assert not [f for f in gate.check_manifest() if "stale sha256" in f]

    def test_a_crlf_manifest_is_caught(self, library):
        """This exact fault broke the v1.4.1 release.

        Assets hash as LF, the manifest ships as CRLF, and every post-download
        hash check fails on the customer's machine.
        """
        import hashlib
        p = _write(library, "s/SKILL.md", "# s\n\nreal content\n")
        payload = {
            "manifest_version": 1, "bundle_version": "9.9.9",
            "skills": [{"name": "s", "files": ["s/SKILL.md"],
                        "sha256": {"s/SKILL.md": hashlib.sha256(p.read_bytes()).hexdigest()}}],
        }
        (library / "manifest.json").write_bytes(
            json.dumps(payload, indent=2).replace("\n", "\r\n").encode("utf-8")
        )
        assert any("CRLF" in f for f in gate.check_manifest())


# ---------------------------------------------------------------------------
# Operation drift — a skill must not name an operation the server lacks
# ---------------------------------------------------------------------------

class TestOperationDrift:
    """These supply their own server source.

    Reading the real sibling checkout makes both tests depend on a machine
    that happens to have both repos. In CI, where only this repo is checked
    out, the check skips and returns [] -- so "an invented operation is
    caught" failed, and "a real operation is not caught" passed for the wrong
    reason, which is worse. A fake dispatch table exercises the detection
    logic everywhere.
    """

    @staticmethod
    def _fake_server(tmp_path):
        src = tmp_path / "fake_server.py"
        src.write_text(
            'def create_element(package_id, name, type):\n'
            '    return {}\n'
            '\n'
            'def ea_model(operation, params):\n'
            '    return {"create_element": create_element}\n',
            encoding="utf-8",
        )
        return src

    def test_an_invented_operation_is_caught(self, library, tmp_path):
        _write(library, "s/SKILL.md",
               '# s\n\nCall `ea_model(operation="summon_the_kraken", params={})`\n')
        findings = gate.check_op_drift(library, server=self._fake_server(tmp_path))
        assert gate.op_drift_ran(), "the check must actually have run"
        assert any("summon_the_kraken" in x for x in findings), findings

    def test_a_real_operation_is_not_caught(self, library, tmp_path):
        _write(library, "s/SKILL.md",
               '# s\n\nCall `ea_model(operation="create_element", params={})`\n')
        findings = gate.check_op_drift(library, server=self._fake_server(tmp_path))
        assert gate.op_drift_ran(), "the check must actually have run"
        assert not any("create_element" in x for x in findings), findings

    def test_a_missing_server_is_reported_not_silently_passed(self, library, tmp_path):
        """The skip must be observable -- it reads as a pass otherwise."""
        _write(library, "s/SKILL.md",
               '# s\n\nCall `ea_model(operation="summon_the_kraken", params={})`\n')
        findings = gate.check_op_drift(library, server=tmp_path / "nope.py")
        assert findings == []
        assert gate.op_drift_ran() is False

# ---------------------------------------------------------------------------
# Rule 4 — the Sparx diagram gallery must not leak into the bundle
#
# The half that matters is TestGalleryNamesNotCaught. A copyright rule earns
# its keep by being precise: widen it until it fires on ordinary words and
# somebody switches it off, and then a real leak ships. Those tests pin every
# term we deliberately let through, so a later reader has to argue with a
# failing test rather than quietly broaden a regex.
# ---------------------------------------------------------------------------

CORPUS_CATALOG = (
    "file\tnotation\tgrammar\n"
    "bpmn-business-process-hardware-retailer.png\tBPMN\tlanes\n"
    "sysml-requirements-hsuv-specification.png\tSysML\ttree\n"
)


class TestCorpusImages:
    @pytest.fixture
    def catalog(self, tmp_path):
        c = tmp_path / "catalog-rescored.tsv"
        c.write_text(CORPUS_CATALOG, encoding="utf-8")
        return c

    def test_the_catalog_supplies_the_corpus_filenames(self, catalog):
        assert gate.corpus_image_names(catalog) == {
            "bpmn-business-process-hardware-retailer.png",
            "sysml-requirements-hsuv-specification.png",
        }

    def test_a_corpus_image_is_caught_and_named(self, library, catalog):
        img = library / "ea-modeling" / "bpmn-business-process-hardware-retailer.png"
        img.parent.mkdir(parents=True)
        img.write_bytes(b"\x89PNG\r\n\x1a\n")
        findings = gate.check_images(library, catalog=catalog)
        assert any("corpus image" in f for f in findings), findings

    def test_a_renamed_corpus_image_is_still_caught(self, library, catalog):
        """The reason the rule is "no images" and not "no corpus filenames".

        A basename match alone is defeated by `cp gallery.png screenshot.png`,
        so it would be the weaker rule as well as the more brittle one.
        """
        img = library / "ea-modeling" / "screenshot.png"
        img.parent.mkdir(parents=True)
        img.write_bytes(b"\x89PNG\r\n\x1a\n")
        findings = gate.check_images(library, catalog=catalog)
        assert any("image file in the bundle" in f for f in findings), findings

    @pytest.mark.parametrize("name", [
        "diagram.png", "diagram.jpg", "diagram.jpeg", "diagram.gif", "diagram.svg",
    ])
    def test_every_image_format_is_covered(self, library, catalog, name):
        img = library / "ea-modeling" / name
        img.parent.mkdir(parents=True, exist_ok=True)
        img.write_bytes(b"\x89PNG\r\n\x1a\n")
        assert gate.check_images(library, catalog=catalog)

    def test_a_missing_catalog_still_blocks_the_image(self, library, tmp_path):
        """The degradation path: a bundle-only checkout has no research/.

        Without the catalog the finding cannot say *which* corpus image this
        is, but it must still be a finding. A check that goes quiet when its
        reference data is absent is indistinguishable from a check that passed.
        """
        assert gate.corpus_image_names(tmp_path / "nope.tsv") == set()
        img = library / "ea-modeling" / "bpmn-business-process-hardware-retailer.png"
        img.parent.mkdir(parents=True)
        img.write_bytes(b"\x89PNG\r\n\x1a\n")
        findings = gate.check_images(library, catalog=tmp_path / "nope.tsv")
        assert len(findings) == 1, findings
        assert "image file in the bundle" in findings[0]

    def test_a_text_only_bundle_is_clean(self, library, catalog):
        _write(library, "ea-modeling/SKILL.md", "# s\n\nWestbrookBank.qea\n")
        assert gate.check_images(library, catalog=catalog) == []

    def test_an_allowlisted_image_passes(self, library, catalog, monkeypatch):
        """The sanctioned escape hatch, so nobody needs to disable the rule."""
        img = library / "ea-modeling" / "ours.png"
        img.parent.mkdir(parents=True)
        img.write_bytes(b"\x89PNG\r\n\x1a\n")
        monkeypatch.setattr(gate, "ALLOWED_IMAGES", {"ea-modeling/ours.png"})
        assert gate.check_images(library, catalog=catalog) == []


class TestGalleryNamesCaught:
    @pytest.mark.parametrize("spelling", [
        "Hardware Retailer", "hardware-retailer", "HardwareRetailer",
        "hardware_retailer", "hardware retailers",
    ])
    def test_hardware_retailer_in_every_spelling(self, library, spelling):
        f = _write(library, "s/SKILL.md", f"# s\n\nModel the {spelling} process.\n")
        assert "Hardware Retailer" in _findings(f)

    @pytest.mark.parametrize("spelling,subject", [
        ("HSUV", "HSUV"),
        ("hsuv", "HSUV"),
        ("the HSUV specification", "HSUV"),
        ("Hybrid SUV", "Hybrid SUV"),
        ("hybrid-suv", "Hybrid SUV"),
        ("HybridSUV", "Hybrid SUV"),
        ("Distiller", "Distiller"),
        ("distiller", "Distiller"),
        ("the Distillery model", "Distiller"),
        ("Bookstore", "Bookstore"),
        ("book-store", "Bookstore"),
        ("Book Store", "Bookstore"),
        ("bookstores", "Bookstore"),
        ("Nobel Prize", "Nobel Prize"),
        ("nobel-prize", "Nobel Prize"),
        ("NobelPrize", "Nobel Prize"),
    ])
    def test_a_gallery_subject_is_caught(self, library, spelling, subject):
        f = _write(library, "s/SKILL.md", f"# s\n\nSee the {spelling} example.\n")
        findings = _findings(f)
        assert f"gallery example subject '{subject}'" in findings, findings

    def test_a_gallery_subject_in_a_fenced_block_is_caught(self, library):
        # A name inside a code sample ships just as surely as one in prose.
        f = _write(library, "s/SKILL.md",
                   '# s\n\n```python\nname = "Hardware Retailer"\n```\n')
        assert "Hardware Retailer" in _findings(f)

    def test_a_gallery_subject_in_the_file_path_is_caught(self, library):
        f = _write(library, "s/references/hsuv-requirements.md", "# notes\n\nplain\n")
        assert "in the file path" in _findings(f)

    def test_a_gallery_finding_is_blocking_not_advisory(self, library):
        f = _write(library, "s/SKILL.md", "# s\n\nThe Hardware Retailer example.\n")
        findings = gate.check_file(f)
        assert findings
        assert all(gate.is_blocking(x) for x in findings), findings

    def test_a_corpus_image_finding_is_blocking_not_advisory(self, library):
        img = library / "s" / "gallery.png"
        img.parent.mkdir(parents=True)
        img.write_bytes(b"\x89PNG\r\n\x1a\n")
        findings = gate.check_images(library)
        assert findings
        assert all(gate.is_blocking(x) for x in findings), findings

    def test_the_line_limit_remains_the_only_advisory_finding(self, library):
        # Pins the contrast: without this, "blocking" could become vacuous.
        body = "\n".join(f"line {i}" for i in range(gate.MAX_SKILL_LINES + 5))
        f = _write(library, "s/SKILL.md", body + "\n")
        assert not any(gate.is_blocking(x) for x in gate.check_file(f))


class TestGalleryNamesNotCaught:
    @pytest.mark.parametrize("line", [
        # Gallery subjects that are ordinary industry vocabulary. Someone
        # else's BPMN tutorial uses each of these too.
        "A travel booking process spans three pools.",
        "An email voting process needs a timer event.",
        "A book lending process is a good first BPMN model.",
        # Textbook state-machine and use-case subjects.
        "Model a smart home device as a component.",
        "A customer login state machine has three states.",
        "A pedestrian crossing is the canonical traffic example.",
        "Use Manage Inventory as the use case name.",
        "The states of water example shows guards.",
        # Electronics and physics vocabulary; SysPhS is an OMG standard.
        "A flip flop needs two stable states.",
        "An opamp block has two input ports.",
        "A liquid tank has one fill port.",
        "SysPhS bindings need a simulation profile.",
        # Reference architectures the gallery reproduces from elsewhere.
        "A connected vehicle solution spans two regions.",
        "Chef Automate runs on three nodes.",
        # Standards and framework names.
        "Render the TOGAF ADM as a custom diagram.",
        "The Zachman framework has six columns.",
        "Use the ArchiMate motivation viewpoint.",
        # Halves of a two-word subject, and near-miss compounds.
        "Check the hardware requirements first.",
        "Every retailer in the model is a business actor.",
        "Buy hardware for a retailer and model both.",
        "An SUV is a vehicle subtype.",
        "Increase book storage on the shared volume.",
        "The notebook store keeps one entry per run.",
        "Store the diagram id for later.",
        "Prized attributes are not tagged values.",
    ])
    def test_an_innocent_line_is_not_flagged(self, library, line):
        f = _write(library, "s/SKILL.md", f"# s\n\n{line}\n")
        assert "gallery example subject" not in _findings(f)


# ---------------------------------------------------------------------------
# The negative case that matters most
# ---------------------------------------------------------------------------

def test_a_clean_file_produces_no_findings(library):
    f = _write(library, "ea-modeling/SKILL.md", (
        "---\n"
        "name: ea-modeling\n"
        "description: Build models.\n"
        "---\n\n"
        "# Modeling\n\n"
        "Use `ea_model(operation=\"create_element\", params={})` against "
        "WestbrookBank.qea.\n"
    ))
    assert gate.check_file(f) == []
