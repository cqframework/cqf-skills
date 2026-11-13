---
name: crmi
description: Use when working with the CRMI (Canonical Resource Management Infrastructure) 2.0.0 implementation guide — which shareable, publishable, computable or executable profile a Library, PlanDefinition, ActivityDefinition, Measure, Questionnaire or ValueSet should claim and what each requires; artifact lifecycle and packaging operations such as $package, $release, $approve and $data-requirements; manifest libraries; and the cqf- and artifact- extensions these use (FHIR Extensions R4 5.4.0). Looks answers up in a local knowledge base of the published definitions. Not for base FHIR R4 resource definitions or CPG clinical guideline profiles.
license: Apache-2.0
---

This skill is a navigator for a local knowledge base (KB) of everything published in the CRMI
package, plus the FHIR Extensions pack, whose `cqf-` and `artifact-` extensions CRMI profiles use.
It doesn't cover base FHIR R4 resource definitions (the `fhir` skill does) or CPG profiles (the
`cpg` skill does).

| IG | Package | Version | File prefix | Files |
|----|---------|---------|-------------|-------|
| Canonical Resource Management Infrastructure | `hl7.fhir.uv.crmi` | 2.0.0 | `hl7.fhir.uv.crmi_` | 199 |
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
  the renderings shorten, such as operation parameter documentation, and for canonical URL
  searches.

If the KB can't be built, say so and use the published IGs instead:
<https://hl7.org/fhir/uv/crmi/> and <https://hl7.org/fhir/extensions/>.

## Capability profiles are claimed together

CRMI defines a profile per artifact type for each capability: shareable, publishable, computable
and executable (for example `crmi-shareablelibrary`, `crmi-publishablelibrary`,
`crmi-computablelibrary`, `crmi-executablelibrary`). In CRMI 2.0.0 each of these derives directly
from the base resource, not from the others. So `crmi-publishablelibrary` doesn't require what
`crmi-shareablelibrary` requires (such as `url`, `version`, `title` and `description`). An artifact
that is meant to be both lists both profiles in `meta.profile`. Artifacts declare their
capabilities with the `cqf-knowledgeCapability` extension. Check each profile's own Elements table
for what it requires.

## Versions

Answer for the versions above, and say which version you used. A project on CRMI 1.0.0 may differ.
CPG 1.0.0 had its own shareable and publishable artifact profiles (`cpg-publishableplandefinition`,
`cpg-shareablelibrary` and others). CPG 2.0.0 dropped them, and the CRMI profiles take their place.

## File lookup

Files are named `{package}_{ResourceType}-{id}.md`. Paths below are relative to the skill folder.

1. **Direct lookup** when you know the package, resource type and id:

   ```sh
   cat resources/profiles/concise/hl7.fhir.uv.crmi_StructureDefinition-crmi-publishablelibrary.md
   ```

2. **Search the listing** when part of the name is unknown:

   ```sh
   ls resources/profiles/concise/ | grep -i "shareableplandefinition"
   ```

3. **Canonical URL lookup**, in the source JSON:

   ```sh
   grep -l '"url" *: *"http://hl7.org/fhir/uv/crmi/OperationDefinition/crmi-package"' resources/profiles/full-source/*.json
   ```

Read only the files you need; the KB is large.

## Reading a rendering

Element tables use `MS` (mustSupport), `!` (isModifier) and `Σ` (isSummary) as flags, and
`{strength}→{valueSetId}@{version}` for bindings. To follow a binding to its value set, search the
listing for the value set id. For the full format of each resource type, see
[format-guide.md](resources/format-guide.md).
