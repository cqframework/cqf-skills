"""Tests for grade_patient.py: one correct Patient, and mutations that must each fail."""
import copy

import pytest

import grade_patient as g


def good_patient():
    return {
        "resourceType": "Patient",
        "id": "example",
        "extension": [
            {"url": g.BIRTH_PLACE, "valueAddress": {"city": "Lisbon", "country": "PT"}},
            {"url": g.MAIDEN_NAME, "valueString": "Silva"},
            {"url": g.NATIONALITY, "extension": [
                {"url": "code", "valueCodeableConcept": {"coding": [
                    {"system": "urn:iso:std:iso:3166", "code": "PT"}]}}]},
            {"url": g.GENDER_IDENTITY, "extension": [
                {"url": "value", "valueCodeableConcept": {"coding": [
                    {"system": "http://snomed.info/sct", "code": "446151000124109"}]}}]},
        ],
        "_birthDate": {"extension": [{"url": g.DATA_ABSENT_REASON, "valueCode": "unknown"}]},
    }


def failures(patient):
    return [msg for ok, msg in g.grade(patient) if not ok]


def test_good_patient_passes():
    assert failures(good_patient()) == []


def _deprecated_gender_identity(p):
    p["extension"][3] = {"url": g.DEPRECATED_GENDER_IDENTITY,
                         "valueCodeableConcept": {"coding": [{"code": "x"}]}}


def _gender_identity_top_level_value(p):
    p["extension"][3] = {"url": g.GENDER_IDENTITY,
                         "valueCodeableConcept": {"coding": [{"code": "x"}]}}


def _nationality_top_level_value(p):
    p["extension"][2] = {"url": g.NATIONALITY,
                         "valueCodeableConcept": {"coding": [{"code": "PT"}]}}


def _birth_place_as_string(p):
    p["extension"][0] = {"url": g.BIRTH_PLACE, "valueString": "Lisbon"}


def _dar_on_patient(p):
    del p["_birthDate"]
    p["extension"].append({"url": g.DATA_ABSENT_REASON, "valueCode": "unknown"})


def _placeholder_birth_date(p):
    p["birthDate"] = "1900-01-01"


def _bad_dar_code(p):
    p["_birthDate"]["extension"][0]["valueCode"] = "missing"


def _wrong_maiden_name_url(p):
    p["extension"][1]["url"] = g.SD + "mothersMaidenName"


@pytest.mark.parametrize("mutate, expected", [
    (_deprecated_gender_identity, "patient-genderIdentity is not used"),
    (_gender_identity_top_level_value, "individual-genderIdentity is complex"),
    (_nationality_top_level_value, "patient-nationality is complex"),
    (_birth_place_as_string, "valueAddress"),
    (_dar_on_patient, "_birthDate has a data-absent-reason"),
    (_placeholder_birth_date, "birthDate has no value"),
    (_bad_dar_code, "_birthDate has a data-absent-reason"),
    (_wrong_maiden_name_url, "patient-mothersMaidenName"),
])
def test_mutation_fails(mutate, expected):
    p = copy.deepcopy(good_patient())
    mutate(p)
    found = failures(p)
    assert any(expected in msg for msg in found), found


def test_not_a_patient():
    assert failures({"resourceType": "Practitioner"}) == ["resourceType is Patient"]
