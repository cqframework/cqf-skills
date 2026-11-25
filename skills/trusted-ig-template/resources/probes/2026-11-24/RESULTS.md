# Probes, 2026-11-24

IG Publisher 3.0.5 runs pre-process transforms with Saxon only, and refuses `xsl:result-document`. This
re-runs the pre-process probe of [2026-11-17](../2026-11-17/RESULTS.md) (§4) the way 3.0.5 does, with
two more stylesheets. Probes §1 to §3 of 2026-11-17 are about Ant 1.10.18, which 3.0.5 still uses; they
weren't re-run.

- Saxon-HE 13.0, the version org.hl7.fhir.core 7.0.6 brings, with xmlresolver 6.0.23, on OpenJDK 21.0.9.
- `4-preprocess-xslt/Probe.java` does what `XSLTransformer.transform` does at 3.0.5: the factory from
  `XMLUtil.newXXEProtectedTransformerFactory()` (external DTD and stylesheet access set to `""`), the
  stylesheet and source as bytes, and a result-document handler that refuses any secondary output.

Run it in a copy of the folder:

```text
java -cp "Saxon-HE-13.0.jar;xmlresolver-6.0.23.jar" Probe.java single.xslt include.xslt document.xslt result-document.xslt java-call.xslt
```

## 4. A pre-process stylesheet, on Saxon

```text
factory: net.sf.saxon.TransformerFactoryImpl
single.xslt -> single-file stylesheet ran
include.xslt -> TransformerConfigurationException: … Access to URI file:/…/single.xslt has been prohibited
document.xslt -> XPathException: Access to URI file:/…/single.xslt has been prohibited
result-document.xslt -> XPathException: … xsl:result-document is not allowed in this transform (it tried to write to file:/…/side-output.txt)
java-call.xslt -> TransformerConfigurationException: … Errors were reported during stylesheet compilation
                  (XPST0017: … Reflexive calls to Java methods are not available under Saxon-HE)
```

- `xsl:include`, `xsl:import` and `document()` still fail: a pre-process stylesheet must be one
  self-contained file, and can't read files.
- `xsl:result-document` stops the transform, and no `side-output.txt` was written. The transform
  produces its main output and nothing else.
- Saxon-HE doesn't run Java extension functions at all: the stylesheet doesn't compile.
- Saxon runs XSLT 2.0 and 3.0, so from 3.0.5 a pre-process stylesheet may use them.
