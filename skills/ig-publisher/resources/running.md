# Running the Publisher and Reading QA

Baseline: IG Publisher 3.0.5, fhir.base.template 1.0.0. Untagged statements hold at these versions only.
Sources: IGPUB-3.0.5, IGPUB-DOCS-3.0.5, TPL-BASE-1.0.0, SAMPLE-IG, EX-DQM-CMS-2025, PROBES-2026-10-22, PROBES-2026-11-14

## Getting a pinned publisher

The usual `_updatePublisher.sh` downloads `releases/latest/download/publisher.jar`
[src: SAMPLE-IG ./_updatePublisher.sh#L2-L4].

EX-DQM-CMS-2025's copy does the same [src: EX-DQM-CMS-2025 _updatePublisher.sh:2-4], so each IG builds
with whichever release was current when the script last ran. 3.0.0 was a new major version, and the
publisher is released often. To know what built an IG, download a fixed release, for example
`https://github.com/HL7/fhir-ig-publisher/releases/download/3.0.5/publisher.jar` (3.0.5 ships
`publisher.jar`, 244,010,552 bytes, and a `publisher.jar.asc` signature, checked 2026-11-24), and record
its version:

```sh
java -jar input-cache/publisher.jar -v
```

`-v` prints the version and exits [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1431-1432].
For 3.0.4 it prints `3.0.4` [src: PROBES-2026-11-14 RESULTS.md].

## Running a build

`_genonce.sh` runs [src: SAMPLE-IG ./_genonce.sh#L19]:

```sh
java -jar input-cache/publisher.jar -ig . $txoption
```

where `$txoption` is `-tx n/a` when `tx.fhir.org` can't be reached. On Windows, `_genonce.bat` runs the
same command [src: SAMPLE-IG ./_genonce.bat#L27-L32], with these differences:

| | macOS / Linux: `_genonce.sh` | Windows: `_genonce.bat` |
| --- | --- | --- |
| Jar locations tried, in order | `./input-cache/publisher.jar`, `../publisher.jar` [src: SAMPLE-IG ./_genonce.sh#L17-L27] | `%CD%\input-cache\publisher.jar`, `..\publisher.jar`, then `%FHIR_PUBLISHER_HOME%\publisher.jar` or, if that is unset, `%USERPROFILE%\.fhir\tools\publisher\publisher.jar` [src: SAMPLE-IG ./_genonce.bat#L2-L8] [src: SAMPLE-IG ./_genonce.bat#L27-L35] |
| Online check | `curl -sSf tx.fhir.org` [src: SAMPLE-IG ./_genonce.sh#L5] | PowerShell request to `https://tx.fhir.org/r4/metadata`, 4 s timeout [src: SAMPLE-IG ./_genonce.bat#L11] |
| At the end | exits | `PAUSE` waits for a key press [src: SAMPLE-IG ./_genonce.bat#L37], so don't use it unattended |

The sample's `.bat` sets `-Dfile.encoding=UTF-8` through `JAVA_TOOL_OPTIONS`
[src: SAMPLE-IG ./_genonce.bat#L23]; the sample's `.sh` doesn't, but the dqm example's `.sh` does
[src: EX-DQM-CMS-2025 _genonce.sh:17]. These are the FHIR sample IG's scripts at 74c54cd; an IG's own
copies may differ. `n/a` means "run without a
terminology server" [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1473-1476].
`java -jar publisher.jar <folder>`, with a single argument, works too
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1721-1722].

**Flags match exactly and take their value from the next argument**
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CliParams.java:15-40] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CliParams.java:66-73]: `-tx n/a`, not `-tx=n/a`. Only the
first occurrence of a valued flag counts.

### Build flags (verified in `Publisher.main` at 3.0.5)

IGPUB-DOCS lists 27 flags [src: IGPUB-DOCS-3.0.5 documentation.md#L24-L55]. It omits flags the code reads,
such as `-no-errors`, `-packages` and `-devtx`, so `Publisher.java` at the same tag is the authority.

| Flag | Effect | Evidence |
| --- | --- | --- |
| `-ig <folder or file>` | The IG to build | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1761] |
| `-tx <url>` / `-tx n/a` / `-devtx` | Terminology server; none; the development tx server. New in 3.0.x after 3.0.1: naming a server with `-tx` also turns the terminology ecosystem off, so every request goes to that server, unless `-ecosystem` is given too | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1955-1969] |
| `-ecosystem <url>` / `-ecosystem n/a` | The terminology ecosystem coordination server (tx-reg); default `https://ecosystem.hl7.org/tx-reg`. Not in 3.0.1 | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1478-1480] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1975-1981] |
| `-threads <n>` | Use up to n extra threads for parallel work, capped at one less than the number of cores; a value that isn't a whole number of 0 or more is an error. Not in 3.0.1 | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CliParams.java:13] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CliParams.java:42-64] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1947-1953] |
| `-rapido -watch` (or `-cascais -watch`) | Watch mode: rebuild when `ig.ini`, `sushi-config.yaml`, `publication-request.json`, `fsh.ini`, `input/`, `fsh/` or `fsh-generated/` changes. From 3.0.4 it waits for files to go quiet, ignores what the build itself wrote, and skips SUSHI when only page content changed (read from source; not yet observed) | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1666-1670] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:231-243] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:212-216] |
| `-no-network` | Prohibit all web access; output is correct only if the caches are complete | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1684-1696] |
| `-trust-template <id>` / `-trust-template all` | Let a template that runs scripts but isn't on the trusted list run locally (the id as the IG names it, without a version); recorded in `trustedTemplates` in `fhir-settings.json`, so it's needed once. Without it such a build stops. New in 3.0.5; see [templates.md](templates.md#how-a-template-chain-is-assembled) | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1764-1766] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/TemplateManager.java:196-221] |
| `-allow-external-links` | Allow symbolic links in the IG's folder that lead outside it, for all IGs; recorded as `allowExternalLinks` in `fhir-settings.json`, and the build then warns. Without it such a build stops; on the ci-build they are always refused. New in 3.0.5 | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1767-1769] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/ExternalLinkPermission.java:33-58] |
| `-ssrf-protection-enabled false` | Let the build reach private-network and plain-http servers. From 3.0.5 it is ignored on the ci-build (`-auto-ig-build`), where only public https servers are reached unless `fhir-settings.json` allows a server with `allowPrivateNetwork` or `allowHttp` | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1869-1875] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1878-1891] |
| `-no-sushi` | Don't run SUSHI even if `fsh/` or `input/fsh/` exists | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1813-1815] |
| `-validation-off` | Skip validation (for authoring only) | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1698-1701] |
| `-generation-off` | Skip narrative generation (for authoring only) | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1702-1705] |
| `-no-validate <type/id,…>`, `-no-narrative <type/id,…>` | Skip validation or narrative for the listed resources | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1676-1683] |
| `-resetTx`, `-resetTxErrors` | Clear the terminology cache, or only its cached errors | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1806-1812] |
| `-packages <folder>` | Load `*.tgz` packages from a folder before resolving dependencies. The help text says it may be repeated, but only the first value is read | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1490-1491] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1786] |
| `-package-cache-folder <folder>` | Use a different package cache. Not for everything: in a 3.0.4 build, one package needed while validating conformance resources went into the default `~/.fhir/packages` [src: PROBES-2026-11-14 RESULTS.md] | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1816-1818] |
| `-proxy <host:port>` | HTTP(S) proxy. The help text shows `-proxy=host:port`, which the exact-match parser doesn't recognise | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1514] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1774-1782] |
| `-debug` | Extra logging | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1796] |
| `-no-errors` | Exit with status 1 if the build has errors (see below) | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1825-1827] |
| `-no-exit` | Don't call `System.exit` (embedding) | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1852-1854] |

**Exit status.** It starts at 0 [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1407] and
becomes 1 only if the build throws, or if `-no-errors` is given and errors were found
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1823-1844]. **Without `-no-errors`, a build
with QA errors exits 0** (read from source; not yet observed). With `-no-errors`, a build that finished
with 1505 errors exited 1 [src: PROBES-2026-11-14 RESULTS.md], as a 3.0.1 build did [src: PROBES-2026-10-22 RESULTS.md]. For CI, pass `-no-errors` or read the
`errs` count in `qa.json`.

A template's `xsl:message terminate="yes"`, such as the missing-`ImplementationGuide.version` check,
surfaces as "Publishing Content Failed" followed by "This error was created by the template"
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1828-1832].

## Outputs

With the base template's defaults (`path-output` = `output`, `path-qa` = `temp/qa`; see
[layout.md](layout.md)):

| File | Contents | Evidence |
| --- | --- | --- |
| `output/qa.html` | The QA report: every message, by file, with suppressed messages counted | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:637] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/renderers/ValidationPresenter.java:918] |
| `output/qa.min.html` | The same report without hints | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/renderers/ValidationPresenter.java:918] |
| `output/qa.txt` | Plain-text messages, easiest to `grep` | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/renderers/ValidationPresenter.java:833] |
| `output/qa.compare.txt`, `output/qa-eslintcompact.txt` | Text forms for diffing between builds and for editors | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/renderers/ValidationPresenter.java:805] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/renderers/ValidationPresenter.java:861] |
| `output/qa.json` | Summary counts (`errs`, `warnings`, `hints`, suppressed counts) and run metadata. Its `tool` field is **not** the publisher version: 3.0.1 and 3.0.4 builds both wrote `6.0.0-snapshot1 (3)` | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:971-988] [src: PROBES-2026-11-14 run1-qa.json] |
| `output/qa-tx.html`, `output/qa-txservers.html` | Terminology server traffic and servers used | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:621] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/renderers/ValidationPresenter.java:650] |
| `<java.io.tmpdir>/fhir-ig-publisher.log` | Build report and log for a local (manual-mode) run | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1846-1848] |

The help text says it plainly: "The most important output from the publisher is qa.html"
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1504].

## ignoreWarnings.txt

The base template points `path-suppressed-warnings` at `input/ignoreWarnings.txt` unless the IG sets
another file [src: TPL-BASE-1.0.0 scripts/onLoad.xslt#L262-L267]. A missing file is an error
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:1708-1712].

**Format** [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:1713-1733]:

```text
== Suppressed Messages ==

# Reason the next messages are acceptable
The exact text of a message
Constraint failed: dom-6%
```

- The first line must be `== Suppressed Messages ==` (case-insensitive). Older files without it still
  load, but the publisher reports an error that the file isn't in the new format.
- A line starting with `#` and a space starts a reason, which applies to the messages after it. A message before any reason is an
  error.
- **Matching** is case-insensitive, against the message text, its HTML, its message id or its
  invariant id. A trailing `%` matches a prefix, a leading `%` a suffix, and both a substring
  [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/SuppressedMessageInformation.java:29-56]
  [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/SuppressedMessageInformation.java:83-95]
  [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/SuppressedMessageInformation.java:105-112].
  `Rule …' Failed (` is rewritten to the validator's current `Constraint failed: …' (` wording first.

**Errors in resource files are not suppressed.** The per-file listing filters only non-error messages
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/renderers/ValidationPresenter.java:496]
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/renderers/ValidationPresenter.java:1017]. A matching
error stays an error; the matched line only adds its reason as a comment
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/renderers/ValidationPresenter.java:1025-1031]. Errors not
tied to a file, such as broken links, can be suppressed
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/renderers/ValidationPresenter.java:507].
**Observed** on 3.0.1 and again on 3.0.4 [src: PROBES-2026-10-22 RESULTS.md]
[src: PROBES-2026-11-14 RESULTS.md]: lines matching 72 warnings and two errors were added to a copy of
EX-DQM-CMS-2025's file. Warnings fell by 72 and `suppressed-warnings` rose by 72. The two errors stayed
in `qa.txt` and in the error count, and `qa.html` showed each with "Editor's Comment :" and the reason.
The matched errors also raised `suppressed-hints` by 2, so that count includes errors that are still
reported.

**A publisher upgrade can make a line stop matching.** The warning line that worked on 3.0.1 matched
nothing on 3.0.4, because the message is now worded with the CQL translator's type labels
[src: PROBES-2026-11-14 RESULTS.md]. After upgrading, compare the `suppressed-*` counts in `qa.json`
with the previous build's.

EX-DQM-CMS-2025's own `ERROR:` lines [src: EX-DQM-CMS-2025 input/ignoreWarnings.txt:4-6] no longer even
match: they name `cms.madie`, `extension[10]` and value set `|0.7.1`, while 3.0.1 and 3.0.4 builds report
`madie.cms.gov.dqms`, `extension[13]` and `|1.3.0` [src: PROBES-2026-10-22 qa-excerpts.txt]
[src: PROBES-2026-11-14 qa-excerpts.txt].

## Reading a QA report

1. **Note the version.** Record the publisher version from `qa.txt`'s header ("IG Publisher Version:")
   or `-v` with any finding. Not `qa.json`'s `tool`.
2. **Start with errors in `qa.txt`.** `grep` it before opening `qa.html`.
3. **Check the IG resource's messages first.** `Unknown Parameters: […]` means a parameter code is
   handled by no layer: a typo, or a code a newer publisher reads
   (see [ig-ini-and-ig-resource.md](ig-ini-and-ig-resource.md#writing-a-parameter)).
4. **CQL messages.** See [cql-loader.md](cql-loader.md#messages-to-know).
5. **Before suppressing, read the reason.** Only warnings and hints can be suppressed (above).
