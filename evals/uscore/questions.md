# US Core Skill Test Questions

Questions that check whether an agent applies US Core 6.1.0 and 9.0.0 from the published profiles,
rather than from memory of other versions. The answer key is in [answers.md](answers.md). Keep it
out of any copy of the skill given to an agent under test.

Answer for the US Core version each question names. Give canonical URLs in full.

## Lookups

### LK-01. Two Condition profiles

Which US Core profile should a Condition from an encounter's diagnosis list claim, and which one
should a problem-list item claim?

### LK-02. The sex extension

In US Core 9.0.0, which extension records a patient's sex, what is its value type, and what
happened to the extension US Core 6.1.0 used?

### LK-03. Gender identity

A developer upgrading from US Core 6.1.0 to 9.0.0 wants to keep sending
`http://hl7.org/fhir/us/core/StructureDefinition/us-core-genderIdentity`. What should they do?

## Requirements

### RQ-01. Additional USCDI Requirements

What does the USCDI flag on an element such as `Patient.telecom` mean, and when must a system
treat it as Must Support?

### RQ-02. A missing mandatory status

A server holds a Condition whose clinical status was never recorded, in a case where US Core
requires `Condition.clinicalStatus`. Can it send `unknown` from the DataAbsentReason code system?
What happens when a client reads that Condition?

### RQ-03. Text-only codes

A system has only free text for `AllergyIntolerance.code` (extensible binding) and for
`AllergyIntolerance.clinicalStatus` (required binding). Is a text-only value valid in each?

## Versions

### VR-01. Unknown administrative gender

A patient's administrative gender is unknown. How should `Patient.gender` be populated for US Core
6.1.0, and for US Core 9.0.0?

### VR-02. New and removed profiles

Name three profiles that US Core 9.0.0 added since 6.1.0, and the profile it removed.

## Tasks

### TK-01. A US Core 9.0.0 Patient

Write a Patient resource, as JSON, that conforms to US Core 9.0.0, for:

- medical record number `MRN-48213` (choose an identifier system)
- name: Maria Reyes, born 1984-03-07
- race: White; ethnicity: Hispanic or Latino
- sex: female, as documented by the clinic
- gender identity: a code of your choice, using an extension that isn't deprecated
- the patient needs an interpreter
- administrative gender: not recorded

Save it as `patient.json`.
