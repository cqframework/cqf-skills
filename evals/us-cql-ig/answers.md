# US CQL IG Skill Test Questions: Answer Key

Expected answers for [questions.md](questions.md). Don't give this file to an agent under test.

Facts come from `hl7.fhir.us.cql` 2.0.0, as rendered in the `us-cql-ig` skill: the pages in
`resources/pages/`, the libraries in `resources/libraries/`, and the USCore ModelInfo in
`resources/modelinfo/`. Translator behaviour was checked with the CQL-to-ELM translator 3.29.0,
using the USCore ModelInfo. Each answer gives the expected facts, the source, what a passing
answer must and must not say, and where the skill covers it ("Skill").

## Model

### MD-01. The using declaration

- **Expected:** `using USCore version '6.1.0-derived'`, usually with `using FHIR version '4.0.1'`.
  The model requires the FHIR 4.0.1 model, and each USCore class extends the FHIR class for its base
  resource (`USCore.PatientProfile` extends `FHIR.Patient`). So FHIR types, the FHIRHelpers
  implicit conversions and FHIRCommon functions apply to USCore data. The suffix distinguishes it
  from a non-derived USCore model.
- **Source:** `modelinfo/README.md`; `pages/usage.md` (USCore ModelInfo).
- **Pass if:** the declaration is exact and it explains that the classes derive from FHIR classes.
- **Fail if:** it gives `using USCore version '6.1.0'` or `'3.1.1'`.
- **Skill:** `SKILL.md` Library header.

### MD-02. Blood pressure by value set

- **Expected:** `BloodPressureProfile` has no primary code path in the ModelInfo, although the IG's
  US Core ModelInfo page lists `code`. The translator only warns ("Retrieve has a terminology
  target but does not specify a code path and the type of the retrieve does not have a primary
  code path defined"), and the ELM retrieve has no `codeProperty`. Write
  `[BloodPressureProfile: code in "Blood Pressure Codes"]`, or drop the terminology, since the
  profile already fixes the code.
- **Source:** `modelinfo/README.md` (Primary code path column); translator 3.29.0.
- **Pass if:** it says there is no primary code path, and gives an explicit `code in` path or a
  retrieve without terminology.
- **Fail if:** it says the retrieve filters on `code` by default.
- **Skill:** `SKILL.md` Retrieving US Core data (Primary code paths).

### MD-03. Class names

- **Expected:** Patient: `[PatientProfile]`, `[USCore.PatientProfile]` or the label
  `["Patient Profile"]`. CareTeam: `[USCore.CareTeam]` or the label `["CareTeam Profile"]`. The
  class is named `CareTeam`, the same as the FHIR type, and an unqualified `[CareTeam]` resolves
  to `FHIR.CareTeam` (template `http://hl7.org/fhir/StructureDefinition/CareTeam`) whatever the
  `using` order, with no warning.
- **Source:** `modelinfo/README.md`; translator 3.29.0.
- **Pass if:** both are right, and CareTeam is qualified or retrieved by label.
- **Fail if:** it writes `[CareTeamProfile]` (no such class: "Could not resolve type name"), or an
  unqualified `[CareTeam]`.
- **Skill:** `SKILL.md` Retrieving US Core data (By class or label, Qualify names that FHIR also
  has).

### MD-04. US Core 9.0.0

- **Expected:** No. US Core 9.0.0 publishes `USCore` version 9.0.0
  (`http://hl7.org/fhir/Library/USCore-ModelInfo`), which requires only the System model and
  isn't derived from the FHIR ModelInfo. This IG's libraries declare
  `using USCore version '6.1.0-derived'` and rely on the FHIR-derived classes.
- **Source:** `SKILL.md`; the US Core 9.0.0 package's `Library-USCore-ModelInfo` example.
- **Pass if:** it says no and gives the version or derivation difference.
- **Skill:** `SKILL.md` Library header.

## Libraries

### LB-01. Patient sex

- **Expected:** `individualSex()`. It returns the `us-core-individual-sex` extension's Coding, and
  if that is absent, maps the deprecated 6.1.0 `us-core-sex` code with `toIndividualSex()`. `sex()`
  is deprecated.
- **Source:** `libraries/USCoreCommon.cql`; `pages/patterns-patient.md` (Patient sex).
- **Pass if:** it names `individualSex()` and describes the fallback.
- **Fail if:** it recommends `sex()` or `birthSex()` for sex.
- **Skill:** `SKILL.md` USCoreCommon functions.

### LB-02. Race

- **Expected:** `Patient.race().ombCategory`, using USCoreCommon's fluent `race()`. It reads the
  `us-core-race` extension and returns a tuple of `ombCategory` and `detailed` Codings and `text`.
  `Patient.race` fails because the USCore Patient class has no race element: extensions aren't
  exposed as elements in this model.
- **Source:** `libraries/USCoreCommon.cql`; `modelinfo/classes/PatientProfile.md`.
- **Pass if:** it uses `race()` (or filters `extension` by URL) and explains why there's no element.
- **Skill:** `SKILL.md` USCoreCommon functions.

### LB-03. Problem list items

- **Expected:** It retrieves `[FHIR."Condition"]` (all Conditions, not a US Core profile),
  keeps those where `isProblemListItem()` (category `problem-list-item`), then applies FHIRCommon's
  `active()` (clinical status active, recurrence or relapse) and `confirmed()` (verification
  status confirmed).
- **Source:** `libraries/USCoreElements.cql`; `cql-ig` FHIRCommon.
- **Pass if:** it describes the category filter and both status filters.
- **Fail if:** it says the definition retrieves the Problems and Health Concerns profile.
- **Skill:** `SKILL.md` Retrieving US Core data (USCoreElements).

## Patterns

### PT-01. Naming

- **Expected:** `"Conditions"`: an unfiltered list should say "All", as in `"All Conditions"`.
  `"BP"`: a singleton should say how it was obtained and what it is, with no abbreviation, as in
  `"Most Recent Systolic Blood Pressure Quantity"`. `"Age"`: a primitive quantity needs its unit,
  as in `"Patient Age in Years"`. `HeightCalc`: a non-fluent function should start with a verb, as
  in `CalculateHeight` or `GetHeight`.
- **Source:** `pages/patterns-overall.md` (Naming Best-Practices).
- **Pass if:** at least three of the four are fixed for the stated reason.
- **Skill:** `SKILL.md` Patterns (Naming).

### PT-02. A syntax error

- **Expected:** A retrieve can't be followed directly by a method-style call, so the translator
  reports a syntax error at the `.`. Wrap it in parentheses,
  `([USCore."AllergyIntolerance"]).active()`, or define the retrieve and call the function on the
  definition, as the IG does: `"All Allergies and Intolerances".active()`.
- **Source:** translator 3.29.0; `pages/patterns-overall.md` (Accessing Data).
- **Pass if:** both forms are given.
- **Skill:** `SKILL.md` Retrieving US Core data (Status and modifiers).

## Tasks

### TK-01. A US Core library

Translate the saved library to ELM JSON (see [README.md](README.md)), check the translator's
messages, then grade the ELM with [grade_elm.py](grade_elm.py):
`python grade_elm.py HypertensionCheck.json`. [reference/](reference/) has a passing answer and a
flawed one, each with its ELM.

- **Script checks** (each must pass):
  - The library is `HypertensionCheck` version 1.0.0, uses USCore, and includes FHIRHelpers 4.0.1.
  - Every retrieve is of a US Core profile, and no terminology retrieve lacks a code path.
  - `"Active Confirmed Hypertension Problems"` retrieves the Problems and Health Concerns profile by
    `code` in the value set, and filters on clinical status and verification status.
  - `"Final Blood Pressure Readings"` retrieves the Blood Pressure profile and filters on status.
  - `"Most Recent Systolic Blood Pressure Quantity"` is based on blood pressure readings, takes the
    systolic component and picks the most recent reading.
  - `"Patient Race Categories"` reads the race extension and returns its OMB categories.
- **Fail if:** translation fails, or the script fails. A warning about a missing code path is a
  failure here even though translation succeeds.
- **Skill:** `SKILL.md` Library header, Retrieving US Core data, USCoreCommon functions.
