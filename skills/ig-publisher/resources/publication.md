# The Publication Process (`-go-publish`)

Baseline: IG Publisher 3.0.5. Untagged statements hold at this version only.
Sources: IGPUB-3.0.5

How a built IG becomes a published version on a FHIR website: what `-go-publish` checks, what it builds
again, and what it writes. Everything here is from reading `PublicationProcess.java` at 3.0.5 (its changes since 3.0.1 only close files properly and, in 3.0.5, add commented-out package signing); the
process was not run. No pinnable guide was found: FHIR/ig-guidance has no page on it, and the HL7
Confluence pages can't be pinned (see [SOURCES.md](SOURCES.md)).

This is a website owner's tool. It needs a local copy of the whole website (with its
`publish-setup.json`, `package-registry.json` and history templates), and it changes that copy.

## Running it

```sh
java -jar publisher.jar -go-publish \
  -source /abs/path/to/ig -web /abs/path/to/website -registry /abs/path/to/fhir-ig-list.json \
  -history /abs/path/to/history-template -templates /abs/path/to/templates -temp /abs/path/to/temp \
  [-zips /abs/path] [-date yyyy-mm-dd] [-tx <url>]
```

The flags [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1552-1555]:

- **Every path must be absolute**, or nothing else is checked
  [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:185-196].
- `-date` defaults to today [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:135-141].
- `-tx` is passed on to the publication builds
  [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:652-656].
- `-upload-server` is rejected: "Uploading files by FTP is no longer supported"
  [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:219-221].

**Exit status starts at 1** and becomes 0 only when publication finishes
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:51]
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:819]
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:166]. Check failures are
printed, one per line, before exit.

## What the IG folder must contain

The `-source` folder is an IG that has already been built normally:

- `output/qa.json` and `output/package.tgz` from that build
  [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:282-289];
- `publication-request.json` at the root, and **no** `package-list.json` there ("must not exist")
  [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:250-256].

### publication-request.json

The fields the 3.0.5 code reads:

| Field | Used for | Evidence |
| --- | --- | --- |
| `package-id` | Must equal the package's id; selects the website's layout rule | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:265-272] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:291-293] |
| `version` | Must be semver and equal the built IG's version | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:260-262] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:458] |
| `path` | The version's URL; must be `<canonical>/<last segment>` unless the website allows a mismatch. Its last segment names the version folder | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:460-464] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:473] |
| `mode` | `working` (the default), `milestone`, `technical-correction`, `creation` or `withdrawal`; anything else stops the run | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:81-109] |
| `status`, `sequence` | Written into the new `package-list.json` entry | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:1248] |
| `desc` or `descmd` | Required. `descmd` may be `@file`, read relative to the IG folder. `changes` is added too | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:459] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:1261-1271] |
| `first` | First publication: creates `package-list.json`, and then also requires `category`, `title`, `introduction`, `ci-build`, `registry-description`, `registry-country` and `registry-authority` | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:383-410] |
| `publish-pattern` | `current-only`: keep only the latest version (only `package.tgz` goes into the version folder) | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:407-409] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:679-690] |
| `allow-current-dependencies` | Without it, a dependency on a `current`, `cibuild` or `dev` version stops the run (except in `creation` mode) | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:367-380] |
| `movedFrom`, `previouslyPublishedAs` | The IG moved from another location or package id on the same website | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:411-437] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:486-500] |
| `registry-reason`, `replacement` | Withdrawal only: the reason, and the replacing specification | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:1375] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:1490-1491] |

## The checks, before anything is written

Against the website copy [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:225-248]
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:438-455]:

- `publish-setup.json` exists and has a layout rule for this package id;
- `package-registry.json` exists and `publish-counter.json` doesn't;
- the IG's `package-list.json` on the website names the same id and canonical, has a category and a
  CI-build entry, and has **no** entry for this version yet.

Against the built IG [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:467-471]:
`qa.json` must report the same package id, IG version, FHIR version and canonical, and must have an `errs`
count.

Against the destination [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:477-484]:
the IG's folder must already exist ("must be set up manually for first publication"), its version folder
must not, and the templates folder must have `header.template`, `preamble.template` and
`postamble.template`.

If the canonical doesn't match the layout rule, that is only printed, not counted as a failure
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:303-309].

## What it does

1. **Works on a copy of the website.** It clears `<temp>/web-root/run-<yyyyMMdd>` and copies in only the
   files it needs [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:208-215].
2. **Builds the IG again,** in a temporary clone of the source, with `-publish <path> -no-exit -resetTx`
   [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:648-657]. Except in `working`
   mode, it builds a second time with `-milestone`
   [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:659-663]. A build that leaves
   no `output/qa.json` stops the process.
3. **Zips the build folder** into `-zips`, by default inside the working root
   [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:666-673].
4. **Copies the output into the version folder**
   [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:676-690] and **adds the version
   to `package-list.json`**. A milestone or technical correction becomes `current`
   [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:1232-1279].
5. **For a milestone, replaces the IG's root folder** with the milestone build. Files that exist only in
   the old root are deleted first, apart from the history files, `package-list.json`,
   `package-registry.json`, `publish-setup.json` and `web.config`
   [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:756-771].
6. **Updates the website's feeds, the package registry and the IG's history page**
   [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:796-811].
7. **Copies the whole working root back over `-web`**
   [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:815]
   [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/WebSourceProvider.java:150-159]. Uploading the
   website is then up to its owner.

`creation` mode skips the builds and only creates an empty history for a new IG
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:643-644]. A technical correction
needs `tech-correction.template.html` and a different version from the current one, and archives the
corrected version first [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:517-532].

## Possible defects, by code read

Not run; each is what the code at 3.0.5 appears to do (unchanged since 3.0.1).

- **The "no increase in errors" guard never fires.** After each publication build, `compareJsonProp` is
  meant to stop the process if errors, warnings or hints went up since the draft. It reads the new count
  from the draft's `qa.json` as well (`int newv = qa.asInteger(name)`, where the new file is `nqa`), so the
  two counts are always equal [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:1292-1327].
- **A withdrawal given as a request file does nothing.** If `-source` is a `.json` file with
  `"mode": "withdrawal"`, `publishInner` returns `null` with the actual call commented out
  [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:201-207], and `publish`
  then calls `size()` on that result. The withdrawal path that does run is the one reached through the IG
  folder's `publication-request.json` [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/PublicationProcess.java:275-279].
- **Deleting stale files in the website source.** `finish` builds each path to delete as
  `path(s, existingFilesBase, s)`, with the file name both first and last
  [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/web/WebSourceProvider.java:150-156], which doesn't look
  like a path under the website source. In a milestone, the stale files are already deleted inside the
  working root (step 5); whether they then disappear from `-web` too was not traced.
