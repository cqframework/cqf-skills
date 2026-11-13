#!/usr/bin/env python3
"""Show what actually changed in a spec section between versions.

Usage: section_diff.py [--spec-dir DIR] 'page|Heading > Path' ...

For each section (page stem and heading path exactly as in INDEX.md), prints which versions contain
it and, for each CHANGES-*.md list that includes it, the diff lines that remain after removing
noise: lines that differ only by quoting of `define` names (`define X:` vs `define "X":`) or by
sub/superscript markup, and table borders, table and figure captions, and image tags. A list with no
remaining lines is reported as "(quoting/markup only)". Use this before tagging a citation
"(same in …)": read every remaining line.
"""

import argparse
import re
import sys
from pathlib import Path

VERSIONS = ("1.4", "1.5.3", "2.0.0")
CHANGE_LISTS = ("CHANGES-1.4-to-1.5.3.md", "CHANGES-1.5.3-to-2.0.0.md")
INDEX_ROW_RE = re.compile(r"^\| ([^|]+?) \| \[(.+)\]\([^)]+\) \| `([^`]+)` \|$")
NOISE_RE = re.compile(r"[=\s-]*|Table [\d‑-]+.*|Figure [\d‑-]+.*|<div><img.*")


def load_index(spec_dir, version):
    """Return {(page, section path): file} for one version's INDEX.md."""
    rows = {}
    for line in (Path(spec_dir) / version / "INDEX.md").read_text().splitlines():
        m = INDEX_ROW_RE.match(line)
        if m:
            rows[(m.group(1), m.group(2))] = m.group(3)
    return rows


def normalize(line):
    """Strip the +/- marker and the noise that does not change meaning."""
    text = re.sub(r'define "([^"]+)"', r"define \1", line[1:])
    return text.replace("<sub>", "~").replace("</sub>", "~").replace("<sup>", "^").replace("</sup>", "^")


def meaningful_lines(diff_body):
    """Diff lines of one section after removing noise and lines present on both sides."""
    lines = [l for l in diff_body.split("\n") if l and l[0] in "+-" and not l.startswith(("+++", "---"))]
    minus = {normalize(l) for l in lines if l[0] == "-"}
    plus = {normalize(l) for l in lines if l[0] == "+"}
    out = []
    for l in lines:
        n = normalize(l)
        if (l[0] == "+" and n in minus) or (l[0] == "-" and n in plus):
            continue
        if NOISE_RE.fullmatch(n.strip()):
            continue
        out.append(l)
    return out


def section_changes(spec_dir, page, section):
    """Return {change list name: [meaningful lines]} for the lists that include the section."""
    found = {}
    for name in CHANGE_LISTS:
        text = (Path(spec_dir) / name).read_text()
        head = f"### {page}.html: {section}\n"
        i = text.find(head)
        if i < 0:
            continue
        j = text.find("\n### ", i + len(head))
        found[name] = meaningful_lines(text[i + len(head): j if j >= 0 else None])
    return found


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec-dir", default=str(Path(__file__).resolve().parent.parent / "resources" / "spec"))
    ap.add_argument("sections", nargs="+", help="'page|Heading > Path'")
    args = ap.parse_args(argv)
    indexes = {v: load_index(args.spec_dir, v) for v in VERSIONS}
    for arg in args.sections:
        if "|" not in arg:
            ap.error(f"expected 'page|Heading > Path', got {arg!r}")
        page, section = arg.split("|", 1)
        have = [v for v in VERSIONS if (page, section) in indexes[v]]
        print(f"== {page} > {section}  [in: {', '.join(have) or 'none'}]")
        for name, lines in section_changes(args.spec_dir, page, section).items():
            label = name[len("CHANGES-"):-len(".md")]
            print(f"   {label}: " + ("" if lines else "(quoting/markup only)"))
            for l in lines:
                print("      " + l)
    return 0


if __name__ == "__main__":
    sys.exit(main())
