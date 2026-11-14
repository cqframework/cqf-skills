# IG Folder Layout, by Layer

Baseline: IG Publisher 3.0.4, fhir.base.template 1.0.0, cqf.fhir.template 1.0.0. Untagged statements hold at these versions only.
Sources: IGPUB-3.0.4, CORE-7.0.6, TOOLS-1.3.0, TPL-BASE-1.0.0, TPL-CQF-1.0.0, SAMPLE-IG, EX-DQM-CMS-2025, VSCQL

The usual `input/...` layout is not built into the publisher. Three layers each set part of it:

1. **The publisher** finds `ig.ini`, runs SUSHI if there is FSH, and falls back to `resources/` and
   `pages/` only when nothing else sets a path.
2. **The template** adds most of the `input/...` folders as IG parameters when the IG is loaded.
   fhir.base.template is the base of cqf.fhir.template 1.0.0
   [src: TPL-CQF-1.0.0 package/package.json#L8-L10], so every cqf IG gets these defaults.
3. **The IG** adds its own folders with `path-*` parameters in its ImplementationGuide resource.

`input/cql` belongs to layer 3: no layer sets a default for `path-binary`.

## Where each folder comes from

| Folder | Role | Set by | Evidence |
| --- | --- | --- | --- |
| `ig.ini` | Names the IG resource and the template | Publisher; its text must start with `[IG]` | [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:294-313] |
| `fsh/` or `input/fsh/` | FSH source; if present, the publisher runs SUSHI first (unless `-no-sushi`; in watch mode, also not when only page content changed) | Publisher | [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:180-190] [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:206-210] |
| `input/capabilities`, `input/examples`, `input/extensions`, `input/models`, `input/operations`, `input/profiles`, `input/resources`, `input/vocabulary`, `input/testing`, `input/history`, `fsh-generated/resources` | Resources to load (`path-resource`) | Template, added alongside the IG's own `path-resource` values | [src: TPL-BASE-1.0.0 scripts/onLoad.xslt#L127-L209] |
| `input/maps` | Resources to load (`path-resource`) | Template, only if the IG sets no `path-resource` of its own | [src: TPL-BASE-1.0.0 scripts/onLoad.xslt#L183-L188] |
| `input/pagecontent`, `input/intro-notes`, `input/pages` | Narrative pages, transformed into Jekyll includes | Template (`pre-process`) | [src: TPL-BASE-1.0.0 config.json#L47-L78] |
| `input/includes`, `input/data`, `input/resourcedocs` | Jekyll includes and data | Template (`pre-process`) | [src: TPL-BASE-1.0.0 config.json#L47-L78] |
| `input/includes/menu.xml` | The site's top menu, included on every page | Template | [src: TPL-BASE-1.0.0 includes/fragment-pagebegin.html#L96] |
| `input/images` | Copied to the output untouched (`path-pages`) | Template, added alongside | [src: TPL-BASE-1.0.0 scripts/onLoad.xslt#L217-L223] |
| `input/liquid` | Liquid narrative templates (`path-liquid`), loaded after the template's own `template/liquid`, so it overrides it (see [templates.md](templates.md#liquid-narrative-templates)) | Template, added alongside | [src: TPL-BASE-1.0.0 scripts/onLoad.xslt#L231-L237] |
| `input/ignoreWarnings.txt` | Suppressed QA messages (`path-suppressed-warnings`) | Template, only if unset | [src: TPL-BASE-1.0.0 scripts/onLoad.xslt#L262-L267] |
| `input-cache/txcache` | Terminology cache (`path-tx-cache`) | Template, only if unset | [src: TPL-BASE-1.0.0 scripts/onLoad.xslt#L256-L261] |
| `temp/pages`, `temp/qa`, `output` | Jekyll work area, QA fragments, generated site (`path-temp`, `path-qa`, `path-output`) | Template, only if unset | [src: TPL-BASE-1.0.0 scripts/onLoad.xslt#L238-L255] |
| `input/cql` | CQL source and modelinfo (`path-binary`) | **The IG only.** No publisher or template default | See [cql-loader.md](cql-loader.md) |
| `input/tests` | Test cases | **Not a publisher parameter.** A CQF/MADIE convention read by other tools. `path-test` is unrelated: it adds files to the package's `/test` folder | [src: TOOLS-1.3.0 CodeSystem-ig-parameters.json#path-test] |

**`package-list.json` and `publication-request.json`.** Many IGs keep a `package-list.json`, the IG's
version history, at the root, as the sample IG does [src: SAMPLE-IG package-list.json]. At 3.0.4 the
build doesn't read a local one: it fetches `package-list.json` from a dependency's or the IG's
*published* canonical URL, to resolve a dependency by version
[src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:2154-2172] and to compare against
previous versions [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/comparators/PreviousVersionComparator.java:177-183].
The other source files that mention it (under `utils/` and `web/`) maintain published websites. The
root file the build does use is `publication-request.json`: outside publication mode it is added to the
package [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherGenerator.java:527-530], and
publication mode reads related-IG versions from it
[src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:2299-2309]. The publication
process itself (`-go-publish`) is not covered yet; see SKILL.md, Not Yet Covered.

*Added alongside* and *only if unset* come from the template's `setParameter`: a default marked
`supplement` is skipped only if the IG already has that exact value. Any other default is skipped if
the IG has any value for the code [src: TPL-BASE-1.0.0 scripts/onLoad.xslt#L383-L417].

**Intro and notes for an artifact page.** For each artifact page, the publisher looks in the page
folders' `_includes` for `<page>-intro.xml`, else `<page>-intro.md`, and `<page>-notes.xml`, else
`<page>-notes.md`, where `<page>` is the page name without `.html`, for example
`StructureDefinition-mypatient` [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherGenerator.java:4123-4153].
The template's `pre-process` copies `input/pagecontent`, `input/intro-notes` and `input/pages` into
`_includes` [src: TPL-BASE-1.0.0 config.json#L65-L78], and its layouts place the intro before the content
and the notes after it, under "Notes:" [src: TPL-BASE-1.0.0 includes/fragment-intro.html#L1-L15]
[src: TPL-BASE-1.0.0 includes/fragment-notes.html#L1-L14]. The suffix is `-notes`, plural.

**Without a template default**, the publisher's own fallbacks apply: `resources/` and `pages/`
[src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:1032-1035], plus `temp/`,
`output/` and `txCache/` [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:419-430].
A listed folder that doesn't exist is dropped without an error
[src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:1056-1066]
[src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherBase.java:179-184].

**A `path-resource` value ending in `/*`** also loads every sub-folder
[src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:1627-1632]
[src: TOOLS-1.3.0 CodeSystem-ig-parameters.json#path-resource].

## Path values on each platform

The publisher joins each `path-*` value to the IG root with `Utilities.path`, which converts both
`\` and `/` to the build machine's separator
[src: CORE-7.0.6 org.hl7.fhir.utilities/…/PathBuilder.java:109-110]. The FHIR sample IG writes
`input\cql` [src: SAMPLE-IG input/myig.xml#L211-L212], and that works on every platform.

| Value in the IG resource | Built on macOS or Linux | Built on Windows |
| --- | --- | --- |
| `input/cql` | `<root>/input/cql` | `<root>\input\cql` |
| `input\cql` | `<root>/input/cql` | `<root>\input\cql` |
| `C:/work/cache` as `path-tx-cache` | `<root>/C:/work/cache` (inferred: not absolute on this OS) | `C:\work\cache` |

`path-temp` and `path-output` must resolve inside the IG root, or the build stops
[src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:524-536]. `path-tx-cache` may be
absolute. The publisher tests it with `Paths.get(value).isAbsolute()`
[src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:512-513]. That test runs on the
build machine, so a Windows drive path counts as absolute only on Windows; the last row is inferred
from that, not observed.

## Tools that assume the default layout

**The VS Code CQL extension** (VSCQL, vscode-cql 1.0.0) treats a
folder as an IG root if it has `ig.ini` or `input/cql`
[src: VSCQL src/model/igLayoutDetector.ts:56-61]. It then reads CQL from `<root>/input/cql`, tests
from `<root>/input/tests` and results from `<root>/input/tests/results`, all hard-coded
[src: VSCQL src/model/cqlProject.ts:230-232]. No file under `src/` reads `path-binary` or
`path-resource` (searched at v1.0.0). So the extension reads CQL from `input/cql` whatever the IG's
`path-binary` says. The `vscode-cql` skill covers the extension and its language server in detail.

## Example: one cqf measure IG

EX-DQM-CMS-2025 shows what one IG configures, not what is required:

- `path-binary` = `input/cql` [src: EX-DQM-CMS-2025 input/dqm-content-cms-2025.xml:177-178].
- Four `path-resource` values (`input/resources/library`, `…/measure`, `…/parameters`,
  `input/vocabulary/valueset`) [src: EX-DQM-CMS-2025 input/dqm-content-cms-2025.xml:161-174]. These are
  added to the template's eleven `added alongside` defaults; they don't replace them.
- `path-pages` = `input/pagecontent` [src: EX-DQM-CMS-2025 input/dqm-content-cms-2025.xml:157-158].
  The template already pre-processes that folder.
- `path-liquid-ig` = `templates/liquid` [src: EX-DQM-CMS-2025 input/dqm-content-cms-2025.xml:181-182].
  The publisher reads this code [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:521-523],
  but the tools CodeSystem doesn't define it (see [ig-parameters.md](ig-parameters.md)).
- `find-other-resources` [src: EX-DQM-CMS-2025 input/dqm-content-cms-2025.xml:152-153]. The tools
  CodeSystem doesn't define it, and no publisher Java file mentions it. For an R4 IG, the base
  template drops it [src: TPL-BASE-1.0.0 scripts/onLoad.xslt#L108] [src: TPL-BASE-1.0.0 scripts/onLoad.xslt#L115],
  so it has no effect.
