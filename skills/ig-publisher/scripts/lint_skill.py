#!/usr/bin/env python3
"""Lint a skill's resource files for the source and version conventions.

Usage:
    lint_skill.py [--skill-dir DIR] [--cqfw-repo DIR]

Defaults: --skill-dir is the folder that contains this script's scripts/ folder. --cqfw-repo is
$CQFW_REPO, a local clone of cqframework/clinical_quality_language. Without it, C4 is skipped
with a warning.

Checks
  SOURCES.md
    S1  file exists and has a registry table
    S2  every row's Kind is one of the allowed kinds
    S3  every row's pinned locator is reproducible (no master/main/current/latest, not a bare URL)
    S4  the registry has a Status column, and every row's status is normative, trial-use,
        informative or n/a (columns are found by header name, so their order doesn't matter)
  Resource files (resources/*.md, except SOURCES.md and to-relocate.md)
    H1  has a "Baseline:" header line
    H2  has a "Sources:" header line whose IDs exist in SOURCES.md
    H3  every ID used in a [src: …] citation is listed in the file's Sources line
    C7  any other source whose Local copy is a resources/… folder (guides, for example): the
        locator's first token, without any #anchor, names a file under that folder
  SKILL.md is checked for citations (C1-C7) only, not for the header lines.
  Not checked: resources/spec/ (generated) and resources/probes/ (dated records of observed
  behaviour, which carry their own run date and versions).
  Citations [src: ID locator]
    C1  ID exists in SOURCES.md
    C2  CQL-<version>: "page-stem > section path" exists in that version's INDEX.md
    C3  CQL-<version>: if the section is in a CHANGES-*.md list, the paragraph (or table row, or
        the enclosing section's "Version differences" table) carries a version tag; a table row
        whose "First version" column holds a version number also counts
    C4  CQFW-<version>: the file exists at the tag v<version> and the line range is in bounds
    C5  PROBES-<date>: the file exists under resources/probes/<date>/
    C6  CQL-TESTS: the test file exists and contains the named test
    C8  no citation of the out-of-date test suites published with a spec version
        ([src: CQL-<version> tests/<file>.xml …]); cite CQL-TESTS instead. The spec's tests
        page itself ([src: CQL-<version> tests > …]) is ordinary spec text and is allowed.

Exit status 1 if any error was reported. Warnings never fail the run.
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path, PureWindowsPath

KINDS = {
    "spec", "test-suite", "guide", "package",
    "implementation-source", "observed-behavior", "convention",
}
STATUSES = {"normative", "trial-use", "informative", "n/a"}
UNPINNED_RE = re.compile(r"(@|#|/|\b)(master|main|current|latest)\b", re.I)
SRC_RE = re.compile(r"\[src:\s*([A-Za-z0-9.\-]+)\s+([^\]]+?)\s*\]")
VERSION_TAG_RE = re.compile(
    r"\((?:1\.4 only|1\.5\+|2\.0\+)(?:,\s*trial-use)?\)"
    r"|\*\*(?:1\.4|1\.5\.3|2\.0(?:\.0)?):\*\*"
    r"|\(same in [^)]+\)"
)
# A "Version differences" table: a bold label or heading followed by a table in the same section.
VERSION_DIFF_RE = re.compile(r"(?:^#+\s*|\*\*)Version differences(?:\*\*)?[^\n]*\n(?:\s*\n)*\|", re.M)
INDEX_ROW_RE =re.compile(r"^\| ([^|]+?) \| \[(.+)\]\([^)]+\) \| `[^`]+` \|$")
CHANGES_TABLE_RE = re.compile(r"^\| ([^|]+?)\.html \| \[(.+)\]\([^)]+\) \|")
CHANGES_LIST_RE = re.compile(r"^- ([^:]+?)\.html: \[?(.+?)\]?(?:\([^)]*\))?$")
SKIP_FILES = {"SOURCES.md", "to-relocate.md"}


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, where, code, msg):
        self.errors.append(f"{where}: {code} {msg}")

    def warn(self, where, code, msg):
        self.warnings.append(f"{where}: {code} {msg}")


def parse_sources(path: Path, rep: Report):
    if not path.exists():
        rep.error(path.name, "S1", "SOURCES.md not found")
        return {}
    rows = {}
    header = None
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.startswith("|"):
            header = None if not line.strip() else header
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if set("".join(cells)) <= set("-: "):
            continue
        row = dict(zip(header, cells))
        sid = row.get("id", "").strip("` ")
        if not sid:
            continue
        rows[sid] = row
        where = f"{path.name}:{n}"
        kind = row.get("kind", "").strip("` ")
        if kind not in KINDS:
            rep.error(where, "S2", f"{sid}: kind {kind!r} not in {sorted(KINDS)}")
        if "status" not in row:
            rep.error(where, "S4", f"{sid}: registry has no Status column")
        else:
            status = row["status"].strip("` ")
            if status not in STATUSES:
                rep.error(where, "S4", f"{sid}: status {status!r} not in {sorted(STATUSES)}")
        loc = row.get("pinned locator", "").strip("` ")
        if not loc:
            rep.error(where, "S3", f"{sid}: no pinned locator")
        elif UNPINNED_RE.search(loc):
            rep.error(where, "S3", f"{sid}: locator is not pinned: {loc!r}")
        elif re.match(r"^https?://", loc) and not re.search(r"[@#]|/v?\d+(\.\d+)+", loc):
            rep.error(where, "S3", f"{sid}: bare URL is not a pinned locator: {loc!r}")
    if not rows:
        rep.error(path.name, "S1", "no registry rows found")
    return rows


def load_index(spec_dir: Path, version: str):
    idx = spec_dir / version / "INDEX.md"
    out = set()
    if idx.exists():
        for line in idx.read_text(encoding="utf-8").splitlines():
            m = INDEX_ROW_RE.match(line)
            if m:
                out.add((m.group(1).strip(), norm_path(m.group(2))))
    return out


def load_changed(spec_dir: Path):
    changed = set()
    for f in spec_dir.glob("CHANGES-*.md"):
        for line in f.read_text(encoding="utf-8").splitlines():
            m = CHANGES_TABLE_RE.match(line) or CHANGES_LIST_RE.match(line)
            if m:
                changed.add((m.group(1).strip(), norm_path(m.group(2))))
    return changed


def norm_path(p: str) -> str:
    return re.sub(r"\s*>\s*", " > ", re.sub(r"\s+", " ", p)).strip()


def split_cql_locator(loc: str):
    """'09-b-cqlreference > Type Operators > Is' -> ('09-b-cqlreference', 'Type Operators > Is')."""
    parts = [p.strip() for p in loc.split(">")]
    if len(parts) < 2:
        return None, None
    return parts[0], " > ".join(parts[1:])


CODE_SPAN_RE = re.compile(r"`[^`]*`")


def blank_code_spans(s: str) -> str:
    """Replace each inline code span, backticks included, with spaces, keeping newlines and the
    text's length, so a `[src: …]` shown as an example is not read as a citation."""
    return CODE_SPAN_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), s)


def blocks(text: str):
    """Yield (start_line, end_line, block_text, enclosing_section_text) for each paragraph.
    Table rows are their own blocks. Inline code spans in block_text are blanked."""
    lines = text.splitlines()
    sections = []  # (start, end) of each heading section
    starts = [i for i, l in enumerate(lines) if re.match(r"^#{1,6}\s", l)] + [len(lines)]
    if not starts or starts[0] != 0:
        starts = [0] + starts
    for a, b in zip(starts, starts[1:]):
        sections.append((a, b))

    def section_of(i):
        for a, b in sections:
            if a <= i < b:
                return "\n".join(lines[a:b])
        return ""

    i = 0
    in_code = False
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            in_code = not in_code
            i += 1
            continue
        if in_code or not line.strip():
            i += 1
            continue
        if line.lstrip().startswith("|"):
            # A table row is its own block; prefix the table's header row so a
            # "First version" column can count as the row's version tag.
            h = i
            while h > 0 and lines[h - 1].lstrip().startswith("|"):
                h -= 1
            header = lines[h] if h != i else ""
            yield (i + 1, i + 1, blank_code_spans((header + "\n" + line) if header else line),
                   section_of(i))
            i += 1
            continue
        j = i
        while j < len(lines) and lines[j].strip() and not lines[j].lstrip().startswith("|") \
                and not lines[j].strip().startswith("```"):
            j += 1
        yield i + 1, j, blank_code_spans("\n".join(lines[i:j])), section_of(i)
        i = j


def local_copy(row):
    """The registry row's Local copy as a skill-relative folder, or None if it has none."""
    m = re.search(r"`?(resources/[^`\s]+?)/?`?(?:\s|$)", row.get("local copy", ""))
    return m.group(1) if m else None


def first_version_cell(block: str) -> bool:
    """True if block is a table row under a header with a 'First version' column, and that
    row's cell holds a version number."""
    lines = block.splitlines()
    if len(lines) != 2 or not lines[0].lstrip().startswith("|"):
        return False
    head = [c.strip().lower() for c in lines[0].strip().strip("|").split("|")]
    row = [c.strip() for c in lines[1].strip().strip("|").split("|")]
    if "first version" not in head:
        return False
    k = head.index("first version")
    return k < len(row) and re.fullmatch(r"\d+(\.\d+)*", row[k]) is not None


def git_file_lines(repo: Path, tag: str, path: str):
    try:
        out = subprocess.run(["git", "-C", str(repo), "show", f"{tag}:{path}"],
                             capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return out.count("\n") + (0 if out.endswith("\n") else 1)


def find_repo_path(repo: Path, tag: str, partial: str):
    """Accept full paths or paths with '…'/'...' elisions; return a unique full path or None."""
    if "…" not in partial and "..." not in partial:
        return partial
    try:
        files = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "--name-only", tag],
                               capture_output=True, text=True, check=True).stdout.splitlines()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    pieces = [p for p in re.split(r"…|\.\.\.", partial) if p]
    hits = [f for f in files if all(p.strip("/") in f for p in pieces) and f.endswith(pieces[-1].strip("/"))]
    return hits[0] if len(hits) == 1 else None


def check_file(path: Path, skill: Path, sources, indexes, changed, cqfw_repo: Path, rep: Report,
               headers=True):
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(skill) if path.is_relative_to(skill) else path
    head = "\n".join(text.splitlines()[:15])
    if headers and not re.search(r"^Baseline:", head, re.M):
        rep.error(str(rel), "H1", "no 'Baseline:' header line in the first 15 lines")
    m = re.search(r"^Sources:\s*(.+)$", head, re.M) if headers else None
    listed = set(sources) if not headers else set()
    if headers and not m:
        rep.error(str(rel), "H2", "no 'Sources:' header line in the first 15 lines")
    elif m:
        listed = {s.strip(" `.") for s in m.group(1).split(",") if s.strip()}
        for sid in sorted(listed - set(sources)):
            rep.error(str(rel), "H2", f"Sources lists unknown ID {sid}")

    used = set()
    for start, end, block, section in blocks(text):
        for cm in SRC_RE.finditer(block):
            sid, loc = cm.group(1), cm.group(2)
            used.add(sid)
            where = f"{rel}:{start}"
            if sid not in sources:
                rep.error(where, "C1", f"unknown source ID {sid}")
                continue
            if sid.startswith("CQL-") and sid != "CQL-TESTS" and loc.startswith("tests/"):
                # The test suites published with the spec are out of date; only cql-tests counts.
                rep.error(where, "C8", f"{sid} {loc}: the test suites published with the spec are "
                                       "out of date; cite CQL-TESTS (cqframework/cql-tests)")
            elif sid.startswith("CQL-") and sid != "CQL-TESTS":
                version = sid[4:]
                page, sec = split_cql_locator(loc)
                if not page:
                    rep.error(where, "C2", f"{sid} locator needs 'page-stem > section path': {loc!r}")
                    continue
                if (page, norm_path(sec)) not in indexes.get(version, set()):
                    rep.error(where, "C2", f"{sid}: section not in {version}/INDEX.md: {page} > {sec}")
                    continue
                if (page, norm_path(sec)) in changed:
                    ok = (VERSION_TAG_RE.search(block) or VERSION_DIFF_RE.search(section)
                          or first_version_cell(block))
                    if not ok:
                        rep.error(where, "C3",
                                  f"{page} > {sec} changed between versions; tag the paragraph "
                                  f"((1.5+), **1.4:** …, (same in …)) or add a Version differences table")
            elif sid.startswith("CQFW-"):
                if cqfw_repo is None:
                    rep.warn(where, "C4", f"{sid} not checked: pass --cqfw-repo or set CQFW_REPO")
                    continue
                tag = "v" + sid[5:]
                lm = re.match(r"^(.+?):(\d+)(?:-(\d+))?$", loc.strip("` "))
                if not lm:
                    rep.error(where, "C4", f"{sid} locator needs 'path:line[-line]': {loc!r}")
                    continue
                full = find_repo_path(cqfw_repo, tag, lm.group(1))
                n = git_file_lines(cqfw_repo, tag, full) if full else None
                if n is None:
                    rep.error(where, "C4", f"{lm.group(1)} not found (uniquely) at {tag}")
                    continue
                hi = int(lm.group(3) or lm.group(2))
                if hi > n:
                    rep.error(where, "C4", f"{full}:{hi} is past the end ({n} lines) at {tag}")
            elif sid.startswith("PROBES-"):
                date = sid[7:]
                fname = loc.split()[0]
                if not (skill / "resources" / "probes" / date / fname).exists():
                    rep.error(where, "C5", f"resources/probes/{date}/{fname} not found")
            elif sid == "CQL-TESTS":
                parts = loc.split()
                tf = skill / "resources" / "spec" / "cql-tests" / parts[0]
                if not tf.exists():
                    rep.error(where, "C6", f"cql-tests/{parts[0]} not found")
                elif len(parts) > 1 and f'name="{parts[1]}"' not in tf.read_text(encoding="utf-8"):
                    rep.error(where, "C6", f"test {parts[1]} not in {parts[0]}")
            else:
                local = local_copy(sources[sid])
                if local is not None:
                    fname = loc.split()[0].split("#")[0]
                    if not (skill / local / fname).exists():
                        rep.error(where, "C7", f"{sid}: {fname} not found under {local}")
    if not headers:
        return
    for sid in sorted(used - listed):
        rep.error(str(rel), "H3", f"cites {sid} but the Sources line does not list it")
    for sid in sorted(listed - used):
        rep.warn(str(rel), "H3", f"Sources lists {sid} but no [src: {sid} …] citation uses it")


def resolve_include(inc: str, skill: Path) -> Path:
    """Resolve an --include argument: absolute paths as given, others relative to the skill dir.

    | Input              | Treated as |
    | ------------------ | ---------- |
    | /path/to/file.md   | absolute   |
    | C:\\path\\file.md    | absolute   |
    | C:/path/file.md    | absolute   |
    | evals/file.md      | skill/evals/file.md |
    """
    if Path(inc).is_absolute() or PureWindowsPath(inc).is_absolute():
        return Path(inc)
    return skill / inc


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill-dir", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--cqfw-repo", default=os.environ.get("CQFW_REPO"))
    ap.add_argument("--include", action="append", default=[], metavar="FILE",
                    help="also lint FILE (absolute, or relative to --skill-dir) with all rules")
    args = ap.parse_args(argv)
    skill = Path(args.skill_dir)
    cqfw_repo = Path(args.cqfw_repo) if args.cqfw_repo else None
    spec = skill / "resources" / "spec"
    rep = Report()
    sources = parse_sources(skill / "resources" / "SOURCES.md", rep)
    indexes = {v: load_index(spec, v) for v in ("1.4", "1.5.3", "2.0.0")}
    changed = load_changed(spec)
    if (skill / "SKILL.md").exists():
        check_file(skill / "SKILL.md", skill, sources, indexes, changed, cqfw_repo, rep,
                   headers=False)
    for f in sorted((skill / "resources").glob("*.md")):
        if f.name in SKIP_FILES:
            continue
        check_file(f, skill, sources, indexes, changed, cqfw_repo, rep)
    for inc in args.include:
        f = resolve_include(inc, skill)
        if not f.is_file():
            rep.error(inc, "I1", "--include file not found")
            continue
        check_file(f, skill, sources, indexes, changed, cqfw_repo, rep)
    for w in rep.warnings:
        print("WARN ", w)
    for e in rep.errors:
        print("ERROR", e)
    print(f"{len(rep.errors)} errors, {len(rep.warnings)} warnings")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
