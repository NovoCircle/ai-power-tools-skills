"""A validator that selects nothing must not be able to report success.

This file exists because of a shipped defect, not as a style check. An earlier
revision of `archimate31_rules.yaml` named every stereotype without EA's
`ArchiMate_` prefix. `validate_model` selects with
`SELECT ... FROM t_object WHERE Stereotype IN (...)` -- exact, no
normalization, no prefix stripping -- so against a model built with EA's own
built-in ArchiMate MDG the ruleset matched ZERO elements and therefore reported
ZERO violations. A run that matched nothing is indistinguishable, in the tool's
output, from a run over a perfectly conformant model. The prefix correction
alone would not stop that happening again to the next rule someone adds, so the
durable fix is this: a test that fails when the ruleset stops selecting things.

Hermetic by construction. Enterprise Architect is never started and no `.qea`
file is opened. Instead the two tables `validate_model` actually queries --
`t_object` and `t_connector` -- are built in an in-memory SQLite database from
stereotype names MEASURED on EA 17.1 build 1716, and the selector SQL is
replayed against them verbatim.

The measured constants below are the load-bearing part, and they are
deliberately NOT derived from the ruleset. If the fixture were generated from
the names the ruleset asks for, every assertion here would be circular and the
test could never fail. `EA171_DECLARED_STEREOTYPES` comes from EA's
`MDGTechnologies/ArchiMate3.xml`, and `EAEXAMPLE_*` from the model Sparx ships
with EA. Both describe what EA does; the ruleset describes what we match. The
tests assert the two agree.

Provenance of each constant, so a future reader can re-take the measurement:
  EA171_DECLARED_STEREOTYPES
    The `ArchiMate_`-prefixed values of `<Stereotype name="...">` in
    `MDGTechnologies/ArchiMate3.xml` (technology id `ArchiMate3`, ArchiMate
    3.1). 73 of the file's 94 distinct stereotype names; the other 21 are
    toolbox page names, not concepts. `Archimate.xml` (ArchiMate 1) and
    `Archimate2.xml` (ArchiMate 2.1.1) declare the prefixed form too, so the
    prefix is not a version artifact.
  EAEXAMPLE_ELEMENT_STEREOTYPES / EAEXAMPLE_CONNECTOR_STEREOTYPES
    `SELECT Stereotype, COUNT(*) FROM t_object` / `t_connector` over
    EAExample.qea, read as SQLite from a copy. 123 elements over 32 distinct
    stereotypes; 116 connectors over 10.
  OTHER_TECHNOLOGY_DECOYS
    Rows in that SAME model whose `t_object.Stereotype` is an unprefixed
    concept name owned by a different notation, taken with the owning profile
    from the element's `t_xref` `Stereotypes` row. These are why matching is
    single-form: ArchiMate is not the only technology with a concept called
    `BusinessProcess`, so a prefix-tolerant match on the unqualified tail would
    validate BPMN and TOGAF elements against ArchiMate rules.
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

STEREOTYPE_PREFIX = "ArchiMate_"

# Repo layout: <root>/ruleset-archimate31/tools/<this file>
ROOT = Path(__file__).resolve().parents[2]
RULES_PATH = ROOT / "ruleset-archimate31" / "archimate31_rules.yaml"
BINDING_PATH = ROOT / "ea-diagram-composition" / "bindings" / "archimate3.yaml"

# Keys in the ruleset whose values are stereotype names compared against a
# `Stereotype` column. `any_of` and `connector_stereotype` drive the selector;
# `source_must_be_one_of` / `target_must_be_one_of` are compared against
# `t_object.Stereotype` for each endpoint, so a wrong name there silences a
# rule's condition just as thoroughly as one in the selector.
STEREOTYPE_KEYS = (
    "any_of",
    "connector_stereotype",
    "source_must_be_one_of",
    "target_must_be_one_of",
)

# --- measured: EA 17.1 build 1716, MDGTechnologies/ArchiMate3.xml -----------
EA171_DECLARED_STEREOTYPES = (
    "ArchiMate_Access", "ArchiMate_Aggregation",
    "ArchiMate_ApplicationCollaboration", "ArchiMate_ApplicationComponent",
    "ArchiMate_ApplicationEvent", "ArchiMate_ApplicationFunction",
    "ArchiMate_ApplicationInteraction", "ArchiMate_ApplicationInterface",
    "ArchiMate_ApplicationProcess", "ArchiMate_ApplicationService",
    "ArchiMate_Artifact", "ArchiMate_Assessment", "ArchiMate_Assignment",
    "ArchiMate_Association", "ArchiMate_BusinessActor",
    "ArchiMate_BusinessCollaboration", "ArchiMate_BusinessEvent",
    "ArchiMate_BusinessFunction", "ArchiMate_BusinessInteraction",
    "ArchiMate_BusinessInterface", "ArchiMate_BusinessObject",
    "ArchiMate_BusinessProcess", "ArchiMate_BusinessRole",
    "ArchiMate_BusinessService", "ArchiMate_Capability",
    "ArchiMate_CommunicationNetwork", "ArchiMate_Composition",
    "ArchiMate_Constraint", "ArchiMate_Contract", "ArchiMate_CourseOfAction",
    "ArchiMate_DataObject", "ArchiMate_Deliverable", "ArchiMate_Device",
    "ArchiMate_DistributionNetwork", "ArchiMate_Driver", "ArchiMate_Equipment",
    "ArchiMate_Facility", "ArchiMate_Flow", "ArchiMate_Gap", "ArchiMate_Goal",
    "ArchiMate_Grouping", "ArchiMate_ImplementationEvent",
    "ArchiMate_Influence", "ArchiMate_Junction", "ArchiMate_Location",
    "ArchiMate_Material", "ArchiMate_Meaning", "ArchiMate_Node",
    "ArchiMate_Outcome", "ArchiMate_Path", "ArchiMate_Plateau",
    "ArchiMate_Principle", "ArchiMate_Product", "ArchiMate_Realization",
    "ArchiMate_Representation", "ArchiMate_Requirement", "ArchiMate_Resource",
    "ArchiMate_Serving", "ArchiMate_Specialization", "ArchiMate_Stakeholder",
    "ArchiMate_SystemSoftware", "ArchiMate_TechnologyCollaboration",
    "ArchiMate_TechnologyEvent", "ArchiMate_TechnologyFunction",
    "ArchiMate_TechnologyInteraction", "ArchiMate_TechnologyInterface",
    "ArchiMate_TechnologyObject", "ArchiMate_TechnologyProcess",
    "ArchiMate_TechnologyService", "ArchiMate_Triggering", "ArchiMate_Value",
    "ArchiMate_ValueStream", "ArchiMate_WorkPackage",
)

# --- measured: t_object.Stereotype in EAExample.qea (EA 17.1) ---------------
EAEXAMPLE_ELEMENT_STEREOTYPES = {
    "ArchiMate_ApplicationComponent": 2, "ArchiMate_ApplicationService": 3,
    "ArchiMate_Artifact": 3, "ArchiMate_Assessment": 6,
    "ArchiMate_BusinessActor": 2, "ArchiMate_BusinessObject": 1,
    "ArchiMate_BusinessProcess": 5, "ArchiMate_BusinessRole": 2,
    "ArchiMate_BusinessService": 3, "ArchiMate_Capability": 27,
    "ArchiMate_Constraint": 1, "ArchiMate_CourseOfAction": 3,
    "ArchiMate_DataObject": 5, "ArchiMate_Deliverable": 6,
    "ArchiMate_Device": 1, "ArchiMate_Driver": 4, "ArchiMate_Gap": 3,
    "ArchiMate_Goal": 4, "ArchiMate_ImplementationEvent": 2,
    "ArchiMate_Junction": 3, "ArchiMate_Location": 1, "ArchiMate_Meaning": 3,
    "ArchiMate_Outcome": 6, "ArchiMate_Plateau": 4, "ArchiMate_Principle": 3,
    "ArchiMate_Requirement": 2, "ArchiMate_Resource": 2,
    "ArchiMate_Stakeholder": 5, "ArchiMate_SystemSoftware": 2,
    "ArchiMate_TechnologyService": 2, "ArchiMate_Value": 3,
    "ArchiMate_WorkPackage": 4,
}

# --- measured: t_connector.Stereotype in EAExample.qea (EA 17.1) ------------
EAEXAMPLE_CONNECTOR_STEREOTYPES = {
    "ArchiMate_Access": 8, "ArchiMate_Aggregation": 4,
    "ArchiMate_Assignment": 9, "ArchiMate_Association": 23,
    "ArchiMate_Composition": 2, "ArchiMate_Influence": 14,
    "ArchiMate_Realization": 35, "ArchiMate_Serving": 8,
    "ArchiMate_Specialization": 3, "ArchiMate_Triggering": 10,
}

# --- measured: same model, unprefixed names owned by OTHER technologies -----
# (stereotype, owning profile as recorded in the element's t_xref FQName, count)
OTHER_TECHNOLOGY_DECOYS = (
    ("BusinessProcess", "BPMN2.0", 20),
    ("DataObject", "BPMN2.0", 34),
    ("Resource", "BPMN2.0", 7),
    ("BusinessService", "TOGAF", 1),
    ("CourseOfAction", "BMM", 1),
)


# ---------------------------------------------------------------------------
# Fixture: the two tables validate_model queries, in the measured form
# ---------------------------------------------------------------------------
def _fixture_db() -> sqlite3.Connection:
    """An in-memory stand-in for a model built with EA's built-in ArchiMate MDG.

    Every stereotype EA 17.1 declares gets one element and, for relationship
    stereotypes, one connector, so per-rule coverage is meaningful. The decoys
    are added at their measured multiplicity because a test that the prefix
    prevents a collision is only convincing if the colliding rows are there to
    be wrongly matched.
    """
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE t_object (Object_ID INTEGER PRIMARY KEY, "
               "Name TEXT, Stereotype TEXT, Package_ID INTEGER)")
    db.execute("CREATE TABLE t_connector (Connector_ID INTEGER PRIMARY KEY, "
               "Name TEXT, Stereotype TEXT, Start_Object_ID INTEGER, "
               "End_Object_ID INTEGER)")

    oid = 0
    for stereo in EA171_DECLARED_STEREOTYPES:
        oid += 1
        db.execute("INSERT INTO t_object VALUES (?, ?, ?, 1)",
                   (oid, f"WBA {stereo.removeprefix(STEREOTYPE_PREFIX)}", stereo))
    for stereo, _profile, count in OTHER_TECHNOLOGY_DECOYS:
        for _ in range(count):
            oid += 1
            db.execute("INSERT INTO t_object VALUES (?, ?, ?, 1)",
                       (oid, f"WBA {stereo}", stereo))

    # One connector per declared relationship stereotype, wired between two
    # elements that exist, so an endpoint lookup returns a real stereotype.
    cid = 0
    for stereo in EAEXAMPLE_CONNECTOR_STEREOTYPES:
        cid += 1
        db.execute("INSERT INTO t_connector VALUES (?, ?, ?, 1, 2)",
                   (cid, f"WBA {stereo}", stereo))
    for stereo in ("ArchiMate_Flow", "ArchiMate_Serving"):
        cid += 1
        db.execute("INSERT INTO t_connector VALUES (?, ?, ?, 1, 2)",
                   (cid, f"WBA {stereo}", stereo))
    db.commit()
    return db


def _q(s: str) -> str:
    """The validator's own literal-quoting helper, reproduced."""
    return "'" + (s or "").replace("'", "''") + "'"


def _select_elements(db: sqlite3.Connection, stereos) -> list:
    """Replay validate_model's element selector SQL verbatim."""
    if not stereos:
        return []
    stereo_list = ", ".join(_q(s) for s in stereos)
    return db.execute(
        "SELECT o.Object_ID, o.Name, o.Stereotype FROM t_object o "
        f"WHERE o.Stereotype IN ({stereo_list})"
    ).fetchall()


def _select_connectors(db: sqlite3.Connection, stereo: str) -> list:
    """Replay validate_model's connector selector SQL verbatim."""
    if not stereo:
        return []
    return db.execute(
        "SELECT Connector_ID, Name, Start_Object_ID, End_Object_ID "
        f"FROM t_connector WHERE Stereotype = {_q(stereo)}"
    ).fetchall()


# ---------------------------------------------------------------------------
# Ruleset access
# ---------------------------------------------------------------------------
def _load_rules() -> dict:
    return yaml.safe_load(RULES_PATH.read_text(encoding="utf-8"))


def _stereotype_names(node, key: str = "") -> set:
    """Every string in the document that is compared against a Stereotype column."""
    found: set = set()
    if isinstance(node, dict):
        for k, v in node.items():
            found |= _stereotype_names(v, k)
    elif isinstance(node, list):
        for v in node:
            found |= _stereotype_names(v, key)
    elif isinstance(node, str) and key in STEREOTYPE_KEYS:
        found.add(node)
    return found


def _selector_stereotypes(rule: dict) -> tuple:
    """(element stereotypes, connector stereotype) a rule's selector asks for."""
    selector = rule.get("selector") or {}
    if selector.get("type") == "element":
        return tuple(((selector.get("stereotypes") or {}).get("any_of")) or []), ""
    if selector.get("type") == "connector":
        return (), selector.get("connector_stereotype", "")
    return (), ""


@pytest.fixture(scope="module")
def rules() -> dict:
    return _load_rules()


@pytest.fixture(scope="module")
def db():
    conn = _fixture_db()
    yield conn
    conn.close()


# ---------------------------------------------------------------------------
# The guard the defect asked for
# ---------------------------------------------------------------------------
def test_ruleset_matches_more_than_zero_archimate_elements(rules, db):
    """The headline guard: zero matches must never read as a clean model.

    Counting ARCHIMATE elements specifically, not rows. That distinction is the
    whole test. The broken ruleset did match rows -- 27 of them, measured on
    EAExample.qea -- but every one belonged to BPMN2.0, TOGAF or neither, and
    not one was an ArchiMate element. A guard that counted rows would have
    called that a pass.
    """
    wanted = set()
    for rule in rules["rules"]:
        wanted |= set(_selector_stereotypes(rule)[0])
    matched = _select_elements(db, sorted(wanted))
    archimate = [row for row in matched if row[2] in EA171_DECLARED_STEREOTYPES]
    assert archimate, (
        "the ruleset's element selectors matched "
        f"{len(archimate)} ArchiMate elements ({len(matched)} rows in total) in a "
        "model that contains ArchiMate elements. validate_model would report 0 "
        "violations, which is indistinguishable from a conformant model. This is "
        "APT-2026-0155 recurring: check the stereotype names carry the "
        f"{STEREOTYPE_PREFIX!r} prefix EA actually stores."
    )


def test_ruleset_matches_more_than_zero_connectors(rules, db):
    total = 0
    for rule in rules["rules"]:
        total += len(_select_connectors(db, _selector_stereotypes(rule)[1]))
    assert total > 0, (
        "the ruleset's connector selectors matched 0 connectors. Every "
        "relationship-endpoint rule is silent, so no endpoint violation can "
        "ever be reported."
    )


def test_every_rule_selects_at_least_one_candidate(rules, db):
    """A single dead rule is the same defect at smaller scale."""
    dead = []
    for rule in rules["rules"]:
        elements, connector = _selector_stereotypes(rule)
        if not (_select_elements(db, elements) or _select_connectors(db, connector)):
            dead.append((rule.get("id", "<no id>"), elements, connector))
    assert not dead, (
        "these rules select nothing and can never report a violation: "
        + "; ".join(f"{rid} (elements={els}, connector={conn!r})"
                   for rid, els, conn in dead)
    )


def test_endpoint_conditions_name_stereotypes_that_exist(rules, db):
    """An endpoint list is compared against t_object.Stereotype too.

    A wrong name here does not silence the rule, it does something worse: the
    endpoint never appears in the allowed list, so every connector of that type
    is reported as a violation. Either way the answer is noise.
    """
    known = {row[0] for row in db.execute("SELECT DISTINCT Stereotype FROM t_object")}
    unknown = {}
    for rule in rules["rules"]:
        condition = rule.get("condition") or {}
        for key in ("source_must_be_one_of", "target_must_be_one_of"):
            bad = sorted(set(condition.get(key) or []) - known)
            if bad:
                unknown.setdefault(rule.get("id", "<no id>"), []).extend(bad)
    assert not unknown, f"endpoint stereotypes no EA element can carry: {unknown}"


# ---------------------------------------------------------------------------
# Why the prefix, and what the unprefixed form actually did
# ---------------------------------------------------------------------------
def test_dropping_the_prefix_matches_no_archimate_element(rules, db):
    """Reproduce the defect, to prove this file discriminates the two outcomes.

    Stripping the prefix from every name -- exactly the form that shipped -- must
    match no ArchiMate element at all. Anything it does match belongs to another
    notation, which is the second half of the argument against a prefix-tolerant
    comparison.
    """
    # Derived from the MEASURED declaration, not from the ruleset. If it were
    # derived from the ruleset it would strip an already-stripped name and
    # quietly become a no-op on exactly the revision it is meant to catch.
    wanted = {n.removeprefix(STEREOTYPE_PREFIX) for n in EA171_DECLARED_STEREOTYPES}
    matched = _select_elements(db, sorted(wanted))
    archimate = [r for r in matched if r[2].startswith(STEREOTYPE_PREFIX)]
    assert not archimate, (
        "unprefixed names matched ArchiMate elements, so the fixture no longer "
        "reproduces what EA stores and this test has stopped being a guard"
    )
    decoys = {s for s, _p, _c in OTHER_TECHNOLOGY_DECOYS}
    assert {r[2] for r in matched} <= decoys
    assert matched, (
        "the decoy rows are missing from the fixture, so nothing here shows that "
        "unprefixed matching collides with other technologies"
    )


def test_selectors_do_not_match_other_technologies(rules, db):
    """The prefix has to be doing disambiguation work, not just decoration."""
    wanted = set()
    for rule in rules["rules"]:
        wanted |= set(_selector_stereotypes(rule)[0])
    matched = {row[2] for row in _select_elements(db, sorted(wanted))}
    collisions = matched & {s for s, _p, _c in OTHER_TECHNOLOGY_DECOYS}
    assert not collisions, (
        "the ruleset selected elements belonging to another notation "
        f"({sorted(collisions)}); an ArchiMate conformance run would report "
        "violations against BPMN, TOGAF or BMM elements"
    )


def test_every_stereotype_name_is_declared_by_the_mdg(rules):
    """Names must be spelled the way EA declares them, prefix included."""
    used = _stereotype_names(rules["rules"])
    assert used, "no stereotype names found -- the parser or the schema moved"
    unknown = sorted(used - set(EA171_DECLARED_STEREOTYPES))
    assert not unknown, (
        "stereotype names EA 17.1's built-in ArchiMate3 MDG does not declare: "
        f"{unknown}. Measured from MDGTechnologies/ArchiMate3.xml."
    )


def test_header_records_the_measurement(rules):
    """The note is the reason this does not get flipped back. Keep it present."""
    text = RULES_PATH.read_text(encoding="utf-8")
    header = text.split("meta:", 1)[0]
    for token in ("17.1", "1716", "t_object.Stereotype", "StereotypeEx",
                  "EAExample.qea", STEREOTYPE_PREFIX):
        assert token in header, (
            f"the header no longer records {token!r}. A convention note with no "
            "measurement behind it is how APT-2026-0155 happened."
        )


def test_the_two_columns_are_documented_as_different(rules):
    """`Stereotype` is unqualified; the qualified name is one join away.

    Confusing the two is the other way to make this ruleset match nothing, so
    the distinction has to stay written down where a rule author will read it.
    """
    header = RULES_PATH.read_text(encoding="utf-8").split("meta:", 1)[0]
    assert "t_xref" in header
    assert re.search(r"ArchiMate3::ArchiMate_\w+", header), (
        "the header no longer shows the profile-qualified form, so nothing warns "
        "an author against matching it against t_object.Stereotype"
    )


# ---------------------------------------------------------------------------
# The two shipped files must not state opposite conventions
# ---------------------------------------------------------------------------
@pytest.mark.skipif(not BINDING_PATH.exists(),
                    reason="ea-diagram-composition is not installed alongside this ruleset")
def test_prefix_agrees_with_the_diagram_composition_binding(rules):
    """APT-2026-0155's second symptom: one bundle, two opposite conventions."""
    binding = yaml.safe_load(BINDING_PATH.read_text(encoding="utf-8"))
    declared = binding.get("stereotype_prefix")
    assert declared == STEREOTYPE_PREFIX, (
        f"the binding declares stereotype_prefix={declared!r} but this ruleset "
        f"matches on {STEREOTYPE_PREFIX!r}. Two artifacts in one bundle stating "
        "opposite conventions is the defect, whichever one is right -- re-take "
        "the measurement and correct both together."
    )
    used = _stereotype_names(rules["rules"])
    assert all(n.startswith(declared) for n in used)


AUTHOR_SKILL = ROOT / "ea-ruleset-author" / "references" / "rule-grammar.md"


@pytest.mark.skipif(not AUTHOR_SKILL.exists(),
                    reason="ea-ruleset-author is not installed alongside this ruleset")
def test_the_authoring_guide_does_not_teach_the_bare_form():
    """This ruleset is named as the canonical reference implementation.

    It got the prefix wrong because the authoring guide said to strip it -- it
    conflated the technology NAMESPACE, which really is left off, with a prefix
    that is part of the stereotype's own name. Correcting one file and not the
    other would just reintroduce the defect in the next ruleset somebody writes.
    """
    text = AUTHOR_SKILL.read_text(encoding="utf-8")
    assert "bare names without namespace prefix" not in text, (
        "the authoring guide is back to telling authors EA stores stereotypes as "
        "bare names. It conflates two different things and it is how "
        "APT-2026-0155 was written."
    )
    assert "connector_stereotype: ArchiMate_Assignment" in text, (
        "the authoring guide no longer shows the prefixed selector, so an author "
        "following it will write names that match nothing"
    )


def test_mdg_family_still_names_the_measured_technology(rules):
    """`ArchiMate3` is the technology id in EA's own MDG, not a display name."""
    assert rules["meta"]["mdg_family"] == "ArchiMate3"
