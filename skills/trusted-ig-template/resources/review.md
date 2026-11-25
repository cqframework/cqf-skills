# Reviewing a Change to a Trusted Template

Baseline: `trusted-template-rules.md` at IG Publisher 3.0.5.
Sources: PUB-3.0.5, PROBES-2026-11-17

Rule 14: every change to a trusted template's `scripts/` or `config.json` is reviewed before it is
released [src: PUB-3.0.5 trusted-template-rules.md:60]. This is a checklist for the author before
asking, and for the reviewer.

## 1. Run the audit

```bash
python scripts/audit_template.py path/to/template
```

It reports each finding with its rule number. ERRORs must be fixed. WARNs need a reason, written in
the pull request: for example "PlantUML reads the IG's `.plantuml` files; it runs with
`-DPLANTUML_SECURITY_PROFILE=SANDBOX`". The audit is static and can't follow every way Ant builds a
value, so it doesn't replace the review below.

## 2. Read the diff of `scripts/` and `config.json`

For every changed line, ask:

| Question | Rule |
| --- | --- |
| Does it run or read a file? Is the path `${ig.scripts}/…`, with no relative paths and no `{$` typos? | 1, 5 |
| Is a new Ant file listed in `otherScripts`? Is a removed one taken out? | 2 |
| Is a new stylesheet `.xslt`, and do its includes name `.xslt` files in `scripts/`? | 3 |
| Does a new `<exec>` or `<java>` run a file in `scripts/` with fixed arguments? | 4 |
| Can any value it uses come from the IG: the IG resource, a page, a file generated from them, a property loaded from one? Does that value reach a command, URL, path or `eval`? | 6 |
| Does a stylesheet whose output is `<loadproperties>`-ed pass every IG value through `normalize-space()`? | 7 |
| Does new inline JavaScript do anything but read properties, join strings and set properties? | 8 |
| Does a value from the IG or a child template go into a path, a properties file, XML, a URL or a command line? Is it checked against a strict pattern, passed as its own `<arg value>` or `<param>`, escaped for where it goes, and its path checked to stay in the template or temp folder? | 9 |
| Does a `pre-process` entry name anything but `template/scripts/<name>.xslt`? Is that file self-contained, with one output? | 10 |
| Does it add a Jekyll plugin, `Gemfile` or symlink, or `plugins` in `_config.yml`? | 11 |
| Does a changed layout or include write an IG value into the page without `escape` (or `url_encode` in a URL), put one into a `<script>`, use a link the IG supplies without checking its scheme, or include a file named by a value? | 12 |
| Does a new `<get>` use a fixed URL, and is its target gated with `unless="${ig.networkprohibited}"`? | 13 |

Then follow each value backwards. A property is only as trustworthy as everything that could have set
it first: Ant properties can't be overwritten, so a `<loadproperties>` that runs earlier wins over a
`<property>` or `<condition>` that runs later [src: PROBES-2026-11-17 RESULTS.md §1].

## 3. Build with it, and with a hostile IG

From 3.0.5 a local build checks trust too: a template that runs scripts and isn't trusted stops the
build until you pass `-trust-template` (see [publisher-trust.md](publisher-trust.md#local-builds-and-the-ci-build)).
What a local build can show:

- **Your template still works.** Build a real IG with the template from a local folder: in the `[IG]`
  section of `ig.ini`, `<template id>#<version> = <folder>`, which also works for a base template and
  is ignored on the ci-build [src: PUB-3.0.5 …/templates/TemplateManager.java:87-97]. Loaded that way,
  the template keeps its own package id and version, so the trust check treats it as the trusted
  template (read from source; not run). Naming the folder in `template =` instead makes it an untrusted
  template that needs `-trust-template`.
- **Hostile values stay text.** Build an IG whose `version`, `title`, page names and parameters contain
  line breaks, `=`, `;`, quotes, `../`, `${…}`, `&`, and HTML such as `<script>alert(1)</script>` and
  `javascript:` links. Check that the build fails safely or shows them as text on every page, and that no
  file appears outside `output/`, `temp/` and `template/`.
- **The network gate works.** Build with network access prohibited and confirm no `<get>` runs.

## 4. Release

Note the review in the release, and keep `scripts/` changes separate from page-content changes so the
reviewed part is easy to see. A new template, or a new id, can't run scripts until it is added to the
publisher's trusted list, which is agreed with the FHIR Product Director first.

## Responsible disclosure

If a review turns up a way for a child template or an IG to run code through a template that is
already released, don't describe it in a public issue or pull request. Report it privately to the
template's maintainers and to the IG Publisher's maintainers, and fix it before explaining it.
