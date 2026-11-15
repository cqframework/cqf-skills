# Test Configuration, Parameters and Results

Baseline: vscode-cql 1.0.0 with cql-language-server 5.0.0. Untagged statements hold at these versions only.
Sources: VSCQL-1.0.0, CQLLS-5.0.0, WIKI-c9e1023

Everything about `input/tests/config.jsonc`: which file is read, which keys exist and who reads them,
test case exclusions, result formats, and parameters. For where test cases themselves live, see
[user-guide.md](user-guide.md#test-cases-and-test-data).

## The file

- **Name.** `input/tests/config.jsonc`, or `input/tests/config.json` if there is no `.jsonc`. If both
  exist, `.jsonc` wins [src: VSCQL-1.0.0 src/helpers/cqlHelpers.ts:32-38]. The language server
  resolves the same pair for its own keys
  [src: CQLLS-5.0.0 ls/server/…/manager/JsonLibraryResolutionConfigProvider.kt:55-60].
- **Which folder.** The extension reads it from each project's `input/tests`
  [src: VSCQL-1.0.0 src/helpers/cqlHelpers.ts:52-59]. The language server reads it from the
  **VS Code workspace folder's** `input/tests`, so with several IG projects in subfolders of one
  workspace folder, the server's library-resolution keys come from the workspace folder, not the
  project [src: CQLLS-5.0.0 ls/server/…/service/FileContentService.kt:270-296]
  [src: WIKI-c9e1023 User-Guide.md:1041].
- **Comments** are allowed: the extension parses it as JSONC
  [src: VSCQL-1.0.0 src/helpers/cqlHelpers.ts:125], and the server's Jackson parser allows comments
  [src: CQLLS-5.0.0 ls/server/…/manager/JsonLibraryResolutionConfigProvider.kt:20].
- **A file that doesn't parse is ignored without a message in the editor**: the extension falls back
  to its defaults and only logs the error [src: VSCQL-1.0.0 src/helpers/cqlHelpers.ts:118-129].
- **Saving from the Configuration Editor removes comments** from a `.jsonc` file, after a
  confirmation prompt. If neither file exists, the editor creates `config.json`
  [src: VSCQL-1.0.0 src/views/configEditorWebview.ts:475-488] [src: VSCQL-1.0.0 src/helpers/cqlHelpers.ts:32-38].

## Keys

| Key | Read by | Default | Meaning |
| --- | --- | --- | --- |
| `testCasesToExclude` | extension | `[]` | Test cases to skip ([below](#excluding-test-cases)) |
| `parameters` | extension | none | Parameter values ([below](#parameters)) |
| `resultFormat` | extension | `"flat"` | `"flat"` or `"individual"` ([below](#result-formats)) |
| `flatResultsInSubfolder` | extension | `false` | Write the flat file into `results/<Lib>/` |
| `libraryResolution` | language server | patch-flexible | `"strict"`; any other value means patch-flexible |
| `unqualifiedCrossProjectSearch` | language server | `false` | Search other projects for unqualified includes |
| `projectSearchOrder` | language server | `[]` | Projects to search first; others follow alphabetically |
| `projectSearchExclude` | language server | `[]` | Projects never searched |

[src: VSCQL-1.0.0 src/helpers/cqlHelpers.ts:23-30]
[src: CQLLS-5.0.0 ls/server/…/manager/LibraryResolutionConfig.kt:3-10]
[src: CQLLS-5.0.0 ls/server/…/manager/JsonLibraryResolutionConfigProvider.kt:57-79]. The last four are
described in [library-resolution.md](library-resolution.md).

**The bundled schema knows only `testCasesToExclude` and `parameters`**, and forbids anything else
(`additionalProperties: false`) [src: VSCQL-1.0.0 schemas/cql-config.schema.json:6-32]. So VS Code
marks the other six keys "not allowed" in `config.jsonc`, though they work. The wiki lists this as a
known issue in 1.0.0 [src: WIKI-c9e1023 User-Guide.md:1125]. The schema is attached only to files
named `config.jsonc` [src: VSCQL-1.0.0 package.json:842-847], so `config.json` gets no checking at all.

## Excluding test cases

```jsonc
{
  "testCasesToExclude": [
    { "library": "MyMeasure", "testCase": "a1b2c3d4-e5f6-7890-abcd-ef1234567890", "reason": "Pending a terminology fix" }
  ]
}
```

Each entry needs `library`, `testCase` (the test case folder name) and `reason`
[src: VSCQL-1.0.0 schemas/cql-config.schema.json:8-20]. Excluded test cases are not run
[src: VSCQL-1.0.0 src/commands/execute-cql-file.ts:97-110].

## Result formats

| Format | Written to | Notes |
| --- | --- | --- |
| `flat` (default) | `input/tests/results/<Lib>.txt`, or `input/tests/results/<Lib>/<Lib>.txt` with `flatResultsInSubfolder` | One text log for all test cases; opens after the run; not shown in the CQL Explorer |
| `individual` | `input/tests/results/<Lib>/TestCaseResult-<testCase>.json` (`TestCaseResult-no-context.json` when there is no test case) | One JSON file per test case; shown under the test case in the CQL Explorer |

[src: VSCQL-1.0.0 src/helpers/cqlHelpers.ts:30] [src: VSCQL-1.0.0 src/commands/execute-cql-file.ts:247-251]
[src: VSCQL-1.0.0 src/commands/execute-cql-file.ts:412-418] [src: WIKI-c9e1023 User-Guide.md:452-541].
`<Lib>` is the `.cql` **file name**, not the name in the `library` declaration
[src: VSCQL-1.0.0 src/commands/execute-cql-file.ts:94]; the wiki says the two must match
[src: WIKI-c9e1023 User-Guide.md:391].

In the flat log, not every message is an error: look for `ERROR:` at the start of a message
[src: WIKI-c9e1023 User-Guide.md:472]. An individual result file holds `executedAt`, `libraryName`,
`testCaseName`, `testCaseDescription` (from a MeasureReport's `cqfm-testCaseDescription`, if any),
`parameters`, `results` (one per top-level `define`) and `errors`
[src: VSCQL-1.0.0 src/commands/execute-cql-file.ts:367-418] [src: WIKI-c9e1023 User-Guide.md:487-519].

Results are text, formatted by the server: `true`, `false`, `null`, a FHIR resource as
`Encounter(id=enc-1)`, a list in brackets, an interval with its brackets and bounds
[src: CQLLS-5.0.0 ls/server/…/command/CqlEvaluator.kt:345-372].

### When a definition fails at run time

Each test case is evaluated on its own, all of the library's definitions together. If any definition
throws a run-time error, that test case gets **no results at all**: its block in the flat log is a
single `Error=<message>` line (with `(cause: …)` when the root cause differs), and an individual result
file has an empty `results` and the message in `errors`. The other test cases still run
[src: CQLLS-5.0.0 ls/server/…/command/CqlEvaluator.kt:545-631]
[src: VSCQL-1.0.0 src/commands/execute-cql-file.ts:380-388]. So one failing definition hides every
other value for that case. To find it, read the message (the language server log has the full cause
chain), then comment definitions out, or debug the test case, until the rest run. Compiling cleanly
doesn't rule this out: an invalid interval, a cast that fails, or a value the data provider can't
build all compile and fail at run time.

## Parameters

Values for a library's `parameter` declarations, at three levels. The same name at a higher level
wins [src: VSCQL-1.0.0 src/helpers/parametersHelper.ts:12-22]:

```jsonc
{
  "parameters": [
    // global: every library
    { "name": "Measurement Period", "type": "Interval<DateTime>", "value": "Interval[@2024-01-01, @2025-01-01)" },
    // library: matched by name, and by version only if "version" is given
    {
      "library": "MyMeasure",
      "parameters": [ { "name": "Product Line", "type": "String", "value": "'HMO'" } ],
      // test case: keyed by the test case folder name
      "testCases": {
        "a1b2c3d4-e5f6-7890-abcd-ef1234567890": [ { "name": "Product Line", "type": "String", "value": "'Medicaid'" } ]
      }
    }
  ]
}
```

- **Matching.** A library block matches the `.cql` file name; its optional `version` must equal the
  version in the file's `library` declaration exactly; test case keys are folder names
  [src: VSCQL-1.0.0 src/helpers/parametersHelper.ts:31-64] [src: VSCQL-1.0.0 src/helpers/fileHelper.ts:47-49].
- **`name`** is the parameter name exactly as declared, case-sensitive, without CQL's double quotes:
  `Measurement Period`, not `"Measurement Period"` [src: WIKI-c9e1023 User-Guide.md:1133].
- **`type`** is one of `String`, `Integer`, `Decimal`, `Boolean`, `DateTime`, `Date`, `Time`,
  `Quantity`, `Interval<DateTime>`, `Interval<Date>` [src: VSCQL-1.0.0 schemas/cql-config.schema.json:44-57].
- **`value` is CQL, not JSON.** The server compiles each value as a CQL literal in a throw-away
  library and evaluates it [src: CQLLS-5.0.0 ls/server/…/command/CqlEvaluator.kt:181-233]. So
  strings need CQL single quotes (`"'HMO'"`), numbers and booleans none, and FHIR types such as
  `FHIR.Period` don't work [src: WIKI-c9e1023 User-Guide.md:1133-1180].
- **Dates.** When `type` contains `DateTime`, a bare date such as `@2024-01-01` is turned into
  `@2024-01-01T`; with `Date` types nothing is converted. The value must still match the parameter's
  declared CQL type [src: CQLLS-5.0.0 ls/server/…/command/CqlEvaluator.kt:181-233]
  [src: WIKI-c9e1023 User-Guide.md:1135].
- **One bad value drops them all.** If any value fails to compile or evaluate, the server logs
  `Failed to evaluate parameter values for [...]` and passes **no** configured parameters for that
  library, so every parameter falls back to its CQL default
  [src: CQLLS-5.0.0 ls/server/…/command/CqlEvaluator.kt:181-233]. The run doesn't fail. Check the
  language server log, and the `parameters` in an individual result file.

**Where a value came from.** In an individual result file each parameter has a `source`:
`config-global`, `config-library`, `config-test-case`, or `default` for a parameter the run didn't
supply, which used its CQL default. Defaults are listed after the configured ones and have no `type`
[src: VSCQL-1.0.0 src/model/parameters.ts:1] [src: VSCQL-1.0.0 src/commands/execute-cql-file.ts:396].

Debug sessions use the same merged parameters as execution
[src: VSCQL-1.0.0 src/commands/debug-test-case.ts:55-77].
