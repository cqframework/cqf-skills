"""Tests for grade_procedure.py: one correct Procedure, and mutations that must each fail."""
import copy

import pytest

import grade_procedure as g


def good():
    return {
        "resourceType": "Procedure",
        "id": "colonoscopy-refused",
        "meta": {"profile": [g.PROFILE]},
        "extension": [{"url": g.RECORDED, "valueDateTime": "2026-03-04T10:00:00Z"}],
        "status": "not-done",
        "statusReason": {"coding": [{"system": g.SNOMED, "code": g.REFUSED,
                                     "display": "Procedure refused (situation)"}]},
        "code": {"extension": [{"url": g.NOT_DONE_VS, "valueCanonical": g.VALUE_SET}],
                 "text": "Colonoscopy"},
        "subject": {"reference": "Patient/example"},
    }


def failures(proc):
    return [msg for ok, msg in g.grade(proc) if not ok]


def test_good_passes():
    assert failures(good()) == []


def _completed(p):
    p["status"] = "completed"


def _reason_as_text(p):
    p["statusReason"] = {"text": "Patient refused"}


def _no_recorded(p):
    p["extension"] = []


def _recorded_on_code(p):
    p["code"]["extension"].append(p.pop("extension")[0])


def _coding_and_value_set(p):
    p["code"]["coding"] = [{"system": g.SNOMED, "code": "73761001"}]


def _coding_only(p):
    del p["code"]["extension"]
    p["code"]["coding"] = [{"system": g.SNOMED, "code": "73761001"}]


def _value_set_as_reason(p):
    del p["code"]["extension"]
    p["reasonCode"] = [{"text": g.VALUE_SET}]


def _performed(p):
    p["performedDateTime"] = "2026-03-04"


def _no_profile(p):
    del p["meta"]


def _wrong_subject(p):
    p["subject"]["reference"] = "Patient/other"


@pytest.mark.parametrize("mutate, expected", [
    (_completed, "status is not-done"),
    (_reason_as_text, "statusReason is SNOMED CT"),
    (_no_recorded, "us-quality-core-recorded"),
    (_recorded_on_code, "us-quality-core-recorded"),
    (_coding_and_value_set, "pnd-1"),
    (_coding_only, "notDoneValueSet extension"),
    (_value_set_as_reason, "notDoneValueSet extension"),
    (_performed, "no performed value"),
    (_no_profile, "meta.profile"),
    (_wrong_subject, "subject is Patient/example"),
])
def test_mutation_fails(mutate, expected):
    p = copy.deepcopy(good())
    mutate(p)
    found = failures(p)
    assert any(expected in m for m in found), found


def test_not_a_procedure():
    assert failures({"resourceType": "Observation"}) == ["resourceType is Procedure"]
