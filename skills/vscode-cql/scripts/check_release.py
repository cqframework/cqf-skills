"""Check whether the sources this skill is pinned to have moved on, and what a re-pin would touch.

Sources followed: the vscode-cql extension (GitHub releases), the cql-language-server version each
extension release downloads (its package.json `javaDependencies`), and the vscode-cql wiki (its
latest commit). For each one that has moved, every [src: …] citation of it is looked up at the new
version:

  same     the cited lines are identical at the same line numbers
  moved    the identical text is at one other place (the citation only needs new line numbers)
  multi    the identical text is at several places (nearest shown; check by hand)
  CHANGED  the cited text is gone or edited: the claim needs re-reading
  missing  the cited file no longer exists

Nothing in the skill is changed. Re-pinning stays a reviewed change: see SOURCES.md.

Usage: python3 scripts/check_release.py [--report FILE] [--cache DIR]
Exit status: 0 if every pin is current, 3 if something newer exists, 1 on error.
Needs git and network access. Set GITHUB_TOKEN to avoid GitHub's anonymous rate limit.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
CACHE_DIR = Path(os.environ.get("VSCQL_SKILL_CACHE", Path.home() / ".cache" / "vscode-cql-skill"))

EXT_REPO = "cqframework/vscode-cql"
LS_REPO = "cqframework/cql-language-server"
WIKI_REPO = "cqframework/vscode-cql.wiki"

PIN_RE = re.compile(r"^\|\s*(VSCQL|CQLLS)-(\d+\.\d+\.\d+)\s*\|", re.M)
WIKI_PIN_RE = re.compile(r"^\|\s*WIKI-[0-9a-f]+\s*\|.*?vscode-cql\.wiki@([0-9a-f]{40})", re.M)
SRC_RE = re.compile(r"\[src:\s*([A-Za-z0-9.\-]+)\s+([^\]]+?)\s*\]")
LINE_LOC_RE = re.compile(r"^(.+?):(\d+)(?:-(\d+))?$")
ANCHOR_LOC_RE = re.compile(r"^(.+?)#L(\d+)(?:-L?(\d+))?")
MAX_ROWS = 150  # per source, so the report fits in an issue body (65,536 characters)


# ---------------------------------------------------------------------------------------------
# Pure helpers (tested offline)

def read_pins(sources_md: str) -> dict[str, str]:
    """Pinned versions from SOURCES.md's table: {'VSCQL': '1.0.0', 'CQLLS': '5.0.0', 'WIKI': '<sha>'}."""
    pins = {m.group(1): m.group(2) for m in PIN_RE.finditer(sources_md)}
    m = WIKI_PIN_RE.search(sources_md)
    if m:
        pins["WIKI"] = m.group(1)
    return pins


def version_key(v: str) -> tuple:
    """Order release versions; a pre-release (1.0.0-ballot) sorts before its release."""
    main, _, pre = v.partition("-")
    nums = tuple(int(x) if x.isdigit() else 0 for x in main.split("."))
    return nums + ((0, pre) if pre else (1, ""))


def is_newer(latest: str | None, pinned: str) -> bool:
    return bool(latest) and version_key(latest) > version_key(pinned)


@dataclass
class Citation:
    file: str
    line: int
    sid: str
    loc: str


def citations(skill: Path) -> list[Citation]:
    out = []
    for f in [skill / "SKILL.md"] + sorted((skill / "resources").glob("*.md")):
        for n, text in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for m in SRC_RE.finditer(text):
                out.append(Citation(f.relative_to(skill).as_posix(), n, m.group(1), m.group(2)))
    return out


def split_loc(loc: str) -> tuple[str, int | None, int | None]:
    """'a/…/B.java:10-12' or 'scripts/x.xslt#L5-L9' -> (path, first, last); no lines -> None."""
    m = LINE_LOC_RE.match(loc)
    if m:
        return m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
    m = ANCHOR_LOC_RE.match(loc)
    if m:
        return m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
    return loc.split("#")[0].split()[0], None, None


def resolve(files: list[str], partial: str) -> str | None:
    """Resolve a path that may elide its middle with '…' to exactly one file."""
    if "…" not in partial:
        return partial if partial in files else None
    head, tail = partial.split("…", 1)
    tail = tail.lstrip("/")
    hits = [f for f in files if f.startswith(head) and f.endswith("/" + tail)]
    return hits[0] if len(hits) == 1 else None


def find_block(old: list[str] | None, new: list[str] | None, a: int, b: int) -> tuple[str, int, int]:
    """Where lines a..b (1-based) of old are in new, comparing with surrounding whitespace ignored."""
    if new is None:
        return "missing", a, b
    if old is None or b > len(old):
        return "CHANGED", a, b
    block = [line.strip() for line in old[a - 1:b]]
    stripped = [line.strip() for line in new]
    n = len(block)
    hits = [i + 1 for i in range(len(new) - n + 1) if stripped[i:i + n] == block]
    if not hits:
        return "CHANGED", a, b
    best = min(hits, key=lambda h: abs(h - a))
    if best == a:
        return "same", a, b
    return ("moved" if len(hits) == 1 else "multi"), best, best + n - 1


@dataclass
class SourceResult:
    sid: str
    pinned: str
    latest: str | None
    rows: list[tuple[str, Citation, str]] = field(default_factory=list)  # (status, citation, new locator)
    notes: list[str] = field(default_factory=list)
    error: str | None = None


def render_report(results: list[SourceResult]) -> str:
    lines = ["# vscode-cql: pinned sources versus latest releases", "",
             "| Source | Pinned | Latest | Status |", "| --- | --- | --- | --- |"]
    for r in results:
        status = ("error: " + r.error) if r.error else ("**newer release**" if is_moved(r) else "current")
        lines.append(f"| {r.sid} | {r.pinned} | {r.latest or '?'} | {status} |")
    for r in results:
        if not is_moved(r) or r.error:
            continue
        counts = Counter(s for s, _, _ in r.rows)
        lines += ["", f"## {r.sid} {r.pinned} → {r.latest}", ""]
        lines += [f"- {n}" for n in r.notes]
        summary = ", ".join(f"{counts[k]} {k}" for k in ("same", "moved", "multi", "CHANGED", "missing") if counts[k])
        lines.append(f"- Citations: {summary or 'none'}")
        review = [(s, c, nl) for s, c, nl in r.rows if s in ("CHANGED", "missing", "multi")]
        if review:
            lines += ["", "Citations to re-read at the new version:", "",
                      "| Status | Where | Citation | At the new version |", "| --- | --- | --- | --- |"]
            for s, c, nl in review[:MAX_ROWS]:
                lines.append(f"| {s} | `{c.file}:{c.line}` | `{c.sid} {c.loc}` | {('`' + nl + '`') if nl else ''} |")
            if len(review) > MAX_ROWS:
                lines += ["", f"…and {len(review) - MAX_ROWS} more; run the script locally for the full list."]
    lines += ["", "To re-pin: update the pins in `scripts/fetch-sources.sh`, `resources/SOURCES.md` and "
              "`scripts/gen_reference.py`, re-run the fetch script, `gen_reference.py` and `lint_skill_vscql.py`, "
              "and re-read every CHANGED citation."]
    return "\n".join(lines) + "\n"


def compare(cites: list[Citation], old_files, new_files, old_lines, new_lines) -> list[tuple[str, Citation, str]]:
    """Look up each citation at the new version. *_files are file lists; *_lines(path) return lines."""
    rows = []
    for c in cites:
        partial, a, b = split_loc(c.loc)
        op, np_ = resolve(old_files, partial), resolve(new_files, partial)
        if np_ is None:
            rows.append(("missing", c, ""))
            continue
        if a is None:
            rows.append(("same", c, ""))
            continue
        status, na, nb = find_block(old_lines(op) if op else None, new_lines(np_), a, b)
        rng = f"{na}" + (f"-{nb}" if nb != na else "")
        rows.append((status, c, "" if status in ("same", "CHANGED") else f"{partial}:{rng}"))
    return rows


def is_moved(r: "SourceResult") -> bool:
    """Has the source moved past its pin? Releases compare by version; the wiki by commit."""
    if r.sid == "WIKI":
        return bool(r.latest) and r.latest != r.pinned
    return is_newer(r.latest, r.pinned)


# ---------------------------------------------------------------------------------------------
# Network and git

def http_json(url: str) -> dict:
    headers = {"Accept": "application/json", "User-Agent": "cqf-skills-release-check"}
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as r:
        return json.load(r)


def latest_github_release(repo: str) -> str:
    return http_json(f"https://api.github.com/repos/{repo}/releases/latest")["tag_name"]


class GitRefs:
    """A blobless bare clone holding just the refs asked for (tags or commit SHAs)."""

    def __init__(self, repo: str, cache: Path):
        self.dir = cache / (repo.split("/")[1] + ".git")
        if not self.dir.is_dir():
            self.dir.parent.mkdir(parents=True, exist_ok=True)
            self._git("init", "-q", "--bare", str(self.dir), here=False)
            self._git("remote", "add", "origin", f"https://github.com/{repo}.git")
        self._files: dict[str, list[str]] = {}

    def _git(self, *args, here=True, check=True) -> subprocess.CompletedProcess:
        cmd = ["git"] + (["-C", str(self.dir)] if here else []) + list(args)
        return subprocess.run(cmd, capture_output=True, check=check)

    def head(self) -> str:
        return self._git("ls-remote", "origin", "HEAD").stdout.decode().split()[0]

    def fetch(self, ref: str) -> None:
        if self._git("rev-parse", "-q", "--verify", f"{ref}^{{commit}}", check=False).returncode == 0:
            return
        if re.fullmatch(r"[0-9a-f]{40}", ref):
            self._git("fetch", "-q", "--filter=blob:none", "origin", ref)
        else:
            self._git("fetch", "-q", "--depth", "1", "--filter=blob:none", "origin",
                      f"refs/tags/{ref}:refs/tags/{ref}")

    def files(self, ref: str) -> list[str]:
        if ref not in self._files:
            self._files[ref] = self._git("ls-tree", "-r", "--name-only", ref).stdout.decode().splitlines()
        return self._files[ref]

    def text(self, ref: str, path: str) -> str | None:
        r = self._git("show", f"{ref}:{path}", check=False)
        return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None

    def lines(self, ref: str, path: str) -> list[str] | None:
        t = self.text(ref, path)
        return t.replace("\r\n", "\n").split("\n") if t is not None else None


def compare_refs(g: GitRefs, cites: list[Citation], old: str, new: str) -> list[tuple[str, Citation, str]]:
    g.fetch(old)
    g.fetch(new)
    return compare(cites, g.files(old), g.files(new), lambda p: g.lines(old, p), lambda p: g.lines(new, p))


def ls_version_of(package_json: str | None) -> str | None:
    """The cql-language-server version an extension release downloads."""
    if not package_json:
        return None
    return json.loads(package_json).get("javaDependencies", {}).get("cql-language-server", {}).get("version")


# ---------------------------------------------------------------------------------------------

def check(skill: Path, cache: Path) -> list[SourceResult]:
    pins = read_pins((skill / "resources" / "SOURCES.md").read_text(encoding="utf-8"))
    cites = citations(skill)
    by_id = lambda sid: [c for c in cites if c.sid == sid]  # noqa: E731
    ext = SourceResult("VSCQL", pins["VSCQL"], None)
    ls = SourceResult("CQLLS", pins["CQLLS"], None)
    wiki = SourceResult("WIKI", pins["WIKI"][:7], None)
    results = [ext, ls, wiki]

    try:
        ext.latest = latest_github_release(EXT_REPO).lstrip("v")
        if is_newer(ext.latest, ext.pinned):
            g = GitRefs(EXT_REPO, cache)
            ext.rows = compare_refs(g, by_id(f"VSCQL-{ext.pinned}"), f"v{ext.pinned}", f"v{ext.latest}")
            shipped = ls_version_of(g.text(f"v{ext.latest}", "package.json"))
            ext.notes.append(f"{ext.latest} downloads cql-language-server {shipped}")
            ls.latest = shipped
        else:
            ls.latest = ls.pinned
    except Exception as e:  # noqa: BLE001 - reported, and the other sources are still checked
        ext.error = f"{type(e).__name__}: {e}"
    try:
        if is_newer(ls.latest, ls.pinned):
            ls.rows = compare_refs(GitRefs(LS_REPO, cache), by_id(f"CQLLS-{ls.pinned}"),
                                   f"v{ls.pinned}", f"v{ls.latest}")
        newest = latest_github_release(LS_REPO).lstrip("v")
        if is_newer(newest, ls.latest or ls.pinned):
            ls.notes.append(f"cql-language-server {newest} is released, but no extension release downloads it yet")
    except Exception as e:  # noqa: BLE001
        ls.error = f"{type(e).__name__}: {e}"
    try:
        g = GitRefs(WIKI_REPO, cache)
        head = g.head()
        wiki.latest = head[:7]
        if head != pins["WIKI"]:
            wiki.rows = compare_refs(g, by_id(f"WIKI-{pins['WIKI'][:7]}"), pins["WIKI"], head)
    except Exception as e:  # noqa: BLE001
        wiki.error = f"{type(e).__name__}: {e}"
    return results


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--report", type=Path, help="also write the Markdown report to this file")
    ap.add_argument("--cache", type=Path, default=CACHE_DIR, help=f"git cache folder (default {CACHE_DIR})")
    ap.add_argument("--skill", type=Path, default=SKILL, help="skill folder to check (default: this one)")
    args = ap.parse_args(argv)
    results = check(args.skill, args.cache)
    report = render_report(results)
    print(report)
    if args.report:
        args.report.write_text(report, encoding="utf-8")
    if any(r.error for r in results):
        return 1
    return 3 if any(is_moved(r) for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
