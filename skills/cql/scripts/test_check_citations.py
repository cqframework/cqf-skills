"""Tests for check_citations.py. Run: python3 -m pytest -q test_check_citations.py"""

import textwrap
from pathlib import Path

import pytest

import check_citations as cc

IS_14 = "If the run-time type of the argument is of the type being tested, the result is true."
IS_153 = "If the run-time type of the argument is the same as or derived from the type being tested, the result is true."


@pytest.fixture
def spec(tmp_path):
    root = tmp_path / "spec"
    for v, text in (("1.4", IS_14), ("1.5.3", IS_153), ("2.0.0", IS_153 + " Note that null is Integer returns false.")):
        d = root / v / "sections" / "09-b-cqlreference"
        d.mkdir(parents=True)
        (d / "029-is.md").write_text(f"<!--\nurl: x\n-->\n#### Is\n\n{text}\n")
        (root / v / "INDEX.md").write_text(
            f"| 09-b | [Type Operators > Is](https://cql.hl7.org/{'N1A/' if v == '1.5.3' else ''}09-b-cqlreference.html#is) | `x` |\n")
    return cc.Spec(root)


def run(spec, tmp_path, body):
    f = tmp_path / "doc.md"
    f.write_text(textwrap.dedent(body))
    lines = []
    counts = cc.check(f, spec, out=lines.append)
    return counts, lines


def test_single_line_quote_ok(spec, tmp_path):
    counts, _ = run(spec, tmp_path, 'CQL 1.5.3 says "the same as or derived from the type being tested".\n')
    assert counts["OK"] == 1 and counts["NOT-FOUND"] == 0


def test_quote_wrapped_across_lines_is_checked(spec, tmp_path):
    counts, _ = run(spec, tmp_path, '''\
        CQL 1.5.3 says "If the run-time type of the argument is the same as or
        derived from the type being tested, the result is true".
        ''')
    assert counts["OK"] == 1


def test_wrapped_misquote_is_caught(spec, tmp_path):
    counts, lines = run(spec, tmp_path, '''\
        CQL 1.5.3 says "If the run-time type of the argument is exactly
        the type being tested, the result is true".
        ''')
    assert counts["NOT-FOUND"] == 1
    assert any("doc.md:1: NOT-FOUND" in l for l in lines)


def test_wrong_version_reported(spec, tmp_path):
    counts, lines = run(spec, tmp_path, 'In 1.5.3: "Note that null is Integer returns false".\n')
    assert counts["WRONG-VERSION"] == 1
    assert any("found in 2.0.0" in l for l in lines)


def test_version_carries_to_next_paragraph(spec, tmp_path):
    counts, _ = run(spec, tmp_path, '''\
        The 1.4 text:

        "If the run-time type of the argument is of the type being tested".
        ''')
    assert counts["OK"] == 1


def test_ellipsis_is_a_gap(spec, tmp_path):
    counts, _ = run(spec, tmp_path, 'CQL 1.5.3: "If the run-time type … the type being tested, the result is true".\n')
    assert counts["OK"] == 1


def test_quotes_in_code_blocks_ignored(spec, tmp_path):
    counts, _ = run(spec, tmp_path, '''\
        ```cql
        define X: "this is a long quoted identifier inside code"
        ```
        ''')
    assert sum(counts.values()) == 0


def test_table_rows_are_separate_paragraphs(spec, tmp_path):
    counts, _ = run(spec, tmp_path, '''\
        | Version | Text |
        | --- | --- |
        | 1.4 | "If the run-time type of the argument is of the type being tested" |
        | 1.5.3 | "the same as or derived from the type being tested" |
        ''')
    assert counts["OK"] == 2


def test_bad_url_anchor(spec, tmp_path):
    counts, _ = run(spec, tmp_path, "See https://cql.hl7.org/09-b-cqlreference.html#nope and "
                                    "https://cql.hl7.org/N1A/09-b-cqlreference.html#is.\n")
    assert counts["BAD-URL"] == 1


def test_default_spec_dir_is_relative_to_script(tmp_path, monkeypatch, capsys):
    # Lay out a fake skill: <skill>/scripts/check_citations.py and <skill>/resources/spec/...
    skill = tmp_path / "skill"
    for v in ("1.4", "1.5.3", "2.0.0"):
        (skill / "resources" / "spec" / v / "sections").mkdir(parents=True)
    d = skill / "resources" / "spec" / "1.5.3" / "sections" / "p"
    d.mkdir(parents=True)
    (d / "000-a.md").write_text("the same as or derived from the type being tested\n")
    (skill / "scripts").mkdir()
    monkeypatch.setattr(cc, "__file__", str(skill / "scripts" / "check_citations.py"))
    doc = tmp_path / "doc.md"
    doc.write_text('CQL 1.5.3: "the same as or derived from the type being tested".\n')
    cc.main([str(doc)])
    assert "OK=1" in capsys.readouterr().out


def test_quote_marks_inside_inline_code_ignored(spec, tmp_path):
    counts, _ = run(spec, tmp_path, 'The ELM is `<operand asType="t:Integer" xsi:type="As">` here, long enough.\n')
    assert sum(counts.values()) == 0


def test_blockquote_markers_are_stripped(spec, tmp_path):
    counts, _ = run(spec, tmp_path, '''\
        CQL 1.5.3:

        > "If the run-time type of the argument is the same as or derived from the type being
        > tested, the result is true."
        ''')
    assert counts["OK"] == 1 and counts["NOT-FOUND"] == 0


def test_short_quote_does_not_pair_with_next(spec, tmp_path):
    counts, _ = run(spec, tmp_path,
                    'In 1.5.3 it is "derived" when the text says "the same as or derived from the type being tested".\n')
    assert counts["OK"] == 1 and counts["NOT-FOUND"] == 0


def test_version_column_header_sets_version(spec, tmp_path):
    counts, lines = run(spec, tmp_path, '''\
        Discussed in 1.5.3 below.

        | Topic | 1.4 | 1.5.3 | 2.0.0 |
        | --- | --- | --- | --- |
        | Is | "If the run-time type of the argument is of the type being tested" | "the same as or derived from the type being tested" | "Note that null is Integer returns false" |
        ''')
    assert counts["OK"] == 3, lines
    assert counts["WRONG-VERSION"] == 0


def test_non_version_column_falls_back_to_prose_version(spec, tmp_path):
    counts, _ = run(spec, tmp_path, '''\
        The 1.4 wording:

        | Operator | Text |
        | --- | --- |
        | Is | "If the run-time type of the argument is of the type being tested" |
        ''')
    assert counts["OK"] == 1


def test_quote_found_only_in_guide_is_reported_as_guide(tmp_path):
    root = tmp_path / "spec"
    d = root / "1.5.3" / "sections" / "p"
    d.mkdir(parents=True)
    (d / "000-a.md").write_text("spec text only\n")
    g = tmp_path / "guides" / "wiki"
    g.mkdir(parents=True)
    (g / "QA.md").write_text("CQL provides a number of ways to say no that may look similar at first\n")
    spec = cc.Spec(root, tmp_path / "guides")
    doc = tmp_path / "doc.md"
    doc.write_text('The wiki says "CQL provides a number of ways to say no that may look similar at first".\n'
                   'And "this sentence appears in neither the spec nor the guide".\n')
    lines = []
    counts = cc.check(doc, spec, out=lines.append)
    assert counts["GUIDE"] == 1 and counts["NOT-FOUND"] == 1, lines
    assert any("GUIDE (guide text, not spec)" in l for l in lines)


def test_no_guide_dir_means_no_guide_classification(spec, tmp_path):
    counts, _ = run(spec, tmp_path, 'Quote "this sentence appears in neither the spec nor the guide".\n')
    assert counts["GUIDE"] == 0 and counts["NOT-FOUND"] == 1


def test_inline_links_in_spec_text_match_rendered_quote(tmp_path):
    root = tmp_path / "spec"
    d = root / "2.0.0" / "sections" / "03-developersguide"
    d.mkdir(parents=True)
    (d / "010-data-models.md").write_text(
        "The local [identifier](#identifiers) for a referenced model must be [unqualified](#qualified-identifiers) and unique.\n")
    spec = cc.Spec(root)
    doc = tmp_path / "doc.md"
    doc.write_text('In 2.0.0: "The local identifier for a referenced model must be unqualified and unique".\n')
    lines = []
    counts = cc.check(doc, spec, out=lines.append)
    assert counts["OK"] == 1, lines


def test_blockquote_with_inner_quote_marks_checked_whole(tmp_path):
    root = tmp_path / "spec"
    (root / "1.5.3" / "sections").mkdir(parents=True)
    g = tmp_path / "guides" / "wiki"
    g.mkdir(parents=True)
    (g / "QA.md").write_text('When calling an "exists" on something that returns "false", you will always get a true result back.\n')
    spec = cc.Spec(root, tmp_path / "guides")
    doc = tmp_path / "doc.md"
    doc.write_text('The page says:\n\n> "When calling an "exists" on something that returns "false", you will\n'
                   '> always get a true result back." [src: CQLWIKI QA.md]\n\nAfterwards, prose.\n')
    lines = []
    counts = cc.check(doc, spec, out=lines.append)
    assert counts["GUIDE"] == 1 and counts["NOT-FOUND"] == 0, lines


def test_blockquote_not_a_single_quotation_uses_pairing(spec, tmp_path):
    counts, _ = run(spec, tmp_path, '''\
        > In 1.5.3 the text reads "the same as or derived from the type being tested" here.
        ''')
    assert counts["OK"] == 1


def test_plain_blockquote_is_the_quotation(spec, tmp_path):
    counts, _ = run(spec, tmp_path, '''\
        CQL 1.5.3:

        > If the run-time type of the argument is the same as or derived from the type being
        > tested, the result is true.
        ''')
    assert counts["OK"] == 1


def test_bold_callout_blockquote_is_not_a_quotation(spec, tmp_path):
    counts, _ = run(spec, tmp_path, '''\
        > **Holding area, not guidance.** Nothing in this file is model-independent CQL.
        ''')
    assert sum(counts.values()) == 0


def test_missing_spec_dir_is_an_error(tmp_path, capsys):
    doc = tmp_path / "doc.md"
    doc.write_text('In 1.5.3: "the same as or derived from the type being tested".\n')
    code = cc.main(["--spec-dir", str(tmp_path / "nowhere"), str(doc)])
    assert code == 2
    assert "no spec sections" in capsys.readouterr().err


# A quote's own link names its version: STU4 is 1.4, N1A is 1.5.3, no prefix is 2.0.0.

N1A_IS = "https://cql.hl7.org/N1A/09-b-cqlreference.html#is"
STU4_IS = "https://cql.hl7.org/STU4/09-b-cqlreference.html#is"
CUR_IS = "https://cql.hl7.org/09-b-cqlreference.html#is"


def test_following_link_overrides_earlier_version_tag(spec, tmp_path):
    counts, _ = run(spec, tmp_path, f'In 1.4 terms, "the same as or derived from the type being tested" ([Is]({N1A_IS})).\n')
    assert counts["OK"] == 1 and counts["WRONG-VERSION"] == 0


def test_stu4_link_means_1_4(spec, tmp_path):
    counts, _ = run(spec, tmp_path, f'Per 2.0.0, "If the run-time type of the argument is of the type being tested" ([Is]({STU4_IS})).\n')
    assert counts["OK"] == 1 and counts["WRONG-VERSION"] == 0


def test_unprefixed_link_means_2_0_0(spec, tmp_path):
    counts, _ = run(spec, tmp_path, f'In 1.5.3 notes: "Note that null is Integer returns false" ([Is]({CUR_IS})).\n')
    assert counts["OK"] == 1 and counts["WRONG-VERSION"] == 0


def test_link_to_wrong_version_is_still_caught(spec, tmp_path):
    counts, lines = run(spec, tmp_path, f'The text "Note that null is Integer returns false" ([Is]({N1A_IS})).\n')
    assert counts["WRONG-VERSION"] == 1
    assert any("[1.5.3] (found in 2.0.0)" in l for l in lines)


def test_preceding_link_names_the_version(spec, tmp_path):
    counts, _ = run(spec, tmp_path, f'Unlike 1.4, [Is]({N1A_IS}) says "the same as or derived from the type being tested".\n')
    assert counts["OK"] == 1 and counts["WRONG-VERSION"] == 0


def test_link_after_a_later_quote_does_not_apply_to_an_earlier_one(spec, tmp_path):
    counts, _ = run(spec, tmp_path,
                    f'In 1.4: "If the run-time type of the argument is of the type being tested", but now '
                    f'"the same as or derived from the type being tested" ([Is]({N1A_IS})).\n')
    assert counts["OK"] == 2 and counts["WRONG-VERSION"] == 0


def test_link_in_a_table_row(spec, tmp_path):
    counts, _ = run(spec, tmp_path, f'''\
        The 1.4 rules:

        | Topic | Text |
        | --- | --- |
        | Is | "the same as or derived from the type being tested" [Is]({N1A_IS}) |
        ''')
    assert counts["OK"] == 1 and counts["WRONG-VERSION"] == 0


def test_version_column_still_wins_over_a_link(spec, tmp_path):
    counts, _ = run(spec, tmp_path, f'''\
        | Topic | 1.4 |
        | --- | --- |
        | Is | "If the run-time type of the argument is of the type being tested" [x]({N1A_IS}) |
        ''')
    assert counts["OK"] == 1


def test_unknown_url_prefix_falls_back_to_the_tag(spec, tmp_path):
    counts, _ = run(spec, tmp_path, 'In 1.4: "If the run-time type of the argument is of the type being tested" '
                                    '([Is](https://cql.hl7.org/2019May/09-b-cqlreference.html#is)).\n')
    assert counts["OK"] == 1


@pytest.mark.parametrize("url, version", [
    ("https://cql.hl7.org/STU4/09-b-cqlreference.html#is", "1.4"),
    ("https://cql.hl7.org/N1A/09-b-cqlreference.html#is", "1.5.3"),
    ("https://cql.hl7.org/09-b-cqlreference.html#is", "2.0.0"),
    ("http://cql.hl7.org/N1A/02-authorsguide.html", "1.5.3"),
    ("https://cql.hl7.org/2019May/09-b-cqlreference.html", None),
    ("https://cql.hl7.org/", None),
])
def test_url_version(url, version):
    assert cc.url_version(url) == version
