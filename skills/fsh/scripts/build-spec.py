#!/usr/bin/env python3
"""Regenerate resources/spec/ from the FHIR Shorthand specification source.

Usage:
    python build-spec.py [SOURCE_DIR]

Without SOURCE_DIR, downloads overview.md and reference.md from HL7/fhir-shorthand at the pinned
commit. With SOURCE_DIR, reads them from that folder instead (for offline use and tests).

The FSH specification (hl7.fhir.uv.shorthand) is published by HL7 under CC0-1.0. This script
removes the publisher's Liquid and HTML markup, splits the language reference into one file per
section, rewrites links between sections, and writes an index. The output is committed, so run
this only when you change the pin or this script. Requires Python 3.9+, no packages.
"""
from __future__ import annotations

import html
import re
import sys
import urllib.request
from pathlib import Path

FSH_VERSION = "3.0.0"
FSH_COMMIT = "b1c724f1d6f7d206ad714ccc0d82ce33110ce0c9"  # tag 3.0.0
RAW = f"https://raw.githubusercontent.com/HL7/fhir-shorthand/{FSH_COMMIT}/input/pagecontent/"
PUBLISHED = "https://hl7.org/fhir/uv/shorthand/"
SOURCES = ("overview.md", "reference.md")
# A level-3 section longer than this is split into one file per level-4 section.
SPLIT_LINES = 400

SKILL = Path(__file__).resolve().parent.parent
OUT = SKILL / "resources" / "spec"


def slugify(heading: str) -> str:
    """GitHub-style anchor for a heading."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def clean(text: str) -> str:
    """Remove publisher markup, keeping the meaning of trial-use and optional markers."""
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\{%\s*include styles\.html\s*%\}\n?", "", text)
    text = re.sub(r"<br/>\n<span style=\"[^\"]*\">(NOTE:[^<]*(?:<[^>]*>[^<]*)*?)</span>\n<br/>",
                  r"> \1", text)
    # Trial-use blocks: {%include tu-div.html%} ... </div>
    text = re.sub(r"\{%\s*include tu-div\.html\s*%\}\n?(.*?)\n?</div>",
                  lambda m: "> **[Trial Use]**\n>\n" + "\n".join(
                      ("> " + line) if line.strip() else ">" for line in m.group(1).split("\n")),
                  text, flags=re.S)
    # One source span closes with <span> instead of </span>.
    text = re.sub(r"\{%\s*include tu-span\.html\s*%\}\s*(.*?)</?span>", r"[TU] \1", text,
                  flags=re.S)
    text = re.sub(r"<span class=\"tuSpan\">(.*?)</span>", r"[TU] \1", text, flags=re.S)
    text = re.sub(r"\{%\s*include tu\.html\s*%\}", "[TU]", text)
    # Optional parts of syntax expressions are orange in the published spec.
    text = re.sub(r"<span class=\"optional\">(.*?)</span>", r"«\1»", text, flags=re.S)
    text = re.sub(r"<span class=\"caption\" id=\"(t\d+)\">(.*?)</span>",
                  r'<a id="\1"></a>**\2**', text)
    text = re.sub(r"<pre><code>(.*?)</code></pre>",
                  lambda m: "```\n" + m.group(1).replace("&nbsp;", " ") + "\n```", text,
                  flags=re.S)
    # One source table cell opens <code> without closing it.
    text = re.sub(r"<code>([^<\n]*?) \|$", r"<code>\1</code> |", text, flags=re.M)
    text = re.sub(r"<code(?: [^>]*)?>(.*?)</code>", lambda m: "`" + html.unescape(m.group(1)) + "`",
                  text)
    # Entities are literal inside fenced code, so decode them there.
    text = re.sub(r"(^[ >]*```.*?^[ >]*```)", lambda m: html.unescape(m.group(1)), text,
                  flags=re.S | re.M)
    text = re.sub(r"<sup>(.*?)</sup>", r"^\1", text)
    text = re.sub(r"\n\{: \.grid \}", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def sections(text: str, level: int) -> list[tuple[str, str]]:
    """Split text at headings of exactly `level` hashes, outside code fences."""
    parts: list[tuple[str, list[str]]] = [("", [])]
    fence = False
    for line in text.split("\n"):
        if line.lstrip(" >").startswith("```"):
            fence = not fence
        m = None if fence else re.match(r"^(#{%d}) (.+)$" % level, line)
        if m:
            parts.append((m.group(2).strip(), [line]))
        else:
            parts[-1][1].append(line)
    return [(title, "\n".join(lines).strip() + "\n") for title, lines in parts]


def headings(text: str) -> list[str]:
    found, fence = [], False
    for line in text.split("\n"):
        if line.lstrip(" >").startswith("```"):
            fence = not fence
        m = None if fence else re.match(r"^(?:> )?#{1,6} (.+)$", line)
        if m:
            found.append(m.group(1).strip())
    return found


def plan(reference: str) -> list[tuple[str, str]]:
    """Return (file name, content) for each reference file, in reading order."""
    files: list[tuple[str, str]] = []
    preamble, *level3 = sections(reference, 3)
    intro = preamble[1]
    for title, body in level3:
        base = slugify(title.replace("FSH ", "").replace("Appendix: ", "appendix "))
        if body.count("\n") <= SPLIT_LINES:
            files.append((base, body))
            continue
        head, *level4 = sections(body, 4)
        for i, (sub, subbody) in enumerate(level4):
            if i == 0:
                subbody = head[1].rstrip() + "\n\n" + subbody
            files.append((f"{base}-{slugify(sub.replace('Defining ', ''))}", subbody))
    numbered = []
    # The reference's short preamble opens the first file.
    files[0] = (files[0][0], intro.rstrip() + "\n\n" + files[0][1])
    for n, (name, body) in enumerate(files, start=1):
        numbered.append((f"{n:02d}-{name.removesuffix('-rules')}.md", body))
    return numbered


def rewrite_links(files: dict[str, str], overview_file: str) -> dict[str, str]:
    anchors: dict[str, str] = {}
    for name, body in files.items():
        for h in headings(body):
            anchors.setdefault(slugify(h), name)
        for tid in re.findall(r'<a id="(t\d+)"></a>', body):
            anchors.setdefault(tid, name)

    def target(name: str, page: str, anchor: str) -> str:
        if page in ("", "reference.html") and anchor:
            dest = anchors.get(anchor)
            if dest is None:
                raise SystemExit(f"{name}: no section has anchor #{anchor}")
            return f"{dest}#{anchor}" if dest != name else f"#{anchor}"
        if page == "reference.html":
            return "README.md"
        if page == "overview.html":
            return overview_file + (f"#{anchor}" if anchor else "")
        return PUBLISHED + page + (f"#{anchor}" if anchor else "")

    out = {}
    for name, body in files.items():
        out[name] = re.sub(
            r"\]\(((?:[a-z_]+\.html)?)(?:#([^)\s]+))?\)",
            lambda m: f"]({target(name, m.group(1), m.group(2) or '')})"
            if m.group(1) or m.group(2) else m.group(0),
            body)
    return out


def build(source: dict[str, str]) -> dict[str, str]:
    overview = clean(source["overview.md"])
    reference = clean(source["reference.md"])
    files = dict(plan(reference))
    files["overview.md"] = "## Overview (informative)\n\n" + overview.strip() + "\n"
    files = rewrite_links(files, "overview.md")
    origin = (f"<!-- Generated by scripts/build-spec.py from the FHIR Shorthand {FSH_VERSION} "
              f"specification (HL7/fhir-shorthand@{FSH_COMMIT[:7]}, CC0-1.0). Do not edit. -->\n\n")
    rows = []
    for name, body in files.items():
        hs = headings(body)
        subs = ", ".join(h for h in hs[1:] if not h.startswith("Step"))[:240]
        rows.append(f"| [{name}]({name}) | {hs[0] if hs else ''} | {subs} | {body.count(chr(10))} |")
    index = (
        f"# FHIR Shorthand {FSH_VERSION} Specification\n\n"
        f"The FSH language reference, split into one file per section. Generated by "
        f"`scripts/build-spec.py` from [HL7/fhir-shorthand]"
        f"(https://github.com/HL7/fhir-shorthand/tree/{FSH_COMMIT}) (CC0-1.0); the published "
        f"specification is at <{PUBLISHED}>.\n\n"
        "Markers carried over from the published spec:\n\n"
        "- `[TU]` and **[Trial Use]** blocks mark trial-use features. Everything else in the "
        "reference is normative, except examples.\n"
        "- In syntax expressions, `«...»` marks an OPTIONAL part (orange text in the published "
        "spec), `{...}` a value to substitute, and `<...>` an element path of the given type.\n\n"
        "| File | Section | Subsections | Lines |\n| --- | --- | --- | --- |\n"
        + "\n".join(rows) + "\n")
    out = {name: origin + body for name, body in files.items()}
    out["README.md"] = index
    return out


def main(argv: list[str]) -> int:
    if len(argv) > 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    source = {}
    for name in SOURCES:
        if len(argv) == 2:
            source[name] = (Path(argv[1]) / name).read_text(encoding="utf-8")
        else:
            with urllib.request.urlopen(RAW + name, timeout=60) as resp:
                source[name] = resp.read().decode("utf-8")
    files = build(source)
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.md"):
        old.unlink()
    for name, body in files.items():
        (OUT / name).write_text(body, encoding="utf-8", newline="\n")
    print(f"Wrote {len(files)} files to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
