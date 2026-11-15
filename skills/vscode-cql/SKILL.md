---
name: vscode-cql
description: Sets up, uses and troubleshoots the vscode-cql VS Code extension (cqframework.cql) and the cql-language-server behind it, including Java requirements, project layout, the CQL Explorer, test cases and input/tests/config.jsonc, parameters, Execute CQL results, the CQL debugger, View ELM, include and package resolution, cql-options.json and logs. Use when someone runs or debugs CQL in VS Code, asks why the extension finds or ignores a file, or contributes to the extension or language server. Pinned to vscode-cql 1.0.0 and cql-language-server 5.0.0.
license: Apache-2.0
---

# vscode-cql

The `cqframework.cql` VS Code extension edits, runs and debugs CQL. It starts **cql-language-server**,
a Kotlin/JVM language server, and talks to it over LSP; compiling, executing, resolving includes and
debugging all happen in the server. This skill covers using both, and contributing to them. For the
CQL language use the `cql` skill. For building an IG with the IG Publisher use `ig-publisher`. For the
FHIR model info and FHIRHelpers use `cql-ig`.

## Versions

| Layer | Pinned at | Why it matters |
| --- | --- | --- |
| Extension | vscode-cql 1.0.0 (2026-11-09), the first 1.x release | Paths, commands, test discovery, results |
| Language server | cql-language-server 5.0.0 (2026-11-05), the one 1.0.0 downloads | Compiling, includes, packages, execution, debugger |
| CQL translator and engine | 5.5.0, in the server; clinical reasoning (cqf-fhir-cr) 4.13.0 | Diagnostics and results; differs from the IG Publisher's translator |
| Java | JDK 17 or later | The extension refuses to start the server without it |

The wiki (the project's own documentation) is pinned at its 1.0.0 update, but it is wrong or ahead of
the code in several places, so every behaviour here is cited to the code at those tags.

## When the User Has Another Version

The extension updates itself, and the server version follows the extension. **First find the
versions**: the Extensions view shows the extension's; the tooltip of the `CQL` status bar item shows
the language server, translator and engine versions. If they aren't 1.0.0 and 5.0.0:

1. Take the claim's `[src: …]` citation.
2. Read the same file at the user's version on GitHub;
   [SOURCES.md](resources/SOURCES.md#looking-up-a-citation-at-another-version) gives the URLs and the
   full paths behind each `…`. Find the code by content, as line numbers drift.
3. If it's unchanged, the claim holds. If it changed, answer from the code at their version and say
   it is read from source, not observed.

A weekly check in this repository reports new extension and server releases and wiki changes.

## Quick Reference

```text
<project>/                  a folder with ig.ini or input/cql (open it as the workspace folder)
  ig.ini                    needed for namespaces, packages and Execute CQL terminology
  input/cql/                libraries (file name = library name) and cql-options.json
  input/tests/<Type>/<Lib>/<patient-id>/   one folder per test case, one resource per file
  input/tests/config.jsonc  exclusions, parameters, result format, library resolution
  input/tests/results/      results
  input/vocabulary/valueset/
```

```jsonc
// input/tests/config.jsonc
{
  "parameters": [
    { "name": "Measurement Period", "type": "Interval<DateTime>", "value": "Interval[@2024-01-01, @2025-01-01)" }
  ],
  "resultFormat": "individual"   // default "flat"; VS Code wrongly flags it "not allowed"
}
```

- Run: right-click in a `.cql` file → Execute CQL. Debug: right-click → Debug Test Case.
- Logs: **CQL: Show CQL Language Server Logs** and **CQL: Show CQL Extension Logs**.
- Command IDs and where each command appears: [commands.md](resources/commands.md).

## Known Gotchas

- **The paths are fixed**: `input/cql`, `input/tests`, `input/vocabulary`. The IG's `path-binary`
  is never read: [user-guide.md](resources/user-guide.md#projects-and-folder-layout)
- **Only the first folder of a multi-root workspace is used**, and projects one level down get a
  warning: [user-guide.md](resources/user-guide.md#projects-and-folder-layout)
- **The CQL Explorer and Execute CQL find test cases differently** (first match versus every
  `<Lib>` folder), so their counts can differ: [user-guide.md](resources/user-guide.md#test-cases-and-test-data)
- **Bundles in test case folders are ignored**; one resource per file:
  [user-guide.md](resources/user-guide.md#test-cases-and-test-data)
- **Execute CQL has no value sets unless the project has an `ig.ini`**:
  [user-guide.md](resources/user-guide.md#terminology)
- **A parameter `value` is a CQL literal** (`"'HMO'"`), and one bad value silently drops every
  configured parameter for that run: [test-config.md](resources/test-config.md#parameters)
- **VS Code flags `resultFormat`, `libraryResolution` and four other valid keys as "not allowed"**;
  the bundled schema is incomplete: [test-config.md](resources/test-config.md#keys)
- **A `dev` dependency writes an empty `<pkg>#current` stub into `~/.fhir/packages`**, which other
  tools such as the IG Publisher then see. The wiki says this no longer happens; at 5.0.0 it does:
  [library-resolution.md](resources/library-resolution.md#fhir-packages-and-dev-dependencies)
- **`cql-options.json` isn't found for CQL files in sub-folders of `input/cql`** (by code read):
  [library-resolution.md](resources/library-resolution.md#compiler-options-cql-optionsjson)
- **After changing `ig.ini`, packages or `config.jsonc`, edit the `.cql` file or reload the window**:
  [library-resolution.md](resources/library-resolution.md#when-changes-are-noticed)
- **No CQL completion in the editor**; only three snippets and word suggestions:
  [user-guide.md](resources/user-guide.md#editing)
- **A hand-written `launch.json` needs `libraryUri` as the `.cql` file's `file:` URI, plus
  `libraryName` and `fhirVersion`**; the wiki's example has neither right. Prefer Debug Test Case:
  [debugging.md](resources/debugging.md#a-launchjson-of-your-own)
- **One run-time error in any definition wipes out that test case's results**: the case shows only
  `Error=…`, the other cases still run:
  [test-config.md](resources/test-config.md#when-a-definition-fails-at-run-time)
- **Expected values in a test case's MeasureReport aren't checked**, and its description shows only
  under the CQFM URL: [user-guide.md](resources/user-guide.md#test-cases-and-test-data)
- **The server's translator is 5.5.0; the IG Publisher's is its own** (4.9.0 in 3.0.4), so diagnostics
  and ELM can differ: [user-guide.md](resources/user-guide.md#viewing-elm)

## Supporting Files

For installing, Java, project layout, test cases, the CQL Explorer, editing, running, terminology, ELM and troubleshooting: see [user-guide.md](resources/user-guide.md)
For `config.jsonc` keys, exclusions, result formats, run-time errors and parameters: see [test-config.md](resources/test-config.md)
For include resolution, namespaces, packages and `dev` dependencies, `cql-options.json` and caching: see [library-resolution.md](resources/library-resolution.md)
For starting and using the debugger, and `launch.json`: see [debugging.md](resources/debugging.md)
For every command, view and debugger attribute, generated from `package.json`: see [commands.md](resources/commands.md)
For architecture, building, running a local server JAR, versions and branches: see [developer-guide.md](resources/developer-guide.md)
For the source IDs in `[src: …]` citations and how to read them online: see [resources/SOURCES.md](resources/SOURCES.md)

For maintainers only:
- Regenerate commands.md: `python3 scripts/gen_reference.py` (`--check` to verify)
- Cache the cited repositories: `scripts/fetch-sources.sh`; check citations: `python3 scripts/lint_skill_vscql.py`
- See whether a newer release is out and which citations it touches: `python3 scripts/check_release.py`
- Tests: `scripts/test_*.py`

## Not Yet Covered

The test case authoring features beyond clone and paste, and the wiki's UAT script. Behaviour marked
"by code read" (the `cql-options.json` sub-folder lookup, `ig.ini` change handling, `${file}` in
`launch.json` on Windows) hasn't been observed in a running extension.
