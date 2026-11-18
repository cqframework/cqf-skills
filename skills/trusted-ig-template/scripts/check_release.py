"""Check whether the trusted template rules, or the publisher code this skill cites, have changed upstream.

Every [src: …] citation of a git-pinned source is looked up upstream: the IG Publisher on its master
branch (the rules and the publisher's checks change there first), and org.hl7.fhir.core at its latest
GitHub release:

  same     the cited lines are identical at the same line numbers
  moved    the identical text is at one other place (the citation only needs new line numbers)
  multi    the identical text is at several places (nearest shown; check by hand)
  CHANGED  the cited text is gone or edited: the claim needs re-reading
  missing  the cited file no longer exists

The rules file is also compared as a whole, so a new rule is reported even though nothing cites it yet.
A source needs a re-pin when any row is CHANGED, missing or multi. New commits that touch none of the
cited code are reported but don't count. Nothing in the skill is changed; re-pinning stays a reviewed
change.

Usage: python3 scripts/check_release.py [--report FILE] [--cache DIR]
Exit status: 0 if every cited line is unchanged, 3 if a re-pin is needed, 1 on error.
Needs git and network access.
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
CACHE_DIR = Path(os.environ.get("TRUSTED_IG_TEMPLATE_SKILL_CACHE", Path.home() / ".cache" / "trusted-ig-template-skill"))

# Registry rows of git-pinned sources: | ID | … | owner/repo@sha | …
PIN_RE = re.compile(r"^\|\s*([A-Z][\w.\-]*)\s*\|.*?\|\s*([\w.\-]+/[\w.\-]+)@([0-9a-f]{40})\s*\|", re.M)
SRC_RE = re.compile(r"\[src:\s*([A-Za-z0-9.\-]+)\s+([^\]]+?)\s*\]")
LINE_LOC_RE = re.compile(r"^(.+?):(\d+)(?:-(\d+))?$")
# "release" compares with the latest GitHub release; anything else names a branch
BRANCHES = {"HL7/fhir-ig-publisher": "master", "hapifhir/org.hl7.fhir.core": "release"}
DEFAULT_BRANCH = "release"
MAX_ROWS = 150  # per source, so the report fits in an issue body (65,536 characters)
NEEDS_REPIN = ("CHANGED", "missing", "multi")


# ---------------------------------------------------------------------------------------------
# Pure helpers (tested offline)

@dataclass
class Pin:
    sid: str
    repo: str
    sha: str

    @property
    def branch(self) -> str:
        return BRANCHES.get(self.repo, DEFAULT_BRANCH)


def read_pins(sources_md: str) -> list[Pin]:
    """Git-pinned rows of SOURCES.md's registry."""
    return [Pin(m.group(1), m.group(2), m.group(3)) for m in PIN_RE.finditer(sources_md)]


@dataclass
class Citation:
    file: str
    line: int
    sid: str
    loc: str


def citations(skill: Path) -> list[Citation]:
    out = []
    for f in [skill / "SKILL.md"] + sorted((skill / "resources").glob("*.md")):
        if f.name == "SOURCES.md":  # the registry describes the citation format; it cites nothing
            continue
        for n, text in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for m in SRC_RE.finditer(text):
                out.append(Citation(f.relative_to(skill).as_posix(), n, m.group(1), m.group(2)))
    return out


def split_loc(loc: str) -> tuple[str, int | None, int | None]:
    """'src/…/B.java:10-12' -> (path, 10, 12); no lines -> (path, None, None)."""
    m = LINE_LOC_RE.match(loc)
    if m:
        return m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
    return loc.split()[0], None, None


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


def compare(cites: list[Citation], old_files, new_files, old_lines, new_lines) -> list[tuple[str, Citation, str]]:
    """Look up each citation at the new commit. *_files are file lists; *_lines(path) return lines."""
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


RULES = "trusted-template-rules.md"


def whole_file(sid: str, path: str, old: list[str] | None, new: list[str] | None) -> tuple[str, Citation, str]:
    """A row for a whole file: same, CHANGED (any edit) or missing."""
    c = Citation("(whole file)", 0, sid, path)
    if new is None:
        return "missing", c, ""
    return ("same" if old == new else "CHANGED"), c, ""


@dataclass
class SourceResult:
    pin: Pin
    head: str | None = None
    rows: list[tuple[str, Citation, str]] = field(default_factory=list)
    error: str | None = None

    @property
    def needs_repin(self) -> bool:
        return any(s in NEEDS_REPIN for s, _, _ in self.rows)


def render_report(results: list[SourceResult]) -> str:
    lines = ["# trusted-ig-template: the rules and cited code versus upstream", "",
             "| Source | Branch | Pinned | Head | Citations | Status |", "| --- | --- | --- | --- | --- | --- |"]
    for r in results:
        counts = Counter(s for s, _, _ in r.rows)
        summary = ", ".join(f"{counts[k]} {k}" for k in ("same", "moved", "multi", "CHANGED", "missing") if counts[k])
        if r.error:
            status = "error: " + r.error
        elif r.needs_repin:
            status = "**cited code changed**"
        elif r.head and r.head != r.pin.sha:
            status = "new commits; cited code unchanged"
        else:
            status = "current"
        head = r.head[:7] if r.head else "?"
        lines.append(f"| {r.pin.sid} | `{r.pin.repo}@{r.pin.branch}` | {r.pin.sha[:7]} | {head} | "
                     f"{summary or 'none'} | {status} |")
    for r in results:
        review = [(s, c, nl) for s, c, nl in r.rows if s in NEEDS_REPIN]
        if not review or r.error:
            continue
        lines += ["", f"## {r.pin.sid}: {r.pin.repo} {r.pin.sha[:7]} → {r.head[:7] if r.head else '?'}", "",
                  f"Compare: <https://github.com/{r.pin.repo}/compare/{r.pin.sha}...{r.head}>", "",
                  "| Status | Where | Citation | At the head |", "| --- | --- | --- | --- |"]
        for s, c, nl in review[:MAX_ROWS]:
            lines.append(f"| {s} | `{c.file}:{c.line}` | `{c.sid} {c.loc}` | {('`' + nl + '`') if nl else ''} |")
        if len(review) > MAX_ROWS:
            lines += ["", f"…and {len(review) - MAX_ROWS} more; run the script locally for the full list."]
    lines += ["", "To re-pin a source: change its commit in `scripts/fetch-sources.sh`, `resources/SOURCES.md` "
              "(the row, its ID and every citation of it) and `scripts/lint_skill_trusted_ig_template.py`, re-read every "
              "CHANGED citation, fix moved line numbers, and run `scripts/fetch-sources.sh` and "
              "`scripts/lint_skill_trusted_ig_template.py`; then re-read the rules file in full and re-run the probes."]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------------------------
# Network and git

def http_json(url: str) -> dict:
    headers = {"Accept": "application/json", "User-Agent": "cqf-skills-release-check"}
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as r:
        return json.load(r)



class GitRepo:
    """A blobless bare clone holding the commits asked for."""

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

    def head(self, branch: str) -> str:
        if branch == "release":
            return self.latest_release()
        ref = "HEAD" if branch == "HEAD" else f"refs/heads/{branch}"
        out = self._git("ls-remote", "origin", ref).stdout.decode().split()
        if not out:
            raise RuntimeError(f"branch {branch} not found")
        return out[0]

    def latest_release(self) -> str:
        """The commit of the repository's latest GitHub release (a peeled tag)."""
        repo = self._git("remote", "get-url", "origin").stdout.decode().strip()
        repo = repo.removeprefix("https://github.com/").removesuffix(".git")
        tag = http_json(f"https://api.github.com/repos/{repo}/releases/latest")["tag_name"]
        out = self._git("ls-remote", "origin", f"refs/tags/{tag}", f"refs/tags/{tag}^{{}}").stdout.decode()
        refs = {ref: sha for sha, ref in (line.split("	") for line in out.splitlines() if "	" in line)}
        sha = refs.get(f"refs/tags/{tag}^{{}}") or refs.get(f"refs/tags/{tag}")
        if not sha:
            raise RuntimeError(f"release tag {tag} not found")
        return sha

    def fetch(self, sha: str) -> None:
        if self._git("rev-parse", "-q", "--verify", f"{sha}^{{commit}}", check=False).returncode != 0:
            self._git("fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", sha)

    def files(self, sha: str) -> list[str]:
        if sha not in self._files:
            self._files[sha] = self._git("ls-tree", "-r", "--name-only", sha).stdout.decode().splitlines()
        return self._files[sha]

    def lines(self, sha: str, path: str) -> list[str] | None:
        r = self._git("show", f"{sha}:{path}", check=False)
        if r.returncode != 0:
            return None
        return r.stdout.decode("utf-8", "replace").replace("\r\n", "\n").split("\n")


def check(skill: Path, cache: Path) -> list[SourceResult]:
    pins = read_pins((skill / "resources" / "SOURCES.md").read_text(encoding="utf-8"))
    cites = citations(skill)
    results = []
    for pin in pins:
        r = SourceResult(pin)
        results.append(r)
        try:
            g = GitRepo(pin.repo, cache)
            r.head = g.head(pin.branch)
            mine = [c for c in cites if c.sid == pin.sid]
            if r.head == pin.sha:
                r.rows = [("same", c, "") for c in mine]
                continue
            g.fetch(pin.sha)
            g.fetch(r.head)
            r.rows = compare(mine, g.files(pin.sha), g.files(r.head),
                             lambda p: g.lines(pin.sha, p), lambda p: g.lines(r.head, p))
            if pin.repo == "HL7/fhir-ig-publisher":
                r.rows.append(whole_file(pin.sid, RULES, g.lines(pin.sha, RULES), g.lines(r.head, RULES)))
        except Exception as e:  # noqa: BLE001 - reported, and the other sources are still checked
            r.error = f"{type(e).__name__}: {e}"
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
    return 3 if any(r.needs_repin for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
