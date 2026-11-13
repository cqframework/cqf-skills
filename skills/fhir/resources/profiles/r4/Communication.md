# Communication

**ID** `Communication` | **URL** `http://hl7.org/fhir/StructureDefinition/Communication` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Patient Care) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

An occurrence of information being transmitted; e.g. an alert that was sent to a responsible provider, a public health agency that was notified about a reportable condition.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Communication` | 0..* | `Communication` |  |  | A record of information transmitted from a sender to a receiver |
| `Communication.identifier` | 0..* | `Identifier` | summary |  | Unique identifier |
| `Communication.instantiatesCanonical` | 0..* | `canonical(PlanDefinition \| ActivityDefinition \| Measure \| OperationDefinition \| Questionnaire)` | summary |  | Instantiates FHIR protocol or definition |
| `Communication.instantiatesUri` | 0..* | `uri` | summary |  | Instantiates external protocol or definition |
| `Communication.basedOn` | 0..* | `Reference(Resource)` | summary |  | Request fulfilled by this communication |
| `Communication.partOf` | 0..* | `Reference(Resource)` | summary |  | Part of this action |
| `Communication.inResponseTo` | 0..* | `Reference(Communication)` |  |  | Reply to |
| `Communication.status` | 1..1 | `code` | modifier summary | required→event-status@4.0.1 | preparation \| in-progress \| not-done \| on-hold \| stopped \| completed \| entered-in-error \| unknown |
| `Communication.statusReason` | 0..1 | `CodeableConcept` | summary | example→communication-not-done-reason | Reason for current status |
| `Communication.category` | 0..* | `CodeableConcept` |  | example→communication-category | Message category |
| `Communication.priority` | 0..1 | `code` | summary | required→request-priority@4.0.1 | routine \| urgent \| asap \| stat |
| `Communication.medium` | 0..* | `CodeableConcept` |  | example→v3-ParticipationMode | A channel of communication |
| `Communication.subject` | 0..1 | `Reference(Patient \| Group)` | summary |  | Focus of message |
| `Communication.topic` | 0..1 | `CodeableConcept` |  | example→communication-topic | Description of the purpose/content |
| `Communication.about` | 0..* | `Reference(Resource)` |  |  | Resources that pertain to this communication |
| `Communication.encounter` | 0..1 | `Reference(Encounter)` | summary |  | Encounter created as part of |
| `Communication.sent` | 0..1 | `dateTime` |  |  | When sent |
| `Communication.received` | 0..1 | `dateTime` |  |  | When received |
| `Communication.recipient` | 0..* | `Reference(Device \| Organization \| Patient \| Practitioner \| PractitionerRole \| RelatedPerson \| Group \| CareTeam \| HealthcareService)` |  |  | Message recipient |
| `Communication.sender` | 0..1 | `Reference(Device \| Organization \| Patient \| Practitioner \| PractitionerRole \| RelatedPerson \| HealthcareService)` |  |  | Message sender |
| `Communication.reasonCode` | 0..* | `CodeableConcept` | summary | example→clinical-findings | Indication for message |
| `Communication.reasonReference` | 0..* | `Reference(Condition \| Observation \| DiagnosticReport \| DocumentReference)` | summary |  | Why was communication done? |
| `Communication.payload` | 0..* | `BackboneElement` |  |  | Message payload |
| `Communication.payload.content[x]` | 1..1 | `string, Attachment, Reference(Resource)` |  |  | Message part content |
| `Communication.note` | 0..* | `Annotation` |  |  | Comments made about the communication |

Elements defined in ancestors: `Communication.id`, `Communication.meta`, `Communication.implicitRules`, `Communication.language`, `Communication.text`, `Communication.contained`, `Communication.extension`, `Communication.modifierExtension`, `Communication.payload.id`, `Communication.payload.extension`, `Communication.payload.modifierExtension`

## Invariants

_No profile-specific invariants._
