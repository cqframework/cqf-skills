#!/usr/bin/env python3
"""Check test cases for a US Quality Core measure against MADiE's import rules before uploading them.

Takes a zip, or a folder laid out like one:

    .madie                   JSON array of {patientId, title, series, description}
    <patient UUID>/<x>.json  one FHIR Bundle per folder

Reports what MADiE would reject or quietly change, following the rules in
resources/test-case-files.md and resources/test-case-content.md (MADiE develop, 2026-11-14).
It doesn't run FHIR profile validation or the measure's CQL.

Usage: check_test_cases.py PATH
Exit status: 1 if any error was found, else 0. Warnings never fail.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
# The browser rejects these in a title or series (checkSpecialCharacters.ts); the server allows `_`.
SPECIAL_RE = re.compile(r"[`!@#$%^&*()_+=\[\]{};':\"\\|,.<>/?~]")
POPULATION_CODES = {
    "initial-population", "numerator", "numerator-exclusion", "denominator", "denominator-exclusion",
    "denominator-exception", "measure-population", "measure-population-exclusion", "measure-observation",
}
USQC = "http://fhir.org/guides/onc/us-quality-core/StructureDefinition/"
QICORE = "http://hl7.org/fhir/us/qicore/StructureDefinition/"


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"{where}: {msg}")


def read_entries(path: Path) -> dict[str, str | None]:
    """{posix path: text, or None for a directory} for a zip or a folder."""
    out: dict[str, str | None] = {}
    if path.is_dir():
        for p in sorted(path.rglob("*")):
            rel = p.relative_to(path).as_posix()
            out[rel + "/" if p.is_dir() else rel] = None if p.is_dir() else p.read_text(encoding="utf-8", errors="replace")
        return out
    with zipfile.ZipFile(path) as z:
        for info in z.infolist():
            name = info.filename
            out[name] = None if info.is_dir() else z.read(info).decode("utf-8", errors="replace")
    return out


def split(name: str) -> list[str]:
    """Split a zip entry name the way MADiE does: on '\\' if present, else '/'."""
    return [p for p in (name.split("\\") if "\\" in name else name.split("/")) if p != ""]


def check_layout(entries: dict[str, str | None], rep: Report) -> tuple[dict[str, list[str]], list | None]:
    """Return ({patient UUID: [json entry names]}, parsed .madie or None)."""
    madie_names = [n for n in entries if n.endswith(".madie") and entries[n] is not None]
    metadata = None
    if not madie_names:
        rep.error(".madie", "missing; MADiE rejects the zip (\"Zip file is in an incorrect format\")")
    else:
        if len(madie_names) > 1:
            rep.warn(".madie", f"{len(madie_names)} files end in .madie; MADiE reads the first: {madie_names[0]}")
        if PurePosixPath(madie_names[0]).parent != PurePosixPath("."):
            rep.warn(madie_names[0], "not at the zip root; MADiE still finds it, but its own exports put it there")
        try:
            metadata = json.loads(entries[madie_names[0]] or "")
            if not isinstance(metadata, list):
                rep.error(madie_names[0], "must be a JSON array")
                metadata = None
        except json.JSONDecodeError as e:
            rep.error(madie_names[0], f"not valid JSON: {e}")

    folders: dict[str, list[str]] = {}
    skipped = set()
    for name, text in entries.items():
        parts = split(name)
        if not parts or name.endswith(".madie") or parts[0] == "__MACOSX":
            continue
        if not UUID_RE.match(parts[0]):
            if len(parts) > 1 or text is None:
                skipped.add(parts[0])
            continue
        folders.setdefault(parts[0], [])
        if text is not None and name.endswith(".json"):
            folders[parts[0]].append(name)
    for s in sorted(skipped):
        nested = [n for n in entries if len(split(n)) > 1 and split(n)[0] == s and UUID_RE.match(split(n)[1])]
        if nested:
            rep.error(s + "/", "a parent folder: MADiE needs the UUID folders at the zip root, so it imports "
                               "nothing from here. Zip the folder's contents instead")
        else:
            rep.warn(s + "/", "not named by a UUID; MADiE skips it")
    if not any(folders.values()):
        rep.error("zip", "no <UUID>/<file>.json entries: \"Unable to find any valid test case json\"")
    for uuid, files in sorted(folders.items()):
        if not files:
            rep.error(uuid + "/", "no JSON file: \"Test Case file is missing.\"")
        elif len(files) > 1:
            rep.error(uuid + "/", f"{len(files)} JSON files; MADiE takes one per folder")
    return folders, metadata


def check_metadata(metadata: list | None, folders: dict[str, list[str]], rep: Report) -> dict[str, dict]:
    by_patient: dict[str, dict] = {}
    if metadata is None:
        return by_patient
    for i, md in enumerate(metadata):
        where = f".madie[{i}]"
        if not isinstance(md, dict) or not md.get("patientId"):
            rep.error(where, "needs a patientId")
            continue
        by_patient[str(md["patientId"])] = md
        if str(md["patientId"]) not in folders:
            rep.warn(where, f"no folder named {md['patientId']}; this entry is ignored")
    seen: dict[str, str] = {}
    for uuid in sorted(folders):
        md = by_patient.get(uuid)
        where = f".madie[{uuid}]"
        if md is None:
            rep.warn(where, "no entry; the title and series will come from the Patient's given and family "
                            "names, and the description from the MeasureReport (usually lost)")
            continue
        title, series = str(md.get("title") or ""), str(md.get("series") or "")
        if not title.strip():
            rep.error(where, "title is required")
        for label, value in (("title", title), ("series", series)):
            bad = sorted(set(SPECIAL_RE.findall(value)))
            if bad:
                rep.error(where, f"{label} {value!r} has {' '.join(bad)}; MADiE won't export it (use letters, digits, -)")
        if len(title) + len(series) > 250:
            rep.error(where, "title and series together are over 250 characters")
        key = re.sub(r"\s", "", (series + "|" + title).lower())
        if key in seen:
            rep.error(where, f"same series and title as {seen[key]}; they must be unique in a measure")
        seen[key] = uuid
    return by_patient


def walk_references(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "reference" and isinstance(v, str):
                yield path, v
            else:
                yield from walk_references(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for v in node:
            yield from walk_references(v, path)


def profiles(resource: dict) -> list[str]:
    return [p.split("|")[0] for p in resource.get("meta", {}).get("profile", []) if isinstance(p, str)]


def check_bundle(where: str, text: str, folder: str, rep: Report) -> None:
    try:
        bundle = json.loads(text)
    except json.JSONDecodeError as e:
        rep.error(where, f"not valid JSON: {e}")
        return
    if not isinstance(bundle, dict) or bundle.get("resourceType") != "Bundle":
        rep.error(where, "not a FHIR Bundle")
        return
    if bundle.get("type") != "collection" or any("request" in e for e in bundle.get("entry", []) if isinstance(e, dict)):
        rep.warn(where, "not a collection bundle without request entries; MADiE stores a US Quality Core "
                        "test case as given, so use a collection")
    resources = [e.get("resource") for e in bundle.get("entry", []) if isinstance(e, dict)]
    resources = [r for r in resources if isinstance(r, dict)]
    patients = [r for r in resources if r.get("resourceType") == "Patient"]
    if len(patients) != 1:
        rep.error(where, f"{len(patients)} Patient resources; a test case has exactly one")
    for p in patients:
        if p.get("id") != folder:
            rep.warn(where, f"Patient id {p.get('id')!r} isn't the folder name; MADiE doesn't align them for a "
                            "US Quality Core measure, so set it to the folder's UUID")
        names = p.get("name") or []
        if not any(n.get("given") for n in names if isinstance(n, dict)):
            rep.error(where, "Patient has no given name: a new test case fails with \"Test Case Title is required.\"")
        if names and (not isinstance(names[0], dict) or "family" not in names[0]):
            rep.error(where, "Patient's first name has no family; MADiE's import fails on it")
        for element in ("identifier", "gender"):
            if not p.get(element):
                rep.error(where, f"Patient has no {element}, which QI-Core requires; the test case will be invalid")
    ids: dict[str, str] = {}
    keys = set()
    for r in resources:
        rid, rtype = r.get("id"), r.get("resourceType")
        if not rid:
            rep.error(where, f"a {rtype} has no id")
            continue
        if rid in ids:
            rep.error(where, f"id {rid!r} is used by a {ids[rid]} and a {rtype}; ids must be unique in the bundle")
        ids[rid] = rtype
        keys.add(f"{rtype}/{rid}")
        if rtype != "MeasureReport" and not r.get("meta", {}).get("profile"):
            rep.warn(where, f"{rtype}/{rid} has no meta.profile (a MADiE warning; it isn't profile-validated)")
    for r in resources:
        if r.get("resourceType") == "MeasureReport":
            continue
        for path, ref in walk_references(r):
            if ref.startswith("#"):
                continue
            if ref.startswith("urn:") or "://" in ref:
                rep.error(where, f"{r.get('resourceType')}/{r.get('id')} {path} = {ref!r}: MADiE resolves only "
                                 "<Type>/<id> references, so this resource is left out of execution")
            elif ref not in keys and not ref.startswith("Patient/"):
                level = rep.error if r.get("resourceType") == "Patient" else rep.warn
                level(where, f"{r.get('resourceType')}/{r.get('id')} {path} = {ref!r} isn't in the bundle; "
                             "MADiE leaves this resource out of execution")
    for r in resources:
        qicore = [p for p in profiles(r) if p.startswith(QICORE)]
        if qicore:
            rep.error(where, f"{r.get('resourceType')}/{r.get('id')} declares QI-Core profile {qicore[0]}; a US Quality "
                             f"Core measure validates against {USQC}<id> profiles only")
    reports = [r for r in resources if r.get("resourceType") == "MeasureReport"]
    if not reports:
        rep.warn(where, "no MeasureReport: a new test case is imported with no expected values")
    for mr in reports:
        for gi, g in enumerate(mr.get("group", []), 1):
            gid = str(g.get("id", ""))
            # MADiE takes the group number from the id's last character; no id means group 1.
            if not gid and gi > 1:
                rep.error(where, f"MeasureReport group {gi} has no id, so MADiE reads it as group 1; use Group_{gi}")
            elif gid and not gid[-1:].isdigit():
                rep.error(where, f"MeasureReport group {gi} id {gid!r} must end in its group number (Group_{gi})")
            elif gid and gid[-1] != str(gi % 10):
                rep.warn(where, f"MeasureReport group {gi} id {gid!r} is read as group {gid[-1]}")
            for p in g.get("population", []):
                codes = [c.get("code") for c in p.get("code", {}).get("coding", [])]
                if not any(c in POPULATION_CODES for c in codes):
                    rep.error(where, f"MeasureReport group {gid}: population code {codes} isn't a measure-population code")


def check(path: Path) -> Report:
    rep = Report()
    entries = read_entries(path)
    folders, metadata = check_layout(entries, rep)
    check_metadata(metadata, folders, rep)
    for uuid, files in sorted(folders.items()):
        if len(files) == 1:
            check_bundle(files[0], entries[files[0]] or "", uuid, rep)
    return rep


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("path", type=Path, help="a test case zip, or a folder laid out like one")
    args = ap.parse_args(argv)
    if not args.path.exists():
        print(f"{args.path}: not found", file=sys.stderr)
        return 1
    rep = check(args.path)
    for w in rep.warnings:
        print("WARN ", w)
    for e in rep.errors:
        print("ERROR", e)
    print(f"{len(rep.errors)} errors, {len(rep.warnings)} warnings")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
