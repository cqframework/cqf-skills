# Test Case Content: Validation, Profiles and Resources

Baseline: MADiE `develop` as of 2026-11-14 (commits in SOURCES.md); QI-Core 4.1.1 and 6.0.0. Untagged statements hold at these versions only.
Sources: FHIRSVC-51b9b37, MSVC-251a73d, MEASURE-18c8d4d, JMODELS-49ffdec, PKGUTIL-dd71537, QICORE-4.1.1, QICORE-6.0.0, ECQM2025-d4e0edd, DQMCMS-757d7c6

What a QI-Core test case bundle must contain for MADiE to validate and run it, and what the usual
measure libraries expect of the resources in it. The FHIR and QI-Core rules themselves are in the
QI-Core IG; this file covers where MADiE and the measure libraries add to them.

## Models

MADiE's measure models are FHIR 4.0.1, QI-Core 4.1.1, QI-Core 6.0.0, US Core 6.1.0-derived, US Quality
Core 0.5.0 and QDM 5.6 [src: JMODELS-49ffdec src/…/models/common/ModelType.java:12-18]. This skill covers
the two QI-Core models, which most CMS FHIR measures use. Test case export is packaged for those two
and US Quality Core 0.5.0 [src: PKGUTIL-dd71537 src/…/PackagingUtilityFactory.java:19-26].

## Validation

MADiE validates a test case when it's created, saved or imported
[src: MSVC-251a73d src/…/services/TestCaseService.java:258-322]. QI-Core 6.0.0 test cases are validated
in the background after saving; 4.1.1 test cases before. The checks
[src: FHIRSVC-51b9b37 src/…/services/ResourceValidationService.java:38-150]:

| Check | Result |
| --- | --- |
| A resource has no id, or two resources share an id (even of different types) | Error |
| `meta.profile` missing, or not a valid URL | Warning: "Resources missing Meta.profile may cause incorrect results" |
| A `meta.profile` whose type isn't the resource's type | Error [src: FHIRSVC-51b9b37 src/…/services/ResourceValidationService.java:400-457] |
| A reference that doesn't resolve to a resource in the bundle, in a resource other than the Patient | Warning, and that resource is **left out when the test case runs** |
| The same, in the Patient | Error |
| FHIR profile validation (HAPI) against each declared profile | Errors and warnings as reported; an unknown code system is a warning |

The HAPI validator loads QI-Core 4.1.1 with US Core 3.1.0 for 4.1.1 measures, and QI-Core 6.0.0 with
US Core 6.1.0 for 6.0.0 measures [src: FHIRSVC-51b9b37 src/…/config/HapiFhirConfig.java:78-110].

A test case with any error is **invalid**. It can't be run unless the measure's test case
configuration allows running invalid test cases [src: MEASURE-18c8d4d src/…/qiCore/EditTestCase.tsx:195-205],
and it's left out of exports.

## Ids and references

- **Ids:** every resource needs one, unique across the bundle. They needn't be UUIDs, though MADiE
  makes UUIDs for resources it creates [src: MEASURE-18c8d4d src/…/api/fhirDefinitionServiceUtilities.tsx:830-845].
  The Patient's id is replaced by the test case's patient id on save; other resources' ids are replaced
  with new UUIDs on every export (see [test-case-files.md](test-case-files.md)).
- **References:** use relative `Patient/<id>` and `<Type>/<id>`. References are resolved by type and id
  within the bundle, so a `urn:uuid:` or absolute reference never resolves, and the resource holding it
  is dropped from execution. Only relative `Patient/…` references are rewritten when the Patient id
  changes [src: MSVC-251a73d src/…/utils/JsonUtil.java:129-132].
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
  cases declare `http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-patient`
  [src: MEASURE-18c8d4d src/…/util/QiCoreTestCaseHelper.ts:5-20]. QI-Core's Patient, in both versions,
  also requires at least one `identifier` and a `gender`
  [src: QICORE-6.0.0 package/StructureDefinition-qicore-patient.json]
  [src: QICORE-4.1.1 package/StructureDefinition-qicore-patient.json]; without them the profile check
  fails and the test case is invalid. Any synthetic identifier works, such as
  `{"system": "https://madie.cms.gov/", "value": "SYN-0001"}`.

## How MADiE runs test cases

MADiE runs QI-Core test cases **in the browser, with fqm-execution 1.8.6**
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

## QI-Core profiles by version

Profile URLs are `http://hl7.org/fhir/us/qicore/StructureDefinition/<id>`. The ids differ between the
two versions for Condition and Observation:

| Resource | QI-Core 4.1.1 | QI-Core 6.0.0 |
| --- | --- | --- |
| Condition | `qicore-condition` | `qicore-condition-problems-health-concerns` (problem list, health concerns) or `qicore-condition-encounter-diagnosis` |
| Observation | `qicore-observation` | `qicore-observation-clinical-result`, `qicore-observation-lab`, `qicore-observation-screening-assessment`, `qicore-simple-observation`, `qicore-nonpatient-observation`, plus the US Core profiles (vital signs, smoking status…) |
| Not-done events | `qicore-observationnotdone`, `qicore-procedurenotdone`… | `qicore-observationcancelled`, `qicore-procedurenotdone`… |
| Patient, Encounter, Procedure, ServiceRequest, DeviceRequest, MedicationRequest, CareTeam, Location, PractitionerRole… | `qicore-<resource>` | `qicore-<resource>` |

[src: QICORE-4.1.1 package/StructureDefinition-qicore-*.json] [src: QICORE-6.0.0 package/StructureDefinition-qicore-*.json]

Use the profiles of the measure's model. MADiE's validator loads only that QI-Core version, so a 6.0.0
profile URL in a 4.1.1 measure's test case, or the reverse, isn't a profile it knows, and the resource
isn't checked against it [src: FHIRSVC-51b9b37 src/…/services/ResourceValidationService.java:426-437].

## Resource notes

- **Observation value and status.** In QI-Core 6.0.0's Simple Observation, `value[x]` is optional and
  must-support, and `category` is required but not fixed to any code
  [src: QICORE-6.0.0 package/StructureDefinition-qicore-simple-observation.json]. It's the general
  Observation profile for observations with no more specific one, not a "no value" profile. Whether an
  Observation counts is decided by the measure's CQL, not the profile: the common `Status` library keeps
  `final`, `amended` and `corrected` results for most kinds
  [src: ECQM2025-d4e0edd input/cql/Status.cql:90-93], `preliminary` too for symptoms
  [src: ECQM2025-d4e0edd input/cql/Status.cql:147-150], and only `final` for smoking status
  [src: ECQM2025-d4e0edd input/cql/Status.cql:142-145]. Read the measure's own logic for the statuses and
  value tests it uses.
- **`dataAbsentReason`** may be given instead of a value, never with one (FHIR invariant obs-6). A measure
  that tests `value is not null` won't count such an Observation; FHIR doesn't require
  `dataAbsentReason` when a value is missing.
- **Condition status.** `verificationStatus` and `clinicalStatus` are both optional in QI-Core
  [src: QICORE-6.0.0 package/StructureDefinition-qicore-condition-problems-health-concerns.json]. The
  `Status` library's `verified()` keeps conditions with **no** verification status, or confirmed,
  unconfirmed, provisional or differential; it drops refuted and entered-in-error
  [src: ECQM2025-d4e0edd input/cql/Status.cql:21-30]. QICoreCommon's `isActive()` needs a clinical
  status of active, recurrence or relapse [src: ECQM2025-d4e0edd input/cql/QICoreCommon.cql:108-114].
  So set `clinicalStatus` when the measure tests for active conditions; `confirmed` isn't required.
- **Encounter.** `status`, `class` and at least one `type` are required. `class` is a Coding from
  `http://terminology.hl7.org/CodeSystem/v3-ActCode`, such as `IMP` (inpatient), `AMB` (ambulatory),
  `EMER` (emergency) or `HH` (home health); the measure's value sets usually test `type`
  [src: QICORE-6.0.0 package/StructureDefinition-qicore-encounter.json]. The `Status` library counts an
  encounter as performed when its status is `finished` [src: ECQM2025-d4e0edd input/cql/Status.cql:69-73].
- **Procedure:** `completed` for performed [src: ECQM2025-d4e0edd input/cql/Status.cql:85-88].
- **Orders** (ServiceRequest, DeviceRequest, MedicationRequest): status `active` or `completed`, with an
  order intent such as `order` [src: ECQM2025-d4e0edd input/cql/Status.cql:37-59].
- **DeviceRequest.** The device is `code[x]`, either `codeCodeableConcept` or `codeReference`; there's
  no plain `code` property in JSON [src: QICORE-6.0.0 package/StructureDefinition-qicore-devicerequest.json].
- **The measurement period.** Date the test data against the measurement period set on the measure in
  MADiE, not the CQL parameter's default; the exported MeasureReport's `period` is that period
  [src: FHIRSVC-51b9b37 src/…/services/TestCaseBundleService.java:176-179].

The `Status` library cited here is version 1.15.000, from the 2025 QI-Core 6.0.0 eCQM content; a
measure may use a different version, or its own status tests.
