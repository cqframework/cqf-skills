"""Tests for section_diff.py. Run: python3 -m pytest -q test_section_diff.py"""

import textwrap

import pytest

import section_diff


def write_index(root, version, rows):
    body = "\n".join(f"| {p} | [{s}](https://x/{p}.html#a) | `sections/{p}/000-a.md` |" for p, s in rows)
    d = root / version
    d.mkdir(parents=True, exist_ok=True)
    (d / "INDEX.md").write_text(f"# idx\n\n| Page | Section | File |\n| --- | --- | --- |\n{body}\n")


def changes(sections):
    """Build a CHANGES list with one diff block per (page, section, diff lines)."""
    parts = ["# changes\n"]
    for page, sec, lines in sections:
        parts.append(f"### {page}.html: {sec}\n\n```diff\n@@ -1 +1 @@\n" + "\n".join(lines) + "\n```\n")
    return "\n".join(parts)


@pytest.fixture
def spec(tmp_path):
    for v in ("1.4", "1.5.3", "2.0.0"):
        write_index(tmp_path, v, [("09-b-cqlreference", "Type Operators > Is")])
    write_index(tmp_path, "1.5.3", [("09-b-cqlreference", "Type Operators > Is"),
                                    ("09-b-cqlreference", "Types > Long")])
    (tmp_path / "CHANGES-1.4-to-1.5.3.md").write_text(changes([
        ("09-b-cqlreference", "Type Operators > Is",
         ['-define IsTrue: 5 is Integer', '+define "IsTrue": 5 is Integer']),
        ("09-b-cqlreference", "Types > Integer",
         ["-range -2^31^ to 2^31^-1", "+range -2<sup>31</sup> to 2<sup>31</sup>-1"]),
    ]))
    (tmp_path / "CHANGES-1.5.3-to-2.0.0.md").write_text(changes([
        ("09-b-cqlreference", "Type Operators > Is", ["+the expression null is Integer returns false."]),
    ]))
    return tmp_path


def test_quoting_only_change_has_no_meaningful_lines(spec):
    got = section_diff.section_changes(spec, "09-b-cqlreference", "Type Operators > Is")
    assert got["CHANGES-1.4-to-1.5.3.md"] == []


def test_real_change_is_kept(spec):
    got = section_diff.section_changes(spec, "09-b-cqlreference", "Type Operators > Is")
    assert got["CHANGES-1.5.3-to-2.0.0.md"] == ["+the expression null is Integer returns false."]


def test_superscript_markup_is_noise(spec):
    got = section_diff.section_changes(spec, "09-b-cqlreference", "Types > Integer")
    assert got["CHANGES-1.4-to-1.5.3.md"] == []


def test_section_absent_from_a_list_is_omitted(spec):
    got = section_diff.section_changes(spec, "09-b-cqlreference", "Types > Integer")
    assert "CHANGES-1.5.3-to-2.0.0.md" not in got


@pytest.mark.parametrize("line", ["+================", "+Table 3‑I - The defined conversions",
                                  "+Figure 4‑D - A diagram", '+<div><img src="x.png"/></div>'])
def test_table_figure_and_image_lines_are_noise(line):
    assert section_diff.meaningful_lines(line) == []


def test_empty_lines_do_not_crash():
    assert section_diff.meaningful_lines("\n\n+real text\n\n") == ["+real text"]


def test_load_index_reads_rows(spec):
    rows = section_diff.load_index(spec, "1.5.3")
    assert ("09-b-cqlreference", "Types > Long") in rows


def test_main_reports_versions_and_quoting_only(spec, capsys):
    assert section_diff.main(["--spec-dir", str(spec), "09-b-cqlreference|Type Operators > Is"]) == 0
    out = capsys.readouterr().out
    assert "[in: 1.4, 1.5.3, 2.0.0]" in out
    assert "1.4-to-1.5.3: (quoting/markup only)" in out
    assert "+the expression null is Integer returns false." in out


def test_main_reports_section_missing_everywhere(spec, capsys):
    section_diff.main(["--spec-dir", str(spec), "09-b-cqlreference|Nope"])
    assert "[in: none]" in capsys.readouterr().out


def test_main_rejects_argument_without_separator(spec):
    with pytest.raises(SystemExit):
        section_diff.main(["--spec-dir", str(spec), "no separator"])
