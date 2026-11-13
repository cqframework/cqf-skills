# Specimen

**ID** `Specimen` | **URL** `http://hl7.org/fhir/StructureDefinition/Specimen` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Orders and Observations) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

A sample to be used for analysis.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Specimen` | 0..* | `Specimen` |  |  | Sample for analysis |
| `Specimen.identifier` | 0..* | `Identifier` | summary |  | External Identifier |
| `Specimen.accessionIdentifier` | 0..1 | `Identifier` | summary |  | Identifier assigned by the lab |
| `Specimen.status` | 0..1 | `code` | modifier summary | required→specimen-status@4.0.1 | available \| unavailable \| unsatisfactory \| entered-in-error |
| `Specimen.type` | 0..1 | `CodeableConcept` | summary | example→v2-0487 | Kind of material that forms the specimen |
| `Specimen.subject` | 0..1 | `Reference(Patient \| Group \| Device \| Substance \| Location)` | summary |  | Where the specimen came from. This may be from patient(s), from a location (e.g., the source of an environmental sample… |
| `Specimen.receivedTime` | 0..1 | `dateTime` | summary |  | The time when specimen was received for processing |
| `Specimen.parent` | 0..* | `Reference(Specimen)` |  |  | Specimen from which this specimen originated |
| `Specimen.request` | 0..* | `Reference(ServiceRequest)` |  |  | Why the specimen was collected |
| `Specimen.collection` | 0..1 | `BackboneElement` |  |  | Collection details |
| `Specimen.collection.collector` | 0..1 | `Reference(Practitioner \| PractitionerRole)` | summary |  | Who collected the specimen |
| `Specimen.collection.collected[x]` | 0..1 | `dateTime, Period` | summary |  | Collection time |
| `Specimen.collection.duration` | 0..1 | `Duration` | summary |  | How long it took to collect specimen |
| `Specimen.collection.quantity` | 0..1 | `Quantity(SimpleQuantity)` |  |  | The quantity of specimen collected |
| `Specimen.collection.method` | 0..1 | `CodeableConcept` |  | example→specimen-collection-method | Technique used to perform collection |
| `Specimen.collection.bodySite` | 0..1 | `CodeableConcept` |  | example→body-site | Anatomical collection site |
| `Specimen.collection.fastingStatus[x]` | 0..1 | `CodeableConcept, Duration` | summary | extensible→v2-0916 | Whether or how long patient abstained from food and/or drink |
| `Specimen.processing` | 0..* | `BackboneElement` |  |  | Processing and processing step details |
| `Specimen.processing.description` | 0..1 | `string` |  |  | Textual description of procedure |
| `Specimen.processing.procedure` | 0..1 | `CodeableConcept` |  | example→specimen-processing-procedure | Indicates the treatment step applied to the specimen |
| `Specimen.processing.additive` | 0..* | `Reference(Substance)` |  |  | Material used in the processing step |
| `Specimen.processing.time[x]` | 0..1 | `dateTime, Period` |  |  | Date and time of specimen processing |
| `Specimen.container` | 0..* | `BackboneElement` |  |  | Direct container of specimen (tube/slide, etc.) |
| `Specimen.container.identifier` | 0..* | `Identifier` | summary |  | Id for the container |
| `Specimen.container.description` | 0..1 | `string` |  |  | Textual description of the container |
| `Specimen.container.type` | 0..1 | `CodeableConcept` |  | example→specimen-container-type | Kind of container directly associated with specimen |
| `Specimen.container.capacity` | 0..1 | `Quantity(SimpleQuantity)` |  |  | Container volume or size |
| `Specimen.container.specimenQuantity` | 0..1 | `Quantity(SimpleQuantity)` |  |  | Quantity of specimen within container |
| `Specimen.container.additive[x]` | 0..1 | `CodeableConcept, Reference(Substance)` |  | example→v2-0371 | Additive associated with container |
| `Specimen.condition` | 0..* | `CodeableConcept` | summary | extensible→v2-0493 | State of the specimen |
| `Specimen.note` | 0..* | `Annotation` |  |  | Comments |

Elements defined in ancestors: `Specimen.id`, `Specimen.meta`, `Specimen.implicitRules`, `Specimen.language`, `Specimen.text`, `Specimen.contained`, `Specimen.extension`, `Specimen.modifierExtension`, `Specimen.collection.id`, `Specimen.collection.extension`, `Specimen.collection.modifierExtension`, `Specimen.processing.id`, `Specimen.processing.extension`, `Specimen.processing.modifierExtension`, `Specimen.container.id`, `Specimen.container.extension`, `Specimen.container.modifierExtension`

## Invariants

_No profile-specific invariants._
