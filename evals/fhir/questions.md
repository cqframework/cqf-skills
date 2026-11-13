# FHIR Skill Test Questions

Questions that check whether an agent answers base FHIR R4 (4.0.1) questions from the R4
definitions, rather than from memory of other FHIR versions or of implementation guide profiles.
The answer key is in [answers.md](answers.md). Keep it out of any copy of the skill given to an
agent under test.

Answer each question for base FHIR R4 (4.0.1), with no implementation guide profiles applied
unless the question names one. Give cardinalities as `min..max`, and name the invariant (for
example `bdl-3`) when one decides the answer.

## Element definitions

### EL-01. Encounter class

In FHIR R4, what is the type and cardinality of `Encounter.class`, and what is its binding? Write
the `class` element for an inpatient encounter.

### EL-02. A minimal Observation

Which elements must a base R4 Observation have to be valid? Is `subject` one of them?

### EL-03. A minimal MedicationRequest

Which elements are required on a base R4 MedicationRequest? Which of them are modifier elements?

### EL-04. Condition status rules

A Condition has `verificationStatus` `entered-in-error`. May it also have a `clinicalStatus`? A
different Condition has an `abatementDateTime`. Which `clinicalStatus` values may it have?

### EL-05. Immunization status and date

Which `status` codes does a base R4 Immunization allow, and which element records when the vaccine
was given? Is that element required, and which types can it take?

### EL-06. Choice elements

What types can `Procedure.performed[x]` and `Patient.deceased[x]` take in R4? Is
`Patient.deceased[x]` a modifier element?

### EL-07. Coverage

Which elements are required on a base R4 Coverage, and with what cardinality?

## Bundles

### BD-01. Request entries

In which bundle types must each entry have a `request`, and in which is `request` not allowed? A
`collection` bundle has entries with `request.method` `PUT`. Is it valid?

### BD-02. Creating resources that reference each other

A transaction creates a new Patient and a new Condition for that patient, and the server assigns
both ids. How should each entry's `fullUrl`, `request` and the Condition's `subject` reference be
written, and what does the server do with them?

### BD-03. Document bundles

What must a `document` bundle contain to be valid in R4?

### BD-04. fullUrl rules

Can two entries in a transaction bundle have the same `fullUrl`? Can a `fullUrl` be
`https://example.org/fhir/Patient/123/_history/2`?

## Tasks

### TK-01. A transaction bundle

Write a FHIR R4 transaction bundle, as JSON, that upserts:

- a Patient: female, born 1958-03-02
- a finished inpatient Encounter for that patient, from 2025-01-15 to 2025-01-17
- an active, confirmed Condition for that patient, type 2 diabetes mellitus (SNOMED CT
  `44054006`), recorded during that encounter
- a final HbA1c Observation for that patient (LOINC `4548-4`) of 8.5 %, taken on 2025-01-16

Use resource ids that come out the same every time the bundle is generated, and say how you made
them. Save the bundle as `bundle.json`.
