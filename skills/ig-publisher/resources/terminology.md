# Terminology: Servers, Caches, Expansion Parameters and Pinning

Baseline: IG Publisher 3.0.5 (org.hl7.fhir.core 7.0.6), fhir.base.template 1.0.0, hl7.fhir.uv.tools 1.3.0. Untagged statements hold at these versions only.
Sources: IGPUB-3.0.5, CORE-7.0.6, TPL-BASE-1.0.0, TOOLS-1.3.0, TOOLS-PAGES-1.3.0, EX-DQM-CMS-2025, PROBES-2026-10-22, PROBES-2026-11-14

How the publisher talks to a terminology server, what it caches locally, and how an IG fixes which
code system and value set versions are used. For running a build, see [running.md](running.md).

## The terminology server

| Setting | Server used | Evidence |
| --- | --- | --- |
| no flag | The production server from `fhir-settings.json`, default `https://tx.fhir.org`, with the terminology ecosystem | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1955-1969] [src: CORE-7.0.6 org.hl7.fhir.utilities/…/settings/FhirSettingsPOJO.java:23-26] |
| `-devtx` | The development server, default `https://tx-dev.fhir.org`, with the ecosystem | same |
| `-tx <url>` | That server, and **no ecosystem**: every terminology request goes to it, unless `-ecosystem <url>` is given too | same |
| `-tx n/a` (any value without `:`) | None: "WARNING: Running without terminology server - terminology content will likely not publish correctly" | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:1160-1163] |

**`fhir-settings.json`** is read from the `-fhir-settings <file>` flag
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1865-1866], else the
`fhir.settings.path` Java system property, else `~/.fhir/fhir-settings.json`
[src: CORE-7.0.6 org.hl7.fhir.utilities/…/settings/FhirSettings.java:225-240]
[src: CORE-7.0.6 org.hl7.fhir.utilities/…/settings/FhirSettings.java:279-280]. It can override both
default server addresses.

**The terminology ecosystem** (new in IG Publisher 3.0.x after 3.0.1, with org.hl7.fhir.core 7.0.6). The
ecosystem coordination server (tx-reg), default `https://ecosystem.hl7.org/tx-reg`, is consulted to find
which server is authoritative for a code system or value set, and requests are routed on to it. `-ecosystem <url>` names another, and
`-ecosystem n/a` turns it off [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:1971-1981]
[src: CORE-7.0.6 org.hl7.fhir.utilities/…/settings/FhirSettings.java:166-175]. This changes what `-tx`
means: in 3.0.1 it only replaced tx.fhir.org; from 3.0.4 it also turns the ecosystem off unless
`-ecosystem` is given, so a private server then answers every request, including for code systems that
tx.fhir.org would have routed elsewhere (read from source; not yet observed).

The probe builds used `https://tx.fhir.org` [src: PROBES-2026-10-22 log-excerpts.txt]; the 3.0.4 build
also logged the ecosystem in use [src: PROBES-2026-11-14 log-excerpts.txt].

## The local terminology cache

The publisher keeps server answers in a folder: `path-tx-cache`, which fhir.base.template sets to
`input-cache/txcache` unless the IG sets it [src: TPL-BASE-1.0.0 scripts/onLoad.xslt#L256-L261]. Without
the template default, it is `<root>/txCache` [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:426].
From 3.0.5 it must be inside the IG's folder, or it is ignored (see [layout.md](layout.md#path-values-on-each-platform)),
and it is cleared without following links.
At start-up [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:1122-1135]:

| Mode | What happens to the cache folder |
| --- | --- |
| `-resetTx` | Every file deleted |
| `-resetTxErrors` | Only cached errors deleted |
| CI auto-build | Every file deleted except `snomed.cache`, `loinc.cache` and `ucum.cache` |
| otherwise | Left alone; the log reports how many files it holds |

Because the cache answers instead of the server, a build can pass with a stale answer. When terminology
results look wrong, or after a value set changes on the server, re-run with `-resetTx`, or with
`-resetTxErrors` to retry only what failed.

**The server-side cache** is a separate thing: a protocol (`$cache-control`) that lets a client send each
value set or code system to the server once per build and then refer to it by URL
[src: TOOLS-PAGES-1.3.0 terminology-caching.md#L1-L21]. A server that loses the cache answers with the
`cache-id-unknown` issue, which means the cache is gone, not that a value set is missing
[src: TOOLS-PAGES-1.3.0 terminology-caching.md#L25-L30]. The page also warns that caching makes any
disagreement about which version a versionless reference means worse, and recommends pinning versions
explicitly [src: TOOLS-PAGES-1.3.0 terminology-caching.md#L82-L86], which is what the next two sections do.

## Expansion parameters

`path-expansion-params` names a Parameters resource used for every expansion
[src: TOOLS-1.3.0 CodeSystem-ig-parameters.json#path-expansion-params].

- **Its path is relative to the folder of the IG resource**, not the IG root as every other `path-*`
  parameter is. The publisher joins it to the directory of the file `ig.ini`'s `ig` key names
  [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:1172-1176]. EX-DQM-CMS-2025's IG
  resource is `input/dqm-content-cms-2025.xml` [src: EX-DQM-CMS-2025 ig.ini:2], so its value
  `resources/parameters/Parameters-manifest.json` [src: EX-DQM-CMS-2025 input/dqm-content-cms-2025.xml:186-187]
  means `input/resources/parameters/Parameters-manifest.json`.
- Setting it also adds an extension to the IG pointing at `Parameters/expansion-parameters`, and saves the
  parameters actually used as `parameters-expansion-parameters.json` and `.xml` in the temp folder
  [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:553-557]
  [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherGenerator.java:312-319]. Those files were not
  in the probe build's IG folder after the run (searched by name), so the temp folder may be cleaned
  later in the build; not traced.

**`ig-expansion-parameters`** (possible defect, by code read). The IG parameter is stored in a map under
its own code [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:579-581]. The loop that
applies it iterates the map's **values** and looks each one up as a **key**, so it adds a parameter named
after the IG parameter's value, with the value `expParamMap.get(<that value>)`, which is null unless the
value happens to equal the code [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:1177-1182].
Because the key is always the same code, only the last such IG parameter survives. Not run; a local probe
with no terminology call could confirm it. Prefer `path-expansion-params`.

## Pinning canonical versions

`pin-canonicals` decides whether the publisher fixes the version of unversioned canonical references,
for example a value set's `compose.include.system` or a profile's binding
[src: TOOLS-1.3.0 CodeSystem-ig-parameters.json#pin-canonicals]:

| Value | Effect | Evidence |
| --- | --- | --- |
| `pin-none` (default) | No pinning | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherFields.java:358] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:926-938] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherBase.java:803-813] |
| `pin-all` | Every unversioned reference whose target has a version | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherBase.java:829-877] |
| `pin-multiples` | Only where more than one version of the target is loaded | same |
| anything else | Build stops: "Unknown value for 'pin-canonicals'" | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:936-937] |

Each pin adds an information message, "Pinned the version of `<url>` to `<version>`". References from
`ImplementationGuide.dependsOn` are never pinned
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherBase.java:1684-1716].

**Where the version goes** depends on `pin-manifest`
[src: TOOLS-1.3.0 CodeSystem-ig-parameters.json#pin-manifest]:

- **Without it**, the version is written into the resource: `system|version` on the canonical, or
  `compose.include.version` [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherBase.java:849-876].
- **With it**, the resources are left alone. The value is the **id** of a Parameters resource in the IG.
  The publisher adds `system-version` (code systems), `default-valueset-version` (value sets) or
  `default-canonical-version` (anything else) parameters to it
  [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherBase.java:1760-1803], and uses that Parameters
  resource as the expansion parameters [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:4994-4998].
  A missing resource stops the build ("Unable to find nominated pin-manifest"). So does a version that
  conflicts with one already in the manifest.

The QA summary line reports the count, for example `pinned = N (all) (in manifest Parameters/<id>)`
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/Publisher.java:783-793].

### Example: one cqf measure IG

EX-DQM-CMS-2025 sets `pin-canonicals` = `pin-all` and `pin-manifest` = `manifest`
[src: EX-DQM-CMS-2025 input/dqm-content-cms-2025.xml:190-195], and points `path-expansion-params` at the
same Parameters resource (above). Its `ignoreWarnings.txt` hides the per-pin messages with
`%Pinned the version of%` [src: EX-DQM-CMS-2025 input/ignoreWarnings.txt:13]. In the probe build
[src: PROBES-2026-10-22 run3-pinning.txt]:

- the QA summary read "pinned = 4854 (all) (in manifest Parameters/manifest)";
- the manifest went from 1 parameter in the input to 764 in the output: 626 `default-valueset-version`,
  123 `default-canonical-version` and 15 `system-version`. A 3.0.4 build gave the same counts
  [src: PROBES-2026-11-14 run1-output-checks.txt].

So the published manifest, not the input file, records the versions this build used. A different
publisher run, cache state or package set can pin different versions.

## Parameterised value sets

The tools IG defines a way to declare parameters on a value set and supply their values at the binding,
mainly for Questionnaires (for example, regions that depend on a chosen country)
[src: TOOLS-PAGES-1.3.0 parameterized-valuesets.md#L5-L20]. Its own page calls the profile usage "as yet
unexplored". It is not used by EX-DQM-CMS-2025, and this skill doesn't cover it further.
