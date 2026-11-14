"""Tests for grade_ig.py: the reference passes, and each targeted mistake fails its check."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import grade_ig  # noqa: E402

REFERENCE = HERE / "reference" / "tk-01"


@pytest.fixture
def project(tmp_path: Path) -> Path:
    dest = tmp_path / "tk-01"
    shutil.copytree(REFERENCE, dest)
    return dest


def failed(project: Path) -> set[str]:
    return {name for name, ok, _ in grade_ig.grade(project) if not ok}


def edit_json(path: Path, change) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    change(data)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def test_reference_passes(project: Path) -> None:
    assert failed(project) == set()
    assert grade_ig.main(["grade_ig.py", str(project)]) == 0


def test_comment_before_ig_section(project: Path) -> None:
    ini = project / "ig.ini"
    ini.write_text("; my IG\n" + ini.read_text(encoding="utf-8"), encoding="utf-8")
    assert failed(project) == {"ig.ini starts with [IG]"}


def test_byte_order_mark(project: Path) -> None:
    ini = project / "ig.ini"
    ini.write_bytes(b"\xef\xbb\xbf" + ini.read_bytes())
    assert "ig.ini starts with [IG]" in failed(project)


def test_unpinned_template(project: Path) -> None:
    ini = project / "ig.ini"
    ini.write_text(ini.read_text(encoding="utf-8").replace("#1.0.0", ""), encoding="utf-8")
    assert failed(project) == {"template pinned to a version"}


def test_missing_ig_file(project: Path) -> None:
    (project / "input" / "example-screening.json").unlink()
    assert "ig key names an existing file" in failed(project)


def test_no_path_binary(project: Path) -> None:
    edit_json(project / "input" / "example-screening.json",
              lambda ig: ig["definition"].pop("parameter"))
    got = failed(project)
    assert "path-binary is set" in got
    assert "ExampleScreening .cql is directly in a path-binary folder" in got


def test_path_binary_as_extension(project: Path) -> None:
    def to_extension(ig):
        ig["definition"].pop("parameter")
        ig["definition"]["extension"] = [{
            "url": grade_ig.IG_PARAM_EXT,
            "extension": [{"url": "code", "valueString": "path-binary"},
                          {"url": "value", "valueString": "input/cql"}],
        }]
    edit_json(project / "input" / "example-screening.json", to_extension)
    assert failed(project) == set()


def test_cql_in_sub_folder(project: Path) -> None:
    sub = project / "input" / "cql" / "measures"
    sub.mkdir()
    shutil.move(str(project / "input" / "cql" / "ExampleScreening.cql"), str(sub / "ExampleScreening.cql"))
    assert "ExampleScreening .cql is directly in a path-binary folder" in failed(project)


def test_inline_cql_attachment(project: Path) -> None:
    edit_json(project / "input" / "resources" / "Library-ExampleScreening.json",
              lambda lib: lib["content"][0].update({"data": "bGlicmFyeQ=="}))
    assert failed(project) == {"ig-loader- attachment has only id (and optionally contentType)"}


def test_content_type_is_allowed(project: Path) -> None:
    edit_json(project / "input" / "resources" / "Library-ExampleScreening.json",
              lambda lib: lib["content"][0].update({"contentType": "text/cql"}))
    assert failed(project) == set()


def test_no_ig_loader(project: Path) -> None:
    edit_json(project / "input" / "resources" / "Library-ExampleScreening.json",
              lambda lib: lib.update({"content": [{"contentType": "text/cql", "data": "bGlicmFyeQ=="}]}))
    assert failed(project) == {"Library content has an ig-loader- attachment"}


def test_wrong_ig_loader_file(project: Path) -> None:
    edit_json(project / "input" / "resources" / "Library-ExampleScreening.json",
              lambda lib: lib["content"][0].update({"id": "ig-loader-input/cql/ExampleScreening.cql"}))
    assert failed(project) == {"ig-loader- id names the .cql file"}


def test_measure_library_name_mismatch(project: Path) -> None:
    edit_json(project / "input" / "resources" / "Measure-ExampleScreening.json",
              lambda m: m.update({"library": ["http://example.org/fhir/screening/Library/example-screening-logic"]}))
    assert failed(project) == {"Measure has exactly one library, matching the CQL name by its last segment"}


def test_measure_two_libraries(project: Path) -> None:
    edit_json(project / "input" / "resources" / "Measure-ExampleScreening.json",
              lambda m: m["library"].append("http://example.org/fhir/screening/Library/Other"))
    assert "Measure has exactly one library, matching the CQL name by its last segment" in failed(project)


def test_ignore_warnings_without_header(project: Path) -> None:
    iw = project / "input" / "ignoreWarnings.txt"
    lines = iw.read_text(encoding="utf-8").splitlines()[1:]
    iw.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert failed(project) == {"ignoreWarnings.txt starts with == Suppressed Messages =="}


def test_ignore_warnings_message_before_reason(project: Path) -> None:
    iw = project / "input" / "ignoreWarnings.txt"
    iw.write_text("== Suppressed Messages ==\n\n%some warning%\n# reason\n", encoding="utf-8")
    assert failed(project) == {"every suppressed message follows a '# ' reason"}


def test_xml_ig_resource(project: Path) -> None:
    (project / "input" / "example-screening.json").unlink()
    (project / "input" / "example-screening.xml").write_text(
        """<ImplementationGuide xmlns="http://hl7.org/fhir">
  <id value="example.fhir.screening"/>
  <fhirVersion value="4.0.1"/>
  <definition>
    <parameter><code value="path-binary"/><value value="input/cql"/></parameter>
  </definition>
</ImplementationGuide>
""", encoding="utf-8")
    ini = project / "ig.ini"
    ini.write_text(ini.read_text(encoding="utf-8").replace(".json", ".xml"), encoding="utf-8")
    assert failed(project) == set()
