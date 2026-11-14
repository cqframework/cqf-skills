---
name: madie
description: Build, import, export and troubleshoot QI-Core test cases and measure CQL in MADiE, the CMS Measure Authoring Development Integrated Environment. Use for MADiE test case zips and the .madie file, test case bundles and their MeasureReport expected values, import errors, test case validation, test case series and titles, and what MADiE checks or rewrites in a measure's CQL. Each behaviour is cited to MADiE's source code.
license: Apache-2.0
---

# MADiE

MADiE (Measure Authoring Development Integrated Environment) is the CMS tool for writing electronic
clinical quality measures in CQL and testing them against test cases: FHIR bundles of synthetic patient
data with expected population results. This skill covers QI-Core measures (QI-Core 4.1.1 and 6.0.0).

Related skills: `cms-qmd` for how to write CMS measure CQL, `cql` for the language, `usqualitycore` for
US Quality Core measures, `vscode-cql` for running CQL and test cases locally.

## Versions

MADiE has no releases. Its repositories are developed on `develop` and deployed in sprints, and this
skill is pinned to `develop` commits of **2026-11-14**; production may be a sprint behind.

| Source | Pinned |
| --- | --- |
| madie-measure, measure-service, madie-fhir-service, packaging-utility, madie-java-models, madie-editor | `develop` commits, 2026-11-10 to 2026-11-13 |
| madie-models | `main`, 2026-10-29 |
| QI-Core | 4.1.1 and 6.0.0, the two QI-Core versions MADiE supports |
| eCQM `Status` and `QICoreCommon` libraries | the 2025 QI-Core 6.0.0 content |

## When MADiE Has Changed

Behaviour in the resource files is cited to MADiE's code in `[src: …]` markers, each naming a source,
a file and lines; [SOURCES.md](resources/SOURCES.md) has the commit for each source and how to read it
on GitHub. When MADiE behaves differently from what the skill says, or the user
reports an error message the skill doesn't mention:

1. Read the cited code on the repository's current `develop` (`main` for madie-models), finding it by
   content near the cited lines.
2. If it's unchanged, the skill's answer holds. If it has changed, answer from the current code and say
   that the answer is read from source, not from the skill.
3. Error messages are quoted in the skill as the code has them; search the repositories for a new
   message's text to find its rule.

## Quick Reference

**A test case zip that imports** (details in [test-case-files.md](resources/test-case-files.md)):

```text
tests.zip                    ← zip the contents, not a parent folder
  .madie                     ← required: [{patientId, title, series, description}]
  <patient UUID>/            ← folder name must be a UUID
    <anything>.json          ← exactly one bundle per folder
```

- The folder UUID becomes the test case's patient id. Import **updates** the test case with that
  patient id if the measure has one (description and JSON only), and creates one otherwise.
- A new test case's expected values come from a MeasureReport in the bundle: `group.id` ending in the
  group number (`Group_1`), populations in the measure's order with `measure-population` codes, `count`
  1 or 0 for a boolean basis. MADiE then removes the MeasureReport from the stored JSON.
- `testCaseId` in `.madie` is MADiE's internal id and isn't read on import.
- The Patient needs a `name` with `given` and `family`, or import fails, and an `identifier` and
  `gender`, which QI-Core requires, or the test case is invalid.

**What MADiE does to the bundle on save:** sets the Patient's id to the patient id, points every
relative `Patient/…` reference at it, changes `transaction` to `collection` and removes `request`,
rewrites existing `fullUrl`s to `https://madie.cms.gov/<Type>/<id>`, and drops the MeasureReport.

**What export produces:** `{eCQM title}-v{version}-{series}-{title}.json` in a folder per patient id, a
`README.txt` and `.madie`, transaction or collection bundles with **new random ids for every resource
except the Patient**, and a MeasureReport with the `cqm-testcase` profile.

**Validation** (details in [test-case-content.md](resources/test-case-content.md)): every resource needs
a unique id; missing `meta.profile` is a warning; a reference that doesn't resolve within the bundle
drops that resource from execution (an error if it's in the Patient); profiles are validated against
the measure's QI-Core version. A test case with errors can't run or be exported.

**CQL** (details in [measure-cql.md](resources/measure-cql.md)): MADiE rewrites the `library` line to
the measure's name and version, forces `called FHIRHelpers`, strips value set versions, and requires
`http://cts.nlm.nih.gov/fhir/ValueSet/<OID>` value sets and a `using` that matches the model. Library
names are `^[A-Z][a-zA-Z0-9]*$`, at most 64 characters; versions are `x.y.zzz`.

## Known Gotchas

- **A parent folder in the zip** makes every entry invalid: "Unable to find any valid test case json".
- **No `.madie` file:** "Zip file is in an incorrect format…". Old exports (before June 2024) lack it.
- **Re-importing an exported zip into the same measure updates, not duplicates**, because the patient
  ids match. Title, series and expected values aren't changed by an update. To copy test cases, change
  the folder UUIDs, and change the titles too, since title and series must be unique in a measure.
- **Expected values silently missing** after import: the MeasureReport's groups or populations don't
  match the measure's. The import still succeeds, with a warning.
- **Resource ids change on every export**, so references to non-Patient ids outside the bundle break.
- **`urn:uuid:` references** never resolve in MADiE; the referencing resource is dropped from
  execution. Use `<Type>/<id>`.
- **Special characters in titles or series** stop export. Use letters, digits and `-`; the browser
  rejects `_` too.
- **Descriptions are lost** when a zip without `.madie` is imported: the fallback reads the old CQFM
  extension URL, and MADiE exports the CQM one.
- **Profile names differ between QI-Core 4.1.1 and 6.0.0** (Condition and Observation especially). Use
  the profiles of the measure's model.
- **MADiE runs test cases with a different engine** from VS Code (fqm-execution, the JavaScript
  engine), and with the Patient's `id` set to the test case's internal id. Logic that passes locally can
  fail in MADiE: don't match on `Patient.id` or resource ids; give test resources identifier keys.
- **A `code` from a code system MADiE doesn't have** stops the CQL from being accepted, even though it
  compiles locally.
- **Series names such as `IPPPass` or `NUMERFail`** are a naming convention, not something MADiE knows.
  The expected values are what count.

## Supporting Files

| File | Contents |
| --- | --- |
| [resources/test-case-files.md](resources/test-case-files.md) | The export zip, the `.madie` file, import rules and errors, what MADiE rewrites, the MeasureReport and expected values, titles and series |
| [resources/test-case-content.md](resources/test-case-content.md) | Validation, ids and references, how MADiE runs test cases, QI-Core profiles by version, notes on the resources measures test |
| [resources/measure-cql.md](resources/measure-cql.md) | Library names and versions, what MADiE rewrites or rejects in CQL (including codes), the default CQL template, testing a shared library with a Cohort measure |
| [resources/SOURCES.md](resources/SOURCES.md) | The pinned sources and how to read a citation on GitHub |
| [scripts/check_test_cases.py](scripts/check_test_cases.py) | Checks a test case folder or zip against MADiE's import rules before uploading |
| [scripts/check_release.py](scripts/check_release.py) | For maintainers: reports cited code that has changed on `develop` |

To check test cases before importing them:

```bash
python3 scripts/check_test_cases.py path/to/tests.zip      # or a folder laid out like the zip
```
