"""Evaluate one acceptance case's checks after a run.

    python tools/acceptance/check_case.py before <case-file> <TC-nn> --run-dir D
    python tools/acceptance/check_case.py after  <case-file> <TC-nn> --run-dir D

The run folder D holds:
    model/WestbrookBank.qea   the run's copy of the model (closed in EA before `after`)
    output/ ...               the writable folders the case names (<output-dir> -> output/,
                              <name-dir> -> <name>/)
    calls.jsonl               the call log written by tools/acceptance/call.py
    reply.md                  the agent's final reply
    before.json               written by `before`: the result of every `expect: unchanged` query,
                              keyed by the query text so editing a case does not lose it

`after` writes D/checks.json and prints one line per check: pass, fail, grade (a `reply` statement
for the grader) or manual (a check this script does not evaluate: `http`, `call`, `xpath`, a skill
load). The case passes when every check is pass, and every grade and manual item is judged pass.

The model copy is opened read-only (sqlite mode=ro). Nothing here starts or touches EA.
"""
import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path


def case_text(case_file, tc):
    text = Path(case_file).read_text(encoding="utf-8")
    parts = re.split(r"\n(?=### TC-\d+)", text)
    for part in parts:
        if re.match(rf"### {re.escape(tc)}\b", part):
            return part
    sys.exit(f"{tc} not found in {case_file}")


def checks_of(case):
    """[(line number within the case, key, value, expect or None)] from the case's check blocks."""
    out, fenced, kind = [], False, None
    lines = case.splitlines()
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("```"):
            fenced = not fenced
            kind = s[3:].strip() if fenced else None
            continue
        if not (fenced and kind == "check") or not s or s.startswith("#"):
            continue
        m = re.match(r"(sql|call|http|file|reply|tools|expect)\s*:\s*(.*)$", s)
        if not m:
            continue
        key, value = m.groups()
        if key == "expect":
            if out and out[-1][3] is None and out[-1][1] in ("sql", "call", "http", "file"):
                out[-1] = out[-1][:3] + (value,)
            continue
        out.append((i + 1, key, value, None))
    return out


def query(db, sql):
    con = sqlite3.connect(f"file:{Path(db).as_posix()}?mode=ro", uri=True)
    try:
        return [list(r) for r in con.execute(sql).fetchall()]
    finally:
        con.close()


def judge_rows(rows, expect, before):
    if expect == "unchanged":
        return rows == before, f"{rows} vs before {before}"
    if expect == "empty":
        return rows == [], str(rows)
    m = re.match(r"(=|>=|<=)\s*(-?\d+)$", expect)
    if m:
        got = rows[0][0] if rows and rows[0] else None
        op, n = m.group(1), int(m.group(2))
        ok = got is not None and {"=": got == n, ">=": got >= n, "<=": got <= n}[op]
        return ok, f"got {got}"
    m = re.match(r"rows:\s*(\[.*\])$", expect)
    if m:
        want = json.loads(m.group(1))
        return rows == want, f"got {rows}"
    return None, f"unknown expect '{expect}'"


def resolve(run_dir, path):
    def sub(m):
        name = m.group(1)
        return "output" if name == "output-dir" else name[:-4] if name.endswith("-dir") else name
    p = re.sub(r"<([a-z-]+)>", sub, path).replace("\\", "/")
    p = Path(p)
    return p if p.is_absolute() else Path(run_dir) / (p if len(p.parts) > 1 else Path("output") / p)


def judge_file(run_dir, path, expect):
    p = resolve(run_dir, path)
    if expect == "exists":
        return p.exists(), str(p)
    if expect == "absent":
        return not p.exists(), str(p)
    m = re.match(r"(not-contains|contains):\s*(.*)$", expect or "")
    if m:
        if not p.exists():
            return False, f"{p} missing"
        found = m.group(2) in p.read_text(encoding="utf-8", errors="replace")
        return (found if m.group(1) == "contains" else not found), str(p)
    return None, f"expect '{expect}' needs a person"


def judge_tools(calls, value):
    def name(c):
        return c["tool"] if c["tool"] == "ping" else f"{c['tool']}.{c['operation']}"
    m = re.match(r"(called|not-called|before):\s*(\S+)\s*(.*)$", value)
    if not m:
        return None, f"unreadable tools check '{value}'"
    verb, target, rest = m.groups()
    if target.startswith(("skill:", "computer-use")):
        return None, "not in the call log; judge from the transcript"
    if verb == "before":
        second = rest.split()[0] if rest else ""
        names = [name(c) for c in calls]
        if target not in names:
            return False, f"{target} never called"
        if second not in names:
            return True, f"{second} never called"
        return names.index(target) < names.index(second), f"order {names}"
    want = json.loads(rest) if rest.strip().startswith("{") else {}
    hits = [c for c in calls if name(c) == target
            and all(c.get("params", {}).get(k) == v for k, v in want.items())]
    return (bool(hits) if verb == "called" else not hits), f"{len(hits)} matching call(s)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=["before", "after"])
    ap.add_argument("case_file")
    ap.add_argument("tc")
    ap.add_argument("--run-dir", required=True)
    a = ap.parse_args()
    run = Path(a.run_dir)
    db = run / "model" / "WestbrookBank.qea"
    checks = checks_of(case_text(a.case_file, a.tc))
    if a.phase == "before":
        before = {v: query(db, v) for n, k, v, e in checks if k == "sql" and e == "unchanged"}
        (run / "before.json").write_text(json.dumps(before), encoding="utf-8")
        print(f"recorded {len(before)} unchanged queries")
        return 0
    before = json.loads((run / "before.json").read_text(encoding="utf-8")) if (run / "before.json").exists() else {}
    log = run / "calls.jsonl"
    calls = [json.loads(l) for l in log.read_text(encoding="utf-8").splitlines() if l.strip()] if log.exists() else []
    results = []
    for n, key, value, expect in checks:
        if key == "sql":
            try:
                ok, detail = judge_rows(query(db, value), expect, before.get(value))
            except sqlite3.Error as exc:
                ok, detail = False, f"sql error: {exc}"
        elif key == "file":
            ok, detail = judge_file(run, value, expect)
        elif key == "tools":
            ok, detail = judge_tools(calls, value)
        elif key == "reply":
            ok, detail = "grade", value
        else:
            ok, detail = None, f"{key} check: run by hand"
        verdict = {True: "pass", False: "fail", None: "manual", "grade": "grade"}[ok]
        results.append({"line": n, "kind": key, "check": value, "expect": expect,
                        "verdict": verdict, "detail": detail})
        print(f"{verdict:6} {key:5} {value[:90]}" + (f"  [{detail[:80]}]" if verdict in ("fail", "manual") else ""))
    (run / "checks.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
    fails = sum(r["verdict"] == "fail" for r in results)
    print(f"{fails} failed, {sum(r['verdict'] == 'grade' for r in results)} to grade, "
          f"{sum(r['verdict'] == 'manual' for r in results)} manual")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
