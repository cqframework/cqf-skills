"""Offline tests for check_release.py and the consistency of the skill's pins and citations."""
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
    assert [(p.sid, p.repo, p.branch) for p in pins] == [
        ("CR-4.13.0", "cqframework/clinical-reasoning", "release")]
    assert re.fullmatch(r"[0-9a-f]{40}", pins[0].sha)


def test_pins_agree_across_the_skill():
    fetch = (SKILL / "scripts" / "fetch-sources.sh").read_text(encoding="utf-8")
    lint = (SKILL / "scripts" / "lint_skill_questionnaire.py").read_text(encoding="utf-8")
    pom = (SKILL / "scripts" / "sdc" / "pom.xml").read_text(encoding="utf-8")
    for p in C.read_pins(SOURCES):
        assert f'"{p.sid}|{p.repo}|{p.sha}|' in fetch
        assert f'"{p.sid}":' in lint
    # the harness runs the pinned release
    assert "<artifactId>cqf-fhir-cr</artifactId><version>4.13.0</version>" in pom


def test_every_citation_names_a_registered_source():
    ids = set(re.findall(r"^\| ([A-Z][\w.\-]*) \|", SOURCES, re.M))
    for c in C.citations(SKILL):
        assert c.sid in ids, f"{c.file}:{c.line} cites unregistered {c.sid}"


def test_cited_files_table_covers_every_elided_citation():
    section = SOURCES.split("**Cited files.**", 1)[1]
    table = re.findall(r"^\| CR \| `([^`]+)` \|$", section, re.M)
    for c in C.citations(SKILL):
        partial = C.split_loc(c.loc)[0]
        if c.sid.startswith("CR-") and "…" in partial:
            assert C.resolve(table, partial), f"{c.file}:{c.line} {c.loc} not in Cited files"


def test_probe_sections_exist():
    results = (SKILL / "resources" / "probes" / "2026-11-14" / "RESULTS.md").read_text(encoding="utf-8")
    sections = set(re.findall(r"^## (\d+)\.", results, re.M))
    for c in C.citations(SKILL):
        if c.sid.startswith("PROBES-"):
            n = re.search(r"§(\d+)", c.loc).group(1)
            assert n in sections, f"{c.file}:{c.line} cites missing §{n}"


def test_compare_flags_a_moved_file():
    old = {"a/X.java": ["1", "2"]}
    new = {"a/X.kt": ["1", "2"]}
    rows = C.compare([C.Citation("r.md", 1, "CR-4.13.0", "a/X.java:1-2")], list(old), list(new), old.get, new.get)
    assert rows[0][0] == "missing"
