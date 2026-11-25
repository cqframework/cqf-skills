# How the IG Publisher Decides What a Template May Run

Baseline: IG Publisher 3.0.5, Ant 1.10.18, org.hl7.fhir.core 7.0.6 (with Saxon-HE 13.0).
Sources: PUB-3.0.5, CORE-7.0.6, PROBES-2026-11-17, PROBES-2026-11-24

What the publisher itself checks, and what it gives a template's scripts. 3.0.5 enforces much more than
3.0.4 did (see [Changed in 3.0.5](#changed-in-305)). Everything else in [rules.md](rules.md) is the
template author's job: the rules describe what a trusted template must not do, whatever the publisher
catches.

## The template chain

A template names its base in `package.json` (`base`, which must also be a dependency). The publisher
installs the base first and then unpacks each child over it into `<IG root>/template/`, so a child's
file replaces the base's file at the same path
[src: PUB-3.0.5 …/templates/TemplateManager.java:260-275]. The `config.json` files are merged, base
first: a child's object properties merge, its primitive values replace the base's, and its **arrays
are appended** to the base's [src: PUB-3.0.5 …/templates/TemplateManager.java:294-302]
[src: PUB-3.0.5 …/templates/TemplateManager.java:493-512].

## Active content

The publisher looks at each template in the chain on its own. A template has *active content* when
[src: PUB-3.0.5 …/templates/TemplateManager.java:319-422]:

| Trigger | Lines |
| --- | --- |
| its `config.json` has `script` or `targets` | `TemplateManager.java:324-326` |
| its `config.json` has a `pre-process` entry with a `transform` (new in 3.0.5) | `TemplateManager.java:328-334` |
| it ships a file whose unpacked path is outside the template folder (new in 3.0.5) | `TemplateManager.java:360-364` |
| it ships **any** file under `scripts/`, whatever its extension (new in 3.0.5) | `TemplateManager.java:396-401` |
| it ships a file at the path of an ant file an earlier template registered (in `script` or `otherScripts`) | `TemplateManager.java:403-405` |
| it ships a file whose extension isn't on the harmless list | `TemplateManager.java:406-413` |

The harmless extensions are `.html .css .png .gif .oet .json .xml .ico .jpg .md .ini .po .eot .otf .svg
.ttf .woff .woff2 .txt .yml .yaml .liquid .gitignore`. `LICENSE`, `README`, `.gitignore`,
`.gitattributes`, `.gitkeep` and some `.github/` housekeeping files are skipped
[src: PUB-3.0.5 …/templates/TemplateManager.java:367-394]. So outside `scripts/`, `.xslt`, `.jar`, `.js`,
`.rb`, `.sh` and `.bat` count as active, while `.xml`, `.txt` and `.json` don't. That is why rule 3 says
stylesheets are `.xslt`, and why rule 2 registers every ant file: the publisher notices a child that
ships either.

A template that names a `script` must also have `otherScripts` (an empty array if there are none). On
the ci-build a template without it stops the build; locally the publisher prints a warning
[src: PUB-3.0.5 …/templates/TemplateManager.java:335-353].

A template in the IG's own folder (`template = #template`) goes through the same check: it is never
trusted, so on the ci-build it can't have active content (new in 3.0.5)
[src: PUB-3.0.5 …/templates/TemplateManager.java:424-452].

## The trusted list

A template with active content is trusted only if [src: PUB-3.0.5 …/templates/TemplateManager.java:566-594]:

- it was named by its own package id;
- that id is on the trusted list, `TrustedTemplates.java`, which records the GitHub repository each
  template is built from [src: PUB-3.0.5 …/templates/TrustedTemplates.java:24-50];
- the version is a release: `n.n.n`, `#current`, or no version. A branch build (`current$branch`), a
  dev build or a labelled version (`-cibuild`) of a trusted template isn't trusted, whether the IG names
  it or another template names it as its base (new in 3.0.5).

On the ci-build, a build that claims a trusted template's package id must be that template, built from
its recorded repository, and an IG can't claim one at all
[src: PUB-3.0.5 …/publisher/PublisherIGLoader.java:1547-1580]. A dependency fetched from an IG's own
location (not a package server) is refused if it is a template or claims a trusted template's id
[src: PUB-3.0.5 …/publisher/PublisherIGLoader.java:2325-2342]. Adding a template to the list is agreed
with the FHIR Product Director first [src: PUB-3.0.5 trusted-template-rules.md:60].

## Local builds and the ci-build

The ci-build runs the publisher with `-auto-ig-build` [src: PUB-3.0.5 …/publisher/Publisher.java:1662-1663]
[src: PUB-3.0.5 …/publisher/PublisherIGLoader.java:379].

- **On the ci-build**, an untrusted chain runs no scripts and no transforms, and `ig.ini` template
  overrides are ignored: they would let an IG substitute its own folder for a trusted template id
  [src: PUB-3.0.5 …/templates/TemplateManager.java:132-136].
- **Locally, an untrusted template that runs scripts stops the build** (new in 3.0.5; before, a local
  build ran any template). That includes your own template while you work on it from a folder. Run
  once with `-trust-template <id>` (the id as the IG names it, without a version) or `-trust-template
  all`; it is recorded in `trustedTemplates` in `fhir-settings.json`
  [src: PUB-3.0.5 …/templates/TemplateManager.java:155-159]
  [src: PUB-3.0.5 …/templates/TemplateManager.java:196-221]. A local build of your trusted template as
  a released version shows whether it is trusted; one from a folder doesn't.
- When the chain isn't trusted, the publisher logs that the template is not trusted
  [src: PUB-3.0.5 …/templates/TemplateManager.java:160-162], **doesn't parse its ant file at all**
  (Ant runs any task outside a target while parsing; new in 3.0.5)
  [src: PUB-3.0.5 …/templates/Template.java:152-159], and running a target fails with "Unable to
  execute … is not trusted (reason: …)" [src: PUB-3.0.5 …/templates/Template.java:468-470].

## What your ant script gets

`config.json`'s `script` is loaded as an Ant project, and `targets` must be present with it
[src: PUB-3.0.5 …/templates/Template.java:139-142]. The publisher calls these targets
[src: PUB-3.0.5 …/templates/Template.java:720-779]:

| `targets` key | When | The IG |
| --- | --- | --- |
| `onLoad` | after the IG resource is loaded | written for the script to read, and the script's version is read back, so it may change the IG |
| `onGenerate` | while the Jekyll source is prepared, after the template's `content/` folders are copied into it | written to read; changes to it are read back except its resources |
| `onJekyll` | just before Jekyll runs, unless `-generation-off` [src: PUB-3.0.5 …/publisher/PublisherGenerator.java:496-499] [src: PUB-3.0.5 …/publisher/PublisherGenerator.java:4459-4466] | not written |
| `onCheck` | after the build, for QA | not written |

Properties the publisher sets [src: PUB-3.0.5 …/templates/Template.java:169-173]
[src: PUB-3.0.5 …/templates/Template.java:755]:

| Property | Value | Trust it? |
| --- | --- | --- |
| basedir | the IG's root folder | No: a relative path in any task resolves here, in the IG [src: PROBES-2026-11-17 RESULTS.md §3] |
| `ig.root` | the IG's root folder | Only as a place to write into, never to choose what runs |
| `ig.template` | `<IG root>/template`, the merged chain | Its `scripts/` folder only; the rest is replaceable by a child |
| `ig.scripts` | `<IG root>/template/scripts` | Yes: start every stylesheet, jar and data path with it |
| `ig.temp` | the Jekyll source folder (onGenerate) | A place to write |
| `ig.networkprohibited` | always set, `true` or `false` | Test its value: `unless="${ig.networkprohibited}"` [src: PROBES-2026-11-17 RESULTS.md §2] |
| `<target>.ig.source`, `<target>.ig.dest` | the IG written for the target, and where to put the changed one | The IG is hostile content (rule 6) |

XML parsers in the publisher's JVM, Ant's `<xslt>` included, don't read external DTDs or entities, so an
IG's XML can't pull a local file into your output (new in 3.0.5; `-Djavax.xml.accessExternalDTD=all`
turns it back on, and it doesn't reach a forked `<java>`) [src: PUB-3.0.5 …/publisher/Publisher.java:160-182].

## Pre-process transforms

`config.json`'s `pre-process` array lists folders to copy into the Jekyll source, each optionally
through a `transform` stylesheet. Its paths are relative to the IG root, so a template's own stylesheet
is `template/scripts/<name>.xslt` [src: PUB-3.0.5 …/publisher/PublisherIGLoader.java:400-404]
[src: PUB-3.0.5 …/publisher/PublisherIGLoader.java:1673-1694]. A transform is active content: an
untrusted template's transform isn't loaded, and the build stops (new in 3.0.5)
[src: PUB-3.0.5 …/publisher/PublisherIGLoader.java:1679-1682].

Transforms run in the publisher itself, not in Ant, with Saxon (Saxon-HE 13.0, from the core library
[src: CORE-7.0.6 pom.xml:41]), external DTD and stylesheet access off, the stylesheet given as bytes,
and a handler that refuses `xsl:result-document`; any other XSLT processor is refused
[src: PUB-3.0.5 …/publisher/XSLTransformer.java:52-77] [src: CORE-7.0.6 …/xml/XMLUtil.java:527-532].
So [src: PROBES-2026-11-24 RESULTS.md §4]:

- `xsl:include`, `xsl:import` and `document()` fail: a pre-process stylesheet is one self-contained file;
- `xsl:result-document` stops the transform: it produces its main output and nothing else;
- Saxon-HE has no Java extension functions;
- XSLT 2.0 and 3.0 are available.

## Jekyll

Jekyll always runs with `--safe` (no `_plugins/`, no `plugins_dir`, no symlinks) and an explicit
`--source`, with a publisher config file read after the IG's `_config.yml` that empties `plugins`, `gems`
and `whitelist`, and with `JEKYLL_NO_BUNDLER_REQUIRE` set. The publisher refuses to run Jekyll at all if
the folder holds a `Gemfile` or `gems.rb` [src: PUB-3.0.5 …/publisher/PublisherGenerator.java:4561-4584].

## Changed in 3.0.5

Before 3.0.5, the rules described protections the publisher didn't yet have: `scripts/` content and
pre-process transforms didn't count as active content, local builds trusted every template, an untrusted
template's ant file was still parsed, pre-process transforms ran without a trust check, and Jekyll ran
without `--safe`. All of these are enforced from 3.0.5. Build trusted templates for 3.0.5 or later, and
follow the rules anyway: they also cover what no publisher check can, such as variable injection
(rule 9) and escaping in Liquid (rule 12).

## Versions

Ant is 1.10.18 [src: PUB-3.0.5 pom.xml:83-86]. Pre-process transforms run on Saxon-HE 13.0.
