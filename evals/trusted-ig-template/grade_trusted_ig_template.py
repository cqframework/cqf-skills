#!/usr/bin/env python3
"""Grade an answer to TK-01: the example template, fixed to follow the trusted template rules.

Usage: python grade_trusted_ig_template.py ANSWER_DIR

ANSWER_DIR is the fixed copy of task/tk-01. The checks are static, and written separately from the
skill's audit script so that the eval doesn't grade the skill with its own tool. Each check says which
of the ten planted problems it covers, and the last group checks the template still does its job.
Exit status: 0 if every check passes, 1 otherwise.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

XSL = "{http://www.w3.org/1999/XSL/Transform}"


@dataclass
class Grade:
    results: list[tuple[bool, str]] = field(default_factory=list)

    def check(self, ok: bool, label: str) -> None:
        self.results.append((bool(ok), label))


def load_xml(p: Path):
    try:
        return ET.parse(p).getroot()
    except (ET.ParseError, OSError):
        return None


def ant_files(root: Path) -> dict[str, ET.Element]:
    out = {}
    for p in root.rglob("*.xml"):
        x = load_xml(p)
        if x is not None and x.tag == "project":
            out[p.relative_to(root).as_posix()] = x
    return out


def stylesheets(root: Path) -> dict[str, ET.Element]:
    out = {}
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in (".xml", ".xslt", ".xsl"):
            x = load_xml(p)
            if x is not None and x.tag in (XSL + "stylesheet", XSL + "transform"):
                out[p.relative_to(root).as_posix()] = x
    return out


def targets(ants: dict[str, ET.Element]) -> dict[str, ET.Element]:
    return {t.get("name"): t for x in ants.values() for t in x.iter("target")}


def grade(root: Path) -> Grade:
    g = Grade()
    try:
        config = json.loads((root / "config.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        config = {}
    ants = ant_files(root)
    sheets = stylesheets(root)
    tg = targets(ants)
    all_tasks = [e for x in ants.values() for e in x.iter()]

    # 1. otherScripts
    registered = {config.get("script")} | set(config.get("otherScripts", []) or [])
    g.check("otherScripts" in config and "scripts/common.xml" in registered,
            "G01 config.json lists scripts/common.xml in otherScripts (problem 1)")
    g.check(all(a in registered for a in ants), "G02 every ant file is registered")

    # 2. relative stylesheet path; 3. .xml stylesheet
    styles = [e.get("style") for e in all_tasks if e.tag in ("xslt", "style") and e.get("style")]
    g.check(styles and all(s.startswith("${ig.scripts}/") for s in styles),
            "G03 every <xslt style> starts with ${ig.scripts}/ (problem 2)")
    g.check(styles and all(s.endswith(".xslt") and (root / "scripts" / s[len("${ig.scripts}/"):]).is_file()
                           for s in styles if s.startswith("${ig.scripts}/")),
            "G04 every stylesheet run is a .xslt file that exists in scripts/ (problem 3)")
    g.check(all(k.endswith(".xslt") and k.startswith("scripts/") for k in sheets),
            "G05 every stylesheet in the template is scripts/*.xslt (problems 3, 9)")

    # 4. loadproperties of IG values
    gv = sheets.get("scripts/getVersions.xslt")
    raw = []
    if gv is not None:
        raw = [v.get("select", "") for v in gv.iter(XSL + "value-of")
               if "@value" in v.get("select", "") and not re.search(r"normalize-space|translate", v.get("select", ""))]
    g.check(gv is not None and not raw,
            "G06 getVersions.xslt passes every IG value through normalize-space() or translate() (problem 4)")

    # 5. groupings.txt
    loads = [e.get("srcFile") or e.get("srcfile") for e in all_tasks if e.tag == "loadfile"]
    g.check("${ig.scripts}/groupings.txt" in loads and (root / "scripts" / "groupings.txt").is_file(),
            "G07 groupings.txt is read from ${ig.scripts}/ and lives in scripts/ (problem 5)")

    # 6. network gate
    sch = tg.get("onGenerate.schemas")
    gets = [e for e in sch.iter("get")] if sch is not None else []
    g.check(sch is not None and sch.get("unless", "").replace(" ", "") == "${ig.networkprohibited}",
            'G08 onGenerate.schemas is gated with unless="${ig.networkprohibited}" (problem 6)')

    # 7. exec with an IG value
    bad_args = [a for e in all_tasks if e.tag in ("exec", "java", "apply") for a in e.iter("arg")
                if re.search(r"\$\{ig(Version|Title)\}", " ".join(a.attrib.values()))]
    g.check(not bad_args, "G09 no program is given an IG value as an argument (problem 7)")

    # 8. eval
    js = [e for e in all_tasks if e.tag in ("script", "scriptdef")]
    g.check(not any(re.search(r"\beval\b", "".join(e.itertext())) for e in js),
            "G10 inline JavaScript doesn't use eval (problem 8)")

    # 9. pre-process transform
    pre = [p for p in config.get("pre-process", []) if isinstance(p, dict)]
    pc = [p for p in pre if p.get("folder") == "input/pagecontent"]
    t = pc[0].get("transform", "") if pc else ""
    tpath = root / t[len("template/"):] if t.startswith("template/") else None
    tsheet = load_xml(tpath) if tpath and tpath.is_file() else None
    g.check(re.fullmatch(r"template/scripts/[\w.\-]+\.xslt", t or "") and tsheet is not None,
            "G11 the pagecontent transform is template/scripts/<name>.xslt and exists (problem 9)")
    g.check(tsheet is not None and not any(e.tag in (XSL + "include", XSL + "import") for e in tsheet.iter()),
            "G12 the pre-process transform is one file, with no include or import (problem 9)")

    # 10. Jekyll
    plugin_files = [p for p in root.rglob("*") if p.name in ("Gemfile", "gems.rb", "_plugins") or p.suffix == ".rb"]
    cfgs = [p for p in root.rglob("_config.yml")]
    plugin_keys = [p for p in cfgs if re.search(r"^(plugins|gems|whitelist)\s*:", p.read_text(encoding="utf-8"), re.M)]
    g.check(not plugin_files and not plugin_keys, "G13 no Gemfile, plugins or plugin settings (problem 10)")

    # Still does its job
    g.check(all(n in tg for n in ("onLoad", "onGenerate", "onCheck", "common.summary")),
            "G14 the onLoad, onGenerate, onCheck and common.summary targets are kept")
    g.check(len(gets) == 1 and gets[0].get("src") == "http://hl7.org/fhir/R4/fhir-single.xsd",
            "G15 the schema is still fetched")
    stamp = tg.get("onGenerate.stamp")
    g.check(stamp is not None and any("stamp.html" in " ".join(e.attrib.values()) for e in stamp.iter()),
            "G16 the footer stamp is still written")
    g.check(tsheet is not None and any("h2" in (e.get("match") or "") for e in tsheet.iter(XSL + "template")),
            "G17 the pagecontent transform still adds heading anchors")
    g.check(any("onGenerate.files" in "".join(e.itertext()) for e in js), "G18 appendArtifacts still sets onGenerate.files")
    return g


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__)
        return 2
    g = grade(Path(argv[0]))
    for ok, label in g.results:
        print(("PASS " if ok else "FAIL ") + label)
    failed = sum(not ok for ok, _ in g.results)
    print(f"{len(g.results) - failed}/{len(g.results)} checks passed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
