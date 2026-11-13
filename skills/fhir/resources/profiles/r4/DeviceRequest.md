# DeviceRequest

**ID** `DeviceRequest` | **URL** `http://hl7.org/fhir/StructureDefinition/DeviceRequest` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Orders and Observations) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Represents a request for a patient to employ a medical device. The device may be an implantable device, or an external assistive device, such as a walker.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DeviceRequest` | 0..* | `DeviceRequest` |  |  | Medical device request |
| `DeviceRequest.identifier` | 0..* | `Identifier` | summary |  | External Request identifier |
| `DeviceRequest.instantiatesCanonical` | 0..* | `canonical(ActivityDefinition \| PlanDefinition)` | summary |  | Instantiates FHIR protocol or definition |
| `DeviceRequest.instantiatesUri` | 0..* | `uri` | summary |  | Instantiates external protocol or definition |
| `DeviceRequest.basedOn` | 0..* | `Reference(Resource)` | summary |  | What request fulfills |
| `DeviceRequest.priorRequest` | 0..* | `Reference(Resource)` | summary |  | What request replaces |
| `DeviceRequest.groupIdentifier` | 0..1 | `Identifier` | summary |  | Identifier of composite request |
| `DeviceRequest.status` | 0..1 | `code` | modifier summary | required→request-status@4.0.1 | draft \| active \| on-hold \| revoked \| completed \| entered-in-error \| unknown |
| `DeviceRequest.intent` | 1..1 | `code` | modifier summary | required→request-intent@4.0.1 | proposal \| plan \| directive \| order \| original-order \| reflex-order \| filler-order \| instance-order \| option |
| `DeviceRequest.priority` | 0..1 | `code` | summary | required→request-priority@4.0.1 | routine \| urgent \| asap \| stat |
| `DeviceRequest.code[x]` | 1..1 | `Reference(Device), CodeableConcept` | summary | example→device-kind | Device requested |
| `DeviceRequest.parameter` | 0..* | `BackboneElement` |  |  | Device details |
| `DeviceRequest.parameter.code` | 0..1 | `CodeableConcept` |  | A code that identifies the device detail. | Device detail |
| `DeviceRequest.parameter.value[x]` | 0..1 | `CodeableConcept, Quantity, Range, boolean` |  |  | Value of detail |
| `DeviceRequest.subject` | 1..1 | `Reference(Patient \| Group \| Location \| Device)` | summary |  | Focus of request |
| `DeviceRequest.encounter` | 0..1 | `Reference(Encounter)` | summary |  | Encounter motivating request |
| `DeviceRequest.occurrence[x]` | 0..1 | `dateTime, Period, Timing` | summary |  | Desired time or schedule for use |
| `DeviceRequest.authoredOn` | 0..1 | `dateTime` | summary |  | When recorded |
| `DeviceRequest.requester` | 0..1 | `Reference(Device \| Practitioner \| PractitionerRole \| Organization)` | summary |  | Who/what is requesting diagnostics |
| `DeviceRequest.performerType` | 0..1 | `CodeableConcept` | summary | example→participant-role | Filler role |
| `DeviceRequest.performer` | 0..1 | `Reference(Practitioner \| PractitionerRole \| Organization \| CareTeam \| HealthcareService \| Patient \| Device \| RelatedPerson)` | summary |  | Requested Filler |
| `DeviceRequest.reasonCode` | 0..* | `CodeableConcept` | summary | example→condition-code | Coded Reason for request |
| `DeviceRequest.reasonReference` | 0..* | `Reference(Condition \| Observation \| DiagnosticReport \| DocumentReference)` | summary |  | Linked Reason for request |
| `DeviceRequest.insurance` | 0..* | `Reference(Coverage \| ClaimResponse)` |  |  | Associated insurance coverage |
| `DeviceRequest.supportingInfo` | 0..* | `Reference(Resource)` |  |  | Additional clinical information |
| `DeviceRequest.note` | 0..* | `Annotation` |  |  | Notes or comments |
| `DeviceRequest.relevantHistory` | 0..* | `Reference(Provenance)` |  |  | Request provenance |

Elements defined in ancestors: `DeviceRequest.id`, `DeviceRequest.meta`, `DeviceRequest.implicitRules`, `DeviceRequest.language`, `DeviceRequest.text`, `DeviceRequest.contained`, `DeviceRequest.extension`, `DeviceRequest.modifierExtension`, `DeviceRequest.parameter.id`, `DeviceRequest.parameter.extension`, `DeviceRequest.parameter.modifierExtension`

## Invariants

_No profile-specific invariants._
