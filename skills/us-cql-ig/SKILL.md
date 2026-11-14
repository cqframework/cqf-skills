---
name: us-cql-ig
description: Writes CQL against US Core using the Common CQL Artifacts for FHIR (US-Based) IG (hl7.fhir.us.cql 2.0.0), which publishes the USCore ModelInfo (6.1.0-derived) and the USCoreCommon, USCoreElements, QICoreCommon and CumulativeMedicationDuration libraries. Covers retrieving US Core profiles, primary code paths, modifier and status handling, and the patient, condition, observation, medication and service patterns. Use when CQL uses USCore, includes USCoreCommon or USCoreElements, or asks how to express US Core data in CQL.
license: Apache-2.0
---

# Common CQL Artifacts for FHIR (US-Based)

The Common CQL Artifacts for FHIR (US-Based) IG (`hl7.fhir.us.cql`, also called the US CQL IG)
gives the CQL model and shared libraries for writing CQL against US Core. It covers version 2.0.0,
which builds on US Core 6.1.0, Using CQL With FHIR 2.0.0 and CRMI 2.0.0.

Related skills: `cql` for the language, `cql-ig` for FHIRHelpers, FHIRCommon and packaging CQL in
FHIR Libraries, and `uscore` for the US Core profiles themselves.

## Reference

| Path | Contents |
| --- | --- |
| [resources/pages/README.md](resources/pages/README.md) | The IG's pages: architectural guidance, usage, the per-resource patterns, query management and testing |
| [resources/libraries/README.md](resources/libraries/README.md) | USCoreCommon, USCoreElements, CumulativeMedicationDuration, QICoreCommon, C4BBCommon and their tests, as published CQL |
| [resources/modelinfo/README.md](resources/modelinfo/README.md) | The USCore ModelInfo 6.1.0-derived: every class, its label, base, primary code path and elements |

`scripts/build-ig.py` regenerates these files from the pinned package and IG source (CC0).

## Library header

```cql
library ExampleUSCoreLogic version '1.0.0'

using USCore version '6.1.0-derived'
using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers
include hl7.fhir.uv.cql.FHIRCommon version '2.0.0' called FC
include USCoreCommon version '2.0.0' called UC
include USCoreElements version '2.0.0' called UCE

context Patient
```

- **The model is `6.1.0-derived`.** Each USCore class extends the FHIR ModelInfo class for its base
  resource (`USCore.PatientProfile` extends `FHIR.Patient`). FHIR types, the FHIRHelpers
  conversions and the FHIRCommon functions all apply to USCore data. The `-derived` suffix
  distinguishes this model from a non-derived USCore model.
- **Includes.** The IG's own libraries include FHIRHelpers and FHIRCommon by namespace
  (`hl7.fhir.uv.cql.`) and without a `called` alias. Using CQL With FHIR requires `called` on every
  include (2.3), so add it in your own libraries.
- **US Core 9.0.0** publishes a different model, `USCore` version 9.0.0 (canonical
  `http://hl7.org/fhir/Library/USCore-ModelInfo`). It requires only the System model, not the FHIR
  ModelInfo. This IG's libraries are written for `6.1.0-derived` and don't target it.

## Retrieving US Core data

- **By class or label.** Retrieve a profile by its class name or its quoted label:
  `[USCore.PractitionerProfile]`, `["Observation Clinical Result Profile"]`,
  `[USCore."AllergyIntolerance"]`. Class names and labels differ, so look them up in
  [modelinfo/README.md](resources/modelinfo/README.md). For example, the Patient class is
  `PatientProfile`, while the CareTeam class is just `CareTeam`.
- **Qualify names that FHIR also has.** Four USCore classes share a name with a FHIR type:
  `AllergyIntolerance`, `CareTeam`, `Location` and `Provenance`. An unqualified `[CareTeam]`
  resolves to `FHIR.CareTeam` whatever the order of the `using` declarations, with no warning, so
  it retrieves base CareTeam rather than the US Core profile. Write `[USCore.CareTeam]` or the
  label `["CareTeam Profile"]`. This is why the IG writes `[USCore."AllergyIntolerance"]`.
- **Primary code paths.** Many USCore classes declare no primary code path, even though the IG's
  US Core ModelInfo page lists one. These include all the vital-signs profiles (Blood Pressure,
  BMI, Body Height, Body Weight, Body Temperature, Heart Rate, Respiratory Rate, Pulse Oximetry,
  Head Circumference and the pediatric profiles), Smoking Status, Pregnancy Status, Pregnancy
  Intent, Sexual Orientation and CarePlan. For these, `[BloodPressureProfile: "Value Set"]` only
  warns ("does not have a primary code path defined"), and the ELM retrieve has no code path.
  Name the path explicitly, as in `[BloodPressureProfile: code in "Value Set"]`, or retrieve
  without terminology. The profile already fixes the code for most of these classes. Check the
  ModelInfo README's Primary code path column before writing any terminology retrieve.
- **Status and modifiers.** Modifier elements such as `clinicalStatus` and `verificationStatus`
  must always be considered. Use the FHIRCommon fluent functions:
  `([USCore."AllergyIntolerance"]).active().confirmed()`. A retrieve needs parentheses before a
  method call, or it is a syntax error; the IG calls them on a definition instead
  (`"All Allergies and Intolerances".active().confirmed()`).
- **USCoreElements** is the data layer. It defines "All ..." and filtered lists by resource type
  and profile (`"All Problem List Items"`, `"Active Confirmed Problem List Items"`,
  `"All Laboratory Results"`, `"Resulted Laboratory Results"`, `"Most Recent Smoking Status"`),
  plus patient functions such as `ageInYears()`, `officialName()` and `medicalRecordNumber()`.
  Reuse these definitions rather than redefining them, after reading how each one selects. For
  example, the Condition lists retrieve `[FHIR."Condition"]` and filter by category
  (`isProblemListItem()`, `isEncounterDiagnosis()`), rather than retrieving a Condition profile.

## USCoreCommon functions

[USCoreCommon.cql](resources/libraries/USCoreCommon.cql) provides US Core-specific fluent
functions. Read each definition before relying on it.

- **Patient:** `race()` and `ethnicity()` return tuples of `ombCategory`, `detailed` and `text`.
  The patient model has no race or ethnicity element, so use these functions or filter
  `extension`. `tribalAffiliation()` and `birthSex()` are also available.
- **Sex:** `individualSex()` reads the `us-core-individual-sex` extension (US Core 8.0 and later),
  and falls back to the 6.1.0 `us-core-sex` extension through `toIndividualSex()`. Prefer it over
  `sex()`, which is deprecated. `sexParameterForClinicalUse()` reads the HL7 extension of that
  name.
- **Observations:** `systolic()` and `diastolic()` for blood pressure, `positive()`, `negative()`,
  `during(encounter)`, `chronologically()` and `chronologicallyAfter()`.
- **Conditions and allergies:** `isHealthConcern()` and `assertedDate()`.

## Patterns

The per-resource pattern pages (`pages/patterns-*.md`) cover modifier elements, search parameters,
cross-version considerations and common functions for Patient, AllergyIntolerance, Condition,
Observation, medications, services, Coverage and Claim. Points that come up most often:

- **Cardinality, Must Support and modifiers** (`patterns-overall.md`): cardinality decides whether
  data can be present at all, Must Support whether it can reasonably be expected, and modifiers
  must always be evaluated for every possible value.
- **Naming** (`patterns-overall.md`):
  - Name the resource type unless there can be no confusion, for example
    `"Metformin AllergyIntolerances"`.
  - Use a plural for lists and a singular for a derived singleton.
  - Put units in the names of quantities, as in `"Patient Age in Days"`.
  - Say how a list was filtered, as in `"Active Confirmed Conditions"`.
  - Use `"All ..."` for an unfiltered list.
  - Start non-fluent function names with a verb, such as `Get` or `Compute`.
- **Architecture** (`architectural-guidance.md`): terminology considerations (value set
  expansion and membership against servers) and performant data access (keep retrieves selective,
  and use optional search parameters with care).
- **Medications:** CumulativeMedicationDuration computes medication periods from
  MedicationRequest, MedicationDispense and MedicationAdministration, and a cumulative duration
  across requests and dispenses (`cumulativeMedicationDuration()`).
- **Versions and dependencies** (`usage.md`): pin dependency versions with a CRMI manifest Library;
  `Library-PriorAuthManifestExample` is the IG's example.

## QI-Core and CARIN Blue Button

The package also publishes QICore ModelInfo 6.0.0-derived with QICoreCommon, and C4BB ModelInfo
2.2.0-derived with C4BBCommon (see `pages/qicore-modelinfo.md` and `pages/c4bb-modelinfo.md`).
This skill condenses only the USCore model.
