# ActivityDefinition

Baseline: FHIR R4 (4.0.1), CPG 2.0.0 and clinical-reasoning 4.13.0. Untagged statements hold in R4.
Sources: FHIR-R4, CPG-2.0.0, CR-4.13.0, PROBES-2026-11-14

An ActivityDefinition is a template for one request (a ServiceRequest, MedicationRequest, Task…). A
PlanDefinition action points to it with `definitionCanonical`; applying it creates the request for a
subject.

## Elements

| Element | Notes |
| --- | --- |
| `kind` | The resource type to create: one of the 15 `request-resource-types` (Appointment, AppointmentResponse, CarePlan, Claim, CommunicationRequest, Contract, DeviceRequest, EnrollmentRequest, ImmunizationRecommendation, MedicationRequest, NutritionOrder, ServiceRequest, SupplyRequest, Task, VisionPrescription) [src: FHIR-R4 package/StructureDefinition-ActivityDefinition.json] |
| `profile` | The profile the created resource should conform to |
| `intent`, `priority`, `doNotPerform` | Copied onto the request |
| `code` | What to do |
| `subject[x]` | Defaults to Patient |
| `timing[x]`, `location`, `participant` | |
| `product[x]`, `quantity`, `dosage` | Medications and supplies |
| `bodySite`, `specimenRequirement`, `observationRequirement`, `observationResultRequirement` | |
| `library` | The logic its dynamicValues use |
| `transform` | A StructureMap applied to produce the request |
| `dynamicValue` | `path` and `expression`, both 1..1 here (on a PlanDefinition action they're 0..1) |

CPG's computable ActivityDefinition requires `kind` and allows at most one `library`
[src: CPG-2.0.0 package/StructureDefinition-cpg-computableactivity.json].

## Applying it: the specification

R4 describes `ActivityDefinition/$apply` [src: FHIR-R4 activitydefinition.html#12.17.3.3]:

1. Create a resource of the type given by `kind`.
2. Set its status to `draft`.
3. Copy the structural elements (code, timing, product, dosage…).
4. Resolve participant and location from the context.
5. Apply the `transform`, if any.
6. Apply the dynamicValues in order.

The operation returns that one resource, and "systems will likely vary widely in the degree of support"
[src: FHIR-R4 activitydefinition-operation-apply.html#12.17.9.1]. Applied from a PlanDefinition, the
request is an option the RequestGroup proposes: CPG says the referenced requests "will have an intent of
`option`" [src: CPG-2.0.0 documentation-approach-09-methods-of-implementation.html#plandefinition-processing-semantics].
CPG 2.0.0 added its own `ActivityDefinition/$apply`, with the same extra parameters as its PlanDefinition
one, returning a transient resource [src: CPG-2.0.0 changes.html#stu2-release-version-200].

## Applying it: clinical-reasoning 4.13.0

The reference implementation creates each kind with a resolver
[src: CR-4.13.0 cqf-fhir-cr/…/activitydefinition/apply/resolvers/R4ResolverFactory.java:36-95]:

- **The kind** comes from a `cpg-activity-kind` extension if there is one, otherwise `kind`.
- **ServiceRequest** gets status `active` and intent `order` unless `intent` is set, and `code` is
  required unless the definition has dynamicValues
  [src: CR-4.13.0 cqf-fhir-cr/…/resolvers/r4/ServiceRequestResolver.java:22-68]. So the result isn't
  `draft`, and isn't `option` when applied from a PlanDefinition, unlike the specification
  [src: PROBES-2026-11-14 RESULTS.md §5]. MedicationRequest and ImmunizationRecommendation likewise need
  their product unless there are dynamicValues.
- **CommunicationRequest** gets status `active` and its payload from `code.text`
  [src: PROBES-2026-11-14 RESULTS.md §1].
- **AppointmentResponse, CarePlan, Claim, Contract, DeviceRequest, EnrollmentRequest, NutritionOrder,
  RequestGroup and VisionPrescription** are created empty, without a subject: only dynamicValues fill
  them.
- A missing `kind` fails, and an unsupported one throws "Unsupported activity type".
- An ActivityDefinition's dynamicValues use its own `library`, not the PlanDefinition's
  [src: CR-4.13.0 cqf-fhir-cr/…/activitydefinition/apply/ApplyRequest.java:66-71]. Give the
  ActivityDefinition a `library` when its dynamicValues name expressions.
- `transform` isn't applied.

Set `intent` (and the status you want through a dynamicValue, if it matters) on the definition rather
than relying on the defaults.
