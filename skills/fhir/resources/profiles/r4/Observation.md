# Observation

**ID** `Observation` | **URL** `http://hl7.org/fhir/StructureDefinition/Observation` | **Status** active
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Orders and Observations) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Measurements and simple assertions made about a patient, device or other subject.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Observation` | 0..* | `Observation` |  |  | Measurements and simple assertions |
| `Observation.identifier` | 0..* | `Identifier` | summary |  | Business Identifier for observation |
| `Observation.basedOn` | 0..* | `Reference(CarePlan \| DeviceRequest \| ImmunizationRecommendation \| MedicationRequest \| NutritionOrder \| ServiceRequest)` | summary |  | Fulfills plan, proposal or order |
| `Observation.partOf` | 0..* | `Reference(MedicationAdministration \| MedicationDispense \| MedicationStatement \| Procedure \| Immunization \| ImagingStudy)` | summary |  | Part of referenced event |
| `Observation.status` | 1..1 | `code` | modifier summary | required→observation-status@4.0.1 | registered \| preliminary \| final \| amended + |
| `Observation.category` | 0..* | `CodeableConcept` |  | preferred→observation-category | Classification of type of observation |
| `Observation.code` | 1..1 | `CodeableConcept` | summary | example→observation-codes | Type of observation (code / type) |
| `Observation.subject` | 0..1 | `Reference(Patient \| Group \| Device \| Location)` | summary |  | Who and/or what the observation is about |
| `Observation.focus` | 0..* | `Reference(Resource)` | summary |  | What the observation is about, when it is not about the subject of record |
| `Observation.encounter` | 0..1 | `Reference(Encounter)` | summary |  | Healthcare event during which this observation is made |
| `Observation.effective[x]` | 0..1 | `dateTime, Period, Timing, instant` | summary |  | Clinically relevant time/time-period for observation |
| `Observation.issued` | 0..1 | `instant` | summary |  | Date/Time this version was made available |
| `Observation.performer` | 0..* | `Reference(Practitioner \| PractitionerRole \| Organization \| CareTeam \| Patient \| RelatedPerson)` | summary |  | Who is responsible for the observation |
| `Observation.value[x]` | 0..1 | `Quantity, CodeableConcept, string, boolean, integer, Range, Ratio, SampledData, time, dateTime, Period` | summary |  | Actual result |
| `Observation.dataAbsentReason` | 0..1 | `CodeableConcept` |  | extensible→data-absent-reason | Why the result is missing |
| `Observation.interpretation` | 0..* | `CodeableConcept` |  | extensible→observation-interpretation | High, low, normal, etc. |
| `Observation.note` | 0..* | `Annotation` |  |  | Comments about the observation |
| `Observation.bodySite` | 0..1 | `CodeableConcept` |  | example→body-site | Observed body part |
| `Observation.method` | 0..1 | `CodeableConcept` |  | example→observation-methods | How it was done |
| `Observation.specimen` | 0..1 | `Reference(Specimen)` |  |  | Specimen used for this observation |
| `Observation.device` | 0..1 | `Reference(Device \| DeviceMetric)` |  |  | (Measurement) Device |
| `Observation.referenceRange` | 0..* | `BackboneElement` |  |  | Provides guide for interpretation |
| `Observation.referenceRange.low` | 0..1 | `Quantity(SimpleQuantity)` |  |  | Low Range, if relevant |
| `Observation.referenceRange.high` | 0..1 | `Quantity(SimpleQuantity)` |  |  | High Range, if relevant |
| `Observation.referenceRange.type` | 0..1 | `CodeableConcept` |  | preferred→referencerange-meaning | Reference range qualifier |
| `Observation.referenceRange.appliesTo` | 0..* | `CodeableConcept` |  | example→referencerange-appliesto | Reference range population |
| `Observation.referenceRange.age` | 0..1 | `Range` |  |  | Applicable age range, if relevant |
| `Observation.referenceRange.text` | 0..1 | `string` |  |  | Text based reference range in an observation |
| `Observation.hasMember` | 0..* | `Reference(Observation \| QuestionnaireResponse \| MolecularSequence)` | summary |  | Related resource that belongs to the Observation group |
| `Observation.derivedFrom` | 0..* | `Reference(DocumentReference \| ImagingStudy \| Media \| QuestionnaireResponse \| Observation \| MolecularSequence)` | summary |  | Related measurements the observation is made from |
| `Observation.component` | 0..* | `BackboneElement` | summary |  | Component results |
| `Observation.component.code` | 1..1 | `CodeableConcept` | summary | example→observation-codes | Type of component observation (code / type) |
| `Observation.component.value[x]` | 0..1 | `Quantity, CodeableConcept, string, boolean, integer, Range, Ratio, SampledData, time, dateTime, Period` | summary |  | Actual component result |
| `Observation.component.dataAbsentReason` | 0..1 | `CodeableConcept` |  | extensible→data-absent-reason | Why the component result is missing |
| `Observation.component.interpretation` | 0..* | `CodeableConcept` |  | extensible→observation-interpretation | High, low, normal, etc. |
| `Observation.component.referenceRange` | 0..* | `see Observation.referenceRange` |  |  | Provides guide for interpretation of component result |

Elements defined in ancestors: `Observation.id`, `Observation.meta`, `Observation.implicitRules`, `Observation.language`, `Observation.text`, `Observation.contained`, `Observation.extension`, `Observation.modifierExtension`, `Observation.referenceRange.id`, `Observation.referenceRange.extension`, `Observation.referenceRange.modifierExtension`, `Observation.component.id`, `Observation.component.extension`, `Observation.component.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `Observation` | `obs-6` | error | dataAbsentReason SHALL only be present if Observation.value[x] is not present | `dataAbsentReason.empty() or value.empty()` |
| `Observation` | `obs-7` | error | If Observation.code is the same as an Observation.component.code then the value element associated with the code SHALL NOT be present | `value.empty() or component.code.where(coding.intersect(%resource.code.coding).exists()).empty()` |
| `Observation.referenceRange` | `obs-3` | error | Must have at least a low or a high or text | `low.exists() or high.exists() or text.exists()` |
