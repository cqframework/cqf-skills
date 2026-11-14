# CQL IG Skill Test Questions

Questions that check whether an agent applies the Using CQL With FHIR IG (`hl7.fhir.uv.cql`
2.0.0): its conformance requirements, the FHIR ModelInfo, FHIRHelpers and FHIRCommon. The answer
key is in [answers.md](answers.md). Keep it out of any copy of the skill given to an agent under
test.

Answer for Using CQL With FHIR 2.0.0, FHIR R4 (4.0.1). Cite conformance requirement numbers where
they apply.

## Lookups

### LK-01. FHIRHelpers and FHIRCommon

What are the canonical URLs and versions of FHIRHelpers and FHIRCommon as published in this IG?
Why do their versions differ?

### LK-02. Primary code paths

In the FHIR ModelInfo, what is the primary code path of MedicationRequest, and of
DeviceUseStatement? What does the translator do with `[AuditEvent: "Some Value Set"]`?

### LK-03. A choice element

What is the CQL type of `Observation.effective` in the FHIR ModelInfo? How would you compare it
to a date range when you don't know which type an instance uses?

## Conformance

### CF-01. Library names

A team wants to name its library `Diabetes_Screening_v2`. Does that conform? If not, why not,
and what would?

### CF-02. Library resource identity

A CQL library is declared `library Common version '2.0.0'` in a namespace whose URI is
`http://example.org/fhir`. What are the `url`, `name` and `version` of the FHIR Library that
carries it?

### CF-03. Includes

Is `include FHIRHelpers version '4.0.1'` acceptable in a library used by a FHIR artifact? What
happens if a library that compares FHIR elements to CQL values leaves FHIRHelpers out altogether?

### CF-04. Type mapping

Which FHIR types do `System.Long`, `Interval<System.DateTime>` and `Interval<System.Quantity>`
map to in FHIR R4?

### CF-05. Translator options

Which translator options does the IG recommend for knowledge artifacts, and which does it say
should not be used?

## Patterns

### PT-01. A missing boolean

Why is `where MR.doNotPerform = false` a problem when looking for MedicationRequests that are not
prohibitions, and what should be written instead?

### PT-02. Active conditions

What exactly does FHIRCommon's `isActive()` test for a Condition?

## Operations

### OP-01. Evaluating results

A client calls `Library/$evaluate` on a library with a definition that returns three Observations
and another that returns an empty list. How are the two results represented in the returned
Parameters, and how does `$cql` differ from `Library/$evaluate`?

## Tasks

### TK-01. Packaging a library

Package this CQL as a FHIR R4 Library resource that conforms to the IG. The library belongs to
the namespace `http://example.org/fhir`. Save it as `library.json`.

```cql
library DiabetesScreening version '1.0.0'

using FHIR version '4.0.1'

include FHIRHelpers version '4.0.1' called FHIRHelpers

codesystem "LOINC": 'http://loinc.org'

valueset "Diabetes": 'http://example.org/fhir/ValueSet/diabetes'

code "HbA1c": '4548-4' from "LOINC" display 'Hemoglobin A1c'

parameter "Measurement Period" Interval<DateTime>

context Patient

define "Has Diabetes":
  exists [Condition: "Diabetes"]

define "HbA1c Results":
  [Observation: "HbA1c"] O
    where O.status = 'final'
```
