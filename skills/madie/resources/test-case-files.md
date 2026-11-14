# Test Case Files: Export, Import and the `.madie` File

Baseline: MADiE `develop` as of 2026-11-14 (commits in SOURCES.md), for QI-Core measures. Untagged statements hold at these commits only.
Sources: FHIRSVC-51b9b37, MSVC-251a73d, MEASURE-18c8d4d, PKGUTIL-dd71537, JMODELS-49ffdec, TSMODELS-960ea63, CQM-2.0.0

What MADiE writes when it exports QI-Core test cases, what it accepts on import, and what it changes in
the JSON. QDM test cases use the same import screen with different rules; they aren't covered here.

## The export zip

Export is from a measure's Test Cases tab. The user chooses **Transaction Bundle** or **Collection
Bundle** [src: MEASURE-18c8d4d src/…/ActionCenter/ActionCenter.tsx:599-613]; the API's default is
collection [src: MSVC-251a73d src/…/resources/ExportController.java:123-125]. Packaging exists for
QI-Core 4.1.1, QI-Core 6.0.0 and US Quality Core 0.5.0 measures [src: PKGUTIL-dd71537 src/…/PackagingUtilityFactory.java:19-26].

```text
CMS9999FHIR-v1.2.000-FHIR-TestCases.zip
  README.txt
  .madie
  6b1a7c1e-4c0f-4e8f-9b0a-1f2e3d4c5b6a/
    CMS9999FHIR-v1.2.000-DENOMPass-InpatientStay.json
  0f3e2d1c-…/
    CMS9999FHIR-v1.2.000-NUMERFail-NoFollowUp.json
```

- **Zip name:** `{eCQM title}-v{version}-FHIR-TestCases.zip`, set by the browser
  [src: MEASURE-18c8d4d src/…/qiCore/TestCaseList.tsx:437-440]. "FHIR" is the model family of every
  non-QDM model [src: TSMODELS-960ea63 src/Model.ts:50-54].
- **No parent folder.** The zip root holds `README.txt`, `.madie` and one folder per test case
  [src: FHIRSVC-51b9b37 src/…/services/TestCaseBundleService.java:648-667].
- **Folder name:** the test case's patient id, a UUID.
- **File name:** `{eCQM title}-v{version}-{series}-{title}.json`, or
  `{eCQM title}-v{version}-{title}.json` when the series is empty. Whitespace is removed from the series
  and title, and nothing else is changed
  [src: FHIRSVC-51b9b37 src/…/utils/ExportFileNamesUtil.java:16-35]
  [src: PKGUTIL-dd71537 src/…/qicore411/PackagingUtilityImpl.java:203]. The eCQM title is the measure's
  "eCQM Abbreviated Title" (at most 32 characters), not its name
  [src: JMODELS-49ffdec src/…/models/measure/Measure.java:90-98]. The version is
  `major.minor.revision` with a three-digit revision, such as `v1.2.000`
  [src: JMODELS-49ffdec src/…/models/common/Version.java:35-42].
- **README.txt** lists `Case # {n} - {patientId} = {series} {title}` for each test case, and the test
  cases left out as invalid [src: FHIRSVC-51b9b37 src/…/services/TestCaseBundleService.java:561-602].
- **Invalid test cases aren't exported.** A test case that failed validation, or has no JSON, is left
  out [src: FHIRSVC-51b9b37 src/…/services/TestCaseBundleService.java:79-93], and the export then returns
  HTTP 206 [src: FHIRSVC-51b9b37 src/…/resources/TestCaseBundleController.java:74-92].
  The browser also refuses to export when a title or series has a special character
  [src: MEASURE-18c8d4d src/…/util/checkSpecialCharacters.ts:3-8].

## The `.madie` file

A JSON array with one entry per exported test case
[src: FHIRSVC-51b9b37 src/…/services/TestCaseBundleService.java:604-625]
[src: JMODELS-49ffdec src/…/dto/TestCaseExportMetaData.java:12-18]:

```json
[
  {
    "testCaseId": "6720f1c2a9e4b51d3c8f0a17",
    "patientId": "6b1a7c1e-4c0f-4e8f-9b0a-1f2e3d4c5b6a",
    "title": "InpatientStay",
    "series": "DENOMPass",
    "description": "Inpatient encounter ending in the measurement period; no follow-up."
  }
]
```

- **`testCaseId`** is MADiE's internal database id for the test case (a 24-character hex string). It is
  **not read on import**; nothing derives it from the patient id. For a hand-built zip, any value, or
  leaving it out, works.
- **`patientId`** joins an entry to its folder [src: MEASURE-18c8d4d src/…/import/TestCaseImportDialog.tsx:160-176].
- **`title`, `series` and `description`** are the only fields import uses
  [src: MSVC-251a73d src/…/services/TestCaseService.java:822-849].
- **It's required.** A zip with no file ending in `.madie` is rejected: "Zip file is in an incorrect
  format. If this is an export prior to June 20, 2024 please reexport your test case and try again."
  [src: MEASURE-18c8d4d src/…/import/TestCaseImportDialog.tsx:96-104]
  [src: MEASURE-18c8d4d src/…/import/TestCaseImportDialog.tsx:178-182].
- **Without a matching entry**, a folder's title falls back to the Patient's first given name and its
  series to the family name [src: MSVC-251a73d src/…/services/TestCaseService.java:822-833]. The
  description falls back to a MeasureReport extension, but only under the old CQFM URL
  `http://hl7.org/fhir/us/cqfmeasures/StructureDefinition/cqfm-testCaseDescription`
  [src: MSVC-251a73d src/…/utils/JsonUtil.java:44-45], while MADiE's own export writes the CQM URL (below),
  so a description survives a round trip only through `.madie`.

## Importing a zip

Import is **Import Test Cases** on the Test Cases tab. It takes one `.zip` file and nothing else: there's
no single-JSON import for QI-Core measures
[src: MEASURE-18c8d4d src/…/import/TestCaseImportDialog.tsx:49-66]. The browser has the file
virus-scanned, opens it with JSZip, and sends the server only the JSON text of each test case
[src: MEASURE-18c8d4d src/…/import/TestCaseImportDialog.tsx:72-134]. The scan upload is limited to
10 MB [src: MSVC-251a73d src/main/resources/application.yml:12-14].

**Which entries count** [src: MEASURE-18c8d4d src/…/import/TestCaseImportDialog.tsx:107-131]:

- An entry counts when its first path segment is a **UUID** and it ends in `.json`. The JSON file's own
  name doesn't matter. Everything else is skipped silently: `__MACOSX/`, folders not named by UUID,
  other file types.
- `\` is accepted as the separator, for zips made by some Windows tools.
- **A parent folder breaks the import.** If the zip has `MyTests/<uuid>/x.json`, the first segment
  isn't a UUID, nothing counts, and the message is "Unable to find any valid test case json. Please
  make sure the format is accurate" [src: MEASURE-18c8d4d src/…/import/TestCaseImportDialog.tsx:183-186].
  Zip the folder's contents, not the folder.
- **One JSON file per folder.** More than one fails with "Multiple test case files are not supported";
  an empty folder fails with "Test Case file is missing."
  [src: MSVC-251a73d src/…/services/TestCaseService.java:560-580].

**New or updated.** Each folder's UUID becomes the test case's patient id
[src: MSVC-251a73d src/…/services/TestCaseService.java:586-608]:

- **A test case with that patient id already exists:** only its description and JSON are replaced. Its
  title, series and expected values are kept [src: MSVC-251a73d src/…/services/TestCaseService.java:745-754].
- **Otherwise a new test case is created**, with its expected values read from the bundle's
  MeasureReport (below).
- A new test case is refused, "Test Case Title is required.", if the Patient has no given name, **even
  when `.madie` supplies a title**, because the name is checked first
  [src: MSVC-251a73d src/…/services/TestCaseService.java:615-628]. A Patient `name` with no `family`
  makes the import fail with an unhandled error [src: MSVC-251a73d src/…/utils/JsonUtil.java:170-177].
  Give the Patient both a given and a family name.
- **Title and series together must be unique** within the measure, ignoring case and whitespace
  [src: MSVC-251a73d src/…/utils/TestCaseServiceUtil.java:753-759]. A test case another user has locked
  isn't changed and is reported as failed [src: MSVC-251a73d src/…/resources/TestCaseController.java:134-148].

## What MADiE changes in the JSON

On every save, including import, a QI-Core test case's JSON is rewritten before validation; import
also removes the MeasureReport
[src: MSVC-251a73d src/…/services/TestCaseService.java:282-295]:

| Change | Detail |
| --- | --- |
| MeasureReport removed (import only) | Import reads the expected values from it, then drops it [src: MSVC-251a73d src/…/utils/TestCaseServiceUtil.java:744-752] |
| Patient id | Set to the test case's patient id, and its `fullUrl` to `https://madie.cms.gov/Patient/<id>` [src: MSVC-251a73d src/…/utils/JsonUtil.java:426-456] |
| Other `fullUrl`s | Rewritten to `https://madie.cms.gov/<Type>/<id>`, only for entries that already have one; ids are kept [src: MSVC-251a73d src/…/utils/JsonUtil.java:459-491] |
| Patient references | Every `"reference": "Patient/<anything>"` becomes `Patient/<patient id>`. Absolute URLs and `urn:uuid:` references aren't touched [src: MSVC-251a73d src/…/utils/JsonUtil.java:129-132] |
| Bundle type | `transaction` becomes `collection`, and every `entry.request` is removed [src: MSVC-251a73d src/…/utils/JsonUtil.java:363-380] |

So a transaction bundle with `request` entries imports fine, but MADiE stores a collection. New test
cases start as a collection bundle with a Patient whose `fullUrl` is on `https://madie.cms.gov/`
[src: MEASURE-18c8d4d src/…/util/QiCoreTestCaseHelper.ts:22-40].

**On export** the reverse happens [src: FHIRSVC-51b9b37 src/…/services/TestCaseBundleService.java:122-162]:

- The Patient's id is the patient id. **Every other resource gets a new random UUID on every export**,
  and each `Type/oldId` reference in the bundle is changed to match. Don't rely on resource ids staying
  the same between exports.
- A transaction export adds `request: {method: PUT, url: <Type>/<id>}` to every entry; a collection
  export has no `request`.

## The MeasureReport

**Export adds one** to each bundle, holding the test case's expected values
[src: FHIRSVC-51b9b37 src/…/services/TestCaseBundleService.java:164-288]:

- `meta.profile`: `http://hl7.org/fhir/uv/cqm/StructureDefinition/cqm-testcase`, the CQM IG's test
  case profile [src: FHIRSVC-51b9b37 src/…/constants/UriConstants.java:129-138]
  [src: CQM-2.0.0 StructureDefinition-cqm-testcase.json]. Not the older CQFM `test-case-cqfm` profile.
- `modifierExtension` `cqm-isTestCase` = true; `extension` `cqf-inputParameters`, pointing at a
  contained Parameters resource with a `subject` parameter set to the Patient id; and
  `cqm-testCaseDescription`.
- `status: complete`, `type: individual`, `measure: https://madie.cms.gov/Measure/<CQL library name>`
  (no version), `period` = the measurement period as dates.
- One `group` per population criteria, with `id` = `Group_1`, `Group_2`… Each population's `code` is
  from `http://terminology.hl7.org/CodeSystem/measure-population`, its `id` is MADiE's display id
  (`InitialPopulation_1`…), and its `count` is the expected value: 1 or 0 for a boolean basis, omitted
  when no expected value is set [src: FHIRSVC-51b9b37 src/…/utils/FhirResourceHelpers.java:72-84].
- `measureScore` is a placeholder, not a computed score.
- `evaluatedResource` lists every resource in the bundle.

**Import reads expected values from it**, when creating a test case
[src: MSVC-251a73d src/…/utils/JsonUtil.java:214-291]:

- The group number is the **last character** of `group.id`, so `Group_1` is group 1 (and a tenth group
  can't be matched).
- Populations are matched to the measure's populations **in order, by code**. Observations are matched
  by an `id` containing `MeasureObservation`.
- For a boolean population basis, `count` 1 is true and anything else false
  [src: MSVC-251a73d src/…/utils/TestCaseServiceUtil.java:256-264].
- If the number of groups, or of populations in a group, differs from the measure's, the test case is
  still imported with a warning and **no expected values**
  [src: MSVC-251a73d src/…/services/TestCaseService.java:660-666]. The same happens with no MeasureReport.

The population codes are those of `PopulationType`: `initial-population`, `numerator`,
`numerator-exclusion`, `denominator`, `denominator-exclusion`, `denominator-exception`,
`measure-population`, `measure-population-exclusion` and `measure-observation`
[src: JMODELS-49ffdec src/…/models/measure/PopulationType.java:8-32].

A minimal MeasureReport that import accepts, for a proportion measure with one group and a boolean
basis:

```json
{
  "resourceType": "MeasureReport",
  "id": "a3f0c9de-2b7e-4f51-9d6c-0e8b1a2c3d4e",
  "meta": { "profile": ["http://hl7.org/fhir/uv/cqm/StructureDefinition/cqm-testcase"] },
  "modifierExtension": [
    { "url": "http://hl7.org/fhir/uv/cqm/StructureDefinition/cqm-isTestCase", "valueBoolean": true }
  ],
  "status": "complete",
  "type": "individual",
  "measure": "https://madie.cms.gov/Measure/ExampleFollowUp",
  "period": { "start": "2026-01-01", "end": "2026-12-31" },
  "group": [{
    "id": "Group_1",
    "population": [
      { "id": "InitialPopulation_1", "code": { "coding": [{ "system": "http://terminology.hl7.org/CodeSystem/measure-population", "code": "initial-population" }] }, "count": 1 },
      { "id": "Denominator_1", "code": { "coding": [{ "system": "http://terminology.hl7.org/CodeSystem/measure-population", "code": "denominator" }] }, "count": 1 },
      { "id": "DenominatorExclusion_1", "code": { "coding": [{ "system": "http://terminology.hl7.org/CodeSystem/measure-population", "code": "denominator-exclusion" }] }, "count": 0 },
      { "id": "Numerator_1", "code": { "coding": [{ "system": "http://terminology.hl7.org/CodeSystem/measure-population", "code": "numerator" }] }, "count": 0 }
    ]
  }]
}
```

List the populations in the order the measure's population criteria define them in MADiE. The safest
template is a MeasureReport from a MADiE export of the same measure.

## Titles and series

- **Both are free text.** The series is labelled "Test Case Group" in MADiE. Its suggestions are the
  series already used on the measure, plus `Add "<text>"`
  [src: MEASURE-18c8d4d src/…/createTestCase/TestCaseSeries.tsx:32-54]. MADiE has no list of series.
- The server accepts letters, digits, spaces, `_` and `-` [src: MSVC-251a73d src/…/utils/TestCaseServiceUtil.java:673-688].
  The browser also rejects `_` and other punctuation
  [src: MEASURE-18c8d4d src/…/util/checkSpecialCharacters.ts:3-8], so use letters, digits and `-`.
- A title is required; title and series are at most 250 characters each, and 250 together on create
  [src: JMODELS-49ffdec src/…/models/measure/TestCase.java:35-48]
  [src: MSVC-251a73d src/…/services/TestCaseService.java:111-113].

**A common naming convention**, not something MADiE checks, carried over from Bonnie: the series names
the population the case is meant to reach or miss.

| Series | The case is meant to |
| --- | --- |
| `IPPPass` / `IPPFail` | enter / not enter the Initial Population |
| `DENOMPass` / `DENOMFail` | enter / not enter the Denominator |
| `DENEXPass` / `DENEXFail` | enter / not enter the Denominator Exclusion |
| `DENEXCEPPass` / `DENEXCEPFail` | enter / not enter the Denominator Exception |
| `NUMERPass` / `NUMERFail` | enter the Numerator / reach the Denominator but not the Numerator |

The series is a label only: what MADiE compares is the expected values, which must be set for each
population.
