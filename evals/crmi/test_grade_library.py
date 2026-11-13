"""Tests for grade_library.py: one correct Library, and mutations that must each fail."""
import copy

import pytest

import grade_library as g


def good_library():
    return {
        "resourceType": "Library",
        "id": "DiabetesScreening",
        "meta": {"profile": [g.SHAREABLE, g.PUBLISHABLE]},
        "extension": [
            {"url": g.CAPABILITY_EXT, "valueCode": "shareable"},
            {"url": g.CAPABILITY_EXT, "valueCode": "publishable"},
        ],
        "url": g.URL,
        "version": "1.0.0",
        "name": "DiabetesScreening",
        "title": "Diabetes Screening",
        "status": "draft",
        "experimental": True,
        "type": {"coding": [{"system": g.LIBRARY_TYPE, "code": "logic-library"}]},
        "date": "2026-11-13",
        "publisher": "Example",
        "description": "Logic for diabetes screening.",
        "content": [{"contentType": "text/cql", "data": "bGlicmFyeSBEaWFiZXRlc1NjcmVlbmluZw=="}],
    }


def failures(lib):
    return [msg for ok, msg in g.grade(lib) if not ok]


def test_good_library_passes():
    assert failures(good_library()) == []


def _only_publishable(lib):
    lib["meta"]["profile"] = [g.PUBLISHABLE]


def _cpg_profile(lib):
    lib["meta"]["profile"].append("http://hl7.org/fhir/uv/cpg/StructureDefinition/cpg-publishablelibrary")


def _no_date(lib):
    del lib["date"]


def _no_title(lib):
    del lib["title"]


def _wrong_capability_url(lib):
    for e in lib["extension"]:
        e["url"] = "http://hl7.org/fhir/uv/crmi/StructureDefinition/crmi-knowledgeCapability"


def _only_shareable_capability(lib):
    lib["extension"] = lib["extension"][:1]


def _wrong_type(lib):
    lib["type"]["coding"][0]["code"] = "asset-collection"


def _bad_status(lib):
    lib["status"] = "final"


def _no_cql(lib):
    lib["content"][0]["contentType"] = "application/elm+json"


@pytest.mark.parametrize("mutate, expected", [
    (_only_publishable, "crmi-shareablelibrary"),
    (_cpg_profile, "no CPG profile"),
    (_no_date, "date is present"),
    (_no_title, "title is present"),
    (_wrong_capability_url, "cqf-knowledgeCapability"),
    (_only_shareable_capability, "cqf-knowledgeCapability"),
    (_wrong_type, "logic-library"),
    (_bad_status, "publication-status"),
    (_no_cql, "text/cql"),
])
def test_mutation_fails(mutate, expected):
    lib = copy.deepcopy(good_library())
    mutate(lib)
    found = failures(lib)
    assert any(expected in msg for msg in found), found


def test_not_a_library():
    assert failures({"resourceType": "PlanDefinition"}) == ["resourceType is Library"]
