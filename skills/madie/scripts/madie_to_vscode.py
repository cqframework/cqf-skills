#!/usr/bin/env python3
"""Unpack MADiE test cases into the layout the VS Code CQL extension runs.

Takes a MADiE test case export (a zip, or a folder laid out like one) and writes, for each test case:

    <tests>/<Library>/<patient UUID>/<ResourceType>-<id>.json   one file per resource

The extension ignores Bundles in test case folders, so each bundle is split into its resources. The
MeasureReport is kept as a file too: it holds the expected values that check_results.py compares with,
and the extension reads its description. MADiE writes the description under the CQM extension URL
and the extension reads only the CQFM one, so the CQFM extension is added alongside it. The `.madie`
file is copied to <tests>/<Library>/.madie, where the extension ignores it and vscode_to_madie.py
reads the titles and series back.

Usage: madie_to_vscode.py SOURCE --library NAME [--tests DIR] [--force]
  SOURCE     a MADiE test case export zip, or a folder laid out like one
  --library  the CQL library to test (the .cql file name, without .cql)
  --tests    the project's test folder (default: input/tests)
  --force    replace test case folders that already exist
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path, PurePosixPath

UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
CQM_DESCRIPTION = "http://hl7.org/fhir/uv/cqm/StructureDefinition/cqm-testCaseDescription"
CQFM_DESCRIPTION = "http://hl7.org/fhir/us/cqfmeasures/StructureDefinition/cqfm-testCaseDescription"
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9\-.]{1,64}$")


def read_source(path: Path) -> dict[str, str]:
    """{posix path: text} of the files in a zip or folder."""
    if path.is_dir():
        return {p.relative_to(path).as_posix(): p.read_text(encoding="utf-8", errors="replace")
                for p in sorted(path.rglob("*")) if p.is_file()}
    with zipfile.ZipFile(path) as z:
        return {i.filename.replace("\\", "/"): z.read(i).decode("utf-8", errors="replace")
                for i in z.infolist() if not i.is_dir()}


def cases(files: dict[str, str]) -> dict[str, str]:
    """{patient UUID: bundle JSON text} for each <UUID>/<file>.json entry, as MADiE's import reads them."""
    out: dict[str, str] = {}
    for name, text in files.items():
        parts = PurePosixPath(name).parts
        if len(parts) >= 2 and UUID_RE.match(parts[0]) and name.endswith(".json"):
            if parts[0] in out:
                raise ValueError(f"{parts[0]}: more than one JSON file")
            out[parts[0]] = text
    return out


def add_cqfm_description(report: dict) -> bool:
    """Copy a CQM test case description into the CQFM extension the VS Code extension reads."""
    exts = report.setdefault("extension", [])
    if any(e.get("url") == CQFM_DESCRIPTION for e in exts):
        return False
    cqm = next((e for e in exts if e.get("url") == CQM_DESCRIPTION), None)
    if not cqm or not cqm.get("valueMarkdown"):
        return False
    exts.append({"url": CQFM_DESCRIPTION, "valueMarkdown": cqm["valueMarkdown"]})
    return True


def split_bundle(uuid: str, text: str, warnings: list[str]) -> dict[str, dict]:
    """{file name: resource} for one test case bundle."""
    bundle = json.loads(text)
    if bundle.get("resourceType") != "Bundle":
        raise ValueError(f"{uuid}: not a Bundle")
    out: dict[str, dict] = {}
    for entry in bundle.get("entry", []):
        resource = entry.get("resource") if isinstance(entry, dict) else None
        if not isinstance(resource, dict):
            continue
        rtype, rid = resource.get("resourceType"), resource.get("id")
        if not rtype or not rid:
            raise ValueError(f"{uuid}: a resource has no resourceType or id")
        if not SAFE_ID_RE.match(str(rid)):
            raise ValueError(f"{uuid}: {rtype} id {rid!r} can't be used in a file name")
        if rtype == "Patient" and rid != uuid:
            warnings.append(f"{uuid}: the Patient's id is {rid!r}; the extension expects it to equal the folder name")
        if rtype == "MeasureReport":
            add_cqfm_description(resource)
        name = f"{rtype}-{rid}.json"
        if name in out:
            raise ValueError(f"{uuid}: two {rtype} resources with id {rid}")
        out[name] = resource
    if not any(n.startswith("Patient-") for n in out):
        raise ValueError(f"{uuid}: no Patient")
    return out


def measurement_period(resources: dict[str, dict]) -> tuple[str, str] | None:
    for name, r in resources.items():
        if name.startswith("MeasureReport-") and r.get("period", {}).get("start"):
            return r["period"]["start"][:10], r["period"].get("end", "")[:10]
    return None


def convert(source: Path, library: str, tests: Path, force: bool = False) -> tuple[list[str], list[str], set]:
    """Write the test cases; return (written case folders, warnings, measurement periods seen)."""
    files = read_source(source)
    found = cases(files)
    if not found:
        raise ValueError("no <UUID>/<file>.json test cases found (is there a parent folder in the zip?)")
    target = tests / library
    warnings: list[str] = []
    periods = set()
    split = {uuid: split_bundle(uuid, text, warnings) for uuid, text in sorted(found.items())}
    existing = [u for u in split if (target / u).exists()]
    if existing and not force:
        raise ValueError(f"{len(existing)} test case folder(s) already exist under {target}, "
                         f"e.g. {existing[0]}; use --force to replace them")
    for uuid, resources in split.items():
        folder = target / uuid
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)
        for name, resource in resources.items():
            (folder / name).write_bytes((json.dumps(resource, indent=2) + "\n").encode("utf-8"))
        p = measurement_period(resources)
        if p:
            periods.add(p)
        else:
            warnings.append(f"{uuid}: no MeasureReport, so no expected values to check")
    madie = next((n for n in files if n.endswith(".madie")), None)
    if madie:
        (target / ".madie").write_bytes(files[madie].encode("utf-8"))
    else:
        warnings.append("no .madie file: titles and series will come from the Patients' names")
    return sorted(split), warnings, periods


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("source", type=Path)
    ap.add_argument("--library", required=True, help="the CQL library name (the .cql file name)")
    ap.add_argument("--tests", type=Path, default=Path("input/tests"), help="test folder (default input/tests)")
    ap.add_argument("--force", action="store_true", help="replace existing test case folders")
    args = ap.parse_args(argv)
    try:
        written, warnings, periods = convert(args.source, args.library, args.tests, args.force)
    except (ValueError, json.JSONDecodeError, zipfile.BadZipFile, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    for w in warnings:
        print("warning: " + w)
    print(f"wrote {len(written)} test case(s) to {args.tests / args.library}")
    if len(periods) == 1:
        start, end = next(iter(periods))
        print("\nThe measurement period MADiE ran with. Unless the library's parameter default matches it, add\n"
              f"to {args.tests / 'config.jsonc'}:\n")
        print(json.dumps({"parameters": [{"library": args.library, "parameters": [{
            "name": "Measurement Period", "type": "Interval<DateTime>",
            "value": f"Interval[@{start}T00:00:00.000, @{end}T23:59:59.999]"}]}]}, indent=2))
    elif len(periods) > 1:
        print("warning: the MeasureReports give different measurement periods: " + ", ".join(
            f"{s}..{e}" for s, e in sorted(periods)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
