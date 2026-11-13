"""Tests for grade_bundle.py: one correct bundle, and mutations that must each fail."""
import copy
import uuid

import pytest

import grade_bundle

NS = uuid.uuid5(uuid.NAMESPACE_URL, "https://example.org/cqf-skills/evals/fhir")
IDS = {t: str(uuid.uuid5(NS, t)) for t in ("Patient", "Encounter", "Condition", "Observation")}


def entry(resource):
    rtype, rid = resource["resourceType"], resource["id"]
    return {"fullUrl": f"https://example.org/fhir/{rtype}/{rid}", "resource": resource,
            "request": {"method": "PUT", "url": f"{rtype}/{rid}"}}


def good_bundle():
    p, e = f"Patient/{IDS['Patient']}", f"Encounter/{IDS['Encounter']}"
    return {"resourceType": "Bundle", "type": "transaction", "entry": [
        entry({"resourceType": "Patient", "id": IDS["Patient"], "gender": "female",
               "birthDate": "1958-03-02"}),
        entry({"resourceType": "Encounter", "id": IDS["Encounter"], "status": "finished",
               "class": {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                         "code": "IMP"},
               "subject": {"reference": p},
               "period": {"start": "2025-01-15", "end": "2025-01-17"}}),
        entry({"resourceType": "Condition", "id": IDS["Condition"],
               "clinicalStatus": {"coding": [{"code": "active"}]},
               "verificationStatus": {"coding": [{"code": "confirmed"}]},
               "code": {"coding": [{"system": "http://snomed.info/sct", "code": "44054006"}]},
               "subject": {"reference": p}, "encounter": {"reference": e}}),
        entry({"resourceType": "Observation", "id": IDS["Observation"], "status": "final",
               "code": {"coding": [{"system": "http://loinc.org", "code": "4548-4"}]},
               "subject": {"reference": p}, "effectiveDateTime": "2025-01-16",
               "valueQuantity": {"value": 8.5, "unit": "%",
                                 "system": "http://unitsofmeasure.org", "code": "%"}}),
    ]}


def failures(bundle):
    return [msg for ok, msg in grade_bundle.grade(bundle) if not ok]


def test_good_bundle_passes():
    assert failures(good_bundle()) == []


def test_urn_uuid_full_urls_pass():
    b = good_bundle()
    for e in b["entry"]:
        e["fullUrl"] = f"urn:uuid:{e['resource']['id']}"
    assert failures(b) == []


def _class_as_codeable_concept(b):
    b["entry"][1]["resource"]["class"] = {"coding": [{"code": "IMP"}]}


def _class_as_list(b):
    b["entry"][1]["resource"]["class"] = [{"code": "IMP"}]


def _dangling_reference(b):
    b["entry"][2]["resource"]["subject"]["reference"] = "Patient/not-in-bundle"


def _post_not_put(b):
    b["entry"][0]["request"]["method"] = "POST"


def _integer_id(b):
    e = b["entry"][0]
    e["resource"]["id"] = "1"
    e["request"]["url"] = "Patient/1"
    e["fullUrl"] = "https://example.org/fhir/Patient/1"


def _duplicate_full_url(b):
    b["entry"][1]["fullUrl"] = b["entry"][0]["fullUrl"]


def _no_observation_status(b):
    del b["entry"][3]["resource"]["status"]


def _batch_type(b):
    b["type"] = "batch"


def _missing_encounter_link(b):
    del b["entry"][2]["resource"]["encounter"]


@pytest.mark.parametrize("mutate, expected", [
    (_class_as_codeable_concept, "single Coding"),
    (_class_as_list, "single Coding"),
    (_dangling_reference, "resolves inside the bundle"),
    (_post_not_put, "request.method is PUT"),
    (_integer_id, "id is a UUID"),
    (_duplicate_full_url, "unique"),
    (_no_observation_status, "Observation.status"),
    (_batch_type, "type is transaction"),
    (_missing_encounter_link, "Condition.encounter"),
])
def test_mutation_fails(mutate, expected):
    b = copy.deepcopy(good_bundle())
    mutate(b)
    found = failures(b)
    assert any(expected in msg for msg in found), found


def test_not_a_bundle():
    assert failures({"resourceType": "Patient"}) == ["resourceType is Bundle"]
