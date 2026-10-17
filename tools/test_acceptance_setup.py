"""Tests for tools/acceptance/setup_case.py and the setup blocks of the shipped acceptance cases.

Nothing here starts EA or the server: the caller is a fake that records what would be sent.
"""
import re
import sys
from pathlib import Path

import pytest

# No backlog item is pinned: these tests cover designed behavior, not a filed defect.
PINS = ()

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools" / "acceptance"))
import setup_case as sc  # noqa: E402

SKILLS = ROOT / "plugins" / "ai-power-tools" / "skills"
CASE_FILES = [SKILLS / "ea-import-export" / "references" / "test-cases.md",
              SKILLS / "ea-stakeholder-reporting" / "references" / "test-cases.md"]

BLOCK = ("[AI Power Tools description v1 begin]\r\nSummary.\r\nBody.\r\n"
         "[AI Power Tools description v1 lang=ArchiMate3@1.0 gen=0af3f0a2e00d33b7 text=0af3f0a2e00d33b7]")


class FakeCaller:
    def __init__(self, notes=BLOCK, open_model=None):
        self.calls, self.notes, self.open_model = [], notes, open_model
        self.next_id = 100

    def call(self, tool, operation, params):
        self.calls.append((tool, operation, params))
        if operation == "get_repository_info":
            return {"project_path": self.open_model, "connection_string": self.open_model}
        if operation == "execute_sql":
            sql = params["sql"]
            if "SELECT Notes" in sql:
                return {"rows": [{"Notes": self.notes}]}
            return {"rows": [{"id": 7}]}
        self.next_id += 1
        return {"ok": True, "element_id": self.next_id, "diagram_id": self.next_id,
                "package_id": self.next_id, "rejected_properties": []}


def test_setup_lines_reads_only_setup_blocks():
    case = "### TC-01: x\n\n```setup\n# a comment\ncall: a.b {}\n\nnotes-set: D | t\n```\n\n```check\nsql: SELECT 1\n```\n"
    assert sc.setup_lines(case) == ["call: a.b {}", "notes-set: D | t"]


def test_names_and_variables_are_substituted_into_json():
    fake = FakeCaller()
    out = sc.substitute('{"p": {package:Customer Engagement}, "e": {$card}}', fake, {"card": 9})
    assert out == '{"p": 7, "e": 9}'


def test_a_name_with_no_single_match_stops_the_setup():
    class Empty(FakeCaller):
        def call(self, tool, operation, params):
            return {"rows": []}
    with pytest.raises(sc.SetupError, match="expected one match"):
        sc.substitute("{diagram:Nope}", Empty(), {})


def test_a_variable_used_before_it_is_kept_stops_the_setup():
    with pytest.raises(sc.SetupError, match="before it was kept"):
        sc.substitute("{$late}", FakeCaller(), {})


def test_ampersand_names_are_looked_up_in_both_stored_forms():
    fake = FakeCaller()
    sc.substitute("{diagram:Transactions & Payments Landscape}", fake, {})
    sql = fake.calls[0][2]["sql"]
    assert "'Transactions & Payments Landscape'" in sql and "'Transactions &amp; Payments Landscape'" in sql


def test_call_keeps_a_result_field_for_later_lines():
    fake = FakeCaller()
    variables = sc.run_setup([
        'call: ea_model.create_element {"name": "Card Disputes"} => card=element_id',
        'call: ea_diagram.add_element_to_diagram {"element_id": {$card}}',
    ], fake)
    assert variables == {"card": 101}
    assert fake.calls[-1][2] == {"element_id": 101}


def test_a_failed_call_stops_the_setup():
    class Fails(FakeCaller):
        def call(self, tool, operation, params):
            return {"ok": False, "error": "boom"}
    with pytest.raises(sc.SetupError, match="failed"):
        sc.run_setup(["call: a.b {}"], Fails())


def test_notes_set_writes_crlf_through_update_diagram():
    fake = FakeCaller()
    sc.run_setup(["notes-set: Some Diagram | First line.\\nSecond line."], fake)
    tool, op, params = fake.calls[-1]
    assert (tool, op) == ("ea_diagram", "update_diagram")
    assert params["properties"]["Notes"] == "First line.\r\nSecond line."
    assert params["include_preview"] is False


def test_notes_insert_adds_the_sentence_above_the_closing_marker_and_keeps_the_rest():
    fake = FakeCaller()
    sc.run_setup(["notes-insert: Some Diagram | The team reviews this each quarter."], fake)
    written = fake.calls[-1][2]["properties"]["Notes"]
    lines = written.split("\r\n")
    assert lines[-2] == "The team reviews this each quarter."
    assert lines[-1].startswith(sc.CLOSING_MARKER)
    assert lines[:3] == BLOCK.split("\r\n")[:3]


def test_notes_insert_refuses_notes_with_no_description_block():
    with pytest.raises(sc.SetupError, match="no description block"):
        sc.run_setup(["notes-insert: D | s"], FakeCaller(notes="Just a person's text."))


def test_dry_run_writes_nothing():
    fake = FakeCaller()
    sc.run_setup(['call: ea_model.create_element {"name": "x"}', "notes-set: D | t"], fake, dry=True)
    assert all(op == "execute_sql" for _, op, _ in fake.calls)


def test_an_unknown_line_stops_the_setup():
    with pytest.raises(sc.SetupError, match="unknown setup line"):
        sc.run_setup(["dance: now"], FakeCaller())


@pytest.mark.parametrize("path", CASE_FILES, ids=lambda p: p.parent.parent.name)
def test_every_setup_block_in_the_shipped_cases_runs_against_a_fake(path):
    """Each setup parses, its placeholders resolve and its calls name real shapes."""
    text = path.read_text(encoding="utf-8")
    seen = 0
    for part in re.split(r"\n(?=### TC-\d+)", text):
        m = re.match(r"### (TC-\d+)", part)
        if not m:
            continue
        lines = sc.setup_lines(part)
        if not lines:
            continue
        seen += 1
        sc.run_setup(lines, FakeCaller())
    assert seen > 0


def _copy_path(tmp_path):
    return tmp_path / "model" / "WestbrookBank.qea"


def test_the_setup_runs_when_the_open_model_is_the_runs_copy(tmp_path):
    fake = FakeCaller(open_model=str(_copy_path(tmp_path)).replace("/", "\\"))
    sc.run_setup(["notes-set: D | t"], fake, run_dir=tmp_path)
    assert fake.calls[0][1] == "get_repository_info"
    assert fake.calls[-1][1] == "update_diagram"


def test_the_setup_refuses_when_another_model_is_open_and_writes_nothing(tmp_path):
    fake = FakeCaller(open_model=r"C:\somewhere\else\WestbrookBank.qea")
    with pytest.raises(sc.SetupError, match="not the run's copy"):
        sc.run_setup(["notes-set: D | t", 'call: ea_model.create_element {"name": "x"}'], fake, run_dir=tmp_path)
    assert [op for _, op, _ in fake.calls] == ["get_repository_info"]


def test_the_setup_refuses_when_no_model_is_open(tmp_path):
    with pytest.raises(sc.SetupError, match="not the run's copy"):
        sc.run_setup(["notes-set: D | t"], FakeCaller(open_model=None), run_dir=tmp_path)


def test_main_requires_a_run_dir(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["setup_case.py", "case.md", "TC-01"])
    with pytest.raises(SystemExit) as exc:
        sc.main()
    assert exc.value.code == 2


def test_a_result_without_the_kept_field_is_a_setup_error():
    with pytest.raises(sc.SetupError, match="no field 'nope'"):
        sc.run_setup(['call: ea_model.create_element {"name": "x"} => v=nope'], FakeCaller())


def test_parameters_that_are_not_json_are_a_setup_error():
    with pytest.raises(sc.SetupError, match="not valid JSON"):
        sc.run_setup(["call: ea_model.create_element {not json}"], FakeCaller())


def test_a_setup_error_prints_one_failed_line_and_returns_non_zero(capsys):
    def refuse():
        raise sc.SetupError("the open model is 'x', not the run's copy 'y'; nothing was written")
    assert sc.run_guarded(refuse) == 1
    out = capsys.readouterr().out
    assert out == "SETUP FAILED: the open model is 'x', not the run's copy 'y'; nothing was written\n"


def test_a_setup_error_inside_an_exception_group_is_still_one_line(capsys):
    def grouped():
        raise ExceptionGroup("unhandled errors in a TaskGroup", [sc.SetupError("name 'Nope': expected one match, found 0")])
    assert sc.run_guarded(grouped) == 1
    assert capsys.readouterr().out == "SETUP FAILED: name 'Nope': expected one match, found 0\n"


def test_an_unexpected_error_is_also_one_failed_line(capsys):
    def boom():
        raise RuntimeError("pipe closed\nwith detail")
    assert sc.run_guarded(boom) == 1
    out = capsys.readouterr().out
    assert out == "SETUP FAILED: unexpected RuntimeError: pipe closed with detail\n"


def test_a_clean_setup_prints_done_and_returns_zero(capsys):
    assert sc.run_guarded(lambda: None) == 0
    assert capsys.readouterr().out == "setup done\n"
