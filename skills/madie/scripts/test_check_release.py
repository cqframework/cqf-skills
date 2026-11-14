"""Offline tests for check_release.py (no network or git), and pin consistency across the skill."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_release as C  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
SOURCES = (SKILL / "resources" / "SOURCES.md").read_text(encoding="utf-8")


def test_read_pins():
    pins = C.read_pins(SOURCES)
    assert len(pins) == 8
    for p in pins:
        assert re.fullmatch(r"[0-9a-f]{40}", p.sha)
        assert p.sid.endswith("-" + p.sha[:7]), f"{p.sid}: the ID must end with the commit's short SHA"
    branches = {p.repo: p.branch for p in pins}
    assert branches["MeasureAuthoringTool/measure-service"] == "develop"
    assert branches["MeasureAuthoringTool/madie-models"] == "main"


def test_pins_agree_across_the_skill():
    fetch = (SKILL / "scripts" / "fetch-sources.sh").read_text(encoding="utf-8")
    lint = (SKILL / "scripts" / "lint_skill_madie.py").read_text(encoding="utf-8")
    for p in C.read_pins(SOURCES):
        assert f'"{p.sid}|{p.repo}|{p.sha}|' in fetch, f"{p.sid} not pinned in fetch-sources.sh"
        assert f'"{p.sid}":' in lint, f"{p.sid} not in lint_skill_madie.py's DEFAULT_REPOS"


def test_every_citation_names_a_registered_source():
    ids = set(re.findall(r"^\| ([A-Z0-9]+-[0-9a-f.]+) \|", SOURCES, re.M))
    for c in C.citations(SKILL):
        assert c.sid in ids, f"{c.file}:{c.line} cites unregistered {c.sid}"


def test_find_block_and_compare():
    old = {"src/a/x.ts": ["1", "2", "3"], "src/a/y.ts": ["a", "b"]}
    new = {"src/a/x.ts": ["0", "1", "2", "3"], "src/a/y.ts": ["a", "c"]}
    cites = [C.Citation("r.md", 1, "MSVC-251a73d", "src/…/x.ts:2-3"),
             C.Citation("r.md", 2, "MSVC-251a73d", "src/…/gone.ts:1"),
             C.Citation("r.md", 3, "MSVC-251a73d", "src/…/y.ts:2"),
             C.Citation("r.md", 4, "MSVC-251a73d", "src/…/y.ts:1")]
    rows = C.compare(cites, list(old), list(new), old.get, new.get)
    assert [(s, nl) for s, _, nl in rows] == [
        ("moved", "src/…/x.ts:3-4"), ("missing", ""), ("CHANGED", ""), ("same", "")]


def test_moved_alone_does_not_need_a_repin():
    pin = C.Pin("MSVC-251a73d", "MeasureAuthoringTool/measure-service", "251a73d" + "0" * 33)
    cite = C.Citation("r.md", 1, pin.sid, "src/…/x.ts:2")
    moved = C.SourceResult(pin, "f" * 40, [("moved", cite, "src/…/x.ts:3"), ("same", cite, "")])
    changed = C.SourceResult(pin, "f" * 40, [("CHANGED", cite, "")])
    assert not moved.needs_repin and changed.needs_repin
    text = C.render_report([moved])
    assert "new commits; cited code unchanged" in text and "## " not in text
    text = C.render_report([changed])
    assert "**cited code changed**" in text and "| CHANGED | `r.md:1` |" in text
    assert f"compare/{pin.sha}...{'f' * 40}" in text


def test_cited_files_table_covers_every_elided_citation():
    section = SOURCES.split("**Cited files.**", 1)[1]
    table: dict[str, list[str]] = {}
    for kind, path in re.findall(r"^\| ([A-Z0-9]+) \| `([^`]+)` \|$", section, re.M):
        table.setdefault(kind, []).append(path)
    for c in C.citations(SKILL):
        partial = C.split_loc(c.loc)[0]
        if "…" in partial:
            kind = c.sid.split("-")[0]
            assert C.resolve(table.get(kind, []), partial), f"{c.file}:{c.line} {c.sid} {c.loc} not in Cited files"
