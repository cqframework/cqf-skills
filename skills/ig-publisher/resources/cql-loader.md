# The CQL Loader

Baseline: IG Publisher 3.0.5, which bundles the cqframework translator 4.9.0 (as 3.0.4 does; its CQL code is unchanged). Untagged statements hold at this version only.
Sources: IGPUB-3.0.5, CORE-7.0.6, TOOLS-1.3.0, SAMPLE-IG, EX-DQM-CMS-2025, VSCQL, PROBES-2026-10-22, PROBES-2026-11-14

How the publisher compiles CQL and attaches it to Library resources. Everything here comes from reading
the publisher's source, checked where noted against a publisher 3.0.4 build
[src: PROBES-2026-11-14 RESULTS.md]. Statements marked **not yet observed** have not been confirmed by
running it.

## Turning it on

The only switch is the `path-binary` IG parameter: "Relative path to a location in the IG repository
in which to look for binary adjunct files. These files are only used in the context of the CQL loader"
[src: TOOLS-1.3.0 CodeSystem-ig-parameters.json#path-binary]. Each value adds a folder
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:606-607], and the CQL step
runs only if there is at least one [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:2624-2627].
No publisher or template default sets `path-binary` (see [layout.md](layout.md)), so an IG without it
compiles no CQL.

## The translator is 4.9.0

IG Publisher 3.0.5 (like 3.0.4) builds against `info.cqframework` 4.9.0
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/pom.xml:19]. 3.0.1 used 3.29.0; the move to 4.9.0 came in
between. The `cql` skill records translator and engine behaviour at a different version (5.4.0), and
editors use their own. A library can compile one way in an editor and another way in the publisher.
When the publisher's result is what counts, as in the published Library's ELM, test against the
publisher's translator version or run the publisher.

## What gets compiled

For each `path-binary` folder, separately
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:335-352]:

1. **Options.** `cql-options.json` in that folder, or the translator's defaults if there is none
   [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:493-505]. Optionally
   `cql-publisher-options.json` too [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:474-486].
2. **Model info first.** Every file whose name contains `-modelinfo` (case-insensitive)
   [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:789-796]. Only XML model info is
   read: a `.json` model info file now fails with "JSON ModelInfo Support is not available in the
   publisher" [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:686-697].
3. **Then every `*.cql` file** [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:798-805].

Both steps use `listFiles` on the folder itself
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:590-601], so **sub-folders are not
compiled**. Add each sub-folder as its own `path-binary` instead.

`include`d libraries resolve from Library resources in the IG's dependency packages, then from the same
folder, then from the translator's built-in FHIR libraries
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:580-584]. A package Library's CQL is
found by its content type, which may now carry media-type parameters, such as `text/cql; version=1.5`
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:150-159]. Model info from a package is
looked up by model name and version only, not by its system URL
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:180-184].

**CQL in more than one folder.** After a second folder with CQL, the subsystem drops its shared options
and library manager [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:603-619], and
any later step that needs them throws "CqlProcessor has been used with multiple Cql paths, ambiguous
options and manager" [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:507-516].
Keeping all CQL in one folder avoids this.

## How a Library gets its CQL and ELM

A Library opts in with a `content` attachment whose `id` is `ig-loader-` plus a file name. Since 3.0.x
after 3.0.1 it may also carry a `contentType`, which is kept; any other element (`data`, `url`, `size`
and so on) means the attachment is left alone
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/loaders/AdjunctFileLoader.java:292-322]. The SAMPLE-IG
Library [src: SAMPLE-IG input/examples/Library-example.json#L23-L25]:

```json
"content": [ {
  "id": "ig-loader-example.cql"
} ]
```

The publisher then [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/loaders/AdjunctFileLoader.java:81-115]:

1. looks for the file in each `path-binary` folder, in order, and takes the first match
   [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/loaders/AdjunctFileLoader.java:245-256];
2. replaces the attachment with the file's bytes. The content type is the attachment's own, if it has
   one, or else set from the extension (`.cql` gives `text/cql`)
   [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/loaders/AdjunctFileLoader.java:96-99]
   [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/loaders/AdjunctFileLoader.java:259-290];
3. for CQL, matched by media type so that `text/cql; version=1.5` counts
   [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/loaders/AdjunctFileLoader.java:101]
   [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/loaders/AdjunctFileLoader.java:117-124], adds
   `application/elm+xml` and `application/elm+json` content as `cql-options.json` `formats` asks, and
   **replaces** the Library's `dataRequirement`, `parameter` and `depends-on` `relatedArtifact` entries
   with what the translator found [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/loaders/AdjunctFileLoader.java:377-397].

**Data requirements** are now computed by the translator's DataRequirementsProcessor at the QM STU1
specification level, and converted from R5 [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:955-977].
3.0.1 built them from the library's retrieves directly. The results may differ; that hasn't been
compared.

**Measures and other knowledge artifacts.** For a Measure, ActivityDefinition, PlanDefinition or
Questionnaire with exactly one library, the publisher computes effective data requirements from the
compiled CQL [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:1353-1372]. It finds the
library by matching the **last path segment of the library canonical** to the CQL library's name
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:1374-1392] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:1434].
If none matches, it warns "Artifact library could not be found so no data requirements were inferred."
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:1440-1445].

## Libraries with embedded CQL

EX-DQM-CMS-2025's Libraries carry their CQL inline, base64 `data` with a `url`
[src: EX-DQM-CMS-2025 input/resources/library/AdultOutpatientEncounters.json:33-36]. None of its 89
Library files uses `ig-loader-` (searched at 46b11c3). The source reading predicts, and publisher builds
of a copy of that IG confirmed:

- **The Library is published as written.** Its attachment has `data`, so the publisher doesn't replace
  it, add ELM or recompute `dataRequirement`, `parameter` or `relatedArtifact` (see above). Whatever
  wrote the file decides what is published, so the inline CQL can drift from `input/cql/*.cql`.
- **Each `.cql` file still compiles, but its own errors go unreported.** A file's translation errors
  are reported only when a Library claims it through `ig-loader-`
  [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/loaders/AdjunctFileLoader.java:377-380]; that is the
  only caller of `getFileInformation`, which marks a file as claimed
  [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:359-379]. Each unclaimed file gets
  one error instead, "CQL source was not associated with a library resource in the IG."
  [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:390-398], reported through
  `getGeneralErrors` [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherProcessor.java:115].
  Model info files in the folder get the same message.
- **Measures are still processed**, with an effective data requirements Library recomputed from the
  compiled `input/cql` library, matched by name as above.

The observations for 3.0.1 and 3.0.4 are in [Observed builds](#observed-builds) below.

**So in such an IG, `qa.html` is not a CQL compile check.** Compile the CQL separately, for example in
the editor or with the cqframework translator, or give each Library an `ig-loader-` attachment so the
publisher reports the errors.

## ELM generation can fail without a QA message

After a successful translation, the publisher builds ELM and extracts related artifacts, parameters and
data requirements, in that order. If any of it throws, the exception is only logged, as "CQL
Translation succeeded for file: '…', but ELM generation failed with the following error: …"
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:736-778].

**The usual cause is "Unknown FHIRTypes code 'Any'"** (by code reading; the observed failures are below).
Each parameter and each top-level define needs a FHIR type for the Library's `parameter` list. The
publisher maps only the CQL System primitives, types in the `FHIR` namespace, and intervals of Date,
DateTime or Quantity; every other type, such as a Tuple, an `Interval<Integer>`, a choice, or a type
from any other model (QICore, USQualityCore and so on), becomes `"Any"`
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:1110-1155]. It then calls
`Enumerations.FHIRTypes.fromCode` [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:1058]
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:1071], which has no `Any` code and
throws [src: CORE-7.0.6 org.hl7.fhir.r5/…/model/Enumerations.java:9045-9510]. So **a library with even
one such define or parameter gets no ELM, parameters or data requirements** from the publisher, and a
library written against a model other than FHIR almost always has one. The warning that the type "is
not supported" is added just before the throw. For an IG whose Libraries use `ig-loader-`, read the
console log, not just QA.

## Messages to know

| Message | Meaning | Evidence |
| --- | --- | --- |
| `CQL Processing failed with (N) errors.` | The file didn't compile; each translator exception is listed with it | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:730-734] |
| `No cql info found for <file>` | An `ig-loader-` file was found but never compiled, for example because it sits in a sub-folder (inferred from the two steps above) | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/loaders/AdjunctFileLoader.java:393-395] |
| `CQL source was not associated with a library resource in the IG.` | A `.cql` or model info file no Library claimed through `ig-loader-`. It replaces that file's own translation errors | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:395] |
| `Unable to find Adjunct Binary <file> in any path-binary folder (…)` / `… : no path-binary parameters are defined in the IG` | An `ig-loader-` name matched no file. Since 3.0.x after 3.0.1 the message names the folders searched, or says there are none | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/loaders/AdjunctFileLoader.java:231-243] |
| `… but ELM generation failed with the following error: …` | Log only, not QA: translation succeeded, then building ELM or extracting related artifacts, parameters or data requirements threw | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:777] |
| `File with a similar name but different casing was found.` | Log only, not QA: a claimed file name differs only in case | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:368-373] |
| `JSON ModelInfo Support is not available in the publisher` | A `*-modelinfo*.json` file. Use XML model info | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:690-693] |
| `Artifact is using … FHIR-ModelInfo …` (four variants) | Information: the publisher rewrote a model-info dependency, depending on whether the IG depends on `fhir.cqf.common#4.0.1` or `hl7.fhir.uv.cql` 2+ | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:542-568] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:1467-1594] |

## Observed builds

Builds of a copy of EX-DQM-CMS-2025 at 46b11c3, whose 103 `.cql` files sit in `input/cql` and whose 89
Libraries embed their CQL:

| | IG Publisher 3.0.1 (translator 3.29.0) | IG Publisher 3.0.4 (translator 4.9.0) |
| --- | --- | --- |
| "ELM generation failed … Unknown FHIRTypes code 'Any'" (log only) | 95 files, 89 of the 90 that aren't `test*` probe libraries | the same |
| Completed translation and ELM | 4, including `NHSNHelpers.cql` | the same |
| Failed translation | 4 `test*` files, with 2, 2, 166 and 1 errors | the same |
| "CQL source was not associated…" in `qa.txt` | 104, the whole of "Build Errors : 104" | the same |
| "CQL Processing failed" in `qa.txt` | 0 | 0 |
| Published Libraries with ELM content | 0 of 89; CQL `data` identical to the input | the same |
| Evidence | [src: PROBES-2026-10-22 RESULTS.md] | [src: PROBES-2026-11-14 RESULTS.md] [src: PROBES-2026-11-14 log-excerpts.txt] |

So the move to translator 4.9.0 changed none of these outcomes for this IG. One thing did change: the
wording of the publisher's "not supported" type warnings, which now uses the translator's type labels,
such as "Result type tuple of codes:list<FHIR.Coding>, display:FHIR.string of definition SDE Race is
not supported" [src: PROBES-2026-11-14 run2-qa-excerpts.txt]. `ignoreWarnings.txt` lines written for
3.0.1's wording no longer match (see [running.md](running.md#ignorewarningstxt)).

## Test cases

`input/tests/` is not read by the publisher's CQL loader. It is a CQF and MADiE convention read by other
tools. The VS Code CQL extension reads it from a hard-coded path
[src: VSCQL src/model/cqlProject.ts:230-232].
