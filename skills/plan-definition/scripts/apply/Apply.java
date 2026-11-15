import ca.uhn.fhir.context.FhirContext;
import java.nio.file.Path;
import java.util.List;
import org.hl7.fhir.instance.model.api.IBaseResource;
import org.hl7.fhir.r4.model.IdType;
import org.opencds.cqf.fhir.cr.activitydefinition.ActivityDefinitionProcessor;
import org.opencds.cqf.fhir.cr.plandefinition.PlanDefinitionProcessor;
import org.opencds.cqf.fhir.utility.monad.Eithers;
import org.opencds.cqf.fhir.utility.repository.ig.IgRepository;

/**
 * Run $apply with clinical-reasoning against a folder in IG layout (input/resources, input/tests, input/vocabulary).
 * Usage: Apply ROOT plan|r5|activity ID SUBJECT
 * Prints the result as JSON, or the exception if the operation throws.
 */
public class Apply {
    public static void main(String[] a) throws Exception {
        FhirContext ctx = FhirContext.forR4Cached();
        ctx.setValidationSupport(new ca.uhn.fhir.context.support.DefaultProfileValidationSupport(ctx));
        IgRepository repo = new IgRepository(ctx, Path.of(a[0]));
        String mode = a[1], id = a[2], subject = a[3];
        IBaseResource out;
        try {
            switch (mode) {
                case "plan" -> out = new PlanDefinitionProcessor(repo).apply(
                        Eithers.forMiddle3(new IdType("PlanDefinition", id)), subject,
                        null, null, null, null, null, null, null, null);
                case "r5" -> out = new PlanDefinitionProcessor(repo).applyR5(
                        Eithers.forMiddle3(new IdType("PlanDefinition", id)), List.of(subject),
                        null, null, null, null, null, null, null, null, null, true, null, null,
                        (IBaseResource) null, (IBaseResource) null, (IBaseResource) null);
                case "activity" -> out = new ActivityDefinitionProcessor(repo).apply(
                        Eithers.forMiddle3(new IdType("ActivityDefinition", id)), subject,
                        null, null, null, null, null, null, null, null);
                default -> throw new IllegalArgumentException(mode);
            }
        } catch (Exception e) {
            System.out.println("THROWS " + e.getClass().getSimpleName() + ": " + e.getMessage());
            return;
        }
        System.out.println(ctx.newJsonParser().setPrettyPrint(true).encodeResourceToString(out));
    }
}
