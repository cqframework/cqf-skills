"""Tests for reflow_md.py. Run: python3 -m pytest -q test_reflow_md.py"""

import textwrap

import reflow_md

LONG_SRC = "[src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/model/OperatorMap.kt:85-117]"


def lines_over(text, width=100):
    return [l for l in text.split("\n") if len(l) > width]


def test_short_paragraph_is_unchanged():
    text = "A short line.\nAnother short line.\n"
    assert reflow_md.reflow(text) == text


def test_long_paragraph_is_wrapped_and_text_kept():
    text = ("word " * 40).strip() + "\n"
    out = reflow_md.reflow(text)
    assert not lines_over(out)
    assert reflow_md.same_text(text, out)


def test_citation_stays_whole_and_punctuation_stays_attached():
    text = "See the tie-break " + LONG_SRC + ". Then more text follows here to make it long enough.\n"
    out = reflow_md.reflow(text)
    assert LONG_SRC + "." in out
    assert "] ." not in out


def test_code_span_and_link_stay_whole():
    text = ("Use `a long inline code span with spaces` and [a link with words](#some-anchor), "
            "then keep writing until the paragraph is clearly longer than one hundred characters.\n")
    out = reflow_md.reflow(text)
    assert "`a long inline code span with spaces`" in out
    assert "[a link with words](#some-anchor)" in out


def test_list_item_keeps_bullet_and_indents_continuation():
    text = "- " + ("item text " * 15).strip() + "\n"
    out = reflow_md.reflow(text).split("\n")
    assert out[0].startswith("- ") and not out[0].startswith("-  ")
    assert out[1].startswith("  ") and not out[1].startswith("   ")


def test_numbered_item_indent_matches_marker():
    out = reflow_md.reflow("10. " + ("text " * 30).strip()).split("\n")
    assert out[0].startswith("10. ")
    assert out[1].startswith("    ") and not out[1].startswith("     ")


def test_blockquote_keeps_markers():
    text = "> " + ("quoted words " * 12).strip() + "\n"
    out = reflow_md.reflow(text).split("\n")
    assert all(l.startswith("> ") for l in out if l)


def test_tables_headings_and_code_are_untouched():
    long = "x " * 70
    text = textwrap.dedent(f"""\
        # Heading {long}

        | a | {long} |
        | --- | --- |

        ```cql
        define "X": {long}
        ```
        """)
    assert reflow_md.reflow(text) == text


def test_lone_unbreakable_token_stays_long():
    out = reflow_md.reflow(LONG_SRC + "\n")
    assert out.split("\n")[0] == LONG_SRC


def test_same_text_detects_change():
    assert reflow_md.same_text("a b\nc", "a\nb c")
    assert not reflow_md.same_text("a b c", "a c b")


def test_main_writes_file(tmp_path, capsys):
    f = tmp_path / "x.md"
    f.write_text(("word " * 40).strip() + "\n")
    assert reflow_md.main([str(f)]) == 0
    assert not lines_over(f.read_text())
    assert "reflowed" in capsys.readouterr().out


def test_main_reports_unchanged(tmp_path, capsys):
    f = tmp_path / "x.md"
    f.write_text("short\n")
    assert reflow_md.main([str(f)]) == 0
    assert "unchanged" in capsys.readouterr().out
