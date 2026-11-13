---
name: fhir-extensions
description: Use when choosing, looking up or writing a standard FHIR R4 extension from the FHIR Extensions Pack (hl7.fhir.uv.extensions.r4 5.4.0) — whether a standard extension exists for some data, its canonical URL, value type or sub-extensions, which resources or elements it may be used on, its binding, and whether it is trial-use, draft or deprecated and what replaces it; for example patient-birthPlace, data-absent-reason, individual-genderIdentity or condition-assertedDate. Also covers the pack's value sets, code systems and search parameters. Not for base FHIR R4 resource definitions or for extensions defined in other implementation guides.
license: Apache-2.0
---

This skill is a navigator for a local knowledge base (KB) of everything in the FHIR Extensions Pack
for R4: the global extensions defined for everyone, plus their value sets, code systems and search
parameters. It doesn't cover base FHIR R4 resource definitions (the `fhir` skill does) or
extensions defined by other IGs, such as US Core, QI-Core, CPG (`cpg-`) or CRMI (`crmi-`).

| IG | Package | Version | File prefix | Files |
|----|---------|---------|-------------|-------|
| FHIR Extensions Pack (R4) | `hl7.fhir.uv.extensions.r4` | 5.4.0 | `hl7.fhir.uv.extensions.r4_` | 912 |

The KB has 724 extension definitions, 97 value sets, 67 code systems and 23 search parameters.
Published at <https://hl7.org/fhir/extensions/>.

## Build the KB first

The KB is generated and isn't distributed with the skill. If
`resources/profiles/concise/VERSIONS` doesn't exist, build it once by running
`bash scripts/build-kb.sh` from the skill folder. It needs bash, curl, tar, `python3` and network
access to packages.fhir.org, and takes about a minute. It writes:

- `resources/profiles/concise/`: one markdown rendering per resource. Use these.
- `resources/profiles/full-source/`: the package JSON the renderings came from.

If the KB can't be built, say so and use the published pack at <https://hl7.org/fhir/extensions/>.

## Before recommending an extension

Each extension's header shows, under the publisher line:

- **Standards Status** and **FMM** (maturity, 0 to 5). 106 extensions in this version are
  `deprecated` and 115 are `draft`. Don't recommend a deprecated extension. Read its
  **Status Reason** line, which usually names the replacement, and recommend that instead. For
  example, `patient-genderIdentity` is deprecated in favour of the Gender Harmony extensions such
  as `individual-genderIdentity`. Say when an extension is draft or has a low FMM.
- **Context**: where the extension may be used. Check that the element you want to extend is
  listed (`Element` means anywhere).

Then read the Elements table for the value type. A simple extension has one `Extension.value[x]`
row with its type and binding. A complex extension has `Extension.value[x]` `0..0` and one
`Extension.extension:<name>` slice per sub-extension, each with its own value type.

## Finding an extension

Files are named `hl7.fhir.uv.extensions.r4_{ResourceType}-{id}.md`. Paths below are relative to the
skill folder.

1. **By id**, when you know it:

   ```sh
   cat resources/profiles/concise/hl7.fhir.uv.extensions.r4_StructureDefinition-patient-birthPlace.md
   ```

2. **By the resource it extends**: list the extensions whose context names the resource:

   ```sh
   grep -l '^\*\*Context:\*\*.*`Patient[`.]' resources/profiles/concise/*StructureDefinition-*.md
   ```

   Most ids start with the resource they extend (`patient-`, `condition-`, `observation-`).
   Shared ones start with `individual-`, `artifact-`, `cqf-`, `workflow-` or `request-`.

3. **By topic**: search the descriptions, then check each match's status and context:

   ```sh
   grep -il 'birth' resources/profiles/concise/*StructureDefinition-*.md
   ```

Read only the files you need; the KB is large.

## Writing an extension in JSON

Use the canonical URL from the header as `url`, and the value element named for its type
(`valueAddress`, `valueCode`, `valueCodeableConcept`). For a complex extension, put each
sub-extension in `extension` with its slice name as `url` (for example `"url": "value"`), and give
the outer extension no `value[x]`. To extend a primitive element such as `Patient.birthDate`, put
the extension in the parallel `_birthDate` object, for example
`"_birthDate": {"extension": [{"url": "http://hl7.org/fhir/StructureDefinition/data-absent-reason", "valueCode": "unknown"}]}`.

## Reading a rendering

Element tables use `MS` (mustSupport), `!` (isModifier) and `Σ` (isSummary) as flags, and
`{strength}→{valueSetId}@{version}` for bindings. A binding without a version may point to a value
set in this KB; one with `@4.0.1` is a base R4 value set. For the full format, see
[format-guide.md](resources/format-guide.md).
