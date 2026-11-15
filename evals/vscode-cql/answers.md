# vscode-cql Skill Test Questions: Answer Key

Expected answers for [questions.md](questions.md). Don't give this file to an agent under test.

Facts are as the `vscode-cql` skill records them for vscode-cql 1.0.0 and cql-language-server 5.0.0,
from the code at those tags. Several contradict the project wiki; those are marked, because an agent
without the skill will usually repeat the wiki. "Skill" says where the skill covers it.

## Setup

### SU-01. Java

- **Expected:** a **JDK** (with `javac`), version **17 or later**. It looks in `JDK_HOME`,
  `JAVA_HOME`, `PATH`, the Windows registry and common install folders, preferring them in that order,
  and stops with "Java 17 or more recent is required…" if none qualifies.
- **Pass if:** JDK 17+ and at least `JAVA_HOME`/`JDK_HOME`.
- **Fail if:** Java 11 (the old summary), or "any JRE".
- **Skill:** `resources/user-guide.md` (Installing and starting).

### SU-02. Two projects

- **Expected:** the extension scans only the **first** workspace folder of a multi-root workspace.
  Open each IG in its own window, or put both under one folder (they're then found one level down,
  with a warning each).
- **Pass if:** it names the first-folder-only behaviour.
- **Skill:** `resources/user-guide.md` (Projects and folder layout).

## Projects and test data

### PL-01. A different CQL folder

- **Expected:** no. The paths are hard-coded: `<root>/input/cql`, `input/tests`, `input/vocabulary`.
  Nothing reads `path-binary`. Move the CQL to `input/cql` and point `path-binary` there, which also
  suits the IG Publisher.
- **Pass if:** no, with the fixed path.
- **Fail if:** it says the extension follows `path-binary`.
- **Skill:** `resources/user-guide.md`.

### PL-02. A Bundle of test data

- **Expected:** Bundles in test case folders are ignored: the server keeps only resources of the type
  it's searching for and doesn't unpack a Bundle. Put each resource in its own file. (The wiki says
  Bundles are supported in one place.)
- **Pass if:** Bundles are ignored; one resource per file.
- **Skill:** `resources/user-guide.md` (Test cases and test data).

### PL-03. File names

- **Expected:** the server detects the naming style; with `<Type>-<id>.json` files present, it
  accepts only type-prefixed files, so `obs-1.json` is silently skipped. Rename it
  `Observation-obs-1.json`.
- **Pass if:** mixed naming, with the type-prefixed rule.
- **Skill:** `resources/user-guide.md` (File names).

### PL-04. Different counts

- **Expected:** there is more than one `ScreeningLogic` folder under `input/tests`. The Explorer takes
  the first match (`input/tests/<Type>/<Lib>`, then `input/tests/<Lib>`, then one level deeper), while
  Execute CQL runs every folder named `<Lib>` anywhere under `input/tests`. Keep one folder.
- **Pass if:** two discovery rules, several `<Lib>` folders.
- **Skill:** `resources/user-guide.md`.

## Configuration and parameters

### CF-01. "Not allowed"

- **Expected:** no; the setting works. The bundled schema lists only `testCasesToExclude` and
  `parameters` and forbids others, so VS Code flags `resultFormat`, `flatResultsInSubfolder` and the
  four library-resolution keys. The wiki lists it as a known issue.
- **Pass if:** it says the key is valid and the schema is incomplete.
- **Fail if:** it tells them to remove or rename the key.
- **Skill:** `resources/test-config.md` (Keys).

### CF-02. Where are the results?

- **Expected:** by default (`flat`), one text file per library, `input/tests/results/<Lib>.txt`. Set
  `"resultFormat": "individual"` in `input/tests/config.jsonc` for
  `input/tests/results/<Lib>/TestCaseResult-<testCase>.json`. There's no VS Code setting for it.
- **Pass if:** flat is the default and `resultFormat` in `config.jsonc`.
- **Fail if:** individual is the default (the old summary), or a VS Code setting.
- **Skill:** `resources/test-config.md` (Result formats).

### CF-03. Only an error

- **Expected:** one definition threw a run-time error (here building an invalid interval) for that
  test case. Each case is evaluated as a whole, so an error in any definition replaces all of that
  case's results with the single `Error=` line; other cases are unaffected. Find the definition from
  the message (the language server log has the cause chain), by commenting definitions out or
  debugging the test case, and fix it (for intervals, guard computed bounds).
- **Pass if:** one definition's run-time error hides the whole case.
- **Fail if:** it says the other thirty-nine definitions returned nothing because they're wrong.
- **Skill:** `resources/test-config.md` (When a definition fails at run time).

### CF-04. Expected values

- **Expected:** it doesn't. Extension 1.0.0 reads a MeasureReport's expected populations (and its
  description, from the CQFM extension only) but never compares them with the results. Compare them
  yourself, for example with the `madie` skill's `check_results.py`, which also applies the measure's
  population rules.
- **Pass if:** no comparison at 1.0.0.
- **Fail if:** it describes a pass/fail view in the extension.
- **Skill:** `resources/user-guide.md` (Test cases and test data).

### PA-01. An unquoted string

- **Expected:** values are CQL literals; `HMO` is parsed as an identifier and fails. When any value
  fails, the server logs `Failed to evaluate parameter values for [...]` and passes **no** configured
  parameters, so every parameter, Measurement Period included, falls back to its CQL default. Use
  `"'HMO'"`.
- **Pass if:** CQL single quotes, and all parameters dropped.
- **Partial if:** only the quoting.
- **Skill:** `resources/test-config.md` (Parameters).

### PA-02. Dates

- **Expected:** `"type": "Interval<DateTime>"`, `"value": "Interval[@2024-01-01T00:00:00.000Z,
  @2025-01-01T00:00:00.000Z)"`, or with bare dates, `Interval[@2024-01-01, @2025-01-01)`, which the
  server converts to DateTime because the type contains `DateTime`. Not `Interval<Date>`.
- **Pass if:** `Interval<DateTime>` and a half-open (or 2024-12-31 closed) 2024 interval.
- **Skill:** `resources/test-config.md`.

## Terminology and libraries

### TE-01. Value sets not found

- **Expected:** Execute CQL loads value sets from the `input/vocabulary` of workspace projects that
  have an `ig.ini`; with none, no value sets are available. Add an `ig.ini` (with its IG resource).
- **Pass if:** it names the missing `ig.ini`.
- **Skill:** `resources/user-guide.md` (Terminology).

### LR-01. Versions

- **Expected:** yes by default: patch-flexible accepts the same major.minor with a patch ≥ the
  requested one. With `"strict"`, no: only `Helpers-1.0.0.cql` would match.
- **Pass if:** both halves right.
- **Skill:** `resources/library-resolution.md`.

### LR-02. Sharing a library

- **Expected:** a namespace-qualified include, using the other project's packageId:
  `include example.fhir.common.SharedLibrary version '…'`. `common-ig` needs an `ig.ini` with that
  packageId and a canonical; it's found in the workspace folder or one level down. Unqualified
  cross-project search exists (`unqualifiedCrossProjectSearch`) but is off by default and not
  recommended.
- **Pass if:** namespace-qualified include and the `ig.ini` requirement.
- **Skill:** `resources/library-resolution.md` (Other projects).

### LR-03. The package cache

- **Expected:** yes. At 5.0.0, for a `dev` dependency, the language server writes a stub package
  (only `package.json`) to `~/.fhir/packages/<packageId>#current`, which other tools then see. Remove
  `~/.fhir/packages/example.fhir.common#current` with no tool running, leaving `*.lock` files. The wiki
  says this stopped happening; at 5.0.0 it hasn't.
- **Pass if:** it identifies the stub and how to remove it.
- **Fail if:** it says the extension never writes to the package cache (the wiki's claim).
- **Skill:** `resources/library-resolution.md` (FHIR packages and `dev` dependencies).

### LR-04. Stale includes

- **Expected:** reload the window (restart the language server). By the code, `ig.ini` and IG changes
  don't reliably invalidate the cached package context or compiled results; editing the `.cql` file
  may not be enough here.
- **Pass if:** reload or restart.
- **Partial if:** only "touch the .cql file".
- **Skill:** `resources/library-resolution.md` (When changes are noticed).

## Debugging and editing

### DB-01. A launch.json

- **Expected:** `libraryUri` must be the `.cql` **file** as a `file:` URI (not the folder, and
  `${file}` gives a plain path); `fhirVersion` (`R4`) is required; for patient data, `testCaseUri`
  (the test case folder's `file:` URI) is needed alongside `testCaseName`. Easier: right-click in the
  editor, or on a test case in the CQL Explorer, and choose **Debug Test Case**, which builds the
  configuration.
- **Pass if:** at least the file URI and `fhirVersion`, plus Debug Test Case.
- **Skill:** `resources/debugging.md`.

### ED-01. Completion

- **Expected:** no; the language server doesn't provide completion for `.cql` files. Only three
  snippets (`define func`) and VS Code's word-based suggestions. The Debug Console does complete
  expression names.
- **Pass if:** no server completion.
- **Skill:** `resources/user-guide.md` (Editing).

## Versions

### VR-01. A newer extension

- **Expected:** the skill's answer (ignored) is for 5.0.0. Check the cited code,
  `IgStandardRepository.kt` near the cited lines, at the `v5.2.0` tag of cql-language-server on
  GitHub (full path in SOURCES.md), finding it by content. If unchanged, the answer holds; otherwise
  answer from 5.2.0's code and say it's read from source.
- **Pass if:** it treats the answer as version-specific and checks the server code at 5.2.0.
- **Fail if:** it states the 5.0.0 behaviour as fact for 5.2.0, or reads the wiki only.
- **Skill:** SKILL.md (When the User Has Another Version).

## Task

### TK-01. Set up a project for the extension

Run `python grade_project.py <answer>/tk-01`. It checks: an `ig.ini`; `input/cql/WeightCheck.cql`
with a matching `library` name; exactly one `WeightCheck` test folder; one resource per file, named
`<Type>-<id>.json`, no Bundles, patient ids equal to folder names and references to them;
`config.jsonc` that parses, with `resultFormat: individual`, a bare `Measurement Period` name, valid
CQL literal values of matching types, and an exclusion with `library`, `testCase` and `reason`; the
value set in `input/vocabulary` by `url`, expanded or a simple code list; and a `cql` launch
configuration with the file URI, `libraryName`, `fhirVersion`, `testCaseName` and `testCaseUri`.

- **Pass if:** every check passes. **Partial if:** one fails.
- **Reference:** [reference/tk-01/](reference/tk-01/). Its CQL translates with no errors.
