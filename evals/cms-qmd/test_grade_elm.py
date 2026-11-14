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
    return load("DiabetesStatinCheck.json")


def failures(elm):
    return [msg for ok, msg in g.grade(elm) if not ok]


def test_reference_passes(good):
    assert failures(good) == []


def test_flawed_answer_fails_on_its_flaws():
    assert failures(load("DiabetesStatinCheck-flawed.json")) == [
        "every retrieve names a US Quality Core or US Core profile (types are qualified)",
        "Qualifying Encounters: retrieves US Quality Core Encounter by the Office Visit value set",
        "Encounters With Diabetes: times problems with prevalencePeriod() or relevantPeriod()",
        "Encounters With Diabetes: doesn't use current clinical status (isActive/active)",
    ]


def defn(elm, name):
    return next(d for d in elm["library"]["statements"]["def"] if d["name"] == name)


def retrieves(elm, name):
    return [n for n in g.walk(defn(elm, name)["expression"]) if n.get("type") == "Retrieve"]


def _negation_profile(elm):
    retrieves(elm, "Has Statin Order")[0]["templateId"] = \
        g.UQC + "us-quality-core-medicationnotrequested"


def _no_code_path(elm):
    del retrieves(elm, "Qualifying Encounters")[0]["codeProperty"]


def _no_status(elm):
    for n in g.walk(defn(elm, "Qualifying Encounters")["expression"]):
        if n.get("type") == "Property" and n.get("path") == "status":
            n["path"] = "class"


def _no_period(elm):
    for n in g.walk(defn(elm, "Qualifying Encounters")["expression"]):
        if n.get("type") == "ParameterRef":
            n["name"] = "Other Period"


def _no_encounter_diagnoses(elm):
    for r in retrieves(elm, "Encounters With Diabetes"):
        if r["templateId"] == g.ENC_DX:
            r["templateId"] = g.PROBLEMS


def _uses_active(elm):
    for n in g.walk(defn(elm, "Encounters With Diabetes")["expression"]):
        if n.get("type") == "FunctionRef" and n.get("name") == "prevalencePeriod":
            n["name"] = "active"


def _wrong_value_set(elm):
    retrieves(elm, "Has Statin Order")[0]["codes"]["name"] = "Aspirin"


def _no_absence(elm):
    d = defn(elm, "Diabetic Patients Without Statin Order")
    d["expression"] = d["expression"]["operand"][0]


def _no_fhir_using(elm):
    elm["library"]["usings"]["def"] = [u for u in elm["library"]["usings"]["def"]
                                       if u["localIdentifier"] != "FHIR"]


@pytest.mark.parametrize("mutate, expected", [
    (_negation_profile, "no negation profile is used"),
    (_no_code_path, "no terminology retrieve without a code path"),
    (_no_status, "Qualifying Encounters: filters on status"),
    (_no_period, "limited to the Measurement Period"),
    (_no_encounter_diagnoses, "looks at encounter diagnoses"),
    (_uses_active, "doesn't use current clinical status"),
    (_wrong_value_set, "Statin Therapy value set"),
    (_no_absence, "expresses the missing order as absence"),
    (_no_fhir_using, "uses the USQualityCore and FHIR models"),
])
def test_mutation_fails(good, mutate, expected):
    elm = copy.deepcopy(good)
    mutate(elm)
    msgs = failures(elm)
    assert any(expected in m for m in msgs), msgs
