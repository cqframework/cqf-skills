---
name: cpg
description: Use when working with the CPG (Clinical Practice Guidelines) 2.0.0 implementation guide — choosing and applying its profiles for computable guidelines, such as recommendation, strategy and pathway PlanDefinitions, computable activities, case feature definitions, metrics and CPG Questionnaires; their required and mustSupport elements and bindings; CPG extensions such as directionOfRecommendation; and the cqf- extensions CPG profiles use (FHIR Extensions R4 5.4.0). Looks answers up in a local knowledge base of the published definitions. Not for base FHIR R4 resource definitions or CRMI artifact lifecycle and packaging.
license: Apache-2.0
---

This skill is a navigator for a local knowledge base (KB) of everything published in the CPG
package, plus the FHIR Extensions pack, whose `cqf-` extensions CPG profiles use. It doesn't cover
base FHIR R4 resource definitions (the `fhir` skill does) or CRMI artifact management and packaging
(the `crmi` skill does).

| IG | Package | Version | File prefix | Files |
|----|---------|---------|-------------|-------|
| Clinical Practice Guidelines | `hl7.fhir.uv.cpg` | 2.0.0 | `hl7.fhir.uv.cpg_` | 574 |
| FHIR Extensions Pack (R4) | `hl7.fhir.uv.extensions.r4` | 5.4.0 | `hl7.fhir.uv.extensions.r4_` | 912 |

The KB holds the packages' StructureDefinitions (profiles and extensions), ValueSets,
CodeSystems, SearchParameters, OperationDefinitions and example instances.

## Build the KB first

The KB is generated and isn't distributed with the skill. If
`resources/profiles/concise/VERSIONS` doesn't exist, build it once by running
`bash scripts/build-kb.sh` from the skill folder. It needs bash, curl, tar, `python3` and network
access to packages.fhir.org, and takes about a minute. It writes:

- `resources/profiles/concise/`: one markdown rendering per resource. Use these.
- `resources/profiles/full-source/`: the package JSON the renderings came from. Use it for text
  the renderings shorten and for canonical URL searches.

If the KB can't be built, say so and use the published IGs instead:
<https://hl7.org/fhir/uv/cpg/> and <https://hl7.org/fhir/extensions/>.

## Versions

Answer for the versions above, and say which version you used. A project on CPG 1.0.0 may differ.
In particular, CPG 2.0.0 no longer has CPG 1.0.0's shareable and publishable artifact profiles
(`cpg-publishableplandefinition`, `cpg-shareablelibrary` and the rest). CRMI 2.0.0 defines
shareable and publishable profiles for these artifacts instead, for example
`crmi-shareableplandefinition` and `crmi-publishablelibrary`; the `crmi` skill covers them. If a
project names a CPG profile that isn't in the KB, check whether it belongs to CPG 1.0.0 before
saying it doesn't exist.

## File lookup

Files are named `{package}_{ResourceType}-{id}.md`. Paths below are relative to the skill folder.

1. **Direct lookup** when you know the package, resource type and id:

   ```sh
   cat resources/profiles/concise/hl7.fhir.uv.cpg_StructureDefinition-cpg-recommendationdefinition.md
   ```

2. **Search the listing** when part of the name is unknown:

   ```sh
   ls resources/profiles/concise/ | grep -i "casefeature"
   ```

3. **Canonical URL lookup**, in the source JSON:

   ```sh
   grep -l '"url" *: *"http://hl7.org/fhir/uv/cpg/StructureDefinition/cpg-computableplandefinition"' resources/profiles/full-source/*.json
   ```

Read only the files you need; the KB is large. A profile's **Base** line names its parent; read
the parent's file too when the profile derives from another CPG profile.

## Reading a rendering

Element tables use `MS` (mustSupport), `!` (isModifier) and `Σ` (isSummary) as flags, and
`{strength}→{valueSetId}@{version}` for bindings. Fixed values and patterns, such as the
`PlanDefinition.type` pattern that distinguishes recommendation, strategy and pathway definitions,
are in the Element Details section. For the full format of each resource type, see
[format-guide.md](resources/format-guide.md).
