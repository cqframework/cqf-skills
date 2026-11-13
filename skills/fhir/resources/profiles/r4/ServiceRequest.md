# ServiceRequest

**ID** `ServiceRequest` | **URL** `http://hl7.org/fhir/StructureDefinition/ServiceRequest` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Orders and Observations) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

A record of a request for service such as diagnostic investigations, treatments, or operations to be performed.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ServiceRequest` | 0..* | `ServiceRequest` |  |  | A request for a service to be performed |
| `ServiceRequest.identifier` | 0..* | `Identifier` | summary |  | Identifiers assigned to this order |
| `ServiceRequest.instantiatesCanonical` | 0..* | `canonical(ActivityDefinition \| PlanDefinition)` | summary |  | Instantiates FHIR protocol or definition |
| `ServiceRequest.instantiatesUri` | 0..* | `uri` | summary |  | Instantiates external protocol or definition |
| `ServiceRequest.basedOn` | 0..* | `Reference(CarePlan \| ServiceRequest \| MedicationRequest)` | summary |  | What request fulfills |
| `ServiceRequest.replaces` | 0..* | `Reference(ServiceRequest)` | summary |  | What request replaces |
| `ServiceRequest.requisition` | 0..1 | `Identifier` | summary |  | Composite Request ID |
| `ServiceRequest.status` | 1..1 | `code` | modifier summary | required→request-status@4.0.1 | draft \| active \| on-hold \| revoked \| completed \| entered-in-error \| unknown |
| `ServiceRequest.intent` | 1..1 | `code` | modifier summary | required→request-intent@4.0.1 | proposal \| plan \| directive \| order \| original-order \| reflex-order \| filler-order \| instance-order \| option |
| `ServiceRequest.category` | 0..* | `CodeableConcept` | summary | example→servicerequest-category | Classification of service |
| `ServiceRequest.priority` | 0..1 | `code` | summary | required→request-priority@4.0.1 | routine \| urgent \| asap \| stat |
| `ServiceRequest.doNotPerform` | 0..1 | `boolean` | modifier summary |  | True if service/procedure should not be performed |
| `ServiceRequest.code` | 0..1 | `CodeableConcept` | summary | example→procedure-code | What is being requested/ordered |
| `ServiceRequest.orderDetail` | 0..* | `CodeableConcept` | summary | example→servicerequest-orderdetail | Additional order information |
| `ServiceRequest.quantity[x]` | 0..1 | `Quantity, Ratio, Range` | summary |  | Service amount |
| `ServiceRequest.subject` | 1..1 | `Reference(Patient \| Group \| Location \| Device)` | summary |  | Individual or Entity the service is ordered for |
| `ServiceRequest.encounter` | 0..1 | `Reference(Encounter)` | summary |  | Encounter in which the request was created |
| `ServiceRequest.occurrence[x]` | 0..1 | `dateTime, Period, Timing` | summary |  | When service should occur |
| `ServiceRequest.asNeeded[x]` | 0..1 | `boolean, CodeableConcept` | summary | example→medication-as-needed-reason | Preconditions for service |
| `ServiceRequest.authoredOn` | 0..1 | `dateTime` | summary |  | Date request signed |
| `ServiceRequest.requester` | 0..1 | `Reference(Practitioner \| PractitionerRole \| Organization \| Patient \| RelatedPerson \| Device)` | summary |  | Who/what is requesting service |
| `ServiceRequest.performerType` | 0..1 | `CodeableConcept` | summary | example→participant-role | Performer role |
| `ServiceRequest.performer` | 0..* | `Reference(Practitioner \| PractitionerRole \| Organization \| CareTeam \| HealthcareService \| Patient \| Device \| RelatedPerson)` | summary |  | Requested performer |
| `ServiceRequest.locationCode` | 0..* | `CodeableConcept` | summary | example→v3-ServiceDeliveryLocationRoleType | Requested location |
| `ServiceRequest.locationReference` | 0..* | `Reference(Location)` | summary |  | Requested location |
| `ServiceRequest.reasonCode` | 0..* | `CodeableConcept` | summary | example→procedure-reason | Explanation/Justification for procedure or service |
| `ServiceRequest.reasonReference` | 0..* | `Reference(Condition \| Observation \| DiagnosticReport \| DocumentReference)` | summary |  | Explanation/Justification for service or service |
| `ServiceRequest.insurance` | 0..* | `Reference(Coverage \| ClaimResponse)` |  |  | Associated insurance coverage |
| `ServiceRequest.supportingInfo` | 0..* | `Reference(Resource)` |  |  | Additional clinical information |
| `ServiceRequest.specimen` | 0..* | `Reference(Specimen)` | summary |  | Procedure Samples |
| `ServiceRequest.bodySite` | 0..* | `CodeableConcept` | summary | example→body-site | Location on Body |
| `ServiceRequest.note` | 0..* | `Annotation` |  |  | Comments |
| `ServiceRequest.patientInstruction` | 0..1 | `string` | summary |  | Patient or consumer-oriented instructions |
| `ServiceRequest.relevantHistory` | 0..* | `Reference(Provenance)` |  |  | Request provenance |

Elements defined in ancestors: `ServiceRequest.id`, `ServiceRequest.meta`, `ServiceRequest.implicitRules`, `ServiceRequest.language`, `ServiceRequest.text`, `ServiceRequest.contained`, `ServiceRequest.extension`, `ServiceRequest.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `ServiceRequest` | `prr-1` | error | orderDetail SHALL only be present if code is present | `orderDetail.empty() or code.exists()` |
