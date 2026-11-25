---
name: trusted-ig-template
description: Writes, reviews and audits HL7 FHIR IG Publisher templates on the trusted list, which may run Ant scripts and pre-process XSLT on the ci-build, against the publisher's 14 trusted template rules. Covers scripts/ and config.json (script, otherScripts, targets, pre-process), stylesheets, jars, loadproperties, inline JavaScript, variable injection, Jekyll plugins, escaping IG values in Liquid layouts and includes, get tasks and ig.networkprohibited, what child templates and IG authors can control, and how the publisher decides trust (the trusted list, released versions only, -trust-template for local builds). Use when someone edits or reviews a trusted template such as fhir.base.template, hl7.fhir.template or cqf.fhir.template, or asks why a build won't run a template's scripts. Pinned to IG Publisher 3.0.5 and its rules file.
license: Apache-2.0
---

# Trusted IG Templates

An IG Publisher template is a package of page layouts, includes, assets and, optionally, code: Ant
scripts the publisher runs at fixed points, and XSLT it runs over IG pages. Only templates on the
publisher's trusted list may run code on the ci-build, and from 3.0.5 a local build asks before running
any other. Anyone can build a child template on a trusted one, and anyone can write an IG with it, so a
trusted template's code, and the pages it builds, must be safe whatever they write. The IG Publisher's
`trusted-template-rules.md` says how. This skill is for the authors and reviewers of those templates.

For configuring and running the publisher for an IG, use the `ig-publisher` skill.

## Versions

| Layer | Pinned at | Why it matters |
| --- | --- | --- |
| The rules | `trusted-template-rules.md` at IG Publisher 3.0.5: 14 rules (12 when first added, in 4e7325f on 2026-11-18) | New; expect them to change |
| IG Publisher | 3.0.5 (2026-11-20) | The first release that enforces most of the rules |
| Ant | 1.10.18, the publisher's | Property and path semantics the rules depend on |
| XSLT | Saxon-HE 13.0 for pre-process transforms | Single-file, no secondary output, no Java calls |

**When the publisher is newer.** The rules and the publisher's checks are being tightened together,
so read `trusted-template-rules.md` on the publisher's `master` first, and compare it with the rules in
[rules.md](resources/rules.md). `scripts/check_release.py` reports whether the rules file or the cited
publisher code has changed. Treat the rules as yours to follow whatever the publisher enforces:
they describe what a trusted template must not do, not a sandbox to rely on.

**When the publisher is older.** Before 3.0.5 the publisher enforced much less: local builds trusted
every template, `scripts/` content and pre-process transforms weren't active content, and Jekyll didn't
run in safe mode ([publisher-trust.md](resources/publisher-trust.md#changed-in-305)).

## How to Work

1. **Read the rule before changing the file.** [rules.md](resources/rules.md) gives each rule with
   the safe form and the mistakes that break it.
2. **Think as the two people you don't control.** A child template author can replace any of your
   files with a harmless extension outside `scripts/` (everything in `content/`, `includes/`,
   `layouts/`…, and any `.xml`, `.txt` or `.json` there). An IG author controls the IG resource, its
   pages, its `_data` and anything generated from them.
3. **Run the audit**: `python scripts/audit_template.py <template folder>`. Fix every ERROR; justify
   every WARN.
4. **Have it reviewed** (rule 14) with [review.md](resources/review.md).
5. **Don't publish a weakness.** If you find a way to get code run through a released template, report
   it privately to its maintainers and the publisher's, not in a public issue.

## Quick Reference

```json
{
  "script": "scripts/ant.xml",
  "otherScripts": ["scripts/common.xml"],
  "targets": { "onLoad": "onLoad", "onGenerate": "onGenerate", "onCheck": "onCheck" },
  "pre-process": [
    { "folder": "input/pagecontent", "relativePath": "_includes", "transform": "template/scripts/processPages.xslt" }
  ]
}
```

```xml
<project name="template" basedir=".">
  <import file="${ig.scripts}/common.xml"/>                          <!-- registered in otherScripts -->
  <target name="onGenerate.versions">
    <xslt in="${onGenerate.ig.source}xml" out="${ig.template}/versions.txt"
          style="${ig.scripts}/getVersions.xslt"/>                   <!-- .xslt, from ${ig.scripts} -->
    <loadproperties srcfile="${ig.template}/versions.txt"/>          <!-- stylesheet uses normalize-space() -->
  </target>
  <target name="onGenerate.schemas" unless="${ig.networkprohibited}"> <!-- the value, not the name -->
    <get src="http://hl7.org/fhir/R4/fhir-single.xsd" dest="${ig.template}/schemas"/>
  </target>
</project>
```

```liquid
<h1>{{ site.data.ig.title | escape }}</h1>                            <!-- escape every IG value -->
<a href="{{ base }}/{{ page.id | url_encode }}.html">…</a>             <!-- url_encode inside a URL -->
```

| The publisher gives you | Value | Use it for |
| --- | --- | --- |
| `${ig.scripts}` | `<IG root>/template/scripts` | Every stylesheet, jar, Ant file and data file |
| `${ig.template}` | `<IG root>/template` | Writing work files; reading only from `scripts/` |
| `${ig.temp}` | the Jekyll source folder | Writing generated pages and data |
| `${ig.root}`, basedir | the IG's folder | Reading IG files as hostile input; relative paths resolve here |
| `${ig.networkprohibited}` | always `true` or `false` | `unless="${ig.networkprohibited}"` on every target that fetches |

## The Fourteen Rules

| # | Rule | Audit |
| --- | --- | --- |
| 1 | Everything scripts run or read as configuration is in `scripts/` | A02, A04 |
| 2 | Register every Ant file: `script`, and `otherScripts` for all it imports | A01, A02 |
| 3 | Stylesheets are `.xslt`; includes and imports name `.xslt` files in `scripts/` | A03 |
| 4 | Executables are in `scripts/`, under fixed names, with fixed arguments | A04, A05 |
| 5 | Files outside `scripts/` are page content: copy them or pass them as text, nothing more | A04 |
| 6 | Nothing derived from IG content reaches a command, `<get>`, a path outside template and temp, or `eval` | A05, A10 |
| 7 | `<loadproperties>` a generated file only when your stylesheet fixes every property name | A06 |
| 8 | Inline JavaScript only joins strings and sets properties | A07 |
| 9 | Protect against variable injection: check values against a strict pattern, pass them as separate arguments, escape them, keep paths inside | A05, A12 |
| 10 | Pre-process transforms name only your own `.xslt`; one output, no file reads, no fetches | A08, A11 |
| 11 | No Jekyll plugins, Gemfiles or symlinks | A09 |
| 12 | Escape IG values in HTML: `escape` for text and attributes, `url_encode` in URLs, nothing into scripts, no dynamic includes | A13 |
| 13 | `<get>` only fixed URLs, and honour `ig.networkprohibited` | A10 |
| 14 | Changes to `scripts/` or `config.json` are reviewed before release | review.md |

## Known Gotchas

All confirmed by probes (`resources/probes/`) or the publisher's code.

- **A relative path in an Ant task is the IG's file.** The project's basedir is the IG root, so
  `style="scripts/x.xslt"` runs the IG's `scripts/x.xslt`. A typo such as `{$ig.scripts}` does the same:
  [rules.md](resources/rules.md#1-everything-a-script-runs-or-reads-as-configuration-is-in-scripts-a02-a04)
- **A line break in an IG value adds a property** to a file you `<loadproperties>`, and because Ant
  properties are immutable, the IG's value wins over yours:
  [rules.md](resources/rules.md#7-loadproperties-of-a-generated-file-the-stylesheet-fixes-every-property-name-a06)
- **`unless="ig.networkprohibited"` never runs the target**: the publisher always sets the property, so
  test its value with `${…}`:
  [rules.md](resources/rules.md#13-get-only-fixed-urls-and-honour-ignetworkprohibited-a10)
- **`.xml` is a harmless extension outside `scripts/`**, so a child can replace an `.xml` stylesheet or
  an unregistered Ant file there without making itself untrusted. Hence `.xslt`, `scripts/`, and
  `otherScripts`: [publisher-trust.md](resources/publisher-trust.md#active-content)
- **From 3.0.5 a local build stops for your own template from a folder** (it isn't trusted by id) until
  you pass `-trust-template <id>`, and on the ci-build only a released version (or `#current`) of a
  trusted template runs scripts, so `#dev` doesn't:
  [publisher-trust.md](resources/publisher-trust.md#local-builds-and-the-ci-build)
- **Pre-process stylesheets can't include, import, `document()` or `xsl:result-document`**: each must be
  one file with one output: [publisher-trust.md](resources/publisher-trust.md#pre-process-transforms)
- **`jsonify` doesn't make an IG value safe in a `<script>`**: a value can end the script block. Put it
  in an escaped `data-` attribute instead:
  [rules.md](resources/rules.md#12-escape-what-you-put-into-html-a13)
- **`config.json` is merged down the template chain**: a child's arrays are appended to yours and its
  values replace yours. A child that sets `script`, `targets` or a `pre-process` `transform` makes itself
  untrusted: [publisher-trust.md](resources/publisher-trust.md#the-template-chain)

## Supporting Files

| File | Contents |
| --- | --- |
| [resources/rules.md](resources/rules.md) | The fourteen rules, the threat model, the safe forms, and the audit checks |
| [resources/publisher-trust.md](resources/publisher-trust.md) | How the publisher loads a template chain, decides trust, and runs scripts, transforms and Jekyll |
| [resources/review.md](resources/review.md) | The rule 14 review checklist, local testing with a hostile IG, and disclosure |
| [resources/SOURCES.md](resources/SOURCES.md) | The sources cited, pinned |
| [resources/probes/2026-11-17/RESULTS.md](resources/probes/2026-11-17/RESULTS.md) | The Ant probes, and pre-process XSLT on 4e7325f, with their files |
| [resources/probes/2026-11-24/RESULTS.md](resources/probes/2026-11-24/RESULTS.md) | Pre-process XSLT on Saxon, as 3.0.5 runs it |
| [scripts/audit_template.py](scripts/audit_template.py) | Static audit of a template folder against the rules (A01 to A13) |
| [scripts/check_release.py](scripts/check_release.py) | Weekly check: has the rules file, or the cited publisher code, changed? |
| [scripts/lint_skill_trusted_ig_template.py](scripts/lint_skill_trusted_ig_template.py) | Lints this skill's citations; `scripts/fetch-sources.sh` caches the sources it checks against |
