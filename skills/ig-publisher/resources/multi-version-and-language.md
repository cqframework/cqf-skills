# Multi-version and Multi-language IGs

Baseline: IG Publisher 3.0.4, hl7.fhir.uv.tools 1.3.0. Untagged statements hold at these versions only.
Sources: IGPUB-3.0.4, IGPUB-DOCS-3.0.4, TOOLS-1.3.0, PROBES-2026-10-22, PROBES-2026-11-14

One IG can produce packages for more than one FHIR version, and pages in more than one language. The
publisher repository documents both [src: IGPUB-DOCS-3.0.4 multi-version-IGs.md]
[src: IGPUB-DOCS-3.0.4 multi-lingual-IGs.md]. That documentation is a guide; the code at the same tag
decides behaviour, and the two disagree in places noted below.

## Extra FHIR-version packages

Which path the publisher takes depends on the IG's own FHIR version.

### An R4 or R4B IG: automatic R4 and R4B packages

For an R4 or R4B IG, the publisher always analyses whether the content can be both R4 and R4B. **If it
can, it writes `package.r4.tgz` and `package.r4b.tgz` beside `package.tgz`, with no parameter needed**
[src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherGenerator.java:542-548]
[src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/R4ToR4BAnalyser.java:440-450]. Each is named
`<packageId>.r4` or `<packageId>.r4b` [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/R4ToR4BAnalyser.java:453-460].

- `r4-exclusion` and `r4b-exclusion` exempt a resource from that analysis
  [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:2736-2741]
  [src: TOOLS-1.3.0 CodeSystem-ig-parameters.json#r4-exclusion].
- The repository documentation calls this the legacy path, still used for every R4 or R4B IG
  [src: IGPUB-DOCS-3.0.4 multi-version-IGs.md#L123-L128].

**Observed** for EX-DQM-CMS-2025, an R4 IG with no version parameters: a 3.0.1 build wrote all three packages
[src: PROBES-2026-10-22 run3-packages.txt], and a 3.0.4 build wrote them and a fourth,
`package-combined.tgz`, which depends only on `hl7.fhir.r4.core#4.0.1` [src: PROBES-2026-11-14 RESULTS.md]. `package.r4b.tgz` declares FHIR `4.3.0` and depends on
`hl7.fhir.r4b.core#4.3.0`, but its other dependencies are unchanged. For example, it still depends on
`hl7.fhir.us.cqfmeasures#5.0.0` and `hl7.terminology.r4#6.5.0`, which are R4 packages. Between the two builds the `hl7.fhir.uv.extensions.r4` dependency moved
from 5.3.0 to 5.4.0 with no change to the IG [src: PROBES-2026-11-14 RESULTS.md]. Whether an R4B
consumer can use it was not tested.

### An R5 IG: `generate-version`

For an R5 IG, each `generate-version` parameter asks for one more package, `<packageId>.<token>.tgz`, made
by converting the content [src: IGPUB-DOCS-3.0.4 multi-version-IGs.md#L19-L32]. Only an R5 base gets the
cross-version analysis page [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:2742-2746].

**Tokens.** The code folds `4.0`, `4.0.1` and `r4` into one family, and likewise for R4B and R5
[src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:3103-3105]. A numeric token works
but gives a warning to use the short form [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:690-696].
An unrecognised token is an error, and no package is made for it
[src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:3136-3144].

**The layers disagree on the allowed values:**

| Layer | Says | Evidence |
| --- | --- | --- |
| Tools CodeSystem | `r2`, `r2b`, `r3`, `r4`, `r5`. "Use with great care, and only after consulting the FHIR Product director … generally only appropriate for terminology resources" | [src: TOOLS-1.3.0 CodeSystem-ig-parameters.json#generate-version] |
| Repository documentation | `r4` and `r4b` from an R5 base | [src: IGPUB-DOCS-3.0.4 multi-version-IGs.md#L5-L17] |
| Publisher code | Any of `r2`, `r3`, `r4`, `r4b`, `r5`, `r6`, or a numeric equivalent | [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:3136-3144] |

**Which resources go into which package.** `r4-inclusion`, `r4b-inclusion` and `r5-inclusion` take a
`Type/id` or a canonical URL [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:797-805].
A resource named in any inclusion set goes only into the packages it is named for; one named in none goes
into all of them [src: IGPUB-DOCS-3.0.4 multi-version-IGs.md#L88-L104].

**Per-version dependencies** use an extension on `dependsOn`,
`http://hl7.org/fhir/tools/StructureDefinition/ig-dependency-for-version`, which can override the package id
or version for one FHIR version, or remove the dependency from it
[src: IGPUB-DOCS-3.0.4 multi-version-IGs.md#L49-L86]. The publisher reads this URL
[src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:121], but **hl7.fhir.uv.tools 1.3.0
has no StructureDefinition for it** (no file in the package mentions it). So the validator may not know the
extension; not tested.

## Multi-language IGs

**The repository's document is unfinished.** It lists six sources of text in an IG (the IG's resources,
dependency packages, the publisher's own code, external terminologies, narrative pages and the template)
[src: IGPUB-DOCS-3.0.4 multi-lingual-IGs.md#L11-L18]. Its "Setting up the IGs" and "Providing the
translations" sections are headings with no text [src: IGPUB-DOCS-3.0.4 multi-lingual-IGs.md#L64-L69].
What follows comes from the CodeSystem and the code.

| Parameter | Effect | Evidence |
| --- | --- | --- |
| `i18n-default-lang` | The language to assume where a resource doesn't state one; turns translation on | [src: TOOLS-1.3.0 CodeSystem-ig-parameters.json#i18n-default-lang] [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:818-821] |
| `i18n-lang` | One more language to translate the IG into; repeat for each | [src: TOOLS-1.3.0 CodeSystem-ig-parameters.json#i18n-lang] [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:822-825] |
| `translation-sources` | A folder of translation files: `.po`, `.xliff` or `.json`. `translation-supplements` is the deprecated name for the same thing | [src: TOOLS-1.3.0 CodeSystem-ig-parameters.json#translation-sources] [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:826-830] |
| `language-translations-mode` | `preserve` keeps every translation in each language's rendering, reordered so that language comes first; otherwise only that language's value is kept | [src: TOOLS-1.3.0 CodeSystem-ig-parameters.json#language-translations-mode] |
| `resource-language-policy` | `all-ig`, `ig-realm` or `all-realm`: whether to fill in `Resource.language`; any other value stops the build | [src: TOOLS-1.3.0 CodeSystem-ig-parameters.json#resource-language-policy] [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/renderers/ValidationPresenter.java:81-94] [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:899-904] |
| `lang-pack` | The IG is a language pack; its CodeSystems are marked as such | [src: TOOLS-1.3.0 CodeSystem-ig-parameters.json#lang-pack] |

**How translation files are found** (code read, not run):

- **Resource translations.** In each `translation-sources` folder, a file whose name starts with
  `<Type>-<id>` followed by `.`, `-` or `_` belongs to that resource. A file starting with `<Type>-$all`
  belongs to every resource of that type
  [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:2975-2989]. Since 3.0.x after
  3.0.1, the files are read in sorted name order, so translations come out in the same order on every
  machine [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:2980-2984]. Missing folders are
  created [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:4034-4044].
- **Translated pages and other source files.** For a language other than the default, the publisher looks
  for a `translation-sources` folder whose path ends in `/<lang>`, `\<lang>` or `-<lang>`, and in it, a
  file at the same relative path as the original. If there is none, the original is used
  [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherGenerator.java:7011-7031]. This differs from the
  documentation's plan of a `[name]-[lang].[ext]` file per page
  [src: IGPUB-DOCS-3.0.4 multi-lingual-IGs.md#L54-L58].
- **The `translations/` folder.** With translation on, the publisher creates `<root>/translations`
  [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:429]
  [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherGenerator.java:241-243] and gives it to its
  translator as a working folder [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherProcessor.java:1997-2000].
  What it writes there was not traced.

**The publisher's own text** (labels, headings, messages) can be translated at run time with `-po <file>`
or `-po-dir <folder>`. `-po-stale-handling` (`include`, `exclude` or `warn`) decides what to do with
translations whose English source has changed [src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/Publisher.java:1472-1477].
