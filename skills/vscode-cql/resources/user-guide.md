# User Guide: Projects, Editing, Running and Troubleshooting

Baseline: vscode-cql 1.0.0 with cql-language-server 5.0.0. Untagged statements hold at these versions only.
Sources: VSCQL-1.0.0, CQLLS-5.0.0, WIKI-030e98c

For exact command names see [commands.md](commands.md); for `config.jsonc` see
[test-config.md](test-config.md); for includes and packages see
[library-resolution.md](library-resolution.md); for the debugger see [debugging.md](debugging.md).

## Installing and starting

- Install **Clinical Quality Language** (`cqframework.cql`) from the VS Code Marketplace. It needs
  VS Code 1.90 or later (see [commands.md](commands.md#the-extension)) and a **JDK 17 or later**
  [src: WIKI-030e98c User-Guide.md:36-46].
- It activates when the workspace contains a `.cql` file, then downloads the language server JAR
  (`cql-ls-server` 5.0.0) from Maven Central once; progress shows in the status bar
  [src: VSCQL-1.0.0 src/java-support/javaServiceInstaller.ts:66-81].
- **Finding Java.** It looks in `JDK_HOME`, `JAVA_HOME`, `PATH`, the Windows registry and common
  install folders, preferring them in that order, and needs a JDK (with `javac`), not just a JRE. If
  none is 17 or later, it stops with "Java 17 or more recent is required…" and a link to download one
  [src: VSCQL-1.0.0 src/java-support/findJavaRuntimes.ts:29-33]
  [src: VSCQL-1.0.0 src/java-support/requirements.ts:58-74]
  [src: VSCQL-1.0.0 src/java-support/requirements.ts:95-107].
- **The status bar item** (lower right) shows `CQL` with a spinner, a check or an error; when ready,
  its tooltip lists the extension, translator, engine, clinical reasoning and language server versions
  [src: VSCQL-1.0.0 src/statusBar.ts:33-75]. CQL commands appear only once the server is connected
  [src: WIKI-030e98c User-Guide.md:381].

## Projects and folder layout

**What counts as a project.** A folder with an `ig.ini` file or an `input/cql` folder. The extension
checks the workspace folder; if that isn't a project, it checks each immediate sub-folder and warns
in the Problems panel for each one it finds that way. If none is found, the workspace folder is used
anyway [src: VSCQL-1.0.0 src/model/igLayoutDetector.ts:56-92]
[src: VSCQL-1.0.0 src/model/cqlSolution.ts:42-48]. **Only the first folder of a multi-root workspace
is scanned** [src: VSCQL-1.0.0 src/model/cqlSolution.ts:42-43].

**Fixed folders.** Every path is relative to the project root and hard-coded
[src: VSCQL-1.0.0 src/model/cqlProject.ts:230-232] [src: VSCQL-1.0.0 src/helpers/cqlHelpers.ts:52-65]:

```text
<project>/
  ig.ini                     optional; needed for namespaces, packages and terminology (below)
  input/
    cql/                     CQL libraries, and cql-options.json
    tests/                   test cases, config.jsonc
      results/               execution results
    vocabulary/valueset/     ValueSets
    vocabulary/codesystem/
```

**The IG Publisher's `path-binary` and `path-resource` are not read**: no file in the extension's
`src/` mentions them (searched at VSCQL-1.0.0). An IG whose `path-binary` isn't `input/cql` can't be
used as is. The IG Publisher, for its part, compiles CQL only from the folders `path-binary` names, and
`input/tests` means nothing to it [src: WIKI-030e98c User-Guide.md:243-281]. A layout that works for
both: CQL in `input/cql` with `path-binary` = `input/cql`, tests in `input/tests`.

**Library names come from file names.** Test folders, parameter blocks and result files use the `.cql`
file name, not the `library` declaration, so keep them equal
[src: VSCQL-1.0.0 src/commands/execute-cql-file.ts:94] [src: WIKI-030e98c User-Guide.md:391]. The CQL
Explorer lists only the `.cql` files directly in `input/cql`
[src: VSCQL-1.0.0 src/model/cqlProject.ts:236-238].

## Test cases and test data

Each test case is a folder named with the patient's id, holding that patient's FHIR resources. There
are **two different lookups** for a library's test cases:

| Used by | Looks in | Takes |
| --- | --- | --- |
| CQL Explorer (and Debug Test Case) | `input/tests/<ResourceType>/<Lib>` for Library, Measure, PlanDefinition, Questionnaire or ActivityDefinition; else `input/tests/<Lib>`; else `input/tests/<any folder>/<Lib>` (not `results`) | The first match |
| Execute CQL | Every folder named `<Lib>` anywhere under `input/tests` | All of them; skips sub-folders named `shared` and excluded test cases |

[src: VSCQL-1.0.0 src/model/igLayoutDetector.ts:107-162] [src: VSCQL-1.0.0 src/model/testCase.ts:35-47].
So with several `<Lib>` folders, Execute CQL can run more test cases than the Explorer shows. Keep one
folder per library, preferably `input/tests/<ResourceType>/<Lib>/`; the other two places produce
warnings in the Problems panel.

**Resources** in a test case folder or its sub-folders are read as JSON, XML or RDF. **Bundles are
ignored**: the server keeps only resources of the type it's searching for, and a Bundle isn't
unpacked [src: CQLLS-5.0.0 ls/server/…/repository/ig/standard/IgStandardRepository.kt:51-56]
[src: CQLLS-5.0.0 ls/server/…/repository/ig/standard/IgStandardRepository.kt:310-330]. Put each
resource in its own file. Every resource must refer to the patient whose id is the folder name
[src: WIKI-030e98c User-Guide.md:574-598].

**File names: `<ResourceType>-<id>.json` or `<id>.json`, never both.** The server looks at the folder
layout once and, if it finds files named with a resource type prefix, accepts only such files for
each type; files named by id alone are then **silently skipped**
[src: CQLLS-5.0.0 ls/server/…/repository/ig/standard/IgStandardConventions.kt:70-115]
[src: CQLLS-5.0.0 ls/server/…/repository/ig/standard/IgStandardRepository.kt:310-314]. The wiki states
the rule as "the extension won't return results" [src: WIKI-030e98c User-Guide.md:604-624]. Prefer
`<ResourceType>-<id>.json`: the extension's **Clone Test Case** and **Paste - Update References**
take the id from after the first `-` in the file name, so they work reliably only with those names
[src: VSCQL-1.0.0 src/cql-explorer/idReplacer.ts:25-35]. Clone gives the copy a new folder UUID and
new ids, rewritten in file names and content [src: VSCQL-1.0.0 src/cql-explorer/testCaseCloner.ts:14-52].

**A MeasureReport in a test case folder** is read by the extension, not the CQL: a file whose name
starts with `MeasureReport` gives the case's description and expected population counts
[src: VSCQL-1.0.0 src/model/testCase.ts:72-101]. Two limits at 1.0.0:

- The description is read only from the CQFM extension, `cqfm-testCaseDescription`
  [src: VSCQL-1.0.0 src/model/testCase.ts:113-123]. MADiE and the CQM IG write `cqm-testCaseDescription`,
  so a MADiE export's descriptions don't show.
- The expected counts are parsed but **never compared** with the results; nothing reports pass or
  fail against them. The `madie` skill's `check_results.py` does that comparison, with the measure's
  population rules.

To test a library itself (not a measure) with CQL, see the `cql` skill's testing guide.

## The CQL Explorer

A tree in the Explorer sidebar (not its own activity bar icon): projects, libraries, test cases,
resources, and individual results [src: WIKI-030e98c User-Guide.md:54-191]. From it you can run all
or selected libraries or test cases, debug a test case, view ELM, open a test case's resources, clone,
delete or paste test cases and resources, filter and sort, and open the Configuration Editor (the gear
button). The full list, with where each command appears, is in [commands.md](commands.md#commands).

- **Fix References** is registered but in no menu at 1.0.0, so it can't be run from the UI, although
  the wiki lists it on the resource menu [src: VSCQL-1.0.0 package.json:424-425]
  [src: WIKI-030e98c User-Guide.md:174].
- **Not visible?** It's inside the Explorer sidebar: right-click the sidebar header and tick CQL
  Explorer, or run `View: Open View` → CQL Explorer, or scroll down; and open the project's root folder
  [src: WIKI-030e98c User-Guide.md:193-211].

## Editing

- **Diagnostics, hover** (including the result type of an expression and of `let` aliases),
  **Go to Definition** (F12, also into included libraries), **Find All References** (Shift+F12),
  **document symbols** (Ctrl+Shift+O) and **Format Document** come from the language server
  [src: CQLLS-5.0.0 ls/server/…/service/CqlTextDocumentService.kt:51-61]
  [src: WIKI-030e98c User-Guide.md:312-373].
- **No CQL completion.** The server doesn't offer completion for `.cql` files
  [src: CQLLS-5.0.0 ls/server/…/service/CqlTextDocumentService.kt:51-61]. Suggestions come from three
  snippets (`define func` for MostRecent, IssuedWithin and PerformedWithin)
  [src: VSCQL-1.0.0 snippets.json:3-23] and VS Code's word-based suggestions, which can be turned off
  with `"[cql]": { "editor.wordBasedSuggestions": "off" }` in settings
  [src: WIKI-030e98c User-Guide.md:334-353]. The Debug Console does complete expression names.
- The extension contributes **no VS Code settings** (see [commands.md](commands.md#the-extension));
  per-project behaviour is in `input/tests/config.jsonc`.
- Compiler options come from `input/cql/cql-options.json`; see
  [library-resolution.md](library-resolution.md#compiler-options-cql-optionsjson).

## Running CQL

- **One library:** right-click in the editor → Execute CQL → **Execute CQL** (all test cases) or
  **Execute CQL - Select Test Cases**. Or use the library's commands in the CQL Explorer.
- **Several libraries:** **CQL: Execute CQL - Select Libraries** from the Command Palette or the CQL
  Explorer toolbar, or **Execute All Libraries** on a project node.
- Execution reads files **from disk**: save first [src: WIKI-030e98c User-Guide.md:450].
- A library with no test cases is still run once, with no patient context
  [src: VSCQL-1.0.0 src/commands/execute-cql-file.ts:112-114].
- The FHIR version comes from the library's `using FHIR` (or `using QICore`) declaration; if there is
  none, it runs as R4 with the message "Unable to determine version of FHIR used. Defaulting to R4."
  [src: VSCQL-1.0.0 src/commands/execute-cql-file.ts:116-125].
- Results go to `input/tests/results/` as one text file per library (default) or one JSON file per
  test case; see [test-config.md](test-config.md#result-formats).

[src: WIKI-030e98c User-Guide.md:375-450] [src: VSCQL-1.0.0 src/commands/execute-cql-file.ts:412-418].

## Terminology

When executing, value sets come from the `input/vocabulary` folders (read recursively, JSON or XML) of
**every project in the workspace that has an `ig.ini`**, matched by `url`; the first match wins. With no
`ig.ini` anywhere, no value sets are available at all
[src: CQLLS-5.0.0 ls/server/…/command/CqlEvaluator.kt:760-768]
[src: CQLLS-5.0.0 ls/server/…/repository/ig/standard/FederatedTerminologyRepo.kt:16-74]
[src: CQLLS-5.0.0 ls/server/…/manager/LibraryResolutionManager.kt:58-65]. The per-library terminology
folder the extension sends doesn't change that
[src: CQLLS-5.0.0 ls/server/…/command/CqlEvaluator.kt:756].

A value set with an `expansion` is used as is. A simple extensional one (a list of codes) is expanded
naively; anything more complex needs a precomputed `expansion`
[src: CQLLS-5.0.0 ls/server/…/repository/ig/standard/IgStandardRepository.kt:44-48] [src: CQLLS-5.0.0 ls/server/…/command/CqlEvaluator.kt:422-432]
[src: WIKI-030e98c User-Guide.md:1069-1102]. Value sets from package dependencies aren't used: copy
them into `input/vocabulary`, for example under an `external` sub-folder
[src: WIKI-030e98c User-Guide.md:1104].

## Viewing ELM

Right-click in the editor → View ELM → **JSON**, **XML**, **AST** (a text tree) or **AST (Split)**
(CQL and AST side by side, linked, refreshed on save). The CQL Explorer's library menu has JSON, XML
and AST [src: WIKI-030e98c User-Guide.md:884-922]. The ELM comes from the language server's translator
(CQL 5.5.0), with locators, result types and annotations always on
[src: CQLLS-5.0.0 ls/server/…/manager/CompilerOptionsManager.kt:53-58]; it can differ from the ELM an IG
Publisher build produces with its own translator.

## Logs and troubleshooting

| Command | Opens |
| --- | --- |
| CQL: Show CQL Language Server Logs | `cql-ls.log`, in VS Code's log folder for the extension (with `gc.log`) |
| CQL: Show CQL Extension Logs | The extension's own log, `language-support-for-cql.log.<date>.log`, rotated daily |
| CQL: Show CQL Extension and Language Server Logs | Both, side by side |

[src: VSCQL-1.0.0 src/cql-language-server/languageServerStarter.ts:72-75]
[src: VSCQL-1.0.0 src/extension.ts:89-90]. The server log rolls daily or at 10 MB and keeps 7 days
[src: CQLLS-5.0.0 ls/server/src/main/resources/logback.xml:7-29].

| Symptom | Likely cause |
| --- | --- |
| "Java 17 or more recent is required" | No JDK 17+ found in `JDK_HOME`, `JAVA_HOME`, `PATH` or the usual places; install one, or point `JAVA_HOME` at it, and reload |
| `spawn /undefined/bin/java ENOENT` | `JAVA_HOME` not visible to VS Code; reported by the wiki with version-manager fixes (SDKMAN!, jenv, asdf, mise) [src: WIKI-030e98c User-Guide.md:1196-1205]. At 1.0.0 a missing JDK normally fails earlier with the message above |
| No CQL commands in menus | The server isn't connected yet; check the status bar item and the server log |
| A parameter seems ignored | One value failed to evaluate, so all configured parameters were dropped; see [test-config.md](test-config.md#parameters) |
| Value sets not found when executing | No `ig.ini` in the project, or the value set's `url` doesn't match; see Terminology above |
| Include or package changes not picked up | Edit the `.cql` file, or reload the window; see [library-resolution.md](library-resolution.md#when-changes-are-noticed) |
| Test case counts differ between the Explorer and a run | Several `<Lib>` folders under `input/tests`; see Test cases above |
| A malformed `config.jsonc` has no effect | The extension ignores a file it can't parse; check the extension log |
