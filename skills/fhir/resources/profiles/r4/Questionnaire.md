# Questionnaire

**ID** `Questionnaire` | **URL** `http://hl7.org/fhir/StructureDefinition/Questionnaire` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (FHIR Infrastructure) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

A structured set of questions intended to guide the collection of answers from end-users. Questionnaires provide detailed control over order, presentation, phraseology and grouping to allow coherent, consistent data collection.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Questionnaire` | 0..* | `Questionnaire` |  |  | A structured set of questions |
| `Questionnaire.url` | 0..1 | `uri` | summary |  | Canonical identifier for this questionnaire, represented as a URI (globally unique) |
| `Questionnaire.identifier` | 0..* | `Identifier` | summary |  | Additional identifier for the questionnaire |
| `Questionnaire.version` | 0..1 | `string` | summary |  | Business version of the questionnaire |
| `Questionnaire.name` | 0..1 | `string` | summary |  | Name for this questionnaire (computer friendly) |
| `Questionnaire.title` | 0..1 | `string` | summary |  | Name for this questionnaire (human friendly) |
| `Questionnaire.derivedFrom` | 0..* | `canonical(Questionnaire)` |  |  | Instantiates protocol or definition |
| `Questionnaire.status` | 1..1 | `code` | modifier summary | required→publication-status@4.0.1 | draft \| active \| retired \| unknown |
| `Questionnaire.experimental` | 0..1 | `boolean` | summary |  | For testing purposes, not real usage |
| `Questionnaire.subjectType` | 0..* | `code` | summary | required→resource-types@4.0.1 | Resource that can be subject of QuestionnaireResponse |
| `Questionnaire.date` | 0..1 | `dateTime` | summary |  | Date last changed |
| `Questionnaire.publisher` | 0..1 | `string` | summary |  | Name of the publisher (organization or individual) |
| `Questionnaire.contact` | 0..* | `ContactDetail` | summary |  | Contact details for the publisher |
| `Questionnaire.description` | 0..1 | `markdown` |  |  | Natural language description of the questionnaire |
| `Questionnaire.useContext` | 0..* | `UsageContext` | summary |  | The context that the content is intended to support |
| `Questionnaire.jurisdiction` | 0..* | `CodeableConcept` | summary | extensible→jurisdiction | Intended jurisdiction for questionnaire (if applicable) |
| `Questionnaire.purpose` | 0..1 | `markdown` |  |  | Why this questionnaire is defined |
| `Questionnaire.copyright` | 0..1 | `markdown` |  |  | Use and/or publishing restrictions |
| `Questionnaire.approvalDate` | 0..1 | `date` |  |  | When the questionnaire was approved by publisher |
| `Questionnaire.lastReviewDate` | 0..1 | `date` |  |  | When the questionnaire was last reviewed |
| `Questionnaire.effectivePeriod` | 0..1 | `Period` | summary |  | When the questionnaire is expected to be used |
| `Questionnaire.code` | 0..* | `Coding` | summary | example→questionnaire-questions | Concept that represents the overall questionnaire |
| `Questionnaire.item` | 0..* | `BackboneElement` |  |  | Questions and sections within the Questionnaire |
| `Questionnaire.item.linkId` | 1..1 | `string` |  |  | Unique id for item in questionnaire |
| `Questionnaire.item.definition` | 0..1 | `uri` |  |  | ElementDefinition - details for the item |
| `Questionnaire.item.code` | 0..* | `Coding` |  | example→questionnaire-questions | Corresponding concept for this item in a terminology |
| `Questionnaire.item.prefix` | 0..1 | `string` |  |  | E.g. "1(a)", "2.5.3" |
| `Questionnaire.item.text` | 0..1 | `string` |  |  | Primary text for the item |
| `Questionnaire.item.type` | 1..1 | `code` |  | required→item-type@4.0.1 | group \| display \| boolean \| decimal \| integer \| date \| dateTime + |
| `Questionnaire.item.enableWhen` | 0..* | `BackboneElement` | modifier |  | Only allow data when |
| `Questionnaire.item.enableWhen.question` | 1..1 | `string` |  |  | Question that determines whether item is enabled |
| `Questionnaire.item.enableWhen.operator` | 1..1 | `code` |  | required→questionnaire-enable-operator@4.0.1 | exists \| = \| != \| > \| < \| >= \| <= |
| `Questionnaire.item.enableWhen.answer[x]` | 1..1 | `boolean, decimal, integer, date, dateTime, time, string, Coding, Quantity, Reference(Resource)` |  | example→questionnaire-answers | Value for question comparison based on operator |
| `Questionnaire.item.enableBehavior` | 0..1 | `code` |  | required→questionnaire-enable-behavior@4.0.1 | all \| any |
| `Questionnaire.item.required` | 0..1 | `boolean` |  |  | Whether the item must be included in data results |
| `Questionnaire.item.repeats` | 0..1 | `boolean` |  |  | Whether the item may repeat |
| `Questionnaire.item.readOnly` | 0..1 | `boolean` |  |  | Don't allow human editing |
| `Questionnaire.item.maxLength` | 0..1 | `integer` |  |  | No more than this many characters |
| `Questionnaire.item.answerValueSet` | 0..1 | `canonical(ValueSet)` |  |  | Valueset containing permitted answers |
| `Questionnaire.item.answerOption` | 0..* | `BackboneElement` |  |  | Permitted answer |
| `Questionnaire.item.answerOption.value[x]` | 1..1 | `integer, date, time, string, Coding, Reference(Resource)` |  | example→questionnaire-answers | Answer value |
| `Questionnaire.item.answerOption.initialSelected` | 0..1 | `boolean` |  |  | Whether option is selected by default |
| `Questionnaire.item.initial` | 0..* | `BackboneElement` |  |  | Initial value(s) when item is first rendered |
| `Questionnaire.item.initial.value[x]` | 1..1 | `boolean, decimal, integer, date, dateTime, time, string, uri, Attachment, Coding, Quantity, Reference(Resource)` |  | example→questionnaire-answers | Actual value for initializing the question |
| `Questionnaire.item.item` | 0..* | `see Questionnaire.item` |  |  | Nested questionnaire items |

Elements defined in ancestors: `Questionnaire.id`, `Questionnaire.meta`, `Questionnaire.implicitRules`, `Questionnaire.language`, `Questionnaire.text`, `Questionnaire.contained`, `Questionnaire.extension`, `Questionnaire.modifierExtension`, `Questionnaire.item.id`, `Questionnaire.item.extension`, `Questionnaire.item.modifierExtension`, `Questionnaire.item.enableWhen.id`, `Questionnaire.item.enableWhen.extension`, `Questionnaire.item.enableWhen.modifierExtension`, `Questionnaire.item.answerOption.id`, `Questionnaire.item.answerOption.extension`, `Questionnaire.item.answerOption.modifierExtension`, `Questionnaire.item.initial.id`, `Questionnaire.item.initial.extension`, `Questionnaire.item.initial.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `Questionnaire` | `que-0` | warning | Name should be usable as an identifier for the module by machine processing applications such as code generation | `name.matches('[A-Z]([A-Za-z0-9_]){0,254}')` |
| `Questionnaire` | `que-2` | error | The link ids for groups and questions must be unique within the questionnaire | `descendants().linkId.isDistinct()` |
| `Questionnaire.item` | `que-1` | error | Group items must have nested items, display items cannot have nested items | `(type='group' implies item.empty().not()) and (type.trace('type')='display' implies item.trace('item').empty())` |
| `Questionnaire.item` | `que-3` | error | Display items cannot have a "code" asserted | `type!='display' or code.empty()` |
| `Questionnaire.item` | `que-4` | error | A question cannot have both answerOption and answerValueSet | `answerOption.empty() or answerValueSet.empty()` |
| `Questionnaire.item` | `que-5` | error | Only 'choice' and 'open-choice' items can have answerValueSet | `(type ='choice' or type = 'open-choice' or type = 'decimal' or type = 'integer' or type = 'date' or type = 'dateTime' or type = 'time' or type = 'string' or type = 'quantity') or (answerValueSet.empty() and answerOption.empty())` |
| `Questionnaire.item` | `que-6` | error | Required and repeat aren't permitted for display items | `type!='display' or (required.empty() and repeats.empty())` |
| `Questionnaire.item` | `que-8` | error | Initial values can't be specified for groups or display items | `(type!='group' and type!='display') or initial.empty()` |
| `Questionnaire.item` | `que-9` | error | Read-only can't be specified for "display" items | `type!='display' or readOnly.empty()` |
| `Questionnaire.item` | `que-10` | error | Maximum length can only be declared for simple question types | `(type in ('boolean' \| 'decimal' \| 'integer' \| 'string' \| 'text' \| 'url' \| 'open-choice')) or maxLength.empty()` |
| `Questionnaire.item` | `que-11` | error | If one or more answerOption is present, initial[x] must be missing | `answerOption.empty() or initial.empty()` |
| `Questionnaire.item` | `que-12` | error | If there are more than one enableWhen, enableBehavior must be specified | `enableWhen.count() > 2 implies enableBehavior.exists()` |
| `Questionnaire.item` | `que-13` | error | Can only have multiple initial values for repeating items | `repeats=true or initial.count() <= 1` |
| `Questionnaire.item.enableWhen` | `que-7` | error | If the operator is 'exists', the value must be a boolean | `operator = 'exists' implies (answer is Boolean)` |
