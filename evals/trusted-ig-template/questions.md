# trusted-ig-template Skill Test Questions

Questions for an agent that maintains an IG Publisher template on the trusted list. Answer each in a
few sentences, as you would to another template author. Then do task TK-01. The answer key is in
`answers.md`; don't read it.

"The rules" are the IG Publisher's `trusted-template-rules.md`. "The ci-build" is the HL7 auto-build.

## Who can change what

**TH-01. A child template.** Someone builds a child template on ours. It ships its own
`includes/fragment-css.html` and its own `scripts/onLoad.xslt`. What happens to each on the ci-build?

**TH-02. Stylesheet extensions.** Why must our stylesheets be `.xslt` rather than `.xml`? They're both
XML.

**TH-03. Works locally.** A child template of ours builds fine on a laptop, but on the ci-build the log
says "Unable to execute 'onGenerate' … is not trusted (reason: Template has file extensions: [.js])".
What happened, and what are the child author's options?

## Where code lives

**WL-01. Two Ant files.** Our `scripts/ant.xml` imports `scripts/macros.xml`, which imports
`scripts/schemas.xml`. What goes in `config.json`?

**WL-02. A stylesheet path.** A target has `<xslt in="…" out="…" style="scripts/onLoad.xslt"/>`. The
file is in our `scripts/` folder and the build works. Is anything wrong?

**WL-03. Configuration data.** Our script reads a table of artifact groupings with
`<loadfile srcFile="${ig.template}/data/groupings.txt"/>`. Is that allowed?

## IG content

**IG-01. A versions file.** A stylesheet writes `igVersion=` followed by the IG's `version` into
`versions.txt`, which we then `<loadproperties>`. Later a `<condition>` sets `dir.schemas`, the
destination of a `<get>`. What can an IG author do, and how do we fix it?

**IG-02. A program argument.** Can we run `<exec executable="${ig.scripts}/stamp.sh">` with
`<arg value="${igVersion}"/>`, where `igVersion` came from the IG?

**IG-03. Inline JavaScript.** A `<scriptdef>` builds a statement as a string from an attribute and runs
it with `eval`. It's only used to append to a property. Is that acceptable?

## Transforms, Jekyll and network

**PP-01. A pre-process stylesheet.** Our `pre-process` transform `template/scripts/processPages.xslt`
uses `<xsl:include href="pageUtils.xslt"/>`. Both files are in `scripts/`. The transform fails. Why, and
what do we do?

**JK-01. A sitemap.** We'd like `jekyll-sitemap` in the template. How?

**NW-01. The network gate.** Our schema download target has `unless="ig.networkprohibited"`, and the
schemas are never downloaded, even with network access. Why?

## Process

**RV-01. Releasing.** What has to happen before we release a change to `scripts/ant.xml`? And to
`includes/footer.html`?

**VR-01. A newer publisher.** How do we find out whether the rules, or the publisher's checks, have
changed since the skill was written?

## Task

**TK-01. Fix a template.** `task/tk-01/` is a template on the trusted list (synthetic). Copy it, and
change the copy so it follows the rules, while keeping what it does: it loads, versions, reads
groupings, fetches a schema, checks the menu, writes a version stamp for the footer, summarises the IG,
adds anchors to headings in page content, and appends to `onGenerate.files`. Save the result as
`tk-01/`, and list each problem you fixed and the rule it broke.
