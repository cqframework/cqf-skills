# MedicationDispense

**ID** `MedicationDispense` | **URL** `http://hl7.org/fhir/StructureDefinition/MedicationDispense` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Pharmacy) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Indicates that a medication product is to be or has been dispensed for a named person/patient. This includes a description of the medication product (supply) provided and the instructions for administering the medication. The medication dispense is the result of a pharmacy system responding to a medication order.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `MedicationDispense` | 0..* | `MedicationDispense` |  |  | Dispensing a medication to a named patient |
| `MedicationDispense.identifier` | 0..* | `Identifier` |  |  | External identifier |
| `MedicationDispense.partOf` | 0..* | `Reference(Procedure)` |  |  | Event that dispense is part of |
| `MedicationDispense.status` | 1..1 | `code` | modifier summary | required→medicationdispense-status@4.0.1 | preparation \| in-progress \| cancelled \| on-hold \| completed \| entered-in-error \| stopped \| declined \| unknown |
| `MedicationDispense.statusReason[x]` | 0..1 | `CodeableConcept, Reference(DetectedIssue)` |  | example→medicationdispense-status-reason | Why a dispense was not performed |
| `MedicationDispense.category` | 0..1 | `CodeableConcept` |  | preferred→medicationdispense-category | Type of medication dispense |
| `MedicationDispense.medication[x]` | 1..1 | `CodeableConcept, Reference(Medication)` | summary | example→medication-codes | What medication was supplied |
| `MedicationDispense.subject` | 0..1 | `Reference(Patient \| Group)` | summary |  | Who the dispense is for |
| `MedicationDispense.context` | 0..1 | `Reference(Encounter \| EpisodeOfCare)` |  |  | Encounter / Episode associated with event |
| `MedicationDispense.supportingInformation` | 0..* | `Reference(Resource)` |  |  | Information that supports the dispensing of the medication |
| `MedicationDispense.performer` | 0..* | `BackboneElement` |  |  | Who performed event |
| `MedicationDispense.performer.function` | 0..1 | `CodeableConcept` |  | example→medicationdispense-performer-function | Who performed the dispense and what they did |
| `MedicationDispense.performer.actor` | 1..1 | `Reference(Practitioner \| PractitionerRole \| Organization \| Patient \| Device \| RelatedPerson)` |  |  | Individual who was performing |
| `MedicationDispense.location` | 0..1 | `Reference(Location)` |  |  | Where the dispense occurred |
| `MedicationDispense.authorizingPrescription` | 0..* | `Reference(MedicationRequest)` |  |  | Medication order that authorizes the dispense |
| `MedicationDispense.type` | 0..1 | `CodeableConcept` |  | example→v3-ActPharmacySupplyType | Trial fill, partial fill, emergency fill, etc. |
| `MedicationDispense.quantity` | 0..1 | `Quantity(SimpleQuantity)` |  |  | Amount dispensed |
| `MedicationDispense.daysSupply` | 0..1 | `Quantity(SimpleQuantity)` |  |  | Amount of medication expressed as a timing amount |
| `MedicationDispense.whenPrepared` | 0..1 | `dateTime` | summary |  | When product was packaged and reviewed |
| `MedicationDispense.whenHandedOver` | 0..1 | `dateTime` |  |  | When product was given out |
| `MedicationDispense.destination` | 0..1 | `Reference(Location)` |  |  | Where the medication was sent |
| `MedicationDispense.receiver` | 0..* | `Reference(Patient \| Practitioner)` |  |  | Who collected the medication |
| `MedicationDispense.note` | 0..* | `Annotation` |  |  | Information about the dispense |
| `MedicationDispense.dosageInstruction` | 0..* | `Dosage` |  |  | How the medication is to be used by the patient or administered by the caregiver |
| `MedicationDispense.substitution` | 0..1 | `BackboneElement` |  |  | Whether a substitution was performed on the dispense |
| `MedicationDispense.substitution.wasSubstituted` | 1..1 | `boolean` |  |  | Whether a substitution was or was not performed on the dispense |
| `MedicationDispense.substitution.type` | 0..1 | `CodeableConcept` |  | example→v3-ActSubstanceAdminSubstitutionCode | Code signifying whether a different drug was dispensed from what was prescribed |
| `MedicationDispense.substitution.reason` | 0..* | `CodeableConcept` |  | example→v3-SubstanceAdminSubstitutionReason | Why was substitution made |
| `MedicationDispense.substitution.responsibleParty` | 0..* | `Reference(Practitioner \| PractitionerRole)` |  |  | Who is responsible for the substitution |
| `MedicationDispense.detectedIssue` | 0..* | `Reference(DetectedIssue)` |  |  | Clinical issue with action |
| `MedicationDispense.eventHistory` | 0..* | `Reference(Provenance)` |  |  | A list of relevant lifecycle events |

Elements defined in ancestors: `MedicationDispense.id`, `MedicationDispense.meta`, `MedicationDispense.implicitRules`, `MedicationDispense.language`, `MedicationDispense.text`, `MedicationDispense.contained`, `MedicationDispense.extension`, `MedicationDispense.modifierExtension`, `MedicationDispense.performer.id`, `MedicationDispense.performer.extension`, `MedicationDispense.performer.modifierExtension`, `MedicationDispense.substitution.id`, `MedicationDispense.substitution.extension`, `MedicationDispense.substitution.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `MedicationDispense` | `mdd-1` | error | whenHandedOver cannot be before whenPrepared | `whenHandedOver.empty() or whenPrepared.empty() or whenHandedOver >= whenPrepared` |
