"""Grade a TK-01 project: an R4 IG set up so that IG Publisher 3.0.4 compiles a CQL library.

Static checks of the files the agent wrote, based on the ig-publisher skill's pinned behaviour.
Running the publisher is the stronger check; this catches the set-up mistakes the skill targets
without a 3-minute build.

Usage: python grade_ig.py <project-folder>
Prints one PASS/FAIL line per check and exits 1 if any check fails.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

FHIR_NS = "{http://hl7.org/fhir}"
IG_PARAM_EXT = "http://hl7.org/fhir/tools/StructureDefinition/ig-parameter"
CQL_NAME = "ExampleScreening"


def read_ig_ini(project: Path) -> tuple[str, dict[str, str]]:
    raw = (project / "ig.ini").read_bytes()
    text = raw.decode("utf-8", errors="replace")
    keys: dict[str, str] = {}
    section = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
        elif section == "IG" and "=" in line and not line.startswith((";", "#")):
            k, v = line.split("=", 1)
            keys[k.strip()] = v.strip()
    return text, keys


def ig_parameters(ig_path: Path) -> tuple[list[tuple[str, str]], list[str]]:
    """Return (code, value) parameters from an R4 IG resource (JSON or XML), and its fhirVersion."""
    params: list[tuple[str, str]] = []
    if ig_path.suffix == ".json":
        ig = json.loads(ig_path.read_text(encoding="utf-8"))
        versions = ig.get("fhirVersion", [])
        definition = ig.get("definition", {})
        for p in definition.get("parameter", []):
            params.append((p.get("code", ""), p.get("value", "")))
        for ext in definition.get("extension", []):
            if ext.get("url") == IG_PARAM_EXT:
                sub = {e.get("url"): e.get("valueString", e.get("valueCode", "")) for e in ext.get("extension", [])}
                params.append((sub.get("code", ""), sub.get("value", "")))
        return params, versions
    root = ET.parse(ig_path).getroot()
    versions = [e.get("value") for e in root.findall(f"{FHIR_NS}fhirVersion")]
    definition = root.find(f"{FHIR_NS}definition")
    if definition is not None:
        for p in definition.findall(f"{FHIR_NS}parameter"):
            code = p.find(f"{FHIR_NS}code")
            value = p.find(f"{FHIR_NS}value")
            params.append((code.get("value") if code is not None else "", value.get("value") if value is not None else ""))
        for ext in definition.findall(f"{FHIR_NS}extension"):
            if ext.get("url") == IG_PARAM_EXT:
                sub = {}
                for e in ext.findall(f"{FHIR_NS}extension"):
                    v = e.find(f"{FHIR_NS}valueString")
                    if v is None:
                        v = e.find(f"{FHIR_NS}valueCode")
                    sub[e.get("url")] = v.get("value") if v is not None else ""
                params.append((sub.get("code", ""), sub.get("value", "")))
    return params, versions


def json_resources(project: Path, resource_type: str) -> list[tuple[Path, dict]]:
    found = []
    for path in sorted((project / "input").rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (ValueError, UnicodeDecodeError):
            continue
        if isinstance(data, dict) and data.get("resourceType") == resource_type:
            found.append((path, data))
    return found


def norm(p: str) -> str:
    return p.replace("\\", "/").strip().rstrip("/")


def grade(project: Path) -> list[tuple[str, bool, str]]:
    results: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> bool:
        results.append((name, ok, detail))
        return ok

    # 1-3. ig.ini
    if not check("ig.ini exists", (project / "ig.ini").is_file()):
        return results
    text, keys = read_ig_ini(project)
    check("ig.ini starts with [IG]", text.startswith("[IG]"),
          "the publisher ignores an ig.ini whose text does not start with [IG] (no BOM, comment or blank line first)")
    template = keys.get("template", "")
    check("template pinned to a version", bool(re.fullmatch(r"cqf\.fhir\.template#\d+\.\d+\.\d+", template)),
          f"template = {template!r}; expected cqf.fhir.template#<x.y.z>")
    ig_rel = keys.get("ig", "")
    ig_path = project / ig_rel if ig_rel else None
    if not check("ig key names an existing file", bool(ig_path and ig_path.is_file()), f"ig = {ig_rel!r}"):
        return results

    # 4-5. IG resource
    try:
        params, versions = ig_parameters(ig_path)
    except (ValueError, ET.ParseError) as e:
        check("IG resource parses", False, str(e))
        return results
    check("IG is R4", "4.0.1" in versions, f"fhirVersion = {versions}")
    binaries = [norm(v) for c, v in params if c == "path-binary"]
    check("path-binary is set", bool(binaries), "no path-binary parameter: the publisher compiles no CQL")

    # 6. The CQL file sits directly in a path-binary folder
    cql_files = [f for b in binaries for f in (project / b).glob("*.cql")] if binaries else []
    named = [f for f in cql_files if re.search(rf"^\s*library\s+\"?{CQL_NAME}\"?", f.read_text(encoding="utf-8"), re.M)]
    check(f"{CQL_NAME} .cql is directly in a path-binary folder", bool(named),
          f"path-binary = {binaries}; sub-folders of a path-binary folder are not compiled")
    if len([b for b in binaries if any((project / b).glob("*.cql"))]) > 1:
        check("CQL in a single path-binary folder", False, "CQL in more than one folder makes later steps throw")

    # 7. The Library claims the file through ig-loader-
    libraries = [(p, r) for p, r in json_resources(project, "Library")
                 if r.get("name") == CQL_NAME or r.get("id") == CQL_NAME
                 or str(r.get("url", "")).rstrip("/").endswith("/" + CQL_NAME)]
    if not check(f"a Library for {CQL_NAME} exists", bool(libraries)):
        return results
    _, lib = libraries[0]
    file_name = named[0].name if named else f"{CQL_NAME}.cql"
    loaders = [a for a in lib.get("content", []) if str(a.get("id", "")).startswith("ig-loader-")]
    check("Library content has an ig-loader- attachment", bool(loaders))
    if loaders:
        a = loaders[0]
        check("ig-loader- id names the .cql file", a.get("id") == f"ig-loader-{file_name}",
              f"id = {a.get('id')!r}; expected ig-loader-{file_name}")
        extra = sorted(set(a) - {"id", "contentType"})
        check("ig-loader- attachment has only id (and optionally contentType)", not extra,
              f"extra elements {extra}: the publisher leaves such an attachment alone")
    check("Library url ends with the CQL library name", str(lib.get("url", "")).rstrip("/").endswith("/" + CQL_NAME),
          f"url = {lib.get('url')!r}")

    # 8. The Measure names one library whose canonical ends with the CQL library name
    measures = json_resources(project, "Measure")
    if check("a Measure exists", bool(measures)):
        libs = measures[0][1].get("library", [])
        check("Measure has exactly one library, matching the CQL name by its last segment",
              len(libs) == 1 and libs[0].split("|")[0].rstrip("/").split("/")[-1] == CQL_NAME,
              f"library = {libs}")

    # 9. ignoreWarnings.txt
    iw = project / "input" / "ignoreWarnings.txt"
    if check("input/ignoreWarnings.txt exists", iw.is_file()):
        lines = [l.rstrip() for l in iw.read_text(encoding="utf-8-sig").splitlines()]
        check("ignoreWarnings.txt starts with == Suppressed Messages ==",
              bool(lines) and lines[0].strip().lower() == "== suppressed messages ==")
        reason_seen = False
        ordered = True
        messages = 0
        for line in lines[1:]:
            if not line.strip():
                continue
            if line.startswith("# "):
                reason_seen = True
            else:
                messages += 1
                ordered = ordered and reason_seen
        check("every suppressed message follows a '# ' reason", messages > 0 and ordered)
    return results


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    results = grade(Path(argv[1]))
    for name, ok, detail in results:
        print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail and not ok else ""))
    failed = sum(not ok for _, ok, _ in results)
    print(f"{len(results) - failed}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
