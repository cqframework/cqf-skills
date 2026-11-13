"""Tests for convert-resource-to-markdown.py. Run: python3 -m pytest -q test_convert_resource.py"""

import importlib.util
import json
import shutil
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent / "convert-resource-to-markdown.py"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "crmi-shareablelibrary.json"


def _load_module():
    spec = importlib.util.spec_from_file_location("convert_resource_to_markdown", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def mod():
    return _load_module()


@pytest.fixture
def input_dir(tmp_path):
    d = tmp_path / "in"
    d.mkdir()
    shutil.copy(FIXTURE, d / FIXTURE.name)
    return d


def test_main_writes_canonical_url(mod, input_dir, tmp_path, monkeypatch):
    out = tmp_path / "out"
    monkeypatch.setattr("sys.argv", ["x", "--input", str(input_dir), "--output", str(out)])
    mod.main()
    assert (out / "crmi-shareablelibrary.md").exists()
    text = (out / "crmi-shareablelibrary.md").read_text(encoding="utf-8")
    assert (
        "http://hl7.org/fhir/uv/crmi/StructureDefinition/crmi-shareablelibrary"
        in text
    )


def test_main_overwrites_existing_output_without_deleting_unrelated(mod, input_dir, tmp_path, monkeypatch):
    out = tmp_path / "out"
    out.mkdir()
    leftover = out / "stale.md"
    leftover.write_text("stale", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["x", "--input", str(input_dir), "--output", str(out)])
    mod.main()
    assert leftover.exists(), "converter must not delete unrelated outputs"
    assert (out / "crmi-shareablelibrary.md").exists()


def test_operation_parameters_render_documentation(mod, tmp_path, monkeypatch):
    # R4 OperationDefinition.parameter has `documentation`, not `description`.
    src = tmp_path / "in"
    src.mkdir()
    (src / "OperationDefinition-op.json").write_text(json.dumps({
        "resourceType": "OperationDefinition", "id": "op", "url": "http://example.org/op",
        "name": "Op", "status": "active", "kind": "operation", "code": "op",
        "system": False, "type": True, "instance": False,
        "parameter": [{"name": "url", "use": "in", "min": 0, "max": "1", "type": "uri",
                       "documentation": "A canonical | reference\nto package."}],
    }), encoding="utf-8")
    out = tmp_path / "out"
    monkeypatch.setattr("sys.argv", ["x", "--input", str(src), "--output", str(out)])
    mod.main()
    text = next(out.glob("*.md")).read_text(encoding="utf-8")
    assert "| url | in | 0..1 | uri | A canonical \\| reference to package. |" in text


def test_default_paths_anchor_to_module_file(mod, tmp_path, monkeypatch):
    # Sanity: argparse defaults resolve relative to the script's location, even when CWD is elsewhere.
    monkeypatch.chdir(tmp_path)
    args = mod.build_parser().parse_args([])
    default_root = Path(SCRIPT).resolve().parents[1]
    assert Path(args.input) == default_root / "resources/profiles/full-source"
    assert Path(args.output) == default_root / "resources/profiles/concise"

