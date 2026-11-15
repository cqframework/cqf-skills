import ca.uhn.fhir.context.FhirContext;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import org.hl7.fhir.instance.model.api.IBaseResource;
import org.hl7.fhir.r4.model.IdType;
import org.hl7.fhir.r4.model.Parameters.ParametersParameterComponent;
import org.hl7.fhir.r4.model.Reference;
import org.hl7.fhir.r4.model.StringType;
import org.hl7.fhir.r4.model.StructureDefinition;
import org.opencds.cqf.fhir.cr.questionnaire.QuestionnaireProcessor;
import org.opencds.cqf.fhir.cr.questionnaireresponse.QuestionnaireResponseProcessor;
import org.opencds.cqf.fhir.utility.monad.Eithers;
import org.opencds.cqf.fhir.utility.repository.ig.IgRepository;

/**
 * Run the SDC operations with clinical-reasoning against a folder in IG layout (input/resources,
 * input/tests, input/vocabulary).
 * Usage: Sdc ROOT populate QUESTIONNAIRE-ID SUBJECT [NAME=Type/id ...]
 *        Sdc ROOT extract QUESTIONNAIRERESPONSE-ID
 *        Sdc ROOT generate STRUCTUREDEFINITION-ID
 * Prints the result as JSON, or the exception if the operation throws.
 */
public class Sdc {
    public static void main(String[] a) throws Exception {
        FhirContext ctx = FhirContext.forR4Cached();
        ctx.setValidationSupport(new ca.uhn.fhir.context.support.DefaultProfileValidationSupport(ctx));
        IgRepository repo = new IgRepository(ctx, Path.of(a[0]));
        String mode = a[1], id = a[2];
        IBaseResource out;
        try {
            switch (mode) {
                case "populate" -> {
                    // each NAME=Type/id becomes a $populate `context` parameter: part `name` (string)
                    // and part `content` (Reference), as SDC defines it
                    List<ParametersParameterComponent> context = new ArrayList<>();
                    for (int i = 4; i < a.length; i++) {
                        String[] nv = a[i].split("=", 2);
                        var p = new ParametersParameterComponent().setName("context");
                        p.addPart().setName("name").setValue(new StringType(nv[0]));
                        p.addPart().setName("content").setValue(new Reference(nv[1]));
                        context.add(p);
                    }
                    out = new QuestionnaireProcessor(repo).populate(
                            Eithers.forMiddle3(new IdType("Questionnaire", id)), a[3], context,
                            null, true, (IBaseResource) null, (IBaseResource) null, (IBaseResource) null);
                }
                case "extract" -> out = new QuestionnaireResponseProcessor(repo).extract(
                        Eithers.forLeft(new IdType("QuestionnaireResponse", id)));
                case "generate" -> out = new QuestionnaireProcessor(repo).generateQuestionnaire(
                        repo.read(StructureDefinition.class, new IdType("StructureDefinition", id)),
                        List.<StringType>of(), false, false);
                default -> throw new IllegalArgumentException(mode);
            }
        } catch (Exception e) {
            System.out.println("THROWS " + e.getClass().getSimpleName() + ": " + e.getMessage());
            return;
        }
        var json = ctx.newJsonParser().setPrettyPrint(true);
        try {
            System.out.println(json.encodeResourceToString(out));
        } catch (ca.uhn.fhir.parser.DataFormatException e) {
            // the result holds a value its element doesn't allow (e.g. Observation.valueDecimal in R4):
            // report it, then print the Bundle entries that can be encoded
            System.out.println("INVALID " + e.getMessage());
            if (out instanceof org.hl7.fhir.r4.model.Bundle b) {
                for (var entry : b.getEntry()) {
                    try {
                        System.out.println(json.encodeResourceToString(entry.getResource()));
                    } catch (ca.uhn.fhir.parser.DataFormatException e2) {
                        System.out.println("INVALID " + entry.getResource().fhirType() + "/"
                                + entry.getResource().getIdElement().getIdPart() + ": " + e2.getMessage());
                    }
                }
            }
        }
    }
}
