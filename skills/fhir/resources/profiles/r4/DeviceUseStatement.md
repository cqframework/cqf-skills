# DeviceUseStatement

**ID** `DeviceUseStatement` | **URL** `http://hl7.org/fhir/StructureDefinition/DeviceUseStatement` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Orders and Observations) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

A record of a device being used by a patient where the record is the result of a report from the patient or another clinician.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DeviceUseStatement` | 0..* | `DeviceUseStatement` |  |  | Record of use of a device |
| `DeviceUseStatement.identifier` | 0..* | `Identifier` | summary |  | External identifier for this record |
| `DeviceUseStatement.basedOn` | 0..* | `Reference(ServiceRequest)` | summary |  | Fulfills plan, proposal or order |
| `DeviceUseStatement.status` | 1..1 | `code` | modifier summary | required→device-statement-status@4.0.1 | active \| completed \| entered-in-error + |
| `DeviceUseStatement.subject` | 1..1 | `Reference(Patient \| Group)` | summary |  | Patient using device |
| `DeviceUseStatement.derivedFrom` | 0..* | `Reference(ServiceRequest \| Procedure \| Claim \| Observation \| QuestionnaireResponse \| DocumentReference)` | summary |  | Supporting information |
| `DeviceUseStatement.timing[x]` | 0..1 | `Timing, Period, dateTime` | summary |  | How often the device was used |
| `DeviceUseStatement.recordedOn` | 0..1 | `dateTime` | summary |  | When statement was recorded |
| `DeviceUseStatement.source` | 0..1 | `Reference(Patient \| Practitioner \| PractitionerRole \| RelatedPerson)` | summary |  | Who made the statement |
| `DeviceUseStatement.device` | 1..1 | `Reference(Device)` | summary |  | Reference to device used |
| `DeviceUseStatement.reasonCode` | 0..* | `CodeableConcept` | summary |  | Why device was used |
| `DeviceUseStatement.reasonReference` | 0..* | `Reference(Condition \| Observation \| DiagnosticReport \| DocumentReference \| Media)` | summary |  | Why was DeviceUseStatement performed? |
| `DeviceUseStatement.bodySite` | 0..1 | `CodeableConcept` | summary | example→body-site | Target body site |
| `DeviceUseStatement.note` | 0..* | `Annotation` |  |  | Addition details (comments, instructions) |

Elements defined in ancestors: `DeviceUseStatement.id`, `DeviceUseStatement.meta`, `DeviceUseStatement.implicitRules`, `DeviceUseStatement.language`, `DeviceUseStatement.text`, `DeviceUseStatement.contained`, `DeviceUseStatement.extension`, `DeviceUseStatement.modifierExtension`

## Invariants

_No profile-specific invariants._
