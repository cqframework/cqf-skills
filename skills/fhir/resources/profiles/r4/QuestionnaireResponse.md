# QuestionnaireResponse

**ID** `QuestionnaireResponse` | **URL** `http://hl7.org/fhir/StructureDefinition/QuestionnaireResponse` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (FHIR Infrastructure) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

A structured set of questions and their answers. The questions are ordered and grouped into coherent subsets, corresponding to the structure of the grouping of the questionnaire being responded to.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `QuestionnaireResponse` | 0..* | `QuestionnaireResponse` |  |  | A structured set of questions and their answers |
| `QuestionnaireResponse.identifier` | 0..1 | `Identifier` | summary |  | Unique id for this set of answers |
| `QuestionnaireResponse.basedOn` | 0..* | `Reference(CarePlan \| ServiceRequest)` | summary |  | Request fulfilled by this QuestionnaireResponse |
| `QuestionnaireResponse.partOf` | 0..* | `Reference(Observation \| Procedure)` | summary |  | Part of this action |
| `QuestionnaireResponse.questionnaire` | 0..1 | `canonical(Questionnaire)` | summary |  | Form being answered |
| `QuestionnaireResponse.status` | 1..1 | `code` | modifier summary | required→questionnaire-answers-status@4.0.1 | in-progress \| completed \| amended \| entered-in-error \| stopped |
| `QuestionnaireResponse.subject` | 0..1 | `Reference(Resource)` | summary |  | The subject of the questions |
| `QuestionnaireResponse.encounter` | 0..1 | `Reference(Encounter)` | summary |  | Encounter created as part of |
| `QuestionnaireResponse.authored` | 0..1 | `dateTime` | summary |  | Date the answers were gathered |
| `QuestionnaireResponse.author` | 0..1 | `Reference(Device \| Practitioner \| PractitionerRole \| Patient \| RelatedPerson \| Organization)` | summary |  | Person who received and recorded the answers |
| `QuestionnaireResponse.source` | 0..1 | `Reference(Patient \| Practitioner \| PractitionerRole \| RelatedPerson)` | summary |  | The person who answered the questions |
| `QuestionnaireResponse.item` | 0..* | `BackboneElement` |  |  | Groups and questions |
| `QuestionnaireResponse.item.linkId` | 1..1 | `string` |  |  | Pointer to specific item from Questionnaire |
| `QuestionnaireResponse.item.definition` | 0..1 | `uri` |  |  | ElementDefinition - details for the item |
| `QuestionnaireResponse.item.text` | 0..1 | `string` |  |  | Name for group or question text |
| `QuestionnaireResponse.item.answer` | 0..* | `BackboneElement` |  |  | The response(s) to the question |
| `QuestionnaireResponse.item.answer.value[x]` | 0..1 | `boolean, decimal, integer, date, dateTime, time, string, uri, Attachment, Coding, Quantity, Reference(Resource)` |  | example→questionnaire-answers | Single-valued answer to the question |
| `QuestionnaireResponse.item.answer.item` | 0..* | `see QuestionnaireResponse.item` |  |  | Nested groups and questions |
| `QuestionnaireResponse.item.item` | 0..* | `see QuestionnaireResponse.item` |  |  | Nested questionnaire response items |

Elements defined in ancestors: `QuestionnaireResponse.id`, `QuestionnaireResponse.meta`, `QuestionnaireResponse.implicitRules`, `QuestionnaireResponse.language`, `QuestionnaireResponse.text`, `QuestionnaireResponse.contained`, `QuestionnaireResponse.extension`, `QuestionnaireResponse.modifierExtension`, `QuestionnaireResponse.item.id`, `QuestionnaireResponse.item.extension`, `QuestionnaireResponse.item.modifierExtension`, `QuestionnaireResponse.item.answer.id`, `QuestionnaireResponse.item.answer.extension`, `QuestionnaireResponse.item.answer.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `QuestionnaireResponse.item` | `qrs-1` | error | Nested item can't be beneath both item and answer | `(answer.exists() and item.exists()).not()` |
