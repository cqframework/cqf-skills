# ig.ini and the ImplementationGuide Resource

Baseline: IG Publisher 3.0.5 (org.hl7.fhir.core 7.0.6), fhir.base.template 1.0.0. Untagged statements hold at these versions only.
Sources: IGPUB-3.0.5, CORE-7.0.6, TPL-BASE-1.0.0, TPL-CQF-1.0.0, TOOLS-1.3.0, IGPUB-DOCS-3.0.5, SAMPLE-IG, EX-DQM-CMS-2025

An IG has two control files. `ig.ini` says where the ImplementationGuide resource is and which
template to use. Everything else is set by IG parameters inside that resource.

## ig.ini

**Finding it.** `-ig` names a folder or a file; for a folder the publisher opens `<folder>/ig.ini`.
The file is used only if its text **starts with** `[IG]`. Otherwise the publisher acts as if there
were no `ig.ini` [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:300-319] and
stops with "The IG Publisher was unable to find an ig.ini"
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:198-207]. A leading comment,
blank line or byte-order mark before `[IG]` causes that error.

**Keys the publisher reads** (searched at 3.0.1, 3.0.4 and 3.0.5, with the same result, for `ini.getStringProperty`, `getLongProperty`,
`getBooleanProperty` and `hasProperty`):

| Section and key | Meaning | Evidence |
| --- | --- | --- |
| `[IG] ig` | Path of the ImplementationGuide resource, relative to the folder holding `ig.ini` | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:358] |
| `[IG] template` | Required: "You must nominate a template" | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:332-334] |
| `[IG] module` | A publisher module to load | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:335] |
| `[IG] jekyll-timeout` | Jekyll timeout, in seconds; on the ci-build at most an hour (3600), with a log line if `ig.ini` asks for more (new in 3.0.5) | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:1013-1018] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:2223-2229] |
| `[IG] usage-stats-opt-out` | Opt out of extension usage statistics | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:1427] |
| `[IG] <package id>[#version]` | Local folder to load that template, or one of its base templates, from (template debugging; ignored in auto-build) | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/TemplateManager.java:88-115] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/TemplateManager.java:132-136] |
| `[dev] branch` | Branch name | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:405] |

SUSHI's `[FSH] timeout` and `[FSH] sushi-version` live in `fsh.ini`, not `ig.ini`
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/FSHRunner.java:58-79]. From 3.0.5, `sushi-version` must be
a version number (`3.16.0`, or with a pre-release suffix such as `3.16.0-beta.1`); anything else, such as
an npm tag or a URL, stops the build [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/FSHRunner.java:200-213].
SUSHI now runs in an empty temporary folder rather than the IG's, and an IG with an `.npmrc` or its own
`node_modules/fsh-sushi` is refused [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/FSHRunner.java:126-143].

**`jekyll-timeout` is in two layers.** The tools CodeSystem defines it as an IG parameter
[src: TOOLS-1.3.0 CodeSystem-ig-parameters.json#jekyll-timeout], but at 3.0.5 the publisher reads it
only from `ig.ini`; the IG parameter `switch` has no case for it (see [ig-parameters.md](ig-parameters.md)).

**Keys nothing reads.** IGPUB-DOCS says "Other entries are allowed, but not used by the
IG-Publisher" [src: IGPUB-DOCS-3.0.5 documentation.md#L7-L18]. For example, EX-DQM-CMS-2025 sets
`fhir-version=4.0.1` [src: EX-DQM-CMS-2025 ig.ini:5], and no publisher source file at 3.0.5 reads a
`fhir-version` key. The FHIR version comes from the IG resource (below).

### The template value

| Value | Loaded from | Evidence |
| --- | --- | --- |
| `cqf.fhir.template#1.0.0` | That package version, from the package cache | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/TemplateManager.java:620-622] |
| `cqf.fhir.template` | `loadPackage(id, null)`: the package cache picks the version (not traced further) | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/TemplateManager.java:616-618] |
| `#my-template` | The folder `my-template` under the IG root | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/TemplateManager.java:608-614] |
| a folder, a `.tgz`, or a GitHub URL | That folder or file; a GitHub URL is downloaded as a zip, with timeouts (30 seconds to connect, 5 minutes to read), at most 200 MB, and refused if an entry name contains `..` (new in 3.0.5) | [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/TemplateManager.java:623-653] [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/TemplateManager.java:666-678] |

The sample IG's comment, "if no version is specified, the publisher will take the #current version"
[src: SAMPLE-IG ig.ini#L35], is convention text; the code above defers to the package cache.

A template's base template is loaded at the version listed in the template's own `package.json`
`dependencies`, or the build fails [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/TemplateManager.java:260-271].
So pinning `cqf.fhir.template#1.0.0` also pins `fhir.base.template#1.0.0` (and `#0.7.1` pins `#0.8.1`)
[src: TPL-CQF-1.0.0 package/package.json#L8-L10].

The publisher unpacks the template into `<root>/template/`, which it **clears on every run**
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/TemplateManager.java:137-142]. Don't edit files there.
From 3.0.5 it is cleared without following links, and if `template/` is itself a link it isn't cleared:
the build stops [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherUtils.java:104-124].

## The ImplementationGuide resource

**Loading.** The publisher parses the file as R5. If its `fhirVersion` isn't R5 or later, or the
parse fails, it re-reads it as R4 and converts it to R5
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:359-374]. The supported
versions are 5.0.0, 4.3.0, 4.0.1, 3.0.2, 1.0.2 and 6.0.0-snapshot1; the first `fhirVersion` is used
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:411-417].

**The template then transforms it** before the publisher reads any parameter
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:407-409]. fhir.base.template 1.0.0 (the same as 0.8.1 here):

- stops the build if `ImplementationGuide.version` is missing
  [src: TPL-BASE-1.0.0 scripts/onLoad.xslt#L29-L31];
- adds the default parameters listed in [layout.md](layout.md);
- for an R2, R3 or R4 IG [src: TPL-BASE-1.0.0 scripts/onLoad.xslt#L20-L22], rewrites every
  `definition.parameter` whose code isn't one of R4's own codes into the
  `http://hl7.org/fhir/tools/StructureDefinition/ig-parameter` extension
  [src: TPL-BASE-1.0.0 scripts/onLoad.xslt#L93-L114]. R4's own codes are `apply`, `path-resource`,
  `path-pages`, `path-tx-cache`, `expansion-parameter`, `rule-broken-links`, `generate-xml`,
  `generate-json`, `generate-turtle` and `html-template` [src: TPL-BASE-1.0.0 scripts/onLoad.xslt#L97-L98].

The R4-to-R5 converter turns each `ig-parameter` extension back into a `definition.parameter`
[src: CORE-7.0.6 org.hl7.fhir.convertors/…/ImplementationGuide40_50.java:245-251]. The net effect: an R4
IG can write any parameter as a plain `definition.parameter` and the publisher still sees it.

### Writing a parameter

An R4 IG, as EX-DQM-CMS-2025 does [src: EX-DQM-CMS-2025 input/dqm-content-cms-2025.xml:177-178]:

```xml
<parameter>
  <code value="path-binary"/>
  <value value="input/cql"/>
</parameter>
```

The extension form, which the template writes for an R4 IG and which the tools IG defines for R4 use
[src: TOOLS-1.3.0 StructureDefinition-ig-parameter.json]:

```xml
<extension url="http://hl7.org/fhir/tools/StructureDefinition/ig-parameter">
  <extension url="code"><valueString value="path-binary"/></extension>
  <extension url="value"><valueString value="input/cql"/></extension>
</extension>
```

**Validation of the extension form.** Because the R4 template rewrites non-R4 codes into the extension,
the validator checks each code against the tools IG's value set. A code the CodeSystem doesn't define
(for example `path-liquid-ig`) then raises errors on the IG resource. EX-DQM-CMS-2025 lists such errors
in its `ignoreWarnings.txt` [src: EX-DQM-CMS-2025 input/ignoreWarnings.txt:3-6]; see
[running.md](running.md#ignorewarningstxt) for why listing an error there doesn't remove it.

**Unknown parameters.** A code that the IG parameter `switch` doesn't handle and the template doesn't
declare as a template parameter is collected [src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:990-996]
and reported once, as a warning on the IG resource: `Unknown Parameters: [code=value, …]`
[src: IGPUB-3.0.5 org.hl7.fhir.publisher.core/…/PublisherProcessor.java:1805-1807].

What each code means, and which layer reads it: [ig-parameters.md](ig-parameters.md).
