# madie Skill Test Questions

Questions for an agent answering MADiE questions. Answer each in a few sentences, as you would to a
measure developer. Then do task TK-01. The answer key is in `answers.md`; don't read it.

All patient data in these questions is synthetic.

## Zips and the `.madie` file

**ZP-01. A parent folder.** I put my three test case folders (each named by a UUID) in a folder called
`TestCases`, zipped `TestCases`, and imported it. MADiE says "Unable to find any valid test case json.
Please make sure the format is accurate". The JSON is valid. What's wrong?

**ZP-02. testCaseId.** I'm generating a `.madie` file for test cases I built outside MADiE. How do I
generate the `testCaseId` for each entry?

**ZP-03. An old zip.** A colleague sent me a test case zip exported in 2023. Importing it gives "Zip file
is in an incorrect format". What do I do?

## Importing

**IM-01. Copying test cases.** I exported a measure's test cases and imported the zip back into the same
measure to duplicate them. No new test cases appeared, and the titles didn't change. Why, and how do I
copy them?

**IM-02. No expected values.** My imported test cases have no expected values, and MADiE showed a warning
about the measure populations. The bundles each have a MeasureReport. What should I check?

**IM-03. Title required.** Import fails for one test case with "Test Case Title is required.", but the
`.madie` file has a title for it. Why?

**IM-04. A transaction bundle.** I generated test cases as transaction bundles: each entry has a
`request`, `fullUrl`s are `urn:uuid:…`, and resources reference each other by those `urn:uuid` values.
Will MADiE accept them?

## Exporting

**EX-01. File names.** What are the JSON files in a MADiE test case export named, and where does each
part of the name come from?

**EX-02. Changing ids.** I exported the same test cases twice and the Encounter and Condition ids are
different each time, but the Patient id is the same. Is something wrong?

**EX-03. The MeasureReport profile.** Which profile does the MeasureReport in a MADiE export declare?

## Validation and resources

**VA-01. meta.profile.** MADiE warns that a resource is "missing the Meta.profile". Can the test case
still run?

**VA-02. A dangling reference.** A Condition's `encounter` points to an Encounter that isn't in the
bundle. What does MADiE do?

**RS-01. Simple Observation.** I was told QI-Core's Simple Observation profile can't have a value, so I
left the value out of my test Observation. Is that right?

**RS-02. Confirmed conditions.** Must a Condition have `verificationStatus` `confirmed` to count in a
CMS QI-Core measure?

**RS-03. A Condition profile.** My test Condition declares
`http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-condition`, and the measure is QI-Core 6.0.0.
Is that a problem?

## Measure CQL

**CQ-01. The library line.** I changed `library MyMeasure version '1.0.0'` in the MADiE editor, saved,
and MADiE put back a different line. Why?

**CQ-02. A value set URL.** My CQL has
`valueset "Office Visit": 'urn:oid:2.16.840.1.113883.3.464.1003.101.12.1001'` and MADiE flags it. Why?

**CQ-03. A library name.** Can a QI-Core measure's CQL library be called `Follow_Up_Measure`?

## Series

**SE-01. Series names.** Must test case series be named `IPPPass`, `NUMERFail` and so on?

## Versions

**VR-01. A newer MADiE.** MADiE shows an import error message the skill doesn't mention. How should the
answer be found?

## Task

**TK-01. Build test cases for import.** A QI-Core 6.0.0 proportion measure in MADiE has the CQL library
`ExampleFollowUp`, eCQM abbreviated title `ExampleFollowUpFHIR`, version `0.1.000`, a 2026 measurement
period, and one population criteria with a boolean basis and the populations Initial Population,
Denominator, Denominator Exclusion and Numerator, in that order. The Initial Population is a finished
inpatient encounter in the measurement period; the Denominator equals it; the Denominator Exclusion is an
active hospice-care condition; the Numerator is an ambulatory encounter within 7 days after discharge.

Build a folder, `tk-01/`, laid out so that zipping its contents gives a zip MADiE imports, with three new
test cases and their expected values:

| Series | Title | IP | DENOM | DENEX | NUMER |
| --- | --- | --- | --- | --- | --- |
| `DENOMPass` | `NoFollowUp` | 1 | 1 | 0 | 0 |
| `NUMERPass` | `FollowUpVisit` | 1 | 1 | 0 | 1 |
| `DENEXPass` | `HospiceCare` | 1 | 1 | 1 | 0 |

Use QI-Core 6.0.0 profiles and synthetic data only.
