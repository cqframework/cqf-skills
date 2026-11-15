import java.nio.file.Files;
import org.cqframework.cql.cql2elm.*;
import org.cqframework.cql.cql2elm.quick.FhirLibrarySourceProvider;
public class Elm {
    public static void main(String[] a) throws Exception {
        LibraryManager lm = new LibraryManager(new ModelManager(), CqlCompilerOptions.Companion.defaultOptions());
        lm.getLibrarySourceLoader().registerProvider(new DefaultLibrarySourceProvider(kotlinx.io.files.PathsJvmKt.Path(a[0])));
        lm.getLibrarySourceLoader().registerProvider(new FhirLibrarySourceProvider());
        CqlTranslator t = CqlTranslator.fromText(Files.readString(java.nio.file.Path.of(a[0], a[1] + ".cql")), lm);
        System.out.println(t.toXml());
    }
}
