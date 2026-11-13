# Encounter

**ID** `Encounter` | **URL** `http://hl7.org/fhir/StructureDefinition/Encounter` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Patient Administration) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

An interaction between a patient and healthcare provider(s) for the purpose of providing healthcare service(s) or assessing the health status of a patient.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Encounter` | 0..* | `Encounter` |  |  | An interaction during which services are provided to the patient |
| `Encounter.identifier` | 0..* | `Identifier` | summary |  | Identifier(s) by which this encounter is known |
| `Encounter.status` | 1..1 | `code` | modifier summary | required→encounter-status@4.0.1 | planned \| arrived \| triaged \| in-progress \| onleave \| finished \| cancelled + |
| `Encounter.statusHistory` | 0..* | `BackboneElement` |  |  | List of past encounter statuses |
| `Encounter.statusHistory.status` | 1..1 | `code` |  | required→encounter-status@4.0.1 | planned \| arrived \| triaged \| in-progress \| onleave \| finished \| cancelled + |
| `Encounter.statusHistory.period` | 1..1 | `Period` |  |  | The time that the episode was in the specified status |
| `Encounter.class` | 1..1 | `Coding` | summary | extensible→v3-ActEncounterCode | Classification of patient encounter |
| `Encounter.classHistory` | 0..* | `BackboneElement` |  |  | List of past encounter classes |
| `Encounter.classHistory.class` | 1..1 | `Coding` |  | extensible→v3-ActEncounterCode | inpatient \| outpatient \| ambulatory \| emergency + |
| `Encounter.classHistory.period` | 1..1 | `Period` |  |  | The time that the episode was in the specified class |
| `Encounter.type` | 0..* | `CodeableConcept` | summary | example→encounter-type | Specific type of encounter |
| `Encounter.serviceType` | 0..1 | `CodeableConcept` | summary | example→service-type | Specific type of service |
| `Encounter.priority` | 0..1 | `CodeableConcept` |  | example→v3-ActPriority | Indicates the urgency of the encounter |
| `Encounter.subject` | 0..1 | `Reference(Patient \| Group)` | summary |  | The patient or group present at the encounter |
| `Encounter.episodeOfCare` | 0..* | `Reference(EpisodeOfCare)` | summary |  | Episode(s) of care that this encounter should be recorded against |
| `Encounter.basedOn` | 0..* | `Reference(ServiceRequest)` |  |  | The ServiceRequest that initiated this encounter |
| `Encounter.participant` | 0..* | `BackboneElement` | summary |  | List of participants involved in the encounter |
| `Encounter.participant.type` | 0..* | `CodeableConcept` | summary | extensible→encounter-participant-type | Role of participant in encounter |
| `Encounter.participant.period` | 0..1 | `Period` |  |  | Period of time during the encounter that the participant participated |
| `Encounter.participant.individual` | 0..1 | `Reference(Practitioner \| PractitionerRole \| RelatedPerson)` | summary |  | Persons involved in the encounter other than the patient |
| `Encounter.appointment` | 0..* | `Reference(Appointment)` | summary |  | The appointment that scheduled this encounter |
| `Encounter.period` | 0..1 | `Period` |  |  | The start and end time of the encounter |
| `Encounter.length` | 0..1 | `Duration` |  |  | Quantity of time the encounter lasted (less time absent) |
| `Encounter.reasonCode` | 0..* | `CodeableConcept` | summary | preferred→encounter-reason | Coded reason the encounter takes place |
| `Encounter.reasonReference` | 0..* | `Reference(Condition \| Procedure \| Observation \| ImmunizationRecommendation)` | summary |  | Reason the encounter takes place (reference) |
| `Encounter.diagnosis` | 0..* | `BackboneElement` | summary |  | The list of diagnosis relevant to this encounter |
| `Encounter.diagnosis.condition` | 1..1 | `Reference(Condition \| Procedure)` | summary |  | The diagnosis or procedure relevant to the encounter |
| `Encounter.diagnosis.use` | 0..1 | `CodeableConcept` |  | preferred→diagnosis-role | Role that this diagnosis has within the encounter (e.g. admission, billing, discharge ...) |
| `Encounter.diagnosis.rank` | 0..1 | `positiveInt` |  |  | Ranking of the diagnosis (for each role type) |
| `Encounter.account` | 0..* | `Reference(Account)` |  |  | The set of accounts that may be used for billing for this Encounter |
| `Encounter.hospitalization` | 0..1 | `BackboneElement` |  |  | Details about the admission to a healthcare service |
| `Encounter.hospitalization.preAdmissionIdentifier` | 0..1 | `Identifier` |  |  | Pre-admission identifier |
| `Encounter.hospitalization.origin` | 0..1 | `Reference(Location \| Organization)` |  |  | The location/organization from which the patient came before admission |
| `Encounter.hospitalization.admitSource` | 0..1 | `CodeableConcept` |  | preferred→encounter-admit-source | From where patient was admitted (physician referral, transfer) |
| `Encounter.hospitalization.reAdmission` | 0..1 | `CodeableConcept` |  | example→v2-0092 | The type of hospital re-admission that has occurred (if any). If the value is absent, then this is not identified as a … |
| `Encounter.hospitalization.dietPreference` | 0..* | `CodeableConcept` |  | example→encounter-diet | Diet preferences reported by the patient |
| `Encounter.hospitalization.specialCourtesy` | 0..* | `CodeableConcept` |  | preferred→encounter-special-courtesy | Special courtesies (VIP, board member) |
| `Encounter.hospitalization.specialArrangement` | 0..* | `CodeableConcept` |  | preferred→encounter-special-arrangements | Wheelchair, translator, stretcher, etc. |
| `Encounter.hospitalization.destination` | 0..1 | `Reference(Location \| Organization)` |  |  | Location/organization to which the patient is discharged |
| `Encounter.hospitalization.dischargeDisposition` | 0..1 | `CodeableConcept` |  | example→encounter-discharge-disposition | Category or kind of location after discharge |
| `Encounter.location` | 0..* | `BackboneElement` |  |  | List of locations where the patient has been |
| `Encounter.location.location` | 1..1 | `Reference(Location)` |  |  | Location the encounter takes place |
| `Encounter.location.status` | 0..1 | `code` |  | required→encounter-location-status@4.0.1 | planned \| active \| reserved \| completed |
| `Encounter.location.physicalType` | 0..1 | `CodeableConcept` |  | example→location-physical-type | The physical type of the location (usually the level in the location hierachy - bed room ward etc.) |
| `Encounter.location.period` | 0..1 | `Period` |  |  | Time period during which the patient was present at the location |
| `Encounter.serviceProvider` | 0..1 | `Reference(Organization)` |  |  | The organization (facility) responsible for this encounter |
| `Encounter.partOf` | 0..1 | `Reference(Encounter)` |  |  | Another Encounter this encounter is part of |

Elements defined in ancestors: `Encounter.id`, `Encounter.meta`, `Encounter.implicitRules`, `Encounter.language`, `Encounter.text`, `Encounter.contained`, `Encounter.extension`, `Encounter.modifierExtension`, `Encounter.statusHistory.id`, `Encounter.statusHistory.extension`, `Encounter.statusHistory.modifierExtension`, `Encounter.classHistory.id`, `Encounter.classHistory.extension`, `Encounter.classHistory.modifierExtension`, `Encounter.participant.id`, `Encounter.participant.extension`, `Encounter.participant.modifierExtension`, `Encounter.diagnosis.id`, `Encounter.diagnosis.extension`, `Encounter.diagnosis.modifierExtension`, `Encounter.hospitalization.id`, `Encounter.hospitalization.extension`, `Encounter.hospitalization.modifierExtension`, `Encounter.location.id`, `Encounter.location.extension`, `Encounter.location.modifierExtension`

## Invariants

_No profile-specific invariants._
