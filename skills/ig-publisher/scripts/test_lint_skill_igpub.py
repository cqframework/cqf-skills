"""Tests for lint_skill_igpub.py. Run: python3 -m pytest -q scripts/test_lint_skill_igpub.py"""

import json
import subprocess
import textwrap
from pathlib import Path

import pytest

import lint_skill_igpub as L

CQL_LINT = Path(__file__).resolve().parent / "lint_skill.py"
needs_cql_lint = pytest.mark.skipif(not CQL_LINT.exists(), reason="cql skill's lint_skill.py not present")

SOURCES = textwrap.dedent("""\
    # Sources

    | ID | Kind | Status | Version | Pinned locator | Published URL | Local copy | Retrieved |
    | --- | --- | --- | --- | --- | --- | --- | --- |
    | GIT-1.0 | implementation-source | n/a | 1.0 | example/repo@1.0 | | none | 2026-10-22 |
    | TOOLS-9.9.9 | package | informative | 9.9.9 | hl7.fhir.uv.tools#9.9.9 | | `resources/sources/tools/` | 2026-10-22 |
    """)

HEADER = textwrap.dedent("""\
    # Topic

    Baseline: test.
    Sources: {sources}

    """)


# --- pure functions -------------------------------------------------------------------------

@pytest.mark.parametrize("arg, sid, path", [
    ("VSCQL=/path/to/vscode-cql", "VSCQL", "/path/to/vscode-cql"),      # macOS / Linux
    ("VSCQL=C:\\src\\vscode-cql", "VSCQL", "C:\\src\\vscode-cql"),      # Windows, backslash
    ("VSCQL=C:/src/vscode-cql", "VSCQL", "C:/src/vscode-cql"),          # Windows, forward slash
    ("X=a=b", "X", "a=b"),                                              # only the first '=' splits
])
def test_parse_repo_arg(arg, sid, path):
    got_id, got_path = L.parse_repo_arg(arg)
    assert got_id == sid
    assert str(got_path) == str(Path(path))


@pytest.mark.parametrize("arg", ["VSCQL", "=/x", "VSCQL="])
def test_parse_repo_arg_rejects(arg):
    with pytest.raises(ValueError):
        L.parse_repo_arg(arg)


@pytest.mark.parametrize("loc, expected", [
    ("src/a/B.java:12-14", ("src/a/B.java", 12, 14)),        # posix, range
    ("src/a/B.java:12", ("src/a/B.java", 12, 12)),           # posix, single line
    ("org.hl7/…/B.java:7", ("org.hl7/…/B.java", 7, 7)),      # elided path
    ("C:\\src\\B.java:12", ("C:\\src\\B.java", 12, 12)),     # Windows, backslash
    ("C:/src/B.java:12-13", ("C:/src/B.java", 12, 13)),      # Windows, forward slash
    ("`src/B.java:3`", ("src/B.java", 3, 3)),                # backticks stripped
    ("src/B.java", None),                                    # no line
    ("src/B.java:abc", None),
])
def test_split_line_locator(loc, expected):
    assert L.split_line_locator(loc) == expected


@pytest.mark.parametrize("loc, expected", [
    ("scripts/onLoad.xslt#L12", (12, 12)),
    ("scripts/onLoad.xslt#L12-L14", (12, 14)),
    ("scripts/onLoad.xslt#L12-14", (12, 14)),
    ("CodeSystem-ig-parameters.json#path-binary", None),
    ("config.json", None),
])
def test_anchor_lines(loc, expected):
    assert L.anchor_lines(loc) == expected


@pytest.mark.parametrize("locator, ref", [
    ("HL7/fhir-ig-publisher@3.0.1", "3.0.1"),
    ("vscode-cql@f910ac74af6f", "f910ac74af6f"),
    ("hl7.fhir.uv.tools#1.3.0", None),
    ("https://example.org/x", None),
])
def test_git_ref(locator, ref):
    assert L.git_ref({"pinned locator": locator}) == ref


def test_codesystem_codes_walks_nested(tmp_path):
    f = tmp_path / "cs.json"
    f.write_text(json.dumps({"concept": [{"code": "a", "concept": [{"code": "b"}]}, {"code": "c"}]}))
    assert L.codesystem_codes(f) == {"a", "b", "c"}


# --- whole-skill runs -----------------------------------------------------------------------

@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    (r / "src" / "deep").mkdir(parents=True)
    (r / "src" / "deep" / "Thing.java").write_text("".join(f"line {i}\n" for i in range(1, 21)))
    run = lambda *a: subprocess.run(["git", "-C", str(r), *a], check=True, capture_output=True)
    run("init", "-q")
    run("-c", "user.email=t@t", "-c", "user.name=t", "add", ".")
    run("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "x")
    run("tag", "1.0")
    return r


@pytest.fixture
def skill(tmp_path):
    s = tmp_path / "ig-publisher"
    tools = s / "resources" / "sources" / "tools"
    tools.mkdir(parents=True)
    (tools / "CodeSystem-ig-parameters.json").write_text(json.dumps({"concept": [{"code": "path-binary"}]}))
    (tools / "notes.txt").write_text("a\nb\nc\n")
    (s / "resources" / "SOURCES.md").write_text(SOURCES)
    return s


def run_lint(skill, repo, body, sources="GIT-1.0, TOOLS-9.9.9", capsys=None, extra=()):
    (skill / "resources" / "topic.md").write_text(HEADER.format(sources=sources) + body)
    args = ["--skill-dir", str(skill), "--cql-lint", str(CQL_LINT), *extra]
    if repo is not None:
        args += ["--repo", f"GIT-1.0={repo}"]
    code = L.main(args)
    out = capsys.readouterr().out if capsys else ""
    return code, out


@needs_cql_lint
def test_clean_skill_passes(skill, repo, capsys):
    body = ("Git [src: GIT-1.0 src/deep/Thing.java:3-5], elided [src: GIT-1.0 src/…/Thing.java:20].\n\n"
            "Code [src: TOOLS-9.9.9 CodeSystem-ig-parameters.json#path-binary], "
            "lines [src: TOOLS-9.9.9 notes.txt#L1-L3].\n")
    code, out = run_lint(skill, repo, body, capsys=capsys)
    assert code == 0, out
    assert "0 errors" in out


@needs_cql_lint
@pytest.mark.parametrize("body, rule", [
    ("[src: GIT-1.0 src/deep/Thing.java:19-21] [src: TOOLS-9.9.9 notes.txt]\n", "G1"),   # past the end
    ("[src: GIT-1.0 src/deep/Thing.java:5-3] [src: TOOLS-9.9.9 notes.txt]\n", "G1"),     # reversed
    ("[src: GIT-1.0 src/deep/Missing.java:1] [src: TOOLS-9.9.9 notes.txt]\n", "G1"),     # no such file
    ("[src: GIT-1.0 src/deep/Thing.java] [src: TOOLS-9.9.9 notes.txt]\n", "G1"),         # no line
    ("[src: GIT-1.0 src/deep/Thing.java:1] [src: TOOLS-9.9.9 notes.txt#L2-L4]\n", "L1"), # past the end
    ("[src: GIT-1.0 src/deep/Thing.java:1] [src: TOOLS-9.9.9 CodeSystem-ig-parameters.json#path-nope]\n", "T1"),
    ("[src: GIT-1.0 src/deep/Thing.java:1] [src: TOOLS-9.9.9 gone.txt]\n", "C7"),        # generic check, imported
])
def test_rule_violations(skill, repo, capsys, body, rule):
    code, out = run_lint(skill, repo, body, capsys=capsys)
    assert code == 1
    assert f" {rule} " in out, out


@needs_cql_lint
@pytest.mark.parametrize("missing", [
    "/no/such/checkout",        # macOS / Linux
    "C:\\no\\such\\checkout",   # Windows, backslash
    "C:/no/such/checkout",      # Windows, forward slash
])
def test_missing_checkout_reports_g0(skill, capsys, missing):
    code, out = run_lint(skill, None, "[src: GIT-1.0 src/deep/Thing.java:1] [src: TOOLS-9.9.9 notes.txt]\n",
                         capsys=capsys, extra=["--repo", f"GIT-1.0={missing}"])
    assert code == 1
    assert " G0 " in out


@needs_cql_lint
def test_header_rules_come_from_cql_lint(skill, repo, capsys):
    # TOOLS-9.9.9 is cited but not listed: H3 belongs to the imported generic checks.
    code, out = run_lint(skill, repo, "[src: GIT-1.0 src/deep/Thing.java:1] [src: TOOLS-9.9.9 notes.txt]\n",
                         sources="GIT-1.0", capsys=capsys)
    assert code == 1
    assert " H3 " in out


def test_load_cql_lint_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        L.load_cql_lint(tmp_path / "nope.py")
