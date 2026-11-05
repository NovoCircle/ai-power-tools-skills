#!/usr/bin/env python3
"""Publish the released plugin trees, and pin the marketplace to them.

The marketplace entry for `ai-power-tools` used to be a relative path into this
repository, and this repository is where skills development happens. So a fresh
`claude plugin install ai-power-tools@novocircle` took whatever was on `main`
that minute -- every merge since the last release -- labeled with the last
release's version and paired with that release's server, which lacked the
operations the newer skills call. Existing installs were insulated only because
Claude Code updates a plugin when its version changes, not when its files do.

The rule: customers install the RELEASED plugin, never the development branch.
So at release this script

1. writes both plugin trees (the tool plugin and the language plugin), byte for
   byte as `tools/build-plugin.py` packaged them into `dist/<name>.plugin`, into
   the releases repository under `plugins/<name>/`, commits them in one commit,
   and tags that commit `v<version>` -- the tag the server release is then cut on
   (`--publish`); and
2. points both marketplace entries at that tag and commit with a `git-subdir`
   source (`--pin-marketplace`), refusing unless the tag exists, the sha is the
   one the tag names, and the trees there carry the expected `plugin.json`. The
   first pin adds the language plugin's entry, and declares it as a dependency in
   the tool plugin's entry. The dependency sits in the marketplace entry because
   that installs it (measured, 2026-11-04) and leaves the `.plugin` archives with
   no dependency, so one tree still ships to both channels unchanged.

After that, a merge to `main` here changes nothing a customer installs. Only a
release tag does, and only this script moves the marketplace to one.

The plugins are skills only: they declare no server, and the build and this
script both refuse a `plugin.json` that has `mcpServers` or a plugin tree with a
`bin/`. The server is the Claude Desktop extension, released separately from the
same releases repository, so the plugin trees are published to that repository
and the server release is cut on the same tag.

Usage:
    python tools/publish-plugin.py                    # dry run: stage, verify, print every step
    python tools/publish-plugin.py --publish          # push the trees and tag them v<version>
    python tools/publish-plugin.py --pin-marketplace  # after the server release is promoted
    python tools/publish-plugin.py --verify           # from outside, as a customer resolves it
    python tools/publish-plugin.py --verify --local   # the same, for the marketplace.json on disk

The default does everything except push, tag or edit, and prints exactly what
`--publish` and `--pin-marketplace` would do. Publishing is how customers
receive this, so it is never the default and never implied.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

_spec = importlib.util.spec_from_file_location("build_plugin", HERE / "build-plugin.py")
build_plugin = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_plugin)

PLUGIN_NAME = "ai-power-tools"
#: Where the tree sits, both here and in the releases repository. The same
#: path in both, so nothing has to translate between them.
PLUGIN_PATH = "plugins/ai-power-tools"
PLUGIN_JSON = f"{PLUGIN_PATH}/.claude-plugin/plugin.json"
#: The language plugin. It ships with the tool plugin: one commit, one tag.
SHELF_NAME = "ai-power-tools-languages"
SHELF_PATH = f"plugins/{SHELF_NAME}"
#: Every plugin that ships as `(name, path)`, tool plugin first.
PLUGINS = ((PLUGIN_NAME, PLUGIN_PATH), (SHELF_NAME, SHELF_PATH))
#: The repository customers add as the marketplace. `--verify` reads its
#: `marketplace.json` from the default branch, exactly as Claude Code does.
SKILLS_REPO = "NovoCircle/ai-power-tools-skills"
#: Where the released plugin tree is published and tagged, and where the server
#: release is cut on the same tag.
RELEASES_REPO = "NovoCircle/ai-power-tools-releases"
STAGING_DIR = ".plugin-release-staging"

_SHA = re.compile(r"^[0-9a-f]{40}$")


# ---------------------------------------------------------------------------
# Paths and local checks
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Paths:
    root: Path

    @property
    def plugin(self) -> Path:
        return self.root / PLUGIN_PATH

    @property
    def plugin_json(self) -> Path:
        return self.root / PLUGIN_JSON

    @property
    def manifest(self) -> Path:
        return self.root / "manifest.json"

    @property
    def marketplace(self) -> Path:
        return self.root / ".claude-plugin" / "marketplace.json"

    @property
    def shelf(self) -> Path:
        return self.root / SHELF_PATH

    def archive(self, name: str = PLUGIN_NAME) -> Path:
        return self.root / "dist" / f"{name}.plugin"

    @property
    def staging(self) -> Path:
        return self.root / STAGING_DIR


def tag_for(version: str) -> str:
    return f"v{version}"


def git_url(repo: str) -> str:
    return f"https://github.com/{repo}.git"


def raw_url(repo: str, ref: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/{repo}/{ref}/{path}"


def git_blob_sha(data: bytes) -> str:
    """The object id git gives these bytes, so a tree can be checked offline."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def read_archive(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as zf:
        return {n: zf.read(n) for n in zf.namelist() if not n.endswith("/")}


def archive_problems(archive: dict[str, bytes], plugin_dir: Path,
                     name: str = PLUGIN_NAME) -> list[str]:
    """The archive must be the tree as it is now, not as it was at some build.

    The archive is what ships -- the same bytes go to Cowork as a `.plugin` and
    to Claude Code through the releases repository -- so a stale one would put
    an older tree behind a newer version number.
    """
    path = f"plugins/{name}"
    on_disk = {f.relative_to(plugin_dir).as_posix(): f.read_bytes()
               for f in build_plugin.plugin_files(plugin_dir)}
    problems = []
    for rel in sorted(set(on_disk) - set(archive)):
        problems.append(f"{rel} is in {path}/ but not in the archive")
    for rel in sorted(set(archive) - set(on_disk)):
        problems.append(f"{rel} is in the archive but no longer in {path}/")
    for rel in sorted(set(on_disk) & set(archive)):
        if on_disk[rel] != archive[rel]:
            problems.append(f"{rel} differs between the archive and {path}/")
    if problems:
        problems.append(f"dist/{name}.plugin is stale - run "
                        f"tools/build-plugin.py")
    return problems


def find_entry(marketplace: dict, name: str = PLUGIN_NAME) -> dict | None:
    return next((p for p in marketplace.get("plugins", [])
                 if p.get("name") == name), None)


def pinned_source(repo: str, version: str, sha: str,
                  path: str = PLUGIN_PATH) -> dict:
    """The entry's `source`, in the shape the Claude Code marketplace reference
    documents under "Plugin sources": `git-subdir` takes `url`, `path`, `ref`
    and `sha`, and when both are set Claude Code checks out `sha`."""
    return {
        "source": "git-subdir",
        "url": git_url(repo),
        "path": path,
        "ref": tag_for(version),
        "sha": sha,
    }


def pin_entries(marketplace: dict, repo: str, version: str, sha: str,
                shelf_description: str) -> dict:
    """A copy of the marketplace with both plugin entries pinned. Key order kept.

    Adds the language plugin's entry when it is missing, at the same tag and
    commit, and declares it as a dependency in the tool plugin's entry: a bare name
    with no version range, because a range resolves against `<plugin>--v<version>`
    tags and ours are `v<version>`.
    """
    out = json.loads(json.dumps(marketplace))
    entry = find_entry(out)
    if entry is None:
        raise ValueError(f"no {PLUGIN_NAME} entry in marketplace.json")
    if find_entry(out, SHELF_NAME) is None:
        out["plugins"].append({"name": SHELF_NAME, "source": None, "version": None,
                               "description": shelf_description})
    for name, path in PLUGINS:
        pinned = find_entry(out, name)
        pinned["source"] = pinned_source(repo, version, sha, path)
        pinned["version"] = version
    entry["dependencies"] = [SHELF_NAME]
    return out


def entry_problems(entry: dict | None, version: str, repo: str,
                   name: str = PLUGIN_NAME, path: str = PLUGIN_PATH) -> list[str]:
    """Whether a marketplace entry is pinned to the release of `version`."""
    if entry is None:
        return [f"marketplace.json has no {name} entry"]
    problems = []
    if entry.get("version") != version:
        problems.append(f"entry version is {entry.get('version')!r}, expected "
                        f"{version!r}")
    src = entry.get("source")
    if not isinstance(src, dict):
        return problems + [
            f"entry source is {src!r}, a path inside the skills repository: a "
            f"fresh install gets that repository's development branch"]
    want = pinned_source(repo, version, src.get("sha", ""), path)
    for key in ("source", "url", "path", "ref"):
        if src.get(key) != want[key]:
            problems.append(f"source.{key} is {src.get(key)!r}, expected "
                            f"{want[key]!r}")
    if not _SHA.match(str(src.get("sha", ""))):
        problems.append(f"source.sha {src.get('sha')!r} is not a full "
                        f"40-character lowercase commit sha")
    return problems


def dependency_problems(entry: dict | None) -> list[str]:
    """The tool plugin's entry has to bring the language plugin."""
    if entry is not None and SHELF_NAME not in (entry.get("dependencies") or []):
        return [f"the {PLUGIN_NAME} entry does not declare {SHELF_NAME} in "
                f"dependencies, so installing it would not bring the language guides"]
    return []


def write_json(path: Path, data: dict) -> None:
    # ensure_ascii matches how the file is written today; LF because every
    # shipped file here is LF.
    path.write_bytes((json.dumps(data, indent=2) + "\n").encode("utf-8"))


# ---------------------------------------------------------------------------
# Git and network -- the only functions the tests replace
# ---------------------------------------------------------------------------

def _git(*args: str, cwd: Path | None = None) -> str:
    out = subprocess.run(["git", *args], cwd=cwd, capture_output=True,
                         text=True)
    if out.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: "
                           f"{(out.stderr or out.stdout).strip()}")
    return out.stdout.strip()


def remote_tag_sha(remote: str, tag: str) -> str | None:
    """The commit `tag` names on `remote`, or None if there is no such tag.

    An annotated tag lists twice; the peeled `^{}` line is the commit.
    """
    out = _git("ls-remote", "--tags", remote, f"refs/tags/{tag}",
               f"refs/tags/{tag}^{{}}")
    refs = {ref: sha for sha, ref in (line.split("\t", 1)
                                      for line in out.splitlines() if "\t" in line)}
    return refs.get(f"refs/tags/{tag}^{{}}") or refs.get(f"refs/tags/{tag}")


def fetch_bytes(url: str) -> tuple[bytes | None, str]:
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return r.read(), ""
    except Exception as exc:  # noqa: BLE001 -- reported, never swallowed
        return None, str(exc)


def skills_source_rev(root: Path) -> tuple[str, bool]:
    """`(commit, dirty)` of the shipped files in this repository."""
    try:
        rev = _git("rev-parse", "HEAD", cwd=root)
        dirty = bool(_git("status", "--porcelain", "--",
                          *(path for _name, path in PLUGINS),
                          ".claude-plugin", "manifest.json", cwd=root))
    except (RuntimeError, OSError):
        return "unknown", True
    return rev, dirty


# ---------------------------------------------------------------------------
# Staging the release commit
# ---------------------------------------------------------------------------

def _rmtree(path: Path) -> None:
    # git marks pack files read-only, which Windows refuses to delete.
    def _retry(func, p, _exc):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    if path.exists():
        if sys.version_info >= (3, 12):
            shutil.rmtree(path, onexc=_retry)
        else:
            shutil.rmtree(path, onerror=_retry)


@dataclass
class Staged:
    clone: Path
    commit: str
    base: str
    created: bool          # False when main already carries this exact tree
    problems: list[str]


def tree_problems(clone: Path, commit: str, archive: dict[str, bytes],
                  path: str = PLUGIN_PATH) -> list[str]:
    """Compare the committed tree to the archive by git object id.

    This is the check that matters: whatever git did on the way in (an
    `autocrlf` on the machine, a filter), the blobs are what a customer's
    checkout of the sha receives.
    """
    listing = _git("ls-tree", "-r", "--full-tree", commit, "--", path, cwd=clone)
    committed = {}
    for line in listing.splitlines():
        meta, file = line.split("\t", 1)
        committed[file[len(path) + 1:]] = meta.split()[2]
    problems = []
    for rel, data in sorted(archive.items()):
        got = committed.pop(rel, None)
        if got is None:
            problems.append(f"{rel} is missing from the staged commit")
        elif got != git_blob_sha(data):
            problems.append(f"{rel} was altered on the way into git (blob "
                            f"{got[:12]}, archive {git_blob_sha(data)[:12]})")
    for rel in sorted(committed):
        problems.append(f"{rel} is in the staged commit but not in the archive")
    return problems


def stage(archives: dict[str, dict[str, bytes]], remote: str, version: str,
          source_rev: str, staging: Path) -> Staged:
    """Clone the releases repository and commit both trees into it, locally, in
    one commit. `archives` is keyed by the tree's path in the repository."""
    _rmtree(staging)
    staging.mkdir(parents=True)
    clone = staging / "releases"
    # autocrlf off in the clone itself: the bytes written must be the bytes
    # committed. A global autocrlf=true is the default on Windows.
    _git("clone", "--quiet", "-c", "core.autocrlf=false", "-c",
         "core.safecrlf=false", remote, str(clone))
    base = _git("rev-parse", "HEAD", cwd=clone)

    for path, archive in archives.items():
        dest = clone / path
        _rmtree(dest)
        for rel, data in archive.items():
            f = dest / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(data)
        _git("add", "-A", "--", path, cwd=clone)

    unchanged = subprocess.run(["git", "diff", "--cached", "--quiet"],
                               cwd=clone).returncode == 0
    if unchanged:
        commit, created = base, False
    else:
        _git("commit", "--quiet", "-m",
             f"{PLUGIN_NAME} plugin {version}\n\n"
             f"Generated by tools/publish-plugin.py in {SKILLS_REPO} from "
             f"commit {source_rev}.\nDo not edit by hand: the next release "
             f"replaces this tree.", cwd=clone)
        commit, created = _git("rev-parse", "HEAD", cwd=clone), True
    return Staged(clone, commit, base, created,
                  [p for path, archive in archives.items()
                   for p in tree_problems(clone, commit, archive, path)])


def tag_state(staged: Staged, remote: str, tag: str) -> tuple[str, str | None]:
    """`("absent" | "same" | "different", sha)` for the tag on the remote.

    "same" means the tag already names a commit carrying these exact trees -- a
    re-run after publishing -- and nothing needs pushing. A tag missing either
    tree is "different".
    """
    sha = remote_tag_sha(remote, tag)
    if sha is None:
        return "absent", None
    _git("fetch", "--quiet", "origin", f"refs/tags/{tag}:refs/tags/{tag}",
         cwd=staged.clone)
    for _name, path in PLUGINS:
        try:
            theirs = _git("rev-parse", f"{sha}:{path}", cwd=staged.clone)
        except RuntimeError:
            return "different", sha
        if theirs != _git("rev-parse", f"{staged.commit}:{path}", cwd=staged.clone):
            return "different", sha
    return "same", sha


# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------

def _local_state(paths: Paths) -> tuple[str | None, str | None, dict, list[str]]:
    version, problems = build_plugin.version_problems(
        paths.plugin, paths.manifest, paths.marketplace)
    if problems:
        return version, None, {}, problems
    pj = json.loads(paths.plugin_json.read_text(encoding="utf-8"))
    return version, RELEASES_REPO, pj, (build_plugin.package_problems(paths.plugin)
                                        + build_plugin.shelf_problems(paths.shelf, paths.plugin))


def _shelf_description(paths: Paths) -> str:
    return json.loads((paths.shelf / ".claude-plugin" / "plugin.json")
                      .read_text(encoding="utf-8")).get("description", "")


def _fail(problems: list[str], what: str = "Nothing pushed, tagged or edited") -> int:
    for p in problems:
        print(f"FAIL: {p}")
    print(f"\n{len(problems)} problem(s). {what}.")
    return 1


def run_stage(paths: Paths, remote: str | None, publish: bool) -> int:
    version, repo, _pj, problems = _local_state(paths)
    if problems:
        return _fail(problems)
    tag = tag_for(version)
    remote = remote or git_url(repo)
    print(f"plugin version      : {version}")
    print(f"releases repository : {repo}")
    print(f"release tag         : {tag}")

    archives: dict[str, dict[str, bytes]] = {}
    for name, path in PLUGINS:
        if not paths.archive(name).is_file():
            return _fail([f"dist/{name}.plugin is missing - run "
                          f"tools/build-plugin.py"])
        archive = read_archive(paths.archive(name))
        problems = archive_problems(archive, paths.root / path, name)
        if problems:
            return _fail(problems)
        archives[path] = archive
        print(f"archive             : dist/{name}.plugin, {len(archive)} "
              f"files, identical to {path}/")

    rev, dirty = skills_source_rev(paths.root)
    print(f"skills source       : {rev}{'  (UNCOMMITTED CHANGES)' if dirty else ''}")
    if dirty and publish:
        return _fail(["the shipped files have uncommitted changes. The release "
                      "commit records which skills commit it came from, so "
                      "commit first."])

    staged = stage(archives, remote, version, rev, paths.staging)
    if staged.problems:
        return _fail(staged.problems)
    clone = os.path.relpath(staged.clone, paths.root)
    if staged.created:
        print(f"staged commit       : {staged.commit}  on releases main "
              f"{staged.base[:12]}  (in {clone})")
    else:
        print(f"staged commit       : {staged.commit}  releases main already "
              f"carries this tree")
    print(f"tree check          : {sum(len(a) for a in archives.values())} blobs "
          f"match the archives byte for byte")

    state, tag_sha = tag_state(staged, remote, tag)
    print(f"remote tag {tag:<9}: "
          + {"absent": "absent",
             "same": f"exists at {tag_sha}, carrying these exact trees",
             "different": f"exists at {tag_sha}, WITHOUT these trees"}[state])
    if state == "different":
        return _fail([
            f"{tag} already exists on {repo} at {tag_sha} and does not carry "
            f"these plugin trees. A published tag is never moved: anyone who "
            f"fetched it would silently hold a different tree under the same "
            f"name. If this is a draft that failed its smoke test, delete the "
            f"draft release and the tag first (build skill Phase 7, \"If the "
            f"smoke test FAILS\"), then re-run."])

    pin_sha = tag_sha if state == "same" else staged.commit
    steps = []
    if state == "absent":
        if staged.created:
            steps.append(["git", "-C", clone, "push", "origin",
                          "HEAD:refs/heads/main"])
        steps.append(["git", "-C", clone, "tag", tag, staged.commit])
        steps.append(["git", "-C", clone, "push", "origin", f"refs/tags/{tag}"])

    marketplace = json.loads(paths.marketplace.read_text(encoding="utf-8"))
    pinned = pin_entries(marketplace, repo, version, pin_sha, _shelf_description(paths))
    after = {name: json.dumps(find_entry(pinned, name)["source"], indent=2)
             for name, _path in PLUGINS}

    if not publish:
        print("\nDRY RUN - nothing pushed, tagged or edited.")
        if steps:
            print("\n--publish would run:\n")
            for s in steps:
                print("  " + " ".join(s))
        else:
            print(f"\n--publish has nothing to do: {tag} is already published.")
        print(f"\nThen, once server release {tag} is promoted, --pin-marketplace "
              f"would set these entries' sources in "
              f".claude-plugin/marketplace.json, and declare {SHELF_NAME} as a "
              f"dependency of {PLUGIN_NAME}:\n")
        for name, source in after.items():
            print(f"  {name}:")
            print("  " + source.replace("\n", "\n  "))
        if steps:
            print("\n  (the sha is this staging run's commit; --publish "
                  "re-stages, so the sha it prints is the one that counts)")
        return 0

    for s in steps:
        print(f"\n$ {' '.join(s)}")
        _git(*s[3:], cwd=staged.clone)
    if steps:
        got = remote_tag_sha(remote, tag)
        if got != staged.commit:
            return _fail([f"after pushing, {tag} names {got}, not "
                          f"{staged.commit}"], "Check the releases repository")
    print(f"\nPUBLISHED: {tag} -> {pin_sha} carries the {version} trees of "
          f"{PLUGIN_NAME} and {SHELF_NAME}. Customers see nothing yet: the marketplace still pins the "
          f"previous release. Cut the server release on this tag (draft, "
          f"--verify-tag), smoke-test, promote, then run --pin-marketplace.")
    return 0


def _published_plugin_problems(repo: str, sha: str, path: str, version: str,
                               label: str) -> list[str]:
    """Whether `plugin.json` under `path` at `sha` is the release of `version`."""
    plugin_json = f"{path}/.claude-plugin/plugin.json"
    data, err = fetch_bytes(raw_url(repo, sha, plugin_json))
    if data is None:
        return [f"{plugin_json} could not be read at {sha}: {err}"]
    theirs = json.loads(data.decode("utf-8"))
    problems = []
    if theirs.get("version") != version:
        problems.append(f"{plugin_json} at {label} says version "
                        f"{theirs.get('version')!r}, expected {version!r}")
    if "mcpServers" in theirs:
        problems.append(f"{plugin_json} at {label} declares mcpServers. The "
                        f"plugin is skills only.")
    return problems


def run_pin(paths: Paths, remote: str | None) -> int:
    version, repo, _pj, problems = _local_state(paths)
    if problems:
        return _fail(problems, "marketplace.json not edited")
    tag = tag_for(version)
    remote = remote or git_url(repo)
    sha = remote_tag_sha(remote, tag)
    if sha is None:
        return _fail([f"{tag} does not exist on {repo}. Run --publish first; "
                      f"the marketplace is only ever pointed at a release tag "
                      f"that exists."], "marketplace.json not edited")
    print(f"remote tag {tag:<9}: {sha}")

    problems = []
    for _name, path in PLUGINS:
        problems += _published_plugin_problems(repo, sha, path, version, tag)
    if problems:
        return _fail(problems, "marketplace.json not edited")

    marketplace = json.loads(paths.marketplace.read_text(encoding="utf-8"))
    before = find_entry(marketplace)["source"]
    pinned = pin_entries(marketplace, repo, version, sha, _shelf_description(paths))
    write_json(paths.marketplace, pinned)
    print(f"\nmarketplace.json {PLUGIN_NAME} source:\n  was {json.dumps(before)}"
          f"\n  now {json.dumps(find_entry(pinned)['source'])}")
    print(f"marketplace.json {SHELF_NAME} source:\n"
          f"  now {json.dumps(find_entry(pinned, SHELF_NAME)['source'])}")
    print("\nCommit this on the release branch and merge it: customers follow "
          "the marketplace on the skills repository's default branch, so the "
          "merge is the moment they switch. Then run --verify.")
    return 0


def run_verify(paths: Paths, remote: str | None, local: bool) -> int:
    version, repo, _pj, problems = _local_state(paths)
    if problems:
        return _fail(problems, "Nothing verified")
    if local:
        where = ".claude-plugin/marketplace.json (local)"
        marketplace = json.loads(paths.marketplace.read_text(encoding="utf-8"))
    else:
        url = raw_url(SKILLS_REPO, "HEAD", ".claude-plugin/marketplace.json")
        where = url
        data, err = fetch_bytes(url)
        if data is None:
            return _fail([f"could not fetch {url}: {err}"], "Nothing verified")
        marketplace = json.loads(data.decode("utf-8"))
    print(f"marketplace         : {where}")
    print(f"expected version    : {version}  (local plugin.json)")
    entry = find_entry(marketplace)
    problems = entry_problems(entry, version, repo) + dependency_problems(entry)
    problems += entry_problems(find_entry(marketplace, SHELF_NAME), version, repo,
                               SHELF_NAME, SHELF_PATH)
    if problems:
        return _fail(problems, "Marketplace NOT verified")
    src = entry["source"]
    remote = remote or src["url"]

    sha = remote_tag_sha(remote, src["ref"])
    print(f"tag {src['ref']:<16}: {sha}  (on {repo})")
    for name, _path in PLUGINS:
        pinned = find_entry(marketplace, name)["source"]["sha"]
        if sha != pinned:
            problems.append(f"{src['ref']} names {sha}, but the {name} entry pins "
                            f"{pinned}")
    for _name, path in PLUGINS:
        problems += _published_plugin_problems(repo, src["sha"], path, version, src["sha"])
    if problems:
        return _fail(problems, "Marketplace NOT verified")
    print("\nMARKETPLACE VERIFIED. Finish with a clean `claude plugin "
          "marketplace add` and install on a machine that has never had the "
          "plugin: that is the customer's path, and nothing here exercises it.")
    return 0


def main(argv: list[str] | None = None, root: Path = ROOT) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true",
                      help="stage and verify, change nothing (the default)")
    mode.add_argument("--publish", action="store_true",
                      help="push both plugin trees to the releases repository "
                           "and tag them v<version>")
    mode.add_argument("--pin-marketplace", action="store_true",
                      help="point the marketplace entries at the existing release "
                           "tag and its sha")
    mode.add_argument("--verify", action="store_true",
                      help="check, from outside, that the marketplace entry "
                           "resolves to the release")
    ap.add_argument("--local", action="store_true",
                    help="with --verify: check the marketplace.json on disk "
                         "instead of the published one")
    ap.add_argument("--releases-remote", metavar="URL",
                    help="git remote for the releases repository (default: "
                         "the releases repository on GitHub)")
    args = ap.parse_args(argv)
    if args.local and not args.verify:
        ap.error("--local applies only to --verify")

    paths = Paths(Path(root))
    try:
        if args.verify:
            return run_verify(paths, args.releases_remote, args.local)
        if args.pin_marketplace:
            return run_pin(paths, args.releases_remote)
        return run_stage(paths, args.releases_remote, args.publish)
    except RuntimeError as exc:
        return _fail([str(exc)])


if __name__ == "__main__":
    sys.exit(main())
