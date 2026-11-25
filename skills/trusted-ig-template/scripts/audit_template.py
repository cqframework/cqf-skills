#!/usr/bin/env python3
"""Audit an IG template folder against the trusted template rules.

Usage: python audit_template.py TEMPLATE_DIR [--json]

TEMPLATE_DIR is the folder you publish as the template package (the one holding config.json and
package/package.json). Findings are printed as

    ERROR A04 scripts/ant.xml:52 rule 1: style="scripts/x.xslt" is relative ...

Checks (rule numbers are those of trusted-template-rules.md):
    A01  config.json: script, targets and otherScripts                         (rule 2)
    A02  every ant file is registered and lives in scripts/                    (rules 1, 2)
    A03  stylesheets are .xslt in scripts/; includes and imports too           (rule 3)
    A04  what a script runs or reads is named from ${ig.scripts}               (rules 1, 5, 6)
    A05  <exec> and <java>: fixed program, fixed arguments                      (rules 4, 6)
    A06  <loadproperties> of a generated file: the stylesheet fixes the names  (rule 7)
    A07  inline JavaScript only joins strings and sets properties              (rule 8)
    A08  pre-process transforms: your own single-file .xslt                    (rule 10)
    A09  no Jekyll plugins, Gemfiles or symlinks                               (rule 11)
    A10  <get>: fixed URL, gated on ${ig.networkprohibited}                     (rule 13)
    A11  stylesheets in scripts/ use no extension functions or side outputs    (rules 6, 10)
    A12  a value the publisher didn't set, in a path or written to a file      (rule 9)
    A13  Liquid: IG values escaped, nothing in scripts, no dynamic includes     (rule 12)

The audit is static and errs towards reporting: a WARN is something to look at, not necessarily wrong.
It can't follow every way Ant builds a path; a clean audit is not a review (rule 14).
Exit status: 1 if any ERROR, else 0.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.parsers.expat
from dataclasses import dataclass, field
from pathlib import Path

XSL = "http://www.w3.org/1999/XSL/Transform"
SAFE_ROOT = "${ig.scripts}/"
# Properties a script may use to build a path or argument. Anything else may come from IG content.
FIXED_PROPS = {"ig.scripts", "ig.template", "ig.temp", "ig.root", "basedir"}
# Extension namespaces that let a stylesheet call code or write other files.
EXTENSION_NS = re.compile(r"^(xalan://|java:|http://xml\.apache\.org/(xalan|xslt)/java|"
                          r"http://xml\.apache\.org/xalan/redirect|http://exslt\.org/common/document|"
                          r"org\.apache\.xalan\.xslt\.extensions\.Redirect|http://saxon\.sf\.net/)")
REPLACEABLE = ("content", "includes", "layouts", "data", "translations", "config", "liquid")
JS_DANGER = re.compile(r"\b(eval|Function|load|loadWithNewGlobal|importClass|importPackage|Packages|"
                       r"Runtime|ProcessBuilder|exec|java\.)\b")
PROP_RE = re.compile(r"\$\{([^}]+)\}")
# Attributes that name a file or folder a task writes, reads or lists (A12). <get> is A10's.
PATH_ATTRS = {
    "copy": ("file", "tofile", "todir"), "move": ("file", "tofile", "todir"), "mkdir": ("dir",),
    "delete": ("file", "dir"), "xslt": ("in", "out", "destdir"), "style": ("in", "out", "destdir"),
    "concat": ("destfile",), "zip": ("destfile", "basedir"), "unzip": ("src", "dest"), "echo": ("file",),
    "echoxml": ("file",), "replace": ("file", "dir"), "fileset": ("dir", "file"), "touch": ("file",),
}
# The publisher sets <target>.ig.source and <target>.ig.dest for each target it calls.
PUBLISHER_PROP_RE = re.compile(r"^[\w.\-]+\.ig\.(source|dest)$")
# Liquid (A13)
LIQUID_OUT_RE = re.compile(r"\{\{-?(.*?)-?\}\}", re.S)
ESCAPING_FILTER_RE = re.compile(r"\|\s*(escape|escape_once|url_encode|uri_escape|cgi_escape|xml_escape|"
                                r"slugify|size|plus|minus|times|divided_by|modulo|round|date_to_xmlschema|"
                                r"number_of_words)\b")
# {% include <file> … %}: group 1 is the file name (the parameters after it may hold values safely)
INCLUDE_RE = re.compile(r"\{%-?\s*include(?:_relative)?\s+(\S+)")
# {{[id]}}, {{[lang]}}…: placeholders the publisher fills in per page before Jekyll runs, not Liquid values
PLACEHOLDER_RE = re.compile(r"\{\{\[\w+\]\}\}")
SCRIPT_RE = re.compile(r"<script\b[^>]*>(.*?)</script\s*>", re.S | re.I)
LIQUID_FOLDERS = ("includes", "layouts", "content", "_includes", "_layouts")


# ---------------------------------------------------------------------------------------------
# A small XML tree with line numbers (ElementTree drops them)

@dataclass
class Node:
    tag: str            # "{ns}local" or "local"
    attrib: dict
    line: int
    children: list = field(default_factory=list)
    text: str = ""
    parent: "Node | None" = None
    nsdecls: dict = field(default_factory=dict)

    @property
    def local(self) -> str:
        return self.tag.rsplit("}", 1)[-1]

    @property
    def ns(self) -> str:
        return self.tag[1:].split("}", 1)[0] if self.tag.startswith("{") else ""

    def iter(self):
        yield self
        for c in self.children:
            yield from c.iter()

    def ancestors(self):
        n = self.parent
        while n is not None:
            yield n
            n = n.parent


def parse_xml(path: Path) -> Node | None:
    p = xml.parsers.expat.ParserCreate(namespace_separator="}")
    root: list[Node] = []
    stack: list[Node] = []
    pending_ns: dict = {}

    def fix(name: str) -> str:
        return "{" + name if "}" in name else name

    def start_ns(prefix, uri):
        pending_ns[prefix or ""] = uri

    def start(name, attrs):
        n = Node(fix(name), {fix(k): v for k, v in attrs.items()}, p.CurrentLineNumber,
                 parent=stack[-1] if stack else None, nsdecls=dict(pending_ns))
        pending_ns.clear()
        if stack:
            stack[-1].children.append(n)
        else:
            root.append(n)
        stack.append(n)

    def end(name):
        stack.pop()

    def chars(data):
        if stack:
            stack[-1].text += data

    p.StartNamespaceDeclHandler = start_ns
    p.StartElementHandler = start
    p.EndElementHandler = end
    p.CharacterDataHandler = chars
    try:
        p.Parse(path.read_bytes(), True)
    except xml.parsers.expat.ExpatError:
        return None
    return root[0] if root else None


# ---------------------------------------------------------------------------------------------
# Findings

@dataclass
class Finding:
    level: str
    code: str
    where: str
    rule: str
    message: str

    def __str__(self):
        return f"{self.level} {self.code} {self.where} rule {self.rule}: {self.message}"


class Audit:
    def __init__(self, root: Path):
        self.root = root
        self.findings: list[Finding] = []

    def rel(self, p: Path, line: int | None = None) -> str:
        r = p.relative_to(self.root).as_posix()
        return f"{r}:{line}" if line else r

    def error(self, code, where, rule, msg):
        self.findings.append(Finding("ERROR", code, where, rule, msg))

    def warn(self, code, where, rule, msg):
        self.findings.append(Finding("WARN", code, where, rule, msg))


# ---------------------------------------------------------------------------------------------
# Helpers

def files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
        for d in dirnames:
            yield Path(dirpath) / d
        for f in filenames:
            yield Path(dirpath) / f


def props(value: str) -> set[str]:
    return set(PROP_RE.findall(value))


def fixed_prop(name: str) -> bool:
    """A property the publisher sets: ig.scripts…, basedir, or <target>.ig.source/.ig.dest."""
    return name in FIXED_PROPS or bool(PUBLISHER_PROP_RE.match(name))


def anchored(value: str) -> bool:
    return value.startswith(SAFE_ROOT)


def under_replaceable(value: str) -> bool:
    m = re.match(r"^\$\{ig\.template\}/([^/]+)/", value)
    return bool(m) and m.group(1) in REPLACEABLE


def scripts_path(root: Path, value: str) -> Path | None:
    """${ig.scripts}/x/y -> root/scripts/x/y; ${ig.template}/scripts/x -> root/scripts/x."""
    for prefix in (SAFE_ROOT, "${ig.template}/scripts/"):
        if value.startswith(prefix):
            return root / "scripts" / value[len(prefix):]
    return None


def in_scripts(root: Path, path: Path) -> bool:
    """Whether path is an existing file inside root/scripts."""
    try:
        return path.is_file() and path.resolve().is_relative_to((root / "scripts").resolve())
    except OSError:
        return False


def is_ant(node: Node | None) -> bool:
    return node is not None and node.tag == "project"


# ---------------------------------------------------------------------------------------------
# Checks

def check_config(a: Audit, config: dict) -> tuple[list[str], list[dict]]:
    """A01. Returns the registered ant files and the pre-process entries."""
    where = "config.json"
    registered: list[str] = []
    script = config.get("script")
    if script is not None:
        registered.append(script)
        if "targets" not in config:
            a.error("A01", where, "2", "names a script but no targets (the publisher refuses this)")
        if "otherScripts" not in config:
            a.error("A01", where, "2", "names a script but no otherScripts; list every ant file the script "
                                       "imports, directly or indirectly (use [] if there are none)")
        if not (a.root / script).is_file():
            a.error("A01", where, "2", f"script {script!r} does not exist")
    elif "targets" in config:
        a.warn("A01", where, "2", "has targets but no script")
    others = config.get("otherScripts", [])
    if not isinstance(others, list):
        a.error("A01", where, "2", "otherScripts must be an array")
        others = []
    for s in others:
        registered.append(s)
        if not (a.root / s).is_file():
            a.error("A01", where, "2", f"otherScripts names {s!r}, which does not exist")
    pre = config.get("pre-process", [])
    return registered, pre if isinstance(pre, list) else []


def check_ant_files(a: Audit, registered: list[str]) -> dict[Path, Node]:
    """A02. Every ant project is registered and in scripts/. Returns the parsed ant files."""
    ants: dict[Path, Node] = {}
    for f in files(a.root):
        if f.is_file() and f.suffix.lower() == ".xml":
            node = parse_xml(f)
            if is_ant(node):
                ants[f] = node
    reg = {Path(r).as_posix() for r in registered}
    for f in ants:
        rel = a.rel(f)
        if rel not in reg:
            a.error("A02", rel, "2", "an ant file that config.json doesn't register; add it to otherScripts "
                                     "(or delete it). A child template could replace it unnoticed")
        if not rel.startswith("scripts/"):
            a.error("A02", rel, "1", "ant files belong in scripts/")
    for r in reg:
        if not r.startswith("scripts/"):
            a.error("A02", "config.json", "1", f"{r} is registered outside scripts/")
    return ants


def path_attr_problem(value: str) -> str | None:
    """Why a path a script runs or reads is unsafe, or None."""
    if "{$" in value:
        return "contains '{$' (a mistyped ${...}): Ant leaves it as text, so the path is relative to the IG root"
    if anchored(value) or value.startswith("@{"):
        return None
    if value.startswith("${ig.template}/scripts/"):
        return None
    if under_replaceable(value):
        return "is outside scripts/, where a child template can replace it (rule 5)"
    if not value.startswith("${"):
        return "is relative, so it resolves against the IG's root folder: the IG chooses the file"
    if value.startswith("${ig.root}") or value.startswith("${basedir}"):
        return "is in the IG's folder: the IG chooses the file"
    return "doesn't start with ${ig.scripts}/"


def property_defs(node: Node) -> dict[str, str]:
    """Properties the ant file sets to a literal value (<property name value|location>)."""
    defs = {}
    for n in node.iter():
        if n.tag == "property" and "name" in n.attrib:
            v = n.attrib.get("value", n.attrib.get("location"))
            if v is not None and n.attrib["name"] not in defs:
                defs[n.attrib["name"]] = v
    return defs


def expand(value: str, defs: dict[str, str]) -> str:
    """Replace ${p} by the ant file's own definition of p, until only the publisher's are left."""
    for _ in range(8):
        new = PROP_RE.sub(lambda m: defs.get(m.group(1), m.group(0)), value)
        if new == value:
            break
        value = new
    return value


def check_ant(a: Audit, f: Path, node: Node, generated_by: dict[str, str]) -> None:
    """A03-A07 and A10 for one ant file."""
    macros_with_get: dict[str, list[Node]] = {}
    targets = {n.attrib.get("name"): n for n in node.children if n.tag == "target"}
    defs = property_defs(node)

    for n in node.iter():
        where = a.rel(f, n.line)
        tag = n.tag
        # A04: paths to things the script runs or reads
        checks = {
            "xslt": ["style"], "style": ["style"],
            "import": ["file"], "include": ["file"] if n.parent is node else [],
            "ant": ["antfile"], "subant": ["antfile"],
            "loadfile": ["srcfile", "srcFile"], "loadproperties": ["srcfile", "srcFile"],
            "property": ["file"], "loadresource": [], "taskdef": ["file"], "typedef": ["file"],
            "java": ["jar"], "exec": ["executable"], "apply": ["executable"],
        }.get(tag, [])
        for attr in checks:
            v = n.attrib.get(attr)
            if v is None:
                continue
            if tag in ("loadproperties", "loadfile") and v in generated_by:
                continue  # built from IG content: A06
            why = path_attr_problem(expand(v, defs))
            if why and tag == "loadfile" and "rule 5" in why:
                a.warn("A04", where, "5", f'<{tag} {attr}="{v}"> reads a file a child template can replace. If '
                                          "the script reads it as configuration (like groupings.txt), move it to "
                                          "scripts/ (rule 1); otherwise use the property only as text")
            elif why:
                rule = "5" if "rule 5" in why else ("4" if tag in ("java", "exec", "apply") else "1")
                a.error("A04", where, rule, f'<{tag} {attr}="{v}"> {why}')
            if tag in ("xslt", "style") and attr == "style" and not v.lower().endswith(".xslt"):
                a.error("A03", where, "3", f'stylesheet {v!r} is not a .xslt file')
        # A12: a value the publisher didn't set, in a path, or written into a file
        for attr in PATH_ATTRS.get(tag, ()):
            v = n.attrib.get(attr)
            loose = sorted(x for x in props(expand(v or "", defs)) if not fixed_prop(x))
            if loose:
                a.error("A12", where, "9", f'<{tag} {attr}="{v}"> builds a path from ${{{", ".join(loose)}}}: '
                                           "if any of it can come from the IG or a child template, check it against "
                                           "a strict pattern and that the resolved path stays in the template or "
                                           "temp folder")
        if tag in ("echo", "echoxml") and "file" in n.attrib:
            loose = sorted(x for x in props(expand(n.attrib.get("message", "") + n.text, defs)) if not fixed_prop(x))
            if loose:
                a.warn("A12", where, "9", f'<{tag}> writes ${{{", ".join(loose)}}} into {n.attrib["file"]!r}: '
                                          "escape it for that file (XML, properties, HTML) and check it")
        # A05: programs and their arguments
        if tag in ("exec", "apply"):
            a.warn("A05", where, "4", f"<{tag}> runs a program: check it is a fixed file in scripts/ with fixed "
                                      "arguments")
        if tag == "java" and "jar" not in n.attrib:
            a.warn("A05", where, "4", "<java> without jar=: check the classpath is only jars in scripts/")
        if tag in ("exec", "java", "apply"):
            for arg in (x for x in n.iter() if x.tag == "arg"):
                for attr in ("value", "line", "file", "path"):
                    v = expand(arg.attrib.get(attr, ""), defs)
                    loose = props(v) - FIXED_PROPS
                    if loose:
                        a.error("A05", a.rel(f, arg.line), "6",
                                f"argument uses ${{{', '.join(sorted(loose))}}}: make sure no part of it comes from "
                                "the IG; arguments are fixed")
                    elif "${ig.root}" in v or "${basedir}" in v:
                        a.warn("A05", a.rel(f, arg.line), "6",
                               "the program reads files from the IG's folder: it must treat them as hostile "
                               "content (no includes, no fetching, no code)")
        # A06: loadproperties of a generated file
        if tag == "loadproperties":
            v = n.attrib.get("srcfile", n.attrib.get("srcFile", ""))
            if v in generated_by:
                check_properties_stylesheet(a, where, generated_by[v])
            elif not anchored(v):
                a.warn("A06", where, "7", f"<loadproperties> of {v!r}: if it is built from IG content, the "
                                          "stylesheet that writes it must fix every property name")
        # A07: inline JavaScript
        if tag in ("script", "scriptdef"):
            body = n.text
            m = JS_DANGER.search(body)
            if m:
                a.error("A07", where, "8", f"inline JavaScript uses {m.group(1)!r}; it may only join strings and "
                                           "set properties")
            if "executeTarget" in body and "getProperty" in body:
                a.warn("A07", where, "8", "inline JavaScript runs a target chosen from a property: check the "
                                          "property can't come from IG content")
        # A10: <get>
        if tag == "get":
            src = expand(n.attrib.get("src", ""), defs)
            loose = props(src) - FIXED_PROPS
            if loose:
                a.error("A10", where, "13", f"<get src> uses ${{{', '.join(sorted(loose))}}}; URLs are fixed or "
                                            "built from fixed parts")
            dest = expand(n.attrib.get("dest", ""), defs)
            if dest and not dest.startswith(("${ig.", "@{")):
                a.warn("A10", where, "6", f"<get dest={dest!r}>: check the IG can't choose where it writes")
            owner = next((x for x in n.ancestors() if x.tag in ("target", "macrodef")), None)
            if owner is not None and owner.tag == "macrodef":
                macros_with_get.setdefault(owner.attrib.get("name", ""), []).append(n)
            elif owner is not None and not gated(owner):
                a.error("A10", where, "13", f'<get> in target {owner.attrib.get("name")!r}, which is not gated '
                                            'with unless="${ig.networkprohibited}"')
        # if/unless by name
        if tag == "target":
            for attr in ("if", "unless"):
                if n.attrib.get(attr) == "ig.networkprohibited":
                    a.error("A10", where, "13", f'{attr}="ig.networkprohibited" tests whether the property is '
                                                'set, and the publisher always sets it; use '
                                                f'{attr}="${{ig.networkprohibited}}"')

    # <get> inside a macro: every target that uses the macro must be gated
    for macro, gets in macros_with_get.items():
        users = [t for t in targets.values() if any(x.tag == macro for x in t.iter())]
        for t in users:
            if not gated(t):
                a.error("A10", a.rel(f, t.line), "13", f"target {t.attrib.get('name')!r} uses <{macro}>, which "
                                                       'calls <get>, and is not gated with '
                                                       'unless="${ig.networkprohibited}"')


def gated(target: Node) -> bool:
    return target.attrib.get("unless", "").replace(" ", "") == "${ig.networkprohibited}"


def check_properties_stylesheet(a: Audit, where: str, style: str) -> None:
    """A06: a stylesheet that writes a properties file must not copy a value with its line breaks."""
    path = scripts_path(a.root, style)
    node = parse_xml(path) if path and path.is_file() else None
    if node is None:
        a.warn("A06", where, "7", f"<loadproperties> of a file built by {style!r}, which couldn't be read; "
                                  "check it fixes every property name")
        return
    for n in node.iter():
        if n.ns == XSL and n.local in ("value-of", "copy-of", "apply-templates"):
            sel = n.attrib.get("select", "")
            if n.local != "value-of" or not re.search(r"normalize-space|translate", sel):
                a.error("A06", where, "7", f"{a.rel(path, n.line)} writes <xsl:{n.local} select={sel!r}> into a "
                                           "properties file; wrap IG values in normalize-space() so a line "
                                           "break can't add a property")


def check_stylesheets(a: Audit) -> None:
    """A03 (stylesheets are .xslt, includes resolve in scripts/) and A11 (no extensions)."""
    for f in files(a.root):
        if not f.is_file() or f.suffix.lower() not in (".xml", ".xslt", ".xsl"):
            continue
        node = parse_xml(f)
        if node is None or node.ns != XSL or node.local not in ("stylesheet", "transform"):
            continue
        rel = a.rel(f)
        if f.suffix.lower() != ".xslt":
            a.error("A03", rel, "3", "a stylesheet must be .xslt: other extensions can be replaced by a child "
                                     "template unnoticed")
        if not rel.startswith("scripts/"):
            a.error("A03", rel, "1", "stylesheets belong in scripts/")
        for n in node.iter():
            where = a.rel(f, n.line)
            if n.ns == XSL and n.local in ("include", "import"):
                href = n.attrib.get("href", "")
                if not (href.endswith(".xslt") and "://" not in href and in_scripts(a.root, f.parent / href)):
                    a.error("A03", where, "3", f"xsl:{n.local} href={href!r} must name a .xslt file in scripts/")
            if n.ns == XSL and n.local == "result-document":
                a.error("A11", where, "10", "xsl:result-document: a stylesheet produces its main output and "
                                           "nothing else")
            for prefix, uri in n.nsdecls.items():
                if EXTENSION_NS.match(uri):
                    a.error("A11", where, "6", f"declares the extension namespace {uri!r} (prefix "
                                               f"{prefix or '(default)'}): no extension functions or elements")
            if n.ns and EXTENSION_NS.match(n.ns):
                a.error("A11", a.rel(f, n.line), "6", f"uses an extension element <{n.local}>")


def check_preprocess(a: Audit, pre: list) -> None:
    """A08."""
    for i, e in enumerate(pre):
        if not isinstance(e, dict) or "transform" not in e:
            continue
        t = e["transform"]
        where = f"config.json pre-process[{i}]"
        if not (t.startswith("template/scripts/") and t.endswith(".xslt")):
            a.error("A08", where, "10", f"transform {t!r} must be one of your own .xslt files, "
                                       "template/scripts/<name>.xslt")
            continue
        path = a.root / t[len("template/"):]
        if not path.is_file():
            a.error("A08", where, "10", f"transform {t!r} does not exist in this template")
            continue
        node = parse_xml(path)
        for n in (node.iter() if node else []):
            if n.ns == XSL and n.local in ("include", "import"):
                a.error("A08", a.rel(path, n.line), "10", f"xsl:{n.local} fails in a pre-process transform "
                                                          "(external stylesheet access is off): make it one file")
            if "document(" in " ".join(n.attrib.values()):
                a.error("A08", a.rel(path, n.line), "10", "document() fails in a pre-process transform, and "
                                                          "transforms must not read files")


def check_jekyll(a: Audit) -> None:
    """A09."""
    for p in files(a.root):
        rel = a.rel(p)
        if p.is_symlink():
            a.error("A09", rel, "11", "symbolic link: Jekyll doesn't follow them, and they can point anywhere")
        elif p.is_dir() and p.name == "_plugins":
            a.error("A09", rel, "11", "no Jekyll plugins")
        elif p.is_file() and p.name in ("Gemfile", "gems.rb", "Gemfile.lock"):
            a.error("A09", rel, "11", f"{p.name}: Jekyll runs without your gems")
        elif p.is_file() and p.suffix.lower() == ".rb":
            a.error("A09", rel, "11", "Ruby file: Jekyll plugins aren't allowed")
        elif p.is_file() and p.name in ("_config.yml", "_config.yaml"):
            for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if re.match(r"^(plugins|gems|whitelist|plugins_dir)\s*:", line):
                    a.error("A09", a.rel(p, n), "11", f"{line.split(':')[0]} in _config.yml: no Jekyll plugins")


def check_liquid(a: Audit) -> None:
    """A13: layouts and includes escape what they write, keep values out of scripts, and include fixed files."""
    for p in files(a.root):
        rel = a.rel(p)
        if not (p.is_file() and p.suffix.lower() in (".html", ".htm") and rel.split("/")[0] in LIQUID_FOLDERS):
            continue
        raw = p.read_text(encoding="utf-8", errors="replace")
        # blank out the publisher's placeholders, keeping offsets (and so line numbers) the same
        text = PLACEHOLDER_RE.sub(lambda m: " " * len(m.group(0)), raw)
        line_of = lambda i: text.count("\n", 0, i) + 1  # noqa: E731
        for m in INCLUDE_RE.finditer(text):
            if "{{" in m.group(1):
                a.error("A13", a.rel(p, line_of(m.start())), "12", "the file to include is chosen by a value: "
                                                                     "include only fixed file names")
        scripts = [(m.start(1), m.end(1)) for m in SCRIPT_RE.finditer(text)]
        unescaped = []
        for m in LIQUID_OUT_RE.finditer(text):
            if any(s <= m.start() < e for s, e in scripts):
                a.error("A13", a.rel(p, line_of(m.start())), "12", f"{{{{{m.group(1).strip()}}}}} is written into a "
                                                                     "<script>: put it in an escaped data- attribute "
                                                                     "and read that instead")
                continue
            line = text.splitlines()[line_of(m.start()) - 1]
            if not ESCAPING_FILTER_RE.search(m.group(1)) and "<!--" not in line and "comment" not in line:
                unescaped.append(line_of(m.start()))
        if unescaped:
            a.warn("A13", a.rel(p, unescaped[0]), "12", f"{len(unescaped)} value(s) written without escape or "
                                                        "url_encode: escape IG values, and comment the ones that are "
                                                        "HTML the publisher produced")


def generated_files(ants: dict[Path, Node]) -> dict[str, str]:
    """out= of every <xslt> -> its style, to recognise properties files built from IG content."""
    out = {}
    for node in ants.values():
        for n in node.iter():
            if n.tag in ("xslt", "style") and "out" in n.attrib and "style" in n.attrib:
                out[n.attrib["out"]] = n.attrib["style"]
    return out


def audit(root: Path) -> list[Finding]:
    a = Audit(root)
    config: dict = {}
    cfg = root / "config.json"
    if cfg.is_file():
        try:
            config = json.loads(cfg.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            a.error("A01", "config.json", "2", f"not valid JSON: {e}")
    registered, pre = check_config(a, config)
    ants = check_ant_files(a, registered)
    gen = generated_files(ants)
    for f, node in sorted(ants.items()):
        check_ant(a, f, node, gen)
    check_stylesheets(a)
    check_preprocess(a, pre)
    check_jekyll(a)
    check_liquid(a)
    return a.findings


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("template", type=Path)
    ap.add_argument("--json", action="store_true", help="print findings as JSON")
    args = ap.parse_args(argv)
    if not args.template.is_dir():
        print(f"not a folder: {args.template}", file=sys.stderr)
        return 2
    findings = audit(args.template.resolve())
    if args.json:
        print(json.dumps([f.__dict__ for f in findings], indent=2))
    else:
        for f in findings:
            print(f)
        errors = sum(f.level == "ERROR" for f in findings)
        print(f"{errors} error(s), {len(findings) - errors} warning(s)")
    return 1 if any(f.level == "ERROR" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
