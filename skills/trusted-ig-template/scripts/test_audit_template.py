"""Tests for audit_template.py: a clean template passes, and each broken rule is reported."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_template as A  # noqa: E402

ANT = """<project name="template" default="onGenerate">
  <import file="${ig.scripts}/common.xml"/>
  <property name="dir.includes" value="${ig.temp}/_includes"/>
  <macrodef name="fetch">
    <attribute name="file"/>
    <sequential>
      <get src="https://hl7.org/fhir/R4/@{file}" dest="${ig.template}/schemas" ignoreerrors="true"/>
    </sequential>
  </macrodef>
  <target name="schemas" unless="${ig.networkprohibited}">
    <fetch file="fhir-single.xsd"/>
  </target>
  <target name="versions">
    <xslt in="${onGenerate.ig.source}xml" out="${ig.template}/versions.txt" style="${ig.scripts}/versions.xslt"/>
    <loadproperties srcfile="${ig.template}/versions.txt"/>
    <loadfile property="groupings" srcFile="${ig.scripts}/groupings.txt"/>
  </target>
  <target name="diagrams">
    <java jar="${ig.scripts}/tool.jar" fork="true">
      <arg line="-o ${dir.includes}"/>
    </java>
  </target>
  <target name="onGenerate" depends="schemas,versions,diagrams"/>
  <scriptdef name="append" language="javascript">
    <attribute name="files"/>
    self.project.setProperty("onGenerate.files", self.project.getProperty("onGenerate.files").concat(";").concat(attributes.get("files")));
  </scriptdef>
</project>
"""
COMMON = '<project name="common"><target name="noop"/></project>\n'
VERSIONS = """<xsl:stylesheet version="1.0" xmlns:f="http://hl7.org/fhir" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text"/>
  <xsl:template match="f:ImplementationGuide">
    <xsl:value-of select="concat('igVersion=', normalize-space(f:version/@value), '&#xa;')"/>
  </xsl:template>
</xsl:stylesheet>
"""
PAGES = """<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="@*|node()"><xsl:copy><xsl:apply-templates select="@*|node()"/></xsl:copy></xsl:template>
</xsl:stylesheet>
"""
CONFIG = {
    "script": "scripts/ant.xml",
    "otherScripts": ["scripts/common.xml"],
    "targets": {"onGenerate": "onGenerate"},
    "pre-process": [{"folder": "input/pages", "relativePath": "_includes",
                     "transform": "template/scripts/pages.xslt"}],
}


def template(tmp_path: Path, **override) -> Path:
    files = {
        "config.json": json.dumps(CONFIG),
        "scripts/ant.xml": ANT,
        "scripts/common.xml": COMMON,
        "scripts/versions.xslt": VERSIONS,
        "scripts/pages.xslt": PAGES,
        "scripts/groupings.txt": "a=b\n",
        "content/assets/css/site.css": "body {}\n",
        "includes/header.html": "<div/>\n",
    }
    files.update(override)
    root = tmp_path / "t"
    for rel, text in files.items():
        if text is None:
            continue
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return root


def codes(root: Path, level="ERROR") -> set[str]:
    return {f.code for f in A.audit(root) if f.level == level}


def test_clean_template(tmp_path):
    findings = A.audit(template(tmp_path))
    assert [str(f) for f in findings if f.level == "ERROR"] == []


def test_missing_other_scripts(tmp_path):
    cfg = dict(CONFIG)
    del cfg["otherScripts"]
    assert {"A01", "A02"} <= codes(template(tmp_path, **{"config.json": json.dumps(cfg)}))


def test_unregistered_ant_file(tmp_path):
    assert codes(template(tmp_path, **{"scripts/extra.xml": COMMON})) == {"A02"}


def test_ant_file_outside_scripts(tmp_path):
    cfg = dict(CONFIG, otherScripts=["scripts/common.xml", "includes/more.xml"])
    root = template(tmp_path, **{"config.json": json.dumps(cfg), "includes/more.xml": COMMON})
    assert codes(root) == {"A02"}


def test_stylesheet_named_xml(tmp_path):
    ant = ANT.replace("${ig.scripts}/versions.xslt", "${ig.scripts}/versions.xml")
    root = template(tmp_path, **{"scripts/ant.xml": ant, "scripts/versions.xml": VERSIONS})
    assert "A03" in codes(root)


def test_relative_style(tmp_path):
    ant = ANT.replace('style="${ig.scripts}/versions.xslt"', 'style="scripts/versions.xslt"')
    assert "A04" in codes(template(tmp_path, **{"scripts/ant.xml": ant}))


def test_mistyped_property(tmp_path):
    ant = ANT.replace('style="${ig.scripts}/versions.xslt"', 'style="{$ig.scripts}/versions.xslt"')
    assert "A04" in codes(template(tmp_path, **{"scripts/ant.xml": ant}))


def test_data_file_outside_scripts(tmp_path):
    ant = ANT.replace('<loadfile property="groupings" srcFile="${ig.scripts}/groupings.txt"/>',
                      '<loadproperties srcfile="${ig.template}/data/settings.txt"/>')
    root = template(tmp_path, **{"scripts/ant.xml": ant})
    assert any(f.code == "A06" and f.level == "WARN" for f in A.audit(root))


def test_import_from_includes(tmp_path):
    ant = ANT.replace('file="${ig.scripts}/common.xml"', 'file="${ig.template}/includes/common.xml"')
    assert "A04" in codes(template(tmp_path, **{"scripts/ant.xml": ant}))


def test_argument_from_unknown_property(tmp_path):
    ant = ANT.replace('-o ${dir.includes}', '-o ${dir.includes} ${igVersion}')
    assert codes(template(tmp_path, **{"scripts/ant.xml": ant})) == {"A05"}


def test_properties_from_raw_ig_value(tmp_path):
    raw = VERSIONS.replace("normalize-space(f:version/@value)", "f:version/@value")
    assert codes(template(tmp_path, **{"scripts/versions.xslt": raw})) == {"A06"}


def test_inline_eval(tmp_path):
    ant = ANT.replace('self.project.setProperty(', 'eval(self.project.getProperty("x")); self.project.setProperty(')
    assert codes(template(tmp_path, **{"scripts/ant.xml": ant})) == {"A07"}


def test_preprocess_transform_outside_scripts(tmp_path):
    cfg = json.loads(json.dumps(CONFIG))
    cfg["pre-process"][0]["transform"] = "template/includes/pages.xslt"
    assert "A08" in codes(template(tmp_path, **{"config.json": json.dumps(cfg)}))


def test_preprocess_transform_with_include(tmp_path):
    pages = PAGES.replace('<xsl:template', '<xsl:include href="versions.xslt"/><xsl:template', 1)
    assert codes(template(tmp_path, **{"scripts/pages.xslt": pages})) == {"A08"}


def test_jekyll_plugin(tmp_path):
    root = template(tmp_path, **{"content/_plugins/x.rb": "puts 1\n", "Gemfile": "gem 'x'\n"})
    assert codes(root) == {"A09"}


def test_jekyll_config_plugins(tmp_path):
    root = template(tmp_path, **{"content/_config.yml": "title: x\nplugins:\n  - jekyll-x\n"})
    assert codes(root) == {"A09"}


def test_get_not_gated(tmp_path):
    ant = ANT.replace('<target name="schemas" unless="${ig.networkprohibited}">', '<target name="schemas">')
    assert codes(template(tmp_path, **{"scripts/ant.xml": ant})) == {"A10"}


def test_get_gated_by_name(tmp_path):
    ant = ANT.replace('unless="${ig.networkprohibited}"', 'unless="ig.networkprohibited"')
    assert codes(template(tmp_path, **{"scripts/ant.xml": ant})) == {"A10"}


def test_get_url_from_property(tmp_path):
    ant = ANT.replace("https://hl7.org/fhir/R4/@{file}", "${igCanonical}/@{file}")
    assert codes(template(tmp_path, **{"scripts/ant.xml": ant})) == {"A10"}


def test_extension_namespace(tmp_path):
    ext = VERSIONS.replace('xmlns:f=', 'xmlns:j="http://xml.apache.org/xalan/java" xmlns:f=')
    assert codes(template(tmp_path, **{"scripts/versions.xslt": ext})) == {"A11"}


def test_result_document(tmp_path):
    rd = PAGES.replace("<xsl:copy>", '<xsl:result-document href="x"/><xsl:copy>')
    assert "A11" in codes(template(tmp_path, **{"scripts/pages.xslt": rd}))


def test_main_exit_status(tmp_path, capsys):
    assert A.main([str(template(tmp_path))]) == 0
    assert A.main([str(template(tmp_path / "b", **{"Gemfile": "x"}))]) == 1


def warn_codes(root: Path) -> set[str]:
    return codes(root, level="WARN")


def test_path_from_ig_value(tmp_path):
    ant = ANT.replace('<target name="diagrams">',
                      '<target name="langs"><copy todir="${ig.temp}/_includes/${lang}"><fileset dir="${ig.template}/includes"/></copy></target>\n'
                      '  <target name="diagrams">')
    assert codes(template(tmp_path, **{"scripts/ant.xml": ant})) == {"A12"}


def test_publisher_target_properties_are_fixed(tmp_path):
    # <target>.ig.source and .ig.dest come from the publisher, so a path built from them is fine
    assert "A12" not in codes(template(tmp_path))


def test_echo_of_ig_value(tmp_path):
    ant = ANT.replace('<target name="diagrams">',
                      '<target name="stamp"><echo file="${ig.temp}/_includes/stamp.html" message="${igVersion}"/></target>\n'
                      '  <target name="diagrams">')
    root = template(tmp_path, **{"scripts/ant.xml": ant})
    assert "A12" in warn_codes(root) and "A12" not in codes(root)


def test_liquid_dynamic_include(tmp_path):
    root = template(tmp_path, **{"includes/menu.html": "{% include {{ page.menu }} %}\n"})
    assert codes(root) == {"A13"}


def test_liquid_value_in_script(tmp_path):
    root = template(tmp_path, **{"layouts/default.html": "<script>var t = {{ site.data.ig.title | jsonify }};</script>\n"})
    assert codes(root) == {"A13"}


def test_liquid_unescaped_value(tmp_path):
    root = template(tmp_path, **{"layouts/default.html": "<h1>{{ site.data.ig.title }}</h1>\n<p>{{ page.x }}</p>\n"})
    findings = [f for f in A.audit(root) if f.code == "A13"]
    assert [f.level for f in findings] == ["WARN"] and "2 value(s)" in findings[0].message


def test_liquid_escaped_and_commented(tmp_path):
    html = ('<h1>{{ site.data.ig.title | escape }}</h1>\n<a href="{{ page.id | url_encode }}.html">x</a>\n'
            '{{ content }} <!-- publisher HTML -->\n')
    assert "A13" not in codes(template(tmp_path, **{"layouts/default.html": html})) | warn_codes(
        template(tmp_path / "b", **{"layouts/default.html": html}))


def test_liquid_publisher_placeholders_and_include_parameters(tmp_path):
    html = ("{% include fragment-intro.html type='{{[type]}}' id='{{[id]}}' %}\n"
            "{% include {{[id]}}-summary.xhtml %}\n")
    assert "A13" not in codes(template(tmp_path, **{"layouts/layout-profile.html": html}))
