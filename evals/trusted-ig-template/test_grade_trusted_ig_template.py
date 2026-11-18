"""Tests for grade_trusted_ig_template.py: the reference passes, the task fails, and fixes undone are caught."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import grade_trusted_ig_template as G  # noqa: E402

HERE = Path(__file__).resolve().parent
REFERENCE = HERE / "reference" / "tk-01"
TASK = HERE / "task" / "tk-01"
ANT = Path("scripts") / "ant.xml"


def failed(root: Path) -> set[str]:
    return {label.split()[0] for ok, label in G.grade(root).results if not ok}


def copy(tmp_path: Path) -> Path:
    dest = tmp_path / "tk-01"
    shutil.copytree(REFERENCE, dest)
    return dest


def replace(root: Path, rel: Path, old: str, new: str) -> None:
    f = root / rel
    text = f.read_text(encoding="utf-8")
    assert old in text, old
    f.write_text(text.replace(old, new), encoding="utf-8")


def test_reference_passes():
    assert failed(REFERENCE) == set()


def test_task_fails_every_problem_check():
    assert failed(TASK) == {f"G{n:02d}" for n in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17)}


def test_other_scripts_removed(tmp_path):
    root = copy(tmp_path)
    cfg = json.loads((root / "config.json").read_text(encoding="utf-8"))
    del cfg["otherScripts"]
    (root / "config.json").write_text(json.dumps(cfg), encoding="utf-8")
    assert failed(root) == {"G01", "G02"}


def test_relative_style(tmp_path):
    root = copy(tmp_path)
    replace(root, ANT, 'style="${ig.scripts}/onLoad.xslt"', 'style="scripts/onLoad.xslt"')
    assert failed(root) == {"G03"}


def test_raw_ig_value(tmp_path):
    root = copy(tmp_path)
    replace(root, Path("scripts") / "getVersions.xslt", "normalize-space(f:title/@value)", "f:title/@value")
    assert failed(root) == {"G06"}


def test_gate_by_name(tmp_path):
    root = copy(tmp_path)
    replace(root, ANT, 'unless="${ig.networkprohibited}"', 'unless="ig.networkprohibited"')
    assert failed(root) == {"G08"}


def test_exec_with_ig_value(tmp_path):
    root = copy(tmp_path)
    replace(root, ANT, '<echo file="${dir.temp.includes}/stamp.html"',
            '<exec executable="${ig.scripts}/stamp.sh"><arg value="${igVersion}"/></exec>'
            '<echo file="${dir.temp.includes}/stamp.html"')
    assert failed(root) == {"G09"}


def test_pre_process_with_include(tmp_path):
    root = copy(tmp_path)
    replace(root, Path("scripts") / "processPages.xslt", "<xsl:template match=\"@*|node()\">",
            '<xsl:include href="onLoad.xslt"/><xsl:template match="@*|node()">')
    assert failed(root) == {"G12"}


def test_gemfile(tmp_path):
    root = copy(tmp_path)
    (root / "Gemfile").write_text("gem 'x'\n", encoding="utf-8")
    assert failed(root) == {"G13"}


def test_fix_that_drops_the_stamp(tmp_path):
    root = copy(tmp_path)
    replace(root, ANT, "stamp.html", "other.html")
    assert failed(root) == {"G16"}
