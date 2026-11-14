"""Tests for check_test_cases.py: a valid synthetic test case set passes, and each MADiE import rule
is caught when broken."""
from __future__ import annotations

import copy
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_test_cases as T  # noqa: E402

PID = "6b1a7c1e-4c0f-4e8f-9b0a-1f2e3d4c5b6a"
QI = "http://hl7.org/fhir/us/qicore/StructureDefinition/"
POP = "http://terminology.hl7.org/CodeSystem/measure-population"


def bundle() -> dict:
    return {
        "resourceType": "Bundle", "id": "b1", "type": "collection",
        "entry": [
            {"fullUrl": f"https://madie.cms.gov/Patient/{PID}",
             "resource": {"resourceType": "Patient", "id": PID, "meta": {"profile": [QI + "qicore-patient"]},
                          "identifier": [{"system": "https://madie.cms.gov/", "value": "SYN-0001"}],
                          "gender": "female", "name": [{"family": "DENOMPass", "given": ["InpatientStay"]}]}},
            {"resource": {"resourceType": "Encounter", "id": "enc-1", "meta": {"profile": [QI + "qicore-encounter"]},
                          "subject": {"reference": f"Patient/{PID}"}}},
            {"resource": {"resourceType": "Condition", "id": "cond-1",
                          "meta": {"profile": [QI + "qicore-condition-encounter-diagnosis"]},
                          "subject": {"reference": f"Patient/{PID}"}, "encounter": {"reference": "Encounter/enc-1"}}},
            {"resource": {"resourceType": "MeasureReport", "id": "mr-1", "status": "complete", "type": "individual",
                          "measure": "https://madie.cms.gov/Measure/ExampleFollowUp",
                          "group": [{"id": "Group_1", "population": [
                              {"code": {"coding": [{"system": POP, "code": "initial-population"}]}, "count": 1},
                              {"code": {"coding": [{"system": POP, "code": "denominator"}]}, "count": 1}]}]}},
        ],
    }


def metadata() -> list:
    return [{"testCaseId": "6720f1c2a9e4b51d3c8f0a17", "patientId": PID, "title": "InpatientStay",
             "series": "DENOMPass", "description": "Synthetic."}]


def write(root: Path, b=None, md=None, extra=None) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    if md is not False:
        (root / ".madie").write_text(json.dumps(metadata() if md is None else md), encoding="utf-8")
    (root / PID).mkdir()
    (root / PID / "ExampleFollowUp-v0.0.000-DENOMPass-InpatientStay.json").write_text(
        json.dumps(bundle() if b is None else b), encoding="utf-8")
    for name, text in (extra or {}).items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return root


def errors(path: Path, model=None) -> str:
    return "\n".join(T.check(path, model).errors)


def test_valid_folder_and_zip_pass(tmp_path):
    root = write(tmp_path / "tc")
    rep = T.check(root)
    assert rep.errors == [] and rep.warnings == []
    z = tmp_path / "tc.zip"
    with zipfile.ZipFile(z, "w") as zf:
        for f in root.rglob("*"):
            zf.write(f, f.relative_to(root).as_posix())
    assert T.check(z).errors == []


def test_missing_madie(tmp_path):
    assert "incorrect format" in errors(write(tmp_path / "tc", md=False))


def test_parent_folder(tmp_path):
    write(tmp_path / "outer" / "MyTests")
    out = errors(tmp_path / "outer")
    assert "MyTests/: a parent folder" in out and "Unable to find any valid test case json" in out


def test_two_files_in_a_folder(tmp_path):
    root = write(tmp_path / "tc", extra={f"{PID}/second.json": json.dumps(bundle())})
    assert "2 JSON files" in errors(root)


def test_patient_name_rules(tmp_path):
    b = bundle()
    b["entry"][0]["resource"]["name"] = [{"family": "X"}]
    assert "Test Case Title is required" in errors(write(tmp_path / "a", b=b))
    b["entry"][0]["resource"]["name"] = [{"given": ["X"]}]
    assert "has no family" in errors(write(tmp_path / "b", b=b))
    b = bundle()
    del b["entry"][0]["resource"]["identifier"]
    assert "Patient has no identifier" in errors(write(tmp_path / "c", b=b))


def test_ids_and_references(tmp_path):
    b = bundle()
    b["entry"][2]["resource"]["id"] = "enc-1"
    assert "ids must be unique" in errors(write(tmp_path / "a", b=b))
    b = bundle()
    b["entry"][2]["resource"]["encounter"]["reference"] = "urn:uuid:3f1b0c2e-1111-4111-8111-111111111111"
    assert "left out of execution" in errors(write(tmp_path / "b", b=b))
    b = bundle()
    b["entry"][2]["resource"]["encounter"]["reference"] = "Encounter/missing"
    rep = T.check(write(tmp_path / "c", b=b))
    assert rep.errors == [] and any("isn't in the bundle" in w for w in rep.warnings)


def test_metadata_rules(tmp_path):
    md = metadata()
    md[0]["title"] = "Inpatient_Stay"
    assert "won't export" in errors(write(tmp_path / "a", md=md))
    md = metadata() + copy.deepcopy(metadata())
    md[1]["patientId"] = "0f3e2d1c-1111-4111-8111-111111111111"
    root = write(tmp_path / "b", md=md, extra={f"{md[1]['patientId']}/x.json": json.dumps(bundle())})
    assert "must be unique" in errors(root)
    rep = T.check(write(tmp_path / "c", md=[]))
    assert any("no entry" in w for w in rep.warnings)


def test_qicore_versions(tmp_path):
    b = bundle()
    b["entry"][1]["resource"]["meta"]["profile"] = [QI + "qicore-condition"]
    assert "mixes QI-Core 4.1.1" in errors(write(tmp_path / "a", b=b))
    assert "6.0.0 profiles in a 4.1.1 measure" in errors(write(tmp_path / "b"), model="qicore4")
    assert errors(tmp_path / "b", model="qicore6") == ""


def test_measure_report(tmp_path):
    b = bundle()
    b["entry"][3]["resource"]["group"][0]["id"] = "Group_A"
    assert "must end in its group number" in errors(write(tmp_path / "a", b=b))
    b = bundle()
    b["entry"][3]["resource"]["group"][0]["population"][0]["code"]["coding"][0]["code"] = "initial"
    assert "isn't a measure-population code" in errors(write(tmp_path / "b", b=b))
    b = bundle()
    del b["entry"][3]
    rep = T.check(write(tmp_path / "c", b=b))
    assert rep.errors == [] and any("no expected values" in w for w in rep.warnings)
