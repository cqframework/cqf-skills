"""Tests for grade_elm.py.

reference/ holds a correct answer and a flawed one, each with the ELM JSON that the CQL-to-ELM
translator 3.29.0 produced from it. The tests also mutate the correct ELM, one requirement at a time.
"""
import copy
import json
from pathlib import Path

import pytest

import grade_elm as g

REF = Path(__file__).resolve().parent / "reference"


def load(name):
    return json.loads((REF / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def good():
    return load("HypertensionCheck.json")


def failures(elm):
    return [msg for ok, msg in g.grade(elm) if not ok]


def test_reference_passes(good):
    assert failures(good) == []


def test_flawed_answer_fails_on_its_two_flaws():
    assert failures(load("HypertensionCheck-flawed.json")) == [
        "no terminology retrieve without a code path",
        "Active Confirmed Hypertension Problems: filters on verification status",
    ]


def defn(elm, name):
    return next(d for d in elm["library"]["statements"]["def"] if d["name"] == name)


def retrieve(elm, name):
    return next(n for n in g.walk(defn(elm, name)["expression"]) if n.get("type") == "Retrieve")


def _drop_code_path(elm):
    del retrieve(elm, "Active Confirmed Hypertension Problems")["codeProperty"]


def _plain_fhir_condition(elm):
    retrieve(elm, "Active Confirmed Hypertension Problems")["templateId"] = \
        "http://hl7.org/fhir/StructureDefinition/Condition"


def _no_active(elm):
    d = defn(elm, "Active Confirmed Hypertension Problems")
    d["expression"]["operand"] = d["expression"]["operand"][0]["operand"]


def _wrong_value_set(elm):
    retrieve(elm, "Active Confirmed Hypertension Problems")["codes"]["name"] = "Diabetes"


def _no_status_filter(elm):
    d = defn(elm, "Final Blood Pressure Readings")
    d["expression"].pop("where")


def _vital_signs_instead(elm):
    retrieve(elm, "Final Blood Pressure Readings")["templateId"] = \
        g.USC + "us-core-vital-signs"


def _diastolic(elm):
    d = defn(elm, "Most Recent Systolic Blood Pressure Quantity")
    d["expression"]["operand"]["source"]["name"] = "diastolic"


def _not_most_recent(elm):
    d = defn(elm, "Most Recent Blood Pressure Reading")
    d["expression"]["type"] = "SingletonFrom"


def _race_from_ethnicity(elm):
    d = defn(elm, "Patient Race Categories")
    d["expression"]["source"]["name"] = "ethnicity"


def _no_uscore(elm):
    elm["library"]["usings"]["def"] = [u for u in elm["library"]["usings"]["def"]
                                       if u["localIdentifier"] != "USCore"]


def _helpers_wrong_version(elm):
    for i in elm["library"]["includes"]["def"]:
        if i["path"] == "FHIRHelpers":
            i["version"] = "4.0.0"


@pytest.mark.parametrize("mutate, expected", [
    (_drop_code_path, "no terminology retrieve without a code path"),
    (_plain_fhir_condition, "every retrieve is of a US Core profile"),
    (_no_active, "filters on clinical status"),
    (_wrong_value_set, "by code in the value set"),
    (_no_status_filter, "Final Blood Pressure Readings: filters on status"),
    (_vital_signs_instead, "retrieves the Blood Pressure profile"),
    (_diastolic, "takes the systolic component"),
    (_not_most_recent, "picks the most recent reading"),
    (_race_from_ethnicity, "reads the US Core race extension"),
    (_no_uscore, "uses the USCore model"),
    (_helpers_wrong_version, "FHIRHelpers version 4.0.1"),
])
def test_mutation_fails(good, mutate, expected):
    elm = copy.deepcopy(good)
    mutate(elm)
    msgs = failures(elm)
    assert any(expected in m for m in msgs), msgs


def test_empty_library():
    assert "library is HypertensionCheck version 1.0.0" in failures({"library": {}})
