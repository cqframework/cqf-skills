# IG Publisher Skill Test Questions: Answer Key

Expected answers for [questions.md](questions.md). Don't give this file to an agent under test.

Facts are as the `ig-publisher` skill records them for IG Publisher 3.0.4 (checked unchanged at 3.0.5,
except TP-02, which is about 3.0.5), org.hl7.fhir.core 7.0.6,
cqf.fhir.template 1.0.0 and fhir.base.template 1.0.0, from the publisher source at those tags and the
probe builds in `resources/probes/`. Each answer gives the expected facts, what a passing answer must
and must not say, and where the skill covers it ("Skill").

## Configuration

### CF-01. A comment at the top of ig.ini

- **Expected:** the publisher uses `ig.ini` only if its text **starts with** `[IG]`. Anything before
  it (a comment, a blank line, a byte-order mark) makes the publisher act as if there were no
  `ig.ini`, hence the error. Move the comment below `[IG]` or remove it.
- **Pass if:** it says the file must start with `[IG]` and the comment is the cause.
- **Fail if:** it blames the comment syntax (`;` versus `#`) or the `-ig` path.
- **Skill:** `resources/ig-ini-and-ig-resource.md` (ig.ini); SKILL.md Known Gotchas.

### CF-02. An unpinned template

- **Expected:** with no `#version`, the package cache picks the version (the publisher calls
  `loadPackage(id, null)`; not traced further). The sample IG's comment that it takes `#current` is
  convention text, not what the code shows. Pin it: `template = cqf.fhir.template#1.0.0`. Yes: a
  template's base template is loaded at the version in its own `package.json` dependencies, so
  `cqf.fhir.template#1.0.0` pins `fhir.base.template#1.0.0`.
- **Pass if:** it recommends `#<version>` and says that pins the base template too.
- **Fail if:** it says the base template must be pinned separately, or states as fact that the
  latest version is always used.
- **Skill:** `resources/ig-ini-and-ig-resource.md` (The template value).

### CF-03. Where CQL comes from

- **Expected:** the `path-binary` IG parameter. No publisher or template default sets it, and the
  CQL step runs only if at least one `path-binary` folder is set; `input/cql` is a convention, not a
  default. Add `path-binary` = `input/cql` to the IG resource's `definition.parameter`.
- **Pass if:** it names `path-binary` and says nothing sets it by default.
- **Fail if:** it says the template provides `input/cql`, or suggests `path-resource`.
- **Skill:** `resources/cql-loader.md` (Turning it on); `resources/layout.md`.

### CF-04. Adding a resource folder

- **Expected:** no. fhir.base.template adds its eleven default resource folders (`input/resources`,
  `input/examples`, `input/profiles`, `fsh-generated/resources` and so on) alongside the IG's own
  `path-resource` values. Only `input/maps` is added just when the IG sets no `path-resource`.
- **Pass if:** it says the IG's value adds to the defaults.
- **Fail if:** it says the IG's value replaces the defaults.
- **Skill:** `resources/layout.md` (Where each folder comes from).

## The CQL loader

### CQ-01. Which translator

- **Expected:** cqframework 4.9.0 (3.0.1 bundled 3.29.0). The publisher version is on the
  "IG Publisher Version:" line at the top of `output/qa.txt`, or from `java -jar publisher.jar -v`.
  `qa.json`'s `tool` field is not the publisher version (3.0.1 and 3.0.4 both wrote
  `6.0.0-snapshot1 (3)`).
- **Pass if:** it gives 4.9.0 and the `qa.txt` header or `-v`.
- **Fail if:** it says the publisher uses the editor's or the latest translator, or reads the version
  from `qa.json`'s `tool`.
- **Skill:** SKILL.md Versions; `resources/cql-loader.md` (The translator is 4.9.0); `resources/running.md` (Outputs).

### CQ-02. Sub-folders

- **Expected:** nothing in the sub-folders: each `path-binary` folder is listed without recursion.
  Adding each sub-folder as its own `path-binary` gets them compiled, but once a second folder has
  CQL the subsystem drops its shared options and library manager, and later steps throw "CqlProcessor
  has been used with multiple Cql paths, ambiguous options and manager". The better fix is to keep all
  CQL in one folder.
- **Pass if:** it says sub-folders aren't compiled and recommends a single folder, or warns about
  the multiple-folder problem.
- **Partial if:** it recommends adding both sub-folders without the warning.
- **Fail if:** it says sub-folders are compiled.
- **Skill:** `resources/cql-loader.md` (What gets compiled).

### CQ-03. Inline CQL

- **Expected:** no. A `.cql` file's own translation errors are reported only when a Library claims
  it through an `ig-loader-` attachment; an unclaimed file gets only "CQL source was not associated…".
  The Libraries are published as written: an attachment with `data` is left alone, so there is no
  fresh ELM and no recomputed `dataRequirement`, `parameter` or `relatedArtifact`, and the inline CQL
  can drift from `input/cql`. Compile the CQL separately, or switch the Libraries to `ig-loader-`.
- **Pass if:** it says compile errors aren't reported and the Libraries aren't updated.
- **Fail if:** it treats the message as harmless or says the publisher adds ELM.
- **Skill:** `resources/cql-loader.md` (Libraries with embedded CQL).

### CQ-04. An ig-loader attachment with a content type

- **Expected:** yes on 3.0.4: an `ig-loader-` attachment may carry `contentType`, which is kept
  (so `text/cql; version=1.5` works); any other element means the attachment is left alone. On 3.0.1
  the attachment had to hold only `id`, so it would have been left alone.
- **Pass if:** it says yes for 3.0.4 and identifies the version difference.
- **Partial if:** it says yes without the version difference.
- **Fail if:** it says no for 3.0.4.
- **Skill:** `resources/cql-loader.md` (How a Library gets its CQL and ELM).

### CQ-05. "ELM generation failed"

- **Expected:** translation worked, but building the Library's ELM, parameters and data requirements
  threw, and that is only logged, never put in QA. The Libraries get no ELM, parameters or data
  requirements from the publisher. The publisher maps each parameter's and top-level define's type to
  a FHIR type; anything outside the System primitives, the `FHIR` namespace and Date, DateTime or
  Quantity intervals (a Tuple, an `Interval<Integer>`, a choice, a QICore or USQualityCore type)
  becomes `Any`, which `FHIRTypes.fromCode` rejects. One such define is enough. Read the console log.
- **Pass if:** it says it is logged only, that the ELM is missing, and names unmappable result
  types as the cause.
- **Partial if:** it gets the effect but not the cause.
- **Fail if:** it says the ELM is fine because translation succeeded.
- **Skill:** `resources/cql-loader.md` (ELM generation can fail without a QA message).

## Running and QA

### RN-01. A green CI build with errors

- **Expected:** the exit status starts at 0 and becomes 1 only if the build throws or `-no-errors`
  is given and errors were found. Add `-no-errors`, or read `errs` in `output/qa.json`.
- **Pass if:** it names `-no-errors` (or checking `qa.json`).
- **Skill:** `resources/running.md` (Exit status).

### RN-02. Suppressing an error

- **Expected:** no; errors in resource files are not suppressed. `ignoreWarnings.txt` hides warnings
  and hints (and link errors not tied to a file). A matched error stays an error, and `qa.html` shows
  the reason as an "Editor's Comment". Fix the cause instead.
- **Pass if:** it says errors can't be suppressed this way.
- **Fail if:** it suggests a different syntax will suppress the error.
- **Skill:** `resources/running.md` (ignoreWarnings.txt).

### RN-03. After an upgrade

- **Expected:** the message wording changed. 3.0.4, with translator 4.9.0, words the warning with
  the translator's type labels ("Result type tuple of codes:list<FHIR.Coding>, display:FHIR.string of
  definition SDE Race is not supported"), so a line written for 3.0.1's wording no longer matches.
  Rewrite the line (a `%…%` substring such as `%of definition SDE Race is not supported%` is
  robust), and after each upgrade compare the `suppressed-*` and `warnings` counts in `qa.json` with
  the previous build's.
- **Pass if:** it identifies changed wording and suggests comparing counts or a looser pattern.
- **Skill:** `resources/running.md` (ignoreWarnings.txt); `resources/probes/2026-11-14/RESULTS.md`.

### RN-04. A proxy

- **Expected:** the flag parser matches `-proxy` exactly and reads the next argument; the
  `-proxy=host:port` form in the help text isn't recognised. Use `-proxy proxy.example.org:8080`.
- **Pass if:** it gives the space-separated form.
- **Skill:** `resources/running.md` (Build flags).

## Terminology and templates

### TX-01. A private terminology server

- **Expected:** in 3.0.4, `-tx <url>` also turns off the terminology ecosystem (the tx-reg
  coordination server, default `https://ecosystem.hl7.org/tx-reg`) unless `-ecosystem <url>` is given
  too. So the private server answers every request, including for code systems tx.fhir.org would
  have routed to another server. In 3.0.1 `-tx` only replaced tx.fhir.org. Read from source; not
  observed.
- **Pass if:** it mentions the ecosystem being turned off and `-ecosystem`.
- **Fail if:** it says only the server address changes.
- **Skill:** `resources/terminology.md` (The terminology server).

### TX-02. Expansion parameters

- **Expected:** `input/resources/parameters/expansion.json`. `path-expansion-params` is relative to
  the folder of the IG resource, not the IG root like every other `path-*` parameter.
- **Pass if:** it gives that path and the reason.
- **Fail if:** it gives `resources/parameters/expansion.json` under the IG root.
- **Skill:** `resources/terminology.md` (Expansion parameters).

### TX-03. Pinned versions

- **Expected:** in the published Parameters resource (`output/Parameters-manifest.json`): the
  publisher adds `system-version`, `default-valueset-version` and `default-canonical-version`
  parameters to the resource named by `pin-manifest`, and uses it as the expansion parameters. The
  resources themselves are left unversioned. In the probe builds the manifest went from 1 parameter
  in to 764 out. The input file doesn't change, and another run can pin different versions.
- **Pass if:** it says the output manifest, not the input or the resources.
- **Skill:** `resources/terminology.md` (Pinning canonical versions).

### TP-01. A custom Measure narrative after a template upgrade

- **Expected:** fhir.base.template 1.0.0 ships its own Liquid for ActivityDefinition, Library,
  Measure and PlanDefinition (0.8.1 shipped none). It adds `template/liquid` and then `input/liquid`
  as `path-liquid` *after* the IG's own values, and the last one loaded wins, so the template's
  `Measure.liquid` replaces the IG's. Options: move the file to `input/liquid` (loaded after
  `template/liquid`), or use `path-liquid-ig`, which loads last but isn't defined in the tools
  CodeSystem, so an R4 IG gets two QA errors on the IG resource that can't be suppressed.
- **Pass if:** it says the template now ships `Measure.liquid` that loads after the IG's folder,
  and gives `input/liquid` or `path-liquid-ig`.
- **Partial if:** it gives a working fix without the cause, or `path-liquid-ig` without its cost.
- **Skill:** `resources/templates.md` (Liquid narrative templates).

### TP-02. Working on the template

- **Expected:** from 3.0.5, a local build stops when a template that runs scripts isn't on the trusted
  list; a folder isn't a trusted template (before 3.0.5 a local build ran any template). Run once with
  `-trust-template ../my-template` (the id as `ig.ini` names it, without a version) or
  `-trust-template all`; it's recorded in `trustedTemplates` in `fhir-settings.json`, so later builds
  don't stop. On the ci-build, `#dev` isn't a released version, so `cqf.fhir.template#dev` is treated as
  untrusted and its scripts don't run; only `n.n.n`, `#current` or no version are trusted.
- **Pass if:** the 3.0.5 local trust check, `-trust-template`, and no for `#dev`.
- **Partial if:** `-trust-template` without the `#dev` answer, or the reverse.
- **Fail if:** it blames the template's content or suggests copying the template into `template/`.
- **Skill:** `resources/templates.md` (How a template chain is assembled); `resources/running.md` (Build flags).

## Versions

### VR-01. A newer publisher

- **Expected:** the skill's claim (yes, `contentType` is kept and anything else makes the publisher
  leave the attachment alone) is for 3.0.5. For 3.0.7, read the cited code, `AdjunctFileLoader.java`
  around the cited lines, at tag `3.0.7` on GitHub
  (`https://github.com/HL7/fhir-ig-publisher/blob/3.0.7/org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/loaders/AdjunctFileLoader.java`),
  finding it by content because line numbers drift. If it's unchanged, the answer holds; if it
  changed, answer from the 3.0.7 code and say it is read from source, not observed.
- **Pass if:** it gives the 3.0.5 answer as the starting point, says it is version-specific, and
  checks (or says to check) the same code at 3.0.7.
- **Fail if:** it states the 3.0.5 behaviour as fact for 3.0.7 without qualification, or answers
  from the publisher's main branch.
- **Skill:** SKILL.md (When the IG Was Built With Another Version); `resources/SOURCES.md`.

## Debugging

### DB-01. Review this set-up

- **Expected:** five problems:
  1. `ig.ini` starts with a comment, so the publisher ignores it ("unable to find an ig.ini").
  2. The template isn't pinned; use `cqf.fhir.template#1.0.0`.
  3. `Screening.cql` is in a sub-folder of the `path-binary` folder, so it isn't compiled. Move it to
     `input/cql` (or point `path-binary` at `input/cql/libraries`).
  4. The Library's attachment has `data` as well as `id`, so the publisher leaves it alone. It must
     hold only `id` (and optionally `contentType`).
  5. The Measure's library canonical ends in `screening-logic`, but the publisher finds the CQL
     library by matching the canonical's last segment to the CQL library name, `Screening`, so no
     data requirements are inferred ("Artifact library could not be found…"). Make the Library's
     `url` end in `/Screening`.
- **Pass if:** it finds at least four, including 3 and 4.
- **Partial if:** it finds 3 and 4 only.
- **Skill:** SKILL.md Known Gotchas; `resources/cql-loader.md`.

## Task

### TK-01. Set up an IG that compiles a measure's CQL

Run `python grade_ig.py <answer>/tk-01`. It checks:

- `ig.ini` starts with `[IG]`, pins `cqf.fhir.template#x.y.z` and names an existing IG resource;
- the IG is R4 and sets `path-binary` (as a parameter or the `ig-parameter` extension);
- `ExampleScreening.cql` is directly in a `path-binary` folder, and CQL is in only one such folder;
- the Library claims it with `content` = `[{"id": "ig-loader-ExampleScreening.cql"}]`, with nothing
  but `id` and optionally `contentType`, and its `url` ends in `/ExampleScreening`;
- the Measure has exactly one library, whose canonical ends in `/ExampleScreening`;
- `input/ignoreWarnings.txt` starts with `== Suppressed Messages ==` and each message follows a
  `# ` reason.

- **Pass if:** every check passes. If the agent ran the publisher, also check its Library output
  has `application/elm+xml` or `application/elm+json` content.
- **Partial if:** one check fails.
- A grader pass doesn't prove the build gets ELM: a define with a Tuple or `Interval<Integer>`
  result would still lose it (see CQ-05). For a full check, build it as described in the README.
- **Reference:** [reference/tk-01/](reference/tk-01/). Built with IG Publisher 3.0.4 and
  `-tx n/a`, its Library got `application/elm+xml` content, six parameters and two data
  requirements, and the suppression line hid all three warnings it targets.
