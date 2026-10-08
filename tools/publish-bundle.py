#!/usr/bin/env python3
"""Stage, verify and (only when told to) publish the skills bundle release.

This existed as folklore and the folklore failed. The bundle reached 2.0.0,
2.1.0, 2.2.0 and 2.3.0 on `main` and **no 2.x release was ever cut**, so
`install_skills` kept serving v1.4.1 from 2026-09-22 -- nine skills under
pre-rename filenames -- against a 2.3.0 server. The backlog item for releasing
2.0.0 was even marked done, on the reasoning that the manifest said a higher
number. The release checklist had no step for this at all, which is how a whole
major series went unpublished without anyone noticing.

So the procedure is a script, and the script refuses rather than guesses.

WHAT THE INSTALLER REQUIRES, and why the staging is not a plain copy: GitHub
release assets are flat -- directory separators are not allowed -- so
`skills_installer.py` (see `_asset_url`) derives each asset name by replacing
`/` with `_` in the manifest's file path. That mapping is duplicated nowhere: it
is re-derived here the same way, and a mismatch means a customer's install
fetches a 404.

AND THE HASHES MUST MATCH BYTE FOR BYTE. `install_skills` refuses a bundle whose
files do not hash to `manifest.json`, so a CRLF conversion anywhere between the
repo and the release silently breaks every install. This script verifies every
hash against the manifest BEFORE staging anything, because discovering it after
publishing means cutting another release.

Usage:
    python tools/publish-bundle.py                  # stage + verify only
    python tools/publish-bundle.py --publish TAG    # actually cut the release
    python tools/publish-bundle.py --verify-published   # re-fetch and re-hash

The default does everything except publish, and prints the exact `gh` command it
would run. Publishing is a deliberate, approved act -- it is how customers
receive this -- so it is never the default and never implied.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.request


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MANIFEST = os.path.join(ROOT, "manifest.json")

sys.path.insert(0, HERE)
from _layout import source_path  # noqa: E402

#: Read from the installer rather than restated, so this cannot drift from the
#: repository customers actually fetch from.
#: Searched upward rather than fixed beside ROOT: in a git worktree the repo
#: sits one level deeper (`<repo>.worktrees/<name>/`), so the sibling lookup
#: missed and this script refused to publish at all -- correctly, since it
#: cannot confirm the target repository, but for a reason that has nothing to
#: do with the release. The same defect silently skipped the gate's op-drift
#: check; see tools/gen-operations.py.
_INSTALLER_REL = ("ai-power-tools", "ea-mcp-server",
                  "ea_mcp_server", "skills_installer.py")


def _find_installer() -> str:
    base = ROOT
    while True:
        candidate = os.path.join(os.path.dirname(base), *_INSTALLER_REL)
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(base)
        if parent == base:
            return os.path.join(os.path.dirname(ROOT), *_INSTALLER_REL)
        base = parent


INSTALLER = _find_installer()


def installer_repo() -> str | None:
    """`owner/name` of the repo the installer resolves, or None."""
    try:
        source = open(INSTALLER, encoding="utf-8").read()
    except OSError:
        return None
    marker = "https://github.com/"
    if marker not in source:
        return None
    tail = source.split(marker, 1)[1]
    parts = []
    for ch in tail:
        if ch in '"\n \t':
            break
        parts.append(ch)
    segments = "".join(parts).strip("/").split("/")
    return "/".join(segments[:2]) if len(segments) >= 2 else None


def asset_name(relative_path: str) -> str:
    """The flat asset name for a manifest path.

    Mirrors `skills_installer._asset_url`. If that changes, this must change in
    the same commit -- a divergence is a 404 for every customer, and neither
    side would fail its own tests.
    """
    return relative_path.replace("/", "_")


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load() -> dict:
    return json.load(open(MANIFEST, encoding="utf-8"))


def collect(manifest: dict) -> tuple[list[tuple[str, str]], list[str]]:
    """`(pairs, problems)` where each pair is `(source_path, asset_name)`."""
    pairs: list[tuple[str, str]] = []
    problems: list[str] = []
    seen: dict[str, str] = {}
    for skill in manifest.get("skills", []):
        name = skill.get("name", "?")
        hashes = skill.get("sha256", {})
        for rel in skill.get("files", []):
            src = str(source_path(rel))
            if not os.path.isfile(src):
                problems.append(f"{name}: {rel} is in the manifest but not on "
                                f"disk")
                continue
            declared = hashes.get(rel)
            if not declared:
                problems.append(f"{name}: {rel} has no sha256 in the manifest; "
                                f"install_skills will refuse the bundle")
                continue
            actual = sha256(src)
            if actual != declared:
                problems.append(
                    f"{name}: {rel} does not match its manifest hash "
                    f"(manifest {declared[:12]}..., file {actual[:12]}...). "
                    f"Run tools/regen-manifest.py. If the only difference is "
                    f"line endings, the file was written CRLF and must be LF.")
                continue
            flat = asset_name(rel)
            if flat in seen and seen[flat] != rel:
                problems.append(
                    f"asset name collision: {rel} and {seen[flat]} both "
                    f"flatten to {flat}. One would overwrite the other on the "
                    f"release, and the installer could not tell which it got.")
                continue
            seen[flat] = rel
            pairs.append((src, flat))
    return pairs, problems


def stage(pairs: list[tuple[str, str]], out_dir: str) -> list[str]:
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)
    staged = []
    for src, flat in pairs:
        dest = os.path.join(out_dir, flat)
        shutil.copyfile(src, dest)
        # Copy then re-hash: a copy that altered a byte would otherwise be
        # discovered by a customer rather than here.
        if sha256(dest) != sha256(src):
            raise SystemExit(f"staging altered {flat}; refusing to continue")
        staged.append(dest)
    manifest_dest = os.path.join(out_dir, "manifest.json")
    shutil.copyfile(MANIFEST, manifest_dest)
    staged.append(manifest_dest)
    return staged


def verify_published(repo: str, manifest: dict) -> int:
    """Fetch what customers fetch and re-hash it. The only proof that counts."""
    base = f"https://github.com/{repo}/releases/latest/download"
    bad = 0
    try:
        with urllib.request.urlopen(f"{base}/manifest.json", timeout=30) as r:
            published = json.loads(r.read().decode("utf-8"))
    except Exception as exc:
        print(f"FAIL: could not fetch the published manifest: {exc}")
        return 1
    local_v = manifest.get("bundle_version")
    pub_v = published.get("bundle_version")
    print(f"published bundle_version: {pub_v}  (local {local_v})")
    if pub_v != local_v:
        print("FAIL: the published manifest is a different version from the "
              "one on disk.")
        bad += 1
    for skill in published.get("skills", []):
        for rel, declared in (skill.get("sha256") or {}).items():
            url = f"{base}/{asset_name(rel)}"
            try:
                with urllib.request.urlopen(url, timeout=30) as r:
                    got = hashlib.sha256(r.read()).hexdigest()
            except Exception as exc:
                print(f"FAIL: {rel} -> {url}: {exc}")
                bad += 1
                continue
            if got != declared:
                print(f"FAIL: {rel} published bytes do not match the published "
                      f"manifest hash")
                bad += 1
    print("PUBLISHED BUNDLE VERIFIED" if not bad
          else f"{bad} problem(s) with the published bundle")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--publish", metavar="TAG",
                    help="cut the release with this tag, e.g. v3.0.0")
    ap.add_argument("--verify-published", action="store_true",
                    help="re-fetch the published assets and re-hash them")
    ap.add_argument("--out", default=os.path.join(ROOT, ".release-staging"))
    ap.add_argument("--notes-file", metavar="PATH",
                    help="Release body. Defaults to a generated note naming "
                         "the bundle and server versions.")
    args = ap.parse_args()

    manifest = load()
    repo = installer_repo()
    print(f"bundle_version      : {manifest.get('bundle_version')}")
    print(f"min_server_version  : {manifest.get('min_server_version')}")
    print(f"installer resolves  : {repo or 'COULD NOT DETERMINE'}")
    if repo is None:
        print("FAIL: cannot read the target repository out of "
              "skills_installer.py. Publishing to a guessed repository would "
              "leave customers fetching from the other one.")
        return 1

    if args.verify_published:
        return verify_published(repo, manifest)

    pairs, problems = collect(manifest)
    for p in problems:
        print(f"FAIL: {p}")
    if problems:
        print(f"\n{len(problems)} problem(s). Nothing staged.")
        return 1

    staged = stage(pairs, args.out)

    # The packaged plugin ships in the same release as the flat bundle assets:
    # the marketplace serves Claude Code the released tree that
    # tools/publish-plugin.py pins in the releases repository, but Cowork is fed by
    # uploading this file, and a release without it leaves that channel with
    # nothing to install. Built by tools/build-plugin.py.
    plugin = os.path.join(ROOT, "dist", "ai-power-tools.plugin")
    if not os.path.isfile(plugin):
        print("FAIL: dist/ai-power-tools.plugin is missing - "
              "run tools/build-plugin.py before publishing.")
        return 1
    plugin_staged = os.path.join(args.out, os.path.basename(plugin))
    shutil.copy2(plugin, plugin_staged)
    staged = list(staged) + [plugin_staged]
    print(f"\nstaged {len(staged)} assets in {args.out}")

    # Build the REAL command, including the real notes file and the real asset
    # list. Both used to be placeholders substituted nowhere: "<NOTES>" was
    # passed to gh verbatim, and the asset list was replaced at call time by
    # `cmd[:-1] + [args.out]`, which dropped the last asset and handed gh the
    # staging DIRECTORY instead. Neither could fail in a dry run, because the
    # dry run prints `cmd[:8]` and never executes -- so the rehearsal was green
    # and the performance was broken, every time, until someone published.
    notes_path = args.notes_file
    if not notes_path:
        notes_path = os.path.join(args.out, "RELEASE-NOTES.md")
        body = "\n".join([
            f"Skills bundle {manifest.get('bundle_version')} for "
            f"AI Power Tools for Sparx EA.",
            "",
            f"Requires server **{manifest.get('min_server_version')}** or "
            f"newer. The floor is enforced all or nothing: an older server "
            f"receives no files and an error naming the version it needs.",
            "",
            f"{len(manifest.get('skills', []))} entries. Installed with "
            f"`install_skills`; the installer verifies every file against "
            f"`manifest.json` and refuses any whose bytes do not match.",
            "",
        ])
        with open(notes_path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    assets = [os.path.join(args.out, os.path.basename(p)) for p in staged]
    cmd = ["gh", "release", "create", args.publish or "<TAG>",
           "--repo", repo, "--title",
           f"Skills bundle {manifest.get('bundle_version')}",
           "--notes-file", notes_path] + assets

    if not args.publish:
        print("\nDRY RUN — nothing published. The command would be:\n")
        # Print every flag, eliding only the asset paths. The old version
        # printed cmd[:8], which stopped exactly before --notes-file and so
        # concealed that it was the literal string "<NOTES>".
        flags = cmd[:len(cmd) - len(assets)]
        print("  " + " ".join(flags) + f" \\\n    <{len(assets)} assets>")
        print(f"\n  notes file: {notes_path}")
        missing = [a for a in assets if not os.path.isfile(a)]
        if missing:
            print(f"  WARNING: {len(missing)} staged asset(s) not on disk")
        print("\nPublishing is a deliberate act and needs approval. Re-run "
              "with --publish TAG once you have it, then immediately run "
              "--verify-published: a bundle whose bytes do not match its "
              "manifest is refused by every customer's installer, and the only "
              "way to know is to fetch it from outside.")
        return 0

    print(f"\npublishing {args.publish} to {repo} ...")
    out = subprocess.run(cmd, capture_output=True, text=True)
    print(out.stdout or out.stderr)
    if out.returncode != 0:
        return out.returncode
    print("published. Now verifying from outside ...")
    return verify_published(repo, manifest)


if __name__ == "__main__":
    sys.exit(main())
