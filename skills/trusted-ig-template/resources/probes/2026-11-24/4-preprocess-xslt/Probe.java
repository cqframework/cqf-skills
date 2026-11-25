import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import javax.xml.XMLConstants;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.stream.StreamSource;
import net.sf.saxon.jaxp.TransformerImpl;
import net.sf.saxon.s9api.SaxonApiException;
import net.sf.saxon.s9api.SaxonApiUncheckedException;

/**
 * Runs each stylesheet named on the command line the way IG Publisher 3.0.5 runs a pre-process transform
 * (XSLTransformer.transform): the factory from XMLUtil.newXXEProtectedTransformerFactory() (core 7.0.6), which
 * with Saxon-HE on the classpath is Saxon's; the stylesheet and source given as bytes, so there is no base URI;
 * and a result-document handler that refuses any secondary output.
 *
 * Usage (Saxon-HE 13.0 and its xmlresolver on the classpath):
 *   java -cp "Saxon-HE-13.0.jar;xmlresolver-6.0.23.jar" Probe.java single.xslt include.xslt document.xslt ...
 */
public class Probe {
  public static void main(String[] args) throws Exception {
    TransformerFactory f = TransformerFactory.newInstance();
    f.setAttribute(XMLConstants.ACCESS_EXTERNAL_DTD, "");
    f.setAttribute(XMLConstants.ACCESS_EXTERNAL_STYLESHEET, "");
    System.out.println("factory: " + f.getClass().getName());
    for (String x : args) {
      try {
        Transformer t = f.newTransformer(new StreamSource(new ByteArrayInputStream(Files.readAllBytes(Path.of(x)))));
        ((TransformerImpl) t).getUnderlyingXsltTransformer().setResultDocumentHandler(uri -> {
          throw new SaxonApiUncheckedException(new SaxonApiException("xsl:result-document is not allowed in this transform (it tried to write to " + uri + ")"));
        });
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        t.transform(new StreamSource(new ByteArrayInputStream("<page/>".getBytes())), new StreamResult(out));
        System.out.println(x + " -> " + out.toString().trim());
      } catch (Throwable e) {
        String m = String.valueOf(e.getMessage()).replaceAll("\\s+", " ");
        System.out.println(x + " -> " + e.getClass().getSimpleName() + ": " + (m.length() > 200 ? m.substring(0, 200) + "…" : m));
      }
    }
  }
}
