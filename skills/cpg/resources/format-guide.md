# FHIR Profiles KB — Format Guide

Reference for interpreting the concise markdown output in `resources/profiles/concise/` in this
skill, as produced by `scripts/convert-resource-to-markdown.py`.

---

## StructureDefinition

### Header block

```text
# Profile: {title}
**ID:** `{id}` | **URL:** `{canonical}` | **Status:** {status}
**Base:** {base} | **Derivation:** constraint|specialization | **Kind:** resource|extension|...
**Publisher:** ... | **Date:** ... | **Version:** ...
```

### Elements table

Six columns:

| Column | Content |
|--------|---------|
| `Path` | Dot-notation element path; slices shown as `Resource.field:sliceName` |
| `Card` | Cardinality — `{min}..{max}`; `0..0` means prohibited |
| `Type` | FHIR type code; profile and target references shown as `Extension(profile-id)`, `Reference(Group)` or `canonical(PlanDefinition)` |
| `Flags` | Space-separated: `MS` mustSupport, `!` isModifier, `Σ` isSummary |
| `Binding` | `{strength}→{valueSetId}`, with `@{version}` when the canonical is versioned (`required→publication-status@4.0.1`), or empty; strength values: `required`, `extensible`, `preferred`, `example` |
| `Description` | The element's short text, cut at 120 characters with `…` (rare). The Element Details section has the full definition. |

### Element Details section

Appears for elements that have constraints, slicing, aliases, mappings, or fixed/pattern
values. Each subsection is headed by the element path in backticks:

```text
### `Resource.field`
- **Cardinality:** ...
- **Type:** ...
- **Flags:** ...
- **Binding:** {strength} → {full ValueSet URL}
- **Short:** {full short description}
- **Definition:** {full definition text}
- **Alias:** [alias1, alias2]
- **Comment:** /* ... */
- **Constraint:** {key} ({severity}): {human description}
  - Expression: `{FHIRPath}`
  - Source: {canonical}
- **Slicing:** discriminator: (type={value|pattern|exists}, path={path}), ordered={bool}, rules={open|closed|openAtEnd}
- **Mapping:** {identity}→{map}
- **Fixed:** {fixedCode | fixedUri | fixedCanonical | ...}
- **Pattern:** {patternCodeableConcept | ...}
```

---

## ValueSet

```text
# Value Set: {title}
**ID:** `{id}` | **URL:** `{canonical}` | **Status:** {status}
**Version:** ... | **Date:** ... | **Publisher:** ... | **Experimental:** ...
```

### Compose section

```text
## Compose
### Include
| System | Filter | Concept |
| :--- | :--- | :--- |
| {system-url} | {property} {op} {value} | {explicit codes} |
```

- **Filter** is populated when the include is a filtered subset (e.g., `concept is-a SIB`)
- **Concept** is populated when the include lists explicit codes rather than a filter
- Blank cells mean "all codes from this system"

### Expansion section (when present)

```text
## Expansion
- **Total:** {n}
### Contains
| Code | Display | System |
```

Only the first 50 expansion codes are listed, followed by `... and N more (truncated)`. Read the
source JSON in `resources/profiles/full-source/` for the rest.

---

## CodeSystem

```text
# Code System: {title}
**ID:** `{id}` | **URL:** `{canonical}` | **Status:** {status}
**Content:** complete|fragment|... | **Case Sensitive:** true|false
```

### Concepts table

```text
## Concepts
| Code | Display | Definition |
```

Definitions are cut at 80 characters; the source JSON in `resources/profiles/full-source/` has the
full text. OperationDefinition parameter documentation is cut at 200 characters.

### Value Set

When `## Value Set` appears, the URL is the implicit ValueSet that includes all codes
from this CodeSystem.

---

## Instance (Patient, Task, ActivityDefinition, PlanDefinition, etc.)

```text
# Instance: {display-name} / {ResourceType}
**ID:** `{id}` | **ResourceType:** {type}
```

Some rich instances (Library, ActivityDefinition) use a structure-definition-like header
with URL, version, status, and publisher instead.

### Fields table

```text
## Fields
| Field Path | Value | Type |
```

- Arrays are indexed: `name[0].family`, `name[0].given[0]`
- Nested objects use dot notation: `address[0].city`
- Boolean values render as Python literals: `True`, `False`
- Values longer than 80 characters are cut with `…`
- Library `content[].data` entries holding CQL or ELM are base64 and are shown as
  `[base64 content — ~N chars]`. Decode them from the source JSON if you need the logic.

### PlanDefinition action paths

Actions are flattened with indexed notation:

```text
action[0].title
action[0].condition[0].expression
action[0].dynamicValue[0].path
action[0].dynamicValue[0].expression
action[0].action[0].title        ← nested sub-action
```

Each action level shows: title, code, condition, dynamic values. Depth rarely exceeds 3.

---

## Chaining: Element → ValueSet

1. In the Elements table, read the **Binding** cell: `required→publication-status@4.0.1`
2. The part after `→` and before any `@` is the ValueSet id: `publication-status`. Base FHIR R4
   value sets (`@4.0.1`) aren't in this KB; look them up in the R4 spec.
3. If it looks like a partial URL, take the last path segment as the id
4. Grep for the file, replacing `<skill-dir>` with this skill's directory:

   ```sh
   ls "<skill-dir>/resources/profiles/concise/" | grep -i "publication-status"
   ```

5. Read the matching ValueSet file for the full code list

---

## Other output styles

The converter also has a compact style (word flags such as `modifier` and `summary`, a
`## Changes from base` table, and `## Invariants` and `## Slices and fixed values` sections instead
of Element Details). The `fhir` skill's base R4 element tables use that style. This KB uses the
full style described above.
