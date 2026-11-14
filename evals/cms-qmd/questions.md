# CMS QMD Skill Test Questions

Questions that check whether an agent writes and reviews CMS measure CQL following the CMS FHIR
Quality Measure Development IG (continuous build, 3 November 2026) against US Quality Core 0.5.0.
The answer key is in [answers.md](answers.md). Keep it out of any copy of the skill given to an
agent under test.

## Patterns

### PT-01. Active during the measurement period

A measure needs diabetes that was active at any time during the measurement period. A developer
writes `[USQualityCore.ConditionProblemsHealthConcerns: "Diabetes"] C where C.isActive()`. What's
wrong, and what should be used instead?

### PT-02. Not prescribed

A measure's numerator is "patients not prescribed a statin". No reason for the absence is part of
the measure's intent. Should the logic use the Medication Not Requested profile?

### PT-03. Diagnosis during an encounter

Where can evidence that a diagnosis was present during an encounter come from, according to the
CMS QMD patterns?

### PT-04. Logic layers

Name the four logic layers, and say which layer should contain the retrieves.

### PT-05. Terminology operators

Which operator compares `Observation.code` to a direct-reference code, which compares it to a
value set, and what should be used instead of `contains` with a list of codes?

## Models and libraries

### ML-01. Unqualified types

A measure library declares `using USQualityCore`, `using USCore` and `using FHIR`, and defines
`[Procedure: "Colonoscopy"]`. Which profile does the retrieve use, and what does the IG say to do?

### ML-02. Shared library behaviour

Which encounter retrieves in CQMCommon 5.2.000 resolve to base FHIR Encounter rather than the US
Quality Core Encounter profile, and does that stop them returning data?

### ML-03. Refactored libraries

What is happening to CQMCommon, and where do you find where its definitions moved?

### ML-04. Prevalence

Why does the IG recommend CQMConcepts' `prevalencePeriod()` over FHIRCommon 2.0.0's
`prevalenceInterval()`?

## Tasks

### TK-01. A measure fragment

Write a CQL library `DiabetesStatinCheck` against US Quality Core 0.5.0 that defines:

- `"Qualifying Encounters"`: finished encounters in the value set "Office Visit"
  (`http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.101.12.1001`) during the
  parameter `"Measurement Period"` (`Interval<DateTime>`)
- `"Encounters With Diabetes"`: qualifying encounters with diabetes (value set "Diabetes",
  `http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.464.1003.103.12.1001`), either as an
  encounter diagnosis linked to the encounter, or as a problem-list item present during the
  encounter
- `"Has Statin Order"`: whether a statin (value set "Statin Therapy",
  `http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.117.1.1.1`) was ordered during the measurement
  period
- `"Diabetic Patients Without Statin Order"`: true when the patient has an encounter with diabetes
  and no statin order. No reason for the missing order is needed.

Use the CMS QMD shared libraries where they help. Save it as `DiabetesStatinCheck.cql`.
