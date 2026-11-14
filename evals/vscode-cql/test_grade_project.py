"""Tests for grade_project.py: the reference passes, and each targeted mistake fails its check."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import grade_project as G  # noqa: E402

REFERENCE = HERE / "reference" / "tk-01"
P1 = "11111111-1111-4111-8111-111111111111"
P2 = "22222222-2222-4222-8222-222222222222"


@pytest.fixture
def project(tmp_path: Path) -> Path:
    dest = tmp_path / "tk-01"
    shutil.copytree(REFERENCE, dest)
    return dest


def failed(project: Path) -> set[str]:
    return {name for name, ok, _ in G.grade(project) if not ok}


def cases(project: Path) -> Path:
    return project / "input" / "tests" / "Library" / "WeightCheck"


def config(project: Path) -> Path:
    return project / "input" / "tests" / "config.jsonc"


def edit_config(project: Path, old: str, new: str) -> None:
    t = config(project).read_text(encoding="utf-8")
    assert old in t
    config(project).write_text(t.replace(old, new), encoding="utf-8")


def test_reference_passes(project: Path) -> None:
    assert failed(project) == set()
    assert G.main(["grade_project.py", str(project)]) == 0


def test_no_ig_ini(project: Path) -> None:
    (project / "ig.ini").unlink()
    assert failed(project) == {"project root has ig.ini"}


def test_cql_outside_input_cql(project: Path) -> None:
    (project / "input" / "logic").mkdir()
    shutil.move(str(project / "input" / "cql" / "WeightCheck.cql"), str(project / "input" / "logic" / "WeightCheck.cql"))
    assert "input/cql/WeightCheck.cql exists" in failed(project)


def test_library_name_differs_from_file(project: Path) -> None:
    f = project / "input" / "cql" / "WeightCheck.cql"
    f.write_text(f.read_text(encoding="utf-8").replace("library WeightCheck", "library WeightChecks"), encoding="utf-8")
    assert failed(project) == {"library declaration matches the file name"}


def test_second_test_folder(project: Path) -> None:
    shutil.copytree(cases(project), project / "input" / "tests" / "Measure" / "WeightCheck")
    assert "exactly one WeightCheck test folder under input/tests" in failed(project)


def test_bundle_in_test_case(project: Path) -> None:
    obs = cases(project) / P1 / "Observation-weight-1.json"
    entry = json.loads(obs.read_text(encoding="utf-8"))
    (cases(project) / P1 / "Bundle-data.json").write_text(
        json.dumps({"resourceType": "Bundle", "type": "collection", "entry": [{"resource": entry}]}), encoding="utf-8")
    obs.unlink()
    assert failed(project) == {"no Bundles in test cases"}


def test_id_only_file_name(project: Path) -> None:
    obs = cases(project) / P1 / "Observation-weight-1.json"
    obs.rename(obs.with_name("weight-1.json"))
    assert failed(project) == {"every test file is named <ResourceType>-<id>.json"}


def test_patient_id_differs_from_folder(project: Path) -> None:
    pat = cases(project) / P1 / f"Patient-{P1}.json"
    pat.write_text(json.dumps({"resourceType": "Patient", "id": "someone-else"}), encoding="utf-8")
    assert failed(project) == {"each test case has a Patient whose id is the folder name"}


def test_reference_to_other_patient(project: Path) -> None:
    obs = cases(project) / P1 / "Observation-weight-1.json"
    obs.write_text(obs.read_text(encoding="utf-8").replace(f"Patient/{P1}", f"Patient/{P2}"), encoding="utf-8")
    assert failed(project) == {"subject/patient references point at the folder's patient"}


def test_default_result_format(project: Path) -> None:
    edit_config(project, '"resultFormat": "individual",', "")
    assert failed(project) == {"resultFormat is individual"}


def test_config_that_does_not_parse(project: Path) -> None:
    edit_config(project, '"resultFormat": "individual",', '"resultFormat": individual,')
    assert "config.jsonc parses" in failed(project)


def test_quoted_parameter_name(project: Path) -> None:
    edit_config(project, '"name": "Measurement Period"', '"name": "\\"Measurement Period\\""')
    got = failed(project)
    assert "Measurement Period is configured by its bare name" in got
    assert "every parameter value is a valid CQL literal for its declared parameter" in got


def test_unquoted_string_value(project: Path) -> None:
    edit_config(project, "\"value\": \"'Medicaid'\"", '"value": "Medicaid"')
    assert failed(project) == {"every parameter value is a valid CQL literal for its declared parameter"}


def test_date_interval_for_datetime_parameter(project: Path) -> None:
    edit_config(project, '"type": "Interval<DateTime>"', '"type": "Interval<Date>"')
    assert failed(project) == {"every parameter value is a valid CQL literal for its declared parameter"}


def test_fhir_type(project: Path) -> None:
    edit_config(project, '"type": "Interval<DateTime>"', '"type": "FHIR.Period"')
    assert failed(project) == {"every parameter value is a valid CQL literal for its declared parameter"}


def test_exclusion_without_reason(project: Path) -> None:
    edit_config(project, '"reason": "Synthetic placeholder patient with no data yet"', '"note": "x"')
    assert failed(project) == {"one test case excluded with library, testCase and reason"}


def test_value_set_missing(project: Path) -> None:
    (project / "input" / "vocabulary" / "valueset" / "ValueSet-body-weight-codes.json").unlink()
    assert failed(project) == {"each declared value set is in input/vocabulary, by url"}


def test_intensional_value_set_without_expansion(project: Path) -> None:
    f = project / "input" / "vocabulary" / "valueset" / "ValueSet-body-weight-codes.json"
    vs = json.loads(f.read_text(encoding="utf-8"))
    vs.pop("expansion")
    vs["compose"] = {"include": [{"system": "http://loinc.org", "filter": [{"property": "COMPONENT", "op": "=", "value": "Body weight"}]}]}
    f.write_text(json.dumps(vs), encoding="utf-8")
    assert failed(project) == {"value sets are expanded or simple code lists"}


def test_launch_with_folder_uri(project: Path) -> None:
    f = project / ".vscode" / "launch.json"
    f.write_text(f.read_text(encoding="utf-8").replace("/input/cql/WeightCheck.cql", "/input/cql"), encoding="utf-8")
    assert failed(project) == {"libraryUri is the .cql file as a file: URI"}


def test_launch_with_vscode_variable(project: Path) -> None:
    f = project / ".vscode" / "launch.json"
    f.write_text(f.read_text(encoding="utf-8").replace("file:///home/user/tk-01/input/cql/WeightCheck.cql", "${file}"),
                 encoding="utf-8")
    assert failed(project) == {"libraryUri is the .cql file as a file: URI"}


def test_launch_without_fhir_version(project: Path) -> None:
    f = project / ".vscode" / "launch.json"
    f.write_text(f.read_text(encoding="utf-8").replace('"fhirVersion": "R4",', ""), encoding="utf-8")
    assert failed(project) == {"libraryName and fhirVersion are set"}


def test_strip_jsonc() -> None:
    text = '{\n  // c\n  "a": "x // not a comment", /* b */ "c": [1, 2,],\n}'
    assert json.loads(G.strip_jsonc(text)) == {"a": "x // not a comment", "c": [1, 2]}


def test_cql_parameters() -> None:
    cql = "parameter \"Measurement Period\" Interval<DateTime>\nparameter Flag Boolean default true\n"
    assert G.cql_parameters(cql) == {"Measurement Period": "Interval<DateTime>", "Flag": "Boolean"}
