#!/usr/bin/env python3
"""Compile every emitted view against a real SQL Server. OPT-IN, SKIPS BY DEFAULT.

    set APT_SQLSERVER_INSTANCE=<instance>
    python -m pytest _shared/tools/test_sql_views_sqlserver.py -q

`test_sql_views.py` touches no database, so it cannot see a view SQL Server
refuses: two arms of a recursive CTE that disagree on a column type, or a
`CASE` whose only result is NULL. This file compiles every view in three model
states and reads the column types back from `sys.columns`.

Without `APT_SQLSERVER_INSTANCE`, or without `sqlcmd`, every test is skipped
with a reason. With the instance set, an unreachable server or a refused
`CREATE DATABASE` is a failure.

It declares the tables the views read itself, so it opens no `.qea` and reads
no existing database. The scratch database is named for the process and is
dropped in teardown, including after a failed assertion.
"""
from __future__ import annotations

import os
import shutil
import subprocess

import pytest

import test_sql_views as hermetic
from report_model import Column, ReportModel, Table
from sql_views import build_views

#: The instance to compile against. Unset, every test here is skipped.
INSTANCE = os.environ.get("APT_SQLSERVER_INSTANCE", "").strip()

SQLCMD = os.environ.get("APT_SQLCMD", "").strip() or shutil.which("sqlcmd") or ""

#: Trusted connection only; no password is read from the environment.
needs_server = pytest.mark.skipif(
    not INSTANCE or not SQLCMD,
    reason="set APT_SQLSERVER_INSTANCE (and have sqlcmd on PATH, or set "
           "APT_SQLCMD) to compile the emitted views against a real instance; "
           "absence skips rather than fails")

#: The tables the views read, reduced to the columns they reference, with EA's
#: SQL Server types: 32-bit `int` identity columns and an `ntext` Description.
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

#: Types narrower than the 64-bit `bigint` and `float` the views declare.
NARROW_TYPES = ("int", "smallint", "tinyint", "real")


def _second_table():
    """A second declared stereotype, so the multi-table branch is compiled.

    It uses a different stereotype from `test_sql_views.declared()`, so the two
    tables get different placement predicates.
    """
    return Table(name="business_service", entity_key="WBA::WBABusinessService",
                 stereotype="WBABusinessService", profile="WBA", declared=True,
                 overflow_tags=["notes"],
                 columns=[Column(name=c, source_tag=c, sql_type=t)
                          for c, t in hermetic.TYPED_COLS])


#: The three states the emitter branches on. The empty model types its columns
#: with `CAST(NULL AS ...)` placeholders instead of projecting EA's.
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

    The drop is confirmed in teardown, whether or not the assertions passed.
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
    """Drop every view in the scratch database, then submit this state's.

    Every view, not just the ones about to be replaced: a state that emits fewer
    views than the one before would otherwise read back the leftovers as its own.
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
    """SQL Server accepts every emitted view, in each model state."""
    views, refused = _compile_state(scratch, state)
    assert not refused, (
        "%d of %d views do not compile with a %s:\n%s"
        % (len(refused), len(views), state,
           "\n".join("  %s: %s" % (n, m[:300]) for n, m in refused)))


@needs_server
@pytest.mark.parametrize("state", list(MODEL_STATES))
def test_no_view_column_comes_back_32_bit(scratch, state):
    """No integer or real view column comes back narrower than 64-bit.

    Read from `sys.columns` after compiling, rather than from the SQL that was
    sent.
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
    """`_pkg` keeps a dangling and a self-parented package as roots with NULL parents.

    Neither shape occurs in a model EA built, so both are inserted here. The
    expected rows match `frame.package_rows`.
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
