"""Tests for the plugin release: publish the tree, pin the marketplace to it.

What these protect is the rule that customers install the RELEASED plugin and
never this repository's development branch. Every way that rule has a chance to
break is a refusal in `publish-plugin.py`, so each test below hands the tool a
known-bad state and asserts it refuses without touching anything, or a
known-good one and asserts it does exactly what it printed.

Hermetic: the "releases repository" is a bare git repository in a temp
directory, so cloning, pushing and tagging are real git against a local path.
The two HTTP reads -- a raw file at a sha, and whether a release asset is
downloadable -- are replaced; nothing here touches the network.

Run:  python -m pytest tools/test_publish_plugin.py
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

_PATH = Path(__file__).resolve().parent / "publish-plugin.py"
_spec = importlib.util.spec_from_file_location("publish_plugin_under_test", _PATH)
tool = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = tool  # dataclasses resolve annotations through it
_spec.loader.exec_module(tool)

VERSION = "9.9.0"
REPO = "Example/releases"
MCPB = f"https://github.com/{REPO}/releases/download/v{VERSION}/Server.mcpb"
SKILL_TEXT = "---\nname: demo\n---\n\n# Demo\n\nLF only.\n"
#: Bytes that a line-ending conversion would alter, in a file git should treat
#: as binary.
BINARY = b"\x89PNG\r\n\x1a\n\x00\x00\r\n\x00"


def git(*args, cwd=None) -> str:
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    return out.stdout.strip()


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(data, indent=2) + "\n").encode("utf-8"))


@pytest.fixture(autouse=True)
def git_config(tmp_path, monkeypatch):
    """A private git config, with autocrlf on -- the Windows default, and the
    setting that would rewrite the tree on its way into the commit."""
    cfg = tmp_path / "gitconfig"
    cfg.write_text("[user]\n\tname = Test\n\temail = test@example.invalid\n"
                   "[core]\n\tautocrlf = true\n[init]\n\tdefaultBranch = main\n",
                   encoding="utf-8")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(cfg))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")


@pytest.fixture
def remote(tmp_path) -> Path:
    """The releases repository as it is today: a README on main."""
    bare = tmp_path / "releases.git"
    git("init", "--quiet", "--bare", str(bare))
    seed = tmp_path / "seed"
    git("clone", "--quiet", str(bare), str(seed))
    (seed / "README.md").write_text("# Releases\n", encoding="utf-8")
    git("add", "README.md", cwd=seed)
    git("commit", "--quiet", "-m", "README", cwd=seed)
    git("push", "--quiet", "origin", "HEAD:refs/heads/main", cwd=seed)
    return bare


def remote_ref(remote: Path, ref: str) -> str | None:
    out = git("ls-remote", str(remote), ref)
    return out.split("\t")[0] if out else None


def build_archive(root: Path) -> None:
    """What tools/build-plugin.py writes, from the same file list."""
    plugin = root / tool.PLUGIN_PATH
    out = root / "dist" / "ai-power-tools.plugin"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in tool.build_plugin.plugin_files(plugin):
            zf.writestr(f.relative_to(plugin).as_posix(), f.read_bytes())


@pytest.fixture
def skills(tmp_path, monkeypatch, remote) -> Path:
    """A skills repository at version 9.9.0, built and committed."""
    root = tmp_path / "skills"
    plugin = root / tool.PLUGIN_PATH
    _write_json(plugin / ".claude-plugin" / "plugin.json",
                {"name": "ai-power-tools", "version": VERSION, "mcpServers": MCPB})
    (plugin / "skills" / "demo").mkdir(parents=True)
    (plugin / "skills" / "demo" / "SKILL.md").write_bytes(SKILL_TEXT.encode())
    (plugin / "skills" / "demo" / "icon.png").write_bytes(BINARY)
    _write_json(root / "manifest.json", {"bundle_version": VERSION, "skills": []})
    _write_json(root / ".claude-plugin" / "marketplace.json", {
        "name": "novocircle", "owner": {"name": "NovoCircle"},
        "plugins": [{"name": "ai-power-tools", "source": "./plugins/ai-power-tools",
                     "version": VERSION, "description": "d"}]})
    build_archive(root)

    monkeypatch.setattr(tool, "skills_source_rev", lambda _root: ("a" * 40, False))
    monkeypatch.setattr(tool, "url_resolves", lambda url: (True, "HTTP 302"))

    def fetch(url):
        # raw.githubusercontent.com/<repo>/<ref>/<path>, answered from the
        # bare repository for the releases repo and from disk for the
        # marketplace on the skills repo's default branch.
        tail = url.split("raw.githubusercontent.com/", 1)[1]
        owner, name, ref, path = tail.split("/", 3)
        if f"{owner}/{name}" == tool.SKILLS_REPO:
            return (root / path).read_bytes(), ""
        out = subprocess.run(["git", "--git-dir", str(remote), "show",
                              f"{ref}:{path}"], capture_output=True)
        return (out.stdout, "") if out.returncode == 0 else (None, "404")
    monkeypatch.setattr(tool, "fetch_bytes", fetch)
    return root


def run(skills: Path, remote: Path, *args: str) -> int:
    return tool.main([*args, "--releases-remote", str(remote)], root=skills)


def marketplace(skills: Path) -> dict:
    return json.loads((skills / ".claude-plugin" / "marketplace.json")
                      .read_text(encoding="utf-8"))


def entry(skills: Path) -> dict:
    return tool.find_entry(marketplace(skills))


# ---------------------------------------------------------------------------
# Refusals before anything is staged
# ---------------------------------------------------------------------------

class TestRefusesBeforeStaging:
    def test_version_drift_refuses(self, skills, remote, capsys):
        _write_json(skills / "manifest.json", {"bundle_version": "9.8.0", "skills": []})
        assert run(skills, remote) == 1
        assert "Version drift" in capsys.readouterr().out
        assert not (skills / tool.STAGING_DIR).exists()

    def test_marketplace_drift_refuses(self, skills, remote, capsys):
        m = marketplace(skills)
        m["plugins"][0]["version"] = "9.8.0"
        _write_json(skills / ".claude-plugin" / "marketplace.json", m)
        assert run(skills, remote) == 1
        assert "marketplace.json entry" in capsys.readouterr().out

    def test_server_pinned_to_another_release_refuses(self, skills, remote, capsys):
        pj = skills / tool.PLUGIN_JSON
        data = json.loads(pj.read_text(encoding="utf-8"))
        data["mcpServers"] = MCPB.replace(f"v{VERSION}", "v9.8.0")
        _write_json(pj, data)
        build_archive(skills)
        assert run(skills, remote) == 1
        assert "pins server release v9.8.0" in capsys.readouterr().out

    def test_floating_server_url_refuses(self, skills, remote, capsys):
        pj = skills / tool.PLUGIN_JSON
        data = json.loads(pj.read_text(encoding="utf-8"))
        data["mcpServers"] = f"https://github.com/{REPO}/releases/latest/download/Server.mcpb"
        _write_json(pj, data)
        assert run(skills, remote) == 1
        assert "not a pinned GitHub release" in capsys.readouterr().out

    def test_missing_archive_refuses(self, skills, remote, capsys):
        (skills / "dist" / "ai-power-tools.plugin").unlink()
        assert run(skills, remote) == 1
        assert "run tools/build-plugin.py" in capsys.readouterr().out

    def test_stale_archive_refuses(self, skills, remote, capsys):
        (skills / tool.PLUGIN_PATH / "skills" / "demo" / "SKILL.md").write_bytes(b"changed\n")
        assert run(skills, remote) == 1
        out = capsys.readouterr().out
        assert "differs between the archive" in out and "stale" in out


# ---------------------------------------------------------------------------
# Dry run
# ---------------------------------------------------------------------------

class TestDryRun:
    @pytest.mark.parametrize("args", [(), ("--dry-run",)])
    def test_stages_and_prints_but_changes_nothing(self, skills, remote, capsys, args):
        main_before = remote_ref(remote, "refs/heads/main")
        before = (skills / ".claude-plugin" / "marketplace.json").read_bytes()
        assert run(skills, remote, *args) == 0
        out = capsys.readouterr().out
        assert "DRY RUN" in out
        assert "push origin HEAD:refs/heads/main" in out
        assert f"tag v{VERSION}" in out and f"push origin refs/tags/v{VERSION}" in out
        assert '"source": "git-subdir"' in out and f'"ref": "v{VERSION}"' in out
        assert remote_ref(remote, "refs/heads/main") == main_before
        assert remote_ref(remote, f"refs/tags/v{VERSION}") is None
        assert (skills / ".claude-plugin" / "marketplace.json").read_bytes() == before

    def test_committed_bytes_are_the_archive_bytes_despite_autocrlf(self, skills, remote):
        assert run(skills, remote) == 0
        clone = skills / tool.STAGING_DIR / "releases"
        base = f"HEAD:{tool.PLUGIN_PATH}/skills/demo"
        got = subprocess.run(["git", "show", f"{base}/SKILL.md"], cwd=clone,
                             capture_output=True).stdout
        assert got == SKILL_TEXT.encode()
        got = subprocess.run(["git", "show", f"{base}/icon.png"], cwd=clone,
                             capture_output=True).stdout
        assert got == BINARY

    def test_the_tree_replaces_what_was_there(self, skills, remote, tmp_path):
        # The releases copy is generated: a file dropped from the plugin must
        # not survive from the previous release.
        work = tmp_path / "old"
        git("clone", "--quiet", str(remote), str(work))
        old = work / tool.PLUGIN_PATH / "skills" / "retired" / "SKILL.md"
        old.parent.mkdir(parents=True)
        old.write_text("retired\n", encoding="utf-8")
        git("add", "-A", cwd=work)
        git("commit", "--quiet", "-m", "old release", cwd=work)
        git("push", "--quiet", "origin", "HEAD:main", cwd=work)

        assert run(skills, remote) == 0
        clone = skills / tool.STAGING_DIR / "releases"
        listed = git("ls-tree", "-r", "--name-only", "HEAD", cwd=clone)
        assert "retired" not in listed
        assert "README.md" in listed  # nothing outside the plugin is touched


def test_tree_problems_catches_an_altered_blob(skills, remote):
    assert run(skills, remote) == 0
    clone = skills / tool.STAGING_DIR / "releases"
    archive = tool.read_archive(skills / "dist" / "ai-power-tools.plugin")
    archive["skills/demo/SKILL.md"] = SKILL_TEXT.replace("\n", "\r\n").encode()
    archive["skills/demo/extra.md"] = b"x\n"
    problems = " | ".join(tool.tree_problems(clone, "HEAD", archive))
    assert "SKILL.md was altered" in problems
    assert "extra.md is missing" in problems


# ---------------------------------------------------------------------------
# Publish
# ---------------------------------------------------------------------------

class TestPublish:
    def test_pushes_the_tree_and_tags_that_commit(self, skills, remote):
        assert run(skills, remote, "--publish") == 0
        tag = remote_ref(remote, f"refs/tags/v{VERSION}")
        assert tag is not None and tag == remote_ref(remote, "refs/heads/main")
        pj = subprocess.run(["git", "--git-dir", str(remote), "show",
                             f"{tag}:{tool.PLUGIN_JSON}"], capture_output=True).stdout
        assert json.loads(pj)["version"] == VERSION

    def test_never_moves_an_existing_tag(self, skills, remote, capsys):
        # Today's state: every server tag names the README-only commit.
        seed = remote_ref(remote, "refs/heads/main")
        git("--git-dir", str(remote), "tag", f"v{VERSION}", seed)
        assert run(skills, remote, "--publish") == 1
        assert "never moved" in capsys.readouterr().out
        assert remote_ref(remote, f"refs/tags/v{VERSION}") == seed
        assert remote_ref(remote, "refs/heads/main") == seed

    def test_a_second_run_is_a_no_op(self, skills, remote, capsys):
        assert run(skills, remote, "--publish") == 0
        tag = remote_ref(remote, f"refs/tags/v{VERSION}")
        main = remote_ref(remote, "refs/heads/main")
        capsys.readouterr()
        assert run(skills, remote) == 0
        assert "already published" in capsys.readouterr().out
        assert run(skills, remote, "--publish") == 0
        assert remote_ref(remote, f"refs/tags/v{VERSION}") == tag
        assert remote_ref(remote, "refs/heads/main") == main

    def test_refuses_uncommitted_shipped_files(self, skills, remote, monkeypatch):
        monkeypatch.setattr(tool, "skills_source_rev", lambda _root: ("a" * 40, True))
        main = remote_ref(remote, "refs/heads/main")
        assert run(skills, remote, "--publish") == 1
        assert remote_ref(remote, "refs/heads/main") == main
        assert remote_ref(remote, f"refs/tags/v{VERSION}") is None

    def test_publish_does_not_edit_the_marketplace(self, skills, remote):
        before = (skills / ".claude-plugin" / "marketplace.json").read_bytes()
        assert run(skills, remote, "--publish") == 0
        assert (skills / ".claude-plugin" / "marketplace.json").read_bytes() == before


# ---------------------------------------------------------------------------
# Pin the marketplace
# ---------------------------------------------------------------------------

class TestPinMarketplace:
    def test_refuses_a_tag_that_does_not_exist(self, skills, remote, capsys):
        before = (skills / ".claude-plugin" / "marketplace.json").read_bytes()
        assert run(skills, remote, "--pin-marketplace") == 1
        assert "does not exist" in capsys.readouterr().out
        assert (skills / ".claude-plugin" / "marketplace.json").read_bytes() == before

    def test_refuses_while_the_server_release_is_a_draft(self, skills, remote,
                                                          monkeypatch, capsys):
        assert run(skills, remote, "--publish") == 0
        monkeypatch.setattr(tool, "url_resolves", lambda url: (False, "HTTP 404"))
        before = (skills / ".claude-plugin" / "marketplace.json").read_bytes()
        assert run(skills, remote, "--pin-marketplace") == 1
        assert "Promote the server release first" in capsys.readouterr().out
        assert (skills / ".claude-plugin" / "marketplace.json").read_bytes() == before

    def test_refuses_a_tag_carrying_another_version(self, skills, remote,
                                                    monkeypatch, capsys):
        assert run(skills, remote, "--publish") == 0
        monkeypatch.setattr(tool, "fetch_bytes", lambda url: (
            json.dumps({"version": "9.8.0", "mcpServers": MCPB}).encode(), ""))
        assert run(skills, remote, "--pin-marketplace") == 1
        assert "says version '9.8.0'" in capsys.readouterr().out
        assert entry(skills)["source"] == "./plugins/ai-power-tools"

    def test_pins_git_subdir_to_the_tag_and_its_sha(self, skills, remote):
        assert run(skills, remote, "--publish") == 0
        assert run(skills, remote, "--pin-marketplace") == 0
        e = entry(skills)
        assert e["source"] == {
            "source": "git-subdir",
            "url": f"https://github.com/{REPO}.git",
            "path": "plugins/ai-power-tools",
            "ref": f"v{VERSION}",
            "sha": remote_ref(remote, f"refs/tags/v{VERSION}"),
        }
        assert e["version"] == VERSION and e["description"] == "d"
        assert list(e) == ["name", "source", "version", "description"]
        raw = (skills / ".claude-plugin" / "marketplace.json").read_bytes()
        assert b"\r\n" not in raw
        # build-plugin's three-file agreement still holds after the pin.
        _v, problems = tool.build_plugin.version_problems(
            skills / tool.PLUGIN_PATH, skills / "manifest.json",
            skills / ".claude-plugin" / "marketplace.json")
        assert problems == []


# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------

def _pinned(skills, remote):
    assert run(skills, remote, "--publish") == 0
    assert run(skills, remote, "--pin-marketplace") == 0


def _edit_source(skills, **changes):
    m = marketplace(skills)
    m["plugins"][0]["source"].update(changes)
    _write_json(skills / ".claude-plugin" / "marketplace.json", m)


class TestVerify:
    def test_passes_once_pinned(self, skills, remote, capsys):
        _pinned(skills, remote)
        capsys.readouterr()
        assert run(skills, remote, "--verify", "--local") == 0
        assert "MARKETPLACE VERIFIED" in capsys.readouterr().out

    def test_reads_the_published_marketplace_by_default(self, skills, remote,
                                                        monkeypatch):
        _pinned(skills, remote)
        seen = []
        real = tool.fetch_bytes
        monkeypatch.setattr(tool, "fetch_bytes",
                            lambda url: (seen.append(url), real(url))[1])
        assert run(skills, remote, "--verify") == 0
        assert seen[0] == (f"https://raw.githubusercontent.com/{tool.SKILLS_REPO}"
                           f"/HEAD/.claude-plugin/marketplace.json")

    def test_fails_on_a_relative_entry(self, skills, remote, capsys):
        assert run(skills, remote, "--verify", "--local") == 1
        assert "development branch" in capsys.readouterr().out

    def test_fails_when_the_sha_is_not_the_tags(self, skills, remote, capsys):
        _pinned(skills, remote)
        _edit_source(skills, sha="b" * 40)
        assert run(skills, remote, "--verify", "--local") == 1
        assert "but the entry pins" in capsys.readouterr().out

    def test_fails_when_the_ref_is_another_release(self, skills, remote, capsys):
        _pinned(skills, remote)
        _edit_source(skills, ref="v9.8.0")
        assert run(skills, remote, "--verify", "--local") == 1
        assert "source.ref is 'v9.8.0'" in capsys.readouterr().out

    def test_fails_when_the_server_bundle_is_gone(self, skills, remote,
                                                  monkeypatch, capsys):
        _pinned(skills, remote)
        monkeypatch.setattr(tool, "url_resolves", lambda url: (False, "HTTP 404"))
        assert run(skills, remote, "--verify", "--local") == 1
        assert "not downloadable" in capsys.readouterr().out

    def test_local_requires_verify(self, skills, remote):
        with pytest.raises(SystemExit):
            run(skills, remote, "--local")


# ---------------------------------------------------------------------------
# Units
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("sha", ["abc123", "A" * 40, "g" * 40, ""])
def test_a_sha_must_be_full_lowercase_hex(sha):
    e = {"name": "ai-power-tools", "version": VERSION,
         "source": tool.pinned_source(REPO, VERSION, sha)}
    assert any("40-character" in p for p in tool.entry_problems(e, VERSION, REPO))


def test_releases_repo_is_read_from_mcp_servers():
    repo, problems = tool.releases_repo({"mcpServers": MCPB}, VERSION)
    assert (repo, problems) == (REPO, [])


def test_blob_sha_matches_git(tmp_path):
    f = tmp_path / "f"
    f.write_bytes(BINARY)
    assert tool.git_blob_sha(BINARY) == git("hash-object", str(f))


def test_an_annotated_tag_resolves_to_its_commit(remote):
    main = remote_ref(remote, "refs/heads/main")
    git("--git-dir", str(remote), "tag", "-a", "v1.0.0", "-m", "annotated", main)
    assert tool.remote_tag_sha(str(remote), "v1.0.0") == main
    assert tool.remote_tag_sha(str(remote), "v0.0.1") is None
