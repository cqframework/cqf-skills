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
        ("PUB-4e7325f", "HL7/fhir-ig-publisher", "master"),
        ("CORE-7.0.6", "hapifhir/org.hl7.fhir.core", "release")]
    assert all(re.fullmatch(r"[0-9a-f]{40}", p.sha) for p in pins)
    assert pins[0].sha.startswith("4e7325f")


def test_pins_agree_across_the_skill():
    fetch = (SKILL / "scripts" / "fetch-sources.sh").read_text(encoding="utf-8")
    lint = (SKILL / "scripts" / "lint_skill_trusted_ig_template.py").read_text(encoding="utf-8")
    for p in C.read_pins(SOURCES):
        assert f'"{p.sid}|{p.repo}|{p.sha}|' in fetch
        assert f'"{p.sid}":' in lint


def test_every_citation_names_a_registered_source():
    ids = set(re.findall(r"^\| ([A-Z][\w.\-]*) \|", SOURCES, re.M))
    for c in C.citations(SKILL):
        assert c.sid in ids, f"{c.file}:{c.line} cites unregistered {c.sid}"


def test_cited_files_table_covers_every_elided_citation():
    section = SOURCES.split("**Cited files.**", 1)[1]
    table = {prefix: re.findall(rf"^\| {prefix} \| `([^`]+)` \|$", section, re.M) for prefix in ("PUB", "CORE")}
    for c in C.citations(SKILL):
        partial = C.split_loc(c.loc)[0]
        prefix = c.sid.split("-")[0]
        if prefix in table:
            assert C.resolve(table[prefix], partial), f"{c.file}:{c.line} {c.loc} not in Cited files"


def test_probe_sections_exist():
    results = (SKILL / "resources" / "probes" / "2026-11-17" / "RESULTS.md").read_text(encoding="utf-8")
    sections = set(re.findall(r"^## (\d+)\.", results, re.M))
    for c in C.citations(SKILL):
        if c.sid.startswith("PROBES-"):
            n = re.search(r"§(\d+)", c.loc).group(1)
            assert n in sections, f"{c.file}:{c.line} cites missing §{n}"


def test_whole_rules_file():
    assert C.whole_file("PUB-x", C.RULES, ["a"], ["a"])[0] == "same"
    assert C.whole_file("PUB-x", C.RULES, ["a"], ["a", "13. A new rule"])[0] == "CHANGED"
    assert C.whole_file("PUB-x", C.RULES, ["a"], None)[0] == "missing"


def test_compare_flags_a_moved_file():
    old = {"a/X.java": ["1", "2"]}
    new = {"a/X.kt": ["1", "2"]}
    rows = C.compare([C.Citation("r.md", 1, "PUB-4e7325f", "a/X.java:1-2")], list(old), list(new), old.get, new.get)
    assert rows[0][0] == "missing"
