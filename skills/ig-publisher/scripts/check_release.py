"""Check whether the sources this skill is pinned to have newer releases, and what a re-pin would touch.

For each pinned source with a newer release (IG Publisher, its core library, the CQF and base
templates, the tools IG), every [src: …] citation of it is looked up at the new version:

  same     the cited lines are identical at the same line numbers
  moved    the identical text is at one other place (the citation only needs new line numbers)
  multi    the identical text is at several places (nearest shown; check by hand)
  CHANGED  the cited text is gone or edited: the claim needs re-reading
  missing  the cited file or CodeSystem code no longer exists

It also reports the core library and CQL translator versions the new publisher builds against.
Nothing in the skill is changed. Re-pinning stays a reviewed change: see SOURCES.md.

Usage: python3 scripts/check_release.py [--report FILE] [--cache DIR]
Exit status: 0 if every pin is current, 3 if a newer release exists, 1 on error.
Needs git and network access. Set GITHUB_TOKEN to avoid GitHub's anonymous rate limit.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import urllib.request
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
CACHE_DIR = Path(os.environ.get("IGPUB_SKILL_CACHE", Path.home() / ".cache" / "ig-publisher-skill"))

PUBLISHER_REPO = "HL7/fhir-ig-publisher"
CORE_REPO = "hapifhir/org.hl7.fhir.core"
PACKAGES = "https://packages.fhir.org"

# Source-ID prefix -> how it is released. Other IDs (probes, example IGs, sample IG, VSCQL) are
# pinned to commits or are records of a run, and have no release to follow.
PIN_RE = re.compile(r"^\|\s*(IGPUB|CORE|TPL-CQF|TPL-BASE|TOOLS)-(\d+\.\d+\.\d+)\s*\|", re.M)
PACKAGE_OF = {"TPL-CQF": "cqf.fhir.template", "TPL-BASE": "fhir.base.template", "TOOLS": "hl7.fhir.uv.tools"}
SRC_RE = re.compile(r"\[src:\s*([A-Za-z0-9.\-]+)\s+([^\]]+?)\s*\]")
LINE_LOC_RE = re.compile(r"^(.+?):(\d+)(?:-(\d+))?$")
ANCHOR_LOC_RE = re.compile(r"^(.+?)#L(\d+)(?:-L?(\d+))?")
MAX_ROWS = 150  # per source, so the report fits in an issue body (65,536 characters)


# ---------------------------------------------------------------------------------------------
# Pure helpers (tested offline)

def read_pins(sources_md: str) -> dict[str, str]:
    """Pinned version of each released source, from SOURCES.md's table: {'IGPUB': '3.0.4', …}."""
    return {m.group(1): m.group(2) for m in PIN_RE.finditer(sources_md)}


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


def pom_property(pom: str, name: str) -> str | None:
    m = re.search(rf"<{re.escape(name)}>\s*([^<\s]+)\s*</{re.escape(name)}>", pom)
    return m.group(1) if m else None


def codesystem_codes(cs: dict) -> set[str]:
    codes: set[str] = set()

    def walk(concepts):
        for c in concepts or []:
            codes.add(c.get("code"))
            walk(c.get("concept"))
    walk(cs.get("concept"))
    return codes


@dataclass
class SourceResult:
    sid: str
    pinned: str
    latest: str | None
    rows: list[tuple[str, Citation, str]] = field(default_factory=list)  # (status, citation, new locator)
    notes: list[str] = field(default_factory=list)
    error: str | None = None


def render_report(results: list[SourceResult]) -> str:
    lines = ["# ig-publisher: pinned sources versus latest releases", "",
             "| Source | Pinned | Latest | Status |", "| --- | --- | --- | --- |"]
    for r in results:
        status = ("error: " + r.error) if r.error else ("**newer release**" if is_newer(r.latest, r.pinned) else "current")
        lines.append(f"| {r.sid} | {r.pinned} | {r.latest or '?'} | {status} |")
    for r in results:
        if not is_newer(r.latest, r.pinned) or r.error:
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
    lines += ["", "To re-pin: update the pins in `scripts/fetch-sources.sh` and `resources/SOURCES.md`, re-run "
              "the fetch script, `gen_ig_parameters.py` and `lint_skill_igpub.py`, re-read every CHANGED "
              "citation, and re-run a probe build if CQL loading, QA or flags changed."]
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


def latest_package(pkg: str) -> str:
    return http_json(f"{PACKAGES}/{pkg}")["dist-tags"]["latest"]


class GitTags:
    """A blobless, shallow bare clone holding just the tags asked for; blobs are fetched on demand."""

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

    def fetch(self, tag: str) -> None:
        if self._git("rev-parse", "-q", "--verify", f"refs/tags/{tag}", check=False).returncode != 0:
            self._git("fetch", "-q", "--depth", "1", "--filter=blob:none", "origin",
                      f"refs/tags/{tag}:refs/tags/{tag}")

    def files(self, tag: str) -> list[str]:
        if tag not in self._files:
            out = self._git("ls-tree", "-r", "--name-only", tag).stdout.decode()
            self._files[tag] = out.splitlines()
        return self._files[tag]

    def text(self, tag: str, path: str) -> str | None:
        r = self._git("show", f"{tag}:{path}", check=False)
        return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None

    def lines(self, tag: str, path: str) -> list[str] | None:
        t = self.text(tag, path)
        return t.replace("\r\n", "\n").split("\n") if t is not None else None


def package_files(pkg: str, version: str) -> dict[str, str]:
    """Text files of a package tarball, keyed by their path in the tarball."""
    req = urllib.request.Request(f"{PACKAGES}/{pkg}/{version}", headers={"User-Agent": "cqf-skills-release-check"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = r.read()
    out = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        for m in tar.getmembers():
            if m.isfile() and re.search(r"\.(json|ini|md|xml|xslt|txt|html|liquid|yml|yaml|js|css|sh)$", m.name):
                out[m.name.lstrip("./")] = tar.extractfile(m).read().decode("utf-8", "replace")
    return out


def lines_of(text: str | None) -> list[str] | None:
    return text.replace("\r\n", "\n").split("\n") if text is not None else None


# ---------------------------------------------------------------------------------------------

def check(skill: Path, cache: Path) -> list[SourceResult]:
    pins = read_pins((skill / "resources" / "SOURCES.md").read_text(encoding="utf-8"))
    cites = citations(skill)
    by_id = lambda sid: [c for c in cites if c.sid == sid]  # noqa: E731
    results = []

    # IG Publisher, and with it the publisher's docs, its core library and its CQL translator.
    pub = SourceResult("IGPUB", pins["IGPUB"], None)
    core = SourceResult("CORE", pins["CORE"], None)
    results += [pub, core]
    try:
        pub.latest = latest_github_release(PUBLISHER_REPO)
        if is_newer(pub.latest, pub.pinned):
            g = GitTags(PUBLISHER_REPO, cache)
            g.fetch(pub.pinned)
            g.fetch(pub.latest)
            for sid in (f"IGPUB-{pub.pinned}", f"IGPUB-DOCS-{pub.pinned}"):
                pub.rows += compare(by_id(sid), g.files(pub.pinned), g.files(pub.latest),
                                    lambda p: g.lines(pub.pinned, p), lambda p: g.lines(pub.latest, p))
            for label, path, prop in (("core library", "pom.xml", "core_version"),
                                      ("CQL translator", "org.hl7.fhir.publisher.core/pom.xml", "info_cqframework_version")):
                old = pom_property(g.text(pub.pinned, path) or "", prop)
                new = pom_property(g.text(pub.latest, path) or "", prop)
                pub.notes.append(f"{pub.latest} builds against {label} {new}" + ("" if new == old else f" (was {old})"))
            core.latest = pom_property(g.text(pub.latest, "pom.xml") or "", "core_version")
        else:
            core.latest = core.pinned
    except Exception as e:  # noqa: BLE001 - reported, and the other sources are still checked
        pub.error = f"{type(e).__name__}: {e}"
    try:
        if is_newer(core.latest, core.pinned):
            g = GitTags(CORE_REPO, cache)
            g.fetch(core.pinned)
            g.fetch(core.latest)
            core.rows = compare(by_id(f"CORE-{core.pinned}"), g.files(core.pinned), g.files(core.latest),
                                lambda p: g.lines(core.pinned, p), lambda p: g.lines(core.latest, p))
    except Exception as e:  # noqa: BLE001
        core.error = f"{type(e).__name__}: {e}"

    # Packages: the two templates and the tools IG.
    for prefix, pkg in PACKAGE_OF.items():
        r = SourceResult(prefix, pins[prefix], None)
        results.append(r)
        try:
            r.latest = latest_package(pkg)
            if not is_newer(r.latest, r.pinned):
                continue
            old, new = package_files(pkg, r.pinned), package_files(pkg, r.latest)
            sid = f"{prefix}-{r.pinned}"
            if prefix == "TOOLS":
                r.rows = compare_tools(by_id(sid), old, new)
            else:
                r.rows = compare(by_id(sid), list(old), list(new),
                                 lambda p: lines_of(old.get(p)), lambda p: lines_of(new.get(p)))
        except Exception as e:  # noqa: BLE001
            r.error = f"{type(e).__name__}: {e}"
    return results


def compare_tools(cites: list[Citation], old: dict[str, str], new: dict[str, str]) -> list[tuple[str, Citation, str]]:
    """Tools IG citations are a file, or 'CodeSystem-ig-parameters.json#<code>': check the code still exists."""
    def find(files: dict[str, str], name: str) -> str | None:
        return next((t for p, t in files.items() if p.endswith("/" + name) or p == name), None)

    rows = []
    for c in cites:
        name, _, code = c.loc.partition("#")
        old_t, new_t = find(old, name), find(new, name)
        if new_t is None:
            rows.append(("missing", c, ""))
        elif code and name.startswith("CodeSystem-"):
            if code not in codesystem_codes(json.loads(new_t)):
                rows.append(("missing", c, ""))
            else:
                same = old_t is not None and _concept(json.loads(old_t), code) == _concept(json.loads(new_t), code)
                rows.append(("same" if same else "CHANGED", c, ""))
        else:
            rows.append(("same" if old_t == new_t else "CHANGED", c, ""))
    return rows


def _concept(cs: dict, code: str):
    stack = list(cs.get("concept") or [])
    while stack:
        c = stack.pop()
        if c.get("code") == code:
            return {k: v for k, v in c.items() if k != "concept"}
        stack += c.get("concept") or []
    return None


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
    return 3 if any(is_newer(r.latest, r.pinned) for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
