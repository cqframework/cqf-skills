#!/usr/bin/env python3
"""Re-wrap overlong prose paragraphs in a markdown file without changing its text.

Usage: reflow_md.py [--width N] FILE ...

Only paragraphs, list items and blockquotes that contain a line longer than the width (default 100)
are re-wrapped. Tables, headings and fenced code are never touched. `[src: …]` citations, inline
code spans and markdown links are kept whole. The file is written only if its text is identical to
the original apart from whitespace (and blockquote markers); otherwise it is left unchanged and the
script exits with status 1.
"""

import argparse
import re
import sys

WORD_RE = re.compile(r"(?:\[src:[^\]]*\]|`[^`]*`|\[[^\]]*\]\([^)]*\)|[^\s])+")
ITEM_RE = re.compile(r"^(\s*)(- |\d+\. )")


def _block_start(line):
    return line.startswith(("|", "#", "```")) or line.strip() == ""


def _wrap(words, first, rest, width):
    out, cur, empty = [], first, True
    for w in words:
        nxt = cur + w if empty else cur + " " + w
        if len(nxt) > width and not empty:
            out.append(cur)
            cur = rest + w
        else:
            cur = nxt
        empty = False
    out.append(cur)
    return out


def same_text(a, b):
    """True if a and b differ only in whitespace and blockquote markers."""
    norm = lambda t: re.sub(r"\s+", " ", re.sub(r"(?m)^> ", "", t)).strip()
    return norm(a) == norm(b)


def reflow(text, width=100):
    """Return text with overlong prose units re-wrapped to width."""
    lines = text.split("\n")
    out, i, fence = [], 0, False
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            fence = not fence
            out.append(line)
            i += 1
            continue
        if fence or _block_start(line):
            out.append(line)
            i += 1
            continue
        item = ITEM_RE.match(line)
        quote = line.startswith("> ")
        lead = item.group(0) if item else ("> " if quote else "")
        j = i + 1
        while (j < len(lines) and not _block_start(lines[j]) and not ITEM_RE.match(lines[j])
               and lines[j].startswith("> ") == quote):
            j += 1
        unit = lines[i:j]
        if any(len(x) > width for x in unit):
            parts = [unit[0][len(lead):]] + [x[2:] if quote else x.strip() for x in unit[1:]]
            rest = "> " if quote else (" " * len(lead) if item else "")
            out += _wrap(WORD_RE.findall(" ".join(parts)), lead, rest, width)
        else:
            out += unit
        i = j
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--width", type=int, default=100)
    ap.add_argument("files", nargs="+")
    args = ap.parse_args(argv)
    status = 0
    for path in args.files:
        with open(path) as f:
            original = f.read()
        new = reflow(original, args.width)
        if not same_text(original, new):
            print(f"{path}: text would change; left unchanged", file=sys.stderr)
            status = 1
            continue
        if new != original:
            with open(path, "w") as f:
                f.write(new)
            print(f"{path}: reflowed")
        else:
            print(f"{path}: unchanged")
    return status


if __name__ == "__main__":
    sys.exit(main())
