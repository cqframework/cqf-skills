"""Tests for grade_bp.py: SUSHI's output for the reference answer, and mutations that must fail.

reference/ holds the reference FSH and the JSON that SUSHI 3.21.0 generated from it. To refresh it,
run `sushi build reference` and commit the new fsh-generated/resources.
"""
import copy
from pathlib import Path

import pytest

import grade_bp as g

RESOURCES = Path(__file__).resolve().parent / "reference" / "fsh-generated" / "resources"


@pytest.fixture(scope="module")
def reference():
    return g.load(RESOURCES)


def failures(found):
    return [msg for ok, msg in g.grade(found) if not ok]


def test_reference_passes(reference):
    assert failures(reference) == []


def element(found, sd_id, el_id):
    sd = found[f"StructureDefinition/{sd_id}"]
    return next(e for e in sd["differential"]["element"] if e["id"] == el_id)


def _code_not_constrained(f):
    del element(f, "simple-bp", "Observation.code")["patternCodeableConcept"]


def _two_reference_targets(f):
    element(f, "simple-bp", "Observation.subject")["type"][0]["targetProfile"].append(
        "http://hl7.org/fhir/StructureDefinition/Group")


def _extensible_binding(f):
    element(f, "simple-bp", "Observation.method")["binding"]["strength"] = "extensible"


def _extension_not_profiled(f):
    # What `extension contains ReviewedBy 0..1` (no `named`) leaves behind.
    del element(f, "simple-bp", "Observation.extension:reviewedBy")["type"]


def _extension_not_must_support(f):
    del element(f, "simple-bp", "Observation.extension:reviewedBy")["mustSupport"]


def _no_component_slicing(f):
    del element(f, "simple-bp", "Observation.component")["slicing"]


def _systolic_optional(f):
    element(f, "simple-bp", "Observation.component:systolic")["min"] = 0


def _wrong_unit(f):
    element(f, "simple-bp", "Observation.component:diastolic.value[x]")["patternQuantity"][
        "code"] = "mmHg"


def _extension_value_string(f):
    element(f, "reviewed-by", "Extension.value[x]")["type"] = [{"code": "string"}]


def _example_id_wrong(f):
    f["Observation/ExampleBP"] = f.pop("Observation/example-bp")


def _example_swapped(f):
    comps = f["Observation/example-bp"]["component"]
    comps[0]["valueQuantity"]["value"], comps[1]["valueQuantity"]["value"] = 80, 120


def _value_set_enumerates(f):
    f["ValueSet/bp-method"]["compose"]["include"][0]["concept"] = [{"code": "auto"}]


@pytest.mark.parametrize("mutate, expected", [
    (_code_not_constrained, "code is LOINC 85354-9"),
    (_two_reference_targets, "references only Patient"),
    (_extensible_binding, "required binding"),
    (_extension_not_profiled, "must-support extension slice"),
    (_extension_not_must_support, "must-support extension slice"),
    (_no_component_slicing, "discriminator on code"),
    (_systolic_optional, "1..1 systolic slice"),
    (_wrong_unit, "diastolic value is a Quantity in UCUM mm[Hg]"),
    (_extension_value_string, "Reference(Practitioner)"),
    (_example_id_wrong, "Observation example-bp was generated"),
    (_example_swapped, "example systolic is 120"),
    (_value_set_enumerates, "all codes from the code system"),
])
def test_mutation_fails(reference, mutate, expected):
    found = copy.deepcopy(reference)
    mutate(found)
    msgs = failures(found)
    assert any(expected in m for m in msgs), msgs


def test_fixed_code_also_passes(reference):
    found = copy.deepcopy(reference)
    el = element(found, "simple-bp", "Observation.code")
    el["fixedCodeableConcept"] = el.pop("patternCodeableConcept")
    assert failures(found) == []


def test_empty_folder(tmp_path):
    msgs = failures(g.load(tmp_path))
    assert "profile simple-bp was generated" in msgs
