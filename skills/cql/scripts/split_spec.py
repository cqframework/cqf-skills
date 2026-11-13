#!/usr/bin/env python3
"""Split the CQL specification's pages into one file per section.

Usage:
    split_spec.py <spec-source-root> <pages-subdir> <out-dir> <version-label> <base-url> <ref>

<spec-source-root> is an extracted HL7/cql checkout. <pages-subdir> is where the pages live in
that checkout: `input/pages` (markdown, 1.5 and later) or `spec/site/STU4` (AsciiDoc, 1.4).
Writes, under <out-dir>/<version-label>/:
    pages/<page>.<md|adoc>          raw page source, unmodified
    sections/<page>/<NNN>-<anchor>.md
                                    one section per heading, presentation markup stripped so
                                    the text matches the rendered site
    elm/*.xsd                       the ELM schema
    INDEX.md                        every section: heading path, anchor, file, URL

Section paths are heading titles joined with " > ", without the page title, so the same section
has the same path in every version regardless of source format.
"""

import html
import re
import shutil
import sys
from pathlib import Path

PAGE_RE = re.compile(r"^\d\d-.*\.(md|adoc)$")
EXTRA_PAGES = {"elm", "grammar", "tests", "changes"}

# Markdown (1.5 and later)
MD_HEADING_RE = re.compile(r"^(#{1,5})\s+(.*?)\s*$")
MD_TRAILING_ANCHOR_RE = re.compile(r"\s*\{:\s*#([\w-]+)\s*\}\s*$")
MD_BLOCK_ANCHOR_RE = re.compile(r"^\s*\{:\s*#([\w-]+)\s*\}\s*$")
MD_FENCE_RE = re.compile(r"^\s*(```|~~~)")
SPAN_RE = re.compile(r"</?span[^>]*>")
ANCHOR_TAG_RE = re.compile(r'<a name="[^"]*"></a>')

# AsciiDoc (1.4)
ADOC_HEADING_RE = re.compile(r"^(={1,6})\s+(.*?)\s*$")
ADOC_BLOCK_ANCHOR_RE = re.compile(r"^\[\[([\w-]+)(?:,[^\]]*)?\]\]\s*$")
ADOC_DELIM_RE = re.compile(r"^(-{4,}|\.{4,}|={4,}|\+{4,}|_{4,}|\*{4,})\s*$")
ADOC_ATTR_RE = re.compile(r"^:[\w-]+:.*$")
ADOC_ROLE_RE = re.compile(r"\[\.[\w-]+\]#(.*?)#")
ADOC_SECTNUM_RE = re.compile(r"^\d+(\.\d+)*\.?\s+")


def slugify(text: str) -> str:
    """kramdown-style auto id: lowercase, drop punctuation, spaces to hyphens."""
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text).lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return text or "section"


def md_text(line: str) -> str:
    return html.unescape(ANCHOR_TAG_RE.sub("", SPAN_RE.sub("", line)))


def adoc_text(line: str) -> str:
    return ADOC_ROLE_RE.sub(r"\1", line)


def parse(lines, fmt):
    """Yield sections as dicts: level, title, anchor, start, body (list of lines)."""
    sections = []
    current = None
    in_block = None  # the fence/delimiter string that opened the current block
    pending_anchor = None
    seen = {}
    for lineno, line in enumerate(lines, start=1):
        heading = None
        anchor_line = None
        if fmt == "md":
            if MD_FENCE_RE.match(line):
                in_block = None if in_block else "```"
            elif not in_block:
                anchor_line = MD_BLOCK_ANCHOR_RE.match(line)
                heading = MD_HEADING_RE.match(line)
            text = md_text(line)
        else:
            delim = ADOC_DELIM_RE.match(line)
            if delim and (in_block is None or in_block == delim.group(1)):
                in_block = None if in_block else delim.group(1)
            elif not in_block:
                anchor_line = ADOC_BLOCK_ANCHOR_RE.match(line)
                heading = ADOC_HEADING_RE.match(line)
            text = adoc_text(line)

        if anchor_line:
            pending_anchor = anchor_line.group(1)
            continue
        if heading:
            level = len(heading.group(1))
            title = heading.group(2)
            explicit = MD_TRAILING_ANCHOR_RE.search(title) if fmt == "md" else None
            is_explicit = bool(explicit or pending_anchor)
            if explicit:
                anchor = explicit.group(1)
                title = MD_TRAILING_ANCHOR_RE.sub("", title)
            elif pending_anchor:
                anchor = pending_anchor
            else:
                anchor = slugify(title)
            pending_anchor = None
            # Repeated auto ids get a numeric suffix: -1, -2, ... on the markdown-built site
            # (1.5+), but -2, -3, ... on the AsciiDoc-built site (1.4).
            n = seen.get(anchor, 0)
            seen[anchor] = n + 1
            if n and not is_explicit:
                anchor = f"{anchor}-{n + 1 if fmt == 'adoc' else n}"
            title = (md_text(title) if fmt == "md" else adoc_text(title)).strip()
            if fmt == "adoc":
                title = ADOC_SECTNUM_RE.sub("", title)
            page_title = fmt == "adoc" and level == 1
            # The AsciiDoc document title is the page title; markdown pages carry theirs in the
            # IG config instead, so keep it out of the body to match.
            current = {
                "level": 0 if page_title else level,
                "title": title,
                "anchor": "" if page_title else anchor,
                "start": lineno,
                "body": [] if page_title else [text],
            }
            sections.append(current)
            continue
        pending_anchor = None if line.strip() else pending_anchor
        if fmt == "adoc" and ADOC_ATTR_RE.match(line) and current and current["level"] == 0:
            continue
        if current is None:
            current = {"level": 0, "title": "(preamble)", "anchor": "", "start": lineno, "body": []}
            sections.append(current)
        current["body"].append(text)

    stack = []
    for s in sections:
        if s["level"] == 0:
            s["path"] = "(preamble)"
            continue
        stack = [p for p in stack if p[0] < s["level"]] + [(s["level"], s["title"])]
        s["path"] = " > ".join(t for _, t in stack)
    return sections


def split_page(page: Path, out_dir: Path, version: str, base_url: str):
    fmt = "adoc" if page.suffix == ".adoc" else "md"
    lines = page.read_text(encoding="utf-8").splitlines()
    html_name = page.stem + ".html"
    sections = parse(lines, fmt)

    page_dir = out_dir / "sections" / page.stem
    page_dir.mkdir(parents=True, exist_ok=True)
    index_rows = []
    for i, s in enumerate(sections):
        if not "".join(s["body"]).strip():
            continue
        url = f"{base_url}/{html_name}" + (f"#{s['anchor']}" if s["anchor"] else "")
        end = sections[i + 1]["start"] - 1 if i + 1 < len(sections) else len(lines)
        name = f"{i:03d}-{s['anchor'] or 'preamble'}.md"
        header = (
            "<!--\n"
            f"cql-spec-version: {version}\n"
            f"page: {html_name}\n"
            f"section: {s['path']}\n"
            f"url: {url}\n"
            f"source-lines: {page.name}:{s['start']}-{end}\n"
            "-->\n"
        )
        (page_dir / name).write_text(header + "\n".join(s["body"]).rstrip() + "\n", encoding="utf-8")
        index_rows.append((page.stem, s["path"], f"sections/{page.stem}/{name}", url))
    return index_rows


def main():
    src, pages_sub, out, version, base_url, ref = sys.argv[1:7]
    src, out = Path(src), Path(out) / version
    if out.exists():
        shutil.rmtree(out)
    (out / "pages").mkdir(parents=True)

    pages_dir = src / pages_sub
    pages = sorted(
        p for p in pages_dir.iterdir()
        if PAGE_RE.match(p.name) or (p.stem in EXTRA_PAGES and p.suffix in (".md", ".adoc"))
    )
    rows = []
    for page in pages:
        shutil.copy2(page, out / "pages" / page.name)
        rows.extend(split_page(page, out, version, base_url))

    # Layouts differ by version: 1.4 and 1.5.3 keep spec/elm/schema; 2.0.0 moved it to
    # input/images/elm/schema. The test suites published with the spec are out of date and are
    # deliberately not copied: conformance tests come only from cqframework/cql-tests.
    for subs, pattern, dest in (
        (("spec/elm/schema", "input/images/elm/schema"), "*.xsd", "elm"),
    ):
        sub = next((s for s in subs if (src / s).is_dir() and any((src / s).glob(pattern))), None)
        if sub:
            (out / dest).mkdir()
            for f in sorted((src / sub).glob(pattern)):
                shutil.copy2(f, out / dest / f.name)

    with (out / "INDEX.md").open("w", encoding="utf-8") as fh:
        fh.write(f"# CQL specification {version} — section index\n\n")
        fh.write(f"Source: HL7/cql at `{ref}`, `{pages_sub}/`. Base URL: {base_url}\n\n")
        fh.write("| Page | Section | File |\n| --- | --- | --- |\n")
        for page, path, rel, url in rows:
            fh.write(f"| {page} | [{path.replace('|', '/')}]({url}) | `{rel}` |\n")
    print(f"{version}: {len(pages)} pages, {len(rows)} sections -> {out}")


if __name__ == "__main__":
    main()
