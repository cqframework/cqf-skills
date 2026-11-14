# Probe 2026-11-14: IG Publisher 3.0.4 on EX-DQM-CMS-2025, with fhir.base.template 1.0.0

Records what three publisher builds did on a copy of one IG, to re-check the 2026-10-22 findings (IG
Publisher 3.0.1) after re-pinning the skill to IG Publisher 3.0.4 and the 1.0.0 templates. It is
evidence of behaviour at these versions and in this environment, not of what the publisher is meant
to do. The skill cites it as PROBES-2026-11-14.

## Environment

| Item | Value |
| --- | --- |
| Publisher | `publisher.jar` from `https://github.com/HL7/fhir-ig-publisher/releases/download/3.0.4/publisher.jar`; it reports "FHIR IG Publisher Version 3.0.4 (Git# 7b7ccec6ce50). Built 2026-11-14T02:51:57.470Z" |
| `java -jar publisher.jar -v` | printed `3.0.4` |
| Jar sha256 | `361b8aa8b2c037bcc0faeb66e0f5882f447259edbae92af5457c493b3514e059` (243,968,337 bytes) |
| Java | Temurin 21.0.9, Windows 11 amd64, 16184 MB available |
| Jekyll | 4.4.1 |
| Terminology server | `https://tx.fhir.org`, with the ecosystem `https://ecosystem.hl7.org/tx-reg` (`log-excerpts.txt`) |
| IG | A copy of dqm-content-cms-2025 at 46b11c35 (the same commit as the 2026-10-22 probe), without `.git`, `bundles/`, `out/`, `temp/`, `output/`, `template/`, `fsh-generated/` or `input-cache/publisher.jar`. `input-cache/txcache` was copied |
| Template | **Changed**: the copy's `ig.ini` was edited from `cqf.fhir.template#0.7.1` to `cqf.fhir.template#1.0.0` (`run-template.diff`), so the build used fhir.base.template 1.0.0 |
| Package cache | A new, empty folder, via `-package-cache-folder` |

## Command

The same for all three runs (`<probe>` is the scratch folder):

```sh
java -Djava.io.tmpdir=<probe>/tmp -jar <probe>/jar/publisher.jar -ig <probe>/ig -no-errors -package-cache-folder <probe>/pkgcache
```

## Runs

| Run | Change | Result |
| --- | --- | --- |
| 1 | the template change above | Completed in 9 min 19 s: err = 1505, warn = 1516, info = 248. Exit 1 |
| 2 | Three lines appended to the copy's `input/ignoreWarnings.txt` (`run2-ignoreWarnings.diff`), the same lines as the 2026-10-22 probe's run 3 | Completed in 2 min 52 s: err = 1505, warn = 1516, info = 248. Exit 1 |
| 3 | One more line appended (`run3-ignoreWarnings.diff`): a control line matching 3.0.4's wording of the warning | Completed: err = 1505, warn = 1444, info = 248. Exit 1 |

## Findings

### 1. CQL: the same results as 3.0.1, on translator 4.9.0

`log-excerpts.txt` lists the outcome for each of the 103 `.cql` files:

- 95 logged "CQL Translation succeeded … but ELM generation failed with the following error: Unknown
  FHIRTypes code 'Any'". Of the 90 files that are not `test*` probe libraries, 89 failed this way and
  only `NHSNHelpers.cql` completed.
- The same four `test*` files as on 3.0.1 failed translation, with 166, 2, 1 and 2 errors.
- `qa.txt` has 104 "CQL source was not associated with a library resource in the IG." lines (one per
  `.cql` file and one for the model info file) and no "CQL Processing failed" line (`qa-excerpts.txt`).
  These are the whole of "Build Errors : 104".

**Confirms** `cql-loader.md` at 3.0.4. The 'Any' failure is now explained by code reading
(CqlSubSystem.java:1110-1155 maps every type outside FHIR and the System primitives to "Any", which
FHIRTypes.fromCode rejects).

### 2. Libraries with embedded CQL are published unchanged

In run 1's output, 0 of 89 `Library-*.json` files have ELM content; `Library-AdultOutpatientEncounters.json`
has the same single `text/cql` attachment as its input, with identical `data`, and no `dataRequirement`
(`run1-output-checks.txt`). **Confirms** the 3.0.1 result.

### 3. fhir.base.template 1.0.0 brings Liquid templates

After run 1, `template/liquid` held `ActivityDefinition.liquid`, `Library.liquid`, `Measure.liquid` and
`PlanDefinition.liquid` (`run1-template-liquid.txt`), with their `.html` fragments. With 0.8.1 the
2026-10-22 probe found none. The IG loads its own five templates with `path-liquid-ig`, which the
publisher loads last, so its templates were the ones used; that wasn't checked page by page.
**New**: the IG's workaround (see `templates.md`) is needed with 1.0.0.

### 4. `path-liquid-ig` still costs two errors

`qa.txt` reports the same two errors on the IG resource for the undefined `path-liquid-ig` code
(`qa-excerpts.txt`).

### 5. `ignoreWarnings.txt`

| Measure | Run 1 | Run 2 | Run 3 |
| --- | --- | --- | --- |
| errs | 1505 | 1505 | 1505 |
| warnings | 1516 | 1516 | 1444 |
| suppressed-warnings | 1288 | 1288 | 1360 |
| suppressed-hints | 6470 | 6472 | 6472 |
| "SDE Race is not supported" lines in `qa.txt` | 72 | 72 | 0 |
| `path-liquid-ig` error lines in `qa.txt` | 2 | 2 | 2 |

(`run1-qa.json`, `run2-qa.json`, `run3-qa.json`, `run2-qa-excerpts.txt`.)

- **Run 2's control line matched nothing.** It was copied from the 2026-10-22 probe, where it matched
  "List of Coding, display: string of definition SDE Race is not supported". 3.0.4, with translator
  4.9.0, words the same warning "Result type tuple of codes:list<FHIR.Coding>, display:FHIR.string of
  definition SDE Race is not supported". **New**: a publisher upgrade can silently stop
  `ignoreWarnings.txt` lines from matching.
- **Run 3's control line, written for the new wording, suppressed all 72 warnings**: warnings fell by
  72 and `suppressed-warnings` rose by 72.
- **The two errors stayed errors** in runs 2 and 3, and `qa.html` showed "Editor's Comment" with the
  reason (`run2-qa-html-comments.txt`). The matched errors raised `suppressed-hints` by 2.

**Confirms** the 3.0.1 result: only warnings and hints are suppressed.

### 6. Exit status and `qa.json`

Both runs exited 1 with `-no-errors`. `run1-qa.json` has `"tool" : "6.0.0-snapshot1 (3)"`, as on 3.0.1,
while `qa.txt`'s header says "IG Publisher Version: 3.0.4".

### 7. Pinning into the manifest

The published `Parameters-manifest.json` has 764 parameters (626 `default-valueset-version`, 123
`default-canonical-version`, 15 `system-version`) from an input with 1 (`run1-output-checks.txt`), as on
3.0.1.

### 8. Packages

Run 1 wrote `package.tgz`, `package.r4.tgz`, `package.r4b.tgz` (FHIR 4.3.0, depending on
`hl7.fhir.r4b.core#4.3.0` and otherwise on the same packages as the R4 one) and `package-combined.tgz`
(depending only on `hl7.fhir.r4.core#4.0.1`). `sub-package-list.json` is `[]`. The dependency on
`hl7.fhir.uv.extensions.r4` is 5.4.0, where the 3.0.1 build had 5.3.0 with the same IG
(`run1-output-checks.txt`).

### 9. `-package-cache-folder` isn't used for everything

32 packages were installed into the folder given with `-package-cache-folder`. One,
`hl7.fhir.us.cqfmeasures#5.0.0`, was installed into the user's default `~/.fhir/packages` during
"Validating Conformance Resources" (log line 452 of run 1). **New.**
