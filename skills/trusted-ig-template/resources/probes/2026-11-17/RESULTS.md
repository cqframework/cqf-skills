# Probes, 2026-11-17

Small, self-contained runs of the Ant and XSLT behavior the rules depend on. Nothing here runs the IG
Publisher: each probe reproduces one step the way the publisher sets it up, as cited.

- Ant 1.10.18, the version the IG Publisher's `pom.xml` names, run as
  `java -cp ant-1.10.18.jar;ant-launcher-1.10.18.jar org.apache.tools.ant.Main` in each folder.
- OpenJDK 21.0.9 and its built-in XSLT processor (XSLTC, XSLT 1.0), which is what Ant's `<xslt>` and
  the publisher's pre-process transforms get from `TransformerFactory.newInstance()` unless another
  processor is on the classpath.

Run them in a copy of this folder; they write output files.

## 1. `<loadproperties>` of a file built from IG content

`1-loadproperties/`: a stylesheet writes `R4=Y` and `igVersion=<the IG's version>` to a text file,
`<loadproperties>` loads it, and only then is `dir.schemas` set with `<condition>`. The IG's version is
`1.0.0`, a line break (`&#xa;`, which FHIR's `string` allows) and `dir.schemas=C:/chosen-by-the-ig`.

```text
[echo] versions: igVersion=[1.0.0] dir.schemas=[C:/chosen-by-the-ig]
[echo] versions-fixed: igVersion=[1.0.0 dir.schemas=C:/chosen-by-the-ig] dir.schemas=[…/input-cache/schemas]
out-versions.txt:
R4=Y
igVersion=1.0.0
dir.schemas=C:/chosen-by-the-ig
```

- The line break in the value starts a new property, so the IG names a property of its own choosing.
- Ant properties are immutable: the `<condition>` that runs afterwards can't change `dir.schemas`, so the
  IG's value wins. Here it would be the destination of the template's `<get>`.
- With `normalize-space()` around the value (`versions-fixed.xslt`), the line break becomes a space and
  the stylesheet names every property.

## 2. Gating a target on `ig.networkprohibited`

`2-network-gate/`: one target has `unless="ig.networkprohibited"`, the other
`unless="${ig.networkprohibited}"`. The publisher always sets the property, to `true` or `false`.

```text
-Dig.networkprohibited=true:
-Dig.networkprohibited=false:
     [echo] byValue RAN
```

- `unless="ig.networkprohibited"` tests whether the property is *set*, so the target never runs, even
  when the network is allowed.
- `unless="${ig.networkprohibited}"` tests the value: it runs when the value is `false` and is skipped
  when it is `true`. Use this form.

## 3. A relative stylesheet path

`3-relative-style/`: the project's basedir stands for the IG root, as the publisher sets it. One `<xslt>`
names `style="scripts/check.xslt"`; another names `style="${ig.scripts}/check.xslt"`.

```text
[echo] style=scripts/check.xslt: IG-supplied stylesheet ran
[echo] style=${ig.scripts}/check.xslt: template stylesheet ran
```

A relative `style` (and any other relative path in an Ant task) resolves against the basedir, which is
the IG's root folder, not the template. The IG then decides which stylesheet runs. Start every path
with `${ig.scripts}` (or `${ig.template}`).

## 4. A pre-process stylesheet

`4-preprocess-xslt/Probe.java` runs a stylesheet the way the publisher runs a pre-process `transform`:
from bytes (so there is no base URI), with the external DTD and stylesheet access attributes set to `""`.

```text
single.xslt -> single-file stylesheet ran
include.xslt -> TransformerConfigurationException: line 2: Could not read stylesheet target 'single.xslt', because 'file' access is not allowed due to restriction set by the accessExternalStylesheet property.
document.xslt -> TransformerException: Could not read stylesheet target '', because 'file' access is not allowed due to restriction set by the accessExternalStylesheet property.
```

- `xsl:include` and `xsl:import` fail, so a pre-process stylesheet has to be a single file. That is
  stricter than rule 3, which applies to the stylesheets your Ant scripts run.
- `document()` fails, so a pre-process stylesheet can't read other files.
