# Probe 2026-10-22: IG Publisher 3.0.1 on EX-DQM-CMS-2025

Records what one publisher build did on a copy of one IG. It is evidence of behaviour at this version
and in this environment, not of what the publisher is meant to do. The skill cites it as
PROBES-2026-10-22.

## Environment

| Item | Value |
| --- | --- |
| Publisher | `publisher.jar` from `https://github.com/HL7/fhir-ig-publisher/releases/download/3.0.1/publisher.jar`; it reports "FHIR IG Publisher Version 3.0.1 (Git# 27b3216092e5). Built 2026-10-15T17:22:33.724Z" |
| `java -jar publisher.jar -v` | printed `3.0.1` |
| Jar sha256 | `2862e5455d6023f7b4b17642341d04f4fee5199daa140ceb2e01c1e75ab27ecc` (248,015,786 bytes). The `.asc` signature was downloaded but not verified |
| Java | Temurin 17.0.17, macOS aarch64, 4096 MB heap available |
| Jekyll | 4.4.1 |
| Terminology server | `https://tx.fhir.org` (log line 22) |
| IG | A copy of dqm-content-cms-2025 at 46b11c35 (clean working tree), rsynced to a scratch folder without `.git`, `bundles/`, `out/`, `temp/`, `output/`, `template/`, `fsh-generated/` or `input-cache/publisher.jar`. `input-cache/txcache` was copied. The original repository was not written to. |
| Package cache | A new, empty folder, via `-package-cache-folder`. After run 1 failed (below), six packages missing from it were copied from `~/.fhir/packages`: `hl7.fhir.r4.examples#4.0.1`, `hl7.fhir.r5.core#5.0.0`, `hl7.fhir.uv.extensions#5.1.0-snapshot1`, `hl7.terminology.r5#5.3.0`, `us.cdc.phinvads#0.12.0`, `us.nlm.vsac#0.18.0` |

## Command

The same command for all three runs (`<probe>` is the scratch folder):

```sh
java -Djava.io.tmpdir=<probe>/tmp -jar <probe>/jar/publisher.jar -ig <probe>/ig -no-errors -package-cache-folder <probe>/pkgcache
```

## Runs

| Run | Change | Result |
| --- | --- | --- |
| 1 | none | Stopped at package loading: `packages2.fhir.org` returned Bad Gateway for `us.nlm.vsac`, and the build failed with "Unable to resolve package id us.nlm.vsac#0.18.0". Exit 1. No QA. A registry outage, not a finding |
| 2 | Package cache seeded (above) | Completed in 4 min 11 s: err = 1502, warn = 1509, info = 248. Exit 1 |
| 3 | Four lines appended to the copy's `input/ignoreWarnings.txt` (see `run3-ignoreWarnings.diff`) | Completed: err = 1502, warn = 1437, info = 248. Exit 1 |

## Findings

### 1. A `.cql` file's translation errors are not reported unless a Library claims it with `ig-loader-`

The IG's 89 Libraries embed their CQL; none uses `ig-loader-`. In run 2:

- 4 of the 103 `.cql` files failed translation, with 2, 2, 166 and 1 errors (`log-excerpts.txt`):
  `testE18DateTimeCompare`, `testI37RecordedAmbiguousOverload`, `testE15Passing` and
  `testI28ChoiceArgumentProbeA`. All four are `test*` probe libraries committed in the IG's
  `input/cql` (13 `test*.cql` files are tracked at 46b11c3), and none has a Library resource. **No
  measure or helper library failed translation.**
- `qa.txt` names each of the four files exactly once, with "CQL source was not associated with a
  library resource in the IG." and nothing else. "CQL Processing failed" appears 0 times
  (`qa-excerpts.txt`).
- "CQL source was not associated…" appears 104 times: once for each of the 103 `.cql` files and once
  for `usqualitycore-modelinfo-0.1.0-cibuild.xml`. Model info files get the message too.
- These 104 messages are the whole of "Build Errors : 104" in the `qa.txt` header.

**Confirms** the source reading in `cql-loader.md` (CqlSubSystem.java:343-363, 374-382; AdjunctFileLoader.java:333-336).

### 2. ELM generation fails for 95 of 103 files, and only the log says so

The log shows "CQL Translation succeeded for file: '…', but ELM generation failed with the following
error: Unknown FHIRTypes code 'Any'" for 95 files; 4 completed successfully and 4 failed translation
(`log-excerpts.txt`). Of the 90 files that are not `test*` probe libraries, 89 hit this failure and
one (`NHSNHelpers.cql`) completed successfully. Nothing about this appears in `qa.txt`. The message is logged by the catch in
`CqlSubSystem.translateFile` (CqlSubSystem.java:753-756). `Enumerations.FHIRTypes.fromCode` is called
for parameter and define result types at CqlSubSystem.java:1011 and :1023; which call raised it here,
and for which parameter or define type, was not determined.

**New**, not predicted by the source reading.

### 3. Libraries with embedded CQL are published unchanged

In run 2's output, 0 of 89 `Library-*.json` files have `application/elm+xml` or `application/elm+json`
content. `Library-AdultOutpatientEncounters.json` has the same single `text/cql` attachment as its input,
with byte-identical `data`, and no `dataRequirement`.

**Confirms** `cql-loader.md`: without `ig-loader-`, the publisher doesn't replace the attachment or add ELM.

Measures, by contrast, are processed. All 74 input Measures already contain an effective data
requirements Library, and in all 74 published Measures that contained Library differs from the input
(a JSON comparison with sorted keys). That fits the publisher recomputing it from the compiled CQL, but
the differences were not examined.

### 4. `ignoreWarnings.txt` suppresses warnings, but a matched error stays an error

Run 3 added a control line matching the 72 "List of Coding, display: string of definition SDE Race is
not supported" warnings, and two lines matching the two `path-liquid-ig` errors on the IG resource
(`run3-ignoreWarnings.diff`).

| Measure | Run 2 | Run 3 | Change |
| --- | --- | --- | --- |
| errs | 1502 | 1502 | 0 |
| warnings | 1509 | 1437 | -72 |
| suppressed-warnings | 1288 | 1360 | +72 |
| suppressed-hints | 6472 | 6474 | +2 |
| "SDE Race is not supported" lines in `qa.txt` | 72 | 0 | -72 |
| `path-liquid-ig` error lines in `qa.txt` | 2 | 2 | 0 |

The two errors remain in `qa.txt` and in `qa.html`, where each now carries "Editor's Comment :" with
the reason line (`run3-qa-html-comments.txt`). The matched errors add to `suppressed-hints` even though
they are still reported.

**Confirms** `running.md` (ValidationPresenter.java:496, 1017, 1025-1031).

The IG's own `ERROR:` lines in `ignoreWarnings.txt` (lines 4-6) don't match today's messages: they name
`ImplementationGuide/cms.madie`, `extension[10]` and value set `|0.7.1`, but run 2 reports
`ImplementationGuide/madie.cms.gov.dqms`, `extension[13]` and `|1.3.0`. Even with matching lines (run
3), the errors stay.

### 5. `-no-errors` gives exit 1 when there are errors

Runs 2 and 3 completed without an exception and exited 1 with 1502 errors. A run without `-no-errors`
was not made, so the source reading that such a build exits 0 (Publisher.java:1223, 1622-1643) is not
observed here.

### 6. `qa.json`'s `tool` is not the publisher version

`run2-qa.json` has `"tool" : "6.0.0-snapshot1 (3)"`. The publisher version is in `qa.txt`'s header,
"IG Publisher Version: 3.0.1". **Corrects** `running.md`, which said `tool` holds the publisher version.

### 7. Pinning into the manifest (re-read of run 3's output, 2026-10-23)

No new build: run 3's `output/` was re-read. The QA summary reads "pinned = 4854 (all) (in manifest
Parameters/manifest)". The IG's `input/resources/parameters/Parameters-manifest.json` has 1 parameter
(`system-version`); the published `output/Parameters-manifest.json` has 764: 626
`default-valueset-version`, 123 `default-canonical-version` and 15 `system-version`
(`run3-pinning.txt`). The per-pin information messages are hidden by the IG's `ignoreWarnings.txt`
line 13, `%Pinned the version of%`.

### 8. No Liquid templates in the template chain (re-read of run 3's folders, 2026-10-23)

No new build. After run 3, `find -name '*.liquid'` found none in the unpacked `template/` folder and none
in any loaded package; the only five were the IG's own, in `templates/liquid` (`run3-liquid-search.txt`).

### 9. An R4 IG gets R4 and R4B packages automatically (re-read of run 3's output, 2026-10-23)

No new build. With no version parameters, run 3 wrote `package.tgz` (`madie.cms.gov.dqms`),
`package.r4.tgz` (`madie.cms.gov.dqms.r4`) and `package.r4b.tgz` (`madie.cms.gov.dqms.r4b`, FHIR 4.3.0).
The R4B package depends on `hl7.fhir.r4b.core#4.3.0`, and otherwise on the same packages as the R4 one,
including `hl7.fhir.us.cqfmeasures#5.0.0` and `hl7.terminology.r4#6.5.0`. `sub-package-list.json` is
`[]` (`run3-packages.txt`). Also seen, not investigated: the packages' dependencies don't include
`hl7.fhir.us.qicore` or `fhir.cqf.common`, although the IG's `dependsOn` lists both.

## Files

| File | Contents |
| --- | --- |
| `run2-qa.json`, `run3-qa.json` | The runs' `output/qa.json`, unmodified |
| `qa-excerpts.txt` | Lines from the runs' `output/qa.txt`, unmodified, with line numbers and section notes |
| `log-excerpts.txt` | Lines from the three runs' console logs, ANSI colour codes removed, with line numbers |
| `run3-ignoreWarnings.diff` | The lines added to the copy's `ignoreWarnings.txt` for run 3 |
| `run3-packages.txt` | Name, version, FHIR version and dependencies of run 3's three packages, and `sub-package-list.json` |
| `run3-pinning.txt` | Run 3's QA summary sentence, the manifest's parameter counts before and after, and `ignoreWarnings.txt` line 13 |
| `run3-liquid-search.txt` | Counts of `*.liquid` files in run 3's `template/`, package cache and `templates/liquid` |
| `run3-qa-html-comments.txt` | Text around each "PROBE 2026-10-22" reason in run 3's `qa.html`, tags removed |
