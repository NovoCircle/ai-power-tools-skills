#!/usr/bin/env python3
"""Compile every emitted view against a real SQL Server. OPT-IN, SKIPS BY DEFAULT.

    set APT_SQLSERVER_INSTANCE=<instance>
    python -m pytest _shared/tools/test_sql_views_sqlserver.py -q

WHY THIS EXISTS IN THE REPOSITORY AND NOT IN A SCRATCH DIRECTORY
----------------------------------------------------------------
`test_sql_views.py` says in its own header that it touches no database, and that
is the right design for it - but it means the three worst defects this emitter
has shipped were all invisible to it, because all three were COMPILE-TIME
errors:

  * a recursive CTE whose two arms disagreed on a column type, which SQL Server
    refuses outright with `Msg 240`, while 411 hermetic tests passed over a view
    that did not exist;
  * a `CASE` whose only result was the bare `NULL` constant (`Msg 8133`);
  * the same `Msg 240` a second time, on a column a hermetic guard could not
    see.

The check that caught them was run by hand from an unversioned directory and
hard-coded an absolute path into a transient worktree, so it worked on exactly
one machine for about a day, and a reviewer who tried to reproduce it could not.
A check nobody else can run is not a check. This is that harness, in the repo,
gated so that it costs nothing when there is no server.

IT NEVER FAILS FOR THE ABSENCE OF A SERVER
------------------------------------------
No `APT_SQLSERVER_INSTANCE`, or no `sqlcmd`, means SKIPPED with a reason that
says what to set. If the instance IS configured and then cannot be reached or
refuses `CREATE DATABASE`, that is a failure rather than a skip: having opted
in, a silent pass would be worse than useless.

IT NEEDS NO MODEL AND NO FIXTURE
--------------------------------
The nine EA tables the views read are declared BELOW, with EA's own physical
types - the identity columns deliberately 32-bit `int`, which is the whole point
of the exercise: the views must declare 64-bit over a 32-bit source. Nothing
here opens a `.qea`, attaches a repository, or reads any existing database, so
it runs against any instance the caller can create a database on and asserts
nothing about the caller's own models. Scratch database names carry the process
id and are dropped in teardown even when an assertion fails.
"""
from __future__ import annotations

import os
import shutil
import subprocess

import pytest

import test_sql_views as hermetic
from report_model import Column, ReportModel, Table
from sql_views import build_views

#: The instance to compile against - an empty value is what makes this file a
#: no-op. Named rather than defaulted: a default would point at one developer's
#: machine, which is how the unversioned predecessor became unrunnable.
INSTANCE = os.environ.get("APT_SQLSERVER_INSTANCE", "").strip()

SQLCMD = os.environ.get("APT_SQLCMD", "").strip() or shutil.which("sqlcmd") or ""

#: Trusted connection only. A password in an environment variable read by a test
#: is a credential this repository should not teach anyone to set.
needs_server = pytest.mark.skipif(
    not INSTANCE or not SQLCMD,
    reason="set APT_SQLSERVER_INSTANCE (and have sqlcmd on PATH, or set "
           "APT_SQLCMD) to compile the emitted views against a real instance; "
           "absence skips rather than fails")

#: EA's own schema for the nine tables the views read, reduced to the columns
#: they reference. The identity columns are `int` BECAUSE EA's are: every one of
#: `Package_ID`, `Parent_ID`, `Object_ID`, `Connector_ID`, `Diagram_ID`,
#: `t_attribute.ID` and `OperationID` is 32-bit in a live repository, so a view
#: that declares `bigint` over them is widening a real narrowing rather than
#: restating a type. `Description` is `ntext`, which is why `_stereo_block` has
#: to cast it before `STRING_SPLIT` will take it.
EA_TABLES = {
    "t_package": "Package_ID int, Parent_ID int, Name nvarchar(255)",
    "t_object": ("Object_ID int, ea_guid nvarchar(40), Name nvarchar(255), "
                 "Object_Type nvarchar(255), Stereotype nvarchar(255), "
                 "Package_ID int"),
    "t_objectproperties": ("PropertyID int, Object_ID int, "
                           "Property nvarchar(255), Value nvarchar(255)"),
    "t_xref": ("Client nvarchar(40), Type nvarchar(255), Name nvarchar(255), "
               "Description ntext"),
    "t_connector": ("Connector_ID int, ea_guid nvarchar(40), "
                    "Start_Object_ID int, End_Object_ID int, "
                    "Connector_Type nvarchar(255), Stereotype nvarchar(255), "
                    "Name nvarchar(255)"),
    "t_diagram": ("Diagram_ID int, Name nvarchar(255), "
                  "Diagram_Type nvarchar(255), Package_ID int"),
    "t_diagramobjects": "Diagram_ID int, Object_ID int",
    "t_attribute": ("ID int, Object_ID int, Name nvarchar(255), "
                    "Type nvarchar(255), Scope nvarchar(255)"),
    "t_operation": ("OperationID int, Object_ID int, Name nvarchar(255), "
                    "Type nvarchar(255), Scope nvarchar(255)"),
}

#: Types that would mean a column came back NARROWER than the logical model
#: declares. `real` is in the list because SQL Server's `real` is `float(24)`,
#: a 32-bit truncation of the `float`/`float(53)` a REAL column must be.
NARROW_TYPES = ("int", "smallint", "tinyint", "real")


def _second_table():
    """A second declared stereotype, so the multi-table branch is compiled too.

    `test_sql_views.declared()` fixes one stereotype, and two tables sharing a
    stereotype would give both the same placement predicate - which compiles,
    but would not be the two-table shape.
    """
    return Table(name="business_service", entity_key="WBA::WBABusinessService",
                 stereotype="WBABusinessService", profile="WBA", declared=True,
                 overflow_tags=["notes"],
                 columns=[Column(name=c, source_tag=c, sql_type=t)
                          for c, t in hermetic.TYPED_COLS])


#: The three states the emitter branches on. The empty one is not a curiosity:
#: its views type their columns with `CAST(NULL AS ...)` placeholders, and a
#: shipped head had those placeholders 64-bit while the populated branch of the
#: same view was 32-bit.
MODEL_STATES = {
    "one declared table": lambda: hermetic.model(),
    "two declared tables": lambda: hermetic.model([hermetic.declared(),
                                                   _second_table()]),
    "empty model": lambda: hermetic.empty_model(),
}


def _sqlcmd(sql, database="master", tolerate=False):
    done = subprocess.run(
        [SQLCMD, "-S", INSTANCE, "-E", "-d", database, "-b", "-h", "-1", "-W",
         "-Q", sql],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    if done.returncode != 0 and not tolerate:
        raise AssertionError(
            "sqlcmd failed against the configured instance.\n%s\n%s"
            % (done.stdout[-1200:], done.stderr[-1200:]))
    return done


def _rows(sql, database):
    out = _sqlcmd("SET NOCOUNT ON; " + sql, database).stdout.strip().splitlines()
    return [line.rstrip() for line in out
            if line.strip() and "rows affected" not in line]


@pytest.fixture(scope="module")
def scratch():
    """A database of our own, created and dropped, named for this process.

    Dropped in teardown whether or not the assertions passed, and the drop is
    confirmed: a check that litters databases across a developer's instance
    stops being run, and then stops being true.
    """
    name = "APT_ViewCompile_%d" % os.getpid()
    _sqlcmd("IF DB_ID('%s') IS NOT NULL BEGIN ALTER DATABASE [%s] SET SINGLE_USER "
            "WITH ROLLBACK IMMEDIATE; DROP DATABASE [%s]; END" % (name, name, name))
    _sqlcmd("CREATE DATABASE [%s]" % name)
    try:
        for table, columns in EA_TABLES.items():
            _sqlcmd("CREATE TABLE %s (%s)" % (table, columns), name)
        yield name
    finally:
        _sqlcmd("ALTER DATABASE [%s] SET SINGLE_USER WITH ROLLBACK IMMEDIATE; "
                "DROP DATABASE [%s]" % (name, name), tolerate=True)
        left = _rows("SELECT name FROM sys.databases WHERE name = '%s'" % name,
                     "master")
        assert not left, "the scratch database %s was not dropped" % name


def _compile_state(scratch, state):
    """Drop EVERY view in the scratch database, then submit this state's.

    Every view, not just the ones about to be replaced: a state that emits
    FEWER views than the one before it would otherwise read back the leftovers
    as if they were its own. Measured while writing this - the empty model
    reported 21 integer/real columns instead of its own 17, because the two
    entity views from the previous parametrization were still there. A check
    whose numbers depend on what ran before it is a check that will eventually
    certify the wrong thing.
    """
    stale = _rows("SELECT name FROM sys.objects WHERE type = 'V'", scratch)
    for name in stale:
        _sqlcmd("DROP VIEW IF EXISTS [%s]" % name, scratch, tolerate=True)
    assert not _rows("SELECT name FROM sys.objects WHERE type = 'V'", scratch), \
        "the scratch database must hold no view before a state is compiled"
    views = build_views(MODEL_STATES[state]()).views
    refused = []
    for name, ddl in views.items():
        done = _sqlcmd(ddl, scratch, tolerate=True)
        if done.returncode != 0:
            refused.append((name, " ".join((done.stdout + done.stderr).split())))
    return views, refused


@needs_server
@pytest.mark.parametrize("state", list(MODEL_STATES))
def test_every_emitted_view_compiles(scratch, state):
    """The assertion no hermetic test can make: SQL Server accepts the SQL.

    Parameterized over all three model states, because two of the three
    compile-time defects this file exists for were in a branch the default
    fixture does not reach.
    """
    views, refused = _compile_state(scratch, state)
    assert not refused, (
        "%d of %d views do not compile with a %s:\n%s"
        % (len(refused), len(views), state,
           "\n".join("  %s: %s" % (n, m[:300]) for n, m in refused)))


@needs_server
@pytest.mark.parametrize("state", list(MODEL_STATES))
def test_no_view_column_comes_back_32_bit(scratch, state):
    """Read the compiled schema back out of `sys.columns` rather than trusting
    the SQL we just sent.

    This is the check that distinguishes "the widening was written" from "the
    widening took effect". A head passed the first and failed the second on 10
    of 16 columns, because a declared type is only what the server says it is.
    """
    views, refused = _compile_state(scratch, state)
    assert not refused, "views must compile before their types can be read back"
    columns = _rows(
        "SELECT o.name + '.' + c.name + ' ' + ty.name FROM sys.columns c "
        "JOIN sys.objects o ON o.object_id = c.object_id "
        "JOIN sys.types ty ON ty.user_type_id = c.user_type_id "
        "WHERE o.type = 'V' AND ty.name IN "
        "('int','bigint','smallint','tinyint','float','real','decimal') "
        "ORDER BY o.name, c.column_id", scratch)
    narrow = [c for c in columns if c.rsplit(" ", 1)[-1] in NARROW_TYPES]
    assert columns, "a %s should still project integer and real columns" % state
    assert not narrow, (
        "%d of %d integer/real view columns came back 32-bit with a %s:\n%s"
        % (len(narrow), len(columns), state, "\n".join("  " + c for c in narrow)))


@needs_server
def test_the_package_tree_returns_its_roots_rather_than_only_compiling(scratch):
    """Compiling is necessary and not sufficient: `_pkg` is a recursive CTE, and
    the defects it has carried were about which ROWS it returns.

    A package whose parent is missing and a package that is its own parent are
    both kept as ROOTS with a NULL parent, matching `frame.package_rows`. Both
    were dropped by an earlier head, which silently lost every element beneath
    them. Neither malformation exists in a model EA built, which is exactly why
    they went unexamined - so they are inserted here deliberately.
    """
    views, refused = _compile_state(scratch, "one declared table")
    assert not refused, "views must compile before their rows can be read"
    _sqlcmd("DELETE FROM t_package", scratch)
    _sqlcmd("INSERT INTO t_package (Package_ID, Parent_ID, Name) VALUES "
            "(1, NULL, 'Model'), (2, 1, 'Child'), (3, 99, 'Dangling'), "
            "(4, 4, 'SelfParent')", scratch)
    got = _rows("SELECT CONVERT(varchar(20), package_id) + '|' + "
                "ISNULL(CONVERT(varchar(20), parent_id), '<null>') + '|' + path "
                "FROM _pkg ORDER BY package_id", scratch)
    assert got == ["1|<null>|Model", "2|1|Model/Child", "3|<null>|Dangling",
                   "4|<null>|SelfParent"], got
    _sqlcmd("DELETE FROM t_package", scratch)
