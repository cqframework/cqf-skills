# Procedure

**ID** `Procedure` | **URL** `http://hl7.org/fhir/StructureDefinition/Procedure` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Patient Care) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

An action that is or was performed on or for a patient. This can be a physical intervention like an operation, or less invasive like long term services, counseling, or hypnotherapy.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Procedure` | 0..* | `Procedure` |  |  | An action that is being or was performed on a patient |
| `Procedure.identifier` | 0..* | `Identifier` | summary |  | External Identifiers for this procedure |
| `Procedure.instantiatesCanonical` | 0..* | `canonical(PlanDefinition \| ActivityDefinition \| Measure \| OperationDefinition \| Questionnaire)` | summary |  | Instantiates FHIR protocol or definition |
| `Procedure.instantiatesUri` | 0..* | `uri` | summary |  | Instantiates external protocol or definition |
| `Procedure.basedOn` | 0..* | `Reference(CarePlan \| ServiceRequest)` | summary |  | A request for this procedure |
| `Procedure.partOf` | 0..* | `Reference(Procedure \| Observation \| MedicationAdministration)` | summary |  | Part of referenced event |
| `Procedure.status` | 1..1 | `code` | modifier summary | required→event-status@4.0.1 | preparation \| in-progress \| not-done \| on-hold \| stopped \| completed \| entered-in-error \| unknown |
| `Procedure.statusReason` | 0..1 | `CodeableConcept` | summary | example→procedure-not-performed-reason | Reason for current status |
| `Procedure.category` | 0..1 | `CodeableConcept` | summary | example→procedure-category | Classification of the procedure |
| `Procedure.code` | 0..1 | `CodeableConcept` | summary | example→procedure-code | Identification of the procedure |
| `Procedure.subject` | 1..1 | `Reference(Patient \| Group)` | summary |  | Who the procedure was performed on |
| `Procedure.encounter` | 0..1 | `Reference(Encounter)` | summary |  | Encounter created as part of |
| `Procedure.performed[x]` | 0..1 | `dateTime, Period, string, Age, Range` | summary |  | When the procedure was performed |
| `Procedure.recorder` | 0..1 | `Reference(Patient \| RelatedPerson \| Practitioner \| PractitionerRole)` | summary |  | Who recorded the procedure |
| `Procedure.asserter` | 0..1 | `Reference(Patient \| RelatedPerson \| Practitioner \| PractitionerRole)` | summary |  | Person who asserts this procedure |
| `Procedure.performer` | 0..* | `BackboneElement` | summary |  | The people who performed the procedure |
| `Procedure.performer.function` | 0..1 | `CodeableConcept` | summary | example→performer-role | Type of performance |
| `Procedure.performer.actor` | 1..1 | `Reference(Practitioner \| PractitionerRole \| Organization \| Patient \| RelatedPerson \| Device)` | summary |  | The reference to the practitioner |
| `Procedure.performer.onBehalfOf` | 0..1 | `Reference(Organization)` |  |  | Organization the device or practitioner was acting for |
| `Procedure.location` | 0..1 | `Reference(Location)` | summary |  | Where the procedure happened |
| `Procedure.reasonCode` | 0..* | `CodeableConcept` | summary | example→procedure-reason | Coded reason procedure performed |
| `Procedure.reasonReference` | 0..* | `Reference(Condition \| Observation \| Procedure \| DiagnosticReport \| DocumentReference)` | summary |  | The justification that the procedure was performed |
| `Procedure.bodySite` | 0..* | `CodeableConcept` | summary | example→body-site | Target body sites |
| `Procedure.outcome` | 0..1 | `CodeableConcept` | summary | example→procedure-outcome | The result of procedure |
| `Procedure.report` | 0..* | `Reference(DiagnosticReport \| DocumentReference \| Composition)` |  |  | Any report resulting from the procedure |
| `Procedure.complication` | 0..* | `CodeableConcept` |  | example→condition-code | Complication following the procedure |
| `Procedure.complicationDetail` | 0..* | `Reference(Condition)` |  |  | A condition that is a result of the procedure |
| `Procedure.followUp` | 0..* | `CodeableConcept` |  | example→procedure-followup | Instructions for follow up |
| `Procedure.note` | 0..* | `Annotation` |  |  | Additional information about the procedure |
| `Procedure.focalDevice` | 0..* | `BackboneElement` |  |  | Manipulated, implanted, or removed device |
| `Procedure.focalDevice.action` | 0..1 | `CodeableConcept` |  | preferred→device-action | Kind of change to device |
| `Procedure.focalDevice.manipulated` | 1..1 | `Reference(Device)` |  |  | Device that was changed |
| `Procedure.usedReference` | 0..* | `Reference(Device \| Medication \| Substance)` |  |  | Items used during procedure |
| `Procedure.usedCode` | 0..* | `CodeableConcept` |  | example→device-kind | Coded items used during the procedure |

Elements defined in ancestors: `Procedure.id`, `Procedure.meta`, `Procedure.implicitRules`, `Procedure.language`, `Procedure.text`, `Procedure.contained`, `Procedure.extension`, `Procedure.modifierExtension`, `Procedure.performer.id`, `Procedure.performer.extension`, `Procedure.performer.modifierExtension`, `Procedure.focalDevice.id`, `Procedure.focalDevice.extension`, `Procedure.focalDevice.modifierExtension`

## Invariants

_No profile-specific invariants._
