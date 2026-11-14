# madie Skill Test Questions: Answer Key

Expected answers for [questions.md](questions.md). Don't give this file to an agent under test.

Facts are as the `madie` skill records them for MADiE `develop` as of 2026-11-14, from the code at the
commits in the skill's SOURCES.md. Several contradict the skill's original source, which an agent may
have learned from; those are marked. "Skill" says where the skill covers it.

## Zips and the `.madie` file

### ZP-01. A parent folder

- **Expected:** MADiE only counts zip entries whose first path segment is a UUID. With everything under
  `TestCases/`, no entry qualifies. Zip the folder's contents (the `.madie` file and the UUID folders),
  not the folder.
- **Pass if:** parent folder, zip the contents.
- **Skill:** `resources/test-case-files.md` (Importing a zip).

### ZP-02. testCaseId

- **Expected:** you don't need to: `testCaseId` is MADiE's internal id, written on export and not read on
  import. Any value, or none, works; the entry is matched to its folder by `patientId`.
- **Pass if:** not read on import; matched by `patientId`.
- **Fail if:** it gives a derivation (the original skill said an md5 of the patient id).
- **Skill:** `resources/test-case-files.md` (The `.madie` file).

### ZP-03. An old zip

- **Expected:** exports before 20 June 2024 have no `.madie` file, which import now requires. Re-export
  from the original measure, or add a `.madie` file listing each folder's `patientId`, `title`, `series`
  and `description`.
- **Pass if:** missing `.madie`, with either fix.
- **Skill:** `resources/test-case-files.md`.

## Importing

### IM-01. Copying test cases

- **Expected:** import matches test cases by patient id (the folder UUID). The exported ids match the
  existing test cases, so each was updated (description and JSON only; title, series and expected values
  kept), not duplicated. To copy, give the folders new UUIDs (and update `.madie`) and change the titles
  or series, since title and series must be unique in a measure.
- **Pass if:** matched by patient id, so updated; new UUIDs to copy.
- **Partial if:** new UUIDs without the reason.
- **Skill:** `resources/test-case-files.md` (New or updated).

### IM-02. No expected values

- **Expected:** expected values are read from the MeasureReport only when its groups and populations
  match the measure's: `group.id` must end in the group number (`Group_1`), and the populations must be
  in the measure's order with `measure-population` codes. If the counts differ, the test case is imported
  without expected values. Also, an import that updates an existing test case never changes its expected
  values.
- **Pass if:** group id, population order and codes.
- **Skill:** `resources/test-case-files.md` (The MeasureReport).

### IM-03. Title required

- **Expected:** a new test case is refused when the Patient has no given name, and MADiE checks this
  before it uses the `.madie` title. Give the Patient a `name` with `given` and `family`.
- **Pass if:** Patient given name.
- **Skill:** `resources/test-case-files.md`.

### IM-04. A transaction bundle

- **Expected:** transaction bundles are accepted; MADiE stores them as collections and removes the
  `request` entries. But MADiE resolves references only as `<Type>/<id>` within the bundle, so
  `urn:uuid:` references don't resolve: the referencing resources are left out of execution (an error if
  it's the Patient). Give resources ids and use `Patient/<id>`, `Encounter/<id>` references.
- **Pass if:** transaction is fine; `urn:uuid` references aren't.
- **Fail if:** it says transaction bundles are rejected.
- **Skill:** `resources/test-case-files.md`, `resources/test-case-content.md` (Ids and references).

## Exporting

### EX-01. File names

- **Expected:** `<patient id>/<eCQM abbreviated title>-v<version>-<series>-<title>.json`, with
  whitespace removed from the series and title, and without the series part when it's empty. The
  version is `major.minor.revision` with three revision digits.
- **Pass if:** eCQM abbreviated title (not the measure name) and the parts in order.
- **Skill:** `resources/test-case-files.md` (The export zip).

### EX-02. Changing ids

- **Expected:** normal. Every export gives each resource except the Patient a new random UUID and
  updates references to match; the Patient's id is the test case's patient id.
- **Pass if:** new ids on each export by design.
- **Skill:** `resources/test-case-files.md` (What MADiE changes in the JSON).

### EX-03. The MeasureReport profile

- **Expected:** `http://hl7.org/fhir/uv/cqm/StructureDefinition/cqm-testcase` (the CQM IG), with the
  `cqm-isTestCase` modifier extension and a contained Parameters resource.
- **Fail if:** `test-case-cqfm` (the original skill's answer).
- **Skill:** `resources/test-case-files.md` (The MeasureReport).

## Validation and resources

### VA-01. meta.profile

- **Expected:** yes: a missing `meta.profile` is a warning, not an error. The resource isn't validated
  against a QI-Core profile, though, and MADiE warns it may give incorrect results.
- **Pass if:** warning only.
- **Skill:** `resources/test-case-content.md` (Validation).

### VA-02. A dangling reference

- **Expected:** a warning, and the Condition is left out when the test case runs. (In the Patient it
  would be an error.)
- **Pass if:** warning and dropped from execution.
- **Skill:** `resources/test-case-content.md`.

### RS-01. Simple Observation

- **Expected:** no. In QI-Core 6.0.0, Simple Observation's `value[x]` is optional and must-support, and
  its category isn't fixed. Whether the Observation counts depends on the measure's CQL; many measures
  test that a value is present and the status is final, amended or corrected.
- **Fail if:** it agrees that the profile forbids a value (the original skill's claim).
- **Skill:** `resources/test-case-content.md` (Resource notes).

### RS-02. Confirmed conditions

- **Expected:** no. `verificationStatus` is optional. The common `Status` library's `verified()` keeps
  conditions with no verification status, or confirmed, unconfirmed, provisional or differential; it
  drops refuted and entered-in-error. QICoreCommon's `isActive()` looks at `clinicalStatus`. The
  measure's own CQL decides.
- **Fail if:** "must be confirmed".
- **Skill:** `resources/test-case-content.md`.

### RS-03. A Condition profile

- **Expected:** yes. `qicore-condition` is QI-Core 4.1.1. In 6.0.0 it's
  `qicore-condition-problems-health-concerns` or `qicore-condition-encounter-diagnosis`; MADiE validates
  against the measure's QI-Core version only.
- **Pass if:** names the 6.0.0 profiles.
- **Skill:** `resources/test-case-content.md` (QI-Core profiles by version).

## Measure CQL

### CQ-01. The library line

- **Expected:** MADiE rewrites the `library` line on save to the measure's CQL library name and version
  ("Library statement was incorrect. MADiE has overwritten it."). Change the name or version in the
  measure's details, or version the measure, not in the CQL.
- **Pass if:** rewritten to match the measure.
- **Skill:** `resources/measure-cql.md`.

### CQ-02. A value set URL

- **Expected:** QI-Core measures need VSAC FHIR URLs:
  `'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1001'`.
- **Pass if:** the VSAC URL form.
- **Skill:** `resources/measure-cql.md`.

### CQ-03. A library name

- **Expected:** no. FHIR-based measures need `^[A-Z][a-zA-Z0-9]*$` (no underscores; QDM allows them), at
  most 64 characters. `FollowUpMeasure` works.
- **Pass if:** no underscores.
- **Skill:** `resources/measure-cql.md`.

## Series

### SE-01. Series names

- **Expected:** no. The series ("Test Case Group") is free text; `IPPPass` and the like are a Bonnie-era
  convention. Title and series together must be unique in a measure, and should use only letters,
  digits, spaces and `-` (the browser rejects `_` and other punctuation on export). The expected values,
  not the series, are what MADiE checks.
- **Pass if:** free text, a convention only.
- **Skill:** `resources/test-case-files.md` (Titles and series).

## Versions

### VR-01. A newer MADiE

- **Expected:** search the MADiE repositories' current `develop` branches for the message text to find
  the rule, read the code near the skill's cited lines, and answer from it, saying the answer is read
  from source.
- **Pass if:** checks the current code rather than guessing.
- **Skill:** SKILL.md (When MADiE Has Changed).

## Task

### TK-01. Build test cases for import

Run `python grade_testcases.py <answer>/tk-01`. It checks:

- the layout (a `.madie` file at the root and three UUID folders with one JSON bundle each, no parent
  folder);
- `.madie` (an entry per folder with the given series and title, unique);
- each bundle (one Patient with given and family names, an identifier and a gender; unique ids;
  relative references that resolve; QI-Core 6.0.0 profiles only);
- the data (a finished Encounter with class `IMP` for every case, a `type` on every Encounter, an `AMB`
  Encounter for the follow-up case, an active Condition for the hospice case);
- a MeasureReport per bundle: `Group_1`, the four populations in order with `measure-population` codes,
  and the counts from the task's table.

- **Pass if:** every check passes. **Partial if:** one fails.
- **Reference:** [reference/tk-01/](reference/tk-01/). It also passes the skill's
  `scripts/check_test_cases.py --model qicore6`, and the FHIR validator against QI-Core 6.0.0 with no
  errors.
