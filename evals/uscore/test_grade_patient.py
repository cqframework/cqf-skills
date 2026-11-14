"""Tests for grade_patient.py: one correct Patient, and mutations that must each fail."""
import copy

import pytest

import grade_patient as g


def good_patient():
    return {
        "resourceType": "Patient",
        "id": "maria-reyes",
        "extension": [
            {"url": g.RACE, "extension": [
                {"url": "ombCategory", "valueCoding": {"system": g.CDCREC, "code": "2106-3",
                                                       "display": "White"}},
                {"url": "text", "valueString": "White"}]},
            {"url": g.ETHNICITY, "extension": [
                {"url": "ombCategory", "valueCoding": {"system": g.CDCREC, "code": "2135-2",
                                                       "display": "Hispanic or Latino"}},
                {"url": "text", "valueString": "Hispanic or Latino"}]},
            {"url": g.INDIVIDUAL_SEX, "valueCoding": {"system": g.SNOMED, "code": "248152002",
                                                      "display": "Female (finding)"}},
            {"url": g.INTERPRETER, "valueCoding": {"system": g.SNOMED, "code": "373066001",
                                                   "display": "Yes"}},
            {"url": g.HL7_GENDER_IDENTITY, "extension": [
                {"url": "value", "valueCodeableConcept": {"coding": [
                    {"system": g.SNOMED, "code": "446141000124107"}]}}]},
        ],
        "identifier": [{"system": "http://hospital.example.org/mrn", "value": "MRN-48213"}],
        "name": [{"family": "Reyes", "given": ["Maria"]}],
        "birthDate": "1984-03-07",
    }


def failures(patient):
    return [msg for ok, msg in g.grade(patient) if not ok]


def test_good_patient_passes():
    assert failures(good_patient()) == []


def _ext(p, url):
    return next(e for e in p["extension"] if e["url"] == url)


def _old_sex(p):
    _ext(p, g.INDIVIDUAL_SEX)["url"] = g.USC + "us-core-sex"


def _uscore_gender_identity(p):
    p["extension"].append({"url": g.USC + "us-core-genderIdentity",
                           "valueCodeableConcept": {"coding": [{"code": "x"}]}})


def _gender_identity_flat(p):
    gi = _ext(p, g.HL7_GENDER_IDENTITY)
    gi.pop("extension")
    gi["valueCodeableConcept"] = {"coding": [{"code": "x"}]}


def _gender_unknown(p):
    p["gender"] = "unknown"


def _gender_dar(p):
    p["_gender"] = {"extension": [{"url": "http://hl7.org/fhir/StructureDefinition/data-absent-reason",
                                   "valueCode": "unknown"}]}


def _race_without_text(p):
    race = _ext(p, g.RACE)
    race["extension"] = [e for e in race["extension"] if e["url"] != "text"]


def _race_flat(p):
    race = _ext(p, g.RACE)
    race["valueCoding"] = race["extension"][0]["valueCoding"]


def _race_wrong_system(p):
    _ext(p, g.RACE)["extension"][0]["valueCoding"]["system"] = "http://example.org/race"


def _ethnicity_detailed_only(p):
    _ext(p, g.ETHNICITY)["extension"][0]["url"] = "detailed"


def _identifier_without_system(p):
    del p["identifier"][0]["system"]


def _sex_as_code(p):
    sex = _ext(p, g.INDIVIDUAL_SEX)
    sex["valueCode"] = "F"
    del sex["valueCoding"]


def _no_interpreter(p):
    p["extension"] = [e for e in p["extension"] if e["url"] != g.INTERPRETER]


@pytest.mark.parametrize("mutate, expected", [
    (_old_sex, "us-core-individual-sex"),
    (_old_sex, "deprecated us-core-sex"),
    (_uscore_gender_identity, "deprecated us-core-genderIdentity"),
    (_gender_identity_flat, "individual-genderIdentity with a value sub-extension"),
    (_gender_unknown, "gender is omitted"),
    (_gender_dar, "gender is omitted"),
    (_race_without_text, "us-core-race has the required text"),
    (_race_flat, "us-core-race is complex"),
    (_race_wrong_system, "ombCategory 2106-3"),
    (_ethnicity_detailed_only, "ombCategory 2135-2"),
    (_identifier_without_system, "identifier has a system"),
    (_sex_as_code, "valueCoding SNOMED CT 248152002"),
    (_no_interpreter, "us-core-interpreter-needed"),
])
def test_mutation_fails(mutate, expected):
    p = copy.deepcopy(good_patient())
    mutate(p)
    found = failures(p)
    assert any(expected in msg for msg in found), found


def test_not_a_patient():
    assert failures({"resourceType": "Practitioner"}) == ["resourceType is Patient"]
