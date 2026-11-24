---
name: ig-publisher
description: Configures, runs and debugs the HL7 FHIR IG Publisher for an Implementation Guide, including ig.ini, IG parameters (path-binary, path-resource, path-liquid…), which input folders come from the template and which from the IG, the CQL loader and ig-loader Libraries, command-line flags, terminology servers and pinning, qa.html and ignoreWarnings.txt. Use when someone builds a FHIR IG, asks why the publisher did something, or reads a QA report. Pinned to IG Publisher 3.0.5, hl7.fhir.uv.tools 1.3.0 and cqf.fhir.template 1.0.0.
license: Apache-2.0
---

# IG Publisher

The HL7 IG Publisher turns an ImplementationGuide resource and its folders into a FHIR IG website,
an NPM package and a QA report. This skill covers configuring and running it, and reading what it
reports. For FHIR resource patterns use the `fhir` skill. For FSH and SUSHI use `fsh`. For CQL
semantics use `cql`. For the FHIR model info, FHIRHelpers and CQL Library conventions use `cql-ig`.

## Versions

| Layer | Pinned at | Why it matters |
| --- | --- | --- |
| IG Publisher | 3.0.5 (2026-11-20), tag `3.0.5` | Released often; 3.0.0 was a new major version, and 3.0.5 tightened template trust and folder checks |
| Its core library | org.hl7.fhir.core 7.0.6 | Path handling, R4-to-R5 conversion, terminology settings |
| Its CQL translator | cqframework 4.9.0 | Not the version the `cql` skill's probes use; 3.0.1 had 3.29.0 |
| FHIR Tooling IG | hl7.fhir.uv.tools 1.3.0 (Informative) | Defines the IG parameters and control extensions |
| Templates | cqf.fhir.template 1.0.0, base fhir.base.template 1.0.0 (2025-09-30) | Supply most of the `input/...` layout, and now Liquid narratives |

Every statement in `resources/` says which versions it holds for. The skill was first written against
3.0.1 and the 0.7.1/0.8.1 templates, re-pinned to 3.0.4 on 2026-11-14 and to 3.0.5 on 2026-11-24;
differences that change a claim are noted where they apply. The probe builds were run on 3.0.1 and 3.0.4;
what 3.0.5 changed is read from source.

## When the IG Was Built With Another Version

IGs usually build with whatever `_updatePublisher` last downloaded, and the publisher releases often.
So **first find out which publisher version built the IG**: the "IG Publisher Version:" line at the top
of `output/qa.txt`, or `java -jar publisher.jar -v`. Not `qa.json`'s `tool`, which holds a FHIR version.
Likewise, the template version is the `#version` in `ig.ini`.

If it isn't 3.0.5 (or the template isn't 1.0.0), the findings here are a strong starting point but not
proof. Before relying on one for that IG:

1. Take the claim's `[src: …]` citation, for example
   `[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/CqlSubSystem.java:1110-1155]`.
2. Read the same file at the IG's version on GitHub. [SOURCES.md](resources/SOURCES.md#looking-up-a-citation-at-another-version)
   gives the URL for each kind of source and the full path behind each `…`. Line numbers drift, so find
   the code by content near the cited lines.
3. If it's unchanged, the claim holds; say so. If it changed, say what changed and answer from the
   code at the IG's version, marked *read from source, not observed*.
4. Observed results (the probes) hold only for the version they record. Re-observing needs a build.

Version differences already known (3.0.1, 3.0.4 and 3.0.5) are noted in each resource file. A weekly
check in this repository reports when a newer publisher, core, template or tools release is out.

## Which Source Answers Which Question

Each question has its own source. When two sources disagree, report the disagreement as a finding;
don't settle it by ranking one above the other.

| Question | Source | Where |
| --- | --- | --- |
| What is parameter X *meant* to do? | The tools IG's `ig-parameters` CodeSystem (Informative) | [ig-parameters.md](resources/ig-parameters.md) (generated from it); TOOLS-1.3.0 in [SOURCES.md](resources/SOURCES.md) |
| What will the publisher *do*? | The publisher's source at the IG's version, plus a probe run if it matters | IGPUB-3.0.5 in [SOURCES.md](resources/SOURCES.md), on GitHub by tag |
| What does *my IG* get? | The template chain, plus the IG's own `ig.ini` and parameters | [layout.md](resources/layout.md), [templates.md](resources/templates.md); TPL-* in SOURCES.md |
| How do people usually set it up? | The FHIR sample IG and the example measure IG (convention only) | SAMPLE-IG, EX-DQM-CMS-2025 |

For example, `path-liquid-ig` is read by the publisher but not defined in the CodeSystem, and
`excludexml` is defined in the CodeSystem and consumed only by the template. Both are findings, and
[ig-parameters.md](resources/ig-parameters.md) lists every case.

## Evidence Rules

1. **Cite a pinned source, by version**, with its source ID and a locator. The citation format,
   the IDs and the locator forms are in [SOURCES.md](resources/SOURCES.md). Don't cite web fetches,
   Confluence or build.fhir.org: they paraphrase, truncate or move.
2. **Keep the layers apart:** what the tools IG says, what the publisher's source does, what a
   template adds, and what one IG configures. Source code is evidence of behaviour, not of intent.
3. **Say when a claim comes from reading code and hasn't been run.** Mark it *not yet observed*.
4. **A probe run records** the publisher version (`-v`), the exact command, and the relevant
   `qa.txt` lines, under `resources/probes/<date>/`.
5. **IGPUB-DOCS is stale.** The repository's `documentation.md` disagrees with `Publisher.java` at
   the same tag. Use the code for flags.

## Quick Reference

```ini
[IG]
ig = input/my-ig.xml
template = cqf.fhir.template#1.0.0
```

```sh
java -jar input-cache/publisher.jar -v
java -jar input-cache/publisher.jar -ig . -no-errors      # exit 1 if QA has errors
java -jar input-cache/publisher.jar -ig . -tx n/a         # no terminology server
```

- `ig.ini` must **start** with `[IG]`.
- Pin the template with `#version`; that also pins its base template.
- CQL compiles only if the IG sets `path-binary`. No layer has a default for it.
- A Library gets compiled ELM only through a `content` attachment with `id: "ig-loader-<file>.cql"`.
- Read `output/qa.txt` first, then `output/qa.html`.

## Known Gotchas

Each link leads to the evidence and the versions it holds for.

- **`ig.ini` that doesn't start with `[IG]` is ignored**, giving "unable to find an ig.ini":
  [ig-ini-and-ig-resource.md](resources/ig-ini-and-ig-resource.md#igini)
- **`input/cql` is no one's default.** The `input/...` folders come from the template; `path-binary`
  comes only from the IG: [layout.md](resources/layout.md#where-each-folder-comes-from)
- **An IG's `path-resource` adds to the template's eleven defaults, it doesn't replace them**:
  [layout.md](resources/layout.md#where-each-folder-comes-from)
- **The publisher compiles CQL with translator 4.9.0** (3.29.0 in 3.0.1), not the version your editor
  uses: [cql-loader.md](resources/cql-loader.md#the-translator-is-490)
- **Sub-folders of a `path-binary` folder are not compiled**:
  [cql-loader.md](resources/cql-loader.md#what-gets-compiled)
- **A Library with inline CQL gets no fresh ELM, and that `.cql` file's compile errors aren't
  reported**, only "CQL source was not associated…" (observed on 3.0.1 and 3.0.4). `qa.html` is then
  not a CQL compile check: [cql-loader.md](resources/cql-loader.md#libraries-with-embedded-cql)
- **"ELM generation failed: Unknown FHIRTypes code 'Any'" is logged, never reported in QA.** Observed
  for 89 of 90 measure and helper libraries on 3.0.1 and 3.0.4; by code read, the publisher maps any
  type outside FHIR and the System primitives to `Any`, which the core library rejects:
  [cql-loader.md](resources/cql-loader.md#elm-generation-can-fail-without-a-qa-message)
- **An error listed in `ignoreWarnings.txt` is still an error** (observed); only warnings, hints and
  link errors are suppressed. **A publisher upgrade can silently stop a line matching**: 3.0.4 words a
  CQL warning differently from 3.0.1: [running.md](resources/running.md#ignorewarningstxt)
- **A build with QA errors exits 0** unless you pass `-no-errors`:
  [running.md](resources/running.md#build-flags-verified-in-publishermain-at-304)
- **`-tx <url>` now also turns off the terminology ecosystem** unless you add `-ecosystem <url>`, so a
  private server answers every request (by code read):
  [terminology.md](resources/terminology.md#the-terminology-server)
- **`-proxy=host:port`, as the help text shows, isn't parsed**; use `-proxy host:port`. Only the first
  `-packages` counts. `-package-cache-folder` isn't used for every package (observed):
  [running.md](resources/running.md#build-flags-verified-in-publishermain-at-304)
- **Parameter codes split across layers**: `path-liquid-ig` and `log-loaded-resources` are read but
  undefined; `no-check-usage` is defined but unread, and `no-usage-check` is the one read;
  `jekyll-timeout` is read only from `ig.ini`: [ig-parameters.md](resources/ig-parameters.md),
  [ig-ini-and-ig-resource.md](resources/ig-ini-and-ig-resource.md#igini)
- **`find-other-resources` has no effect** in an R4 IG on fhir.base.template:
  [layout.md](resources/layout.md#example-one-cqf-measure-ig)
- **`path-expansion-params` is relative to the IG resource's folder**, not the IG root like every other
  `path-*`: [terminology.md](resources/terminology.md#expansion-parameters)
- **With `pin-all` and `pin-manifest`, the published manifest, not the input file, holds the pinned
  versions** (1 parameter in, 764 out, in the probe builds):
  [terminology.md](resources/terminology.md#example-one-cqf-measure-ig)
- **cqf.fhir.template 1.0.0 is cosmetic**; every default comes from fhir.base.template 1.0.0:
  [templates.md](resources/templates.md#what-each-template-in-the-cqf-chain-contributes)
- **fhir.base.template 1.0.0 ships Liquid narratives** for ActivityDefinition, Library, Measure and
  PlanDefinition, and they beat an IG's `path-liquid` folder. Use `input/liquid`, or `path-liquid-ig`
  (which costs two QA errors): [templates.md](resources/templates.md#liquid-narrative-templates)
- **An R4 IG gets `package.r4.tgz`, `package.r4b.tgz` and `package-combined.tgz` without asking**, and
  the R4B package keeps its R4 dependencies (observed):
  [multi-version-and-language.md](resources/multi-version-and-language.md#an-r4-or-r4b-ig-automatic-r4-and-r4b-packages)
- **`-go-publish` rebuilds the IG with `-resetTx`, and its "no more errors than the draft" check can't fail**
  (possible defect, by code read): [publication.md](resources/publication.md#possible-defects-by-code-read)
- **`<root>/template/` is wiped on every run**:
  [ig-ini-and-ig-resource.md](resources/ig-ini-and-ig-resource.md#the-template-value)
- **From 3.0.5 a local build stops for an untrusted template that runs scripts**, such as a template
  you're working on from a folder: run once with `-trust-template <id>`. On the ci-build, only a
  released version (or `#current`) of a trusted template runs scripts, so `#dev` doesn't:
  [templates.md](resources/templates.md#how-a-template-chain-is-assembled)
- **From 3.0.5 symbolic links out of the IG's folder stop the build** (locally, until you pass
  `-allow-external-links`; on the ci-build, always), and `path-tx-cache` outside the IG's folder is
  ignored: [running.md](resources/running.md#build-flags-verified-in-publishermain-at-305),
  [layout.md](resources/layout.md#path-values-on-each-platform)
- **The VS Code CQL extension reads `input/cql` and `input/tests` whatever `path-binary` says**
  (the `vscode-cql` skill covers the extension):
  [layout.md](resources/layout.md#tools-that-assume-the-default-layout)

## Supporting Files

For which folder each layer sets, path values on each platform, and tools that assume the default layout: see [layout.md](resources/layout.md)
For `ig.ini` keys, template values, IG resource loading, R4 parameters and unknown parameters: see [ig-ini-and-ig-resource.md](resources/ig-ini-and-ig-resource.md)
For every IG parameter, with its definition and which layer reads it (generated): see [ig-parameters.md](resources/ig-parameters.md)
For `path-binary`, `ig-loader-` Libraries, `cql-options.json`, effective data requirements and CQL messages: see [cql-loader.md](resources/cql-loader.md)
For getting a pinned jar, command-line flags, exit status, QA outputs and `ignoreWarnings.txt`: see [running.md](resources/running.md)
For the terminology server and ecosystem, the local tx cache, expansion parameters and `pin-canonicals`/`pin-manifest`: see [terminology.md](resources/terminology.md)
For how a template chain is assembled, what fhir.base.template's `config.json` controls, and Liquid narrative templates: see [templates.md](resources/templates.md)
For extra FHIR-version packages (R4/R4B automatic, R5 `generate-version`) and translation parameters: see [multi-version-and-language.md](resources/multi-version-and-language.md)
For `-go-publish`: `publication-request.json` fields, the checks, what it rebuilds and writes, and possible defects: see [publication.md](resources/publication.md)
For the source IDs used in `[src: …]` citations: see [resources/SOURCES.md](resources/SOURCES.md)
For recorded publisher runs (version, checksum, command, QA and log excerpts): see [the 3.0.4 probe](resources/probes/2026-11-14/RESULTS.md) and [the 3.0.1 probe](resources/probes/2026-10-22/RESULTS.md)
For maintainers only (not needed to answer questions):
- Local copies of the published sources, for the linter and the generator: `scripts/fetch-sources.sh` (see [resources/sources/README.md](resources/sources/README.md))
- Regenerate ig-parameters.md: `python3 scripts/gen_ig_parameters.py` (`--check` to verify)
- Check citations, versions and line ranges: `python3 scripts/lint_skill_igpub.py`
- See whether a newer release is out and which citations it touches: `python3 scripts/check_release.py`
- Tests: `scripts/test_*.py`

## Not Yet Covered

The template's own Jekyll includes and layouts in detail. `-go-publish` is covered from source only; it
was not run. Whether the new terminology ecosystem changes any result for a measure IG was not tested.
