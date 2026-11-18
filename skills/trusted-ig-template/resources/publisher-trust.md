# How the IG Publisher Decides What a Template May Run

Baseline: IG Publisher at 4e7325f (3.0.4 plus five commits), Ant 1.10.18, org.hl7.fhir.core 7.0.6.
Sources: PUB-4e7325f, CORE-7.0.6, PROBES-2026-11-17

What the publisher itself checks, and what it gives a template's scripts. Everything else in
[rules.md](rules.md) is the template author's job: the rules describe what a trusted template must not
do whatever the publisher catches.

## The template chain

A template names its base in `package.json` (`base`, which must also be a dependency). The publisher
installs the base first and then unpacks each child over it into `<IG root>/template/`, so a child's
file replaces the base's file at the same path
[src: PUB-4e7325f …/templates/TemplateManager.java:189-204]. The `config.json` files are merged, base
first: a child's object properties merge, its primitive values replace the base's, and its **arrays
are appended** to the base's [src: PUB-4e7325f …/templates/TemplateManager.java:304-307]
[src: PUB-4e7325f …/templates/TemplateManager.java:357-376].

## Active content, and the trusted list

The publisher looks at each template in the chain on its own
[src: PUB-4e7325f …/templates/TemplateManager.java:222-302]. A template has *active content* when:

| Trigger | Where |
| --- | --- |
| its `config.json` has `script` or `targets` | `TemplateManager.java:222-224` |
| it ships a file at the path of an ant file an earlier template registered (in `script` or `otherScripts`) | `TemplateManager.java:282-284` |
| it ships a file whose extension isn't on the harmless list | `TemplateManager.java:285-297` |

The harmless extensions are `.html .css .png .gif .oet .json .xml .ico .jpg .md .ini .po .eot .otf .svg
.ttf .woff .woff2 .txt .yml .yaml .liquid .gitignore` (`.po` was added after 3.0.4). `LICENSE`,
`README`, `.gitignore`, `.gitattributes`, `.gitkeep` and some `.github/` housekeeping files are skipped
[src: PUB-4e7325f …/templates/TemplateManager.java:248-287]. So `.xslt`, `.jar`, `.js`, `.rb`, `.sh`
and `.bat` all count as active, while `.xml`, `.txt` and `.json` don't. That is why rule 3 says
stylesheets are `.xslt`: a child can replace a `.xml` stylesheet without the publisher noticing.

A template with active content must be loaded by its own package id, and that id must be on the
publisher's hard-coded trusted list; otherwise the build can't run scripts
[src: PUB-4e7325f …/templates/TemplateManager.java:403-440]. Adding a template to the list is agreed
with the FHIR Product Director first [src: PUB-4e7325f trusted-template-rules.md:38].

A template that names a `script` must also have `otherScripts` (an empty array if there are none). On
the ci-build a template without it stops the build; locally the publisher prints a warning
[src: PUB-4e7325f …/templates/TemplateManager.java:226-243].

## Local builds and the ci-build

The ci-build runs the publisher with `-auto-ig-build` [src: PUB-4e7325f …/publisher/Publisher.java:1637-1638]
[src: PUB-4e7325f …/publisher/PublisherIGLoader.java:372]. Only then does trust matter:

- **Locally, every template is trusted**, whatever it contains
  [src: PUB-4e7325f …/templates/TemplateManager.java:143-145]. A local build never shows you that a
  child of your template has become untrusted.
- **On the ci-build, `ig.ini` template overrides are ignored**: they would let an IG substitute its
  own folder for a trusted template id [src: PUB-4e7325f …/templates/TemplateManager.java:121-125].
- When the chain isn't trusted, the publisher logs that the template is not trusted, and running any
  ant target fails with "Unable to execute … is not trusted (reason: …)"
  [src: PUB-4e7325f …/templates/TemplateManager.java:146-148]
  [src: PUB-4e7325f …/templates/Template.java:463-465].

## What your ant script gets

`config.json`'s `script` is loaded as an Ant project, and `targets` must be present with it
[src: PUB-4e7325f …/templates/Template.java:139-142]. The publisher calls these targets:

| `targets` key | When | The IG |
| --- | --- | --- |
| `onLoad` | after the IG resource is loaded | written for the script to read, and the script's version is read back, so it may change the IG |
| `onGenerate` | while the Jekyll source is prepared, after the template's `content/` folders are copied into it | written to read; changes to it are read back except its resources |
| `onJekyll` | read from `config.json`, but nothing calls it at this commit | not written |
| `onCheck` | after the build, for QA | not written |

[src: PUB-4e7325f …/templates/Template.java:701-756]

Properties the publisher sets [src: PUB-4e7325f …/templates/Template.java:165-169]
[src: PUB-4e7325f …/templates/Template.java:735]:

| Property | Value | Trust it? |
| --- | --- | --- |
| basedir | the IG's root folder | No: a relative path in any task resolves here, in the IG [src: PROBES-2026-11-17 RESULTS.md §3] |
| `ig.root` | the IG's root folder | Only as a place to write into, never to choose what runs |
| `ig.template` | `<IG root>/template`, the merged chain | Its `scripts/` folder only; the rest is replaceable by a child |
| `ig.scripts` | `<IG root>/template/scripts` | Yes: start every stylesheet, jar and data path with it |
| `ig.temp` | the Jekyll source folder (onGenerate) | A place to write |
| `ig.networkprohibited` | always set, `true` or `false` | Test its value: `unless="${ig.networkprohibited}"` [src: PROBES-2026-11-17 RESULTS.md §2] |
| `<target>.ig.source`, `<target>.ig.dest` | the IG written for the target, and where to put the changed one | The IG is hostile content (rule 6) |

## Pre-process transforms

`config.json`'s `pre-process` array lists folders to copy into the Jekyll source, each optionally
through a `transform` stylesheet. Its paths are relative to the IG root, so a template's own stylesheet
is `template/scripts/<name>.xslt` [src: PUB-4e7325f …/publisher/PublisherIGLoader.java:393-397]
[src: PUB-4e7325f …/publisher/PublisherIGLoader.java:1611-1627].

Transforms run in the publisher itself, not in Ant, with the external DTD and stylesheet access
attributes set to `""` and the stylesheet given as bytes
[src: PUB-4e7325f …/publisher/XSLTransformer.java:47-59] [src: CORE-7.0.6 …/xml/XMLUtil.java:527-532].
So `xsl:include`, `xsl:import` and `document()` fail in a pre-process stylesheet: it has to be one
self-contained file [src: PROBES-2026-11-17 RESULTS.md §4].

## Versions

Ant is 1.10.18 [src: PUB-4e7325f pom.xml:83-86], and the XSLT processor is the JDK's (XSLT 1.0) unless
one is on the classpath. Write XSLT 1.0.
