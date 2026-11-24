# trusted-ig-template Skill Test Questions: Answer Key

Expected answers for [questions.md](questions.md). Don't give this file to an agent under test.

Facts are as the `trusted-ig-template` skill records them, for the 14 rules and the publisher's checks
in IG Publisher 3.0.5, with Ant 1.10.18. Those marked *probe* were confirmed by the skill's probes.

## Who can change what

### TH-01. A child template

- **Expected:** `includes/fragment-css.html` has a harmless extension: it replaces ours, and a child with
  only harmless files has no active content, so it needs no trust and the build runs our scripts with
  the child's include as page content.
  `.xslt` is not a harmless extension, so shipping `scripts/onLoad.xslt` gives the child active
  content; it isn't on the trusted list, so the ci-build runs no scripts at all.
- **Pass if:** the HTML replaces ours; the `.xslt` makes the child untrusted and stops scripts running.
- **Skill:** `resources/publisher-trust.md` (Active content).

### TH-02. Stylesheet extensions

- **Expected:** the publisher treats `.xml` as harmless, so a child template could replace a `.xml`
  stylesheet without the publisher noticing, and our scripts would run its XSLT. `.xslt` isn't harmless,
  so a child that ships one is flagged (rule 3).
- **Pass if:** `.xml` is harmless and replaceable unnoticed.
- **Skill:** `resources/rules.md` (rule 3).

### TH-03. Works locally

- **Expected:** locally `-trust-template` recorded the author's trust in `fhir-settings.json`, so the
  laptop runs it; the ci-build trusts only the publisher's list. The child ships a `.js` file, which
  isn't a harmless extension, so it has active content and isn't on the list. Options: drop the `.js`
  (or have the trusted parent ship it), or get the template onto the trusted list, which is agreed with
  the FHIR Product Director first.
- **Pass if:** local trust is the author's own (`-trust-template`); `.js` is active; remove it or get
  it trusted.
- **Skill:** `resources/publisher-trust.md` (Local builds and the ci-build).

## Where code lives

### WL-01. Two Ant files

- **Expected:** `"script": "scripts/ant.xml"`, `"otherScripts": ["scripts/macros.xml",
  "scripts/schemas.xml"]` (indirect imports too), and `targets`. On the ci-build a template that names a
  script without `otherScripts` stops the build.
- **Pass if:** both files in `otherScripts`. **Partial if:** only the direct import.
- **Skill:** `resources/rules.md` (rule 2).

### WL-02. A stylesheet path

- **Expected:** yes: Ant resolves a relative path against the project's basedir, which the publisher
  sets to the IG's root folder, so this runs whatever the IG puts at `scripts/onLoad.xslt` in its own
  folder (*probe*). Use `style="${ig.scripts}/onLoad.xslt"`.
- **Pass if:** the IG chooses the stylesheet; use `${ig.scripts}`.
- **Skill:** `resources/rules.md` (rule 1).

### WL-03. Configuration data

- **Expected:** no: `data/` is outside `scripts/`, so a child template can replace it, and rule 1 says
  what a script reads as configuration (it names `groupings.txt`) lives in `scripts/`. Move it and read
  `${ig.scripts}/groupings.txt`.
- **Pass if:** move it to `scripts/`.
- **Skill:** `resources/rules.md` (rules 1, 5).

## IG content

### IG-01. A versions file

- **Expected:** a version containing a line break adds a property of the IG's choosing, such as
  `dir.schemas=…`; Ant properties are immutable, so the later `<condition>` can't change it, and the IG
  chooses where `<get>` writes (*probe*). Wrap every IG value in `normalize-space()` (or remove line
  breaks with `translate`), so the stylesheet fixes every property name (rule 7), and use the values
  only as text.
- **Pass if:** a line break injects a property that wins; normalize-space.
- **Skill:** `resources/rules.md` (rule 7).

### IG-02. A program argument

- **Expected:** no: nothing derived from IG content may reach an `<exec>` or `<java>` argument (rule
  6), and executables run with fixed arguments (rule 4). Have a stylesheet write the stamp: it escapes
  the version for HTML (rules 9, 12). An `<echo file=…>` writes the value unescaped, so the audit warns
  (A12).
- **Pass if:** no, and an alternative that doesn't run a program with it.
- **Skill:** `resources/rules.md` (rules 4, 6).

### IG-03. Inline JavaScript

- **Expected:** no: inline JavaScript only joins strings and sets properties, and never evaluates
  (rule 8). Use `concat` and `setProperty` directly.
- **Pass if:** no eval.
- **Skill:** `resources/rules.md` (rule 8).

### IG-04. A language folder

- **Expected:** variable injection (rule 9): the language codes come from the IG, so `../` in one
  writes outside `_includes`, wherever the IG chooses. Check each code against a strict pattern (letters
  and `-`, say) and stop with an error if it doesn't match; don't clean it up; and check the resolved
  path stays inside the temp folder.
- **Pass if:** `../` (path traversal) and a strict-pattern check that stops the build.
- **Partial if:** sanitising (stripping characters) instead of rejecting.
- **Skill:** `resources/rules.md` (rule 9).

## Transforms, Jekyll and network

### PP-01. A pre-process stylesheet

- **Expected:** the publisher runs pre-process transforms itself, on Saxon, from bytes, with external
  stylesheet access off, so `xsl:include`, `xsl:import` and `document()` fail (*probe*); from 3.0.5
  `xsl:result-document` is refused too. Merge the two into one
  self-contained `.xslt` in `scripts/`.
- **Pass if:** includes fail there; make it one file.
- **Skill:** `resources/publisher-trust.md` (Pre-process transforms).

### JK-01. A sitemap

- **Expected:** you can't: no Jekyll plugins (rule 11); `plugins` in `_config.yml`, `_plugins/` and a
  Gemfile are ignored or refused. Generate the sitemap another way: a Liquid page, or a stylesheet in
  `onGenerate` writing it into the Jekyll source.
- **Pass if:** no plugins, and a Liquid or generated alternative.
- **Skill:** `resources/rules.md` (rule 11).

### LQ-01. A page title

- **Expected:** no (rule 12). The titles come from the IG, so HTML in one becomes part of every page:
  write `{{ page.title | escape }}` and `{{ site.data.ig.title | escape }}`. The script is worse:
  `jsonify` doesn't stop a value ending the `<script>` block early. Put the value in an escaped `data-`
  attribute (`data-name="{{ site.data.ig.name | escape }}"`) and read it from the script.
- **Pass if:** `escape` for the title, and a `data-` attribute instead of `jsonify` in the script.
- **Partial if:** `escape` without the script problem.
- **Skill:** `resources/rules.md` (rule 12).

### NW-01. The network gate

- **Expected:** `unless="ig.networkprohibited"` tests whether the property is *set*, and the publisher
  always sets it (`true` or `false`), so the target never runs (*probe*). Use
  `unless="${ig.networkprohibited}"`.
- **Pass if:** the `${…}` form.
- **Skill:** `resources/rules.md` (rule 13).

## Process

### RV-01. Releasing

- **Expected:** a change to `scripts/` (or `config.json`) is reviewed before release (rule 14). A change
  to `includes/footer.html` doesn't need that review: it's page content. Run the audit and the review
  checklist.
- **Pass if:** `scripts/` needs review; `includes/` doesn't.
- **Skill:** `resources/review.md`.

### VR-01. A newer publisher

- **Expected:** read `trusted-template-rules.md` on the publisher's `master` and compare; run the
  skill's `scripts/check_release.py`, which compares the rules file as a whole and every cited line.
- **Pass if:** compare the rules file upstream, or run the check.
- **Skill:** `SKILL.md` (Versions).

## Task

### TK-01. Fix a template

Run `python grade_trusted_ig_template.py <answer>/tk-01`. The ten planted problems and their fixes:

| # | Problem | Rule | Fix |
| --- | --- | --- | --- |
| 1 | `config.json` has no `otherScripts` | 2 | `"otherScripts": ["scripts/common.xml"]` |
| 2 | `style="scripts/onLoad.xslt"` is relative | 1 | `${ig.scripts}/onLoad.xslt` |
| 3 | `checkMenu.xml` is a stylesheet named `.xml` | 3 | rename to `.xslt` |
| 4 | `getVersions.xslt` copies `version` and `title` with their line breaks | 7 | `normalize-space()` |
| 5 | `groupings.txt` is read from `data/` | 1 | move to `scripts/` |
| 6 | `unless="ig.networkprohibited"` | 13 | `unless="${ig.networkprohibited}"` |
| 7 | `stamp.sh` is given `${igVersion}` | 4, 6, 9 | write the stamp with a stylesheet, which escapes it (an unescaped `<echo file>` passes the grader, but the audit warns) |
| 8 | `appendArtifacts` uses `eval` | 8 | `concat` and `setProperty` |
| 9 | the pre-process transform is in `includes/` and includes another file | 10 | one `scripts/processPages.xslt` |
| 10 | a `Gemfile` and `plugins` in `_config.yml` | 11 | remove both |

- **Pass if:** 18/18 checks (G01 to G18) and the list of problems names all ten with their rules.
  **Partial if:** one problem missed, or a fix that drops a feature (G14 to G18).
- **Reference:** [reference/tk-01/](reference/tk-01/). The skill's `scripts/audit_template.py` reports
  0 errors and 0 warnings on it, and 17 errors on the unfixed task.
