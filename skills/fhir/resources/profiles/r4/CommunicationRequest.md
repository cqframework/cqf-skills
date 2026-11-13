# CommunicationRequest

**ID** `CommunicationRequest` | **URL** `http://hl7.org/fhir/StructureDefinition/CommunicationRequest` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Patient Care) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

A request to convey information; e.g. the CDS system proposes that an alert be sent to a responsible provider, the CDS system proposes that the public health agency be notified about a reportable condition.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CommunicationRequest` | 0..* | `CommunicationRequest` |  |  | A request for information to be sent to a receiver |
| `CommunicationRequest.identifier` | 0..* | `Identifier` | summary |  | Unique identifier |
| `CommunicationRequest.basedOn` | 0..* | `Reference(Resource)` | summary |  | Fulfills plan or proposal |
| `CommunicationRequest.replaces` | 0..* | `Reference(CommunicationRequest)` | summary |  | Request(s) replaced by this request |
| `CommunicationRequest.groupIdentifier` | 0..1 | `Identifier` | summary |  | Composite request this is part of |
| `CommunicationRequest.status` | 1..1 | `code` | modifier summary | required→request-status@4.0.1 | draft \| active \| on-hold \| revoked \| completed \| entered-in-error \| unknown |
| `CommunicationRequest.statusReason` | 0..1 | `CodeableConcept` |  | Codes identifying the reason for the current state of a request. | Reason for current status |
| `CommunicationRequest.category` | 0..* | `CodeableConcept` |  | example→communication-category | Message category |
| `CommunicationRequest.priority` | 0..1 | `code` | summary | required→request-priority@4.0.1 | routine \| urgent \| asap \| stat |
| `CommunicationRequest.doNotPerform` | 0..1 | `boolean` | modifier summary |  | True if request is prohibiting action |
| `CommunicationRequest.medium` | 0..* | `CodeableConcept` |  | example→v3-ParticipationMode | A channel of communication |
| `CommunicationRequest.subject` | 0..1 | `Reference(Patient \| Group)` |  |  | Focus of message |
| `CommunicationRequest.about` | 0..* | `Reference(Resource)` |  |  | Resources that pertain to this communication request |
| `CommunicationRequest.encounter` | 0..1 | `Reference(Encounter)` | summary |  | Encounter created as part of |
| `CommunicationRequest.payload` | 0..* | `BackboneElement` |  |  | Message payload |
| `CommunicationRequest.payload.content[x]` | 1..1 | `string, Attachment, Reference(Resource)` |  |  | Message part content |
| `CommunicationRequest.occurrence[x]` | 0..1 | `dateTime, Period` | summary |  | When scheduled |
| `CommunicationRequest.authoredOn` | 0..1 | `dateTime` | summary |  | When request transitioned to being actionable |
| `CommunicationRequest.requester` | 0..1 | `Reference(Practitioner \| PractitionerRole \| Organization \| Patient \| RelatedPerson \| Device)` | summary |  | Who/what is requesting service |
| `CommunicationRequest.recipient` | 0..* | `Reference(Device \| Organization \| Patient \| Practitioner \| PractitionerRole \| RelatedPerson \| Group \| CareTeam \| HealthcareService)` |  |  | Message recipient |
| `CommunicationRequest.sender` | 0..1 | `Reference(Device \| Organization \| Patient \| Practitioner \| PractitionerRole \| RelatedPerson \| HealthcareService)` | summary |  | Message sender |
| `CommunicationRequest.reasonCode` | 0..* | `CodeableConcept` | summary | example→v3-ActReason | Why is communication needed? |
| `CommunicationRequest.reasonReference` | 0..* | `Reference(Condition \| Observation \| DiagnosticReport \| DocumentReference)` | summary |  | Why is communication needed? |
| `CommunicationRequest.note` | 0..* | `Annotation` |  |  | Comments made about communication request |

Elements defined in ancestors: `CommunicationRequest.id`, `CommunicationRequest.meta`, `CommunicationRequest.implicitRules`, `CommunicationRequest.language`, `CommunicationRequest.text`, `CommunicationRequest.contained`, `CommunicationRequest.extension`, `CommunicationRequest.modifierExtension`, `CommunicationRequest.payload.id`, `CommunicationRequest.payload.extension`, `CommunicationRequest.payload.modifierExtension`

## Invariants

_No profile-specific invariants._
