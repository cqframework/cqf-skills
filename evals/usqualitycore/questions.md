# US Quality Core Skill Test Questions

Questions that check whether an agent applies US Quality Core 0.5.0 (`fhir.onc.us-quality-core`)
from the published profiles and pages, rather than treating it as QI-Core or US Core. The answer
key is in [answers.md](answers.md). Keep it out of any copy of the skill given to an agent under
test.

Answer for US Quality Core 0.5.0.

## Conformance

### CF-01. How requirements are marked

How does US Quality Core mark the elements an implementation must support, and how does that
differ from adding Must Support flags?

### CF-02. Is it in scope?

Must a US Quality Core server support the Communication and Device profiles? What about
Encounter?

### CF-03. Modifiers

What does US Quality Core require of modifier elements that aren't flagged as Must Support?

## Negation

### NG-01. A medication not ordered

A clinician decided not to order an anticoagulant for a documented medical reason. Which US
Quality Core profile records that, and what does the profile fix?

### NG-02. Value set or code

In the Procedure Not Done profile, how do you say which procedure wasn't done, and can you give a
code and a value set at the same time?

## CQL

### CQ-01. A failing comparison

This library fails to translate at the comparison. Why, and what is the fix?

```cql
library GenderCheck version '1.0.0'

using USQualityCore version '0.5.0'

include FHIRHelpers version '4.0.1' called FHIRHelpers

context Patient

define "Is Female":
  Patient.gender = 'female'
```

### CQ-02. The wrong encounters

A library declares `using USQualityCore version '0.5.0'` and `using FHIR version '4.0.1'`, then
`define "Inpatient": [Encounter: "Encounter Inpatient"]`. What does the retrieve return, and how
should it be written?

## QDM

### QD-01. Encounter, Performed

A developer converting a QDM eCQM asks what "Encounter, Performed" maps to in US Quality Core, and
which statuses it covers.

## Tasks

### TK-01. A procedure not done

Write a Procedure resource, as JSON, conforming to the US Quality Core Procedure Not Done profile,
for:

- patient `Patient/example`
- no procedure from the value set `http://example.org/fhir/ValueSet/colonoscopy` was performed
- because the patient refused (SNOMED CT 183944003 "Procedure refused (situation)")
- recorded on 2026-03-04 at 10:00 UTC

Save it as `procedure.json`.
