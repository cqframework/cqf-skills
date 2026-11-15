import java.nio.file.Files;
import java.util.*;
import kotlin.Unit;
import org.cqframework.cql.cql2elm.*;
import org.cqframework.cql.cql2elm.quick.FhirLibrarySourceProvider;
import org.hl7.elm.r1.*;
import org.opencds.cqf.cql.engine.data.CompositeDataProvider;
import org.opencds.cqf.cql.engine.data.DataProvider;
import org.opencds.cqf.cql.engine.execution.*;
import org.opencds.cqf.cql.engine.fhir.model.R4FhirModelResolver;

/** Translate each probe library, print its diagnostics, then evaluate every expression definition. */
public class Probe {
    public static void main(String[] args) throws Exception {
        java.nio.file.Path dir = java.nio.file.Path.of(args[0]);
        CqlCompilerOptions opts = CqlCompilerOptions.Companion.defaultOptions();
        for (int i = 1; i < args.length; i++) {
            String name = args[i];
            ModelManager mm = new ModelManager();
            LibraryManager lm = new LibraryManager(mm, opts);
            LibraryManager elm = new LibraryManager(new ModelManager(), opts);
            elm.getLibrarySourceLoader().registerProvider(new DefaultLibrarySourceProvider(kotlinx.io.files.PathsJvmKt.Path(dir.toString())));
            elm.getLibrarySourceLoader().registerProvider(new FhirLibrarySourceProvider());
            lm.getLibrarySourceLoader().registerProvider(new DefaultLibrarySourceProvider(kotlinx.io.files.PathsJvmKt.Path(dir.toString())));
            lm.getLibrarySourceLoader().registerProvider(new FhirLibrarySourceProvider());
            String text = Files.readString(dir.resolve(name + ".cql"));
            System.out.println("=== " + name);
            CqlTranslator t = CqlTranslator.fromText(text, lm);
            for (CqlCompilerException e : t.getExceptions()) {
                String where = e.getLocator() == null ? "" : " (line " + e.getLocator().getStartLine() + ")";
                System.out.println("  " + e.getSeverity() + where + ": " + e.getMessage());
            }
            if (!t.getErrors().isEmpty()) continue;
            java.util.List<String> exprs = new ArrayList<>();
            Library lib = t.getTranslatedLibrary().getLibrary();
            if (lib.getStatements() != null) {
                for (ExpressionDef d : lib.getStatements().getDef()) {
                    if (!(d instanceof FunctionDef) && !"Patient".equals(d.getName())) exprs.add(d.getName());
                }
            }
            if (exprs.isEmpty()) continue;
            // compile once more through the manager so the engine can load it
            // the engine loads (and sorts) the library itself through the manager
            Map<String, DataProvider> providers = new HashMap<>();
            providers.put("http://hl7.org/fhir", new CompositeDataProvider(new R4FhirModelResolver(), null));
            CqlEngine engine = new CqlEngine(new Environment(elm, providers, null));
            for (String ex : exprs) {
                try {
                    EvaluationParams.LibraryParams.Builder lb = new EvaluationParams.LibraryParams.Builder();
                    lb.expressions(ex);
                    EvaluationParams.Builder b = new EvaluationParams.Builder();
                    b.library(lib.getIdentifier(), lb.build());
                    EvaluationResults rs = engine.evaluate(b.build());
                    if (rs.hasExceptions()) {
                        Throwable th = rs.getExceptions().values().iterator().next();
                        StringBuilder sb = new StringBuilder();
                        while (th != null) { sb.append(" | ").append(th.getClass().getSimpleName()).append(": ").append(th.getMessage()); th = th.getCause(); }
                        System.out.println("  " + ex + " => ERROR" + sb);
                        continue;
                    }
                    ExpressionResult r = rs.getOnlyResultOrThrow().get(ex);
                    System.out.println("  " + ex + " = " + (r == null || r.getValue() == null ? "null" : r.getValue().toString()));
                } catch (Exception e) {
                    System.out.println("  " + ex + " => ERROR " + e.getClass().getSimpleName() + ": " + e.getMessage());
                }
            }
        }
    }
}
