# Questionnaire and QuestionnaireResponse: Structure

Baseline: FHIR R4 (4.0.1), with SDC 4.0.0's added rules. Untagged statements hold in R4.
Sources: FHIR-R4, FHIR-R5, SDC-4.0.0

What a Questionnaire's elements mean and the rules a QuestionnaireResponse must follow. Expressions,
population and SDC behavior extensions are in [population.md](population.md); extraction is in
[extraction.md](extraction.md). Element tables for the other R4 resources are in the `fhir` skill.

## Items

`Questionnaire.item` is recursive. Every item has a `linkId`, "unique within the Questionnaire"
[src: FHIR-R4 questionnaire-definitions.html#Questionnaire.item.linkId], and a `type`.

| Type | Answer type | Notes |
| --- | --- | --- |
| `group` | none | "should have at least one child item" |
| `display` | none | "will not capture an answer or have child items" |
| `boolean`, `decimal`, `integer`, `date`, `dateTime`, `time` | the same type | |
| `string`, `text` | valueString | `text` is multi-line |
| `url` | valueUri | |
| `choice` | valueCoding | from `answerOption` or `answerValueSet` |
| `open-choice` | valueCoding or valueString | a listed option, or free text |
| `attachment`, `reference`, `quantity` | Attachment, Reference, Quantity | |

[src: FHIR-R4 codesystem-item-type.html#item-type-group] [src: FHIR-R4 questionnaire.html#question-types]

**R5 differs.** `choice` and `open-choice` are replaced by `coding` with
`answerConstraint` (`optionsOnly`, the default, `optionsOrType`, `optionsOrString`)
[src: FHIR-R5 codesystem-item-type.html#item-type-coding]
[src: FHIR-R5 questionnaire-definitions.html#Questionnaire.item.answerConstraint]. SDC 4.0.0 lets R4
content use `answerConstraint` through the cross-version extension
`http://hl7.org/fhir/5.0/StructureDefinition/extension-Questionnaire.item.answerConstraint`
[src: SDC-4.0.0 package/StructureDefinition-sdc-questionnairecommon.json].

**Nesting.** Questions can have child items too, not only groups: "the Questionnaire resource supports
nested items beneath both items of type "group" … as well as beneath questions"
[src: FHIR-R4 questionnaire.html#notes]. Only `display` items can't have children (que-1).

## Invariants

The R4 invariants on `Questionnaire.item` [src: FHIR-R4 package/StructureDefinition-Questionnaire.json]
[src: FHIR-R4 questionnaire.html#invs]:

| Key | Rule |
| --- | --- |
| que-1 | Group items must have nested items, display items cannot have nested items |
| que-2 | linkIds are unique within the Questionnaire (`descendants().linkId.isDistinct()`) |
| que-3 | Display items cannot have a `code` |
| que-4 | A question cannot have both `answerOption` and `answerValueSet` |
| que-5 | Only `choice` and `open-choice` items can have `answerValueSet` (the text; the expression also allows other types) |
| que-6, que-9 | `required`, `repeats` and `readOnly` aren't permitted on display items |
| que-7 | With `operator` `exists`, the enableWhen answer must be a boolean |
| que-8 | `initial` can't be specified for groups or display items |
| que-10 | `maxLength` only on boolean, decimal, integer, string, text, url and open-choice |
| que-11 | With `answerOption`, `initial` must be absent (use `answerOption.initialSelected`) |
| que-12 | With more than one `enableWhen`, `enableBehavior` is required. The R4 expression tests `count() > 2`, so a validator only flags three or more; R5 fixes it [src: FHIR-R5 questionnaire-definitions.html#Questionnaire.item] |
| que-13 | Only repeating items can have more than one `initial` |

SDC's base profiles add: a linkId is at most 255 characters (que-15), `answerExpression` excludes
`answerOption` and `answerValueSet` (sdc-1), and if `version` is present, `versionAlgorithm` must be too
(sdc-2) [src: SDC-4.0.0 package/StructureDefinition-sdc-questionnairecommon.json].

## Answers: answerOption, answerValueSet, initial

- `answerOption.value[x]` is integer, date, time, string, Coding or Reference
  [src: FHIR-R4 questionnaire-definitions.html#Questionnaire.item.answerOption.value_x_].
- `answerValueSet` "only supports defining values for 'string' and Coding elements"; for a string item the
  allowed values are the expansion's codes [src: SDC-4.0.0 behavior.html#answerOption].
- `initial` is a default the user can change unless the item is `readOnly`; only repeating items can have
  more than one [src: FHIR-R4 questionnaire-definitions.html#Questionnaire.item.initial]. A computed
  default uses SDC's `initialExpression` instead, and an item can't have both
  [src: SDC-4.0.0 populate.html#exp-pop].

## enableWhen

```json
"enableWhen": [
  { "question": "smoker", "operator": "=", "answerBoolean": true },
  { "question": "packs", "operator": "exists", "answerBoolean": true }
],
"enableBehavior": "all"
```

- **Operators**: `exists` ("True if whether an answer exists is equal to the enableWhen answer (which must
  be a boolean)"), `=`, `!=`, `>`, `<`, `>=`, `<=`. `=` is true when "at least one answer has a value that
  is equal" [src: FHIR-R4 package/CodeSystem-questionnaire-enable-operator.json]. The `answer[x]` type
  matches the question's answer type (`answerCoding` for a choice).
- **enableBehavior** `all` or `any`; it "must be specified if more than one enableWhen value is provided"
  [src: FHIR-R4 questionnaire-definitions.html#Questionnaire.item.enableBehavior].
- **Disabled items.** enableWhen is a modifier: a disabled item "behaves as though the elements weren't
  actually present", all its descendants are disabled too, and `required` doesn't apply
  [src: FHIR-R4 questionnaire-definitions.html#Questionnaire.item.enableWhen]. SDC: "no answers are stored
  for non-enabled content" [src: SDC-4.0.0 behavior.html#enableWhen].
- **Which question.** If several items share the linkId (in repeating groups), `question` means the nearest
  occurrence, searching ancestors, then preceding, then following items
  [src: FHIR-R4 questionnaire-definitions.html#Questionnaire.item.enableWhen.question].
- For conditions enableWhen can't express, SDC has `enableWhenExpression` ([population.md](population.md)).

## QuestionnaireResponse

- **Hierarchy.** The response's items "SHALL mirror the hierarchy of the corresponding Questionnaire"
  [src: FHIR-R4 questionnaireresponse.html#notes]. Groups nest directly under `item`; children of a
  question nest under each `answer.item` [src: FHIR-R4 questionnaireresponse-definitions.html#QuestionnaireResponse.item].
  qrs-1: an item can't have both `answer` and `item`
  [src: FHIR-R4 package/StructureDefinition-QuestionnaireResponse.json].
- **Repeats.** A repeating question is one response item with several answers; a repeating group is
  several response items with the same linkId (SDC's qrs-2 and sdcqr-2; not R4 core invariants)
  [src: SDC-4.0.0 package/StructureDefinition-sdc-questionnaireresponsecommon.json].
- **Elements.** A response item has `linkId`, `definition`, `text`, `answer` (with `value[x]` and `item`)
  and `item`. It has no `initial` [src: FHIR-R4 package/StructureDefinition-QuestionnaireResponse.json].
- **Status**: `in-progress`, `completed`, `amended`, `entered-in-error`, `stopped`
  [src: FHIR-R4 package/CodeSystem-questionnaire-answers-status.json].
- **Which items to include.** All items SHOULD be included if relevant, which "might also include items
  that were not enabled… though of course these will not have answers"
  [src: FHIR-R4 questionnaireresponse.html#link].
