"""Tests for grade_plandefinition.py: one correct PlanDefinition, and mutations that must each fail."""
import copy

import pytest

import grade_plandefinition as g


def good_plandefinition():
    return {
        "resourceType": "PlanDefinition",
        "id": "DiabetesScreeningRecommendation",
        "meta": {"profile": [
            g.RECOMMENDATION,
            "http://hl7.org/fhir/uv/crmi/StructureDefinition/crmi-shareableplandefinition",
        ]},
        "url": "http://example.org/fhir/PlanDefinition/DiabetesScreeningRecommendation",
        "version": "1.0.0",
        "title": "Diabetes Screening Recommendation",
        "type": {"coding": [{"system": g.PLAN_TYPE, "code": "eca-rule"}]},
        "status": "draft",
        "library": [g.LIBRARY],
        "action": [{
            "title": "Offer diabetes screening",
            "extension": [{
                "url": g.DIRECTION_EXT,
                "valueCodeableConcept": {"coding": [{
                    "system": "http://hl7.org/fhir/uv/cpg/CodeSystem/cpg-recommendation-direction-cs",
                    "code": "for"}]},
            }],
            "definitionCanonical": g.ACTIVITY,
        }],
    }


def failures(pd):
    return [msg for ok, msg in g.grade(pd) if not ok]


def test_good_plandefinition_passes():
    assert failures(good_plandefinition()) == []


def _no_profile(pd):
    pd["meta"]["profile"] = pd["meta"]["profile"][1:]


def _old_shareable(pd):
    pd["meta"]["profile"].append(g.CPG + "cpg-shareableplandefinition")


def _workflow_type(pd):
    pd["type"]["coding"][0]["code"] = "workflow-definition"


def _bad_status(pd):
    pd["status"] = "final"


def _no_library(pd):
    del pd["library"]


def _no_actions(pd):
    pd["action"] = []


def _direction_against(pd):
    pd["action"][0]["extension"][0]["valueCodeableConcept"]["coding"][0]["code"] = "against"


def _cqf_direction_url(pd):
    pd["action"][0]["extension"][0]["url"] = "http://hl7.org/fhir/StructureDefinition/cqf-directionOfRecommendation"


def _definition_uri(pd):
    action = pd["action"][0]
    action["definitionUri"] = action.pop("definitionCanonical")


@pytest.mark.parametrize("mutate, expected", [
    (_no_profile, "claims cpg-recommendationdefinition"),
    (_old_shareable, "CPG 1.0.0"),
    (_workflow_type, "eca-rule"),
    (_bad_status, "publication-status"),
    (_no_library, "library includes"),
    (_no_actions, "at least one action"),
    (_direction_against, "directionOfRecommendation"),
    (_cqf_direction_url, "directionOfRecommendation"),
    (_definition_uri, "definitionCanonical"),
])
def test_mutation_fails(mutate, expected):
    pd = copy.deepcopy(good_plandefinition())
    mutate(pd)
    found = failures(pd)
    assert any(expected in msg for msg in found), found


def test_not_a_plandefinition():
    assert failures({"resourceType": "Library"}) == ["resourceType is PlanDefinition"]
