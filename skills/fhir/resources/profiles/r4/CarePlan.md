# CarePlan

**ID** `CarePlan` | **URL** `http://hl7.org/fhir/StructureDefinition/CarePlan` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Patient Care) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Describes the intention of how one or more practitioners intend to deliver care for a particular patient, group or community for a period of time, possibly limited to care for a specific condition or set of conditions.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CarePlan` | 0..* | `CarePlan` |  |  | Healthcare plan for patient or group |
| `CarePlan.identifier` | 0..* | `Identifier` | summary |  | External Ids for this plan |
| `CarePlan.instantiatesCanonical` | 0..* | `canonical(PlanDefinition \| Questionnaire \| Measure \| ActivityDefinition \| OperationDefinition)` | summary |  | Instantiates FHIR protocol or definition |
| `CarePlan.instantiatesUri` | 0..* | `uri` | summary |  | Instantiates external protocol or definition |
| `CarePlan.basedOn` | 0..* | `Reference(CarePlan)` | summary |  | Fulfills CarePlan |
| `CarePlan.replaces` | 0..* | `Reference(CarePlan)` | summary |  | CarePlan replaced by this CarePlan |
| `CarePlan.partOf` | 0..* | `Reference(CarePlan)` | summary |  | Part of referenced CarePlan |
| `CarePlan.status` | 1..1 | `code` | modifier summary | required→request-status@4.0.1 | draft \| active \| on-hold \| revoked \| completed \| entered-in-error \| unknown |
| `CarePlan.intent` | 1..1 | `code` | modifier summary | required→care-plan-intent@4.0.1 | proposal \| plan \| order \| option |
| `CarePlan.category` | 0..* | `CodeableConcept` | summary | example→care-plan-category | Type of plan |
| `CarePlan.title` | 0..1 | `string` | summary |  | Human-friendly name for the care plan |
| `CarePlan.description` | 0..1 | `string` | summary |  | Summary of nature of plan |
| `CarePlan.subject` | 1..1 | `Reference(Patient \| Group)` | summary |  | Who the care plan is for |
| `CarePlan.encounter` | 0..1 | `Reference(Encounter)` | summary |  | Encounter created as part of |
| `CarePlan.period` | 0..1 | `Period` | summary |  | Time period plan covers |
| `CarePlan.created` | 0..1 | `dateTime` | summary |  | Date record was first recorded |
| `CarePlan.author` | 0..1 | `Reference(Patient \| Practitioner \| PractitionerRole \| Device \| RelatedPerson \| Organization \| CareTeam)` | summary |  | Who is the designated responsible party |
| `CarePlan.contributor` | 0..* | `Reference(Patient \| Practitioner \| PractitionerRole \| Device \| RelatedPerson \| Organization \| CareTeam)` |  |  | Who provided the content of the care plan |
| `CarePlan.careTeam` | 0..* | `Reference(CareTeam)` |  |  | Who's involved in plan? |
| `CarePlan.addresses` | 0..* | `Reference(Condition)` | summary |  | Health issues this plan addresses |
| `CarePlan.supportingInfo` | 0..* | `Reference(Resource)` |  |  | Information considered as part of plan |
| `CarePlan.goal` | 0..* | `Reference(Goal)` |  |  | Desired outcome of plan |
| `CarePlan.activity` | 0..* | `BackboneElement` |  |  | Action to occur as part of plan |
| `CarePlan.activity.outcomeCodeableConcept` | 0..* | `CodeableConcept` |  | example→care-plan-activity-outcome | Results of the activity |
| `CarePlan.activity.outcomeReference` | 0..* | `Reference(Resource)` |  |  | Appointment, Encounter, Procedure, etc. |
| `CarePlan.activity.progress` | 0..* | `Annotation` |  |  | Comments about the activity status/progress |
| `CarePlan.activity.reference` | 0..1 | `Reference(Appointment \| CommunicationRequest \| DeviceRequest \| MedicationRequest \| NutritionOrder \| Task \| ServiceRequest \| VisionPrescription \| RequestGroup)` |  |  | Activity details defined in specific resource |
| `CarePlan.activity.detail` | 0..1 | `BackboneElement` |  |  | In-line definition of activity |
| `CarePlan.activity.detail.kind` | 0..1 | `code` |  | required→care-plan-activity-kind@4.0.1 | Appointment \| CommunicationRequest \| DeviceRequest \| MedicationRequest \| NutritionOrder \| Task \| ServiceRequest \| VisionPrescription |
| `CarePlan.activity.detail.instantiatesCanonical` | 0..* | `canonical(PlanDefinition \| ActivityDefinition \| Questionnaire \| Measure \| OperationDefinition)` |  |  | Instantiates FHIR protocol or definition |
| `CarePlan.activity.detail.instantiatesUri` | 0..* | `uri` |  |  | Instantiates external protocol or definition |
| `CarePlan.activity.detail.code` | 0..1 | `CodeableConcept` |  | example→procedure-code | Detail type of activity |
| `CarePlan.activity.detail.reasonCode` | 0..* | `CodeableConcept` |  | example→clinical-findings | Why activity should be done or why activity was prohibited |
| `CarePlan.activity.detail.reasonReference` | 0..* | `Reference(Condition \| Observation \| DiagnosticReport \| DocumentReference)` |  |  | Why activity is needed |
| `CarePlan.activity.detail.goal` | 0..* | `Reference(Goal)` |  |  | Goals this activity relates to |
| `CarePlan.activity.detail.status` | 1..1 | `code` | modifier | required→care-plan-activity-status@4.0.1 | not-started \| scheduled \| in-progress \| on-hold \| completed \| cancelled \| stopped \| unknown \| entered-in-error |
| `CarePlan.activity.detail.statusReason` | 0..1 | `CodeableConcept` |  |  | Reason for current status |
| `CarePlan.activity.detail.doNotPerform` | 0..1 | `boolean` | modifier |  | If true, activity is prohibiting action |
| `CarePlan.activity.detail.scheduled[x]` | 0..1 | `Timing, Period, string` |  |  | When activity is to occur |
| `CarePlan.activity.detail.location` | 0..1 | `Reference(Location)` |  |  | Where it should happen |
| `CarePlan.activity.detail.performer` | 0..* | `Reference(Practitioner \| PractitionerRole \| Organization \| RelatedPerson \| Patient \| CareTeam \| HealthcareService \| Device)` |  |  | Who will be responsible? |
| `CarePlan.activity.detail.product[x]` | 0..1 | `CodeableConcept, Reference(Medication \| Substance)` |  | example→medication-codes | What is to be administered/supplied |
| `CarePlan.activity.detail.dailyAmount` | 0..1 | `Quantity(SimpleQuantity)` |  |  | How to consume/day? |
| `CarePlan.activity.detail.quantity` | 0..1 | `Quantity(SimpleQuantity)` |  |  | How much to administer/supply/consume |
| `CarePlan.activity.detail.description` | 0..1 | `string` |  |  | Extra info describing activity to perform |
| `CarePlan.note` | 0..* | `Annotation` |  |  | Comments about the plan |

Elements defined in ancestors: `CarePlan.id`, `CarePlan.meta`, `CarePlan.implicitRules`, `CarePlan.language`, `CarePlan.text`, `CarePlan.contained`, `CarePlan.extension`, `CarePlan.modifierExtension`, `CarePlan.activity.id`, `CarePlan.activity.extension`, `CarePlan.activity.modifierExtension`, `CarePlan.activity.detail.id`, `CarePlan.activity.detail.extension`, `CarePlan.activity.detail.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `CarePlan.activity` | `cpl-3` | error | Provide a reference or detail, not both | `detail.empty() or reference.empty()` |
