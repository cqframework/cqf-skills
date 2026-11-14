"""Tests for grade_library.py: the reference Library, and mutations that must each fail."""
import base64
import copy
import json
from pathlib import Path

import pytest

import grade_library as g

REFERENCE = Path(__file__).resolve().parent / "reference" / "Library-DiabetesScreening.json"


@pytest.fixture(scope="module")
def reference():
    return json.loads(REFERENCE.read_text(encoding="utf-8"))


def failures(library):
    return [msg for ok, msg in g.grade(library) if not ok]


def test_reference_passes(reference):
    assert failures(reference) == []


def test_reference_content_matches_cql_file(reference):
    cql = (REFERENCE.parent / "DiabetesScreening.cql").read_text(encoding="utf-8")
    assert base64.b64decode(reference["content"][0]["data"]).decode("utf-8") == cql


def _param(lib, name):
    return next(p for p in lib["parameter"] if p["name"] == name)


def _drop_dep(prefix):
    def mutate(lib):
        lib["relatedArtifact"] = [r for r in lib["relatedArtifact"]
                                  if not r["resource"].startswith(prefix)]
    return mutate


def _url_without_library_segment(lib):
    lib["url"] = "http://example.org/fhir/DiabetesScreening"


def _name_with_underscore(lib):
    lib["name"] = "Diabetes_Screening"


def _two_cql_contents(lib):
    lib["content"].append(dict(lib["content"][0]))


def _elm_only(lib):
    lib["content"] = [{"contentType": "application/elm+json", "data": "e30="}]


def _cql_not_base64(lib):
    lib["content"][0]["data"] = "library DiabetesScreening version '1.0.0'"


def _list_result_single(lib):
    _param(lib, "HbA1c Results")["max"] = "1"


def _period_as_string(lib):
    _param(lib, "Measurement Period")["type"] = "string"


def _boolean_as_input(lib):
    _param(lib, "Has Diabetes")["use"] = "in"


def _invented_output(lib):
    lib["parameter"].append({"name": "Diabetes Count", "use": "out", "min": 0, "max": "1",
                             "type": "integer"})


def _value_set_as_code(lib):
    cond = next(d for d in lib["dataRequirement"] if d["type"] == "Condition")
    cond["codeFilter"] = [{"path": "code", "code": [{"system": "http://example.org", "code": "x"}]}]


def _no_observation_requirement(lib):
    lib["dataRequirement"] = [d for d in lib["dataRequirement"] if d["type"] != "Observation"]


def _wrong_library_type(lib):
    lib["type"]["coding"][0]["code"] = "module-definition"


def _helpers_unversioned(lib):
    for r in lib["relatedArtifact"]:
        if "FHIRHelpers" in r["resource"]:
            r["resource"] = r["resource"].split("|")[0]


@pytest.mark.parametrize("mutate, expected", [
    (_url_without_library_segment, "url is"),
    (_name_with_underscore, "name is"),
    (_two_cql_contents, "exactly one text/cql"),
    (_elm_only, "exactly one text/cql"),
    (_cql_not_base64, "base64 of the given CQL"),
    (_drop_dep("http://hl7.org/fhir/uv/cql/Library/FHIR-ModelInfo"), "FHIR ModelInfo"),
    (_drop_dep("http://hl7.org/fhir/uv/cql/Library/FHIRHelpers"), "FHIRHelpers"),
    (_helpers_unversioned, "FHIRHelpers"),
    (_drop_dep("http://loinc.org"), "LOINC code system"),
    (_drop_dep("http://example.org/fhir/ValueSet"), "Diabetes value set"),
    (_list_result_single, "HbA1c Results is Observation, max *"),
    (_period_as_string, "Measurement Period is a Period"),
    (_boolean_as_input, "Has Diabetes is a boolean"),
    (_invented_output, "no output parameters"),
    (_value_set_as_code, "Diabetes value set (4.4)"),
    (_no_observation_requirement, "LOINC 4548-4"),
    (_wrong_library_type, "logic-library"),
])
def test_mutation_fails(reference, mutate, expected):
    lib = copy.deepcopy(reference)
    mutate(lib)
    msgs = failures(lib)
    assert any(expected in m for m in msgs), msgs


def test_older_canonical_form_passes(reference):
    lib = copy.deepcopy(reference)
    for r in lib["relatedArtifact"]:
        r["resource"] = r["resource"].replace("http://hl7.org/fhir/uv/cql/Library/",
                                              "http://hl7.org/fhir/Library/")
    assert failures(lib) == []


def test_not_a_library():
    assert failures({"resourceType": "Measure"}) == ["resourceType is Library"]
