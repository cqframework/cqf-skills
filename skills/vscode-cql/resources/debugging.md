# Debugging CQL

Baseline: vscode-cql 1.0.0 with cql-language-server 5.0.0. Untagged statements hold at these versions only.
Sources: VSCQL-1.0.0, CQLLS-5.0.0, WIKI-030e98c

The extension debugs CQL through the Debug Adapter Protocol. The debugger runs inside the language
server: the extension asks the server to start a session (`org.opencds.cqf.cql.debug.startDebugSession`)
and connects to the port it returns [src: VSCQL-1.0.0 src/debug/cqlDebugAdapterDescriptorFactory.ts:15-19].
A session evaluates one library against one test case's data, with the same parameters as Execute CQL
(see [test-config.md](test-config.md#parameters)).

## Starting a session

- **From the editor:** right-click in a `.cql` file, **Debug Test Case**, then pick a test case.
- **From the CQL Explorer:** **Debug Test Case** on a test case, or on the test cases node (then
  pick one).

Both build the launch configuration for you: the library, its FHIR version (from the `using FHIR`
or `using QICore` declaration, `R4` if neither), the test case folder, the terminology and options
locations, and the merged parameters [src: VSCQL-1.0.0 src/commands/debug-test-case.ts:46-77]
[src: VSCQL-1.0.0 src/helpers/cqlHelpers.ts:84-96]. No `launch.json` is needed, and these are the
recommended ways in [src: WIKI-030e98c User-Guide.md:754-775] [src: WIKI-030e98c User-Guide.md:817].
The wiki also describes a "Debug CQL File" button in the editor title bar
[src: WIKI-030e98c User-Guide.md:756], but 1.0.0's `package.json` contributes no editor title menu
(see [commands.md](commands.md)).

### A `launch.json` of your own

The debugger type is `cql`. Its schema requires `libraryUri` and `fhirVersion` and also lists
`testCaseName`, `testCaseUri`, `terminologyUri`, `rootDir`, `optionsPath` and `stepGranularity`
[src: VSCQL-1.0.0 package.json:788-836]. The server also reads `libraryName` and `parameters`, which
the built-in commands send but the schema doesn't list
[src: CQLLS-5.0.0 ls/server/…/debug/CqlDebugServer.kt:686-710].

`libraryUri` is the **`.cql` file** as a `file:` URI: the built-in commands pass the file's URI
[src: VSCQL-1.0.0 src/commands/debug-test-case.ts:38-77], and the server parses it with `URI.create`
and compiles it [src: CQLLS-5.0.0 ls/server/…/debug/CqlDebugServer.kt:439-448]. VS Code variables
such as `${file}` expand to plain paths, which on Windows contain backslashes and aren't valid URIs
(read from the code; not observed). So write the URIs out:

```json
{
  "type": "cql",
  "request": "launch",
  "name": "Debug MyLibrary",
  "libraryUri": "file:///home/me/my-ig/input/cql/MyLibrary.cql",
  "libraryName": "MyLibrary",
  "fhirVersion": "R4",
  "testCaseName": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "testCaseUri": "file:///home/me/my-ig/input/tests/MyLibrary/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

The wiki's example uses the folder (`${fileDirname}`) for `libraryUri` and omits `fhirVersion`
[src: WIKI-030e98c User-Guide.md:798-815]; both disagree with the code. Without a test case,
every expression that needs patient data evaluates to `null` [src: WIKI-030e98c User-Guide.md:817].
`fhirVersion` takes `DSTU2`, `DSTU3`, `R4` or `R5`, as the built-in command derives it
[src: VSCQL-1.0.0 src/helpers/cqlHelpers.ts:84-96].

## While it runs

- **Breakpoints** go in the gutter on a `define` line; they can also be set on operands inside a
  definition. Breakpoints on other lines (`library`, `using`) stay unverified
  [src: WIKI-030e98c User-Guide.md:777-794]. **Conditions are ignored**: the server reads only the
  line and doesn't advertise conditional breakpoints
  [src: CQLLS-5.0.0 ls/server/…/debug/CqlDebugServer.kt:229-236].
- **Stepping:** Continue (F5), Step Over (F10), Step Into (F11), Step Out (Shift+F11). Stepping into
  libraries with no workspace file, such as FHIRHelpers, opens them as virtual documents
  [src: WIKI-030e98c User-Guide.md:783-794].
- **Step granularity:** CQL level (the default) stops on `define` lines; AST level stops on every ELM
  node. Switch with **CQL: Toggle Step Granularity (CQL ↔ AST)** or the status bar item, or start
  with `"stepGranularity": "ast"` [src: VSCQL-1.0.0 src/debug/stepGranularityToggle.ts:14-34]
  [src: WIKI-030e98c User-Guide.md:840-856].
- **Variables** shows, while paused: **Parameters** (if the library has any), **Locals**,
  **Resolved Defines** and **Test Case**; otherwise **Expressions** and **Test Case**
  [src: CQLLS-5.0.0 ls/server/…/debug/CqlDebugServer.kt:796-857]. The wiki's "Arguments, Expressions,
  Context" [src: WIKI-030e98c User-Guide.md:819-827] doesn't match 5.0.0.
- **Debug Console** evaluates CQL against the paused frame (earlier defines, parameters and the
  context are in scope), with completion for expression names; hovering and the Watch panel use the
  same evaluation [src: CQLLS-5.0.0 ls/server/…/debug/CqlDebugServer.kt:1103-1129]
  [src: WIKI-030e98c User-Guide.md:829-838].
- **CQL AST view** in the Run and Debug sidebar follows the current frame; clicking a node shows its
  CQL source [src: VSCQL-1.0.0 src/debug/cqlAstTreeDataProvider.ts:107]. The view appears only during
  a CQL session (see [commands.md](commands.md#views)).

## Limits

- Test data is read from disk when the session starts; edit the files and restart to change it
  [src: WIKI-030e98c User-Guide.md:870-876].
- The extension sets `debug.openExplorerOnEnd` to `true`, so the Explorer comes back when a session
  ends [src: VSCQL-1.0.0 package.json:848-850].
