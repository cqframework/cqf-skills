# CMS QMD Skill Test Questions: Answer Key

Expected answers for [questions.md](questions.md). Don't give this file to an agent under test.

Facts come from the CMS QMD IG at the pinned commit, as rendered in the `cms-qmd` skill: the pages
in `resources/pages/` and the libraries in `resources/libraries/`. Translator behaviour was checked
with the CQL-to-ELM translator 3.29.0, using the USQualityCore and USCore ModelInfo. Each answer
gives the expected facts, the source, what a passing answer must and must not say, and where the
skill covers it ("Skill").

## Patterns

### PT-01. Active during the measurement period

- **Expected:** `isActive()` tests the *current* clinical status, but measures are retrospective,
  so it can't show the condition was active during the measurement period. Use CQMConcepts'
  `prevalencePeriod()` (onset-based) or `relevantPeriod()` (onset, else asserted or recorded
  date), as in `C.prevalencePeriod() overlaps "Measurement Period"`.
- **Source:** `pages/pattern_conditions.md`.
- **Pass if:** it explains current versus retrospective status and names `prevalencePeriod()` or
  `relevantPeriod()`.
- **Fail if:** it keeps `isActive()`, or recommends FHIRCommon's `prevalenceInterval()` without
  noting its known issue.
- **Skill:** `SKILL.md` Authoring guidance (Retrospective status).

### PT-02. Not prescribed

- **Expected:** No. When the reason isn't part of the intent, use absence of evidence: `not exists`
  over the positive MedicationRequest profile. Negation profiles are only for when the logic needs
  documentation that something didn't happen together with a reason.
- **Source:** `pages/pattern_negation.md` (Choosing a negation pattern).
- **Pass if:** it says no and gives absence of evidence.
- **Skill:** `SKILL.md` Authoring guidance (Negation).

### PT-03. Diagnosis during an encounter

- **Expected:** three sources: a ConditionEncounterDiagnosis linked to the encounter, a
  ConditionProblemsHealthConcerns item whose prevalence period overlaps the encounter, and the
  encounter's `reasonCode`. Measure intent decides which to combine.
- **Source:** `pages/pattern_encounters.md` (Evidence of Diagnosis during an Encounter).
- **Pass if:** all three.
- **Partial if:** two.
- **Skill:** `SKILL.md` Authoring guidance (Diagnosis during an encounter).

### PT-04. Logic layers

- **Expected:** Concepts (value sets, codes, accessors), Elements (retrieves with status, intent and
  validity filters), Inferences (clinical classification, correlation, temporal scoping), and
  Measure (population criteria). Retrieves belong in the Elements layer.
- **Source:** `pages/pattern_layers.md`.
- **Pass if:** the four layers in order and the Elements layer for retrieves.
- **Skill:** `SKILL.md` Authoring guidance (Logic layers).

### PT-05. Terminology operators

- **Expected:** `~` for a direct-reference code, `in` for a value set, and `=` only for code
  elements with a required binding. `contains` has no terminology overload, so use FHIRCommon's
  `includesCode()`.
- **Source:** `pages/pattern_fhir.md` (Use of terminologies).
- **Pass if:** all three parts.
- **Skill:** `SKILL.md` Authoring guidance (Terminology).

## Models and libraries

### ML-01. Unqualified types

- **Expected:** base FHIR Procedure (`http://hl7.org/fhir/StructureDefinition/Procedure`), not the
  US Quality Core Procedure profile, with no warning. Type resolution falls back to labels, and
  `Procedure` is the FHIR type's label. The IG's Known Issues says artifact logic should always
  qualify: `[USQualityCore.Procedure: "Colonoscopy"]`.
- **Source:** `pages/knownissues.md` (Seemingly Ambiguous Type References Are Allowed); translator
  3.29.0.
- **Pass if:** base FHIR, and the qualified form.
- **Fail if:** it says the unqualified name is ambiguous and fails to translate, or that it picks
  the US Quality Core profile.
- **Skill:** `SKILL.md` Library header.

### ML-02. Shared library behaviour

- **Expected:** all four: Encounter Inpatient, Emergency Department Visit, Observation Services and
  Outpatient Surgery Service, plus its Location retrieve. They still return data, because a base
  template matches any Encounter. Data requirements and profile-based filtering name base
  Encounter, though, not the US Quality Core profile.
- **Source:** `libraries/CQMCommon.cql`; translator 3.29.0.
- **Pass if:** it identifies the unqualified retrieves and says data is still returned.
- **Skill:** `SKILL.md` The shared libraries don't always qualify.

### ML-03. Refactored libraries

- **Expected:** CQMCommon is being refactored into CQMConcepts, CQMElements and CQMInferences, along
  the logic layers. The Refactored Index maps QI-Core shared libraries and definitions to their US
  Quality Core versions and where content moved, and records which versions are in MADiE.
- **Source:** `pages/refactored_index.md`.
- **Pass if:** the three libraries and the Refactored Index.
- **Skill:** `SKILL.md` Authoring guidance (Logic layers), Refactoring QI-Core measures.

### ML-04. Prevalence

- **Expected:** FHIRCommon 2.0.0's `prevalenceInterval()` gives the wrong result for an inactive
  condition or allergy with no abatement date. The fix is planned for Using CQL With FHIR STU 3, so
  until then CQMConcepts 0.4.000 and later provide `prevalencePeriod()`.
- **Source:** `pages/knownissues.md` (Prevalence Interval Issue).
- **Pass if:** the inactive-without-abatement case and the interim CQMConcepts function.
- **Skill:** `SKILL.md` Known issues.

## Tasks

### TK-01. A measure fragment

Translate the saved library to ELM JSON, check the translator's messages, then grade the ELM with
[grade_elm.py](grade_elm.py) (`python grade_elm.py DiabetesStatinCheck.json`).
[reference/](reference/) has a passing answer and a flawed one (unqualified `Encounter`,
`isActive()`), each with its ELM. The flawed one translates without a warning.

- **Script checks** (each must pass):
  - The library is `DiabetesStatinCheck` and uses the USQualityCore and FHIR models.
  - Every retrieve names a US Quality Core or US Core profile, and no terminology retrieve lacks a
    code path.
  - `"Qualifying Encounters"` retrieves US Quality Core Encounter by Office Visit, filters on
    status, and uses the Measurement Period.
  - `"Encounters With Diabetes"` looks at encounter diagnoses and problem-list items, times
    problems with `prevalencePeriod()` or `relevantPeriod()`, and doesn't use `isActive()` or
    `active()`.
  - `"Has Statin Order"` retrieves US Quality Core MedicationRequest by Statin Therapy.
  - `"Diabetic Patients Without Statin Order"` expresses the missing order as absence, and no
    negation profile is used.
- **Read for:** status and intent filters on the statin orders, which the script doesn't check.
- **Fail if:** translation fails, or the script fails.
- **Skill:** `SKILL.md` Library header, Authoring guidance.
