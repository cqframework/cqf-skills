# Developer Guide: Architecture, Building and Releasing

Baseline: vscode-cql 1.0.0 with cql-language-server 5.0.0. Untagged statements hold at these versions only.
Sources: VSCQL-1.0.0, CQLLS-5.0.0, WIKI-c9e1023

For contributors to the extension or the language server. For using the extension, see
[user-guide.md](user-guide.md).

## Architecture

Two projects, talking over stdio:

```text
vscode-cql (TypeScript VS Code extension)
       │  JSON-RPC over stdio (LSP), plus workspace/executeCommand for custom commands
       ▼
cql-language-server (Kotlin/JVM fat JAR)
```

The extension starts the server as `<JDK>/bin/java -Xmx4g … -jar cql-ls-server-<version>.jar`, with
the log file passed as `-DLOG_FILE` [src: VSCQL-1.0.0 src/cql-language-server/languageServerStarter.ts:56-86].
The server version is `javaDependencies.cql-language-server` in `package.json`
[src: VSCQL-1.0.0 package.json:865-871].

### The extension (`src/`)

| Folder or file | Role |
| --- | --- |
| `extension.ts` | Entry point: checks Java, starts the LSP client, registers commands |
| `java-support/` | Finding a JDK 17+ (`requirements.ts`, `findJavaRuntimes.ts`) and downloading the server JAR (`javaServiceInstaller.ts`) |
| `cql-language-server/` | LSP client setup and the server process launch |
| `cql-service/` | Requests to the server, such as Execute CQL |
| `commands/` | Command implementations: execute, View ELM, debug test case, logs |
| `cql-explorer/` | The CQL Explorer tree and test case and resource operations |
| `debug/` | The DAP client: adapter factory, CQL AST view, step granularity toggle |
| `model/` | Project and IG layout detection, test cases, test configuration |
| `views/` | Webviews, such as the configuration editor |

[src: WIKI-c9e1023 Developer-Guide.md:17-31], checked against the tree at VSCQL-1.0.0.

### The language server (`ls/server/src/main/kotlin/org/opencds/cqf/cql/`)

No dependency injection framework: `ls/service/Main.kt` builds the object graph by hand and starts
the LSP listener on stdio [src: WIKI-c9e1023 Developer-Guide.md:33-46]. The shaded JAR's main class
is `org.opencds.cqf.cql.ls.service.MainKt` [src: CQLLS-5.0.0 ls/server/pom.xml:150].

| Area | Classes |
| --- | --- |
| LSP services | `CqlLanguageServer` (root), `CqlTextDocumentService` (hover, diagnostics, formatting, navigation), `CqlWorkspaceService` (`workspace/executeCommand`), `DiagnosticsService` |
| Managers | `CqlCompilationManager` (compiles and caches per source URI), `CompilerOptionsManager` (`cql-options.json`), `IgContextManager` (IG and package context), `LibraryResolutionManager` |
| Providers | `HoverProvider`, `FormattingProvider`, `DefinitionProvider`, `DocumentSymbolProvider`, `ReferencesProvider`, `FederatedLibrarySourceProvider` |
| Commands | `ExecuteCqlCommandContribution`, `ViewElmCommandContribution`, `DebugCommandContribution`, `GetVersionInfoCommandContribution`, `VirtualSourceCommandContribution` |
| Debugger (DAP) | `CqlDebugServer`, `DebugSession`, `StreamingBreakpointHandler` (in `debug/`) |
| Content | `FederatedContentService` (open editors first, then disk), `ActiveContentService`, `FileContentService` |
| Execution | `CqlEvaluator` |

[src: WIKI-c9e1023 Developer-Guide.md:48-99]. Every class listed exists at CQLLS-5.0.0 (searched by
file name). The extension starts a debug session through the server command
`org.opencds.cqf.cql.debug.startDebugSession` and connects to the port it returns
[src: VSCQL-1.0.0 src/debug/cqlDebugAdapterDescriptorFactory.ts:15-19].

## Building

| | Language server | Extension |
| --- | --- | --- |
| Needs | Java 17+ and Maven 3.8+ | Node.js 20+ |
| Build | `mvn package -DskipTests` (fat JAR in `ls/server/target/`) | `npm install`, `npm run compile` |
| Test | `mvn test` | `npm test` |

[src: WIKI-c9e1023 Developer-Guide.md:105-135]. The server compiles for Java 17
[src: CQLLS-5.0.0 pom.xml:15-17].

The extension's npm scripts [src: VSCQL-1.0.0 package.json:856-862]:

| Script | Does |
| --- | --- |
| `compile` | `tsc -p ./` |
| `watch` | `tsc -watch -p ./`, for the F5 loop |
| `package` | cleans `dist`, then `vsce package --out build`: a VSIX without the server JAR, which is downloaded on first run |
| `package:local` | compile, `scripts/download-jar.js`, then `vsce package` with `.vscodeignore.local`: a VSIX with the JAR bundled |
| `test` | `vscode-test` (after `pretest` cleans and compiles) |

The build is plain `tsc`. esbuild bundling is on a feature branch and not in 1.0.0
[src: WIKI-c9e1023 Developer-Guide.md:196].

## Running a locally built server

The extension loads `dist/java-support/jars/cql-ls-server-<version>.jar`
[src: VSCQL-1.0.0 src/java-support/javaServiceInstaller.ts:16-18] and downloads it from
`https://repo1.maven.org/maven2/` only when that file is missing
[src: VSCQL-1.0.0 src/java-support/javaServiceInstaller.ts:66-69]. So:

1. `mvn package -DskipTests` in `cql-language-server`.
2. Copy `ls/server/target/cql-ls-server-<version>.jar` into `vscode-cql/dist/java-support/jars/`.
3. Make `javaDependencies.cql-language-server.version` in `package.json` equal `<version>`. A
   `-SNAPSHOT` version can't be downloaded, so the copied file must be there.
4. Press F5 in `vscode-cql/` to start the Extension Development Host, or restart it.

[src: WIKI-c9e1023 Developer-Guide.md:145-170]. `mvn test` and `mvn package` don't change a running
extension host; restart it.

**End-to-end check** after starting the host: diagnostics and hover in a `.cql` file; Execute CQL
and the View ELM commands; F12, Shift+F12 and Ctrl+Shift+O; a debug session from the CQL Explorer;
and a clean start in "Show CQL Extension and Language Server Logs"
[src: WIKI-c9e1023 Developer-Guide.md:171-179].

## Versions and branches

- **Extension:** an even minor (`1.0.x`, `1.2.x`) is a Marketplace release; an odd minor (`1.1.x`,
  `1.3.x`) is a pre-release, published with `--pre-release`. The Marketplace doesn't accept suffixes
  such as `-alpha` [src: WIKI-c9e1023 Developer-Guide.md:202-209].
- **Language server:** `master` always carries a `-SNAPSHOT` version; releases are cut from `master`,
  with no release branches, and `master` then moves to the next SNAPSHOT
  [src: WIKI-c9e1023 Developer-Guide.md:211-215].
- **Branching:** trunk-based on `master`. Short-lived `feature/`, `bugfix/`, `hotfix/` or `task/`
  branches, merged by pull request; never commit to `master` directly
  [src: WIKI-c9e1023 Developer-Guide.md:217-233].
