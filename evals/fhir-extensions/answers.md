# FHIR Extensions Skill Test Questions: Answer Key

Expected answers for [questions.md](questions.md). Don't give this file to an agent under test.

Facts come from the package `hl7.fhir.uv.extensions.r4` 5.4.0, as rendered in the
`fhir-extensions` skill's knowledge base (`resources/profiles/concise/`, built by
`scripts/build-kb.sh`). A source written as `patient-birthPlace` is the file
`hl7.fhir.uv.extensions.r4_StructureDefinition-patient-birthPlace.md` there. Each answer gives the
expected facts, the source, what a passing answer must and must not say, and where the skill
covers it ("Skill").

An answer fails if it recommends a deprecated extension without saying so, invents an extension,
or gives a URL, value type or context that doesn't match the package.

## Lookups

### EX-01. Place of birth

- **Expected:** `http://hl7.org/fhir/StructureDefinition/patient-birthPlace`, `valueAddress`
  `1..1`, context `Patient`, trial-use, FMM 3 (work group pa).
- **Source:** `patient-birthPlace`.
- **Pass if:** the URL, the `Address` type and the Patient context are correct, and it gives the
  status.
- **Skill:** `SKILL.md` Finding an extension, Before recommending an extension.

### EX-02. Mother's maiden name

- **Expected:** `http://hl7.org/fhir/StructureDefinition/patient-mothersMaidenName`, `valueString`
  `1..1`, context `Patient`, trial-use, FMM 3.
- **Source:** `patient-mothersMaidenName`.
- **Pass if:** the URL and the `string` type are correct.
- **Skill:** `SKILL.md` Finding an extension.

### EX-03. When a condition was asserted

- **Expected:** `http://hl7.org/fhir/StructureDefinition/condition-assertedDate`, `valueDateTime`
  `1..1`, contexts `Condition` and `AllergyIntolerance`, trial-use, FMM 3.
- **Source:** `condition-assertedDate`.
- **Pass if:** the URL, the `dateTime` type and both contexts are correct.
- **Fail if:** it says the extension can be used only on Condition.
- **Skill:** `SKILL.md` Before recommending an extension (Context).

### EX-04. Nationality

- **Expected:** `http://hl7.org/fhir/StructureDefinition/patient-nationality`, contexts
  `Patient`, `RelatedPerson` and `Person`, trial-use, FMM 3. It's a complex extension:
  `Extension.value[x]` is `0..0`, with sub-extensions `code` (`0..1`, `valueCodeableConcept`) and
  `period` (`0..1`, `valuePeriod`).
- **Source:** `patient-nationality`.
- **Pass if:** it says the extension is complex and names both sub-extensions and their types.
- **Fail if:** it gives the extension a top-level `valueCodeableConcept`.
- **Skill:** `SKILL.md` Before recommending an extension (complex extensions), Writing an
  extension in JSON.

## Status

### ST-01. Gender identity

- **Expected:** No. `patient-genderIdentity` is deprecated (FMM 1). Its status reason says it "has
  been replaced by the profiles and extensions defined in the Gender Harmony Guide". Use
  `http://hl7.org/fhir/StructureDefinition/individual-genderIdentity` (trial-use, FMM 2), with
  contexts `Patient`, `RelatedPerson`, `Person`, `Practitioner`, `PractitionerRole` and
  `FamilyMemberHistory`. It's complex: sub-extension `value` (`1..1`, `valueCodeableConcept`,
  preferred binding to `gender-identity`), `period` (`0..1`, `valuePeriod`) and `comment`
  (`0..1`, `valueString`).
- **Source:** `patient-genderIdentity` (Standards Status, Status Reason);
  `individual-genderIdentity`.
- **Pass if:** it says the extension is deprecated, recommends `individual-genderIdentity`, and
  describes the `value` sub-extension.
- **Fail if:** it recommends `patient-genderIdentity`, or gives `individual-genderIdentity` a
  top-level value.
- **Skill:** `SKILL.md` Before recommending an extension (names this example).

### ST-02. Disability

- **Expected:** No. `patient-disability` is deprecated. The pack says to use the Flag resource for
  disability information meant for administrative use, and Condition for clinical diagnoses that
  correspond to disabilities.
- **Source:** `patient-disability` (Standards Status, Description).
- **Pass if:** it says the extension is deprecated and names Flag and Condition.
- **Skill:** `SKILL.md` Before recommending an extension.

## Usage

### US-01. A missing value

- **Expected:** `http://hl7.org/fhir/StructureDefinition/data-absent-reason`, `valueCode` `1..1`
  with a required binding to the `data-absent-reason` value set (for example `unknown`), context
  `Element` (any element), trial-use, FMM 3. `birthDate` is a primitive, so the extension goes in
  `_birthDate`: `"_birthDate": {"extension": [{"url": "...data-absent-reason", "valueCode":
  "unknown"}]}`, with no `birthDate` value.
- **Source:** `data-absent-reason`; R4 JSON representation of primitive extensions.
- **Pass if:** the URL and the `_birthDate` placement are correct.
- **Fail if:** it puts the extension in `Patient.extension`, or sets `birthDate` to a placeholder
  date.
- **Skill:** `SKILL.md` Writing an extension in JSON.

## Tasks

### TK-01. A Patient with extensions

Grade the saved Patient with [grade_patient.py](grade_patient.py), then read it.

- **Script checks** (each must pass):
  - `resourceType` is `Patient`.
  - `patient-birthPlace` with a `valueAddress` whose city is Lisbon.
  - `patient-mothersMaidenName` with `valueString` `Silva`.
  - `patient-nationality` with a `code` sub-extension whose `valueCodeableConcept` has code `PT`,
    and no top-level value.
  - `individual-genderIdentity` with a `value` sub-extension holding a `valueCodeableConcept`, and
    no top-level value. No `patient-genderIdentity`.
  - No `birthDate` value, and a `data-absent-reason` extension in `_birthDate` with a
    data-absent-reason code.
- **Fail if:** the script fails.
- **Skill:** `SKILL.md` Before recommending an extension, Writing an extension in JSON.
