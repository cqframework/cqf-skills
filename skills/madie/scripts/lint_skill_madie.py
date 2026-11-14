#!/usr/bin/env python3
"""Lint the madie skill for the source and version conventions.

Usage:
    lint_skill_madie.py [--skill-dir DIR] [--cql-lint FILE] [--repo ID=GITDIR ...]

The generic checks come from the cql skill's linter, imported by path (it is owned by the cql
skill; don't copy it):
    S1-S4  SOURCES.md registry (exists, Kind, pinned locator, Status)
    H1-H3  resource files have Baseline: and Sources: lines, and cite only what they list
    C1     every [src: ID …] ID is in SOURCES.md
    C7     a source with a resources/… local copy: the locator's file exists under it
This linter adds:
    G1  a git-backed source (no local copy; pinned locator `name@ref`): the locator is
        `path:line[-line]`, the file exists at ref, and the lines are in bounds
    G0  the checkout for a git-backed source is not available (pass --repo ID=GITDIR)
    L1  a local-copy locator with a `#Lnn[-Lmm]` anchor: the lines are in bounds
    T1  [src: TOOLS-… CodeSystem-ig-parameters.json#code]: the code exists in that CodeSystem

Exit status 1 if any error was reported. Warnings never fail the run.
"""

import argparse
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

HOME = Path.home()
SCRIPTS = Path(__file__).resolve().parent
# The generic checks live in lint_skill.py, a copy of the cql skill's linter kept identical to it
# (scripts/validate_skills.py enforces that).
DEFAULT_CQL_LINT = SCRIPTS / "lint_skill.py"
# Where scripts/fetch-sources.sh caches the pinned source repos. Others can be passed with
# --repo ID=GITDIR.
CACHE_DIR = Path(os.environ.get("MADIE_SKILL_CACHE", HOME / ".cache" / "madie-skill"))
DEFAULT_REPOS = {
    "MEASURE-18c8d4d": CACHE_DIR / "madie-measure.git",
    "MSVC-251a73d": CACHE_DIR / "measure-service.git",
    "FHIRSVC-51b9b37": CACHE_DIR / "madie-fhir-service.git",
    "PKGUTIL-dd71537": CACHE_DIR / "packaging-utility.git",
    "JMODELS-49ffdec": CACHE_DIR / "madie-java-models.git",
    "TSMODELS-960ea63": CACHE_DIR / "madie-models.git",
    "EDITOR-e2635c7": CACHE_DIR / "madie-editor.git",
    "ECQM2025-d4e0edd": CACHE_DIR / "ecqm-content-qicore-2025.git",
    "DQMCMS-757d7c6": CACHE_DIR / "dqm-content-cms-2026.git",
}
GIT_LOCATOR_RE = re.compile(r"^[\w.\-]+(?:/[\w.\-]+)?@([0-9A-Za-z._\-]+)$")
LINE_LOC_RE = re.compile(r"^(.+?):(\d+)(?:-(\d+))?$")
ANCHOR_LINES_RE = re.compile(r"#L(\d+)(?:-L?(\d+))?$")


def load_cql_lint(path: Path):
    spec = importlib.util.spec_from_file_location("cql_lint_skill", path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"cql linter not found at {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_repo_arg(arg: str):
    """'ID=GITDIR' -> ('ID', Path(GITDIR)). Only the first '=' splits, so any path form works.

    | Input                     | ID    | Path                 |
    | ------------------------- | ----- | -------------------- |
    | VSCQL=/path/to/vscode-cql | VSCQL | /path/to/vscode-cql  |
    | VSCQL=C:\\src\\vscode-cql  | VSCQL | C:\\src\\vscode-cql   |
    | VSCQL=C:/src/vscode-cql   | VSCQL | C:/src/vscode-cql    |
    """
    sid, sep, path = arg.partition("=")
    if not sep or not sid or not path:
        raise ValueError(f"--repo needs ID=GITDIR, got {arg!r}")
    return sid, Path(path)


def git_ref(row):
    """The ref of a git-backed registry row, or None if the row is not git-backed."""
    loc = row.get("pinned locator", "").strip("` ")
    m = GIT_LOCATOR_RE.match(loc)
    return m.group(1) if m else None


def split_line_locator(loc: str):
    """'a/b.java:12-14' -> ('a/b.java', 12, 14); 'a/b.java:12' -> ('a/b.java', 12, 12); else None.

    The path is repo-relative, but a drive-letter path still splits at the last ':':

    | Locator               | Path            | Lines  |
    | --------------------- | --------------- | ------ |
    | src/a/B.java:12-14    | src/a/B.java    | 12-14  |
    | C:\\src\\B.java:12      | C:\\src\\B.java   | 12     |
    | C:/src/B.java:12      | C:/src/B.java   | 12     |
    """
    m = LINE_LOC_RE.match(loc.strip("` "))
    if not m:
        return None
    lo = int(m.group(2))
    return m.group(1), lo, int(m.group(3) or lo)


def anchor_lines(loc: str):
    """'file#L12' -> (12, 12); 'file#L12-L14' or 'file#L12-14' -> (12, 14); else None."""
    m = ANCHOR_LINES_RE.search(loc.split()[0])
    if not m:
        return None
    lo = int(m.group(1))
    return lo, int(m.group(2) or lo)


def codesystem_codes(path: Path):
    def walk(cs):
        for c in cs:
            yield c["code"]
            yield from walk(c.get("concept", []))
    return set(walk(json.loads(path.read_text(encoding="utf-8")).get("concept", [])))


def check_extra(path: Path, skill: Path, sources, repos, lint, rep):
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(skill) if path.is_relative_to(skill) else path
    cs_cache = {}
    for start, _end, block, _section in lint.blocks(text):
        for cm in lint.SRC_RE.finditer(block):
            sid, loc = cm.group(1), cm.group(2)
            row = sources.get(sid)
            if row is None:
                continue  # C1 already reported it
            where = f"{rel}:{start}"
            local = lint.local_copy(row)
            ref = None if local else git_ref(row)
            if ref:
                parts = split_line_locator(loc)
                if not parts:
                    rep.error(where, "G1", f"{sid} locator needs 'path:line[-line]': {loc!r}")
                    continue
                repo = repos.get(sid)
                if repo is None or not repo.exists():
                    rep.error(where, "G0", f"{sid}: no checkout (pass --repo {sid}=GITDIR)")
                    continue
                full = lint.find_repo_path(repo, ref, parts[0])
                n = lint.git_file_lines(repo, ref, full) if full else None
                if n is None:
                    rep.error(where, "G1", f"{sid}: {parts[0]} not found (uniquely) at {ref}")
                elif parts[2] > n or parts[1] < 1 or parts[1] > parts[2]:
                    rep.error(where, "G1", f"{sid}: {full}:{parts[1]}-{parts[2]} out of range "
                                           f"({n} lines) at {ref}")
            elif local:
                fname = loc.split()[0].split("#")[0]
                f = skill / local / fname
                lines = anchor_lines(loc)
                if lines and f.is_file():
                    n = len(f.read_text(encoding="utf-8", errors="replace").splitlines())
                    if lines[1] > n or lines[0] < 1 or lines[0] > lines[1]:
                        rep.error(where, "L1", f"{sid}: {fname}#L{lines[0]}-L{lines[1]} out of range ({n} lines)")
                if sid.startswith("TOOLS-") and fname == "CodeSystem-ig-parameters.json" and "#" in loc:
                    code = loc.split()[0].split("#", 1)[1]
                    if f.is_file():
                        if f not in cs_cache:
                            cs_cache[f] = codesystem_codes(f)
                        if code not in cs_cache[f]:
                            rep.error(where, "T1", f"{sid}: code {code!r} not in {fname}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill-dir", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--cql-lint", default=str(DEFAULT_CQL_LINT))
    ap.add_argument("--repo", action="append", default=[], metavar="ID=GITDIR")
    args = ap.parse_args(argv)
    lint = load_cql_lint(Path(args.cql_lint))
    skill = Path(args.skill_dir)
    repos = dict(DEFAULT_REPOS)
    for r in args.repo:
        sid, p = parse_repo_arg(r)
        repos[sid] = p
    rep = lint.Report()
    sources = lint.parse_sources(skill / "resources" / "SOURCES.md", rep)
    files = []
    if (skill / "SKILL.md").exists():
        files.append((skill / "SKILL.md", False))
    files += [(f, True) for f in sorted((skill / "resources").glob("*.md")) if f.name not in lint.SKIP_FILES]
    for f, headers in files:
        lint.check_file(f, skill, sources, {}, set(), Path("."), rep, headers=headers)
        check_extra(f, skill, sources, repos, lint, rep)
    for w in rep.warnings:
        print("WARN ", w)
    for e in rep.errors:
        print("ERROR", e)
    print(f"{len(rep.errors)} errors, {len(rep.warnings)} warnings")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
