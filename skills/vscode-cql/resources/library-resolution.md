# Library Resolution, Packages and Compiler Options

Baseline: cql-language-server 5.0.0 (with vscode-cql 1.0.0). Untagged statements hold at these versions only.
Sources: CQLLS-5.0.0, VSCQL-1.0.0, WIKI-030e98c

How the language server finds the library an `include` names, what it does with FHIR packages, which
compiler options it uses, and when it notices changes. All of this is in the language server; the
extension only passes file locations.

The wiki's developer notes on this topic were written against language server 4.6.0-SNAPSHOT
[src: WIKI-030e98c developer-notes/CQL-Library-Resolution.md:3-11]. Where 5.0.0 differs, this page
follows the code.

## Where an include is looked for

In order, first match wins [src: CQLLS-5.0.0 ls/server/…/provider/FederatedLibrarySourceProvider.kt:16-53]
[src: CQLLS-5.0.0 ls/server/…/manager/CqlCompilationManager.kt:179-197]
[src: CQLLS-5.0.0 ls/server/…/manager/LibraryProviderRegistrar.kt:28-34]:

1. **Local `.cql` files** (below).
2. **Libraries in the IG's FHIR packages**, the `dependsOn` packages of the project's IG, from
   `~/.fhir/packages`.
3. **FHIRHelpers built into the translator**: versions 1.0.2, 1.6, 1.8, 3.0.0, 3.0.1, 3.2.0, 4.0.0 and
   4.0.1, from the `quick` 5.5.0 artifact. Exact versions only; no R4B or R5 FHIRHelpers
   [src: CQLLS-5.0.0 pom.xml:97-101] [src: CQLLS-5.0.0 ls/server/…/manager/LibraryProviderRegistrar.kt:33].

Execute CQL builds its own engine but keeps the same order
[src: CQLLS-5.0.0 ls/server/…/command/CqlEvaluator.kt:478-491]. When the same library is in several
places, the first is used and the others only get a log warning
[src: CQLLS-5.0.0 ls/server/…/provider/FederatedLibrarySourceProvider.kt:67-74].

## Local files

A breadth-first search, so a shallower file beats a deeper one
[src: CQLLS-5.0.0 ls/server/…/service/FileContentService.kt:144-227]:

| Tier | Searched | When |
| --- | --- | --- |
| 1 | The folder of the library doing the `include`, and its sub-folders | Always |
| 2 | `input/cql` of the **VS Code workspace folder** | Always (skipped if tier 1 is that folder) |
| 3 | `input/cql` of the other projects that have an `ig.ini` | Only with `unqualifiedCrossProjectSearch: true` |

Two passes: **exact version** through all tiers first, then a **compatible version** through all
tiers. So `input/cql/Helper-1.0.0.cql` beats `Helper-1.0.1.cql` next to the including library
[src: CQLLS-5.0.0 ls/server/…/service/FileContentService.kt:304-405] [src: WIKI-030e98c User-Guide.md:948-955].

- File names are `<Library>-<version>.cql` or `<Library>.cql`, matched case-insensitively. A hyphen in
  the library name is fine: the version is the last hyphen-separated part that parses as a version.
- At one depth, the newest compatible file wins, and a versioned file beats an unversioned one.
- An `include` without a version takes the newest file at the shallowest depth.

### Version matching: `libraryResolution`

Set in `input/tests/config.jsonc` (see [test-config.md](test-config.md#keys))
[src: CQLLS-5.0.0 ls/server/…/manager/JsonLibraryResolutionConfigProvider.kt:57-79]:

| Value | Compatible means |
| --- | --- |
| anything but `"strict"`, or absent: patch-flexible | Same major.minor, patch ≥ the requested one: `FHIRHelpers-4.0.1.cql` satisfies `version '4.0.0'`. An unversioned file matches any version |
| `"strict"` | Only the exact `<Library>-<version>.cql` when the include gives a version; the compatible pass is skipped |

### Other projects

**Namespace-qualified includes** are the way to use another project's library. The namespace is the
other project's `packageId`:

```cql
include example.fhir.common.SharedLogic version '1.0.0'
```

The server indexes every `ig.ini` project in the workspace folder or one level down, by `packageId` and
canonical, and sends a qualified include straight to that project's `input/cql`, always
patch-flexible [src: CQLLS-5.0.0 ls/server/…/manager/LibraryResolutionManager.kt:126-185]. A project
without an `ig.ini` (or whose `ig.ini` has no `[IG]` section) can't be found this way. An unknown
namespace isn't an error in the server: the include falls through to the packages and FHIRHelpers, and
any error comes from the translator [src: CQLLS-5.0.0 ls/server/…/service/FileContentService.kt:156-168].
If two projects share a canonical, the first wins and a warning is logged
[src: CQLLS-5.0.0 ls/server/…/manager/LibraryResolutionManager.kt:74-94].

**Unqualified includes** search other projects only with `unqualifiedCrossProjectSearch: true`
(tier 3). `projectSearchOrder` lists folder names to search first, the rest follow alphabetically;
`projectSearchExclude` lists folder names never searched
[src: CQLLS-5.0.0 ls/server/…/service/FileContentService.kt:391-405]. It is off by default so that a
sibling project's copy doesn't silently replace the package version you meant
[src: WIKI-030e98c User-Guide.md:994-1000].

**Open each IG project as its own workspace folder** for predictable results. The extension uses only
the first folder of a multi-root workspace [src: VSCQL-1.0.0 src/model/cqlSolution.ts:42-43], and the
server's tier 2 and `config.jsonc` come from the workspace folder, not from a project in a sub-folder
[src: WIKI-030e98c User-Guide.md:1041].

## FHIR packages and `dev` dependencies

The server reads the project's IG `dependsOn` and loads those packages through the shared FHIR package
cache, `~/.fhir/packages`, which the IG Publisher, SUSHI and the validator also use. Package libraries
are tier 2 above; package model info is used too [src: CQLLS-5.0.0 ls/server/…/manager/IgContextManager.kt:112-114].

**A `dependsOn` with `version="dev"` writes a stub into the real package cache.** For each such
dependency, the server looks for a sibling folder whose `ig.ini` has that `packageId`, then writes a
package containing only a `package.json` to the cache as `<packageId>#current`
[src: CQLLS-5.0.0 ls/server/…/manager/IgContextManager.kt:196-279]. The dev project's CQL itself is
found by the namespace index or the local search above, not from the stub.

That stub is then in `~/.fhir/packages` for every tool. The IG Publisher, asked for `#current` of that
package, can pick up an empty package. If an IG Publisher build or another tool behaves as if a
package has no content, look for `~/.fhir/packages/<packageId>#current/package/` holding only
`package.json` (and maybe `.index.json`), and remove that folder with no tool running. Leave `*.lock`
files alone [src: WIKI-030e98c developer-notes/FHIR-Package-Cache.md:64-101].

The wiki describes a different design, in which `dev` packages are built in memory and the server
"never writes stub or partial packages", and says the stubs came from versions before 4.11
[src: WIKI-030e98c developer-notes/FHIR-Package-Cache.md:17-24]
[src: WIKI-030e98c developer-notes/FHIR-Package-Cache.md:64-72]. No 4.11 was released (the
CHANGELOG goes from 4.10.0 to 5.0.0) [src: CQLLS-5.0.0 CHANGELOG.md:4-35], and 5.0.0 still writes the
stub. Treat the wiki's description as not yet released.

## Compiler options: `cql-options.json`

- **Editor diagnostics** read `cql-options.json` from the `cql` folder above the file being compiled:
  for `input/cql/A.cql`, `input/cql/cql-options.json`
  [src: CQLLS-5.0.0 ls/server/…/manager/CompilerOptionsManager.kt:23-36]. For a file in a sub-folder,
  such as `input/cql/measures/A.cql`, that becomes `input/cql/cql/cql-options.json`, which doesn't
  exist, so those files silently get the translator's defaults (read from the code; not observed).
- A missing or unreadable file means the translator's defaults, with an info message in the log.
  Either way the server adds `EnableLocators`, `EnableResultTypes`, `EnableAnnotations` and signature
  level `All` [src: CQLLS-5.0.0 ls/server/…/manager/CompilerOptionsManager.kt:38-58].
- **Execute CQL** uses the options file the extension passes, `<project>/input/cql/cql-options.json`
  [src: VSCQL-1.0.0 src/helpers/cqlHelpers.ts:58-65] [src: CQLLS-5.0.0 ls/server/…/command/CqlEvaluator.kt:412-419].

The options are the CQL-to-ELM translator's, for example:

```json
{
  "options": ["EnableAnnotations", "EnableLocators", "DisableListDemotion", "DisableListPromotion"],
  "formats": ["XML", "JSON"],
  "validateUnits": true,
  "errorLevel": "Info",
  "signatureLevel": "None"
}
```

[src: WIKI-030e98c User-Guide.md:285-310]. The IG Publisher reads the same file from each
`path-binary` folder, with its own translator version, so the two can report different diagnostics
for the same CQL.

## When changes are noticed

| You change | The server | To be sure |
| --- | --- | --- |
| A `.cql` file | Recompiles it | nothing |
| `config.jsonc` / `config.json` | Clears the library-resolution settings, but not compiled results | Edit (touch) the `.cql` file |
| `cql-options.json` | Clears cached options, but not compiled results | Edit the `.cql` file |
| `ig.ini` or the IG's `dependsOn` | Tries to invalidate, but by the code the keys don't match, so cached package context and compiled results can stay stale | Restart the language server (reload the window) |

[src: CQLLS-5.0.0 ls/server/…/manager/CqlCompilationManager.kt:75-90]
[src: CQLLS-5.0.0 ls/server/…/manager/CqlCompilationManager.kt:132-143]
[src: CQLLS-5.0.0 ls/server/…/manager/IgContextManager.kt:50-62]
[src: CQLLS-5.0.0 ls/server/…/service/CqlWorkspaceService.kt:42]. The `ig.ini` row is a code reading,
not observed.
