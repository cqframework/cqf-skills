"""Grade a TK-01 project: a CQL project set up for the VS Code CQL extension 1.0.0 / language server 5.0.0.

Static checks of the files the agent wrote, for the mistakes the vscode-cql skill targets: paths the
extension doesn't read, test data it ignores, parameter values that silently drop, terminology that
isn't loaded, and a launch.json the debugger can't use. Running it in VS Code is the stronger check.

Usage: python grade_project.py <project-folder>
Prints one PASS/FAIL line per check and exits 1 if any check fails.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

LIB = "WeightCheck"
TYPES = {"String", "Integer", "Decimal", "Boolean", "DateTime", "Date", "Time", "Quantity",
         "Interval<DateTime>", "Interval<Date>"}
TYPED_NAME = re.compile(r"^[A-Z][A-Za-z]+-[A-Za-z0-9.\-]+\.json$")


def strip_jsonc(text: str) -> str:
    """Remove // and /* */ comments outside strings, and trailing commas."""
    out, i, n, in_str = [], 0, len(text), False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 1
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
            out.append(c)
        elif text.startswith("//", i):
            while i < n and text[i] != "\n":
                i += 1
            continue
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end < 0 else end + 2
            continue
        else:
            out.append(c)
        i += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))


def cql_parameters(cql: str) -> dict[str, str]:
    """Declared parameter name -> declared type text (may be empty)."""
    out = {}
    for m in re.finditer(r'^\s*parameter\s+("([^"]+)"|(\w+))\s*([^\n]*)', cql, re.M):
        name = m.group(2) or m.group(3)
        out[name] = re.sub(r"\s+default\b.*$", "", m.group(4)).strip()
    return out


def grade(project: Path) -> list[tuple[str, bool, str]]:
    results: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> bool:
        results.append((name, ok, detail))
        return ok

    # 1. Project and library
    check("project root has ig.ini", (project / "ig.ini").is_file(),
          "without an ig.ini, Execute CQL loads no value sets and other projects can't use namespaces")
    cql_file = project / "input" / "cql" / f"{LIB}.cql"
    if not check(f"input/cql/{LIB}.cql exists", cql_file.is_file(), "the extension reads only <root>/input/cql"):
        return results
    cql = cql_file.read_text(encoding="utf-8")
    m = re.search(r"^\s*library\s+\"?([\w.]+)\"?", cql, re.M)
    check("library declaration matches the file name", bool(m) and m.group(1).split(".")[-1] == LIB,
          f"declared {m.group(1) if m else None!r}")

    # 2. Test cases: one folder, one resource per file, consistent names, patient id = folder name
    folders = [p for p in (project / "input" / "tests").rglob(LIB) if p.is_dir() and "results" not in p.parts]
    if not check(f"exactly one {LIB} test folder under input/tests", len(folders) == 1,
                 f"found {[str(f.relative_to(project)) for f in folders]}; Execute CQL runs every one, the Explorer shows one"):
        return results
    cases = [d for d in folders[0].iterdir() if d.is_dir() and d.name != "shared"]
    check("at least two test cases", len(cases) >= 2, f"found {len(cases)}")
    bundles, bad_names, wrong_patient, bad_refs = [], [], [], []
    for case in cases:
        files = [f for f in case.rglob("*.json")]
        for f in files:
            try:
                r = json.loads(f.read_text(encoding="utf-8"))
            except ValueError:
                bad_names.append(f"{f.name} (not JSON)")
                continue
            if r.get("resourceType") == "Bundle":
                bundles.append(f.name)
                continue
            if not TYPED_NAME.match(f.name) or not f.name.startswith(r.get("resourceType", "") + "-"):
                bad_names.append(f.name)
            if r.get("resourceType") == "Patient" and r.get("id") != case.name:
                wrong_patient.append(f"{case.name}/{f.name}")
            for key in ("subject", "patient"):
                ref = (r.get(key) or {}).get("reference") if isinstance(r.get(key), dict) else None
                if ref and ref != f"Patient/{case.name}":
                    bad_refs.append(f"{case.name}/{f.name}: {ref}")
        if not any(json.loads(f.read_text(encoding="utf-8")).get("resourceType") == "Patient" for f in files
                   if f.name.startswith("Patient-")):
            wrong_patient.append(f"{case.name}: no Patient-<id>.json")
    check("no Bundles in test cases", not bundles, f"ignored by the server: {bundles}")
    check("every test file is named <ResourceType>-<id>.json", not bad_names,
          f"mixed or id-only names are skipped once type-prefixed names are present: {bad_names}")
    check("each test case has a Patient whose id is the folder name", not wrong_patient, str(wrong_patient))
    check("subject/patient references point at the folder's patient", not bad_refs, str(bad_refs))

    # 3. config.jsonc
    cfg_path = project / "input" / "tests" / "config.jsonc"
    if not check("input/tests/config.jsonc exists", cfg_path.is_file()):
        return results
    try:
        cfg = json.loads(strip_jsonc(cfg_path.read_text(encoding="utf-8")))
    except ValueError as e:
        check("config.jsonc parses", False, f"{e}; the extension silently ignores a file it can't parse")
        return results
    check("resultFormat is individual", cfg.get("resultFormat") == "individual", f"{cfg.get('resultFormat')!r}")
    declared = cql_parameters(cql)
    entries = [p for p in cfg.get("parameters", []) if "library" not in p]
    for block in cfg.get("parameters", []):
        if "library" in block:
            entries += block.get("parameters", [])
            for overrides in (block.get("testCases") or {}).values():
                entries += overrides
    mp = [p for p in entries if p.get("name") == "Measurement Period"]
    check("Measurement Period is configured by its bare name", bool(mp) and "Measurement Period" in declared,
          "name must equal the declared parameter, without CQL double quotes")
    problems = []
    for p in entries:
        name, typ, val = p.get("name"), p.get("type"), str(p.get("value", ""))
        if name not in declared:
            problems.append(f"{name!r} is not declared in the library")
        if typ not in TYPES:
            problems.append(f"{name}: type {typ!r}")
        if typ == "String" and not re.fullmatch(r"'.*'", val):
            problems.append(f"{name}: String value {val!r} needs CQL single quotes")
        if typ and typ.startswith("Interval") and not val.startswith("Interval"):
            problems.append(f"{name}: {val!r} is not an interval literal")
        if typ == "Interval<Date>" and "DateTime" in declared.get(name, ""):
            problems.append(f"{name}: Interval<Date> for a DateTime parameter")
    check("every parameter value is a valid CQL literal for its declared parameter", not problems,
          "; ".join(problems) + " (one bad value drops all configured parameters)")
    excl = cfg.get("testCasesToExclude", [])
    check("one test case excluded with library, testCase and reason",
          len(excl) == 1 and all(k in excl[0] for k in ("library", "testCase", "reason"))
          and excl[0].get("library") == LIB and excl[0].get("testCase") in {c.name for c in cases},
          f"{excl}")

    # 4. Terminology
    vs_urls = re.findall(r"^\s*valueset\s+\"[^\"]+\"\s*:\s*'([^']+)'", cql, re.M)
    found = {}
    for f in (project / "input" / "vocabulary").rglob("*.json") if (project / "input" / "vocabulary").exists() else []:
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
        except ValueError:
            continue
        if r.get("resourceType") == "ValueSet":
            found[r.get("url")] = r
    missing = [u for u in vs_urls if u not in found]
    check("the library declares a value set", bool(vs_urls))
    check("each declared value set is in input/vocabulary, by url", not missing, f"missing {missing}")
    unusable = [u for u in vs_urls if u in found and not found[u].get("expansion")
                and any("filter" in inc or "valueSet" in inc for inc in found[u].get("compose", {}).get("include", []))]
    check("value sets are expanded or simple code lists", not unusable, f"need an expansion: {unusable}")

    # 5. launch.json
    lj = project / ".vscode" / "launch.json"
    if check(".vscode/launch.json exists", lj.is_file()):
        try:
            conf = [c for c in json.loads(strip_jsonc(lj.read_text(encoding="utf-8"))).get("configurations", [])
                    if c.get("type") == "cql"]
        except ValueError:
            conf = []
        c = conf[0] if conf else {}
        check("a cql launch configuration", bool(c))
        uri = str(c.get("libraryUri", ""))
        check("libraryUri is the .cql file as a file: URI", uri.startswith("file:") and uri.endswith(f"/{LIB}.cql"),
              f"{uri!r}")
        check("libraryName and fhirVersion are set", c.get("libraryName") == LIB and c.get("fhirVersion") in
              {"DSTU2", "DSTU3", "R4", "R5"}, f"libraryName={c.get('libraryName')!r} fhirVersion={c.get('fhirVersion')!r}")
        tc = str(c.get("testCaseUri", ""))
        check("testCaseName and testCaseUri name a test case", c.get("testCaseName") in {d.name for d in cases}
              and tc.startswith("file:") and tc.rstrip("/").endswith("/" + str(c.get("testCaseName"))),
              f"testCaseName={c.get('testCaseName')!r} testCaseUri={tc!r}")
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
