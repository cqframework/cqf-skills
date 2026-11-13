# FamilyMemberHistory

**ID** `FamilyMemberHistory` | **URL** `http://hl7.org/fhir/StructureDefinition/FamilyMemberHistory` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Patient Care) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Significant health conditions for a person related to the patient relevant in the context of care for the patient.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `FamilyMemberHistory` | 0..* | `FamilyMemberHistory` |  |  | Information about patient's relatives, relevant for patient |
| `FamilyMemberHistory.identifier` | 0..* | `Identifier` | summary |  | External Id(s) for this record |
| `FamilyMemberHistory.instantiatesCanonical` | 0..* | `canonical(PlanDefinition \| Questionnaire \| ActivityDefinition \| Measure \| OperationDefinition)` | summary |  | Instantiates FHIR protocol or definition |
| `FamilyMemberHistory.instantiatesUri` | 0..* | `uri` | summary |  | Instantiates external protocol or definition |
| `FamilyMemberHistory.status` | 1..1 | `code` | modifier summary | required→history-status@4.0.1 | partial \| completed \| entered-in-error \| health-unknown |
| `FamilyMemberHistory.dataAbsentReason` | 0..1 | `CodeableConcept` | summary | example→history-absent-reason | subject-unknown \| withheld \| unable-to-obtain \| deferred |
| `FamilyMemberHistory.patient` | 1..1 | `Reference(Patient)` | summary |  | Patient history is about |
| `FamilyMemberHistory.date` | 0..1 | `dateTime` | summary |  | When history was recorded or last updated |
| `FamilyMemberHistory.name` | 0..1 | `string` | summary |  | The family member described |
| `FamilyMemberHistory.relationship` | 1..1 | `CodeableConcept` | summary | example→v3-FamilyMember | Relationship to the subject |
| `FamilyMemberHistory.sex` | 0..1 | `CodeableConcept` | summary | extensible→administrative-gender | male \| female \| other \| unknown |
| `FamilyMemberHistory.born[x]` | 0..1 | `Period, date, string` |  |  | (approximate) date of birth |
| `FamilyMemberHistory.age[x]` | 0..1 | `Age, Range, string` | summary |  | (approximate) age |
| `FamilyMemberHistory.estimatedAge` | 0..1 | `boolean` | summary |  | Age is estimated? |
| `FamilyMemberHistory.deceased[x]` | 0..1 | `boolean, Age, Range, date, string` | summary |  | Dead? How old/when? |
| `FamilyMemberHistory.reasonCode` | 0..* | `CodeableConcept` | summary | example→clinical-findings | Why was family member history performed? |
| `FamilyMemberHistory.reasonReference` | 0..* | `Reference(Condition \| Observation \| AllergyIntolerance \| QuestionnaireResponse \| DiagnosticReport \| DocumentReference)` | summary |  | Why was family member history performed? |
| `FamilyMemberHistory.note` | 0..* | `Annotation` |  |  | General note about related person |
| `FamilyMemberHistory.condition` | 0..* | `BackboneElement` |  |  | Condition that the related person had |
| `FamilyMemberHistory.condition.code` | 1..1 | `CodeableConcept` |  | example→condition-code | Condition suffered by relation |
| `FamilyMemberHistory.condition.outcome` | 0..1 | `CodeableConcept` |  | example→condition-outcome | deceased \| permanent disability \| etc. |
| `FamilyMemberHistory.condition.contributedToDeath` | 0..1 | `boolean` |  |  | Whether the condition contributed to the cause of death |
| `FamilyMemberHistory.condition.onset[x]` | 0..1 | `Age, Range, Period, string` |  |  | When condition first manifested |
| `FamilyMemberHistory.condition.note` | 0..* | `Annotation` |  |  | Extra information about condition |

Elements defined in ancestors: `FamilyMemberHistory.id`, `FamilyMemberHistory.meta`, `FamilyMemberHistory.implicitRules`, `FamilyMemberHistory.language`, `FamilyMemberHistory.text`, `FamilyMemberHistory.contained`, `FamilyMemberHistory.extension`, `FamilyMemberHistory.modifierExtension`, `FamilyMemberHistory.condition.id`, `FamilyMemberHistory.condition.extension`, `FamilyMemberHistory.condition.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `FamilyMemberHistory` | `fhs-1` | error | Can have age[x] or born[x], but not both | `age.empty() or born.empty()` |
| `FamilyMemberHistory` | `fhs-2` | error | Can only have estimatedAge if age[x] is present | `age.exists() or estimatedAge.empty()` |
