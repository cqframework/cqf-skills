"""Tests for build-ig.py, on a small synthetic package and pages in the shape of the real IG."""
import base64
import importlib.util
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("build_ig", HERE / "build-ig.py")
bi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bi)

MODELINFO = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<modelInfo name="USQualityCore" version="0.5.0" url="http://fhir.org/guides/onc/us-quality-core" targetUrl="http://hl7.org/fhir"
  targetQualifier="usqualitycore" patientClassName="Patient" patientBirthDatePropertyName="birthDate"
  xmlns="urn:hl7-org:elm-modelinfo:r1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <requiredModelInfo name="System" version="1.0.0"/>
  <requiredModelInfo name="FHIR" version="4.0.1"/>
  <requiredModelInfo name="USCore" version="6.1.0-derived"/>
  <typeInfo xsi:type="ClassInfo" namespace="USQualityCore" name="Encounter" identifier="http://fhir.org/guides/onc/us-quality-core/StructureDefinition/us-quality-core-encounter" label="US Quality Core Encounter" retrievable="true" primaryCodePath="type" baseType="USCore.EncounterProfile">
    <element name="type"><elementTypeSpecifier xsi:type="ListTypeSpecifier" elementType="FHIR.CodeableConcept"/></element>
    <element name="diagnosis"><elementTypeSpecifier xsi:type="ListTypeSpecifier" elementType="USQualityCore.Encounter.Diagnosis"/></element>
  </typeInfo>
  <typeInfo xsi:type="ClassInfo" namespace="USQualityCore" name="Encounter.Diagnosis" retrievable="false" baseType="FHIR.BackboneElement">
    <element name="rank" elementType="FHIR.positiveInt"/>
  </typeInfo>
  <typeInfo xsi:type="ClassInfo" namespace="USQualityCore" name="Patient" label="US Quality Core Patient" retrievable="true" baseType="USCore.PatientProfile"/>
  <contextInfo name="Patient" keyElement="id" birthDateElement="birthDate">
    <contextType namespace="USQualityCore" name="Patient"/>
  </contextInfo>
</modelInfo>
"""


def _library(lib_id, version, content_type, text, deps=()):
    return {"resourceType": "Library", "id": lib_id, "version": version,
            "url": f"http://fhir.org/guides/onc/us-quality-core/Library/{lib_id}",
            "relatedArtifact": [{"type": "depends-on", "resource": d} for d in deps],
            "content": [{"contentType": content_type,
                         "data": base64.b64encode(text.encode("utf-8")).decode("ascii")}]}


@pytest.fixture
def package():
    pkg = {f"Library-{n}.json": _library(n, "0.5.0", "text/cql", f"library {n}\r\n")
           for n in bi.LIBRARIES}
    pkg["Library-USQualityCoreCommon.json"]["relatedArtifact"] = [
        {"type": "depends-on", "resource": "http://hl7.org/fhir/uv/cql/Library/FHIRCommon|2.0.0"}]
    pkg[f"Library-{bi.MODELINFO_LIBRARY}.json"] = _library(bi.MODELINFO_LIBRARY, "0.5.0",
                                                           "application/xml", MODELINFO)
    return pkg


@pytest.fixture
def pages():
    out = {name: f"### {title}\n\nText.\n" for name, title in bi.PAGES}
    out["modelinfo.md"] = """{% include cql-informational-notice.md %}

### Using the model

See [Must Support]({{site.data.fhir.ver.uscore}}/must-support.html),
[the model](Library-USQualityCore-ModelInfo.html), [common](Library-USQualityCoreCommon.html),
[negation](negation.html#negation-in-cql), [here](modelinfo.html#using-the-model) and
[a profile](StructureDefinition-us-quality-core-encounter.html).

{% lang-fragment table-profiles.xhtml %}
{% include img-portrait.html img="x.png" caption="X" %}

<ul>
    <li>
        [US Quality Core Encounter](StructureDefinition-us-quality-core-encounter.html)
    </li>
    <li>
        <a href="profiles.html">Profiles</a>
    </li>
</ul>
"""
    return out


@pytest.fixture
def includes():
    return {"cql-informational-notice.md": "> The CQL content here is informational.\n"}


@pytest.fixture
def built(package, pages, includes):
    return bi.build(package, pages, includes)


def test_includes_inlined_and_markup_removed(built):
    page = built["pages/modelinfo.md"]
    assert "> The CQL content here is informational." in page
    for leftover in ("{%", "{{", "<li", "<ul", "<a "):
        assert leftover not in page, leftover
    assert "generated table here: table-profiles.xhtml" in page
    assert ("- [US Quality Core Encounter]"
            f"({bi.PUBLISHED}StructureDefinition-us-quality-core-encounter.html)\n"
            "- [Profiles](profiles.md)") in page


def test_page_links(built):
    page = built["pages/modelinfo.md"]
    assert "[Must Support](http://hl7.org/fhir/us/core/STU6.1/must-support.html)" in page
    assert "[the model](../modelinfo/README.md)" in page
    assert "[common](../libraries/USQualityCoreCommon.cql)" in page
    assert "[negation](negation.md#negation-in-cql)" in page
    assert "[here](#using-the-model)" in page


def test_page_index(built):
    for name, title in bi.PAGES:
        assert f"| [{name}]({name}) | {title} |" in built["pages/README.md"]


def test_libraries(built):
    assert built["libraries/USQualityCoreCommon.cql"] == "library USQualityCoreCommon\n"
    assert ("| [USQualityCoreCommon.cql](USQualityCoreCommon.cql) | "
            "`http://fhir.org/guides/onc/us-quality-core/Library/USQualityCoreCommon` | 0.5.0 | "
            "FHIRCommon|2.0.0 |") in built["libraries/README.md"]


def test_modelinfo(built):
    index = built["modelinfo/README.md"]
    assert "using USQualityCore version '0.5.0'" in index
    assert "**Requires:** System 1.0.0, FHIR 4.0.1, USCore 6.1.0-derived." in index
    assert "Declare `using FHIR` too" in index
    assert ("| [Encounter](classes/Encounter.md) | US Quality Core Encounter | "
            "`USCore.EncounterProfile` | yes | `type` |") in index
    enc = built["modelinfo/classes/Encounter.md"]
    assert "## USQualityCore.Encounter.Diagnosis" in enc
    assert "| type | `List<FHIR.CodeableConcept>` |" in enc


def test_committed_indexes_match_files():
    res = HERE.parent / "resources"
    for folder, pattern in (("pages", "*.md"), ("libraries", "*.cql")):
        listed = set()
        for line in (res / folder / "README.md").read_text(encoding="utf-8").splitlines():
            if line.startswith("| ["):
                listed.add(line.split("](")[1].split(")")[0])
        assert listed == {p.name for p in (res / folder).glob(pattern)} - {"README.md"}, folder
    classes = {p.stem for p in (res / "modelinfo" / "classes").glob("*.md")}
    index = (res / "modelinfo" / "README.md").read_text(encoding="utf-8")
    assert all(f"(classes/{c}.md)" in index for c in classes)
