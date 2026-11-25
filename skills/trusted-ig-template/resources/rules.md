# The Trusted Template Rules, and How to Follow Them

Baseline: `trusted-template-rules.md` at IG Publisher 3.0.5 (14 rules; 12 when first added in 4e7325f); Ant 1.10.18.
Sources: PUB-3.0.5, PROBES-2026-11-17, PROBES-2026-11-24

The rules are short. This file says what each one asks of a template's files, shows the safe form,
and names the `scripts/audit_template.py` check that looks for it (A01 to A13).

## The threat model

A trusted template runs its Ant scripts and its pre-process transforms on the ci-build. Two kinds of
people you don't control build on it [src: PUB-3.0.5 trusted-template-rules.md:5]
[src: PUB-3.0.5 trusted-template-rules.md:20]:

| Who | What they control | What they can't do |
| --- | --- | --- |
| The author of a **child template** (one with your template as `base`) | Any of your files with a harmless extension, by shipping a file at the same path: `content/`, `includes/`, `layouts/`, `data/`, `translations/`, `.xml`, `.txt`, `.json` files… | Add code: a child that adds code isn't trusted, and its build runs no scripts (see [publisher-trust.md](publisher-trust.md)) |
| The author of an **IG** | The ImplementationGuide resource, every page and resource, and the IG's own folders | Change your template |

Your scripts must stay safe whatever either of them writes. So the questions to ask of every line are:
*could a child template have replaced the file this reads?* and *could an IG have written this value?*

## Where code lives

### 1. Everything a script runs or reads as configuration is in `scripts/` (A02, A04)

Ant files, stylesheets, jars and data files such as `groupings.txt` all go in `scripts/`
[src: PUB-3.0.5 trusted-template-rules.md:9]. Name each one from `${ig.scripts}`:

```xml
<xslt in="${onGenerate.ig.source}xml" out="${ig.temp}/_data/info.json" style="${ig.scripts}/genJson.xslt"/>
<loadfile property="groupings" srcFile="${ig.scripts}/groupings.txt" encoding="UTF-8"/>
```

Never a relative path. The publisher sets the Ant project's basedir to the IG's root folder, so
`style="scripts/genJson.xslt"` runs whatever the IG puts at `<IG root>/scripts/genJson.xslt`
[src: PROBES-2026-11-17 RESULTS.md §3]. A mistyped `{$ig.scripts}` is the same mistake: Ant leaves it
as literal text, which makes the path relative.

### 2. Register every Ant file (A01, A02)

`config.json` names the main file in `script`, and every file it imports, directly or indirectly, in
`otherScripts` [src: PUB-3.0.5 trusted-template-rules.md:10]:

```json
{
  "script": "scripts/ant.xml",
  "otherScripts": ["scripts/common.xml"],
  "targets": { "onLoad": "onLoad", "onGenerate": "onGenerate", "onCheck": "onCheck" }
}
```

`otherScripts` is required even when it is empty (`[]`). Ant files end in `.xml`, a harmless extension:
registering them is what makes the publisher notice a child that replaces one.

### 3. Stylesheets are `.xslt`, never `.xml` (A03)

`.xslt` isn't a harmless extension, so a child that ships one is flagged; a child that replaces a
`.xml` stylesheet isn't. `xsl:include` and `xsl:import` may name only other `.xslt` files in `scripts/`
[src: PUB-3.0.5 trusted-template-rules.md:11].

### 4. Executables live in `scripts/`, under fixed names, with fixed arguments (A04, A05)

[src: PUB-3.0.5 trusted-template-rules.md:12]

```xml
<java jar="${ig.scripts}/plantuml.jar" fork="true" failonerror="true">
  <arg line="-tsvg -o &quot;${ig.temp}/_includes&quot; &quot;${ig.root}/input/images-source/**.plantuml&quot;"/>
</java>
```

Arguments may use the publisher's fixed properties (`ig.scripts`, `ig.template`, `ig.temp`, `ig.root`)
and your own properties built only from them. If the program reads IG files, as here, it is reading
hostile content: make sure it can't be told by that content to include other files, fetch URLs or run
code (for PlantUML, its security profile).

## Files outside `scripts/`

### 5. Anything outside `scripts/` may have been replaced by a child (A04)

`content/`, `includes/`, `layouts/`, `data/`, `translations/` and the rest are page content
[src: PUB-3.0.5 trusted-template-rules.md:16]. You may copy them, or pass them to a stylesheet as
text. Never:

- import them (`<import>`, `xsl:include`), run them, or `eval` them;
- load them as Ant properties (`<loadproperties>`, `<property file>`);
- let them choose a target, a file or a URL.

`<loadfile>` of `${ig.template}/translations/strings.xml` is acceptable only if the property is used as
text, for example passed to a stylesheet as a parameter.

## IG content is hostile

### 6. Nothing derived from the IG reaches a command, a URL, a path or `eval` (A05, A10)

That covers the ImplementationGuide resource (`${onLoad.ig.source}`, `${onGenerate.ig.source}`), its
pages, and any file generated from them [src: PUB-3.0.5 trusted-template-rules.md:20]. It must not
reach:

- an `<exec>` or `<java>` argument;
- a `<get>` URL or destination;
- a file path outside the template and temp folders;
- JavaScript `eval`.

Reading the IG with a stylesheet and writing the result to a fixed file is fine. Using what the
stylesheet produced to *choose* something is not.

### 7. `<loadproperties>` of a generated file: the stylesheet fixes every property name (A06)

[src: PUB-3.0.5 trusted-template-rules.md:21] A properties file has one property per line, so a value
copied with its line breaks writes properties of the IG's choosing. Ant properties can't be changed once
set, so a property loaded from the IG overrides the one your script sets later
[src: PROBES-2026-11-17 RESULTS.md §1]:

```xml
<!-- unsafe: an IG version of "1.0.0&#xa;dir.schemas=/anywhere" sets dir.schemas -->
<xsl:value-of select="concat('igVersion=', f:version/@value, '&#xa;')"/>
<!-- safe: line breaks become spaces -->
<xsl:value-of select="concat('igVersion=', normalize-space(f:version/@value), '&#xa;')"/>
```

Wrap every IG value in `normalize-space()` (or `translate(., '&#xa;&#xd;', '')`). The values are still
the IG's: use them only as text, never in a path, URL or argument.

### 8. Inline JavaScript only joins strings and sets properties (A07)

`<script>` and `<scriptdef>` may do what `appendArtifacts` does: read properties, join strings, set a
property [src: PUB-3.0.5 trusted-template-rules.md:22]. No `eval`, `load`, `Function`, Java classes
or processes, and no `executeTarget` on a name that came from IG content.

```xml
<scriptdef name="appendArtifacts" language="javascript">
  <attribute name="files"/>
  self.project.setProperty("onGenerate.files",
    self.project.getProperty("onGenerate.files").concat(";").concat(attributes.get("files")));
</scriptdef>
```

### 9. Protect your scripts against variable injection (A05, A12)

New in the 14-rule version. Variable injection is a value your script picks up from the IG or from a
child template (a file name, an id, a link, a parameter) being pasted into something that is read again
later, where characters in it mean something [src: PUB-3.0.5 trusted-template-rules.md:23-28]:

| The value goes into | The dangerous characters | What they do |
| --- | --- | --- |
| a properties file | a line break | add properties of the IG's choosing (rule 7; [probe](probes/2026-11-17/RESULTS.md)) |
| a file name or path | `../` | reach files outside the folder you meant |
| `<arg line="…">` | a space or a quote | add command-line arguments |
| XML | `&`, `<`, a `DOCTYPE` | add markup, or make the parser read other files |
| a value Ant reads as a property | `${…}` | expand into another property's value |

The rules' defences [src: PUB-3.0.5 trusted-template-rules.md:30-34]:

- **Check** each such value against a strict pattern of the characters you expect (letters, digits, `.`,
  `-`, `_`) and stop with an error if it doesn't match. Don't try to clean it up.
- **Pass values as separate arguments**: `<arg value="…"/>`, or `<param>` on `<xslt>`. Never paste them
  into a larger string such as `<arg line="…"/>` or the text of a stylesheet.
- **Escape** a value for where it ends up: XML-escape it for XML, URL-encode it for a URL.
- **Check the resolved path** is still inside the template or temp folder before using a value in it.

In XSLT, a check can be a `translate()` that removes the allowed characters and an `xsl:message
terminate="yes"` if anything is left:

```xml
<xsl:variable name="lang" select="f:definition/f:parameter[f:code/@value='i18n-lang']/f:value/@value"/>
<xsl:if test="translate($lang, 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-', '') != ''">
  <xsl:message terminate="yes">i18n-lang '<xsl:value-of select="$lang"/>' isn't a language code</xsl:message>
</xsl:if>
```

The audit can't tell where a value came from. It reports a property it can't trace to the publisher's
fixed ones in a path, an argument or `<echo>` output, and any property pasted into `<arg line>` (A12);
look at each one.

## Pre-process transforms

### 10. Name only your own `.xslt` files; a transform produces its main output only (A08, A11)

[src: PUB-3.0.5 trusted-template-rules.md:38]

```json
"pre-process": [
  { "folder": "input/pagecontent", "relativePath": "_includes", "transform": "template/scripts/processPages.xslt" }
]
```

The path is relative to the IG root, so your own stylesheet is `template/scripts/<name>.xslt`. The
publisher runs pre-process stylesheets itself, on Saxon, with external access turned off, so
`xsl:include`, `xsl:import` and `document()` fail: each transform must be one self-contained file. From
3.0.5 `xsl:result-document` stops the transform [src: PROBES-2026-11-24 RESULTS.md §4]. Don't write to
any other output, and use no extension elements or functions (Xalan's `redirect`, Java calls) in any of
your stylesheets: the ones Ant runs aren't protected the same way.

## Jekyll

### 11. No Jekyll plugins (A09)

No `_plugins/` folder, no `plugins` or `whitelist` in `_config.yml`, no `Gemfile` or `gems.rb`, and no
symbolic links [src: PUB-3.0.5 trusted-template-rules.md:42]. From 3.0.5 the publisher runs Jekyll
with `--safe` and a fixed `--source`, empties `plugins`, `gems` and `whitelist`, and refuses to run it
at all if there is a `Gemfile` or `gems.rb` (see [publisher-trust.md](publisher-trust.md#jekyll)). Write
Liquid that needs nothing more.

## Pages built with Liquid

### 12. Escape what you put into HTML (A13)

New in the 14-rule version. Your layouts and includes build pages from values that come from the IG:
titles, names, descriptions, ids, links and the data files in `_data`. A value written into the page as
it is puts any HTML or script in it into the page, and the script then runs for everyone who reads the
IG on build.fhir.org or hl7.org [src: PUB-3.0.5 trusted-template-rules.md:46-52]:

| Where the value goes | Write |
| --- | --- |
| text, or an attribute (always quoted) | `{{ value \| escape }}`, `title="{{ value \| escape }}"` |
| part of a URL | `{{ value \| url_encode }}` |
| a whole link the IG supplies | only if it starts with `http://`, `https://` or a relative path, never `javascript:` |
| a script | an escaped `data-` attribute, read from the script: `data-name="{{ value \| escape }}"`. Not the script text, even with `jsonify`, which doesn't stop a value ending the `<script>` block |
| which file to include | never a value: no `{% include {{ value }} %}` |

```liquid
<!-- unsafe -->
<h1>{{ site.data.ig.title }}</h1>
<script>var ig = {{ site.data.ig.name | jsonify }};</script>
<!-- safe -->
<h1>{{ site.data.ig.title | escape }}</h1>
<div id="ig" data-name="{{ site.data.ig.name | escape }}"></div>
```

Leave a value unescaped only if it is HTML the publisher has already produced, such as a rendered
narrative or fragment, and say so in a comment beside it.

Templates often choose an include by language or page (`{% include {{include.lang}}/menu.xml %}`), and
the audit reports each one. Under rule 12, list the choices instead (`{% if include.lang == 'fr' %}{%
include fr/menu.xml %}…`), or check the value against a strict pattern before using it. The publisher's
own per-page placeholders, such as `{{[id]}}` and `{{[lang]}}`, are filled in before Jekyll runs; they
aren't Liquid values, and the audit skips them.

## Network

### 13. `<get>` only fixed URLs, and honour `ig.networkprohibited` (A10)

[src: PUB-3.0.5 trusted-template-rules.md:56] A URL may be built from fixed parts, such as a macro
attribute every caller passes as a literal. Gate every target that fetches on the property's **value**:

```xml
<target name="onGenerate.r4-schemas" if="R4" unless="${ig.networkprohibited}">
  <getSchemas version="R4" url="http://hl7.org/fhir/R4/"/>
</target>
```

The publisher always sets `ig.networkprohibited`, to `true` or `false`, so `unless="ig.networkprohibited"`
(the name) means "never run", and leaving the gate off means "always run"
[src: PROBES-2026-11-17 RESULTS.md §2]. A `<get>` inside a `<macrodef>` is gated by the targets that use
the macro.

## Changes

### 14. Have changes reviewed before release

Any change to a trusted template's `scripts/` or `config.json` is reviewed before release, and adding a
template to the trusted list is agreed with the FHIR Product Director first
[src: PUB-3.0.5 trusted-template-rules.md:60]. See [review.md](review.md).
