"""Tests for gen_ig_parameters.py. Run: python3 -m pytest -q scripts/test_gen_ig_parameters.py"""

import json
import textwrap
from pathlib import Path

import pytest

import gen_ig_parameters as G

LOADER = textwrap.dedent("""\
    class X {
      void f() {
          String pc = p.getCode().getCode();
          if (pc == null) {
            throw new Error();
          } else switch (pc) {
            case "logging":
              break;
            case "pin-canonicals":
              switch (p.getValue()) {
                case "pin-all":
                  break;
              }
              break;
            case "path-binary":
              break;
            default:
              if (pc.startsWith("wantGen-")) {
              }
          }
      }
    }
    """)

XSLT = textwrap.dedent("""\
    <xsl:stylesheet>
      <xsl:template name="addParameters">
        <xsl:call-template name="setParameter">
          <xsl:with-param name="code" select="'path-resource'"/>
          <xsl:with-param name="value" select="'input/resources'"/>
          <xsl:with-param name="supplement" select="'Y'"/>
        </xsl:call-template>
        <xsl:call-template name="setParameter">
          <xsl:with-param name="code" select="'path-qa'"/>
          <xsl:with-param name="value" select="'temp/qa'"/>
        </xsl:call-template>
      </xsl:template>
      <xsl:template name="other">
        <xsl:call-template name="setParameter">
          <xsl:with-param name="code" select="'not-a-default'"/>
        </xsl:call-template>
      </xsl:template>
    </xsl:stylesheet>
    """)

CONFIG = '{\n  "script": "x",\n  "template-parameters": ["releaselabel", "made-up"]\n}\n'


def test_loader_cases_top_level_only():
    cases, start, end = G.loader_cases(LOADER)
    assert cases == {"logging": 7, "pin-canonicals": 9, "path-binary": 15}  # not the nested "pin-all"
    assert (start, end) == (6, 18)


def test_loader_cases_without_switch():
    with pytest.raises(ValueError):
        G.loader_cases("class X {}")


@pytest.mark.parametrize("code, line", [
    ("logging", 7),
    ("wantGen-json", 18),   # handled by the default branch's prefix test
    ("nope", None),
])
def test_publisher_reads(code, line):
    cases, _, end = G.loader_cases(LOADER)
    assert G.publisher_reads(code, cases, end) == line


def test_template_parameters():
    assert G.template_parameters(CONFIG) == {"releaselabel": 3, "made-up": 3}


def test_template_defaults_only_in_add_parameters():
    d = G.template_defaults(XSLT)
    assert d == {"path-resource": [("input/resources", True, 4)], "path-qa": [("temp/qa", False, 9)]}


@pytest.mark.parametrize("select, value", [
    ("'input/cql'", "input/cql"),
    ("concat(a, 'b')", "concat(a, 'b')"),
    ("'", "'"),
])
def test_unquote(select, value):
    assert G.unquote(select) == value


def test_render_layers_and_findings():
    cs = {"url": "http://hl7.org/fhir/tools/CodeSystem/ig-parameters", "version": "9",
          "concept": [{"code": "logging", "display": "a|b", "definition": "Kinds of log.\n* ```init```"},
                      {"code": "releaselabel", "display": "r", "definition": "Label."},
                      {"code": "path-qa", "display": "q", "definition": "QA."}]}
    cases, a, b = G.loader_cases(LOADER)
    out = G.render(cs, cases, (a, b), G.template_parameters(CONFIG), G.template_defaults(XSLT))
    assert "| `logging` | a\\|b | yes [src: IGPUB-3.0.4 " in out
    assert "| `releaselabel` | r | no | yes [src: TPL-BASE-1.0.0 config.json#L3] | none |" in out
    assert "`temp/qa` (only if unset) [src: TPL-BASE-1.0.0 scripts/onLoad.xslt#L9]" in out
    # findings: read but undefined; template-only codes and defaults not in the CodeSystem
    assert "| `path-binary` | [src: IGPUB-3.0.4 " in out
    assert "| `made-up` | template parameter" in out
    assert "| `path-resource` | default `input/resources`" in out
    # definitions are verbatim, inside a fence
    assert "```text\nKinds of log.\n* ```init```\n```" in out


CACHE = G.CACHE_DIR / "fhir-ig-publisher.git"
SOURCES = Path(G.__file__).resolve().parent.parent / "resources" / "sources" / "tools-1.3.0"


@pytest.mark.skipif(not (CACHE.exists() and SOURCES.exists()), reason="run scripts/fetch-sources.sh first")
def test_generated_file_is_up_to_date():
    assert G.main(["--check"]) == 0
