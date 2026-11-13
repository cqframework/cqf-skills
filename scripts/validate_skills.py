#!/usr/bin/env python3
"""Validate skills and the marketplace manifest.

Checks:
  - every skills/<dir>/SKILL.md has YAML frontmatter with a valid `name` and `description`
  - `name` matches the folder name
  - SKILL.md body stays within the recommended length
  - relative links in SKILL.md resolve inside the skill folder
  - .claude-plugin/marketplace.json references only existing skills, and every skill
    belongs to exactly one plugin
  - files that several skills each carry a copy of (SHARED_FILES) are identical in every skill
    that has them, so a fix made in one copy isn't lost in the others

Requires: Python 3.9+, PyYAML.  Usage: python scripts/validate_skills.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
MAX_NAME = 64
MAX_DESCRIPTION = 1024
MAX_BODY_LINES = 500

# Skills must be self-contained, so tooling used by several skills is copied into each one.
# Paths are relative to the skill folder. Edit one copy, then copy it to the others.
SHARED_FILES = [
    "scripts/convert-resource-to-markdown.py",
    "scripts/test_convert_resource.py",
    "scripts/fixtures/crmi-shareablelibrary.json",
    "resources/format-guide.md",
]


def parse_skill(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError("missing YAML frontmatter")
    meta = yaml.safe_load(match.group(1)) or {}
    if not isinstance(meta, dict):
        raise ValueError("frontmatter is not a mapping")
    return meta, match.group(2)


def check_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"{skill_dir.name}: missing SKILL.md"]
    try:
        meta, body = parse_skill(skill_md)
    except (ValueError, yaml.YAMLError) as exc:
        return [f"{skill_dir.name}: {exc}"]

    name = meta.get("name")
    desc = meta.get("description")
    if not isinstance(name, str) or not NAME_RE.match(name) or len(name) > MAX_NAME:
        errors.append(f"{skill_dir.name}: invalid name {name!r}")
    elif name != skill_dir.name:
        errors.append(f"{skill_dir.name}: name {name!r} does not match folder name")
    if not isinstance(desc, str) or not desc.strip():
        errors.append(f"{skill_dir.name}: missing description")
    elif len(desc) > MAX_DESCRIPTION:
        errors.append(f"{skill_dir.name}: description exceeds {MAX_DESCRIPTION} characters")
    if re.search(r"[<>]", f"{name}{desc}"):
        errors.append(f"{skill_dir.name}: name/description must not contain angle brackets")

    if len(body.splitlines()) > MAX_BODY_LINES:
        errors.append(f"{skill_dir.name}: SKILL.md body exceeds {MAX_BODY_LINES} lines")

    for target in LINK_RE.findall(body):
        if re.match(r"^[a-z]+:", target):
            continue  # external URL
        resolved = (skill_dir / target).resolve()
        if not resolved.is_relative_to(skill_dir.resolve()):
            errors.append(f"{skill_dir.name}: link {target!r} points outside the skill folder")
        elif not resolved.exists():
            errors.append(f"{skill_dir.name}: broken link {target!r}")
    return errors


def check_marketplace(skill_names: set[str]) -> list[str]:
    errors: list[str] = []
    data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    seen: dict[str, str] = {}
    for plugin in data.get("plugins", []):
        if plugin.get("source") != "./":
            # Hosted in another repository; its skills are validated there.
            if not isinstance(plugin.get("source"), dict):
                errors.append(f"marketplace: plugin {plugin['name']!r} has an unsupported source")
            continue
        for ref in plugin.get("skills", []):
            skill = Path(ref).name
            if not (ROOT / ref).joinpath("SKILL.md").is_file():
                errors.append(f"marketplace: plugin {plugin['name']!r} references missing skill {ref!r}")
            if skill in seen:
                errors.append(f"marketplace: skill {skill!r} is in both {seen[skill]!r} and {plugin['name']!r}")
            seen[skill] = plugin["name"]
    for name in sorted(skill_names - seen.keys()):
        errors.append(f"marketplace: skill {name!r} is not assigned to any plugin")
    return errors


def check_shared_files(skill_dirs: list[Path]) -> list[str]:
    errors: list[str] = []
    for rel in SHARED_FILES:
        copies = [d / rel for d in skill_dirs if (d / rel).is_file()]
        if len(copies) < 2:
            continue
        # Compare with line endings normalized, so a Windows checkout doesn't differ spuriously.
        first = copies[0].read_bytes().replace(b"\r\n", b"\n")
        for other in copies[1:]:
            if other.read_bytes().replace(b"\r\n", b"\n") != first:
                skill, base = (p.relative_to(SKILLS_DIR).parts[0] for p in (other, copies[0]))
                errors.append(f"shared file {rel}: the copy in skills/{skill} differs from "
                              f"the copy in skills/{base}")
    return errors


def main() -> int:
    skill_dirs = sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()) if SKILLS_DIR.is_dir() else []
    errors: list[str] = []
    for d in skill_dirs:
        errors.extend(check_skill(d))
    errors.extend(check_marketplace({d.name for d in skill_dirs}))
    errors.extend(check_shared_files(skill_dirs))

    for err in errors:
        print(f"ERROR: {err}", file=sys.stderr)
    print(f"Checked {len(skill_dirs)} skill(s): {'FAILED' if errors else 'OK'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
