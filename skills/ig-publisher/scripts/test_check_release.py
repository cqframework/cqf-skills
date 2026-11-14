"""Offline tests for check_release.py (no network or git)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_release as C  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent


def test_read_pins_from_this_skill():
    pins = C.read_pins((SKILL / "resources" / "SOURCES.md").read_text(encoding="utf-8"))
    assert set(pins) == {"IGPUB", "CORE", "TPL-CQF", "TPL-BASE", "TOOLS"}
    # The docs row (IGPUB-DOCS-x) must not be read as the publisher pin.
    assert pins["IGPUB"] == pins["IGPUB"].strip() and pins["IGPUB"][0].isdigit()


def test_pins_match_fetch_script():
    pins = C.read_pins((SKILL / "resources" / "SOURCES.md").read_text(encoding="utf-8"))
    fetch = (SKILL / "scripts" / "fetch-sources.sh").read_text(encoding="utf-8")
    assert f'IGPUB_REF="{pins["IGPUB"]}"' in fetch
    assert f'|org.hl7.fhir.core|{pins["CORE"]}|' in fetch.replace("hapifhir/", "")
    assert f'|cqf.fhir.template|{pins["TPL-CQF"]}|' in fetch
    assert f'|fhir.base.template|{pins["TPL-BASE"]}|' in fetch
    assert f'|hl7.fhir.uv.tools|{pins["TOOLS"]}|' in fetch


def test_version_ordering():
    assert C.is_newer("3.0.10", "3.0.4")
    assert C.is_newer("1.0.0", "0.8.1")
    assert not C.is_newer("3.0.4", "3.0.4")
    assert not C.is_newer("1.0.0-ballot", "1.0.0")
    assert C.is_newer("1.0.0", "1.0.0-ballot")
    assert not C.is_newer(None, "1.0.0")


def test_split_loc_forms():
    assert C.split_loc("org.hl7.fhir.publisher.core/…/Publisher.java:1906-1920") == (
        "org.hl7.fhir.publisher.core/…/Publisher.java", 1906, 1920)
    assert C.split_loc("a/B.java:12") == ("a/B.java", 12, 12)
    assert C.split_loc("scripts/onLoad.xslt#L256-L261") == ("scripts/onLoad.xslt", 256, 261)
    assert C.split_loc("documentation.md#L7-L18") == ("documentation.md", 7, 18)
    assert C.split_loc("CodeSystem-ig-parameters.json#path-binary") == ("CodeSystem-ig-parameters.json", None, None)


def test_resolve_elided_paths():
    files = ["mod/src/main/java/x/Publisher.java", "mod/src/main/java/y/Other.java", "pom.xml"]
    assert C.resolve(files, "mod/…/Publisher.java") == "mod/src/main/java/x/Publisher.java"
    assert C.resolve(files, "pom.xml") == "pom.xml"
    assert C.resolve(files, "mod/…/Missing.java") is None
    assert C.resolve(files + ["mod/z/Publisher.java"], "mod/…/Publisher.java") is None  # ambiguous


def test_find_block_statuses():
    old = ["a", "b", "c", "d"]
    assert C.find_block(old, ["a", "b", "c", "d"], 2, 3) == ("same", 2, 3)
    assert C.find_block(old, ["x", "y", "a", "b", "  c", "d"], 2, 3) == ("moved", 4, 5)
    assert C.find_block(old, ["b", "c", "z", "b", "c"], 2, 3)[0] == "multi"
    assert C.find_block(old, ["a", "B", "c"], 2, 3) == ("CHANGED", 2, 3)
    assert C.find_block(old, None, 1, 1) == ("missing", 1, 1)
    assert C.find_block(None, ["a"], 1, 1) == ("CHANGED", 1, 1)


def test_compare_rows():
    cites = [C.Citation("r.md", 1, "IGPUB-1.0.0", "m/…/A.java:2-3"),
             C.Citation("r.md", 2, "IGPUB-1.0.0", "m/…/Gone.java:1"),
             C.Citation("r.md", 3, "IGPUB-1.0.0", "m/…/A.java")]
    old = {"m/x/A.java": ["1", "2", "3"], "m/x/Gone.java": ["g"]}
    new = {"m/x/A.java": ["0", "1", "2", "3"]}
    rows = C.compare(cites, list(old), list(new), old.get, new.get)
    assert [(s, nl) for s, _, nl in rows] == [("moved", "m/…/A.java:3-4"), ("missing", ""), ("same", "")]


def test_compare_tools_codes():
    cs_old = {"concept": [{"code": "path-binary", "definition": "old"}, {"code": "gone", "definition": "x"}]}
    cs_new = {"concept": [{"code": "path-binary", "definition": "new"}, {"code": "kept", "concept": [{"code": "nested"}]}]}
    old = {"package/CodeSystem-ig-parameters.json": json.dumps(cs_old)}
    new = {"package/CodeSystem-ig-parameters.json": json.dumps(cs_new)}
    cites = [C.Citation("r.md", 1, "TOOLS-1.3.0", "CodeSystem-ig-parameters.json#path-binary"),
             C.Citation("r.md", 2, "TOOLS-1.3.0", "CodeSystem-ig-parameters.json#gone"),
             C.Citation("r.md", 3, "TOOLS-1.3.0", "StructureDefinition-ig-parameter.json")]
    assert [s for s, _, _ in C.compare_tools(cites, old, new)] == ["CHANGED", "missing", "missing"]
    assert C.codesystem_codes(cs_new) == {"path-binary", "kept", "nested"}


def test_pom_property():
    pom = "<properties>\n  <core_version>7.0.6</core_version>\n  <info_cqframework_version> 4.9.0 </info_cqframework_version>"
    assert C.pom_property(pom, "core_version") == "7.0.6"
    assert C.pom_property(pom, "info_cqframework_version") == "4.9.0"
    assert C.pom_property(pom, "missing") is None


def test_citations_found_in_this_skill():
    cites = C.citations(SKILL)
    ids = {c.sid.rsplit("-", 1)[0] for c in cites}
    assert {"IGPUB", "CORE", "TPL-BASE", "TOOLS"} <= ids
    assert all(c.line > 0 for c in cites)


def test_render_report():
    cur = C.SourceResult("TOOLS", "1.3.0", "1.3.0")
    new = C.SourceResult("IGPUB", "3.0.4", "3.0.5", notes=["3.0.5 builds against CQL translator 4.9.0"])
    new.rows = [("same", C.Citation("a.md", 1, "IGPUB-3.0.4", "x:1"), ""),
                ("CHANGED", C.Citation("b.md", 7, "IGPUB-3.0.4", "y:2-3"), "")]
    err = C.SourceResult("CORE", "7.0.6", None, error="URLError: offline")
    text = C.render_report([new, cur, err])
    assert "| IGPUB | 3.0.4 | 3.0.5 | **newer release** |" in text
    assert "| TOOLS | 1.3.0 | 1.3.0 | current |" in text
    assert "error: URLError: offline" in text
    assert "1 same, 1 CHANGED" in text
    assert "| CHANGED | `b.md:7` | `IGPUB-3.0.4 y:2-3` |" in text


def test_cited_files_table_covers_every_git_citation():
    """SOURCES.md lists the full path of every elided IGPUB/CORE file, for building GitHub URLs."""
    import re
    text = (SKILL / "resources" / "SOURCES.md").read_text(encoding="utf-8")
    section = text.split("**Cited files.**", 1)[1].split("\n## ", 1)[0]
    table = {}
    for kind, path in re.findall(r"^\| (IGPUB|CORE) \| `([^`]+)` \|$", section, re.M):
        table.setdefault(kind, []).append(path)
    for c in C.citations(SKILL):
        kind = c.sid.rsplit("-", 1)[0]
        if kind not in ("IGPUB", "CORE"):
            continue
        partial = C.split_loc(c.loc)[0]
        assert C.resolve(table[kind], partial), f"{c.file}:{c.line} {c.sid} {c.loc} is not in the Cited files table"
