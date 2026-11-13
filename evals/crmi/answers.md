# CRMI Skill Test Questions: Answer Key

Expected answers for [questions.md](questions.md). Don't give this file to an agent under test.

Facts come from the packages `hl7.fhir.uv.crmi` 2.0.0 and `hl7.fhir.uv.extensions.r4` 5.4.0, as
rendered in the `crmi` skill's knowledge base (`resources/profiles/concise/`, built by
`scripts/build-kb.sh`). A source written as `crmi_StructureDefinition-crmi-shareablelibrary` is
the file `hl7.fhir.uv.crmi_StructureDefinition-crmi-shareablelibrary.md` there. VR-01 also relies
on the contents of CPG 2.0.0 (`hl7.fhir.uv.cpg`). Each answer gives the expected facts, the source,
what a passing answer must and must not say, and where the skill covers it ("Skill").

An answer fails if it presents a CPG 1.0.0 profile as current, invents a profile, extension or
code, or gives a canonical URL that doesn't match the package.

## Versions

### VR-01. An older CPG profile

- **Expected:** No. Both are CPG 1.0.0 profiles; CPG 2.0.0 has no shareable or publishable artifact
  profiles. CRMI 2.0.0 defines them: claim `crmi-shareableplandefinition` and
  `crmi-publishableplandefinition` for PlanDefinitions, and `crmi-shareablelibrary` and
  `crmi-publishablelibrary` for Libraries
  (`http://hl7.org/fhir/uv/crmi/StructureDefinition/<id>`).
- **Source:** `crmi_StructureDefinition-crmi-shareableplandefinition`,
  `crmi_StructureDefinition-crmi-publishableplandefinition`; no `cpg-publishable*` or
  `cpg-shareable*` profile in CPG 2.0.0.
- **Pass if:** it says the profiles are from CPG 1.0.0 and names the CRMI profiles with correct
  URLs.
- **Fail if:** it describes `cpg-publishableplandefinition` as current, or says the profiles never
  existed.
- **Skill:** `SKILL.md` Versions.

## Profiles

### PR-01. A shareable Library

- **Expected:** `url` `1..1`, `version` `1..1`, `title` `1..1`, `status` `1..1`, `type` `1..1` and
  `description` `1..1`. `name` is `0..1` (mustSupport, not required). `url`, `version`, `title`,
  `status` and `description` are mustSupport. The `knowledgeCapability`, `versionAlgorithm` and
  `webSource` extension slices are mustSupport, with `0..*`, `0..1` and `0..1`.
- **Source:** `crmi_StructureDefinition-crmi-shareablelibrary`, Elements.
- **Pass if:** it lists exactly those six required elements and says `name` is optional.
- **Fail if:** it says `name` or `date` is required by this profile.
- **Skill:** KB lookup (`SKILL.md` File lookup).

### PR-02. Publishable without shareable

- **Expected:** No. In CRMI 2.0.0, `crmi-publishablelibrary` derives directly from `Library`, not
  from `crmi-shareablelibrary`. On its own it requires only `status` `1..1`, `type` `1..1` and
  `date` `1..1`. `url`, `version`, `title` and `description` stay `0..1`. To require them, the
  Library must also claim `crmi-shareablelibrary`. (`crmi-computablelibrary` and
  `crmi-executablelibrary` also derive directly from `Library`.)
- **Source:** `crmi_StructureDefinition-crmi-publishablelibrary`: **Base** `Library`; Elements
  `Library.url 0..1`, `Library.date 1..1`.
- **Pass if:** it says the publishable profile doesn't require `url` or `version`, names `status`,
  `type` and `date`, and says to claim both profiles.
- **Fail if:** it says publishable inherits shareable's requirements.
- **Skill:** `SKILL.md` Capability profiles are claimed together; KB lookup.

## Extensions

### EX-01. Knowledge capability

- **Expected:** `http://hl7.org/fhir/StructureDefinition/cqf-knowledgeCapability` (FHIR Extensions
  5.4.0). The value is `valueCode` `1..1`, with a required binding to `knowledge-capability`:
  `shareable`, `computable`, `publishable` and `executable`. The CRMI profiles slice it as
  `extension:knowledgeCapability` `0..*`, mustSupport.
- **Source:** `extensions.r4_StructureDefinition-cqf-knowledgeCapability`,
  `extensions.r4_CodeSystem-knowledge-capability`.
- **Pass if:** the URL, the `code` type and all four codes are correct.
- **Fail if:** it gives a `crmi-` or `cpg-` URL for this extension.
- **Skill:** `SKILL.md` Capability profiles are claimed together; KB lookup.

### EX-02. Copyright label

- **Expected:** `http://hl7.org/fhir/StructureDefinition/artifact-copyrightLabel`, `valueString`
  `1..1` (status draft in Extensions 5.4.0). Yes: `crmi-publishablelibrary` has the slice
  `extension:copyrightLabel` `0..1`, mustSupport.
- **Source:** `extensions.r4_StructureDefinition-artifact-copyrightLabel`,
  `crmi_StructureDefinition-crmi-publishablelibrary`.
- **Pass if:** the URL, the `string` type and the mustSupport answer are correct.
- **Skill:** KB lookup.

## Operations

### OP-01. $package

- **Expected:** `http://hl7.org/fhir/uv/crmi/OperationDefinition/crmi-package`, code `package`.
  Type and instance level, not system level, on canonical resources including Library, Measure,
  PlanDefinition, ActivityDefinition, Questionnaire, ValueSet and CodeSystem. It returns `return`
  `1..1` `Bundle`. A paged result (`count` or `offset`) is a `collection`, and `count = 0` gives a
  `searchset`. The first resource is an outcome manifest: OperationOutcome content that clients
  SHALL examine to see whether the bundle holds what they expected.
- **Source:** `crmi_OperationDefinition-crmi-package` (header and Parameters), and the `return`
  parameter documentation.
- **Pass if:** it gives the URL, says type and instance (not system), says the result is a Bundle,
  and names the outcome manifest as the first resource.
- **Fail if:** it says `$package` returns a Library or an ImplementationGuide.
- **Skill:** KB lookup.

## Tasks

### TK-01. A shareable, publishable logic library

Grade the saved Library with [grade_library.py](grade_library.py), then read it.

- **Script checks** (each must pass):
  - `resourceType` is `Library`. `meta.profile` holds both
    `http://hl7.org/fhir/uv/crmi/StructureDefinition/crmi-shareablelibrary` and
    `http://hl7.org/fhir/uv/crmi/StructureDefinition/crmi-publishablelibrary`, and no `cpg-` profile.
  - The given `url` and `version`, plus a `name`, `title` and `description`.
  - `status` is a publication-status code, and `date` is present (publishable).
  - `type` has the coding `http://terminology.hl7.org/CodeSystem/library-type` `logic-library`.
  - `cqf-knowledgeCapability` extensions with the correct URL and `valueCode` `shareable` and
    `publishable`.
  - `content` has an attachment with `contentType` `text/cql`.
- **Fail if:** the script fails, or it claims a CPG 1.0.0 profile.
- **Skill:** `SKILL.md` Capability profiles are claimed together; KB lookup of
  `crmi-shareablelibrary`, `crmi-publishablelibrary` and `cqf-knowledgeCapability`.
