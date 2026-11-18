import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import javax.xml.XMLConstants;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.stream.StreamResult;
import javax.xml.transform.stream.StreamSource;

/**
 * Runs each stylesheet named on the command line the way the IG Publisher runs a pre-process
 * transform: XSLTransformer.transform(source, xslt) with XMLUtil.newXXEProtectedTransformerFactory(),
 * both given as bytes, so there is no base URI.
 *
 * Usage: java Probe.java single.xslt include.xslt document.xslt
 */
public class Probe {
  public static void main(String[] args) throws Exception {
    TransformerFactory f = TransformerFactory.newInstance();
    f.setAttribute(XMLConstants.ACCESS_EXTERNAL_DTD, "");
    f.setAttribute(XMLConstants.ACCESS_EXTERNAL_STYLESHEET, "");
    for (String x : args) {
      try {
        Transformer t = f.newTransformer(new StreamSource(new ByteArrayInputStream(Files.readAllBytes(Path.of(x)))));
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        t.transform(new StreamSource(new ByteArrayInputStream("<page/>".getBytes())), new StreamResult(out));
        System.out.println(x + " -> " + out.toString().trim());
      } catch (Exception e) {
        String m = String.valueOf(e.getMessage());
        int i = m.lastIndexOf("Exception: ");
        System.out.println(x + " -> " + e.getClass().getSimpleName() + ": " + (i < 0 ? m : m.substring(i + 11)).trim());
      }
    }
  }
}
