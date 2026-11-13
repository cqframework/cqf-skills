#!/usr/bin/env python3
"""Check spec quotes and links in markdown files against the local CQL spec copy.

Usage: check_citations.py [--spec-dir DIR] <file.md> [...]

The spec directory defaults to ../resources/spec relative to this script.

For every double-quoted passage of 25+ characters (quote marks are paired in order; quotes may
wrap across lines within a paragraph, including "> " blockquotes), find its version and check the passage appears verbatim (whitespace- and quote-normalized; "…" or "..." is a gap) in
that version's section files. A quote found in no spec version but in a local guide copy
(--guide-dir, default ../resources/guides) is reported as GUIDE: real text, but guidance, not
spec. The version is the column header when the quote sits in a table
column headed 1.4 / 1.5.3 / 2.0.0; otherwise the quote's own cql.hl7.org link (STU4 is 1.4, N1A
is 1.5.3, no prefix is 2.0.0): the first link after the quote and before the next quote, else
the last link before the quote and after the previous one; otherwise the nearest preceding
version mention in the paragraph, then in earlier paragraphs (default 1.5.3). Reports OK, WRONG-VERSION (found only in other versions) and
NOT-FOUND. Also checks every cql.hl7.org URL with an anchor resolves to a section in an INDEX.md.

Quotes of non-spec text (skill text, error messages) are reported as NOT-FOUND; read the report,
don't treat it as a pass/fail gate.
"""

import argparse
import re
import sys
from pathlib import Path

VERSIONS = ["1.4", "1.5.3", "2.0.0"]
VER_RE = re.compile(r"(?<![\d.])(1\.4|1\.5\.3|1\.5|2\.0\.0|2\.0)(?![\d.])")
URL_RE = re.compile(r"https?://cql\.hl7\.org/[^\s)\]>`\"]+")


MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def norm(s):
    # Inline links render as their text: "[identifier](#identifiers)" reads "identifier".
    s = MD_LINK_RE.sub(r"\1", s)
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"[`*_]", "", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def canon_version(s):
    return {"1.5": "1.5.3", "2.0": "2.0.0"}.get(s, s)


URL_PREFIX_VERSION = {"STU4": "1.4", "N1A": "1.5.3"}


def url_version(url):
    """The spec version a cql.hl7.org URL points at: STU4 is 1.4, N1A is 1.5.3, and a page with
    no prefix (https://cql.hl7.org/09-b-cqlreference.html) is the current 2.0.0. None otherwise."""
    m = re.match(r"https?://cql\.hl7\.org/([^/]+)/", url)
    if m:
        return URL_PREFIX_VERSION.get(m.group(1))
    if re.match(r"https?://cql\.hl7\.org/\d\d-[^/]*$", url):
        return "2.0.0"
    return None


def link_version(para, start, end, prev_end, next_start):
    """Version named by the quote's own link: the first versioned cql.hl7.org URL between the
    quote's end and the next quote, else the last one between the previous quote and this one."""
    links = [(m.start(), url_version(m.group(0))) for m in URL_RE.finditer(para)]
    after = [v for pos, v in links if end <= pos < next_start and v]
    if after:
        return after[0]
    before = [v for pos, v in links if prev_end <= pos < start and v]
    return before[-1] if before else None


class Spec:
    def __init__(self, spec_dir: Path, guide_dir: Path = None):
        self.corpus = {}
        self.urls = set()
        self.guide = ""
        if guide_dir and guide_dir.is_dir():
            self.guide = norm("\n".join(p.read_text(encoding="utf-8", errors="replace")
                                        for p in guide_dir.rglob("*.md")))
        for v in VERSIONS:
            files = (spec_dir / v / "sections").rglob("*.md")
            self.corpus[v] = norm("\n".join(p.read_text(encoding="utf-8") for p in files))
            idx = spec_dir / v / "INDEX.md"
            if idx.exists():
                for m in re.finditer(r"\]\((https://cql\.hl7\.org/[^)]+)\)", idx.read_text()):
                    self.urls.add(m.group(1))

    def found(self, quote, v):
        parts = [norm(p) for p in re.split(r"\s*(?:…|\.\.\.)\s*", quote) if len(p.strip()) >= 8]
        if not parts:
            return None
        pos = 0
        text = self.guide if v == "guide" else self.corpus.get(v, "")
        for p in parts:
            i = text.find(p, pos)
            if i < 0:
                return False
            pos = i + len(p)
        return True


def cells(row):
    return [c.strip() for c in row.strip().strip("|").split("|")]


def paragraphs(text):
    """Yield (start_line, joined_text, table_header, blockquote) for each paragraph outside
    fenced code. Table rows and list items each start a new paragraph; blockquote markers are
    removed, and blockquote is True when the paragraph came from a "> " block. table_header is
    the header row's cells for a table body row, else None."""
    buf, start, in_code, bq = [], 0, False, False
    header, prev_table = None, False
    for n, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            if buf:
                yield start, " ".join(buf), None, bq
                buf = []
            continue
        if in_code:
            continue
        if line.lstrip().startswith("|"):
            if buf:
                yield start, " ".join(buf), None, bq
                buf = []
            if not prev_table:
                header = cells(line)
                prev_table = True
            elif not re.fullmatch(r"\|?[\s:|-]+\|?", line.strip()):
                yield n, line.strip(), header, False
            continue
        prev_table = False
        is_bq = re.match(r"^\s*>", line) is not None
        line = re.sub(r"^\s*>\s?", "", line)
        new_block = not line.strip() or line.lstrip().startswith(("- ", "* ", "#")) \
            or re.match(r"^\s*\d+\.\s", line) or (buf and is_bq != bq)
        if new_block and buf:
            yield start, " ".join(buf), None, bq
            buf = []
        if line.strip():
            if not buf:
                start = n
                bq = is_bq
            buf.append(line.strip())
    if buf:
        yield start, " ".join(buf), None, bq


# A blockquote that is one whole quotation: its inner quote marks belong to the quoted text.
WHOLE_QUOTE_RE = re.compile(r'^\s*["“](.{25,})["”][.,;:]?\s*(?:\[src:[^\]]*\]\s*)*$', re.S)


def quotes(text):
    """Pair quote marks in order (straight or curly) and yield (start, inner) for each pair
    whose inner text is 25+ characters. Pairing in order keeps a short quote from making the
    text between two quotes look like one."""
    marks = [m.start() for m in re.finditer(r"[\"“”]", text)]
    for a, b in zip(marks[0::2], marks[1::2]):
        inner = text[a + 1:b]
        if len(inner) >= 25:
            yield a, inner


def check(path, spec: Spec, out=print):
    text = Path(path).read_text(encoding="utf-8")
    counts = {"OK": 0, "GUIDE": 0, "WRONG-VERSION": 0, "NOT-FOUND": 0, "BAD-URL": 0}
    current = "1.5.3"
    for n, para, header, bq in paragraphs(text):
        for m in URL_RE.finditer(para):
            u = m.group(0).rstrip(".,;")
            if "#" in u and u not in spec.urls:
                counts["BAD-URL"] += 1
                out(f"{path}:{n}: BAD-URL {u}")
        para_ver = None
        # Quote marks inside inline code (`asType="t:Integer"`) are not quotations.
        para = re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), para)
        # In a table whose column headers name versions, a quote takes its column's version.
        col_ver = None
        if header:
            col_ver = [canon_version(h) if VER_RE.fullmatch(h) else None for h in header]
            bounds = [m.start() for m in re.finditer(r"\|", para)]
        found_quotes = list(quotes(para))
        if bq:
            whole = WHOLE_QUOTE_RE.match(para)
            if whole:
                found_quotes = [(whole.start(1), whole.group(1))]
            elif not found_quotes and not para.lstrip().startswith("**"):
                # A blockquote with no quote marks is itself the quotation (callouts that open
                # with bold, such as "**Note:**", are not).
                body = re.sub(r"(?:\s*\[src:[^\]]*\])+\s*$", "", para).strip()
                if len(body) >= 25:
                    found_quotes = [(0, body)]
        spans = [(qs, qs + len(q) + 2) for qs, q in found_quotes]
        for i, (qstart, q) in enumerate(found_quotes):
            v = None
            if col_ver:
                k = sum(1 for b in bounds if b < qstart) - 1
                if 0 <= k < len(col_ver):
                    v = col_ver[k]
            if v is None:
                prev_end = spans[i - 1][1] if i else 0
                next_start = spans[i + 1][0] if i + 1 < len(spans) else len(para)
                v = link_version(para, qstart, spans[i][1], prev_end, next_start)
            if v is None:
                vm = list(VER_RE.finditer(para[:qstart]))
                if vm:
                    para_ver = canon_version(vm[-1].group(1))
                v = para_ver or current
            r = spec.found(q, v)
            if r is None:
                continue
            if r:
                counts["OK"] += 1
                continue
            others = [o for o in VERSIONS if o != v and spec.found(q, o)]
            if not others and spec.guide and spec.found(q, "guide"):
                counts["GUIDE"] += 1
                out(f"{path}:{n}: GUIDE (guide text, not spec): \"{q[:110]}\"")
                continue
            kind = "WRONG-VERSION" if others else "NOT-FOUND"
            counts[kind] += 1
            extra = f" (found in {', '.join(others)})" if others else ""
            out(f"{path}:{n}: {kind} [{v}]{extra}: \"{q[:110]}\"")
        vms = list(VER_RE.finditer(para))
        if vms:
            current = canon_version(vms[-1].group(1))
    out(f"{path}: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
    return counts


def main(argv=None):
    ap = argparse.ArgumentParser()
    resources = Path(__file__).resolve().parent.parent / "resources"
    ap.add_argument("--spec-dir", default=str(resources / "spec"))
    ap.add_argument("--guide-dir", default=str(resources / "guides"),
                    help="local guide copies; a quote found only here is reported as GUIDE")
    ap.add_argument("files", nargs="+")
    args = ap.parse_args(argv)
    spec_dir = Path(args.spec_dir)
    missing = [v for v in VERSIONS if not (spec_dir / v / "sections").is_dir()]
    if missing:
        print(f"error: no spec sections for {', '.join(missing)} under {spec_dir} "
              f"(use --spec-dir)", file=sys.stderr)
        return 2
    spec = Spec(spec_dir, Path(args.guide_dir))
    for p in args.files:
        check(p, spec)
    return 0


if __name__ == "__main__":
    sys.exit(main())
