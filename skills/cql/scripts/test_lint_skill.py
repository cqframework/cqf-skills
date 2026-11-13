"""Tests for lint_skill.py. Run: python3 -m pytest -q test_lint_skill.py"""

import subprocess
import textwrap
from pathlib import Path

import pytest

import lint_skill

SOURCES = textwrap.dedent("""\
    # Sources

    | ID | Kind | Status | Version | Pinned locator | Published URL | Local copy | Retrieved |
    | --- | --- | --- | --- | --- | --- | --- | --- |
    | CQL-1.4 | spec | trial-use | 1.4 | HL7/cql@v1.4-release | https://cql.hl7.org/STU4/ | resources/spec/1.4/ | 2026-10-22 |
    | CQL-1.5.3 | spec | normative | 1.5.3 | HL7/cql@v1.5.3 | https://cql.hl7.org/N1A/ | resources/spec/1.5.3/ | 2026-10-22 |
    | CQL-2.0.0 | spec | trial-use | 2.0.0 | HL7/cql@2e191f8f | https://cql.hl7.org/ | resources/spec/2.0.0/ | 2026-10-22 |
    | CQL-TESTS | test-suite | informative | f724ee4d | cqframework/cql-tests@f724ee4d | | resources/spec/cql-tests/ | 2026-10-22 |
    | CQFW-9.9.9 | implementation-source | n/a | 9.9.9 | cqframework/clinical_quality_language@v9.9.9 | | | 2026-10-22 |
    | PROBES-2026-10-22 | observed-behavior | n/a | 2026-10-22 | resources/probes/2026-10-22/ | | resources/probes/2026-10-22/ | 2026-10-22 |
    """)

HEADER = textwrap.dedent("""\
    # Topic

    Baseline: CQL 1.5.3. Untagged statements hold in 1.4, 1.5.3 and 2.0.0.
    Sources: {sources}

    """)


def index_md(rows):
    body = "\n".join(f"| {p} | [{s}](https://x/{p}.html#a) | `sections/{p}/000-a.md` |" for p, s in rows)
    return f"# idx\n\n| Page | Section | File |\n| --- | --- | --- |\n{body}\n"


@pytest.fixture
def skill(tmp_path):
    s = tmp_path / "cql"
    spec = s / "resources" / "spec"
    for v in ("1.4", "1.5.3", "2.0.0"):
        (spec / v).mkdir(parents=True)
        (spec / v / "INDEX.md").write_text(index_md([
            ("09-b-cqlreference", "Type Operators > Is"),
            ("09-b-cqlreference", "List Operators > Exists"),
        ]))
    (spec / "CHANGES-1.4-to-1.5.3.md").write_text(
        "| Page | Section | +/- |\n| --- | --- | --- |\n"
        "| 09-b-cqlreference.html | [Type Operators > Is](https://x#is) | +1 / -1 |\n")
    (spec / "cql-tests").mkdir()
    (spec / "cql-tests" / "CqlListOperatorsTest.xml").write_text('<test name="EqualNullNull">')
    (s / "resources" / "probes" / "2026-10-22").mkdir(parents=True)
    (s / "resources" / "probes" / "2026-10-22" / "RESULTS.md").write_text("# r\n")
    (s / "resources" / "SOURCES.md").write_text(SOURCES)
    return s


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "cqfw"
    (r / "cql-to-elm" / "model").mkdir(parents=True)
    (r / "cql-to-elm" / "model" / "OperatorMap.kt").write_text("\n".join(f"line {i}" for i in range(1, 121)) + "\n")
    run = lambda *a: subprocess.run(["git", "-C", str(r), *a], check=True, capture_output=True)
    run("init", "-q")
    run("add", ".")
    run("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "x")
    run("tag", "v9.9.9")
    return r


def lint(skill, repo, body, sources="CQL-1.5.3", name="topic.md", capsys=None):
    (skill / "resources" / name).write_text(HEADER.format(sources=sources) + textwrap.dedent(body))
    code = lint_skill.main(["--skill-dir", str(skill), "--cqfw-repo", str(repo)])
    out = capsys.readouterr().out if capsys else ""
    return code, out


def test_clean_file_passes(skill, repo, capsys):
    code, out = lint(skill, repo, """\
        `exists` ignores nulls. [src: CQL-1.5.3 09-b-cqlreference > List Operators > Exists]
        """, capsys=capsys)
    assert code == 0, out
    assert "0 errors" in out


def test_missing_headers(skill, repo, capsys):
    (skill / "resources" / "bare.md").write_text("# Bare\n\nNo headers here.\n")
    code = lint_skill.main(["--skill-dir", str(skill), "--cqfw-repo", str(repo)])
    out = capsys.readouterr().out
    assert code == 1
    assert "bare.md: H1" in out and "bare.md: H2" in out


def test_unknown_source_id(skill, repo, capsys):
    code, out = lint(skill, repo, "Claim. [src: CQL-9.9 09-b-cqlreference > Type Operators > Is]\n",
                     sources="CQL-1.5.3, CQL-9.9", capsys=capsys)
    assert code == 1
    assert "H2 Sources lists unknown ID CQL-9.9" in out
    assert "C1 unknown source ID CQL-9.9" in out


def test_cited_id_missing_from_header(skill, repo, capsys):
    code, out = lint(skill, repo, "Claim. [src: CQL-1.4 09-b-cqlreference > List Operators > Exists]\n",
                     capsys=capsys)
    assert code == 1
    assert "H3 cites CQL-1.4" in out


def test_unknown_section_path(skill, repo, capsys):
    code, out = lint(skill, repo, "Claim. [src: CQL-1.5.3 09-b-cqlreference > Type Operators > Iss]\n",
                     capsys=capsys)
    assert code == 1 and "C2" in out


def test_changed_section_needs_version_tag(skill, repo, capsys):
    code, out = lint(skill, repo, "`is` tests the run-time type. [src: CQL-1.5.3 09-b-cqlreference > Type Operators > Is]\n",
                     capsys=capsys)
    assert code == 1 and "C3" in out


@pytest.mark.parametrize("tagged", [
    "`is` tests the type (same in 1.4, 2.0). [src: CQL-1.5.3 09-b-cqlreference > Type Operators > Is]\n",
    "`is` tests the type. **1.4:** worded differently. [src: CQL-1.5.3 09-b-cqlreference > Type Operators > Is]\n",
    "`is` tests the type (1.5+). [src: CQL-1.5.3 09-b-cqlreference > Type Operators > Is]\n",
    "`is` tests the type (1.5+, trial-use). [src: CQL-1.5.3 09-b-cqlreference > Type Operators > Is]\n",
])
def test_version_tag_satisfies_changed_section(skill, repo, capsys, tagged):
    code, out = lint(skill, repo, tagged, capsys=capsys)
    assert code == 0, out


def test_version_differences_table_satisfies_changed_section(skill, repo, capsys):
    code, out = lint(skill, repo, """\
        ## Is

        `is` tests the run-time type. [src: CQL-1.5.3 09-b-cqlreference > Type Operators > Is]

        **Version differences**

        | Version | Text |
        | --- | --- |
        | 1.4 | "is of the type" |
        """, capsys=capsys)
    assert code == 0, out


def test_tag_in_other_paragraph_does_not_count(skill, repo, capsys):
    code, out = lint(skill, repo, """\
        Something else (1.5+).

        `is` tests the run-time type. [src: CQL-1.5.3 09-b-cqlreference > Type Operators > Is]
        """, capsys=capsys)
    assert code == 1 and "C3" in out


def test_cqfw_line_range(skill, repo, capsys):
    ok, out = lint(skill, repo, "Ties. [src: CQFW-9.9.9 cql-to-elm/model/OperatorMap.kt:85-117]\n",
                   sources="CQFW-9.9.9", capsys=capsys)
    assert ok == 0, out
    bad, out = lint(skill, repo, "Ties. [src: CQFW-9.9.9 cql-to-elm/model/OperatorMap.kt:85-200]\n",
                    sources="CQFW-9.9.9", capsys=capsys)
    assert bad == 1 and "C4" in out and "past the end" in out


def test_cqfw_elided_path_resolves(skill, repo, capsys):
    code, out = lint(skill, repo, "Ties. [src: CQFW-9.9.9 cql-to-elm/…/OperatorMap.kt:85]\n",
                     sources="CQFW-9.9.9", capsys=capsys)
    assert code == 0, out


def test_cqfw_missing_file(skill, repo, capsys):
    code, out = lint(skill, repo, "X. [src: CQFW-9.9.9 cql-to-elm/model/Nope.kt:1]\n",
                     sources="CQFW-9.9.9", capsys=capsys)
    assert code == 1 and "C4" in out


def test_probe_and_test_locators(skill, repo, capsys):
    code, out = lint(skill, repo, """\
        Observed. [src: PROBES-2026-10-22 RESULTS.md §2]
        Test. [src: CQL-TESTS CqlListOperatorsTest.xml EqualNullNull]
        """, sources="PROBES-2026-10-22, CQL-TESTS", capsys=capsys)
    assert code == 0, out
    code, out = lint(skill, repo, """\
        Observed. [src: PROBES-2026-10-22 MISSING.md §2]
        Test. [src: CQL-TESTS CqlListOperatorsTest.xml NoSuchTest]
        """, sources="PROBES-2026-10-22, CQL-TESTS", capsys=capsys)
    assert code == 1 and "C5" in out and "C6" in out


def test_citations_in_code_blocks_are_ignored(skill, repo, capsys):
    code, out = lint(skill, repo, """\
        ```text
        [src: CQL-9.9 nowhere > at all]
        ```
        """, capsys=capsys)
    assert code == 0, out


def test_unused_source_is_warning_only(skill, repo, capsys):
    code, out = lint(skill, repo, "No citations.\n", sources="CQL-1.5.3", capsys=capsys)
    assert code == 0
    assert "WARN" in out and "H3" in out


@pytest.mark.parametrize("loc,ok", [
    ("HL7/cql@v1.5.3", True),
    ("hl7.fhir.us.qicore#7.0.0", True),
    ("cqframework/cql-tests@f724ee4d", True),
    ("resources/probes/2026-10-22/", True),
    ("HL7/cql@master", False),
    ("mermaid-js/mermaid@main", False),
    ("https://hl7.org/fhir/us/qicore/current/", False),
    ("https://fshschool.org/docs/sushi/", False),
    ("https://hl7.org/fhir/R4/4.0.1/", True),
])
def test_pinned_locator_rule(tmp_path, loc, ok):
    p = tmp_path / "SOURCES.md"
    p.write_text("| ID | Kind | Status | Pinned locator |\n| --- | --- | --- | --- |\n"
                 f"| X | package | n/a | {loc} |\n")
    rep = lint_skill.Report()
    lint_skill.parse_sources(p, rep)
    assert (not rep.errors) == ok, rep.errors


def test_bad_kind(tmp_path):
    p = tmp_path / "SOURCES.md"
    p.write_text("| ID | Kind | Status | Pinned locator |\n| --- | --- | --- | --- |\n| X | webpage | n/a | a@v1 |\n")
    rep = lint_skill.Report()
    lint_skill.parse_sources(p, rep)
    assert any("S2" in e for e in rep.errors)


def test_skip_files_not_linted(skill, repo, capsys):
    (skill / "resources" / "to-relocate.md").write_text("# no headers, cites [src: NOPE x]\n")
    code = lint_skill.main(["--skill-dir", str(skill), "--cqfw-repo", str(repo)])
    out = capsys.readouterr().out
    assert "to-relocate.md" not in out


def run(skill, repo, capsys):
    code = lint_skill.main(["--skill-dir", str(skill), "--cqfw-repo", str(repo)])
    return code, capsys.readouterr().out


def test_skill_md_citations_are_linted_without_header_rule(skill, repo, capsys):
    (skill / "SKILL.md").write_text("---\nname: cql\n---\n\nClaim. [src: CQL-9.9 x > y]\n")
    code, out = run(skill, repo, capsys)
    assert code == 1
    assert "SKILL.md:" in out and "C1 unknown source ID CQL-9.9" in out
    assert "SKILL.md: H1" not in out and "SKILL.md: H2" not in out


def test_skill_md_clean_citation_passes(skill, repo, capsys):
    (skill / "SKILL.md").write_text("# S\n\nX. [src: CQL-1.5.3 09-b-cqlreference > List Operators > Exists]\n")
    code, out = run(skill, repo, capsys)
    assert code == 0, out


TABLE = """\
| Feature | First version | Status |
| --- | --- | --- |
| `is` [src: CQL-1.5.3 09-b-cqlreference > Type Operators > Is] | {cell} | — |
"""


@pytest.mark.parametrize("cell,ok", [("1.5", True), ("1.4", True), ("2.0", True), ("—", False), ("", False)])
def test_first_version_column_counts_as_tag(skill, repo, capsys, cell, ok):
    (skill / "SKILL.md").write_text("# S\n\n" + TABLE.format(cell=cell))
    code, out = run(skill, repo, capsys)
    assert (code == 0) == ok, out


def test_other_table_columns_do_not_count_as_tag(skill, repo, capsys):
    (skill / "SKILL.md").write_text(
        "# S\n\n| Feature | Notes |\n| --- | --- |\n"
        "| `is` [src: CQL-1.5.3 09-b-cqlreference > Type Operators > Is] | 1.5 |\n")
    code, out = run(skill, repo, capsys)
    assert code == 1 and "C3" in out


def test_probe_records_are_not_linted(skill, repo, capsys):
    (skill / "resources" / "probes" / "2026-10-22" / "RESULTS.md").write_text("# r\n[src: NOPE x]\n")
    code, out = run(skill, repo, capsys)
    assert "RESULTS.md" not in out


@pytest.mark.parametrize("kind", ["normative-spec", "informative-guide", "webpage"])
def test_old_or_unknown_kinds_rejected(tmp_path, kind):
    p = tmp_path / "SOURCES.md"
    p.write_text(f"| ID | Kind | Status | Pinned locator |\n| --- | --- | --- | --- |\n| X | {kind} | n/a | a@v1 |\n")
    rep = lint_skill.Report()
    lint_skill.parse_sources(p, rep)
    assert any("S2" in e for e in rep.errors)


@pytest.mark.parametrize("status,ok", [("normative", True), ("trial-use", True), ("informative", True),
                                       ("n/a", True), ("draft", False), ("", False)])
def test_status_values(tmp_path, status, ok):
    p = tmp_path / "SOURCES.md"
    p.write_text(f"| ID | Kind | Status | Pinned locator |\n| --- | --- | --- | --- |\n| X | spec | {status} | a@v1 |\n")
    rep = lint_skill.Report()
    lint_skill.parse_sources(p, rep)
    assert (not any("S4" in e for e in rep.errors)) == ok, rep.errors


def test_missing_status_column(tmp_path):
    p = tmp_path / "SOURCES.md"
    p.write_text("| ID | Kind | Pinned locator |\n| --- | --- | --- |\n| X | spec | a@v1 |\n")
    rep = lint_skill.Report()
    lint_skill.parse_sources(p, rep)
    assert any("S4" in e and "no Status column" in e for e in rep.errors)


def test_column_order_does_not_matter(tmp_path):
    p = tmp_path / "SOURCES.md"
    p.write_text("| Pinned locator | Status | ID | Kind |\n| --- | --- | --- | --- |\n| a@v1 | normative | X | spec |\n")
    rep = lint_skill.Report()
    assert "X" in lint_skill.parse_sources(p, rep)
    assert not rep.errors, rep.errors


def test_spec_published_test_citation_is_rejected(skill, repo, capsys):
    # Even when a copy of the spec's own suite exists locally, citing it is an error.
    t = skill / "resources" / "spec" / "1.5.3" / "tests"
    t.mkdir(parents=True)
    (t / "CqlTypeOperatorsTest.xml").write_text('<test name="StringToIntegerError" invalid="true">')
    code, out = lint(skill, repo, "Invalid in 1.5.3. [src: CQL-1.5.3 tests/CqlTypeOperatorsTest.xml StringToIntegerError]\n",
                     capsys=capsys)
    assert code == 1 and "C8" in out and "CQL-TESTS" in out
    code, out = lint(skill, repo, "X. [src: CQL-1.4 tests/CqlTypeOperatorsTest.xml StringToIntegerError]\n",
                     sources="CQL-1.4", capsys=capsys)
    assert code == 1 and "C8" in out


def add_guide(skill):
    g = skill / "resources" / "guides" / "cql-wiki"
    g.mkdir(parents=True)
    (g / "QA-Much-Ado-About-Nothing.md").write_text("# Q&A\n")
    with (skill / "resources" / "SOURCES.md").open("a") as fh:
        fh.write("| CQLWIKI | guide | informative | cc3c3512 | cqframework/CQL-Formatting-and-Usage-Wiki.wiki@cc3c3512 "
                 "| https://github.com/cqframework/CQL-Formatting-and-Usage-Wiki/wiki | `resources/guides/cql-wiki/` | 2026-10-22 |\n")


def test_guide_citation_file_must_exist(skill, repo, capsys):
    # the fixture's registry table ends without a trailing blank line, so the appended row joins it
    add_guide(skill)
    code, out = lint(skill, repo, "Idiom. [src: CQLWIKI QA-Much-Ado-About-Nothing.md]\n",
                     sources="CQLWIKI", capsys=capsys)
    assert code == 0, out
    code, out = lint(skill, repo, "Idiom. [src: CQLWIKI QA-Much-Ado-About-Nothing.md#answer]\n",
                     sources="CQLWIKI", capsys=capsys)
    assert code == 0, out
    code, out = lint(skill, repo, "Idiom. [src: CQLWIKI Missing-Page.md]\n", sources="CQLWIKI", capsys=capsys)
    assert code == 1 and "C7" in out and "Missing-Page.md" in out


def test_source_without_local_copy_is_not_file_checked(skill, repo, capsys):
    with (skill / "resources" / "SOURCES.md").open("a") as fh:
        fh.write("| CONV-1 | convention | n/a | v1 | team-notes@v1 | | none | 2026-10-22 |\n")
    code, out = lint(skill, repo, "Team rule. [src: CONV-1 anything at all]\n", sources="CONV-1", capsys=capsys)
    assert code == 0, out


def test_include_lints_a_file_outside_resources(skill, repo, capsys):
    (skill / "evals").mkdir()
    (skill / "evals" / "key.md").write_text(HEADER.format(sources="CQL-1.5.3")
                                            + "Claim. [src: CQL-9.9 x > y]\n")
    code = lint_skill.main(["--skill-dir", str(skill), "--cqfw-repo", str(repo),
                            "--include", "evals/key.md"])
    out = capsys.readouterr().out
    assert code == 1
    assert "key.md:" in out and "C1 unknown source ID CQL-9.9" in out


def test_include_absent_by_default(skill, repo, capsys):
    (skill / "evals").mkdir()
    (skill / "evals" / "key.md").write_text("# no headers\n")
    code, out = run(skill, repo, capsys)
    assert "key.md" not in out


def test_include_accepts_absolute_path(skill, repo, capsys, tmp_path):
    other = tmp_path / "elsewhere.md"
    other.write_text("# Bare\n\nNo headers.\n")
    code = lint_skill.main(["--skill-dir", str(skill), "--cqfw-repo", str(repo),
                            "--include", str(other)])
    out = capsys.readouterr().out
    assert code == 1
    assert "elsewhere.md: H1" in out


def test_include_missing_file_is_an_error(skill, repo, capsys):
    code = lint_skill.main(["--skill-dir", str(skill), "--cqfw-repo", str(repo),
                            "--include", "evals/nope.md"])
    out = capsys.readouterr().out
    assert code == 1
    assert "nope.md" in out and "not found" in out


@pytest.mark.parametrize("inc, absolute", [
    ("/path/to/file.md", True),        # macOS / Linux
    ("C:\\path\\to\\file.md", True),   # Windows, backslash
    ("C:/path/to/file.md", True),      # Windows, forward slash
    ("evals/file.md", False),          # relative to the skill dir
])
def test_resolve_include_platform_paths(tmp_path, inc, absolute):
    got = lint_skill.resolve_include(inc, tmp_path)
    if absolute:
        assert got == lint_skill.Path(inc)
    else:
        assert got == tmp_path / "evals" / "file.md"


def test_citation_inside_inline_code_is_not_linted(skill, repo, capsys):
    code, out = lint(skill, repo, "Cite as `[src: NOPE-1 some locator]` in prose.\n", capsys=capsys)
    assert code == 0, out
    assert "NOPE-1" not in out


def test_citation_beside_inline_code_is_still_linted(skill, repo, capsys):
    code, out = lint(skill, repo, "`code` then [src: CQL-9.9 x > y] and `more`\n",
                     sources="CQL-1.5.3, CQL-9.9", capsys=capsys)
    assert code == 1
    assert "C1 unknown source ID CQL-9.9" in out


def test_code_span_wrapped_across_lines_hides_its_citation_only(skill, repo, capsys):
    code, out = lint(skill, repo, """\
        Example: `[src: NOPE-1
        x > y]` and then [src: CQL-9.9 a > b].
        """, sources="CQL-1.5.3, CQL-9.9", capsys=capsys)
    assert "NOPE-1" not in out
    assert "C1 unknown source ID CQL-9.9" in out


def test_blocks_keeps_line_numbers_and_length_with_code_spans():
    text = "Para one with `[src: X y]` code.\nsecond line\n\n| a | `b` |\n"
    got = list(lint_skill.blocks(text))
    assert [(s, e) for s, e, _, _ in got] == [(1, 2), (4, 4)]
    first = got[0][2]
    assert len(first) == len("Para one with `[src: X y]` code.\nsecond line")
    assert "[src:" not in first and "second line" in first
