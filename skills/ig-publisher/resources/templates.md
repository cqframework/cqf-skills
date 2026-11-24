# Templates and Liquid

Baseline: IG Publisher 3.0.5 (org.hl7.fhir.core 7.0.6), cqf.fhir.template 1.0.0, fhir.base.template 1.0.0. Untagged statements hold at these versions only.
Sources: IGPUB-3.0.5, CORE-7.0.6, TPL-CQF-1.0.0, TPL-BASE-1.0.0, TOOLS-1.3.0, EX-DQM-CMS-2025, PROBES-2026-10-22, PROBES-2026-11-14

A template supplies an IG's page layouts, includes, styles and build scripts, and many of its default
parameters. Liquid templates are per-resource-type narrative templates. Since fhir.base.template 1.0.0,
the base template ships some of its own as well as any the IG supplies. How `ig.ini` names a template,
and how versions are resolved, is in [ig-ini-and-ig-resource.md](ig-ini-and-ig-resource.md#the-template-value).

## How a template chain is assembled

1. The publisher clears `<root>/template/` [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/TemplateManager.java:137-142].
2. It installs the named template. If that package's `package.json` names a `base`, it installs the base
   **first**, at the version listed in `dependencies`, recursively
   [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/TemplateManager.java:260-271].
3. Each package is unpacked into `template/` after its base
   [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/TemplateManager.java:275]. A file with the same name
   replaces the base's file. A file named `_append.<name>` is **appended** to the base's `<name>` instead
   [src: CORE-7.0.6 org.hl7.fhir.utilities/…/npm/NpmPackage.java:1545-1583].

**Scripts.** A template's `config.json` names an Ant script and its `onLoad`, `onGenerate` and, from
fhir.base.template 1.0.0, `onCheck` targets [src: TPL-BASE-1.0.0 config.json#L2-L8]. `onCheck` runs
after generation, and its Ant target writes `onCheck-validation.json`, whose messages are added to QA
[src: TPL-BASE-1.0.0 scripts/ant.xml#L174-L185] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/templates/Template.java:772-779]
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherGenerator.java:5073].

**Which templates may run scripts** (changed in 3.0.5; the rules for template authors are in the
`trusted-ig-template` skill):

- **The trusted list** is in `TrustedTemplates.java`, with the GitHub repository each template is built
  from. It includes `fhir.base.template` (whose entry carries the comment "no longer trusted: GG decision,
  19-11-2026", though the entry is still there) and `cqf.fhir.template`, built from
  `cqframework/cqf-ig-template` [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/templates/TrustedTemplates.java:24-50].
- **Only a released version is trusted**: `n.n.n`, `#current`, or no version. `#dev`, a branch build
  (`current$branch`) or a labelled version such as `-cibuild` isn't, and on the ci-build its scripts don't
  run [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/TemplateManager.java:566-594].
- **On the ci-build**, a template that claims a trusted id must be built from that repository, and an IG
  can't use a trusted template's package id [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:1547-1580].
- **Locally, an untrusted template that runs scripts stops the build** (before 3.0.5 it just ran). That
  includes a template loaded from a folder or GitHub URL while you work on it. Run once with
  `-trust-template <id>` (the id as the IG names it, without a version) or `-trust-template all`; it is
  recorded in `trustedTemplates` in `fhir-settings.json`, so later runs don't ask
  [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/TemplateManager.java:155-159]
  [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/TemplateManager.java:196-221].

**Accessibility routines** (new in IG Publisher 3.0.x after 3.0.1). Each template can list JavaScript
routine names under `accessibility-routines` in its `config.json`. The publisher writes calls to them
into `content/assets/js/accessible.js` in place of a marker line, and rejects a name that isn't a valid
JavaScript function name [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/TemplateManager.java:454-491].
fhir.base.template 1.0.0 lists none.

## What each template in the cqf chain contributes

| Template | Contributes | Evidence |
| --- | --- | --- |
| fhir.base.template 1.0.0 | `config.json` (scripts, template parameters, page types, formats, `pre-process`, `script-mappings`, per-type defaults), `scripts/onLoad.xslt` (the default IG parameters in [layout.md](layout.md)), `includes/`, `layouts/`, and, new in 1.0.0, 33 files in `liquid/`: Liquid narrative templates for ActivityDefinition, Library, Measure and PlanDefinition, and the fragments they include | [src: TPL-BASE-1.0.0 config.json] [src: TPL-BASE-1.0.0 scripts/onLoad.xslt] [src: TPL-BASE-1.0.0 liquid/Measure.liquid] |
| cqf.fhir.template 1.0.0 | Cosmetic only: `cqf.css`, `cql.js` and images, and text appended to the header, footer and CSS includes. No `config.json`, scripts or Liquid. 1.0.0 differs from 0.7.1 only in CSS, one attribute name and its base dependency | [src: TPL-CQF-1.0.0 includes/_append.fragment-header.html#L1-L3] [src: TPL-CQF-1.0.0 includes/_append.fragment-footer.html#L1-L2] [src: TPL-CQF-1.0.0 includes/_append.fragment-css.html#L1] [src: TPL-CQF-1.0.0 package/package.json#L8-L10] |

So for a cqf IG, **every parameter default, page rule and template Liquid comes from
fhir.base.template**. Both templates' 1.0.0 releases are dated 2025-09-30, so an IG whose `ig.ini`
doesn't pin a version has been getting 1.0.0 since then; 0.7.1 and 0.8.1 date from 2024.

## fhir.base.template's config.json

| Key | What it controls | Evidence |
| --- | --- | --- |
| `template-parameters` | Parameter codes passed to the template instead of being reported as unknown: `copyrightyear`, `excludelogbinaryformat`, `excludejson`, `excludemap`, `excludettl`, `excludexml`, `fmm-definition`, `globals-in-artifacts`, `releaselabel`, `shownav`. If a template lists none, a short built-in list applies | [src: TPL-BASE-1.0.0 config.json#L9] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/templates/Template.java:786-788] |
| `extraTemplates` | Extra pages per artifact: mappings, testing, examples, format, profile history and change history | [src: TPL-BASE-1.0.0 config.json#L11-L39] |
| `formats` | Order of the format pages (`xml`, `json`, `ttl`) | [src: TPL-BASE-1.0.0 config.json#L40-L45] |
| `pre-process` | Folders copied into Jekyll's `_includes` and `_data` (see [layout.md](layout.md)) | [src: TPL-BASE-1.0.0 config.json#L47-L78] |
| `script-mappings` | New in 1.0.0: media types `text/x-gherkin`, `text/markdown` and `text/graphql` mapped to script names | [src: TPL-BASE-1.0.0 config.json#L80-L84] |
| `defaults` | Per resource type: the layout for each page, and each page's file name. "Anything not mentioned defaults to true" | [src: TPL-BASE-1.0.0 config.json#L85-L89] |

For example, a Library or a Measure gets `layout-canonical.html` as its main page, named
`{{[type]}}-{{[id]}}.html` (for example `Library-AdultOutpatientEncounters.html`), plus format, testing and
change-history pages [src: TPL-BASE-1.0.0 config.json#L237-L256].

## Liquid narrative templates

A Liquid template replaces the publisher's built-in narrative for every resource of one type: if one
exists for the type, the renderer factory returns a Liquid renderer instead
[src: CORE-7.0.6 org.hl7.fhir.services/…/renderers/RendererFactory.java:48-52]
[src: CORE-7.0.6 org.hl7.fhir.services/…/renderers/RendererFactory.java:108-112].

**Naming.** In each Liquid folder, `<Type>.liquid` is stored under the resource type, lowercased: the file
name up to its first `.`. Files ending `.html` are stored under their full name, as include fragments.
Sub-folders are not read [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/IGPublisherLiquidTemplateServices.java:43-57].
The template for a resource is looked up by `fhirType()`, lowercased
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/IGPublisherLiquidTemplateServices.java:59-63].

**Three parameters, loaded in a fixed order.** A later load of the same name **replaces** an earlier one
(a map `put`), so the last folder loaded wins:

| Order | Parameter | Defined in the tools CodeSystem? | Evidence |
| --- | --- | --- | --- |
| 1 | `path-liquid-template` | yes: "provided by the template" | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:533-535] [src: TOOLS-1.3.0 CodeSystem-ig-parameters.json#path-liquid-template] |
| 2 | `path-liquid` | yes | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:530-532] [src: TOOLS-1.3.0 CodeSystem-ig-parameters.json#path-liquid] |
| 3 | `path-liquid-ig` | **no** | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:536-538] |

Within one parameter, folders load in parameter order [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:1048-1056].
fhir.base.template adds `template/liquid` and then `input/liquid` as `path-liquid`, both *added alongside*
the IG's own values [src: TPL-BASE-1.0.0 scripts/onLoad.xslt#L224-L237]. The template's defaults are
written after the IG's parameters [src: TPL-BASE-1.0.0 scripts/onLoad.xslt#L93-L106]. So, by the code:

- **The template's own Liquid now applies to every IG on fhir.base.template 1.0.0.** An IG with no
  Liquid of its own gets the template's ActivityDefinition, Library, Measure and PlanDefinition
  narratives in place of the publisher's built-in ones. With 0.8.1 there were none.
- **An IG folder given as `path-liquid` loses to `template/liquid`** for those four types, because the
  template's folder is added after it.
- **`input/liquid` wins over `template/liquid`**, because the template adds it last.
- **`path-liquid-ig` wins over all of them.**

The CodeSystem says the same thing for its two codes: "any liquid templates found in path-liquid override
ones found in path-liquid-template" [src: TOOLS-1.3.0 CodeSystem-ig-parameters.json#path-liquid-template].

### Example: one cqf measure IG

EX-DQM-CMS-2025 puts five Liquid templates in `templates/liquid`, `ActivityDefinition`, `Group`, `Library`,
`Measure` and `PlanDefinition`, with 74 `.html` fragments alongside (79 files tracked at 46b11c3), and
loads them with `path-liquid-ig` [src: EX-DQM-CMS-2025 input/dqm-content-cms-2025.xml:181-182]. Its
`ignoreWarnings.txt` explains that this is "a temporary workaround for getting the IG to make use of
liquid templates in the IG when the fhir template includes liquid templates for the same resources"
[src: EX-DQM-CMS-2025 input/ignoreWarnings.txt:3].

That IG pins `cqf.fhir.template#0.7.1`, and with it fhir.base.template 0.8.1, which ships no Liquid. A
3.0.1 build found no `.liquid` file in the template chain, so the workaround had nothing to override
[src: PROBES-2026-10-22 run3-liquid-search.txt]. With 1.0.0 it does: four of the IG's five types are
also in the template's `liquid/` folder. A 3.0.4 build of the same IG with the template set to `#1.0.0` had
`ActivityDefinition.liquid`, `Library.liquid`, `Measure.liquid` and `PlanDefinition.liquid` in
`template/liquid` [src: PROBES-2026-11-14 run1-template-liquid.txt], so with 1.0.0 the workaround is needed.

**What `path-liquid-ig` costs.** It is not in the tools CodeSystem, so in an R4 IG, where the template
rewrites it into the `ig-parameter` extension, the validator reports two errors on the IG resource
[src: PROBES-2026-10-22 qa-excerpts.txt] [src: PROBES-2026-11-14 qa-excerpts.txt], and they can't be suppressed (see
[running.md](running.md#ignorewarningstxt)). With fhir.base.template 1.0.0, the only defined
alternative that still overrides the template's Liquid is to put the files in `input/liquid`, which the
template loads last among the `path-liquid` folders. Listing the folder as `path-liquid` would not:
`template/liquid` is added after it (by the load order above; not observed).
