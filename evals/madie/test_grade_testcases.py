"""Tests for grade_testcases.py: the reference answer passes, and each deliberate mistake is caught."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import grade_testcases as G  # noqa: E402

REFERENCE = Path(__file__).resolve().parent / "reference" / "tk-01"
FOLLOWUP = "22222222-2222-4222-8222-222222222222"
HOSPICE = "33333333-3333-4333-8333-333333333333"


def copy(tmp_path: Path) -> Path:
    dest = tmp_path / "tk-01"
    shutil.copytree(REFERENCE, dest)
    return dest


def bundle_file(root: Path, pid: str) -> Path:
    return next((root / pid).glob("*.json"))


def edit(root: Path, pid: str, fn) -> None:
    f = bundle_file(root, pid)
    b = json.loads(f.read_text(encoding="utf-8"))
    fn(b)
    f.write_text(json.dumps(b), encoding="utf-8")


def failed(root: Path) -> set[str]:
    return {label.split()[0] for ok, label in G.grade(root).results if not ok}


def test_reference_passes():
    g = G.grade(REFERENCE)
    assert all(ok for ok, _ in g.results), [label for ok, label in g.results if not ok]
    assert len(g.results) >= 40


def test_parent_folder(tmp_path):
    outer = tmp_path / "outer"
    shutil.copytree(REFERENCE, outer / "TestCases")
    assert {"L1", "L2"} <= failed(outer)


def test_missing_madie(tmp_path):
    root = copy(tmp_path)
    (root / ".madie").unlink()
    assert {"L1", "M2", "M3"} <= failed(root)


def test_wrong_series(tmp_path):
    root = copy(tmp_path)
    md = json.loads((root / ".madie").read_text(encoding="utf-8"))
    md[0]["series"] = "DENOM_Pass"
    (root / ".madie").write_text(json.dumps(md), encoding="utf-8")
    assert {"M3", "M4"} <= failed(root)


def test_two_files(tmp_path):
    root = copy(tmp_path)
    shutil.copy(bundle_file(root, HOSPICE), root / HOSPICE / "copy.json")
    assert "L3" in failed(root)


def test_patient_without_identifier(tmp_path):
    root = copy(tmp_path)
    edit(root, HOSPICE, lambda b: b["entry"][0]["resource"].pop("identifier"))
    assert failed(root) == {"B3a"}


def test_urn_uuid_reference(tmp_path):
    root = copy(tmp_path)
    edit(root, HOSPICE, lambda b: b["entry"][2]["resource"]["subject"].update(
        reference="urn:uuid:33333333-3333-4333-8333-333333333333"))
    assert failed(root) == {"B5"}


def test_duplicate_ids(tmp_path):
    root = copy(tmp_path)
    edit(root, FOLLOWUP, lambda b: b["entry"][2]["resource"].update(id=b["entry"][1]["resource"]["id"]))
    assert "B4" in failed(root)


def test_qicore_profile(tmp_path):
    root = copy(tmp_path)
    edit(root, HOSPICE, lambda b: b["entry"][2]["resource"]["meta"].update(
        profile=["http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-condition-problems-health-concerns"]))
    assert failed(root) == {"B6"}


def test_transaction_bundle(tmp_path):
    root = copy(tmp_path)
    edit(root, HOSPICE, lambda b: b.update(type="transaction"))
    assert failed(root) == {"B1"}


def test_patient_id_not_folder(tmp_path):
    root = copy(tmp_path)
    def change(b):
        b["entry"][0]["resource"]["id"] = "p1"
        for e in b["entry"][1:]:
            for k in ("subject",):
                if k in e["resource"]:
                    e["resource"][k] = {"reference": "Patient/p1"}
    edit(root, HOSPICE, change)
    assert failed(root) == {"B3b"}


def test_missing_followup_encounter(tmp_path):
    root = copy(tmp_path)
    edit(root, FOLLOWUP, lambda b: b["entry"].pop(2))
    assert failed(root) == {"D2"}


def test_inactive_hospice_condition(tmp_path):
    root = copy(tmp_path)
    edit(root, HOSPICE, lambda b: b["entry"][2]["resource"].pop("clinicalStatus"))
    assert failed(root) == {"D3"}


def test_population_order(tmp_path):
    root = copy(tmp_path)
    edit(root, FOLLOWUP, lambda b: b["entry"][-1]["resource"]["group"][0]["population"].reverse())
    assert failed(root) == {"R3"}


def test_wrong_count(tmp_path):
    root = copy(tmp_path)
    edit(root, FOLLOWUP, lambda b: b["entry"][-1]["resource"]["group"][0]["population"][3].update(count=0))
    assert failed(root) == {"R4"}


def test_missing_measure_report(tmp_path):
    root = copy(tmp_path)
    edit(root, HOSPICE, lambda b: b["entry"].pop())
    assert failed(root) == {"R1"}
