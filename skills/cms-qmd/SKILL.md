---
name: cms-qmd
description: Applies the CMS FHIR Quality Measure Development IG (cms.fhir.qmd, continuous build), the guidance for CMS digital quality measures written in CQL against US Quality Core 0.5.0. Covers the CQL style guide, logic layers, the Pattern Index and per-resource patterns (encounters, conditions, observations, medications, procedures, claims, coverage, billing), negation patterns, known issues, and the CQMCommon, CQMConcepts, CQMElements, ClaimCommon and MedicationCommon libraries. Use when authoring or reviewing CQL for a CMS eCQM or dQM, refactoring a QI-Core measure to US Quality Core, or using those libraries.
license: Apache-2.0
---

# CMS FHIR Quality Measure Development

The CMS FHIR Quality Measure Development IG (CMS QMD, `cms.fhir.qmd`) gives the authoring
guidance, patterns and shared libraries for CMS digital quality measures written in CQL against
US Quality Core 0.5.0, US Core 6.1.0 and the US CQL IG 2.0.0. It hasn't been released to the FHIR
package registry. This skill pins its continuous build (0.8.0-cibuild, 3 November 2026).

Related skills:

- `usqualitycore`: the profiles and the USQualityCore model
- `us-cql-ig`: USCoreCommon and USCoreElements
- `cql-ig`: FHIRHelpers and FHIRCommon
- `cql`: the language itself
- `crmi`: packaging artifacts

## Reference

| Path | Contents |
| --- | --- |
| [resources/pages/README.md](resources/pages/README.md) | Every page of the IG: measure guidance, patterns, Pattern Index, per-resource patterns, negation, known issues, the US Quality Core update process, the Refactored Index, MADiE and measure profiles |
| [resources/libraries/README.md](resources/libraries/README.md) | CQMCommon, CQMConcepts, CQMElements, CQMInferences, ClaimCommon, ClaimElements, MedicationCommon and FHIRBuilders, with versions, models and includes |

`scripts/build-ig.py` regenerates these files from cqframework/cms-qmd at the pinned commit. The
IG declares its content CC0, and the repository is Apache-2.0.

Start with [pages/pattern_index.md](resources/pages/pattern_index.md). It lists every data element
and pattern once, across this IG and the US CQL IG, with links.

## Library header

```cql
library ExampleMeasure version '1.0.000'

using USQualityCore version '0.5.0'
using USCore version '6.1.0-derived'
using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers
include hl7.fhir.uv.cql.FHIRCommon version '2.0.0' called FHIRCommon
include hl7.fhir.us.cql.USCoreCommon version '2.0.0' called USCoreCommon
include CQMConcepts version '0.5.000' called CQMConcepts
include CQMElements version '0.5.000' called CQMElements
```

- **Declare all three models, with versions.** For quality measures, the model declaration SHALL
  include a version. `using FHIR` is also needed for the FHIRHelpers conversions to apply.
- **Always qualify types.** Write `[USQualityCore.Encounter]`, `[USCore.BloodPressureProfile]` and
  `FHIR.Procedure`. With all three models declared, an unqualified `Encounter` or `Procedure`
  resolves to the FHIR base resource, because type resolution falls back to the label and the
  FHIR label is the only exact match. Known Issues ("Seemingly Ambiguous Type References Are
  Allowed") says artifact logic should *always* qualify. The translator confirms that unqualified
  retrieves produce base FHIR templates with no warning.

## The shared libraries don't always qualify

Translating the pinned libraries with the CQL-to-ELM translator 3.29.0 shows unqualified retrieves
that resolve to base FHIR rather than US Quality Core:

- **CQMCommon 5.2.000:** the Encounter Inpatient, Emergency Department Visit, Observation Services
  and Outpatient Surgery Service retrieves, and its Location retrieve, use
  `http://hl7.org/fhir/StructureDefinition/Encounter` and `.../Location`.
- **CQMConcepts 0.5.000:** the five `TESTING SUPPORT:` encounter definitions do the same.
- **CQMElements 0.5.000:** `emergencyDepartmentArrivalTime()` and `firstInpatientIntensiveCareUnit()`
  retrieve base FHIR Location. Its other retrieves are qualified.

These still return the data, because base templates match any resource of the type. But data
requirements and profile-based filtering will name the base resource rather than the US Quality
Core profile. Qualify retrieves in new logic, and expect this when reviewing measures built on
these libraries.

## Authoring guidance

- **Style** (`measure_guidance.md`, CQL Style Guide):
  - Library-level identifiers are descriptive, unabbreviated and in initial case.
  - Data type names are PascalCase and unquoted.
  - Element names are camelCase.
  - Aliases are PascalCase and differ from every other identifier in scope.
  - Argument names are camelCase.
- **Logic layers** (`pattern_layers.md`): Concepts (value sets, codes and accessors) ← Elements
  (retrieves with status, intent and validity filters) ← Inferences (clinical classification and
  timing) ← Measure (population criteria). Keep every retrieve in the Elements layer, and keep
  thresholds and populations out of it. CQMConcepts, CQMElements and CQMInferences follow these
  layers. They are replacing CQMCommon (`refactored_index.md`).
- **Terminology** (`pattern_fhir.md`):
  - Use `~` for a direct-reference code, `in` for a value set, and `=` only for code elements with
    a required binding.
  - Don't use `contains` with terminology; use FHIRCommon's `includesCode()`.
  - Don't test membership by string.
  - A direct-reference code's identifier is never a URI.
- **Retrospective status** (`pattern_conditions.md`, `pattern_allergies.md`): measures look back
  at a measurement period, so don't use `isActive()`, which tests *current* clinical status, to
  decide that a condition was active then. Use CQMConcepts' `prevalencePeriod()` (onset only) or
  `relevantPeriod()` (onset, else asserted or recorded date), rather than FHIRCommon's
  `prevalenceInterval()` (see Known issues).
- **Negation** (`pattern_negation.md`): use absence of evidence (`not exists` over the positive
  profile) unless the measure needs a documented reason. Only then use a US Quality Core negation
  profile.
- **Diagnosis during an encounter** (`pattern_encounters.md`): look in up to three places: the
  ConditionEncounterDiagnosis linked to the encounter, a ConditionProblemsHealthConcerns item whose
  `prevalencePeriod()` overlaps the encounter, and `Encounter.reasonCode`. Measure intent decides
  which to combine.
- **Hospitalization** (`pattern_encounters.md`): CQMElements defines hospitalization, ED,
  observation and ICU logic (`"Hospitalization Encounters"`, `hospitalization()`,
  `hospitalizationLengthOfStay()`, `observationVisit()`). Use it rather than redefining it.
- **Claims, coverage and billing** (`pattern_claim.md`, `pattern_coverage.md`,
  `pattern_billingrelated.md`): use ClaimCommon and ClaimElements for claim diagnoses,
  procedures and encounter items.

## Known issues

`knownissues.md` lists problems that affect how measures are written:

- **Primary code paths.** CarePlan in US Core, and NutritionOrder and ImmunizationRecommendation
  in US Quality Core, have missing or wrong primary code paths. Filter those in a `where` clause.
  The vital-signs profiles deliberately have none, because the profile fixes the code.
- **Fluent functions on choice types** can't always be resolved.
- **Fluent function overloads** need care.
- **Type references** that look ambiguous are allowed, as described above.
- **FHIRCommon 2.0.0's `prevalenceInterval()`** mishandles an inactive condition or allergy with
  no abatement date. Use CQMConcepts' `prevalencePeriod()` (0.4.000 or later) until Using CQL With
  FHIR STU 3 fixes it.

Check it before working around a translator or engine problem.

## Refactoring QI-Core measures

`usqc_update_process.md` describes moving QI-Core 6.0.0 measures to US Quality Core 0.5.0.
`refactored_index.md` maps each QI-Core shared library, and where its definitions now live, to its
US Quality Core version. It also records which versions are published in MADiE. `MADiE.md` covers
authoring in MADiE.
