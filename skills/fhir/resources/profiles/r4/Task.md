# Task

**ID** `Task` | **URL** `http://hl7.org/fhir/StructureDefinition/Task` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Orders and Observations) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

A task to be performed.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Task` | 0..* | `Task` |  |  | A task to be performed |
| `Task.identifier` | 0..* | `Identifier` |  |  | Task Instance Identifier |
| `Task.instantiatesCanonical` | 0..1 | `canonical(ActivityDefinition)` | summary |  | Formal definition of task |
| `Task.instantiatesUri` | 0..1 | `uri` | summary |  | Formal definition of task |
| `Task.basedOn` | 0..* | `Reference(Resource)` | summary |  | Request fulfilled by this task |
| `Task.groupIdentifier` | 0..1 | `Identifier` | summary |  | Requisition or grouper id |
| `Task.partOf` | 0..* | `Reference(Task)` | summary |  | Composite task |
| `Task.status` | 1..1 | `code` | modifier summary | required→task-status@4.0.1 | draft \| requested \| received \| accepted \| + |
| `Task.statusReason` | 0..1 | `CodeableConcept` | summary | Codes to identify the reason for current status. These will typically be specific to a particular workflow. | Reason for current status |
| `Task.businessStatus` | 0..1 | `CodeableConcept` | summary | The domain-specific business-contextual sub-state of the task. For example: "Blood drawn", "IV inserted", "Awaiting physician signature", etc. | E.g. "Specimen collected", "IV prepped" |
| `Task.intent` | 1..1 | `code` | summary | required→task-intent@4.0.1 | unknown \| proposal \| plan \| order \| original-order \| reflex-order \| filler-order \| instance-order \| option |
| `Task.priority` | 0..1 | `code` |  | required→request-priority@4.0.1 | routine \| urgent \| asap \| stat |
| `Task.code` | 0..1 | `CodeableConcept` | summary | example→task-code | Task Type |
| `Task.description` | 0..1 | `string` | summary |  | Human-readable explanation of task |
| `Task.focus` | 0..1 | `Reference(Resource)` | summary |  | What task is acting on |
| `Task.for` | 0..1 | `Reference(Resource)` | summary |  | Beneficiary of the Task |
| `Task.encounter` | 0..1 | `Reference(Encounter)` | summary |  | Healthcare event during which this task originated |
| `Task.executionPeriod` | 0..1 | `Period` | summary |  | Start and end time of execution |
| `Task.authoredOn` | 0..1 | `dateTime` |  |  | Task Creation Date |
| `Task.lastModified` | 0..1 | `dateTime` | summary |  | Task Last Modified Date |
| `Task.requester` | 0..1 | `Reference(Device \| Organization \| Patient \| Practitioner \| PractitionerRole \| RelatedPerson)` | summary |  | Who is asking for task to be done |
| `Task.performerType` | 0..* | `CodeableConcept` |  | preferred→performer-role | Requested performer |
| `Task.owner` | 0..1 | `Reference(Practitioner \| PractitionerRole \| Organization \| CareTeam \| HealthcareService \| Patient \| Device \| RelatedPerson)` | summary |  | Responsible individual |
| `Task.location` | 0..1 | `Reference(Location)` | summary |  | Where task occurs |
| `Task.reasonCode` | 0..1 | `CodeableConcept` |  | Indicates why the task is needed. E.g. Suspended because patient admitted to hospital. | Why task is needed |
| `Task.reasonReference` | 0..1 | `Reference(Resource)` |  |  | Why task is needed |
| `Task.insurance` | 0..* | `Reference(Coverage \| ClaimResponse)` |  |  | Associated insurance coverage |
| `Task.note` | 0..* | `Annotation` |  |  | Comments made about the task |
| `Task.relevantHistory` | 0..* | `Reference(Provenance)` |  |  | Key events in history of the Task |
| `Task.restriction` | 0..1 | `BackboneElement` |  |  | Constraints on fulfillment tasks |
| `Task.restriction.repetitions` | 0..1 | `positiveInt` |  |  | How many times to repeat |
| `Task.restriction.period` | 0..1 | `Period` |  |  | When fulfillment sought |
| `Task.restriction.recipient` | 0..* | `Reference(Patient \| Practitioner \| PractitionerRole \| RelatedPerson \| Group \| Organization)` |  |  | For whom is fulfillment sought? |
| `Task.input` | 0..* | `BackboneElement` |  |  | Information used to perform task |
| `Task.input.type` | 1..1 | `CodeableConcept` |  | Codes to identify types of input parameters. These will typically be specific to a particular workflow. E.g. "Comparison source", "Applicable consent", "Concomitent Medications", etc. | Label for the input |
| `Task.input.value[x]` | 1..1 | `base64Binary, boolean, canonical, code, date, dateTime, decimal, id, instant, integer, markdown, oid, positiveInt, string, time, unsignedInt, uri, url, uuid, Address, Age, Annotation, Attachment, CodeableConcept, Coding, ContactPoint, Count, Distance, Duration, HumanName, Identifier, Money, Period, Quantity, Range, Ratio, Reference, SampledData, Signature, Timing, ContactDetail, Contributor, DataRequirement, Expression, ParameterDefinition, RelatedArtifact, TriggerDefinition, UsageContext, Dosage, Meta` |  |  | Content to use in performing the task |
| `Task.output` | 0..* | `BackboneElement` |  |  | Information produced as part of task |
| `Task.output.type` | 1..1 | `CodeableConcept` |  | Codes to identify types of input parameters. These will typically be specific to a particular workflow. E.g. "Identified issues", "Preliminary results", "Filler order", "Final results", etc. | Label for output |
| `Task.output.value[x]` | 1..1 | `base64Binary, boolean, canonical, code, date, dateTime, decimal, id, instant, integer, markdown, oid, positiveInt, string, time, unsignedInt, uri, url, uuid, Address, Age, Annotation, Attachment, CodeableConcept, Coding, ContactPoint, Count, Distance, Duration, HumanName, Identifier, Money, Period, Quantity, Range, Ratio, Reference, SampledData, Signature, Timing, ContactDetail, Contributor, DataRequirement, Expression, ParameterDefinition, RelatedArtifact, TriggerDefinition, UsageContext, Dosage, Meta` |  |  | Result of output |

Elements defined in ancestors: `Task.id`, `Task.meta`, `Task.implicitRules`, `Task.language`, `Task.text`, `Task.contained`, `Task.extension`, `Task.modifierExtension`, `Task.restriction.id`, `Task.restriction.extension`, `Task.restriction.modifierExtension`, `Task.input.id`, `Task.input.extension`, `Task.input.modifierExtension`, `Task.output.id`, `Task.output.extension`, `Task.output.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `Task` | `inv-1` | error | Last modified date must be greater than or equal to authored-on date. | `lastModified.exists().not() or authoredOn.exists().not() or lastModified >= authoredOn` |
