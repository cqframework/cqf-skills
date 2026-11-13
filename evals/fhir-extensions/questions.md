# FHIR Extensions Skill Test Questions

Questions that check whether an agent finds and applies standard extensions from the FHIR
Extensions Pack for R4 (`hl7.fhir.uv.extensions.r4` 5.4.0), including their status, where they may
be used and their value types, rather than from memory of older versions. The answer key is in
[answers.md](answers.md). Keep it out of any copy of the skill given to an agent under test.

Answer for FHIR R4 and the FHIR Extensions Pack 5.4.0. Give canonical URLs in full and say whether
each extension is draft, trial-use or deprecated.

## Lookups

### EX-01. Place of birth

Is there a standard extension for a patient's place of birth? Give its URL, value type, where it
may be used, and its status and maturity.

### EX-02. Mother's maiden name

Which standard extension records a patient's mother's maiden name, and what is its value type?

### EX-03. When a condition was asserted

Which standard extension records the date a condition was first asserted? Which resources may use
it, and what is its value type?

### EX-04. Nationality

Describe the standard nationality extension: its URL, where it may be used, and its structure.

## Status

### ST-01. Gender identity

A colleague wants to record a patient's gender identity with
`http://hl7.org/fhir/StructureDefinition/patient-genderIdentity`. Is that the right extension to
use? If not, what should they use, and how is it structured?

### ST-02. Disability

Should a new implementation use the `patient-disability` extension? What does the pack say to do
instead?

## Usage

### US-01. A missing value

A patient's date of birth is unknown. Which standard extension records why a value is missing,
where may it be used, and how do you attach it to `Patient.birthDate` in JSON?

## Tasks

### TK-01. A Patient with extensions

Write a FHIR R4 Patient resource, as JSON, using standard extensions from the FHIR Extensions Pack
for:

- place of birth: Lisbon, Portugal
- mother's maiden name: Silva
- nationality: Portuguese (urn:iso:std:iso:3166 code `PT`)
- gender identity: a CodeableConcept of your choice, using the current extension, not a
  deprecated one
- date of birth: unknown, recorded with the reason it is missing

Save it as `patient.json`.
