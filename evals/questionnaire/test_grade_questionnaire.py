"""Tests for grade_questionnaire.py: the reference passes, and each deliberate mistake is caught."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import grade_questionnaire as G  # noqa: E402

REFERENCE = Path(__file__).resolve().parent / "reference" / "tk-01"
Q = Path("input") / "resources" / "Questionnaire-intake.json"
SDC = "http://hl7.org/fhir/uv/sdc/StructureDefinition/"


def copy(tmp_path: Path) -> Path:
    dest = tmp_path / "tk-01"
    shutil.copytree(REFERENCE, dest)
    return dest


def edit(root: Path, fn, rel: Path = Q) -> None:
    f = root / rel
    r = json.loads(f.read_text(encoding="utf-8"))
    fn(r)
    f.write_text(json.dumps(r), encoding="utf-8")


def item(r: dict, link_id: str) -> dict:
    for it, _ in G.walk(r["item"]):
        if it["linkId"] == link_id:
            return it
    raise KeyError(link_id)


def failed(root: Path) -> set[str]:
    return {label.split()[0] for ok, label in G.grade(root).results if not ok}


def test_reference_passes():
    g = G.grade(REFERENCE)
    assert all(ok for ok, _ in g.results), [label for ok, label in g.results if not ok]


def test_duplicate_link_id(tmp_path):
    root = copy(tmp_path)
    edit(root, lambda r: item(r, "smoker").update(linkId="given-name"))
    assert "Q2" in failed(root)


def test_two_enable_whens_without_behavior(tmp_path):
    root = copy(tmp_path)
    edit(root, lambda r: item(r, "packs")["enableWhen"].append(
        {"question": "given-name", "operator": "exists", "answerBoolean": True}))
    assert failed(root) == {"Q3"}


def test_launch_context_name_as_code(tmp_path):
    root = copy(tmp_path)

    def fn(r):
        lc = [e for e in r["extension"] if e["url"].endswith("launchContext")][0]
        lc["extension"][0] = {"url": "name", "valueCode": "patient"}
    edit(root, fn)
    assert failed(root) == {"E2"}


def test_qualified_identifier(tmp_path):
    root = copy(tmp_path)
    edit(root, lambda r: item(r, "given-name")["extension"][0]["valueExpression"].update(
        expression='IntakeLogic."Given Name"'))
    assert failed(root) == {"E5"}


def test_subject_variable(tmp_path):
    root = copy(tmp_path)
    edit(root, lambda r: item(r, "conditions.code")["extension"][0]["valueExpression"].update(
        expression="%subject.name.given.first()"))
    assert "E6" in failed(root)


def test_cqf_calculated_value(tmp_path):
    root = copy(tmp_path)
    edit(root, lambda r: item(r, "packs").setdefault("extension", []).append(
        {"url": "http://hl7.org/fhir/StructureDefinition/cqf-calculatedValue", "valueString": "Packs"}))
    assert failed(root) == {"E7"}


def test_weight_not_extracted(tmp_path):
    root = copy(tmp_path)
    edit(root, lambda r: item(r, "weight").update(
        extension=[e for e in item(r, "weight")["extension"] if not e["url"].endswith("observationExtract")]))
    assert failed(root) == {"P1"}


def test_weight_returns_a_list(tmp_path):
    root = copy(tmp_path)
    edit(root, lambda r: item(r, "weight")["extension"][0]["valueExpression"].update(expression="Active Conditions"))
    assert failed(root) == {"P2"}


def test_context_name_missing(tmp_path):
    root = copy(tmp_path)
    edit(root, lambda r: item(r, "conditions")["extension"][0]["valueExpression"].pop("name"))
    assert failed(root) == {"P3", "P4"}


def test_extra_coded_item(tmp_path):
    root = copy(tmp_path)
    edit(root, lambda r: item(r, "smoker").update(code=[{"system": "http://loinc.org", "code": "72166-2"}]))
    assert failed(root) == {"P5"}


def test_initial_expression_on_group(tmp_path):
    root = copy(tmp_path)
    edit(root, lambda r: item(r, "conditions")["extension"].append(
        {"url": SDC + "sdc-questionnaire-initialExpression",
         "valueExpression": {"language": "text/cql-identifier", "expression": "Given Name"}}))
    assert failed(root) == {"Q5"}


def test_response_answer_and_item(tmp_path):
    root = copy(tmp_path)
    rel = Path("input") / "tests" / "QuestionnaireResponse-intake-1-completed.json"
    edit(root, lambda r: r["item"][4].update(answer=[{"valueBoolean": True}]), rel)
    assert failed(root) == {"T3"}
