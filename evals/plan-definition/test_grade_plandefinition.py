"""Tests for grade_plandefinition.py: the reference passes, and each deliberate mistake is caught."""
from __future__ import annotations

import base64
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import grade_plandefinition as G  # noqa: E402

REFERENCE = Path(__file__).resolve().parent / "reference" / "tk-01"
RES = Path("input") / "resources"


def copy(tmp_path: Path) -> Path:
    dest = tmp_path / "tk-01"
    shutil.copytree(REFERENCE, dest)
    return dest


def edit(root: Path, name: str, fn) -> None:
    f = root / RES / name
    r = json.loads(f.read_text(encoding="utf-8"))
    fn(r)
    f.write_text(json.dumps(r), encoding="utf-8")


def failed(root: Path) -> set[str]:
    return {label.split()[0] for ok, label in G.grade(root).results if not ok}


def test_reference_passes():
    g = G.grade(REFERENCE)
    assert all(ok for ok, _ in g.results), [label for ok, label in g.results if not ok]


def test_wrong_type(tmp_path):
    root = copy(tmp_path)
    edit(root, "PlanDefinition-hba1c-follow-up.json", lambda r: r["type"]["coding"][0].update(code="order-set"))
    assert failed(root) == {"P2"}


def test_expression_not_in_library(tmp_path):
    root = copy(tmp_path)
    edit(root, "PlanDefinition-hba1c-follow-up.json",
         lambda r: r["action"][0]["condition"][0]["expression"].update(expression="Needs A1c"))
    assert failed(root) == {"L2"}


def test_inline_language(tmp_path):
    root = copy(tmp_path)
    edit(root, "PlanDefinition-hba1c-follow-up.json",
         lambda r: r["action"][0]["condition"][0]["expression"].update(language="text/fhirpath"))
    assert failed(root) == {"L2"}


def test_absolute_dynamic_value_path(tmp_path):
    root = copy(tmp_path)
    edit(root, "PlanDefinition-hba1c-follow-up.json",
         lambda r: r["action"][0]["dynamicValue"].append({"path": "ServiceRequest.priority",
                                                           "expression": {"language": "text/cql-identifier", "expression": "Order Reason"}}))
    assert failed(root) == {"P8"}


def test_start_condition(tmp_path):
    root = copy(tmp_path)
    edit(root, "PlanDefinition-hba1c-follow-up.json", lambda r: r["action"][0]["condition"][0].update(kind="start"))
    assert failed(root) == {"P5"}


def test_two_libraries(tmp_path):
    root = copy(tmp_path)
    edit(root, "PlanDefinition-hba1c-follow-up.json", lambda r: r["library"].append("http://example.org/fhir/Library/Other"))
    assert "P3" in failed(root)


def test_definition_points_elsewhere(tmp_path):
    root = copy(tmp_path)
    edit(root, "PlanDefinition-hba1c-follow-up.json",
         lambda r: r["action"][0].update(definitionCanonical="http://example.org/fhir/ActivityDefinition/other"))
    assert failed(root) == {"P6"}


def test_default_intent(tmp_path):
    root = copy(tmp_path)
    edit(root, "ActivityDefinition-order-hba1c.json", lambda r: r.pop("intent"))
    assert failed(root) == {"A3"}


def test_activity_dynamic_value_without_library(tmp_path):
    root = copy(tmp_path)
    edit(root, "ActivityDefinition-order-hba1c.json",
         lambda r: r.update(dynamicValue=[{"path": "priority", "expression": {"language": "text/cql-identifier", "expression": "Order Reason"}}]))
    assert failed(root) == {"A4"}


def test_cql_not_in_content(tmp_path):
    root = copy(tmp_path)
    edit(root, "Library-HbA1cFollowUp.json", lambda r: r.update(content=[]))
    assert {"L1", "L2", "L3", "L4", "L5"} <= failed(root)


def test_no_lookback(tmp_path):
    root = copy(tmp_path)
    def change(r):
        cql = base64.b64decode(r["content"][0]["data"]).decode().replace("6 months", "1 year")
        r["content"][0]["data"] = base64.b64encode(cql.encode()).decode()
    edit(root, "Library-HbA1cFollowUp.json", change)
    assert failed(root) == {"L4"}


def test_missing_observation(tmp_path):
    root = copy(tmp_path)
    (root / "input" / "tests" / "Observation-recent-hba1c.json").unlink()
    assert failed(root) == {"T2"}
