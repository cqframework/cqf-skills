# Goal

**ID** `Goal` | **URL** `http://hl7.org/fhir/StructureDefinition/Goal` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Patient Care) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Describes the intended objective(s) for a patient, group or organization care, for example, weight loss, restoring an activity of daily living, obtaining herd immunity via immunization, meeting a process improvement objective, etc.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Goal` | 0..* | `Goal` |  |  | Describes the intended objective(s) for a patient, group or organization |
| `Goal.identifier` | 0..* | `Identifier` |  |  | External Ids for this goal |
| `Goal.lifecycleStatus` | 1..1 | `code` | modifier summary | required→goal-status@4.0.1 | proposed \| planned \| accepted \| active \| on-hold \| completed \| cancelled \| entered-in-error \| rejected |
| `Goal.achievementStatus` | 0..1 | `CodeableConcept` | summary | preferred→goal-achievement | in-progress \| improving \| worsening \| no-change \| achieved \| sustaining \| not-achieved \| no-progress \| not-attainable |
| `Goal.category` | 0..* | `CodeableConcept` | summary | example→goal-category | E.g. Treatment, dietary, behavioral, etc. |
| `Goal.priority` | 0..1 | `CodeableConcept` | summary | preferred→goal-priority | high-priority \| medium-priority \| low-priority |
| `Goal.description` | 1..1 | `CodeableConcept` | summary | example→clinical-findings | Code or text describing goal |
| `Goal.subject` | 1..1 | `Reference(Patient \| Group \| Organization)` | summary |  | Who this goal is intended for |
| `Goal.start[x]` | 0..1 | `date, CodeableConcept` | summary | example→goal-start-event | When goal pursuit begins |
| `Goal.target` | 0..* | `BackboneElement` |  |  | Target outcome for the goal |
| `Goal.target.measure` | 0..1 | `CodeableConcept` | summary | example→observation-codes | The parameter whose value is being tracked |
| `Goal.target.detail[x]` | 0..1 | `Quantity, Range, CodeableConcept, string, boolean, integer, Ratio` | summary | Codes to identify the target value of the focus to be achieved to signify the fulfillment of the goal. | The target value to be achieved |
| `Goal.target.due[x]` | 0..1 | `date, Duration` | summary |  | Reach goal on or before |
| `Goal.statusDate` | 0..1 | `date` | summary |  | When goal status took effect |
| `Goal.statusReason` | 0..1 | `string` |  |  | Reason for current status |
| `Goal.expressedBy` | 0..1 | `Reference(Patient \| Practitioner \| PractitionerRole \| RelatedPerson)` | summary |  | Who's responsible for creating Goal? |
| `Goal.addresses` | 0..* | `Reference(Condition \| Observation \| MedicationStatement \| NutritionOrder \| ServiceRequest \| RiskAssessment)` |  |  | Issues addressed by this goal |
| `Goal.note` | 0..* | `Annotation` |  |  | Comments about the goal |
| `Goal.outcomeCode` | 0..* | `CodeableConcept` |  | example→clinical-findings | What result was achieved regarding the goal? |
| `Goal.outcomeReference` | 0..* | `Reference(Observation)` |  |  | Observation that resulted from goal |

Elements defined in ancestors: `Goal.id`, `Goal.meta`, `Goal.implicitRules`, `Goal.language`, `Goal.text`, `Goal.contained`, `Goal.extension`, `Goal.modifierExtension`, `Goal.target.id`, `Goal.target.extension`, `Goal.target.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `Goal.target` | `gol-1` | error | Goal.target.measure is required if Goal.target.detail is populated | `(detail.exists() and measure.exists()) or detail.exists().not()` |
