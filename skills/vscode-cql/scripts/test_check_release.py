"""Offline tests for check_release.py (no network or git), and pin consistency across the skill."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_release as C  # noqa: E402
import gen_reference as G  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
SOURCES = (SKILL / "resources" / "SOURCES.md").read_text(encoding="utf-8")


def test_read_pins():
    pins = C.read_pins(SOURCES)
    assert set(pins) == {"VSCQL", "CQLLS", "WIKI"}
    assert re.fullmatch(r"\d+\.\d+\.\d+", pins["VSCQL"]) and re.fullmatch(r"[0-9a-f]{40}", pins["WIKI"])


def test_pins_agree_across_the_skill():
    pins = C.read_pins(SOURCES)
    fetch = (SKILL / "scripts" / "fetch-sources.sh").read_text(encoding="utf-8")
    assert f'"VSCQL-{pins["VSCQL"]}|cqframework/vscode-cql|v{pins["VSCQL"]}|' in fetch
    assert f'"CQLLS-{pins["CQLLS"]}|cqframework/cql-language-server|v{pins["CQLLS"]}|' in fetch
    assert f'|cqframework/vscode-cql.wiki|{pins["WIKI"]}|' in fetch
    assert G.REF == f"v{pins['VSCQL']}" and G.SOURCE_ID == f"VSCQL-{pins['VSCQL']}"
    # The extension release pins the server version that SOURCES.md records.
    commands = (SKILL / "resources" / "commands.md").read_text(encoding="utf-8")
    assert f"cql-ls-server:{pins['CQLLS']}`" in commands


def test_is_moved():
    assert C.is_moved(C.SourceResult("VSCQL", "1.0.0", "1.0.2"))
    assert not C.is_moved(C.SourceResult("VSCQL", "1.0.0", "1.0.0"))
    assert C.is_moved(C.SourceResult("WIKI", "c9e1023", "abc1234"))
    assert not C.is_moved(C.SourceResult("WIKI", "c9e1023", "c9e1023"))
    assert not C.is_moved(C.SourceResult("WIKI", "c9e1023", None))


def test_ls_version_of():
    assert C.ls_version_of('{"javaDependencies": {"cql-language-server": {"version": "5.1.0"}}}') == "5.1.0"
    assert C.ls_version_of("{}") is None
    assert C.ls_version_of(None) is None


def test_find_block_and_compare():
    old = {"src/a/x.ts": ["1", "2", "3"]}
    new = {"src/a/x.ts": ["0", "1", "2", "3"]}
    cites = [C.Citation("r.md", 1, "VSCQL-1.0.0", "src/…/x.ts:2-3"),
             C.Citation("r.md", 2, "VSCQL-1.0.0", "src/…/gone.ts:1")]
    rows = C.compare(cites, list(old), list(new), old.get, new.get)
    assert [(s, nl) for s, _, nl in rows] == [("moved", "src/…/x.ts:3-4"), ("missing", "")]


def test_report_marks_moved_wiki():
    text = C.render_report([C.SourceResult("VSCQL", "1.0.0", "1.0.0"), C.SourceResult("WIKI", "c9e1023", "abc1234")])
    assert "| VSCQL | 1.0.0 | 1.0.0 | current |" in text
    assert "| WIKI | c9e1023 | abc1234 | **newer release** |" in text


def test_cited_files_table_covers_every_elided_citation():
    section = SOURCES.split("**Cited files.**", 1)[1].split("\n## ", 1)[0]
    table: dict[str, list[str]] = {}
    for kind, path in re.findall(r"^\| (VSCQL|CQLLS|WIKI) \| `([^`]+)` \|$", section, re.M):
        table.setdefault(kind, []).append(path)
    for c in C.citations(SKILL):
        partial = C.split_loc(c.loc)[0]
        if "…" in partial:
            kind = c.sid.split("-")[0]
            assert C.resolve(table.get(kind, []), partial), f"{c.file}:{c.line} {c.sid} {c.loc} not in Cited files"
