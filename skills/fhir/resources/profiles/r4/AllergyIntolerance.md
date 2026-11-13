# AllergyIntolerance

**ID** `AllergyIntolerance` | **URL** `http://hl7.org/fhir/StructureDefinition/AllergyIntolerance` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Patient Care) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Risk of harmful or undesirable, physiological response which is unique to an individual and associated with exposure to a substance.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `AllergyIntolerance` | 0..* | `AllergyIntolerance` |  |  | Allergy or Intolerance (generally: Risk of adverse reaction to a substance) |
| `AllergyIntolerance.identifier` | 0..* | `Identifier` | summary |  | External ids for this item |
| `AllergyIntolerance.clinicalStatus` | 0..1 | `CodeableConcept` | modifier summary | required→allergyintolerance-clinical@4.0.1 | active \| inactive \| resolved |
| `AllergyIntolerance.verificationStatus` | 0..1 | `CodeableConcept` | modifier summary | required→allergyintolerance-verification@4.0.1 | unconfirmed \| confirmed \| refuted \| entered-in-error |
| `AllergyIntolerance.type` | 0..1 | `code` | summary | required→allergy-intolerance-type@4.0.1 | allergy \| intolerance - Underlying mechanism (if known) |
| `AllergyIntolerance.category` | 0..* | `code` | summary | required→allergy-intolerance-category@4.0.1 | food \| medication \| environment \| biologic |
| `AllergyIntolerance.criticality` | 0..1 | `code` | summary | required→allergy-intolerance-criticality@4.0.1 | low \| high \| unable-to-assess |
| `AllergyIntolerance.code` | 0..1 | `CodeableConcept` | summary | example→allergyintolerance-code | Code that identifies the allergy or intolerance |
| `AllergyIntolerance.patient` | 1..1 | `Reference(Patient)` | summary |  | Who the sensitivity is for |
| `AllergyIntolerance.encounter` | 0..1 | `Reference(Encounter)` |  |  | Encounter when the allergy or intolerance was asserted |
| `AllergyIntolerance.onset[x]` | 0..1 | `dateTime, Age, Period, Range, string` |  |  | When allergy or intolerance was identified |
| `AllergyIntolerance.recordedDate` | 0..1 | `dateTime` |  |  | Date first version of the resource instance was recorded |
| `AllergyIntolerance.recorder` | 0..1 | `Reference(Practitioner \| PractitionerRole \| Patient \| RelatedPerson)` |  |  | Who recorded the sensitivity |
| `AllergyIntolerance.asserter` | 0..1 | `Reference(Patient \| RelatedPerson \| Practitioner \| PractitionerRole)` | summary |  | Source of the information about the allergy |
| `AllergyIntolerance.lastOccurrence` | 0..1 | `dateTime` |  |  | Date(/time) of last known occurrence of a reaction |
| `AllergyIntolerance.note` | 0..* | `Annotation` |  |  | Additional text not captured in other fields |
| `AllergyIntolerance.reaction` | 0..* | `BackboneElement` |  |  | Adverse Reaction Events linked to exposure to substance |
| `AllergyIntolerance.reaction.substance` | 0..1 | `CodeableConcept` |  | example→substance-code | Specific substance or pharmaceutical product considered to be responsible for event |
| `AllergyIntolerance.reaction.manifestation` | 1..* | `CodeableConcept` |  | example→clinical-findings | Clinical symptoms/signs associated with the Event |
| `AllergyIntolerance.reaction.description` | 0..1 | `string` |  |  | Description of the event as a whole |
| `AllergyIntolerance.reaction.onset` | 0..1 | `dateTime` |  |  | Date(/time) when manifestations showed |
| `AllergyIntolerance.reaction.severity` | 0..1 | `code` |  | required→reaction-event-severity@4.0.1 | mild \| moderate \| severe (of event as a whole) |
| `AllergyIntolerance.reaction.exposureRoute` | 0..1 | `CodeableConcept` |  | example→route-codes | How the subject was exposed to the substance |
| `AllergyIntolerance.reaction.note` | 0..* | `Annotation` |  |  | Text about event not captured in other fields |

Elements defined in ancestors: `AllergyIntolerance.id`, `AllergyIntolerance.meta`, `AllergyIntolerance.implicitRules`, `AllergyIntolerance.language`, `AllergyIntolerance.text`, `AllergyIntolerance.contained`, `AllergyIntolerance.extension`, `AllergyIntolerance.modifierExtension`, `AllergyIntolerance.reaction.id`, `AllergyIntolerance.reaction.extension`, `AllergyIntolerance.reaction.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `AllergyIntolerance` | `ait-1` | error | AllergyIntolerance.clinicalStatus SHALL be present if verificationStatus is not entered-in-error. | `verificationStatus.coding.where(system = 'http://terminology.hl7.org/CodeSystem/allergyintolerance-verification' and code = 'entered-in-error').exists() or clinicalStatus.exists()` |
| `AllergyIntolerance` | `ait-2` | error | AllergyIntolerance.clinicalStatus SHALL NOT be present if verification Status is entered-in-error | `verificationStatus.coding.where(system = 'http://terminology.hl7.org/CodeSystem/allergyintolerance-verification' and code = 'entered-in-error').empty() or clinicalStatus.empty()` |
