# Test Case Content: Validation, Profiles and Resources

Baseline: MADiE `develop` as of 2026-11-14 (commits in SOURCES.md); US Quality Core 0.5.0. Untagged statements hold at these versions only.
Sources: FHIRSVC-51b9b37, MSVC-251a73d, MEASURE-18c8d4d, JMODELS-49ffdec, USQC-0.5.0, CQLIG-2.0.0, DQMCMS-757d7c6

What a test case bundle for a US Quality Core measure must contain for MADiE to validate and run it, and
what the usual measure libraries expect of the resources in it. The profiles themselves are in the US
Quality Core IG (the `usqualitycore` skill); this file covers where MADiE and the measure libraries add
to them.

## Models

MADiE's measure models are FHIR 4.0.1, QI-Core 4.1.1, QI-Core 6.0.0, US Core 6.1.0-derived, US Quality
Core 0.5.0 and QDM 5.6 [src: JMODELS-49ffdec src/…/models/common/ModelType.java:12-18]. This skill covers
**US Quality Core 0.5.0** ("US Quality Core v0.5.0" in MADiE), the model of current CMS FHIR measures. A
QI-Core 6.0.0 measure can be drafted as a US Quality Core one (see [measure-cql.md](measure-cql.md)).

## Validation

MADiE validates a test case when it's created, saved or imported; for a US Quality Core measure it does so
before saving, and the save waits for the result
[src: MSVC-251a73d src/…/services/TestCaseService.java:258-322]. The checks
[src: FHIRSVC-51b9b37 src/…/services/ResourceValidationService.java:38-150]:

| Check | Result |
| --- | --- |
| A resource has no id, or two resources share an id (even of different types) | Error |
| `meta.profile` missing, or not a valid URL | Warning: "Resources missing Meta.profile may cause incorrect results" |
| A `meta.profile` whose type isn't the resource's type | Error [src: FHIRSVC-51b9b37 src/…/services/ResourceValidationService.java:400-457] |
| A reference that doesn't resolve to a resource in the bundle, in a resource other than the Patient | Warning, and that resource is **left out when the test case runs** |
| The same, in the Patient | Error |
| FHIR profile validation (HAPI) against each declared profile | Errors and warnings as reported; an unknown code system is a warning |

For US Quality Core measures the HAPI validator loads US Quality Core 0.5.0, US Core 6.1.0 and the FHIR
extensions pack, and checks codes against MADiE's terminology services
[src: FHIRSVC-51b9b37 src/…/config/HapiFhirConfig.java:168-210]. A profile it doesn't have, such as a
QI-Core profile, isn't checked at all [src: FHIRSVC-51b9b37 src/…/services/ResourceValidationService.java:426-437].

A test case with any error is **invalid**. It can't be run unless the measure's test case
configuration allows running invalid test cases [src: MEASURE-18c8d4d src/…/qiCore/EditTestCase.tsx:195-205],
and it's left out of exports.

## Ids and references

- **Ids:** every resource needs one, unique across the bundle. They needn't be UUIDs, though MADiE
  makes UUIDs for resources it creates [src: MEASURE-18c8d4d src/…/api/fhirDefinitionServiceUtilities.tsx:830-845].
  Every resource except the Patient gets a new UUID on each export (see
  [test-case-files.md](test-case-files.md)).
- **The Patient's id** should be the test case's patient id (the folder UUID). For a US Quality Core
  measure MADiE doesn't set it on import or save, so set it yourself.
- **References:** use relative `Patient/<id>` and `<Type>/<id>`. References are resolved by type and id
  within the bundle, so a `urn:uuid:` or absolute reference never resolves, and the resource holding it
  is dropped from execution.
- **Find resources by key, not id, in test logic.** Because export gives every resource except the
  Patient a new id, and MADiE runs a case with a different Patient id (below), CQL that recognises a
  test resource by its id, or by a `'Location/x'` reference string, breaks after an export and
  re-import. Give each resource a readable key in an `identifier` (a system of your own, such as
  `http://example.org/fhir/identifiers`) and match on that; references between resources in the
  bundle are rewritten consistently, so following them is safe
  [src: DQMCMS-757d7c6 .claude/skills/cql/SKILL.md:129-148].
- **Order:** the Patient needn't be the first entry.
- **The Patient** needs a `name` with both `given` and `family` for import to work (see
  [test-case-files.md](test-case-files.md)), and `meta.profile` for profile validation. MADiE's new test
  cases declare `http://fhir.org/guides/onc/us-quality-core/StructureDefinition/us-quality-core-patient`
  [src: MEASURE-18c8d4d src/…/util/QiCoreTestCaseHelper.ts:5-20]. That profile also requires at least
  one `identifier` and a `gender` [src: USQC-0.5.0 package/StructureDefinition-us-quality-core-patient.json];
  without them the profile check fails and the test case is invalid. Any synthetic identifier works,
  such as `{"system": "https://madie.cms.gov/", "value": "SYN-0001"}`.

## How MADiE runs test cases

MADiE runs FHIR test cases **in the browser, with fqm-execution 1.8.6**
[src: MEASURE-18c8d4d package.json:117] [src: MEASURE-18c8d4d src/…/api/CalculationService.ts:206-230],
which uses cql-execution, the JavaScript CQL engine. The VS Code CQL extension and most servers use the
Java engine (see the `vscode-cql` skill). The two can disagree, so a library that passes its tests in
VS Code can still fail in MADiE:

- **The Patient's id changes.** Before a case runs, MADiE sets the Patient's `id` to the test case's
  internal id (a 24-character hex string), not the patient UUID, so that each case has a unique id
  [src: MEASURE-18c8d4d src/…/api/CalculationService.ts:158-170]. In MADiE, `Patient.id` and
  `'Patient/' + Patient.id` therefore don't match the `Patient/<uuid>` references in the bundle, while
  in VS Code they do. Don't compare references with the Patient's id in test logic; retrieves still
  return the resources in the case's bundle.
- **Engine differences seen in practice** (observed in `dqm-content-cms-2026` test libraries, not
  traced to the engine's code) [src: DQMCMS-757d7c6 .claude/skills/cql/SKILL.md:136-141]:
  - Overloads of one function name on `FHIR.Resource` and `FHIR.Reference` resolved to the wrong
    overload at run time. Give such functions distinct names.
  - A function over `FHIR.Resource` that branches with `is` / `as` didn't evaluate. Write one function
    per resource type instead.

Check test results in MADiE itself before relying on them; a local run is a first check only.

## Profiles

Profile URLs are `http://fhir.org/guides/onc/us-quality-core/StructureDefinition/<id>`, and the ids are
`us-quality-core-<resource>`, with these splits [src: USQC-0.5.0 package/StructureDefinition-us-quality-core-*.json]:

| Resource | Profiles |
| --- | --- |
| Condition | `us-quality-core-condition-problems-health-concerns` (problem list, health concerns) or `us-quality-core-condition-encounter-diagnosis` |
| Observation | `us-quality-core-observation-clinical-result`, `-observation-lab`, `-observation-screening-assessment`, `-simple-observation`, `-nonpatient-observation`, plus the US Core profiles for vital signs, smoking status and the like |
| Not-done events | `us-quality-core-observationcancelled`, `-procedurenotdone`, `-medicationnotrequested`, `-medicationadministrationnotdone`, `-medicationdispensedeclined`, `-servicenotrequested`, `-devicenotrequested`, `-immunizationnotdone`, `-communicationnotdone`, `-taskrejected` |
| Patient, Encounter, Procedure, ServiceRequest, DeviceRequest, MedicationRequest, CareTeam, Location, Claim, Coverage… | `us-quality-core-<resource>` |

## Resource notes

Whether a resource counts is decided by the measure's CQL, not the profile, so read the measure's logic
for the statuses and values it tests. The CMS libraries' conventions are in the `cms-qmd` skill. What
the profiles and FHIRCommon 2.0.0 (included by MADiE's default US Quality Core CQL) set:

- **Observation value and status.** In Simple Observation, `value[x]` is optional and must-support,
  `category` is required, and `status` is bound to the profile's non-negative observation statuses
  [src: USQC-0.5.0 package/StructureDefinition-us-quality-core-simple-observation.json]. It's the general
  Observation profile for observations with no more specific one, not a "no value" profile. Measures
  commonly count `final`, `amended` and `corrected` results with a value.
- **`dataAbsentReason`** may be given instead of a value, never with one (FHIR invariant obs-6). A measure
  that tests `value is not null` won't count such an Observation; FHIR doesn't require
  `dataAbsentReason` when a value is missing.
- **Condition status.** `verificationStatus` and `clinicalStatus` are both optional
  [src: USQC-0.5.0 package/StructureDefinition-us-quality-core-condition-problems-health-concerns.json].
  FHIRCommon's `verified()` keeps conditions with **no** verification status, or confirmed, unconfirmed,
  provisional or differential, and drops refuted and entered-in-error; its `isActive()` needs a clinical
  status of active, recurrence or relapse [src: CQLIG-2.0.0 package/Library-FHIRCommon.json]. So set
  `clinicalStatus` when the measure tests for active conditions; `confirmed` isn't required.
- **Encounter.** `status`, `class` and at least one `type` are required. `class` is a Coding from
  `http://terminology.hl7.org/CodeSystem/v3-ActCode`, such as `IMP` (inpatient), `AMB` (ambulatory),
  `EMER` (emergency) or `HH` (home health); the measure's value sets usually test `type`
  [src: USQC-0.5.0 package/StructureDefinition-us-quality-core-encounter.json]. Measures count a performed
  encounter by `status` `finished`.
- **DeviceRequest.** The device is `code[x]`, either `codeCodeableConcept` or `codeReference`; there's
  no plain `code` property in JSON [src: USQC-0.5.0 package/StructureDefinition-us-quality-core-devicerequest.json].
- **The measurement period.** Date the test data against the measurement period set on the measure in
  MADiE, not the CQL parameter's default; the exported MeasureReport's `period` is that period
  [src: FHIRSVC-51b9b37 src/…/services/TestCaseBundleService.java:176-179].
