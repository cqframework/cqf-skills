# Sources

Registry of every source the skill's resource files cite. Cite a claim inline as
`[src: ID path:line[-line]]`, with the path relative to the repository root at the pinned ref. A `…`
elides the middle of a path; the rest must match one file (full paths are listed below).

| ID | Kind | Status | Version | Pinned locator | Published URL | Local copy | Retrieved |
| --- | --- | --- | --- | --- | --- | --- | --- |
| VSCQL-1.0.0 | implementation-source | n/a | vscode-cql 1.0.0, released 2026-11-09, commit 855eac7b5f21c788d0e0e856d741cadc35e6bda9 | cqframework/vscode-cql@v1.0.0 | <https://github.com/cqframework/vscode-cql/tree/v1.0.0> | none (git show v1.0.0:PATH; the fetch script caches a clone) | 2026-11-14 |
| CQLLS-5.0.0 | implementation-source | n/a | cql-language-server 5.0.0, released 2026-11-05, commit 68e601fa6b8ef7df99f8ef29b86d4464d94bd400; the version vscode-cql 1.0.0 downloads | cqframework/cql-language-server@v5.0.0 | <https://github.com/cqframework/cql-language-server/tree/v5.0.0> | none (git show v5.0.0:PATH; the fetch script caches a clone) | 2026-11-14 |
| WIKI-030e98c | guide | informative | The vscode-cql wiki at commit 030e98c (2026-11-20, "update links"; the Developer Guide last changed in 03238e1, 2026-11-17, which dropped `hotfix/` branches); its developer notes were last changed at de7bd96 (2026-07-08) and are headed with 4.6.0-SNAPSHOT versions | cqframework/vscode-cql.wiki@030e98c76e8452e67f99d9507768fb2eb4814e2e | <https://github.com/cqframework/vscode-cql/wiki> | none (git show 030e98c:PATH; the fetch script caches a clone) | 2026-11-24 |

## Looking up a citation at another version

No local copy is needed to check a claim. A citation names the exact file and lines, so the same place
can be read at the pinned version or at the version a user actually has:

| Source | URL for a citation at version `<v>` |
| --- | --- |
| VSCQL | `https://github.com/cqframework/vscode-cql/blob/v<v>/<path>#L<a>-L<b>` (tags are `v` plus the version) |
| CQLLS | `https://github.com/cqframework/cql-language-server/blob/v<v>/<path>#L<a>-L<b>`. The server version an extension release uses is `javaDependencies.cql-language-server.version` in that release's `package.json` |
| WIKI | `https://github.com/cqframework/vscode-cql/wiki/<Page>` shows the current wiki only; the pinned text is in the wiki's git repository, `https://github.com/cqframework/vscode-cql.wiki.git` |

Line numbers move between releases, so at another version find the cited code by its content near the
cited lines. The installed extension's version is shown in VS Code's Extensions view; the language
server's, translator's and engine's versions are in the tooltip of the CQL status bar item.

**Cited files.** The full paths behind each `…`:

| Source | Path |
| --- | --- |
| CQLLS | `ls/server/src/main/kotlin/org/opencds/cqf/cql/debug/CqlDebugServer.kt` |
| CQLLS | `ls/server/src/main/kotlin/org/opencds/cqf/cql/ls/server/command/CqlEvaluator.kt` |
| CQLLS | `ls/server/src/main/kotlin/org/opencds/cqf/cql/ls/server/manager/CompilerOptionsManager.kt` |
| CQLLS | `ls/server/src/main/kotlin/org/opencds/cqf/cql/ls/server/manager/CqlCompilationManager.kt` |
| CQLLS | `ls/server/src/main/kotlin/org/opencds/cqf/cql/ls/server/manager/IgContextManager.kt` |
| CQLLS | `ls/server/src/main/kotlin/org/opencds/cqf/cql/ls/server/manager/JsonLibraryResolutionConfigProvider.kt` |
| CQLLS | `ls/server/src/main/kotlin/org/opencds/cqf/cql/ls/server/manager/LibraryProviderRegistrar.kt` |
| CQLLS | `ls/server/src/main/kotlin/org/opencds/cqf/cql/ls/server/manager/LibraryResolutionConfig.kt` |
| CQLLS | `ls/server/src/main/kotlin/org/opencds/cqf/cql/ls/server/manager/LibraryResolutionManager.kt` |
| CQLLS | `ls/server/src/main/kotlin/org/opencds/cqf/cql/ls/server/provider/FederatedLibrarySourceProvider.kt` |
| CQLLS | `ls/server/src/main/kotlin/org/opencds/cqf/cql/ls/server/repository/ig/standard/FederatedTerminologyRepo.kt` |
| CQLLS | `ls/server/src/main/kotlin/org/opencds/cqf/cql/ls/server/repository/ig/standard/IgStandardConventions.kt` |
| CQLLS | `ls/server/src/main/kotlin/org/opencds/cqf/cql/ls/server/repository/ig/standard/IgStandardRepository.kt` |
| CQLLS | `ls/server/src/main/kotlin/org/opencds/cqf/cql/ls/server/service/CqlTextDocumentService.kt` |
| CQLLS | `ls/server/src/main/kotlin/org/opencds/cqf/cql/ls/server/service/CqlWorkspaceService.kt` |
| CQLLS | `ls/server/src/main/kotlin/org/opencds/cqf/cql/ls/server/service/FileContentService.kt` |

## Notes

- **What each source is evidence of.** VSCQL-1.0.0 and CQLLS-5.0.0 show what the extension and the
  language server *do* at those versions. WIKI-030e98c says what the maintainers *describe*; where it
  and the code disagree, the code is cited and the disagreement noted.
- **The wiki's developer notes are older than its user guide.** `developer-notes/` was last changed
  on 2026-07-08 and its headers name language server 4.6.0-SNAPSHOT, so every claim taken from it was
  checked against CQLLS-5.0.0.
- **Local clones are for maintenance.** `scripts/fetch-sources.sh` caches blobless clones at the
  pinned refs under `~/.cache/vscode-cql-skill/` (or `$VSCQL_SKILL_CACHE`), for
  `scripts/lint_skill_vscql.py` and `scripts/check_release.py`.
