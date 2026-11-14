"""Tests for build-ig.py, on a small synthetic package and pages in the shape of the real IG."""
import base64
import importlib.util
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("build_ig", HERE / "build-ig.py")
bi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bi)

MODELINFO = """<?xml version="1.0" encoding="UTF-8"?>
<modelInfo xmlns="urn:hl7-org:elm-modelinfo:r1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  name="FHIR" version="4.0.1" url="http://hl7.org/fhir" targetQualifier="fhir"
  patientClassName="FHIR.Patient" patientBirthDatePropertyName="birthDate.value">
  <typeInfo baseType="System.Any" namespace="FHIR" name="Resource" retrievable="false" xsi:type="ClassInfo"/>
  <typeInfo baseType="FHIR.Resource" namespace="FHIR" name="DomainResource" retrievable="false" xsi:type="ClassInfo"/>
  <typeInfo baseType="FHIR.Element" namespace="FHIR" name="boolean" retrievable="false" xsi:type="ClassInfo">
    <element name="value" elementType="System.Boolean"/>
  </typeInfo>
  <typeInfo baseType="FHIR.Element" namespace="FHIR" name="ObservationStatus" retrievable="false" xsi:type="ClassInfo">
    <element name="value" elementType="System.String"/>
  </typeInfo>
  <typeInfo baseType="FHIR.Element" namespace="FHIR" name="Period" retrievable="false" xsi:type="ClassInfo">
    <element name="start" elementType="FHIR.dateTime"/>
  </typeInfo>
  <typeInfo baseType="FHIR.DomainResource" namespace="FHIR" name="Observation" identifier="http://hl7.org/fhir/StructureDefinition/Observation" retrievable="true" primaryCodePath="code" xsi:type="ClassInfo">
    <element name="status" elementType="FHIR.ObservationStatus"/>
    <element name="category">
      <elementTypeSpecifier elementType="FHIR.CodeableConcept" xsi:type="ListTypeSpecifier"/>
    </element>
    <element name="effective">
      <elementTypeSpecifier xsi:type="ChoiceTypeSpecifier">
        <choice namespace="FHIR" name="dateTime" xsi:type="NamedTypeSpecifier"/>
        <choice namespace="FHIR" name="Period" xsi:type="NamedTypeSpecifier"/>
      </elementTypeSpecifier>
    </element>
    <element name="component">
      <elementTypeSpecifier elementType="FHIR.Observation.Component" xsi:type="ListTypeSpecifier"/>
    </element>
    <contextRelationship context="Patient" relatedKeyElement="subject"/>
  </typeInfo>
  <typeInfo baseType="FHIR.BackboneElement" namespace="FHIR" name="Observation.Component" retrievable="false" xsi:type="ClassInfo">
    <element name="code" elementType="FHIR.CodeableConcept"/>
  </typeInfo>
  <conversionInfo functionName="FHIRHelpers.ToInterval" fromType="FHIR.Period" toType="Interval&lt;System.DateTime&gt;"/>
  <contextInfo name="Patient" keyElement="id" birthDateElement="birthDate.value">
    <contextType namespace="FHIR" name="Patient"/>
  </contextInfo>
</modelInfo>
"""


def _library(lib_id, version, content_type, text, deps=()):
    return {
        "resourceType": "Library", "id": lib_id, "version": version,
        "url": f"http://hl7.org/fhir/uv/cql/Library/{lib_id}",
        "relatedArtifact": [{"type": "depends-on", "resource": d} for d in deps],
        "content": [{"contentType": content_type,
                     "data": base64.b64encode(text.encode("utf-8")).decode("ascii")}],
    }


@pytest.fixture
def package():
    pkg = {f"Library-{n}.json": _library(n, "2.0.0", "text/cql", f"library {n}\r\n")
           for n in bi.LIBRARIES}
    pkg["Library-FHIRCommon.json"]["relatedArtifact"] = [
        {"type": "depends-on", "resource": "http://hl7.org/fhir/uv/cql/Library/FHIRHelpers|4.0.1"},
        {"type": "depends-on", "resource": "http://loinc.org"}]
    pkg["Library-FHIR-ModelInfo.json"] = _library("FHIR-ModelInfo", "4.0.1", "application/xml",
                                                  MODELINFO)
    return pkg


@pytest.fixture
def pages():
    out = {name: f"### {title}\n\nText.\n" for name, title in bi.PAGES}
    out["conformance.md"] = """{% include fhir-conformance.xhtml %}

### Library Resources

**Conformance Requirement 4.1 (Library Resources):** [<img src="conformance.png" width="20" class="self-link" height="20"/>](#conformance-requirement-4-1)

See [CQLLibrary](StructureDefinition-cql-library.html), [patterns](patterns.html#choices),
[FHIRHelpers](Library-FHIRHelpers.html), [the model](Library-FHIR-ModelInfo.html),
[a section](conformance.html#library-resources) and
[isSelective]({{site.data.fhir.ver.ext}}/StructureDefinition-cqf-isSelective.html).

{: .grid}
<table class="grid">
  <tr><th>Extension</th><th>FMM</th></tr>
  <tr><td><a href="{{site.data.fhir.path}}extensibility.html">Ext | one</a></td><td><a class="fmm" href="x" title="Maturity Level">1</a></td></tr>
</table>
"""
    out["fhir-modelinfo.md"] = "Classes:\n\n|---|---|\n|[Observation]({{site.data.fhir.path}}observation.html)|code|\n"
    return out


@pytest.fixture
def built(package, pages):
    return bi.build(package, pages)


def test_page_markup_removed(built):
    page = built["pages/conformance.md"]
    for leftover in ("{%", "{{", "<img", "<table", "<td", "{: .grid}"):
        assert leftover not in page, leftover
    assert "**Conformance Requirement 4.1 (Library Resources):**\n" in page
    assert "| [Ext \\| one](http://hl7.org/fhir/R4/extensibility.html) | 1 |" in page


def test_page_links(built):
    page = built["pages/conformance.md"]
    assert "[CQLLibrary](https://hl7.org/fhir/uv/cql/STU2/StructureDefinition-cql-library.html)" in page
    assert "[patterns](patterns.md#choices)" in page
    assert "[FHIRHelpers](../libraries/FHIRHelpers.cql)" in page
    assert "[the model](../modelinfo/README.md)" in page
    assert "[a section](#library-resources)" in page
    assert f"[isSelective]({bi.EXTENSIONS}/StructureDefinition-cqf-isSelective.html)" in page


def test_headerless_modelinfo_table_gets_header(built):
    assert "|Class|Primary Code Path|\n|---|---|\n|[Observation]" in built["pages/fhir-modelinfo.md"]


def test_page_index(built):
    index = built["pages/README.md"]
    for name, title in bi.PAGES:
        assert f"| [{name}]({name}) | {title} |" in index


def test_libraries(built):
    assert built["libraries/FHIRHelpers.cql"] == "library FHIRHelpers\n"
    index = built["libraries/README.md"]
    assert "| [FHIRCommon.cql](FHIRCommon.cql) | `http://hl7.org/fhir/uv/cql/Library/FHIRCommon` | 2.0.0 | FHIRHelpers|4.0.1 |" in index


def test_modelinfo_resource_file(built):
    obs = built["modelinfo/resources/Observation.md"]
    assert "# FHIR.Observation" in obs
    assert "**Primary code path:** `code`" in obs
    assert "**Context relationships:** Patient via `subject`" in obs
    assert "| category | `List<FHIR.CodeableConcept>` |" in obs
    assert "| effective | `Choice<FHIR.dateTime, FHIR.Period>` |" in obs
    assert "## FHIR.Observation.Component" in obs


def test_modelinfo_categories(built):
    assert "modelinfo/resources/Resource.md" in built
    assert "modelinfo/resources/Period.md" not in built
    assert "## FHIR.Period" in built["modelinfo/datatypes.md"]
    prims = built["modelinfo/primitives.md"]
    assert "| FHIR.boolean | `FHIR.Element` | `System.Boolean` |" in prims
    assert "| FHIR.ObservationStatus | `FHIR.Element` | `System.String` |" in prims
    assert ("| `FHIR.Period` | `Interval<System.DateTime>` | `FHIRHelpers.ToInterval` |"
            in built["modelinfo/conversions.md"])


def test_modelinfo_index(built):
    index = built["modelinfo/README.md"]
    assert "| Patient | `FHIR.Patient` | `id` | `birthDate.value` |" in index
    assert "| [Observation](resources/Observation.md) | yes | `code` | Patient |" in index


def test_missing_content_type_is_an_error(package, pages):
    package["Library-FHIRHelpers.json"]["content"][0]["contentType"] = "application/elm+json"
    with pytest.raises(SystemExit, match="FHIRHelpers has no text/cql"):
        bi.build(package, pages)


def test_committed_indexes_match_files():
    res = HERE.parent / "resources"
    for folder, pattern in (("pages", "*.md"), ("libraries", "*.cql")):
        listed = set()
        for line in (res / folder / "README.md").read_text(encoding="utf-8").splitlines():
            if line.startswith("| ["):
                listed.add(line.split("](")[1].split(")")[0])
        files = {p.name for p in (res / folder).glob(pattern)} - {"README.md"}
        assert listed == files, folder
    resources = {p.stem for p in (res / "modelinfo" / "resources").glob("*.md")}
    index = (res / "modelinfo" / "README.md").read_text(encoding="utf-8")
    assert all(f"(resources/{r}.md)" in index for r in resources)
