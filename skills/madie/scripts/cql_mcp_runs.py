"""Read the test-run records cql-mcp saves for `cql_test_run_suite` and `cql_test_run_file`.

Requires: Python 3.9+, standard library only. Shared by the `cql` and `madie` skills (listed in
SHARED_FILES in scripts/validate_skills.py, so the copies must stay identical).

cql-mcp keeps its runs in `<workspace>/.cql-debug/test-runs/`:

    <timestamp>-<hash8>.json   one run record per run
    latest-<suite>.json        {"hash": "<64 hex>"}, the suite's most recent run
    previous-<suite>.json      the run before that

A run record has `hash`, `timestamp`, `suiteName` and `cases`; each case has `patientId` (the test
case folder name), `status`, `expressions` (a list of `{"name", "value"}`, values formatted as
Execute CQL formats them) and `errors`.

The hash covers the suite, the CQL file, the library name and version, the parameters and the
patient ids, not the data or the results, so re-running a suite on the same cases gives a new run
record with the same hash. A pointer is therefore resolved to the newest run record with that hash.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

RUN_FILE_RE = re.compile(r"^(.*)-([0-9a-fA-F]{8})\.json$")


def _timestamp_key(timestamp: str) -> str:
    """Comparable form of both timestamp spellings cql-mcp uses (2026-09-10T095126906Z and
    2026-09-10T09:51:26.906Z)."""
    return re.sub(r"[^0-9A-Za-z]", "", timestamp).upper()


def is_pointer(path: Path) -> bool:
    return path.name.startswith(("latest-", "previous-")) and path.suffix == ".json"


def load_run(path: Path) -> dict:
    """The run record at `path`: a run record file, or a `latest-`/`previous-` pointer, which is
    resolved to the newest run record in the same folder with the pointer's hash."""
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not is_pointer(path):
        if "cases" not in data:
            raise ValueError(f"{path}: not a cql-mcp run record (no 'cases')")
        return data
    want = str(data.get("hash", "")).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", want):
        raise ValueError(f"{path}: not a cql-mcp run pointer (no 64-digit 'hash')")
    candidates = []
    for f in path.parent.iterdir():
        m = RUN_FILE_RE.match(f.name)
        if not m or is_pointer(f) or m.group(2).lower() != want[:8]:
            continue
        run = json.loads(f.read_text(encoding="utf-8"))
        if str(run.get("hash", "")).lower() == want:
            candidates.append((_timestamp_key(str(run.get("timestamp", m.group(1)))), f.name, run))
    if not candidates:
        raise ValueError(f"{path}: no run record in {path.parent} has hash {want[:8]}")
    return max(candidates, key=lambda c: (c[0], c[1]))[2]


def case_results(run: dict) -> list[tuple[str, dict[str, str], list[str]]]:
    """(patientId, {expression name: formatted value}, error messages) for each case of a run. A case
    the language server crashed on (`errored`) or didn't run (`skipped`) always has an error."""
    out = []
    for case in run.get("cases", []):
        values = {str(e.get("name")): str(e.get("value")) for e in case.get("expressions") or []}
        errors = [e if isinstance(e, str) else json.dumps(e) for e in case.get("errors") or []]
        if case.get("status") in ("errored", "skipped") and not errors:
            errors.append(f"the case was {case['status']} (see the run record)")
        out.append((str(case.get("patientId")), values, errors))
    return out
