---
name: usqualitycore
description: Looks up and applies US Quality Core 0.5.0 (fhir.onc.us-quality-core), the ONC profiles for USCDI+ Quality built on US Core 6.1.0 and derived from QI-Core 6.0.0. Covers USCDI+ Quality flags, in-scope profiles and conformance, negation profiles, the QDM-to-US Quality Core mapping, the USQualityCore ModelInfo and USQualityCoreCommon. Use when building or checking data against US Quality Core, choosing a US Quality Core profile, or writing CQL with `using USQualityCore`. For CMS measure authoring patterns, use the cms-qmd skill.
license: Apache-2.0
---

# US Quality Core

US Quality Core (`fhir.onc.us-quality-core` 0.5.0, ONC) profiles the data needed for quality
measurement and reporting, as defined by USCDI+ Quality V1. Its profiles derive from US Core 6.1.0
where possible, and it carries forward the whole QI-Core 6.0.0 profile set. 0.5.0 is the only
release.

Related skills: `uscore` for US Core itself, `us-cql-ig` for the USCore model and libraries it
builds on, `cms-qmd` for CMS measure authoring patterns, and `cql-ig` for FHIRHelpers and
FHIRCommon.

## Reference

| Path | Contents |
| --- | --- |
| [resources/pages/README.md](resources/pages/README.md) | The IG's pages: conformance, Must Support, USCDI+ Quality, negation, relationship with US Core and QI-Core, the QDM 5.6 mapping, ModelInfo and patterns |
| [resources/modelinfo/README.md](resources/modelinfo/README.md) | The USQualityCore ModelInfo 0.5.0: every class, its label, base, primary code path and elements |
| [resources/libraries/README.md](resources/libraries/README.md) | USQualityCoreCommon and its tests, as published CQL |
| `resources/profiles/0.5.0/` | One element table per profile and extension. Build with `bash scripts/build-kb.sh`. |

`scripts/build-ig.py` regenerates the pages, ModelInfo and libraries from the pinned package and
the IG source (FHIR/us-quality-core at the 0.5.0 release, CC0). The element tables are built
locally and not committed. Their format is in
[resources/format-guide.md](resources/format-guide.md) (Other output styles).

## Conformance

These are from `pages/general-requirements.md` and `pages/must-support.md`.

- **USCDI+ Quality flags.** US Quality Core marks required elements with the `uscdiplusquality`
  extension rather than adding Must Support flags. The element tables show it as the `USCDI+Q`
  flag. Implementations SHALL support every flagged element and every Must Support element
  inherited from US Core.
- **In-scope profiles.** Implementations SHALL support every profile with at least one flagged
  element. Profiles carried over from QI-Core with no flagged element are out of scope for
  conformance: BodyStructure, Claim, ClaimResponse, Communication, Communication Not Done,
  CommunicationRequest, Device, DeviceUseStatement, Flag, ImagingStudy, ImmunizationEvaluation,
  ImmunizationRecommendation, MedicationStatement, NonPatient Observation, NutritionOrder,
  QuestionnaireResponse and Substance. The full lists are in `pages/uscdiquality.md` (Summary
  List of In-Scope Profiles).
- **Modifiers.** Modifier elements SHALL be treated as Must Support, and applications SHALL NOT
  process instances with unknown modifier elements.
- **US Core too.** Applications SHALL conform to the US Quality Core profiles and the US Core
  profiles at once. Where US Quality Core binds more tightly, its binding applies.
- **"Any" references** SHALL point to resources conforming to a US Quality Core profile when the
  base resource has one.
- **Servers** SHALL support the US Quality Core Server CapabilityStatement's SHALL interactions
  and searches, and declare the profiles they support.

## Negation profiles

To record that something did not happen, US Quality Core has ten negation profiles, each paired
with a positive one (`pages/negation.md`):

| Positive | Negation |
| --- | --- |
| Communication | Communication Not Done (out of scope for conformance) |
| DeviceRequest | Device Not Requested |
| Immunization | Immunization Not Done |
| MedicationAdministration | MedicationAdministration Not Done |
| MedicationDispense | MedicationDispense Declined |
| MedicationRequest | Medication Not Requested |
| Simple Observation | Observation Cancelled (also for the vital-signs and other observation profiles) |
| Procedure | Procedure Not Done |
| ServiceRequest | Service Not Requested |
| Task | Task Rejected |

Each says what didn't happen (usually a value set), states explicitly that it didn't happen (for
example `doNotPerform` or a status of `not-done`), and records when a clinician gave the reason.
Use one only when the reason matters. When it doesn't, absence of the positive record is enough.

## CQL against US Quality Core

The ModelInfo, libraries and patterns are informational in 0.5.0: they support tooling but add no
conformance requirements.

```cql
library ExampleQualityLogic version '1.0.0'

using USQualityCore version '0.5.0'
using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers
include hl7.fhir.uv.cql.FHIRCommon version '2.0.0' called FC
include USQualityCoreCommon version '0.5.0' called UQCC

valueset "Encounter Inpatient": 'http://cts.nlm.nih.gov/fhir/ValueSet/2.16.840.1.113883.3.666.5.307'

context Patient

define "Finished Inpatient Encounters":
  [USQualityCore.Encounter: "Encounter Inpatient"] E
    where E.status = 'finished'
```

- **The model derives from USCore 6.1.0-derived and FHIR 4.0.1,** so FHIR types, FHIRHelpers,
  FHIRCommon and the US CQL IG's USCoreCommon apply to US Quality Core data.
- **Declare `using FHIR version '4.0.1'` as well.** With only `using USQualityCore`, the
  FHIRHelpers conversions don't apply. `Patient.gender = 'female'` fails ("Could not resolve call
  to operator Equal with signature (FHIR.AdministrativeGender,System.String)"), and every
  terminology retrieve warns "Could not resolve membership operator". The same holds for
  `using USCore` on its own.
- **Then qualify every class.** Class names are mostly FHIR type names (`Patient`, `Encounter`,
  `Procedure`), plus the negation profiles (`ProcedureNotDone`, `MedicationNotRequested`). Once
  `using FHIR` is declared, an unqualified `[Encounter]` silently retrieves base FHIR Encounter,
  whatever the order of the declarations. Write `[USQualityCore.Encounter]`. The CMS QMD shared
  libraries declare all three models but leave some retrieves unqualified; see the `cms-qmd`
  skill.
- **Primary code paths** are defined for nearly every retrievable class. Patient, Practitioner and
  QuestionnaireResponse have none. NutritionOrder (`code`) and ImmunizationRecommendation
  (`vaccineCode`) declare paths that aren't top-level elements of those classes. The CMS QMD Known
  Issues page says to filter those two in a `where` clause instead. Check the ModelInfo README
  before writing a terminology retrieve.
- **USQualityCoreCommon** has the encounter class codes and other common terminology, and the
  functions QICoreCommon used to provide that haven't moved to FHIRCommon or USCoreCommon. Read
  [USQualityCoreCommon.cql](resources/libraries/USQualityCoreCommon.cql) before relying on a
  function.

## From QDM

`pages/qdm-to-us-quality-core.md` maps each QDM 5.6 datatype and attribute to its US Quality Core
profile and element. It is the place to start when converting a QDM-based eCQM. It is QI-Core
6.0.0's mapping, updated to name the US Quality Core profiles.
