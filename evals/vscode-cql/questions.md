# vscode-cql Skill Test Questions

Questions that check whether an agent sets up, uses and troubleshoots the VS Code CQL extension 1.0.0
and cql-language-server 5.0.0 correctly. The answer key is in [answers.md](answers.md). Keep it out of
any copy of the skill given to an agent under test.

## Setup

### SU-01. Java

The extension won't start the language server on a new machine. What Java does it need, and where
does it look for it?

### SU-02. Two projects

A developer opens a multi-root workspace with two IG repositories, `measures-ig` and `shared-ig`, as
separate workspace folders. The CQL Explorer shows only `measures-ig`. Why?

## Projects and test data

### PL-01. A different CQL folder

An IG keeps its CQL in `input/logic` and sets `path-binary` to `input/logic`. Will the extension find
and run those libraries?

### PL-02. A Bundle of test data

A test case folder holds `Patient-p1.json` and `Bundle-p1-data.json`, a collection Bundle with the
patient's Encounters and Observations. The results act as if the patient has no Encounters. Why?

### PL-03. File names

A test case folder has `Patient-p1.json`, `Encounter-e1.json` and `obs-1.json` (an Observation). The
Observation is never seen. Why?

### PL-04. Different counts

The CQL Explorer shows three test cases for `ScreeningLogic`, but Execute CQL runs five. What's the
likely cause?

## Configuration and parameters

### CF-01. "Not allowed"

VS Code underlines `"resultFormat": "individual"` in `input/tests/config.jsonc` with "Property
resultFormat is not allowed". Is the setting wrong?

### CF-02. Where are the results?

After Execute CQL, where are the results by default, and how do you get one JSON file per test case?

### CF-03. Only an error

After Execute CQL, one test case's results show just `Error=Invalid Interval - the ending boundary
must be greater than or equal to the starting boundary.`, with no other values, while the other test
cases look normal. The library has forty definitions. What happened, and how do I find the problem?

### CF-04. Expected values

My test case folders each have a MeasureReport with the expected population counts. How does the
extension tell me which test cases pass?

### PA-01. An unquoted string

`config.jsonc` has `{ "name": "Product Line", "type": "String", "value": "HMO" }` alongside a
correct Measurement Period. The run succeeds, but the Measurement Period seems to be ignored too.
Why?

### PA-02. Dates

The library declares `parameter "Measurement Period" Interval<DateTime>`. Which `type` and `value`
should the configuration use for all of 2024?

## Terminology and libraries

### TE-01. Value sets not found

A value set is in `input/vocabulary/valueset/` with the right `url`, but Execute CQL behaves as if it
doesn't exist. The project has `input/cql` and `input/tests` but no `ig.ini`. What's wrong?

### LR-01. Versions

A library has `include Helpers version '1.0.0'`, and the only file is `input/cql/Helpers-1.0.1.cql`.
Does it resolve? What if `config.jsonc` sets `"libraryResolution": "strict"`?

### LR-02. Sharing a library

How should a measure project include a library from a sibling project, `common-ig` (packageId
`example.fhir.common`), in the same workspace folder?

### LR-03. The package cache

A team's IG declares a `dependsOn` with `version="dev"` for a sibling project. Since then, IG
Publisher builds behave as if `example.fhir.common#current` is empty. Could the extension be
involved?

### LR-04. Stale includes

After adding a package to the IG's `dependsOn` in `ig.ini`'s IG resource, an include from that
package still shows as unresolved. What should the developer do?

## Debugging and editing

### DB-01. A launch.json

A developer copied this from the wiki, and debugging doesn't work:

```json
{ "type": "cql", "request": "launch", "libraryUri": "${fileDirname}",
  "libraryName": "${fileBasenameNoExtension}", "testCaseName": "p1" }
```

What's wrong, and what's the easier way?

### ED-01. Completion

Typing in a `.cql` file offers no suggestions for expression names defined earlier in the library.
Is the extension broken?

## Versions

### VR-01. A newer extension

A user has vscode-cql 1.2.0 with cql-language-server 5.2.0 and asks whether Bundles in test case
folders are still ignored. How should the answer be reached?

## Task

### TK-01. Set up a project for the extension

Create `tk-01/`, a CQL project that the VS Code CQL extension 1.0.0 can run and debug:

- `input/cql/WeightCheck.cql`: FHIR 4.0.1; a value set "Body Weight Codes"
  (`http://example.org/fhir/ValueSet/body-weight-codes`) holding LOINC 29463-7; parameters
  `"Measurement Period" Interval<DateTime>` and `"Product Line" String default 'Commercial'`; and
  definitions for whether the patient has a body weight Observation in the measurement period and
  whether the product line is Commercial.
- At least two test cases with synthetic data, one of which has a weight Observation.
- The value set, so that Execute CQL can use it.
- `input/tests/config.jsonc`: results as one JSON file per test case; Measurement Period = all of
  2024 for every test case; Product Line = Medicaid for one test case only; and one test case
  excluded, with a reason.
- `.vscode/launch.json` that debugs `WeightCheck` with one of the test cases. Assume the project is
  at `/home/user/tk-01`.
