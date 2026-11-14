# US Quality Core Skill Test Questions: Answer Key

Expected answers for [questions.md](questions.md). Don't give this file to an agent under test.

Facts come from US Quality Core 0.5.0, as rendered in the `usqualitycore` skill: the pages in
`resources/pages/`, the ModelInfo in `resources/modelinfo/`, and the element tables in the
knowledge base (`resources/profiles/0.5.0/`, built by `scripts/build-kb.sh`). Translator behaviour
was checked with the CQL-to-ELM translator 3.29.0, using the USQualityCore ModelInfo. Each answer
gives the expected facts, the source, what a passing answer must and must not say, and where the
skill covers it ("Skill").

## Conformance

### CF-01. How requirements are marked

- **Expected:** with the `uscdiplusquality` extension on each element (shown as "(USCDI+ Quality)"
  in the IG and as the `USCDI+Q` flag in the element tables), following QI-Core's approach.
  US Quality Core doesn't add Must Support flags beyond those inherited from US Core.
  Implementations SHALL support all flagged elements and all inherited US Core Must Support
  elements.
- **Source:** `pages/must-support.md`; `pages/general-requirements.md` (Summary of Conformance
  Requirements).
- **Pass if:** it names the USCDI+ Quality flag and says Must Support is inherited from US Core.
- **Fail if:** it says US Quality Core marks its requirements with Must Support.
- **Skill:** `SKILL.md` Conformance.

### CF-02. Is it in scope?

- **Expected:** No for Communication and Device. They are carried over from QI-Core 6.0.0 but have
  no USCDI+ Quality-flagged elements, so they are out of scope for conformance. Encounter has
  flagged elements and SHALL be supported.
- **Source:** `pages/uscdiquality.md` (Summary List of In-Scope and Out-of-Scope Profiles).
- **Pass if:** all three are right.
- **Skill:** `SKILL.md` Conformance (In-scope profiles).

### CF-03. Modifiers

- **Expected:** they SHALL be treated as Must Support even if not declared, and applications SHALL
  NOT process instances that include unknown modifier elements.
- **Source:** `pages/general-requirements.md` (Summary of Conformance Requirements).
- **Pass if:** both parts.
- **Skill:** `SKILL.md` Conformance (Modifiers).

## Negation

### NG-01. A medication not ordered

- **Expected:** US Quality Core Medication Not Requested
  (`http://fhir.org/guides/onc/us-quality-core/StructureDefinition/us-quality-core-medicationnotrequested`),
  a MedicationRequest with `doNotPerform` fixed to `true`, and a reason. It is the negation
  counterpart of the MedicationRequest profile.
- **Source:** `pages/negation.md`; `0.5.0/us-quality-core-medicationnotrequested`.
- **Pass if:** it names the profile and the fixed `doNotPerform`.
- **Fail if:** it uses MedicationAdministration Not Done or a positive MedicationRequest.
- **Skill:** `SKILL.md` Negation profiles.

### NG-02. Value set or code

- **Expected:** either code the procedure in `Procedure.code.coding`, or put the
  `us-quality-core-notDoneValueSet` extension (a canonical to the value set) on `Procedure.code`.
  Not both: invariant pnd-1 requires exactly one (`notDoneValueSet.exists() xor
  code.coding.exists()`).
- **Source:** `0.5.0/us-quality-core-procedurenotdone` (Invariants, Slices).
- **Pass if:** both options and the exclusive or.
- **Skill:** `SKILL.md` Negation profiles; knowledge base.

## CQL

### CQ-01. A failing comparison

- **Expected:** with only `using USQualityCore`, the FHIRHelpers implicit conversions aren't
  available. Translation fails with "Could not resolve call to operator Equal with signature
  (FHIR.AdministrativeGender,System.String)". Add `using FHIR version '4.0.1'`, and then qualify
  US Quality Core classes in retrieves.
- **Source:** translator 3.29.0.
- **Pass if:** it adds `using FHIR` as the fix. Comparing `Patient.gender.value` also translates,
  but only works around this one comparison, so it is PARTIAL on its own.
- **Fail if:** it blames the FHIRHelpers version or the missing `called` alias.
- **Skill:** `SKILL.md` CQL against US Quality Core.

### CQ-02. The wrong encounters

- **Expected:** with `using FHIR` declared, the unqualified `Encounter` resolves to the FHIR type
  whatever the order of the declarations, so the retrieve returns base FHIR Encounters (template
  `http://hl7.org/fhir/StructureDefinition/Encounter`) rather than US Quality Core Encounters.
  Write `[USQualityCore.Encounter: "Encounter Inpatient"]`.
- **Source:** translator 3.29.0.
- **Pass if:** it says the retrieve is base FHIR and gives the qualified form.
- **Skill:** `SKILL.md` CQL against US Quality Core.

## QDM

### QD-01. Encounter, Performed

- **Expected:** the US Quality Core Encounter profile, with `Encounter.status` constrained to
  arrived, triaged, in-progress, on-leave or finished. Most retrospective eCQMs constrain it to
  finished.
- **Source:** `pages/qdm-to-us-quality-core.md` (Encounter, Performed).
- **Pass if:** the profile and the status constraint, or at least finished for retrospective
  measures.
- **Skill:** `SKILL.md` From QDM.

## Tasks

### TK-01. A procedure not done

Grade the saved Procedure with [grade_procedure.py](grade_procedure.py)
(`python grade_procedure.py procedure.json`), then read it.

- **Script checks** (each must pass):
  - `meta.profile` claims US Quality Core Procedure Not Done, and `status` is `not-done`.
  - `statusReason` has SNOMED CT 183944003.
  - The `us-quality-core-recorded` extension on the Procedure has a valueDateTime on 2026-03-04.
  - `code` carries the `us-quality-core-notDoneValueSet` extension with the colonoscopy value set,
    and no coding (pnd-1).
  - `subject` is `Patient/example`, and there is no performed value.
- **Fail if:** the script fails.
- **Skill:** `SKILL.md` Negation profiles; knowledge base.
