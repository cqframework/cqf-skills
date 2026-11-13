# Medication

**ID** `Medication` | **URL** `http://hl7.org/fhir/StructureDefinition/Medication` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Pharmacy) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

This resource is primarily used for the identification and definition of a medication for the purposes of prescribing, dispensing, and administering a medication as well as for making statements about medication use.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Medication` | 0..* | `Medication` |  |  | Definition of a Medication |
| `Medication.identifier` | 0..* | `Identifier` | summary |  | Business identifier for this medication |
| `Medication.code` | 0..1 | `CodeableConcept` | summary | example→medication-codes | Codes that identify this medication |
| `Medication.status` | 0..1 | `code` | modifier summary | required→medication-status@4.0.1 | active \| inactive \| entered-in-error |
| `Medication.manufacturer` | 0..1 | `Reference(Organization)` | summary |  | Manufacturer of the item |
| `Medication.form` | 0..1 | `CodeableConcept` |  | example→medication-form-codes | powder \| tablets \| capsule + |
| `Medication.amount` | 0..1 | `Ratio` | summary |  | Amount of drug in package |
| `Medication.ingredient` | 0..* | `BackboneElement` |  |  | Active or inactive ingredient |
| `Medication.ingredient.item[x]` | 1..1 | `CodeableConcept, Reference(Substance \| Medication)` |  |  | The actual ingredient or content |
| `Medication.ingredient.isActive` | 0..1 | `boolean` |  |  | Active ingredient indicator |
| `Medication.ingredient.strength` | 0..1 | `Ratio` |  |  | Quantity of ingredient present |
| `Medication.batch` | 0..1 | `BackboneElement` |  |  | Details about packaged medications |
| `Medication.batch.lotNumber` | 0..1 | `string` |  |  | Identifier assigned to batch |
| `Medication.batch.expirationDate` | 0..1 | `dateTime` |  |  | When batch will expire |

Elements defined in ancestors: `Medication.id`, `Medication.meta`, `Medication.implicitRules`, `Medication.language`, `Medication.text`, `Medication.contained`, `Medication.extension`, `Medication.modifierExtension`, `Medication.ingredient.id`, `Medication.ingredient.extension`, `Medication.ingredient.modifierExtension`, `Medication.batch.id`, `Medication.batch.extension`, `Medication.batch.modifierExtension`

## Invariants

_No profile-specific invariants._
