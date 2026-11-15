# Test Cases in VS Code

Baseline: vscode-cql 1.0.0 with cql-language-server 5.0.0; fqm-execution 1.8.6 (MADiE's engine); MADiE `develop` as of 2026-11-14. Untagged statements hold at these versions only.
Sources: VSCQL-855eac7, CQLLS-68e601f, FQM-8f1038a, MEASURE-18c8d4d, CQLTESTS-5747d2b

How to work on MADiE test cases in VS Code with the CQL extension (`cqframework.cql`), in both
directions:

- **VS Code to MADiE:** build and check test cases locally, then package them as a zip MADiE imports.
- **MADiE to VS Code:** unpack a MADiE export, run it with Execute CQL, and check each case against the
  expected values MADiE stored.

Setting up the extension itself (Java, `ig.ini`, value sets, `config.jsonc`) is in the `vscode-cql`
skill. The scripts here are in `scripts/`; run them from the project root.

## The two layouts

| | MADiE zip | VS Code |
| --- | --- | --- |
| Test case | `<patient UUID>/<anything>.json`, one Bundle | `input/tests/<Library>/<patient UUID>/`, one resource per file, named `<ResourceType>-<id>.json` |
| Titles, series, descriptions | `.madie` at the zip root | `input/tests/<Library>/.madie` (kept by the scripts; the extension ignores it) |
| Expected values | a MeasureReport in the Bundle | a `MeasureReport-<id>.json` file in the test case folder |

- **The extension ignores Bundles** in a test case folder: it reads files of the resource type it's
  retrieving and skips the rest [src: CQLLS-68e601f ls/server/…/repository/ig/standard/IgStandardRepository.kt:310-330].
  So an exported test case has to be split into one file per resource.
- **Test cases are folders** under every folder named after the library (the `.cql` file name) in
  `input/tests`; files beside them, and a sub-folder named `shared`, aren't test cases
  [src: VSCQL-855eac7 src/model/testCase.ts:25-51]. The folder name is the patient id, so it should equal
  the Patient's `id`.
- **The MeasureReport file is harmless to the run** (nothing retrieves MeasureReport) and the extension
  reads it: a file whose name starts with `MeasureReport` gives the case's expected populations and
  description [src: VSCQL-855eac7 src/model/testCase.ts:72-101]. The extension reads the description only
  under the CQFM URL, `cqfm-testCaseDescription` [src: VSCQL-855eac7 src/model/testCase.ts:113-123], while
  MADiE exports it under the CQM URL; `madie_to_vscode.py` adds the CQFM extension. Extension 1.0.0
  doesn't compare the expected values with the results; `check_results.py` does.

## From MADiE to VS Code

1. Export the test cases from MADiE (either bundle type).
2. Unpack them for the library under test:

   ```bash
   python3 scripts/madie_to_vscode.py ExampleFollowUpFHIR-v0.1.000-FHIR-TestCases.zip --library ExampleFollowUp
   ```

   This writes `input/tests/ExampleFollowUp/<patient UUID>/<ResourceType>-<id>.json` for each case,
   keeps `.madie`, and prints a `config.jsonc` entry for the measurement period the MeasureReports
   record. It won't overwrite existing case folders without `--force`.
3. **Set the measurement period.** MADiE runs with the measurement period set on the measure, not the
   CQL parameter's default; the US Quality Core template declares `"Measurement Period"` with no default
   at all. Add the printed entry to `input/tests/config.jsonc` (see the `vscode-cql` skill for the
   format).
4. **Provide the value sets.** The test cases don't carry terminology. Put expanded value sets for the
   measure in `input/vocabulary/valueset/` (the project needs an `ig.ini`; see the `vscode-cql` skill).
5. Set `"resultFormat": "individual"` in `config.jsonc`, run **Execute CQL** on the library, and check
   the results (below).

## From VS Code to MADiE

1. Build each test case as a folder `input/tests/<Library>/<new UUID>/` with one resource per file,
   named `<ResourceType>-<id>.json`, and the Patient's `id` equal to the folder name. Follow
   [test-case-content.md](test-case-content.md): US Quality Core profiles, a Patient with given and
   family names, an `identifier` and a `gender`, and relative references.
2. Add a `MeasureReport-<id>.json` with the expected values, in the form described in
   [test-case-files.md](test-case-files.md#the-measurereport), so MADiE sets them on import.
3. Give it a title and series, either in `input/tests/<Library>/.madie` (an entry with the folder's
   `patientId`) or as the Patient's first given name (title) and family name (series), which is what
   MADiE's import falls back to.
4. Run and check the cases in VS Code (below) until they pass.
5. Package them:

   ```bash
   python3 scripts/vscode_to_madie.py input/tests/ExampleFollowUp -o ExampleFollowUp-tests.zip
   ```

   This writes a collection Bundle per case with the Patient first and `fullUrl`s on
   `https://madie.cms.gov/`, and the `.madie` file, then runs `check_test_cases.py` on the zip. Import it
   into the measure in MADiE.

## Checking results

Execute CQL writes each top-level definition's value per test case. With the `individual` result
format each case gets `input/tests/results/<Library>/TestCaseResult-<case>.json`, with its results, any
errors, and the parameters used and where they came from [src: VSCQL-855eac7 src/commands/execute-cql-file.ts:361-419];
the default `flat` format puts every case's `name=value` lines in one log
[src: VSCQL-855eac7 src/commands/execute-cql-file.ts:345-359]. Values are formatted by the language
server: `true`, `false`, `null`, a resource as `Encounter(id=enc-1)`, and a list in brackets
[src: CQLLS-68e601f ls/server/…/command/CqlEvaluator.kt:345-372].

```bash
python3 scripts/check_results.py input/tests/ExampleFollowUp input/tests/results/ExampleFollowUp \
  --measure ExampleFollowUp-Measure.json
```

`--measure` takes the Measure resource (or a Bundle containing it, such as MADiE's measure export), for
each group's population definitions, population basis and scoring. Without it, give a small JSON file
with `--populations`, or rely on the usual definition names (`"Initial Population"`, `"Denominator"`…).

**How pass and fail are decided.** The script reproduces what MADiE does with the same definition
results:

1. **Population values.** For a boolean population basis, a population is met when its definition is
   `true` or a non-empty list. Otherwise each resource a population definition returns is an episode,
   identified by its id [src: FQM-8f1038a src/calculation/DetailedResultsBuilder.ts:445-453]
   [src: FQM-8f1038a src/calculation/DetailedResultsBuilder.ts:464-574].
2. **Population rules.** fqm-execution then clears populations that can't apply
   [src: FQM-8f1038a src/calculation/DetailedResultsBuilder.ts:269-319]:
   - not in the Initial Population: in no population;
   - not in the Denominator: not in the Denominator Exclusion, Denominator Exception, Numerator or
     Numerator Exclusion;
   - in the Denominator Exclusion: not in the Numerator, Numerator Exclusion or Denominator Exception;
   - not in the Numerator: not in the Numerator Exclusion; in the Numerator: not in the Denominator
     Exception.

   So a `"Numerator"` definition that's true for an excluded patient still counts as 0. Ratio
   measures treat the numerator and denominator independently, and continuous-variable measures clear
   the Measure Population Exclusion outside the Measure Population
   [src: FQM-8f1038a src/calculation/DetailedResultsBuilder.ts:165-267]. For episode-based groups the
   rules apply to each episode.
3. **Comparison.** MADiE compares a boolean population's truthiness with the expected value, so an
   unset expected value means "not met", and an episode-based population's episode count with the
   expected count, unset meaning 0 [src: MEASURE-18c8d4d src/…/api/CalculationService.ts:319-327]
   [src: MEASURE-18c8d4d src/…/api/CalculationService.ts:358-407]. A case passes when every expected
   population of every group does [src: MEASURE-18c8d4d src/…/api/CalculationService.ts:409-424]
   [src: MEASURE-18c8d4d src/…/api/CalculationService.ts:648-653].

Measure observations and stratifiers aren't checked: observation values come from functions the
results file doesn't include, and the script lists them as not checked. It also notes when the
measurement period came from the CQL default rather than `config.jsonc`.

## When VS Code and MADiE disagree

The two engines differ: MADiE runs fqm-execution on cql-execution, the JavaScript engine, and VS Code
runs the Java engine (see [test-case-content.md](test-case-content.md#how-madie-runs-test-cases)). With the
same CQL, data, value sets and measurement period, they should agree; when they don't, one of them
doesn't follow the CQL specification, and that's a conformance defect to report, not something to
work around in the measure.

1. **Rule out the inputs.** The same measurement period (MADiE's measure setting against
   `config.jsonc`), the same value set expansions, the same library versions, and no test logic that
   depends on `Patient.id` (MADiE replaces it at run time).
2. **Reduce it.** Find the definition whose value differs, then the smallest expression that still
   differs. Rewrite it with literals and selectors instead of retrieved data where possible: a conformance
   test can't use data.
3. **Decide what the specification requires**, with the `cql` skill's diagnosing steps, and check
   whether a test for it already exists in cqframework/cql-tests.
4. **Add a test to cqframework/cql-tests** demonstrating the discrepancy, as a pull request. Tests are
   XML, grouped by operator in `tests/cql/`, each with the expression and the output the specification
   requires [src: CQLTESTS-5747d2b tests/cql/CqlArithmeticFunctionsTest.xml:92-96]:

   ```xml
   <test name="AddIntegerOverflow" version="1.0">
     <!-- arithmetic overflow yields null per https://cql.hl7.org/09-b-cqlreference.html#add -->
     <expression>(maximum Integer) + 1</expression>
     <output>null</output>
   </test>
   ```

   Cite the specification section in a comment, say in the pull request which engine (and version)
   gives which result, and open an issue on the engine that's wrong, linking the test.
