#!/usr/bin/env python3
import argparse
import json
import os
import glob
import re
import unicodedata
from pathlib import Path, PurePosixPath, PureWindowsPath

COMPLEXITY_FIELDS = [
    'constraint', 'slicing', 'alias', 'comment', 'mapping',
    'fixedCode', 'fixedUri', 'fixedCanonical', 'fixedString',
    'fixedInteger', 'fixedBoolean', 'patternCodeableConcept',
    'patternQuantity', 'meaningWhenMissing', 'binding', 'condition',
    'representation'
]

# Profiling extensions that must be rendered in element tables.
EXT_TYPE_MUST_SUPPORT = "http://hl7.org/fhir/StructureDefinition/elementdefinition-type-must-support"
EXT_USCDI = "http://hl7.org/fhir/us/core/StructureDefinition/uscdi-requirement"
EXT_ADDITIONAL_BINDING = "http://hl7.org/fhir/tools/StructureDefinition/additional-binding"
EXT_UQC = "http://fhir.org/guides/onc/us-quality-core/StructureDefinition/uscdiplusquality"
EXT_KEY = "http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-keyelement"

# Single anchored emit point for the per-file legend. Sits directly under
# `_header_lines(...)` so any agent reading the top of the file sees the
# flag glossary before the body. Keep both compact renderers on this path.
LEGEND_ANCHOR = "post-header"

# Boilerplate rows hidden from the compact element table (unless the profile changes them).
NOISE_LEAF = {"id", "extension", "modifierExtension"}
NOISE_ROOT = {"id", "meta", "implicitRules", "language", "text", "contained",
              "extension", "modifierExtension"}

GENERATED_MARKER = "<!-- generated: do not edit -->"

FLAG_STYLES = {
    "legacy": {"modifier": "!", "summary": "Σ", "uqc": "UQ"},
    "words": {"modifier": "modifier", "summary": "summary", "uqc": "USCDI+Q"},
}

# ``key`` shares the word style in every mode; there is no legacy glyph for it.
FLAG_TOKENS = {"key": "key"}

# R4 core canonicals look like http://hl7.org/fhir/ValueSet/x (one path segment
# after /fhir/); US Core and friends add another segment and keep their version.
R4_CORE_CANONICAL_RE = re.compile(r"^http://hl7\.org/fhir/[A-Za-z]+/[^/]+$")
OID_RE = re.compile(r"^\d+(?:\.\d+)+$")


def legend_line(flag_uqc=False, *, flag_key=False, flag_uscdi_use=False):
    """One-line legend; ``USCDI``, ``key`` and ``USCDI+Q`` are all lazy/gated.

    Each gated token is set by the per-file renderer when any element in the
    snapshot carries the corresponding extension. R4 has no `uscdi-requirement`
    extension on any element, so its files no longer mention the `USCDI`
    token; US Core files do because they use it.
    """
    tokens = [
        "`MS` mustSupport",
        "`modifier` isModifier",
        "`summary` isSummary",
    ]
    if flag_uscdi_use:
        tokens.append("`USCDI` USCDI requirement")
    if flag_key:
        tokens.append("`key` QI-Core key element")
    if flag_uqc:
        tokens.append("`USCDI+Q` USCDI+ Quality requirement")
    tokens.append("`(MS)` in Type applies to that type or target")
    return "_Legend: " + " · ".join(tokens) + "._"



def clean(text):
    """Collapse whitespace, escape pipes, and NFKC-normalize.

    NFKC coerces ``𝗔𝗗𝗗𝗜𝗧𝗜𝗢𝗡𝗔𝗟 𝗨𝗦𝗖𝗗𝗜:`` (U+1D5xx) and friends into plain
    ASCII, which makes emitted descriptions searchable and saves tokens.
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", str(text))
    text = text.replace("\n", " ").replace("\r", " ").replace("|", "\\|")
    text = " ".join(text.split())
    return text


def truncate(text, length=120):
    text = clean(text)
    if len(text) > length:
        return text[:length - 1] + "…"
    return text


def split_canonical(value):
    """Split a FHIR canonical ``url|version`` into its parts."""
    base, separator, version = str(value or "").partition("|")
    return base, (version if separator else "")


def is_r4_core_canonical(url):
    return bool(R4_CORE_CANONICAL_RE.match(str(url or "")))


def canonical_name(url, *, drop_r4_version=True):
    """Readable canonical label: ``id@version``, with the R4 core version dropped."""
    base, version = split_canonical(url)
    name = url_tail(base)
    if not version:
        return name
    if drop_r4_version and version == "4.0.1" and is_r4_core_canonical(base):
        return name
    return f"{name}@{version}"


def _is_placeholder_text(text, el):
    """True when a short/definition merely echoes the element's id or name."""
    value = str(text or "").strip().rstrip(". ")
    if not value:
        return True
    identifiers = {str(el.get("id") or "").strip(), str(el.get("path") or "").strip()}
    for identifier in identifiers:
        if not identifier:
            continue
        if value == identifier or value == identifier.rsplit(".", 1)[-1]:
            return True
    return False


def _first_sentence(text):
    text = clean(text)
    match = re.match(r"(.+?[.!?])(?:\s|$)", text)
    return match.group(1) if match else text


def short_text(el, length=120):
    """Description cell: prefer `short`, fall back to `definition`, skip placeholders."""
    for key in ("short", "definition"):
        raw = el.get(key) or ""
        if not raw or _is_placeholder_text(raw, el):
            continue
        text = clean(raw)
        # `(USCDI+ Quality)` and friends carry no meaning on their own.
        if re.fullmatch(r"\([^)]*\)", text):
            continue
        if key == "definition":
            text = _first_sentence(text)
        if "|" in text:
            return text
        return truncate(text, length)
    return ""


def url_tail(url):
    if not url:
        return ""
    return str(url).replace("\\", "/").rstrip("/").rsplit("/", 1)[-1]


def path_stem(path):
    """Filename stem for POSIX and Windows paths, regardless of host OS."""
    text = str(path)
    if "\\" in text:
        return PureWindowsPath(text).stem
    return PurePosixPath(text).stem


def _ext_with_url(extensions, url):
    for ext in extensions or []:
        if ext.get("url") == url:
            return ext
    return None


def has_ext(el, url):
    return _ext_with_url(el.get("extension"), url) is not None


def true_ext(el, url):
    """True only when the named boolean extension is present with valueBoolean true."""
    ext = _ext_with_url(el.get("extension"), url)
    return bool(ext and ext.get("valueBoolean") is True)


def additional_bindings(el):
    """Additional bindings carried on el.binding (tools IG extension)."""
    binding = el.get("binding") or {}
    out = []
    for ext in binding.get("extension", []) or []:
        if ext.get("url") != EXT_ADDITIONAL_BINDING:
            continue
        item = {}
        for sub in ext.get("extension", []) or []:
            key = sub.get("url", "")
            item[key] = (sub.get("valueCanonical") or sub.get("valueCode")
                         or sub.get("valueMarkdown") or sub.get("valueString") or "")
        out.append(item)
    return out


def flags_from_element(el, flag_uscdi=False, flag_uqc=False, style="legacy"):
    tokens = FLAG_STYLES.get(style, FLAG_STYLES["legacy"])
    parts = []
    if el.get("mustSupport"):
        parts.append("MS")
    if el.get("isModifier"):
        parts.append(tokens["modifier"])
    if el.get("isSummary"):
        parts.append(tokens["summary"])
    # QI-Core key element is identified by the extension on the element
    # itself; we always render ``key`` when present so the same flag column
    # semantics apply regardless of which package is being emitted.
    if true_ext(el, EXT_KEY):
        parts.append(FLAG_TOKENS["key"])
    if flag_uscdi and true_ext(el, EXT_USCDI):
        parts.append("USCDI")
    if flag_uqc and true_ext(el, EXT_UQC):
        parts.append(tokens["uqc"])
    return " ".join(parts)


def type_str_from_element(el):
    types = el.get("type", [])
    if not types:
        content_ref = el.get("contentReference", "")
        if content_ref:
            return f"see {content_ref.lstrip('#')}"
        return "Inherited"
    type_parts = []
    for t in types:
        code = t.get("code", "")
        profiles = t.get("profile", [])
        targets = t.get("targetProfile", [])
        type_ms = true_ext(t, EXT_TYPE_MUST_SUPPORT)
        if targets:
            target_meta = t.get("_targetProfile", [])
            rendered = []
            for i, target in enumerate(targets):
                meta = target_meta[i] if i < len(target_meta) else {}
                ms = true_ext(meta, EXT_TYPE_MUST_SUPPORT) if meta else False
                label = canonical_name(target)
                rendered.append(f"{label} (MS)" if ms else label)
            type_parts.append(f"{code}({' | '.join(rendered)})")
        elif profiles:
            profile_names = [canonical_name(p) for p in profiles]
            type_parts.append(f"{code}({', '.join(profile_names)})")
        else:
            type_parts.append(f"{code} (MS)" if type_ms else code)
    return ", ".join(type_parts)


def cardinality_str(el):
    min_val = el.get("min", 0)
    max_val = el.get("max", "*")
    return f"{min_val}..{max_val}"


def binding_str(el):
    binding = el.get("binding")
    if not binding:
        return ""
    strength = binding.get("strength", "")
    value_set = str(binding.get("valueSet", "") or "")
    base, version = split_canonical(value_set)
    version = version or str(binding.get("version", "") or "")
    if base:
        tail = url_tail(base)
        if OID_RE.match(tail):
            # OID value sets are meaningless without their CTS URL.
            label = base
        elif version:
            label = f"{tail}@{version}"
        else:
            label = tail
        return f"{strength}→{label}" if strength else label
    elif binding.get("description"):
        return binding.get("description", "")
    return strength


def _coding_text(coding):
    system = coding.get("system", "")
    code = coding.get("code", "")
    if system and code:
        return f"{system}#{code}"
    return code or coding.get("display", "") or system


def _value_text(value):
    if isinstance(value, list):
        return ", ".join(text for text in (_value_text(item) for item in value) if text)
    if isinstance(value, dict):
        if "coding" in value:
            codings = ", ".join(
                text for text in (_coding_text(c) for c in value.get("coding") or []) if text
            )
            if value.get("text"):
                codings = f"{codings} \"{value['text']}\"" if codings else f"\"{value['text']}\""
            return codings
        if "system" in value and "code" in value:
            return _coding_text(value)
        if "system" in value and "value" in value:
            return f"{value['system']}#{value['value']}"
        if "value" in value:
            unit = value.get("unit") or value.get("code") or ""
            return f"{value['value']} {unit}".strip()
        if "reference" in value:
            return f"Reference({value['reference']})"
        if "text" in value:
            return str(value["text"])
        return json.dumps(value, separators=(",", ":"), sort_keys=True)
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def fixed_pattern_text(el):
    """Summarize every fixed[x]/pattern[x] on an element."""
    parts = []
    for key, value in el.items():
        if key.startswith("fixed"):
            prefix, kind = "fixed", key[len("fixed"):]
        elif key.startswith("pattern"):
            prefix, kind = "pattern", key[len("pattern"):]
        else:
            continue
        text = _value_text(value)
        if text:
            parts.append(f"{prefix} {kind}: {text}")
    return "; ".join(parts) or "—"


def slicing_text(el):
    slicing = el.get("slicing")
    if not slicing:
        return "—"
    parts = []
    discriminators = []
    for discriminator in slicing.get("discriminator", []) or []:
        kind = discriminator.get("type", "")
        path = discriminator.get("path", "")
        discriminators.append(f"{kind}@{path}" if path else kind)
    if discriminators:
        parts.append("discriminator " + "; ".join(discriminators))
    if slicing.get("rules"):
        parts.append(f"rules={slicing['rules']}")
    if slicing.get("ordered"):
        parts.append("ordered")
    return ", ".join(parts) or "—"


def has_complexity(el):
    return any(el.get(f) for f in COMPLEXITY_FIELDS)


EXT_STANDARDS_STATUS = "http://hl7.org/fhir/StructureDefinition/structuredefinition-standards-status"
EXT_FMM = "http://hl7.org/fhir/StructureDefinition/structuredefinition-fmm"
EXT_WG = "http://hl7.org/fhir/StructureDefinition/structuredefinition-wg"


def _lifecycle_and_context_lines(profile):
    """Header lines for standards status, maturity and work group, and, for an extension
    definition, the contexts it may be used in and any context invariants."""
    lines = []
    meta = {}
    reasons = []
    for ext in profile.get("extension") or []:
        url = ext.get("url")
        if url == EXT_STANDARDS_STATUS:
            meta["Standards Status"] = ext.get("valueCode")
            # Why an artifact is deprecated (and what replaces it) is an extension on the code.
            for sub in (ext.get("_valueCode") or {}).get("extension") or []:
                if sub.get("url") == EXT_STANDARDS_STATUS + "-reason":
                    reasons.append(clean(sub.get("valueMarkdown") or sub.get("valueString") or ""))
        elif url == EXT_FMM:
            meta["FMM"] = ext.get("valueInteger")
        elif url == EXT_WG:
            meta["WG"] = ext.get("valueCode")
    parts = [f"**{k}:** {meta[k]}" for k in ("Standards Status", "FMM", "WG")
             if meta.get(k) not in (None, "")]
    if parts:
        lines.append(" | ".join(parts))
    reasons = [r for r in reasons if r]
    if reasons:
        lines.append(f"**Status Reason:** {' '.join(reasons)}")
    if profile.get("type") == "Extension" and profile.get("derivation") == "constraint":
        contexts = [f"{c.get('type', '')} `{c.get('expression', '')}`"
                    for c in profile.get("context") or []]
        if contexts:
            lines.append(f"**Context:** {'; '.join(contexts)}")
        invariants = [f"`{clean(i)}`" for i in profile.get("contextInvariant") or []]
        if invariants:
            lines.append(f"**Context invariant:** {'; '.join(invariants)}")
    return lines


def convert_structure_definition(profile, output_dir, json_filepath):
    snapshot = profile.get("snapshot", {})
    snapshot_elements = snapshot.get("element", [])

    md = []

    base_def = profile.get("baseDefinition", "")
    derivation = profile.get("derivation", "")
    kind = profile.get("kind", "")
    abstract = profile.get("abstract", False)
    title = profile.get("title", profile.get("name", "Unnamed Profile"))
    profile_id = profile.get("id", "Unknown-ID")
    url = profile.get("url", "")
    status = profile.get("status", "unknown")
    publisher = profile.get("publisher", "")
    date = profile.get("date", "")
    version = profile.get("version", "0.0.1")

    md.append(f"# Profile: {title}")
    md.append(f"**ID:** `{profile_id}` | **URL:** `{url}` | **Status:** {status}")
    md.append(f"**Base:** {os.path.basename(base_def) if base_def else 'none'} | **Derivation:** {derivation} | **Kind:** {kind} | **Abstract:** {str(abstract).lower()}")
    if publisher or date or version:
        md.append(f"**Publisher:** {publisher} | **Date:** {date} | **Version:** {version}")
    md.extend(_lifecycle_and_context_lines(profile))
    md.append("")

    description = profile.get("description", "")
    if description:
        md.append(f"## Description\n{clean(description)}\n")

    md.append("## Elements")
    md.append("| Path | Card | Type | Flags | Binding | Description |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")

    detail_sections = []

    for el in snapshot_elements:
        path = el.get("id", el.get("path", ""))
        card = cardinality_str(el)
        type_str = type_str_from_element(el)
        if type_str == "Inherited" and el.get("path") == profile.get("type"):
            type_str = profile.get("type", "")
        fl = flags_from_element(el)
        bind = binding_str(el)
        short = short_text(el)
        slice_name = el.get("sliceName", "")

        path_label = f"`{display_path(el)}`"

        md.append(
            f"| {path_label} | {card} | `{clean(type_str)}` | {fl} | {clean(bind)} | {short} |"
        )

        if has_complexity(el):
            section = build_element_detail(el, display_path(el))
            if section:
                detail_sections.append(section)

    if detail_sections:
        md.append("")
        md.append("## Element Details")
        md.extend(detail_sections)

    write_output(md, json_filepath, output_dir)


def build_element_detail(el, path):
    lines = []
    header_path = path or display_path(el)

    lines.append(f"### `{header_path}`")

    card = cardinality_str(el)
    type_str = type_str_from_element(el)
    base_info = el.get("base", {})
    base_path = base_info.get("path", "")
    base_min = base_info.get("min", "")
    base_max = base_info.get("max", "")
    base_str = f"({base_path}, {base_min}..{base_max})" if base_path else ""

    lines.append(f"- **Cardinality:** {card}")
    lines.append(f"- **Type:** {type_str}")
    if base_str:
        lines.append(f"- **Base:** {base_str}")

    fl = flags_from_element(el)
    if fl:
        is_mod = el.get("isModifier", False)
        is_sum = el.get("isSummary", False)
        flags_detail = []
        if 'MS' in fl:
            flags_detail.append("MustSupport=true")
        if '!' in fl:
            flags_detail.append(f"isModifier={str(is_mod).lower()}")
        if 'Σ' in fl:
            flags_detail.append(f"isSummary={str(is_sum).lower()}")
        lines.append(f"- **Flags:** {', '.join(flags_detail)}")

    bind = el.get("binding")
    if bind:
        strength = bind.get("strength", "")
        vs = bind.get("valueSet", "")
        desc = bind.get("description", "")
        lines.append(f"- **Binding:** {strength} → {vs}")
        if desc:
            lines.append(f"  - Description: {clean(desc)}")

    short = el.get("short", "")
    if short:
        lines.append(f"- **Short:** {clean(short)}")

    definition = el.get("definition", "")
    if definition:
        lines.append(f"- **Definition:** {clean(definition)}")

    aliases = el.get("alias", [])
    if aliases:
        lines.append(f"- **Alias:** [{', '.join(aliases)}]")

    comment = el.get("comment", "")
    if comment:
        lines.append(f"- **Comment:** /* {clean(comment)} */")

    constraints = el.get("constraint", [])
    for c in constraints:
        key = c.get("key", "")
        sev = c.get("severity", "")
        human = c.get("human", "")
        expr = c.get("expression", "")
        source = c.get("source", "")
        lines.append(f"- **Constraint:** {key} ({sev}): {human}")
        if expr:
            lines.append(f"  - Expression: `{expr}`")
        if source:
            lines.append(f"  - Source: {os.path.basename(source) if source else ''}")

    slicing = el.get("slicing", {})
    if slicing:
        disc = slicing.get("discriminator", [])
        ordered = slicing.get("ordered", False)
        rules = slicing.get("rules", "")
        desc = slicing.get("description", "")
        disc_parts = []
        for d in disc:
            dt = d.get("type", "")
            dp = d.get("path", "")
            disc_parts.append(f"type={dt}, path={dp}")
        lines.append(f"- **Slicing:** discriminator: ({'; '.join(disc_parts)}), ordered={str(ordered).lower()}, rules={rules}")
        if desc:
            lines.append(f"  - Description: {clean(desc)}")

    fixed_uri = el.get("fixedUri")
    if fixed_uri:
        lines.append(f"- **Fixed URI:** `{fixed_uri}`")

    fixed_canonical = el.get("fixedCanonical")
    if fixed_canonical:
        lines.append(f"- **Fixed Canonical:** `{fixed_canonical}`")

    fixed_string = el.get("fixedString")
    if fixed_string:
        lines.append(f"- **Fixed String:** `{fixed_string}`")

    fixed_code = el.get("fixedCode")
    if fixed_code:
        lines.append(f"- **Fixed Code:** `{fixed_code}`")

    pattern_cc = el.get("patternCodeableConcept")
    if pattern_cc:
        codings = pattern_cc.get("coding", [])
        if codings:
            code = codings[0].get("code", "")
            system = codings[0].get("system", "")
            display = codings[0].get("display", "")
            lines.append(f"- **Pattern CodeableConcept:** code=`{code}`, system=`{system}`, display=`{display}`")

    pattern_qty = el.get("patternQuantity")
    if pattern_qty:
        val = pattern_qty.get("value", "")
        comp = pattern_qty.get("comparator", "")
        unit = pattern_qty.get("unit", "")
        lines.append(f"- **Pattern Quantity:** value={val}, comparator={comp}, unit={unit}")

    mappings = el.get("mapping", [])
    for m in mappings:
        identity = m.get("identity", "")
        m_map = m.get("map", "")
        if identity and m_map:
            lines.append(f"- **Mapping:** {identity}→{m_map}")

    condition = el.get("condition", [])
    if condition:
        lines.append(f"- **Condition:** {', '.join(condition)}")

    representation = el.get("representation", [])
    if representation:
        lines.append(f"- **Representation:** {', '.join(representation)}")

    meaning_when = el.get("meaningWhenMissing")
    if meaning_when:
        lines.append(f"- **Meaning When Missing:** {clean(meaning_when)}")

    lines.append("")
    return "\n".join(lines)


def display_path(el):
    eid = el.get("id") or el.get("path", "")
    slice_name = el.get("sliceName", "")
    if slice_name and not eid.endswith(":" + slice_name):
        return f"{eid}:{slice_name}"
    return eid


def _snapshot(profile):
    return (profile.get("snapshot") or {}).get("element", [])


def _differential(profile):
    return (profile.get("differential") or {}).get("element", [])


def _section(lines, title):
    lines.append("")
    lines.append(f"## {title}")
    lines.append("")


def _header_lines(profile, package=None):
    title = profile.get("title") or profile.get("name") or "Unnamed Profile"
    lines = [f"# {title}", ""]
    lines.append(
        f"**ID** `{profile.get('id', '')}` | **URL** `{profile.get('url', '')}` | "
        f"**Status** {profile.get('status', 'unknown')}"
    )
    lines.append(
        f"**Base** `{url_tail(profile.get('baseDefinition', ''))}` | "
        f"**Derivation** {profile.get('derivation', '')} | **Kind** {profile.get('kind', '')}"
    )
    extra = []
    if profile.get("version"):
        extra.append(f"**Version** {profile['version']}")
    if profile.get("publisher"):
        extra.append(f"**Publisher** {clean(profile['publisher'])}")
    if package:
        extra.append(f"**Package** `{package}`")
    if extra:
        lines.append(" | ".join(extra))
    return lines


def _is_noise(el, profile_type, differential_ids):
    eid = el.get("id") or el.get("path", "")
    if el.get("sliceName") or el.get("mustSupport"):
        return False
    if eid in differential_ids:
        return False
    if eid == profile_type:
        return False
    leaf = eid.rsplit(".", 1)[-1]
    if eid.count(".") == 1:
        return leaf in NOISE_ROOT
    return leaf in NOISE_LEAF


def _declared_keys(el, base=None):
    """Keys the differential states; no longer compares against base.

    Previously the function only emitted ``text`` when the differential's
    ``short``/``definition``/``comment`` differed from by_id on the
    profile's own snapshot; since the snapshot already mirrors what the
    differential wrote, ``text`` never fired in practice. The fix reports
    ``text`` whenever the differential declares any of those fields, and
    surfaces provenance tokens (``key``, ``USCDI``, ``USCDI+Q``) when the
    differential carries the corresponding extension. Tokens are spelled
    the same as those in the Flags column so a single search finds both.
    ``base`` is kept for callers but ignored.
    """
    keys = []
    if "min" in el or "max" in el:
        keys.append("card")
    if "type" in el:
        keys.append("type")
    if "contentReference" in el:
        keys.append("contentRef")
    if "binding" in el:
        keys.append("binding")
    if "mustSupport" in el:
        keys.append(f"MS={'true' if el['mustSupport'] else 'false'}")
    if "slicing" in el:
        keys.append("slicing")
    if "constraint" in el:
        keys.append("constraint")
    if any(k.startswith("fixed") for k in el):
        keys.append("fixed")
    if any(k.startswith("pattern") for k in el):
        keys.append("pattern")
    if any(field in el for field in ("short", "definition", "comment")):
        keys.append("text")
    if true_ext(el, EXT_KEY):
        keys.append("key")
    if true_ext(el, EXT_USCDI):
        keys.append("USCDI")
    if true_ext(el, EXT_UQC):
        keys.append("USCDI+Q")
    return ", ".join(keys) or "—"


def _table_row(el, profile_type, flag_uscdi, flag_uqc, declared=None,
               flag_style="words", note=None):
    eid = display_path(el)
    if note:
        eid = f"{eid} ({note})"
    card = cardinality_str(el)
    type_str = type_str_from_element(el)
    if type_str == "Inherited" and el.get("path") == profile_type:
        type_str = profile_type
    flags = flags_from_element(el, flag_uscdi, flag_uqc, style=flag_style)
    binding = binding_str(el)
    addl = additional_bindings(el)
    if addl:
        binding = (binding + f" +{len(addl)} addl").strip()
    cells = [
        f"`{eid}`",
        card,
        f"`{clean(type_str)}`",
        flags,
        clean(binding),
        short_text(el),
    ]
    if declared is not None:
        cells.insert(5, declared)
    return "| " + " | ".join(cells) + " |"


def _element_rows(elements, profile_type, differential_ids, flag_uscdi, flag_uqc,
                  flag_style="words"):
    rows = []
    hidden = []
    for el in elements:
        if _is_noise(el, profile_type, differential_ids):
            hidden.append(el.get("id") or el.get("path", ""))
            continue
        rows.append(_table_row(el, profile_type, flag_uscdi, flag_uqc,
                               flag_style=flag_style))
    return rows, hidden


def _invariants_rows(elements, hidden_paths=None):
    hidden_paths = set(hidden_paths or ())
    grouped = {}
    for el in elements:
        for con in el.get("constraint", []) or []:
            key = con.get("key", "")
            # dom-*/ele-1 are universal, and ext-1 is repeated on every Extension.
            if key.startswith("dom-") or key in ("ele-1", "ext-1"):
                continue
            sig = (key, con.get("severity", ""), con.get("human", ""), con.get("expression", ""))
            grouped.setdefault(sig, []).append(el.get("id") or el.get("path", ""))
    rows = []
    for (key, severity, human, expression), paths in grouped.items():
        paths = sorted(set(paths), key=lambda p: ("." in p, p))
        if hidden_paths and all(path in hidden_paths for path in paths):
            continue
        if len(paths) > 2:
            path_cell = ", ".join(paths[:2]) + f" (+{len(paths) - 2})"
        else:
            path_cell = ", ".join(paths)
        rows.append(
            f"| `{path_cell}` | `{key}` | {severity} | {clean(human)} | `{clean(expression)}` |"
        )
    return rows


def _additional_binding_rows(elements):
    rows = []
    for el in elements:
        for item in additional_bindings(el):
            rows.append(
                f"| `{display_path(el)}` | {clean(item.get('purpose', ''))} | "
                f"`{clean(item.get('valueSet', ''))}` | {clean(item.get('documentation', ''))} |"
            )
    return rows


def _slices_rows(elements):
    """Slices, slicing definitions, and fixed/pattern values in one place."""
    rows = []
    for el in elements:
        if not (el.get("sliceName") or el.get("slicing")
                or any(k.startswith(("fixed", "pattern")) for k in el)):
            continue
        fixed = fixed_pattern_text(el)
        # Slices that carve themselves out via a required binding (e.g.
        # US Core Condition.category:us-core) have no fixed/pattern but a
        # binding; show the binding in the Fixed / pattern cell so the
        # discriminator is visible in the table.
        if fixed == "—":
            bind = binding_str(el)
            if bind:
                fixed = f"binding: {bind}"
        rows.append(
            f"| `{display_path(el)}` | {cardinality_str(el)} | "
            f"`{clean(type_str_from_element(el))}` | {clean(fixed)} | "
            f"{clean(slicing_text(el))} |"
        )
    return rows


def _extension_rows(elements, link_ids=None):
    """Extension slices profiled on this resource, with canonical URL and version."""
    link_ids = set(link_ids or ())
    rows = []
    seen = set()
    for el in elements:
        for type_ref in el.get("type", []) or []:
            if type_ref.get("code") != "Extension":
                continue
            for profile in type_ref.get("profile", []) or []:
                base, version = split_canonical(profile)
                extension_id = url_tail(base)
                key = (display_path(el), base)
                if not extension_id or key in seen:
                    continue
                seen.add(key)
                if extension_id in link_ids:
                    target = f"[{extension_id}]({extension_id}.md)"
                else:
                    target = "—"
                rows.append(
                    f"| `{display_path(el)}` | `{base}` | {version or '—'} | {target} |"
                )
    return rows


def _write_details(profile, output_dir, json_filepath, name):
    sections = []
    for el in _snapshot(profile):
        if has_complexity(el):
            section = build_element_detail(el, display_path(el))
            if section:
                sections.append(section)
    if not sections:
        return
    title = profile.get("title") or profile.get("name") or "Profile"
    md = [f"# {title} — element details", ""]
    md.extend(sections)
    write_output(md, json_filepath, output_dir, f"{name}.details")


def convert_structure_definition_compact(profile, output_dir, json_filepath, *,
                                         name=None, details=False, package=None,
                                         flag_uscdi=True, flag_uqc=False,
                                         flag_style="words", link_ids=None):
    elements = _snapshot(profile)
    if not elements:
        raise ValueError(f"no snapshot; cannot render {profile.get('id')}")

    profile_type = profile.get("type", "")
    differential = _differential(profile)
    differential_ids = {el.get("id") for el in differential}
    by_id = {el.get("id"): el for el in elements}

    md = _header_lines(profile, package)
    # Pin the legend directly under the header block (LEGEND_ANCHOR).
    snapshot = _snapshot(profile)
    flag_key = any(true_ext(el, EXT_KEY) for el in snapshot)
    flag_uscdi_use = any(true_ext(el, EXT_USCDI) for el in snapshot)
    md.append("")
    md.append(legend_line(flag_uqc, flag_key=flag_key, flag_uscdi_use=flag_uscdi_use))
    if profile.get("description"):
        _section(md, "Description")
        md.append(clean(profile["description"]))

    if profile.get("derivation") == "constraint" and differential:
        _section(md, "Changes from base")
        md.append("| Path | Card | Type | Flags | Binding | Declared | Description |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for diff_el in differential:
            base_el = by_id.get(diff_el.get("id"))
            note = None
            if base_el is None:
                base_el = diff_el
                note = "declared only"
            md.append(_table_row(base_el, profile_type, flag_uscdi, flag_uqc,
                                 declared=_declared_keys(diff_el),
                                 flag_style=flag_style, note=note))

    _section(md, "Elements")
    rows, hidden = _element_rows(elements, profile_type, differential_ids,
                                 flag_uscdi, flag_uqc, flag_style)
    md.append("| Path | Card | Type | Flags | Binding | Description |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    md.extend(rows)
    if hidden:
        md.append("")
        md.append("Elements defined in ancestors: " + ", ".join(f"`{h}`" for h in hidden))

    slice_rows = _slices_rows(elements)
    if slice_rows:
        _section(md, "Slices and fixed values")
        md.append("| Path | Card | Type | Fixed / pattern | Slicing |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        md.extend(slice_rows)

    extension_rows = _extension_rows(elements, link_ids)
    if extension_rows:
        _section(md, "Extensions")
        md.append("| Path | Extension URL | Version | KB |")
        md.append("| :--- | :--- | :--- | :--- |")
        md.extend(extension_rows)

    invariant_rows = _invariants_rows(elements, hidden)
    _section(md, "Invariants")
    if invariant_rows:
        md.append("| Path | Key | Severity | Human | Expression |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        md.extend(invariant_rows)
    else:
        md.append("_No profile-specific invariants._")

    binding_rows = _additional_binding_rows(elements)
    if binding_rows:
        _section(md, "Additional bindings")
        md.append("| Path | Purpose | Value set | Documentation |")
        md.append("| :--- | :--- | :--- | :--- |")
        md.extend(binding_rows)

    out_name = name or profile.get("id")
    write_output(md, json_filepath, output_dir, out_name)
    if details:
        _write_details(profile, output_dir, json_filepath, out_name)


def convert_extension_compact(profile, output_dir, json_filepath, *,
                              name=None, details=False, package=None,
                              flag_uscdi=True, flag_uqc=False,
                              flag_style="words", link_ids=None):
    elements = _snapshot(profile)
    if not elements:
        raise ValueError(f"no snapshot; cannot render {profile.get('id')}")

    md = _header_lines(profile, package)
    # Pin the legend directly under the header block (LEGEND_ANCHOR).
    snapshot = _snapshot(profile)
    flag_key = any(true_ext(el, EXT_KEY) for el in snapshot)
    flag_uscdi_use = any(true_ext(el, EXT_USCDI) for el in snapshot)
    md.append("")
    md.append(legend_line(flag_uqc, flag_key=flag_key, flag_uscdi_use=flag_uscdi_use))
    contexts = profile.get("context") or []
    if contexts:
        _section(md, "Context")
        for ctx in contexts:
            md.append(f"- `{ctx.get('type', '')}`: `{ctx.get('expression', '')}`")
    if profile.get("description"):
        _section(md, "Description")
        md.append(clean(profile["description"]))

    sub_slices = [el for el in elements
                  if (el.get("id") or "").startswith("Extension.extension:")
                  and el["id"].count(".") == 1]
    value_el = next((el for el in elements if el.get("id") == "Extension.value[x]"), None)

    if sub_slices:
        _section(md, "Sub-extensions")
        md.append("| Slice | URL | Card | Value type | Binding | Description |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for sub in sub_slices:
            slice_name = sub["id"].split(":", 1)[1]
            value = next((el for el in elements
                          if el.get("id") == f"{sub['id']}.value[x]"), None)
            url_el = next((el for el in elements
                           if el.get("id") == f"{sub['id']}.url"), None)
            slice_url = ""
            if url_el:
                slice_url = url_el.get("fixedUri") or url_el.get("patternUri") or ""
            value_type = type_str_from_element(value) if value else "—"
            binding = binding_str(value) if value else ""
            md.append(
                f"| `{slice_name}` | `{slice_url or '—'}` | {cardinality_str(sub)} | "
                f"`{clean(value_type)}` | {clean(binding)} | {short_text(sub)} |"
            )
    else:
        _section(md, "Value")
        md.append("| Card | Type | Binding | Description |")
        md.append("| :--- | :--- | :--- | :--- |")
        if value_el:
            md.append(
                f"| {cardinality_str(value_el)} | `{clean(type_str_from_element(value_el))}` | "
                f"{clean(binding_str(value_el))} | {short_text(value_el)} |"
            )
        else:
            md.append("| — | — | — | No value[x] element |")

    invariant_rows = _invariants_rows(elements)
    _section(md, "Invariants")
    if invariant_rows:
        md.append("| Path | Key | Severity | Human | Expression |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        md.extend(invariant_rows)
    else:
        md.append("_No profile-specific invariants._")

    out_name = name or profile.get("id")
    write_output(md, json_filepath, output_dir, out_name)
    if details:
        _write_details(profile, output_dir, json_filepath, out_name)


def _read_package_meta(package_dir):
    package_json = package_dir / "package.json"
    if not package_json.exists():
        return {}
    try:
        return json.loads(package_json.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}


def write_index(output_dir, package_label, entries, meta=None, flag_uqc=False,
                flag_key=False, flag_uscdi_use=False):
    """Write the generated README index; refuse to clobber a hand-written README."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    readme = output_dir / "README.md"
    if readme.exists() and GENERATED_MARKER not in readme.read_text(encoding="utf-8"):
        raise RuntimeError(
            f"refusing to overwrite hand-written README: {readme}"
        )

    meta = meta or {}
    lines = [f"# {package_label} element tables", "", GENERATED_MARKER, ""]
    lines.append(
        f"Generated by `scripts/generate_element_kbs.py` from `{package_label}`. "
        "Do not edit by hand."
    )
    lines.append("")
    dependencies = meta.get("dependencies") or {}
    if dependencies:
        lines.append("Dependencies: " + ", ".join(
            f"`{name}@{version}`" for name, version in sorted(dependencies.items())
        ))
        lines.append("")
    kinds = {}
    for entry in entries:
        kinds[entry["kind"]] = kinds.get(entry["kind"], 0) + 1
    counts = ", ".join(f"{count} {kind}" for kind, count in sorted(kinds.items()))
    noun = "file" if len(entries) == 1 else "files"
    lines.append(f"{len(entries)} {noun} ({counts}).")
    lines.append("")
    lines.append("| ID | Title | Base | Kind | File |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")
    for entry in sorted(entries, key=lambda item: item["id"]):
        lines.append(
            f"| `{entry['id']}` | {clean(entry['title'])} | "
            f"`{clean(entry['base'])}` | {clean(entry['kind'])} | "
            f"[`{clean(entry['file'])}`]({entry['file']}) |"
        )
    lines.append("")
    lines.append("## Legend")
    lines.append("")
    lines.append("| Token | Meaning |")
    lines.append("| :--- | :--- |")
    lines.append("| `MS` | mustSupport |")
    lines.append("| `modifier` | isModifier |")
    lines.append("| `summary` | isSummary |")
    if flag_uscdi_use:
        lines.append("| `USCDI` | USCDI requirement extension is true |")
    if flag_key:
        lines.append("| `key` | QI-Core key element extension is true |")
    if flag_uqc:
        lines.append("| `USCDI+Q` | USCDI+ Quality requirement extension is true |")
    lines.append("| `strength→vs` | binding strength and value set id (`@version` when versioned) |")
    lines.append("| `Declared` | differential keys; booleans as `MS=true`/`MS=false`, text-only changes as `text` |")
    lines.append("| `(MS)` in Type | mustSupport applies to that specific type/target |")
    lines.append("| `Elements defined in ancestors` | inherited elements hidden from the table |")
    lines.append("| `Slices and fixed values` | slicing definitions and fixed/pattern values |")
    lines.append("| `Extensions` | extension URL and version; KB links resolve inside this directory |")
    lines.append("| `No profile-specific invariants` | only `dom-*`, `ele-1` and `ext-1` apply |")
    lines.append("")
    readme.write_text("\n".join(lines) + "\n", encoding="utf-8")


def output_name(profile, json_filepath, naming="id"):
    """Pure filename stem for a rendered StructureDefinition."""
    if naming == "id":
        return profile.get("id") or path_stem(json_filepath)
    return path_stem(json_filepath)


def convert_package(package_dir, output_dir, *, kinds=("resource",), only=None,
                    derivation=None, naming="id", index=True, details=False,
                    flag_uscdi=True, flag_uqc=False, flag_style="words",
                    package_label=None, progress=None):
    """Render every matching StructureDefinition in a package directory."""
    package_dir = Path(package_dir)
    meta = _read_package_meta(package_dir)
    if package_label is None:
        if meta.get("name"):
            package_label = f"{meta['name']}@{meta.get('version', '')}".rstrip("@")
        else:
            package_label = package_dir.name

    only_set = set(only) if only else None
    kinds = set(kinds) if kinds else None
    stats = {"written": 0, "skipped": 0, "by_kind": {}, "package": package_label,
             "flag_key": False, "flag_uscdi_use": False}
    entries = []

    # First pass: identify everything that will be rendered, so extension KB links
    # only point at files that actually exist in this package.
    selected = []
    link_ids = set()
    for json_path in sorted(package_dir.glob("StructureDefinition-*.json")):
        try:
            profile = json.loads(json_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            stats["skipped"] += 1
            if progress:
                progress(f"skipped (unreadable) {json_path.name}: {exc}")
            continue
        if profile.get("resourceType") != "StructureDefinition":
            continue
        if kinds is not None and profile.get("kind") not in kinds:
            stats["skipped"] += 1
            continue
        if derivation is not None and profile.get("derivation") != derivation:
            stats["skipped"] += 1
            continue
        if only_set is not None and profile.get("id") not in only_set:
            stats["skipped"] += 1
            continue
        if not _snapshot(profile):
            stats["skipped"] += 1
            if progress:
                progress(f"skipped (no snapshot) {json_path.name}")
            continue
        out_name = output_name(profile, json_path, naming)
        selected.append((json_path, profile, out_name))
        link_ids.add(out_name)

    for json_path, profile, out_name in selected:
        kwargs = {
            "name": out_name,
            "details": details,
            "package": package_label,
            "flag_uscdi": flag_uscdi,
            "flag_uqc": flag_uqc,
            "flag_style": flag_style,
            "link_ids": link_ids,
        }
        if profile.get("type") == "Extension":
            convert_extension_compact(profile, output_dir, str(json_path), **kwargs)
        else:
            convert_structure_definition_compact(profile, output_dir, str(json_path), **kwargs)

        kind = profile.get("kind", "")
        stats["written"] += 1
        stats["by_kind"][kind] = stats["by_kind"].get(kind, 0) + 1
        # Lazy package-level gates for the legend tokens: any profile
        # carrying the qicore-keyelement or uscdi-requirement extension
        # flips the corresponding flag for the index.
        if any(true_ext(el, EXT_KEY) for el in profile.get("snapshot", {}).get("element", [])):
            stats["flag_key"] = True
        if any(true_ext(el, EXT_USCDI) for el in profile.get("snapshot", {}).get("element", [])):
            stats["flag_uscdi_use"] = True
        entries.append({
            "id": profile.get("id", ""),
            "title": profile.get("title") or profile.get("name") or "",
            "base": url_tail(profile.get("baseDefinition", "")) or "—",
            "kind": kind,
            "file": f"{out_name}.md",
        })

    if index:
        write_index(output_dir, package_label, entries, meta,
                    flag_uqc=flag_uqc, flag_key=stats["flag_key"],
                    flag_uscdi_use=stats["flag_uscdi_use"])
    stats["files"] = entries
    return stats


def convert_value_set(profile, output_dir, json_filepath):
    md = []
    title = profile.get("title", profile.get("name", "Unnamed ValueSet"))
    vs_id = profile.get("id", "Unknown-ID")
    url = profile.get("url", "")
    status = profile.get("status", "unknown")
    version = profile.get("version", "0.0.1")
    date = profile.get("date", "")
    publisher = profile.get("publisher", "")
    experimental = profile.get("experimental", False)
    content = profile.get("content", "")
    description = profile.get("description", "")

    md.append(f"# Value Set: {title}")
    md.append(f"**ID:** `{vs_id}` | **URL:** `{url}` | **Status:** {status}")
    md.append(f"**Version:** {version} | **Date:** {date} | **Publisher:** {publisher} | **Experimental:** {str(experimental).lower()}")
    if content:
        md.append(f"**Content:** {content}")
    md.append("")

    if description:
        md.append(f"## Description\n{clean(description)}\n")

    compose = profile.get("compose", {})
    if compose:
        md.append("## Compose")
        includes = compose.get("include", [])
        excludes = compose.get("exclude", [])

        if includes:
            md.append("### Include")
            md.append("| System | Filter | Concept |")
            md.append("| :--- | :--- | :--- |")
            for inc in includes:
                system = inc.get("system", "")
                filters = inc.get("filter", [])
                concepts = inc.get("concept", [])
                filter_str = "; ".join([f"{f.get('property')} {f.get('op')} {f.get('value')}" for f in filters])
                concept_codes = ", ".join([c.get("code", "") for c in concepts])
                md.append(f"| {system} | {filter_str} | {concept_codes} |")

        if excludes:
            md.append("### Exclude")
            md.append("| System | Filter | Concept |")
            md.append("| :--- | :--- | :--- |")
            for exc in excludes:
                system = exc.get("system", "")
                filters = exc.get("filter", [])
                concepts = exc.get("concept", [])
                filter_str = "; ".join([f"{f.get('property')} {f.get('op')} {f.get('value')}" for f in filters])
                concept_codes = ", ".join([c.get("code", "") for c in concepts])
                md.append(f"| {system} | {filter_str} | {concept_codes} |")
        md.append("")

    expansion = profile.get("expansion", {})
    if expansion:
        total = expansion.get("total", "")
        contains = expansion.get("contains", [])
        md.append("## Expansion")
        md.append(f"- **Total:** {total}")
        if contains:
            md.append("| Code | Display | System |")
            md.append("| :--- | :--- | :--- |")
            for c in contains[:50]:
                code = c.get("code", "")
                display = c.get("display", "")
                system = c.get("system", "")
                md.append(f"| {code} | {display} | {system} |")
            if len(contains) > 50:
                md.append(f"... and {len(contains) - 50} more (truncated)")
        md.append("")

    copyright_text = profile.get("copyright")
    if copyright_text:
        md.append(f"## Copyright\n{clean(copyright_text)}\n")

    write_output(md, json_filepath, output_dir)


def convert_code_system(profile, output_dir, json_filepath):
    md = []
    title = profile.get("title", profile.get("name", "Unnamed CodeSystem"))
    cs_id = profile.get("id", "Unknown-ID")
    url = profile.get("url", "")
    status = profile.get("status", "unknown")
    version = profile.get("version", "0.0.1")
    date = profile.get("date", "")
    publisher = profile.get("publisher", "")
    experimental = profile.get("experimental", False)
    content = profile.get("content", "")
    case_sensitive = profile.get("caseSensitive", "")
    description = profile.get("description", "")

    md.append(f"# Code System: {title}")
    md.append(f"**ID:** `{cs_id}` | **URL:** `{url}` | **Status:** {status}")
    md.append(f"**Version:** {version} | **Date:** {date} | **Publisher:** {publisher} | **Experimental:** {str(experimental).lower()}")
    md.append(f"**Content:** {content} | **Case Sensitive:** {str(case_sensitive).lower() if case_sensitive else 'false'}")
    md.append("")

    if description:
        md.append(f"## Description\n{clean(description)}\n")

    value_set = profile.get("valueSet")
    if value_set:
        md.append(f"## Value Set\n{value_set}\n")

    concepts = profile.get("concept", [])
    if concepts:
        md.append("## Concepts")
        md.append("| Code | Display | Definition |")
        md.append("| :--- | :--- | :--- |")
        for c in concepts:
            code = c.get("code", "")
            display = c.get("display", "")
            definition = truncate(c.get("definition", ""), 80)
            md.append(f"| {code} | {display} | {definition} |")
        md.append("")

    write_output(md, json_filepath, output_dir)


def convert_operation_definition(profile, output_dir, json_filepath):
    md = []
    title = profile.get("title", profile.get("name", "Unnamed Operation"))
    op_id = profile.get("id", "Unknown-ID")
    url = profile.get("url", "")
    status = profile.get("status", "unknown")
    kind = profile.get("kind", "")
    experimental = profile.get("experimental", False)
    date = profile.get("date", "")
    publisher = profile.get("publisher", "")
    description = profile.get("description", "")

    md.append(f"# Operation Definition: {title}")
    md.append(f"**ID:** `{op_id}` | **URL:** `{url}` | **Status:** {status}")
    md.append(f"**Kind:** {kind} | **Experimental:** {str(experimental).lower()} | **Date:** {date} | **Publisher:** {publisher}")
    md.append("")

    if description:
        md.append(f"## Description\n{clean(description)}\n")

    code = profile.get("code", "")
    system = profile.get("system", False)
    type_flag = profile.get("type", False)
    instance = profile.get("instance", False)
    md.append(f"## Signature")
    md.append(f"- **System:** {str(system).lower()} | **Type:** {str(type_flag).lower()} | **Instance:** {str(instance).lower()}")
    md.append(f"- **Operation Code:** {code}")
    md.append("")

    resources = profile.get("resource", [])
    if resources:
        md.append(f"## Resources\n{', '.join(resources)}\n")

    params = profile.get("parameter", [])
    if params:
        md.append("## Parameters")
        md.append("| Name | Use | Cardinality | Type | Description |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        for p in params:
            name = p.get("name", "")
            use = p.get("use", "")
            min_card = p.get("min", "")
            max_card = p.get("max", "")
            p_type = p.get("type", "")
            # R4 OperationDefinition.parameter carries its text in `documentation`.
            description = truncate(p.get("documentation") or p.get("description", ""), 200)
            md.append(f"| {name} | {use} | {min_card}..{max_card} | {p_type} | {description} |")
        md.append("")

    write_output(md, json_filepath, output_dir)


def convert_search_parameter(profile, output_dir, json_filepath):
    md = []
    title = profile.get("title", profile.get("name", "Unnamed SearchParameter"))
    sp_id = profile.get("id", "Unknown-ID")
    url = profile.get("url", "")
    status = profile.get("status", "unknown")
    code = profile.get("code", "")
    base = profile.get("base", [])
    sp_type = profile.get("type", "")
    expression = profile.get("expression", "")
    xpath_usage = profile.get("xpathUsage", "")
    description = profile.get("description", "")

    md.append(f"# Search Parameter: {title}")
    md.append(f"**ID:** `{sp_id}` | **URL:** `{url}` | **Status:** {status}")
    md.append(f"**Code:** {code} | **Base:** {', '.join(base)} | **Type:** {sp_type}")
    if xpath_usage:
        md.append(f"**XPath Usage:** {xpath_usage}")
    md.append("")

    if description:
        md.append(f"## Description\n{clean(description)}\n")

    if expression:
        md.append(f"## Expression\n`{expression}`\n")

    targets = profile.get("target", [])
    if targets:
        md.append(f"## Target Types\n{', '.join(targets)}\n")

    write_output(md, json_filepath, output_dir)


def convert_capability_statement(profile, output_dir, json_filepath):
    md = []
    title = profile.get("title", profile.get("name", "Unnamed CapabilityStatement"))
    cs_id = profile.get("id", "Unknown-ID")
    url = profile.get("url", "")
    status = profile.get("status", "unknown")
    kind = profile.get("kind", "")
    experimental = profile.get("experimental", False)
    date = profile.get("date", "")
    publisher = profile.get("publisher", "")
    description = profile.get("description", "")

    md.append(f"# Capability Statement: {title}")
    md.append(f"**ID:** `{cs_id}` | **URL:** `{url}` | **Status:** {status}")
    md.append(f"**Kind:** {kind} | **Experimental:** {str(experimental).lower()} | **Date:** {date} | **Publisher:** {publisher}")
    md.append("")

    if description:
        md.append(f"## Description\n{clean(description)}\n")

    rest = profile.get("rest", [])
    if rest:
        md.append("## REST Behavior")
        for r in rest:
            mode = r.get("mode", "")
            md.append(f"### Mode: {mode}")
            resources = r.get("resource", [])
            if resources:
                md.append("| Type | Supported Profiles | Interactions | SearchParams |")
                md.append("| :--- | :--- | :--- | :--- |")
                for res in resources:
                    res_type = res.get("type", "")
                    profiles = res.get("supportedProfile", [])
                    interactions = res.get("interaction", [])
                    search_params = res.get("searchParam", [])
                    profile_str = ", ".join([os.path.basename(p) for p in profiles[:3]])
                    if len(profiles) > 3:
                        profile_str += f" +{len(profiles) - 3} more"
                    interaction_str = ", ".join([i.get("code", "") for i in interactions])
                    sp_str = ", ".join([sp.get("name", "") for sp in search_params[:5]])
                    if len(search_params) > 5:
                        sp_str += f" +{len(search_params) - 5} more"
                    md.append(f"| {res_type} | {profile_str} | {interaction_str} | {sp_str} |")
                md.append("")
        md.append("")

    write_output(md, json_filepath, output_dir)


def flatten_actions(actions, prefix="action"):
    rows = []
    for i, action in enumerate(actions):
        path = f"{prefix}[{i}]"
        title = action.get("title", "")
        description = action.get("description", "")
        code_vals = action.get("code", [])
        code_str = ", ".join([f"{c.get('coding', [{}])[0].get('code', '')}" for c in code_vals if c.get('coding')])
        condition = action.get("condition", [])
        condition_str = "; ".join([f"{c.get('kind')} {c.get('expression', '')}" for c in condition])
        dynamic_values = action.get("dynamicValue", [])
        dv_str = "; ".join([f"{dv.get('path')}: {dv.get('expression')}" for dv in dynamic_values])
        rows.append((path, title, code_str, condition_str, dynamic_values, action))
        sub_actions = action.get("action", [])
        if sub_actions:
            rows.extend(flatten_actions(sub_actions, f"{path}.action"))
    return rows


def convert_plandefinition(profile, output_dir, json_filepath):
    md = []
    title = profile.get("title", profile.get("name", "Unnamed PlanDefinition"))
    pd_id = profile.get("id", "Unknown-ID")
    url = profile.get("url", "")
    status = profile.get("status", "unknown")
    version = profile.get("version", "0.0.1")
    date = profile.get("date", "")
    publisher = profile.get("publisher", "")
    description = profile.get("description", "")

    md.append(f"# Plan Definition: {title}")
    md.append(f"**ID:** `{pd_id}` | **URL:** `{url}` | **Status:** {status}")
    md.append(f"**Version:** {version} | **Date:** {date} | **Publisher:** {publisher}")
    md.append("")

    if description:
        md.append(f"## Description\n{clean(description)}\n")

    triggers = profile.get("trigger", [])
    if triggers:
        md.append("## Triggers")
        for t in triggers:
            t_type = t.get("type", "")
            t_code = ""
            if t.get("codeableConcept"):
                t_code = t['codeableConcept'].get("coding", [{}])[0].get("code", "")
            md.append(f"- **{t_type}** {t_code}")
        md.append("")

    actions = profile.get("action", [])
    if actions:
        md.append("## Actions")
        md.append("| Path | Title | Code | Condition | Dynamic Values |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        rows = flatten_actions(actions)
        for row in rows:
            path, act_title, code_str, condition_str, dv, action = row
            dynamic_values = action.get("dynamicValue", [])
            dv_str = "; ".join([f"{d.get('path')}: {d.get('expression', '')}" for d in dynamic_values])
            md.append(f"| `{path}` | {act_title} | {code_str} | {condition_str} | {dv_str} |")
        md.append("")

    write_output(md, json_filepath, output_dir)


def convert_activity_definition(profile, output_dir, json_filepath):
    md = []
    title = profile.get("title", profile.get("name", "Unnamed ActivityDefinition"))
    ad_id = profile.get("id", "Unknown-ID")
    url = profile.get("url", "")
    status = profile.get("status", "unknown")
    version = profile.get("version", "0.0.1")
    date = profile.get("date", "")
    publisher = profile.get("publisher", "")
    description = profile.get("description", "")

    md.append(f"# Activity Definition: {title}")
    md.append(f"**ID:** `{ad_id}` | **URL:** `{url}` | **Status:** {status}")
    md.append(f"**Version:** {version} | **Date:** {date} | **Publisher:** {publisher}")
    md.append("")

    if description:
        md.append(f"## Description\n{clean(description)}\n")

    dynamic_values = profile.get("dynamicValue", [])
    if dynamic_values:
        md.append("## Dynamic Values")
        md.append("| Path | Expression |")
        md.append("| :--- | :--- |")
        for dv in dynamic_values:
            dv_path = dv.get("path", "")
            dv_expr = dv.get("expression", "")
            md.append(f"| {dv_path} | {dv_expr} |")
        md.append("")

    transform = profile.get("transform")
    if transform:
        md.append(f"## Transform\n`{transform}`\n")

    product = profile.get("product")
    if product:
        product_type = product.get("type", "")
        ref = product.get("reference", "")
        md.append(f"## Product\nType: {product_type}, Reference: {ref}\n")

    patient_instruction = profile.get("patientInstruction")
    if patient_instruction:
        md.append(f"## Patient Instruction\n{clean(patient_instruction)}\n")

    write_output(md, json_filepath, output_dir)


def flatten_instance_fields(obj, prefix="", rows=None):
    if rows is None:
        rows = []
    if obj is None:
        return rows
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in ("meta", "text", "contained", "_id"):
                continue
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                flatten_instance_fields(value, path, rows)
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    list_path = f"{path}[{i}]"
                    if isinstance(item, dict):
                        flatten_instance_fields(item, list_path, rows)
                    else:
                        type_str = type(item).__name__
                        rows.append((list_path, str(item), type_str))
            else:
                type_str = type(value).__name__
                rows.append((path, str(value), type_str))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            list_path = f"{prefix}[{i}]"
            if isinstance(item, dict):
                flatten_instance_fields(item, list_path, rows)
            else:
                rows.append((list_path, str(item), type(item).__name__))
    else:
        rows.append((prefix, str(obj), type(obj).__name__))
    return rows


def convert_instance(profile, output_dir, json_filepath):
    md = []
    resource_type = profile.get("resourceType", "Unknown")
    inst_id = profile.get("id", "Unknown-ID")
    title = profile.get("title", profile.get("name", f"{resource_type} instance"))

    md.append(f"# Instance: {title}")
    md.append(f"**ID:** `{inst_id}` | **ResourceType:** {resource_type}")
    md.append("")

    rows = flatten_instance_fields(profile)

    if rows:
        content_type_by_index = {}
        for row in rows:
            p = row[0]
            if p.startswith("content[") and ".contentType" in p:
                idx = p.split(".contentType")[0]
                content_type_by_index[idx] = row[1]

        md.append("## Fields")
        md.append("| Field Path | Value | Type |")
        md.append("| :--- | :--- | :--- |")
        for path, value, type_str in rows:
            display_value = clean(str(value))
            is_base64 = False
            if re.match(r'^content\[\d+\]\.data$', path) and type_str == "str":
                idx = re.match(r'^content\[(\d+)\]\.data$', path).group(1)
                idx_prefix = f"content[{idx}]"
                ct = content_type_by_index.get(idx_prefix, "")
                if ct in ("text/cql", "application/elm+xml", "application/elm+json"):
                    is_base64 = True
            if is_base64:
                display_value = f"[base64 content — ~{len(value)} chars]"
            elif len(display_value) > 80:
                display_value = display_value[:79] + "…"
            md.append(f"| `{path}` | {display_value} | {type_str} |")

    write_output(md, json_filepath, output_dir)


def write_output(md, json_filepath, output_dir, name=None):
    if name:
        output_filename = f"{name}.md"
    else:
        base_name, _ = os.path.splitext(os.path.basename(json_filepath))
        output_filename = f"{base_name}.md"
    output_path = os.path.join(output_dir, output_filename)
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(md) + "\n")


def convert_resource(json_filepath, output_dir):
    filename = os.path.basename(json_filepath)

    if filename.startswith('_') or filename.endswith('.index.json'):
        print(f'Skipped (index/package): {json_filepath}')
        return

    try:
        with open(json_filepath, 'r', encoding='utf-8-sig') as f:
            profile = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f'Error reading {json_filepath}: {e}')
        return

    if 'resourceType' not in profile:
        print(f'Skipped (no resourceType): {json_filepath}')
        return

    resource_type = profile.get('resourceType', '')

    handlers = {
        'StructureDefinition': convert_structure_definition,
        'ValueSet': convert_value_set,
        'CodeSystem': convert_code_system,
        'OperationDefinition': convert_operation_definition,
        'SearchParameter': convert_search_parameter,
        'CapabilityStatement': convert_capability_statement,
        'PlanDefinition': convert_plandefinition,
        'ActivityDefinition': convert_activity_definition,
    }

    if resource_type in handlers:
        handlers[resource_type](profile, output_dir, json_filepath)
        print(f'Converted ({resource_type}): {json_filepath}')
    else:
        convert_instance(profile, output_dir, json_filepath)
        print(f'Converted (instance): {json_filepath}')


def convert_resource_compact(json_filepath, output_dir, *, details=False,
                             flag_uqc=False, flag_style="words"):
    filename = os.path.basename(json_filepath)
    if filename.startswith('_') or filename.endswith('.index.json'):
        print(f'Skipped (index/package): {json_filepath}')
        return
    try:
        with open(json_filepath, 'r', encoding='utf-8-sig') as f:
            profile = json.load(f)
    except (json.JSONDecodeError, IOError) as exc:
        print(f'Error reading {json_filepath}: {exc}')
        return
    if profile.get("resourceType") != "StructureDefinition":
        print(f'Skipped (not StructureDefinition): {json_filepath}')
        return
    if not _snapshot(profile):
        print(f'Skipped (no snapshot): {json_filepath}')
        return
    kwargs = {"details": details, "flag_uqc": flag_uqc, "flag_style": flag_style}
    if profile.get("type") == "Extension":
        convert_extension_compact(profile, output_dir, json_filepath, **kwargs)
    else:
        convert_structure_definition_compact(profile, output_dir, json_filepath, **kwargs)
    print(f'Converted (compact): {json_filepath}')


SKILL_ROOT = Path(__file__).resolve().parents[1]   # the skill folder


def build_parser():
    ap = argparse.ArgumentParser(
        description="Convert full-source FHIR JSON to concise markdown profiles."
    )
    ap.add_argument("--input", default=str(SKILL_ROOT / "resources/profiles/full-source"))
    ap.add_argument("--output", default=str(SKILL_ROOT / "resources/profiles/concise"))
    ap.add_argument("--package-dir", default=None,
                    help="Render every StructureDefinition-*.json in a package directory.")
    ap.add_argument("--only", default=None,
                    help="Comma-separated allowlist of profile ids (package mode).")
    ap.add_argument("--kinds", default="resource,complex-type",
                    help="Comma-separated StructureDefinition kinds (package mode).")
    ap.add_argument("--derivation", default=None,
                    help="Optional derivation filter, e.g. specialization (package mode).")
    ap.add_argument("--naming", choices=["basename", "id"], default="basename",
                    help="Output filename source (default: JSON basename, as used by the CPG KB).")
    ap.add_argument("--format", choices=["full", "compact"], default="full",
                    help="Rendering format for --input mode (compact is used by the element KBs).")
    ap.add_argument("--details", action="store_true",
                    help="Also write {id}.details.md with definitions, comments and mappings.")
    ap.add_argument("--no-index", action="store_true",
                    help="Do not write the generated README.md index (package mode).")
    ap.add_argument("--flag-uqc", action="store_true",
                    help="Render the UQC uscdiplusquality extension as the USCDI+Q flag.")
    ap.add_argument("--flag-style", choices=["legacy", "words"], default="words",
                    help="Compact flag tokens (words for element KBs, legacy for symbols).")
    return ap


def main():
    args = build_parser().parse_args()
    if args.package_dir:
        only = [item.strip() for item in args.only.split(",") if item.strip()] if args.only else None
        kinds = [item.strip() for item in args.kinds.split(",") if item.strip()]
        stats = convert_package(
            args.package_dir,
            args.output,
            kinds=kinds,
            only=only,
            derivation=args.derivation or None,
            naming=args.naming,
            index=not args.no_index,
            details=args.details,
            flag_uqc=args.flag_uqc,
            flag_style=args.flag_style,
        )
        print(f"Wrote {stats['written']} files, skipped {stats['skipped']} → {args.output}")
        return
    for json_file in sorted(glob.glob(os.path.join(args.input, "*.json"))):
        if args.format == "compact":
            convert_resource_compact(json_file, args.output, details=args.details,
                                     flag_uqc=args.flag_uqc,
                                     flag_style=args.flag_style)
        else:
            convert_resource(json_file, args.output)


if __name__ == "__main__":
    main()
