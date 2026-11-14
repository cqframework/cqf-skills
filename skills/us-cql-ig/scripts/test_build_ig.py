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
<modelInfo name="USCore" version="6.1.0-derived" url="http://hl7.org/fhir/us/core" targetUrl="http://hl7.org/fhir"
  targetQualifier="uscore" patientClassName="PatientProfile" patientBirthDatePropertyName="birthDate"
  xmlns="urn:hl7-org:elm-modelinfo:r1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <requiredModelInfo name="System" version="1.0.0"/>
  <requiredModelInfo name="FHIR" version="4.0.1"/>
  <typeInfo xsi:type="ClassInfo" namespace="USCore" name="PatientProfile" identifier="http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient" label="Patient Profile" target="Patient" retrievable="true" baseType="FHIR.Patient">
    <element name="identifier"><elementTypeSpecifier xsi:type="ListTypeSpecifier" elementType="FHIR.Identifier"/></element>
    <element name="deceased"><elementTypeSpecifier xsi:type="ChoiceTypeSpecifier">
      <choice xsi:type="NamedTypeSpecifier" namespace="FHIR" name="boolean"/>
      <choice xsi:type="NamedTypeSpecifier" namespace="FHIR" name="dateTime"/></elementTypeSpecifier></element>
  </typeInfo>
  <typeInfo xsi:type="ClassInfo" namespace="USCore" name="BloodPressureProfile" label="Blood Pressure Profile" retrievable="true" baseType="USCore.VitalSignsProfile">
    <element name="component"><elementTypeSpecifier xsi:type="ListTypeSpecifier" elementType="USCore.BloodPressureProfile.Component"/></element>
  </typeInfo>
  <typeInfo xsi:type="ClassInfo" namespace="USCore" name="BloodPressureProfile.Component" retrievable="false" baseType="FHIR.BackboneElement">
    <element name="code" elementType="FHIR.CodeableConcept"/>
  </typeInfo>
  <typeInfo xsi:type="ClassInfo" namespace="USCore" name="VitalSignsProfile" label="Vital Signs Profile" retrievable="true" primaryCodePath="code" baseType="FHIR.Observation"/>
  <contextInfo name="Patient" keyElement="id" birthDateElement="birthDate">
    <contextType namespace="USCore" name="PatientProfile"/>
  </contextInfo>
</modelInfo>
"""


def _library(lib_id, version, content_type, text):
    return {"resourceType": "Library", "id": lib_id, "version": version,
            "url": f"http://hl7.org/fhir/us/cql/Library/{lib_id}",
            "relatedArtifact": [],
            "content": [{"contentType": content_type,
                         "data": base64.b64encode(text.encode("utf-8")).decode("ascii")}]}


@pytest.fixture
def package():
    pkg = {f"Library-{n}.json": _library(n, "2.0.0", "text/cql", f"library {n}\r\n")
           for n in bi.LIBRARIES}
    pkg["Library-USCoreElements.json"]["relatedArtifact"] = [
        {"type": "depends-on", "resource": "http://hl7.org/fhir/us/cql/Library/USCoreCommon|2.0.0"}]
    pkg["Library-USCore-ModelInfo.json"] = _library("USCore-ModelInfo", "6.1.0-derived",
                                                    "application/xml", MODELINFO)
    for m in bi.OTHER_MODELINFO:
        pkg[f"Library-{m}.json"] = _library(m, "1.0.0-derived", "application/xml", "<x/>")
    return pkg


@pytest.fixture
def pages():
    out = {name: f"### {title}\n\nText.\n" for name, title in bi.PAGES}
    out["patterns-patient.md"] = """{% include img.html img="x.png" caption="X" %}

### Patient sex

See [sex]({{site.data.fhir.ver.uscore6}}/StructureDefinition-us-core-sex.html),
[using CQL]({{site.data.fhir.ver.cql}}/using-cql.html), [elements](Library-USCoreElements.html),
[the model](Library-USCore-ModelInfo.html), [overall](patterns-overall.html#accessing-data),
[here](patterns-patient.html#patient-sex), [manifest](Library-PriorAuthManifestExample.html) and
<a href="usage.html">usage</a>.

{% include globals-table-en.xhtml %}
"""
    return out


@pytest.fixture
def built(package, pages):
    return bi.build(package, pages)


def test_page_markup_and_links(built):
    page = built["pages/patterns-patient.md"]
    for leftover in ("{%", "{{", "<a "):
        assert leftover not in page, leftover
    assert "[sex](http://hl7.org/fhir/us/core/STU6.1/StructureDefinition-us-core-sex.html)" in page
    assert "[using CQL](http://hl7.org/fhir/uv/cql/STU2/using-cql.html)" in page
    assert "[elements](../libraries/USCoreElements.cql)" in page
    assert "[the model](../modelinfo/README.md)" in page
    assert "[overall](patterns-overall.md#accessing-data)" in page
    assert "[here](#patient-sex)" in page
    assert f"[manifest]({bi.PUBLISHED}Library-PriorAuthManifestExample.html)" in page
    assert "[usage](usage.md)" in page
    assert "generated table here: globals-table-en.xhtml" in page


def test_page_index(built):
    index = built["pages/README.md"]
    for name, title in bi.PAGES:
        assert f"| [{name}]({name}) | {title} |" in index


def test_libraries(built):
    assert built["libraries/USCoreCommon.cql"] == "library USCoreCommon\n"
    index = built["libraries/README.md"]
    assert ("| [USCoreElements.cql](USCoreElements.cql) | "
            "`http://hl7.org/fhir/us/cql/Library/USCoreElements` | 2.0.0 | USCoreCommon|2.0.0 |") in index
    assert "| `http://hl7.org/fhir/us/cql/Library/USCore-ModelInfo` | 6.1.0-derived |" in index


def test_modelinfo(built):
    index = built["modelinfo/README.md"]
    assert "using USCore version '6.1.0-derived'" in index
    assert "**Requires:** System 1.0.0, FHIR 4.0.1." in index
    assert "| [BloodPressureProfile](classes/BloodPressureProfile.md) | Blood Pressure Profile | `USCore.VitalSignsProfile` | yes |  |" in index
    assert "| [VitalSignsProfile](classes/VitalSignsProfile.md) | Vital Signs Profile | `FHIR.Observation` | yes | `code` |" in index
    assert "modelinfo/classes/BloodPressureProfile.Component.md" not in built
    bp = built["modelinfo/classes/BloodPressureProfile.md"]
    assert "## USCore.BloodPressureProfile.Component" in bp
    patient = built["modelinfo/classes/PatientProfile.md"]
    assert "**Profile:** `http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient`" in patient
    assert "| deceased | `Choice<FHIR.boolean, FHIR.dateTime>` |" in patient


def test_content_type_with_parameters_is_read(package, pages):
    package["Library-USCoreCommon.json"]["content"][0]["contentType"] = "text/cql; version=1.5"
    assert bi.build(package, pages)["libraries/USCoreCommon.cql"] == "library USCoreCommon\n"


def test_committed_indexes_match_files():
    res = HERE.parent / "resources"
    for folder, pattern in (("pages", "*.md"), ("libraries", "*.cql")):
        listed = set()
        for line in (res / folder / "README.md").read_text(encoding="utf-8").splitlines():
            if line.startswith("| ["):
                listed.add(line.split("](")[1].split(")")[0])
        files = {p.name for p in (res / folder).glob(pattern)} - {"README.md"}
        assert listed == files, folder
    classes = {p.stem for p in (res / "modelinfo" / "classes").glob("*.md")}
    index = (res / "modelinfo" / "README.md").read_text(encoding="utf-8")
    assert all(f"(classes/{c}.md)" in index for c in classes)
