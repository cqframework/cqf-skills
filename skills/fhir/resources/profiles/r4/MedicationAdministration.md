# MedicationAdministration

**ID** `MedicationAdministration` | **URL** `http://hl7.org/fhir/StructureDefinition/MedicationAdministration` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Pharmacy) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Describes the event of a patient consuming or otherwise being administered a medication. This may be as simple as swallowing a tablet or it may be a long running infusion. Related resources tie this event to the authorizing prescription, and the specific encounter between patient and health care practitioner.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `MedicationAdministration` | 0..* | `MedicationAdministration` |  |  | Administration of medication to a patient |
| `MedicationAdministration.identifier` | 0..* | `Identifier` |  |  | External identifier |
| `MedicationAdministration.instantiates` | 0..* | `uri` | summary |  | Instantiates protocol or definition |
| `MedicationAdministration.partOf` | 0..* | `Reference(MedicationAdministration \| Procedure)` | summary |  | Part of referenced event |
| `MedicationAdministration.status` | 1..1 | `code` | modifier summary | required→medication-admin-status@4.0.1 | in-progress \| not-done \| on-hold \| completed \| entered-in-error \| stopped \| unknown |
| `MedicationAdministration.statusReason` | 0..* | `CodeableConcept` |  | example→reason-medication-not-given-codes | Reason administration not performed |
| `MedicationAdministration.category` | 0..1 | `CodeableConcept` |  | preferred→medication-admin-category | Type of medication usage |
| `MedicationAdministration.medication[x]` | 1..1 | `CodeableConcept, Reference(Medication)` | summary | example→medication-codes | What was administered |
| `MedicationAdministration.subject` | 1..1 | `Reference(Patient \| Group)` | summary |  | Who received medication |
| `MedicationAdministration.context` | 0..1 | `Reference(Encounter \| EpisodeOfCare)` |  |  | Encounter or Episode of Care administered as part of |
| `MedicationAdministration.supportingInformation` | 0..* | `Reference(Resource)` |  |  | Additional information to support administration |
| `MedicationAdministration.effective[x]` | 1..1 | `dateTime, Period` | summary |  | Start and end time of administration |
| `MedicationAdministration.performer` | 0..* | `BackboneElement` | summary |  | Who performed the medication administration and what they did |
| `MedicationAdministration.performer.function` | 0..1 | `CodeableConcept` |  | example→med-admin-perform-function | Type of performance |
| `MedicationAdministration.performer.actor` | 1..1 | `Reference(Practitioner \| PractitionerRole \| Patient \| RelatedPerson \| Device)` | summary |  | Who performed the medication administration |
| `MedicationAdministration.reasonCode` | 0..* | `CodeableConcept` |  | example→reason-medication-given-codes | Reason administration performed |
| `MedicationAdministration.reasonReference` | 0..* | `Reference(Condition \| Observation \| DiagnosticReport)` |  |  | Condition or observation that supports why the medication was administered |
| `MedicationAdministration.request` | 0..1 | `Reference(MedicationRequest)` |  |  | Request administration performed against |
| `MedicationAdministration.device` | 0..* | `Reference(Device)` |  |  | Device used to administer |
| `MedicationAdministration.note` | 0..* | `Annotation` |  |  | Information about the administration |
| `MedicationAdministration.dosage` | 0..1 | `BackboneElement` |  |  | Details of how medication was taken |
| `MedicationAdministration.dosage.text` | 0..1 | `string` |  |  | Free text dosage instructions e.g. SIG |
| `MedicationAdministration.dosage.site` | 0..1 | `CodeableConcept` |  | example→approach-site-codes | Body site administered to |
| `MedicationAdministration.dosage.route` | 0..1 | `CodeableConcept` |  | example→route-codes | Path of substance into body |
| `MedicationAdministration.dosage.method` | 0..1 | `CodeableConcept` |  | example→administration-method-codes | How drug was administered |
| `MedicationAdministration.dosage.dose` | 0..1 | `Quantity(SimpleQuantity)` |  |  | Amount of medication per dose |
| `MedicationAdministration.dosage.rate[x]` | 0..1 | `Ratio, Quantity(SimpleQuantity)` |  |  | Dose quantity per unit of time |
| `MedicationAdministration.eventHistory` | 0..* | `Reference(Provenance)` |  |  | A list of events of interest in the lifecycle |

Elements defined in ancestors: `MedicationAdministration.id`, `MedicationAdministration.meta`, `MedicationAdministration.implicitRules`, `MedicationAdministration.language`, `MedicationAdministration.text`, `MedicationAdministration.contained`, `MedicationAdministration.extension`, `MedicationAdministration.modifierExtension`, `MedicationAdministration.performer.id`, `MedicationAdministration.performer.extension`, `MedicationAdministration.performer.modifierExtension`, `MedicationAdministration.dosage.id`, `MedicationAdministration.dosage.extension`, `MedicationAdministration.dosage.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `MedicationAdministration.dosage` | `mad-1` | error | SHALL have at least one of dosage.dose or dosage.rate[x] | `dose.exists() or rate.exists()` |
