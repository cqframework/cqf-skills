# AdverseEvent

**ID** `AdverseEvent` | **URL** `http://hl7.org/fhir/StructureDefinition/AdverseEvent` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Patient Care) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Actual or potential/avoided event causing unintended physical injury resulting from or contributed to by medical care, a research study or other healthcare setting factors that requires additional monitoring, treatment, or hospitalization, or that results in death.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `AdverseEvent` | 0..* | `AdverseEvent` |  |  | Medical care, research study or other healthcare event causing physical injury |
| `AdverseEvent.identifier` | 0..1 | `Identifier` | summary |  | Business identifier for the event |
| `AdverseEvent.actuality` | 1..1 | `code` | modifier summary | required→adverse-event-actuality@4.0.1 | actual \| potential |
| `AdverseEvent.category` | 0..* | `CodeableConcept` | summary | extensible→adverse-event-category | product-problem \| product-quality \| product-use-error \| wrong-dose \| incorrect-prescribing-information \| wrong-technique \| wrong-route-of-administration \| wrong-rate \| wrong-duration \| wrong-time \| expired-drug \| medical-device-use-error \| problem-different-manufacturer \| unsafe-physical-environment |
| `AdverseEvent.event` | 0..1 | `CodeableConcept` | summary | example→adverse-event-type | Type of the event itself in relation to the subject |
| `AdverseEvent.subject` | 1..1 | `Reference(Patient \| Group \| Practitioner \| RelatedPerson)` | summary |  | Subject impacted by event |
| `AdverseEvent.encounter` | 0..1 | `Reference(Encounter)` | summary |  | Encounter created as part of |
| `AdverseEvent.date` | 0..1 | `dateTime` | summary |  | When the event occurred |
| `AdverseEvent.detected` | 0..1 | `dateTime` | summary |  | When the event was detected |
| `AdverseEvent.recordedDate` | 0..1 | `dateTime` | summary |  | When the event was recorded |
| `AdverseEvent.resultingCondition` | 0..* | `Reference(Condition)` | summary |  | Effect on the subject due to this event |
| `AdverseEvent.location` | 0..1 | `Reference(Location)` | summary |  | Location where adverse event occurred |
| `AdverseEvent.seriousness` | 0..1 | `CodeableConcept` | summary | example→adverse-event-seriousness | Seriousness of the event |
| `AdverseEvent.severity` | 0..1 | `CodeableConcept` | summary | required→adverse-event-severity@4.0.1 | mild \| moderate \| severe |
| `AdverseEvent.outcome` | 0..1 | `CodeableConcept` | summary | required→adverse-event-outcome@4.0.1 | resolved \| recovering \| ongoing \| resolvedWithSequelae \| fatal \| unknown |
| `AdverseEvent.recorder` | 0..1 | `Reference(Patient \| Practitioner \| PractitionerRole \| RelatedPerson)` | summary |  | Who recorded the adverse event |
| `AdverseEvent.contributor` | 0..* | `Reference(Practitioner \| PractitionerRole \| Device)` | summary |  | Who was involved in the adverse event or the potential adverse event |
| `AdverseEvent.suspectEntity` | 0..* | `BackboneElement` | summary |  | The suspected agent causing the adverse event |
| `AdverseEvent.suspectEntity.instance` | 1..1 | `Reference(Immunization \| Procedure \| Substance \| Medication \| MedicationAdministration \| MedicationStatement \| Device)` | summary |  | Refers to the specific entity that caused the adverse event |
| `AdverseEvent.suspectEntity.causality` | 0..* | `BackboneElement` | summary |  | Information on the possible cause of the event |
| `AdverseEvent.suspectEntity.causality.assessment` | 0..1 | `CodeableConcept` | summary | example→adverse-event-causality-assess | Assessment of if the entity caused the event |
| `AdverseEvent.suspectEntity.causality.productRelatedness` | 0..1 | `string` | summary |  | AdverseEvent.suspectEntity.causalityProductRelatedness |
| `AdverseEvent.suspectEntity.causality.author` | 0..1 | `Reference(Practitioner \| PractitionerRole)` | summary |  | AdverseEvent.suspectEntity.causalityAuthor |
| `AdverseEvent.suspectEntity.causality.method` | 0..1 | `CodeableConcept` | summary | example→adverse-event-causality-method | ProbabilityScale \| Bayesian \| Checklist |
| `AdverseEvent.subjectMedicalHistory` | 0..* | `Reference(Condition \| Observation \| AllergyIntolerance \| FamilyMemberHistory \| Immunization \| Procedure \| Media \| DocumentReference)` | summary |  |  |
| `AdverseEvent.referenceDocument` | 0..* | `Reference(DocumentReference)` | summary |  |  |
| `AdverseEvent.study` | 0..* | `Reference(ResearchStudy)` | summary |  |  |

Elements defined in ancestors: `AdverseEvent.id`, `AdverseEvent.meta`, `AdverseEvent.implicitRules`, `AdverseEvent.language`, `AdverseEvent.text`, `AdverseEvent.contained`, `AdverseEvent.extension`, `AdverseEvent.modifierExtension`, `AdverseEvent.suspectEntity.id`, `AdverseEvent.suspectEntity.extension`, `AdverseEvent.suspectEntity.modifierExtension`, `AdverseEvent.suspectEntity.causality.id`, `AdverseEvent.suspectEntity.causality.extension`, `AdverseEvent.suspectEntity.causality.modifierExtension`

## Invariants

_No profile-specific invariants._
