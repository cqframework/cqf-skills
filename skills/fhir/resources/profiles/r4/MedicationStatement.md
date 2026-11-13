# MedicationStatement

**ID** `MedicationStatement` | **URL** `http://hl7.org/fhir/StructureDefinition/MedicationStatement` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Pharmacy) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

A record of a medication that is being consumed by a patient. A MedicationStatement may indicate that the patient may be taking the medication now or has taken the medication in the past or will be taking the medication in the future. The source of this information can be the patient, significant other (such as a family member or spouse), or a clinician. A common scenario where this information is captured is during the history taking process during a patient visit or stay. The medication information may come from sources such as the patient's memory, from a prescription bottle, or from a list of medications the patient, clinician or other party maintains. The primary difference between a medication statement and a medication administration is that the medication administration has complete administration information and is based on actual administration information from the person who administered the medication. A medication statement is often, if not always, less specific. There is no required date/time when the medication was administered, in fact we only know that a source has reported the patient is taking this medication, where details such as time, quantity, or rate or even medication product may be incomplete or missing or less precise. As stated earlier, the medication statement information may come from the patient's memory, from a prescription bottle or from a list of medications the patient, clinician or other party maintains. Medication administration is more formal and is not missing detailed information.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `MedicationStatement` | 0..* | `MedicationStatement` |  |  | Record of medication being taken by a patient |
| `MedicationStatement.identifier` | 0..* | `Identifier` | summary |  | External identifier |
| `MedicationStatement.basedOn` | 0..* | `Reference(MedicationRequest \| CarePlan \| ServiceRequest)` | summary |  | Fulfils plan, proposal or order |
| `MedicationStatement.partOf` | 0..* | `Reference(MedicationAdministration \| MedicationDispense \| MedicationStatement \| Procedure \| Observation)` | summary |  | Part of referenced event |
| `MedicationStatement.status` | 1..1 | `code` | modifier summary | required→medication-statement-status@4.0.1 | active \| completed \| entered-in-error \| intended \| stopped \| on-hold \| unknown \| not-taken |
| `MedicationStatement.statusReason` | 0..* | `CodeableConcept` |  | example→reason-medication-status-codes | Reason for current status |
| `MedicationStatement.category` | 0..1 | `CodeableConcept` | summary | preferred→medication-statement-category | Type of medication usage |
| `MedicationStatement.medication[x]` | 1..1 | `CodeableConcept, Reference(Medication)` | summary | example→medication-codes | What medication was taken |
| `MedicationStatement.subject` | 1..1 | `Reference(Patient \| Group)` | summary |  | Who is/was taking the medication |
| `MedicationStatement.context` | 0..1 | `Reference(Encounter \| EpisodeOfCare)` | summary |  | Encounter / Episode associated with MedicationStatement |
| `MedicationStatement.effective[x]` | 0..1 | `dateTime, Period` | summary |  | The date/time or interval when the medication is/was/will be taken |
| `MedicationStatement.dateAsserted` | 0..1 | `dateTime` | summary |  | When the statement was asserted? |
| `MedicationStatement.informationSource` | 0..1 | `Reference(Patient \| Practitioner \| PractitionerRole \| RelatedPerson \| Organization)` |  |  | Person or organization that provided the information about the taking of this medication |
| `MedicationStatement.derivedFrom` | 0..* | `Reference(Resource)` |  |  | Additional supporting information |
| `MedicationStatement.reasonCode` | 0..* | `CodeableConcept` |  | example→condition-code | Reason for why the medication is being/was taken |
| `MedicationStatement.reasonReference` | 0..* | `Reference(Condition \| Observation \| DiagnosticReport)` |  |  | Condition or observation that supports why the medication is being/was taken |
| `MedicationStatement.note` | 0..* | `Annotation` |  |  | Further information about the statement |
| `MedicationStatement.dosage` | 0..* | `Dosage` |  |  | Details of how medication is/was taken or should be taken |

Elements defined in ancestors: `MedicationStatement.id`, `MedicationStatement.meta`, `MedicationStatement.implicitRules`, `MedicationStatement.language`, `MedicationStatement.text`, `MedicationStatement.contained`, `MedicationStatement.extension`, `MedicationStatement.modifierExtension`

## Invariants

_No profile-specific invariants._
