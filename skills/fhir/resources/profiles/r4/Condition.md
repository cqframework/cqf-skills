# Condition

**ID** `Condition` | **URL** `http://hl7.org/fhir/StructureDefinition/Condition` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Patient Care) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

A clinical condition, problem, diagnosis, or other event, situation, issue, or clinical concept that has risen to a level of concern.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Condition` | 0..* | `Condition` |  |  | Detailed information about conditions, problems or diagnoses |
| `Condition.identifier` | 0..* | `Identifier` | summary |  | External Ids for this condition |
| `Condition.clinicalStatus` | 0..1 | `CodeableConcept` | modifier summary | required→condition-clinical@4.0.1 | active \| recurrence \| relapse \| inactive \| remission \| resolved |
| `Condition.verificationStatus` | 0..1 | `CodeableConcept` | modifier summary | required→condition-ver-status@4.0.1 | unconfirmed \| provisional \| differential \| confirmed \| refuted \| entered-in-error |
| `Condition.category` | 0..* | `CodeableConcept` |  | extensible→condition-category | problem-list-item \| encounter-diagnosis |
| `Condition.severity` | 0..1 | `CodeableConcept` |  | preferred→condition-severity | Subjective severity of condition |
| `Condition.code` | 0..1 | `CodeableConcept` | summary | example→condition-code | Identification of the condition, problem or diagnosis |
| `Condition.bodySite` | 0..* | `CodeableConcept` | summary | example→body-site | Anatomical location, if relevant |
| `Condition.subject` | 1..1 | `Reference(Patient \| Group)` | summary |  | Who has the condition? |
| `Condition.encounter` | 0..1 | `Reference(Encounter)` | summary |  | Encounter created as part of |
| `Condition.onset[x]` | 0..1 | `dateTime, Age, Period, Range, string` | summary |  | Estimated or actual date, date-time, or age |
| `Condition.abatement[x]` | 0..1 | `dateTime, Age, Period, Range, string` |  |  | When in resolution/remission |
| `Condition.recordedDate` | 0..1 | `dateTime` | summary |  | Date record was first recorded |
| `Condition.recorder` | 0..1 | `Reference(Practitioner \| PractitionerRole \| Patient \| RelatedPerson)` | summary |  | Who recorded the condition |
| `Condition.asserter` | 0..1 | `Reference(Practitioner \| PractitionerRole \| Patient \| RelatedPerson)` | summary |  | Person who asserts this condition |
| `Condition.stage` | 0..* | `BackboneElement` |  |  | Stage/grade, usually assessed formally |
| `Condition.stage.summary` | 0..1 | `CodeableConcept` |  | example→condition-stage | Simple summary (disease specific) |
| `Condition.stage.assessment` | 0..* | `Reference(ClinicalImpression \| DiagnosticReport \| Observation)` |  |  | Formal record of assessment |
| `Condition.stage.type` | 0..1 | `CodeableConcept` |  | example→condition-stage-type | Kind of staging |
| `Condition.evidence` | 0..* | `BackboneElement` |  |  | Supporting evidence |
| `Condition.evidence.code` | 0..* | `CodeableConcept` | summary | example→manifestation-or-symptom | Manifestation/symptom |
| `Condition.evidence.detail` | 0..* | `Reference(Resource)` | summary |  | Supporting information found elsewhere |
| `Condition.note` | 0..* | `Annotation` |  |  | Additional information about the Condition |

Elements defined in ancestors: `Condition.id`, `Condition.meta`, `Condition.implicitRules`, `Condition.language`, `Condition.text`, `Condition.contained`, `Condition.extension`, `Condition.modifierExtension`, `Condition.stage.id`, `Condition.stage.extension`, `Condition.stage.modifierExtension`, `Condition.evidence.id`, `Condition.evidence.extension`, `Condition.evidence.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `Condition` | `con-3` | warning | Condition.clinicalStatus SHALL be present if verificationStatus is not entered-in-error and category is problem-list-item | `clinicalStatus.exists() or verificationStatus.coding.where(system='http://terminology.hl7.org/CodeSystem/condition-ver-status' and code = 'entered-in-error').exists() or category.select($this='problem-list-item').empty()` |
| `Condition` | `con-4` | error | If condition is abated, then clinicalStatus must be either inactive, resolved, or remission | `abatement.empty() or clinicalStatus.coding.where(system='http://terminology.hl7.org/CodeSystem/condition-clinical' and (code='resolved' or code='remission' or code='inactive')).exists()` |
| `Condition` | `con-5` | error | Condition.clinicalStatus SHALL NOT be present if verification Status is entered-in-error | `verificationStatus.coding.where(system='http://terminology.hl7.org/CodeSystem/condition-ver-status' and code='entered-in-error').empty() or clinicalStatus.empty()` |
| `Condition.stage` | `con-1` | error | Stage SHALL have summary or assessment | `summary.exists() or assessment.exists()` |
| `Condition.evidence` | `con-2` | error | evidence SHALL have code or details | `code.exists() or detail.exists()` |
