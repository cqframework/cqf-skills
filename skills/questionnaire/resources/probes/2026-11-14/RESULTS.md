# Probe results, 2026-11-14

Run with clinical-reasoning **4.13.0** (`org.opencds.cqf.fhir:cqf-fhir-cr`, which brings the CQL
translator and engine 5.4.0 and HAPI FHIR 8.12.0), through `scripts/sdc/run.sh`, on the project in this
folder. All data is synthetic.

- `input/resources/`: Libraries `PopRules` and `OtherRules` (CQL base64 in `Library.content`), the
  Questionnaires below, and the profile `StructureDefinition/probe-observation`.
- `input/tests/`: `Patient/adult-1` (Ada, female, born 1980-04-01), `Patient/child-1` (Bo, born 2018),
  two body-weight Observations of adult-1 (68.5 kg on 2026-01-10, 70.2 kg on 2026-06-10), two Conditions
  (diabetes, onset 2015-03-01; hypertension, onset 2019-07-15), `Encounter/enc-1`, and the
  QuestionnaireResponses used for `$extract`.

`PopRules` defines, in context Patient: `"Given Name"` (`Patient.name[0].given[0]`), `"Weights"` (the
weight values, a list of two Decimals), `"Last Weight Quantity"` (a Quantity), `"Gender Code"`
(`Patient.gender`, a FHIR code), `"Gender Coding"` (a System Code), `"Has Diabetes"` (`exists [Condition]`),
`"Conditions"` (`[Condition]`), `"Throws"` (`singleton from { 1, 2 }`, a run-time error), `"Null Value"`
(`null as String`) and `"Patient Resource"` (`Patient`). `OtherRules` defines `"Given Name"` as
`'From OtherRules'`.

## 1. Questionnaire/pop, `$populate`

`run.sh . populate pop Patient/adult-1` (subject only, no `context`). `pop` has `cqf-library` PopRules and
a `launchContext` `patient`. It returns a **QuestionnaireResponse**: id `pop-adult-1`, status
`in-progress`, `questionnaire` = `http://example.org/fhir/Questionnaire/pop|1.0.0` (the Questionnaire is not
contained), subject the patient, `authored` the time of the run. Errors are issues of a contained
OperationOutcome `populate-outcome-pop-adult-1`, referenced by a `cqf-messages` extension on the response.
Every item populated from an expression carries the extension `questionnaireresponse-author` with
valueReference `http://cqframework.org/fhir/Device/clinical-quality-language`.

| Item | Definition | Answer |
| --- | --- | --- |
| `given` | string, initialExpression `text/cql-identifier` `Given Name` | `Ada` |
| `given-qualified` | `text/cql-identifier` `OtherRules."Given Name"` | none; issue "Could not resolve expression reference 'OtherRules."Given Name"' in library 'PopRules'" |
| `birth-fhirpath` | date, `text/fhirpath` `%patient.birthDate` | none; issue "Could not resolve identifier %patient" (see §2) |
| `birth-subject` | `text/fhirpath` `%subject.birthDate` | none; "Could not resolve identifier %subject" |
| `age` | integer, `text/cql-expression` `AgeInYears()` | `46` |
| `weights-repeats` | decimal, `repeats: true`, `Weights` | two answers, `70.2` and `68.5` |
| `weights-single` | decimal, **not repeating**, `Weights` | **two answers**, `70.2` and `68.5` |
| `weight-quantity` | quantity, `Last Weight Quantity` | valueQuantity 70.2 kg |
| `gender-code` | choice with Coding answerOptions, `Gender Code` (a FHIR `code`) | **valueString** `female` |
| `gender-coding` | choice, `Gender Coding` (a System Code) | valueCoding `female` |
| `has-diabetes` | boolean, **calculatedExpression** `Has Diabetes` | **none** |
| `old-calculated` | boolean, `cqf-calculatedValue` (valueString) `Has Diabetes` | none |
| `static` | string, `initial` valueString `fixed` | `fixed` (copied as an answer) |
| `throws` | `Throws` | none; issue "Expected a list with at most one element…" |
| `null` | `Null Value` | none, no issue |
| `missing` | `No Such Definition` | none; issue "Could not resolve expression reference 'No Such Definition' in library 'PopRules'" |
| `type-mismatch` | **integer**, `Given Name` (a String) | **valueString** `Ada` |
| `hidden` | `questionnaire-hidden` true, `Given Name` | `Ada` |
| `enabled-when` | `enableWhen` has-diabetes = true (has-diabetes has no answer), `Given Name` | **`Ada`** |
| `obs-weight` | quantity, `code` LOINC 29463-7 and `observationLinkPeriod` 100 years, no expression | **none** |
| `conditions` | group, `repeats: true`, itemPopulationContext `Conditions` named `condition`; children `conditions.code` (`%condition.code.coding.first()`) and `conditions.onset` (`%condition.onset`), both `text/fhirpath` | two `conditions` items, one per Condition: SNOMED 44054006 with `2015-03-01`, SNOMED 38341003 with `2019-07-15` |
| `nested-parent` | boolean, `Has Diabetes`, with a child question `nested-child` (`Given Name`) | `true`; `nested-child` is under `answer.item`, answered `Ada` |

## 2. Launch context and subject

| Run | Result |
| --- | --- |
| `populate pop Patient/adult-1 patient=Patient/adult-1` (a `context` with name `patient`) | as §1, but `birth-fhirpath` (`%patient.birthDate`) is answered `1980-04-01`; `%subject` still doesn't resolve |
| `populate no-lib Patient/adult-1` (no `context`) | `%patient…` items fail to compile ("Could not resolve identifier %patient"); `text/cql-expression` `AgeInYears()` gives `46` |
| `populate ref Patient/adult-1 patient=Patient/child-1` | the response's subject is **Patient/child-1** and `given` is `Bo`: the `patient` context overrides `subject` |
| `populate ref Patient/adult-1 encounter=Encounter/enc-1` (`ref` declares no launchContext) | the response's id is `ref-enc-1` and its **subject is `Encounter/enc-1`**; no item is answered and **no issue** is reported |

## 3. Questionnaire/no-lib: FHIRPath runs as CQL

`no-lib` has no `cqf-library`; `run.sh . populate no-lib Patient/adult-1 patient=Patient/adult-1`:

| Item | Expression (`text/fhirpath` unless noted) | Answer |
| --- | --- | --- |
| `fhirpath` | `%patient.birthDate` | `1980-04-01` |
| `cqlexpr` | `AgeInYears()` (`text/cql-expression`) | `46` |
| `fp-first` | `%patient.name.given.first()` | `Ada` |
| `fp-where` | `%patient.name.where(family = 'Example').given` | `Ada` |
| `fp-matches` | `'abc'.matches('b')` | **`false`** |

In FHIRPath, `matches` is a partial match, so `'abc'.matches('b')` is true. The engine returned false,
matching the whole string as CQL 5.4.0's engine does: the expression was evaluated as CQL. Expressions
that are also valid CQL, such as `.first()` and `.where()`, work.

## 4. Questionnaire/two-libs: library selection

`two-libs` has `cqf-library` PopRules then OtherRules; both define `"Given Name"`.

| Item | Expression | Answer |
| --- | --- | --- |
| `noref` | `text/cql-identifier` `Given Name`, no `reference` | `From OtherRules` |
| `ref-other` | the same, `reference` = OtherRules | `From OtherRules` |
| `qualified-expr` | `text/cql-expression` `OtherRules."Given Name"` | `From OtherRules` |
| `qualified-expr-pop` | `text/cql-expression` `PopRules."Given Name"` | `Ada` |

With no `reference`, this run used OtherRules, the second declared. The libraries are held in an
unordered map, so which one is used isn't guaranteed.

## 5. Questionnaire/ref: a Resource result

`ref` has `patient-ref` (type `reference`, initialExpression `Patient Resource`) and `given`.
`run.sh . populate ref Patient/adult-1` returns a response with **no `patient-ref` item at all** and the
issue "Error encountered populating item (patient-ref): class org.hl7.fhir.r4.model.Patient cannot be cast
to class org.hl7.fhir.r4.model.Type"; `given` is answered `Ada`.

## 6. `$extract`

`Questionnaire/extract` items: `weight` (quantity, LOINC 29463-7, `observationExtract` true), `height`
(decimal, LOINC 8302-2, **no** `observationExtract`), `smoker` (group with `observationExtract` true, child
`smoker.status` boolean, LOINC 72166-2), `free` (string, no code), `allergy` (group with
`itemExtractionContext` valueCode `AllergyIntolerance`; children with `definition`
`…/AllergyIntolerance#AllergyIntolerance.code` and `#AllergyIntolerance.note.text`).

| Run | Result |
| --- | --- |
| `extract extract-1` (all items answered, `height` 165) | the result **can't be serialized**: the Observation for `height` has a `valueDecimal`, which R4 Observation doesn't allow. The `height` Observation exists although the item has no `observationExtract`. The log also shows "No resource of type StructureDefinition found for url: http://hl7.org/fhir/StructureDefinition/AllergyIntolerance" |
| `extract extract-2` (the same without `height`) | a **transaction Bundle** `extract-extract-2`, every entry `request.method` POST with no `fullUrl`: Observations `extract-extract-2.weight` and `extract-extract-2.smoker.status`, and AllergyIntolerance `extract-extract-2-allergy` |

Each Observation: status `final`; category system **`http://hl7.org/fhir/observation-category`**, code
`survey`; `code` from the item; subject the response's subject; `effectiveDateTime` and `issued` the
response's `authored`; value from the answer (valueQuantity, valueBoolean); `derivedFrom` the
QuestionnaireResponse; and an extension `http://hl7.org/fhir/uv/sdc/StructureDefinition/derivedFromLinkId`
with a sub-extension `text` holding the linkId. The AllergyIntolerance has `code` and `note.text` from the
answers, and **no `patient`**.

`Questionnaire/extract-sdc4`: `symptoms` (choice, repeats, LOINC 75325-1, `observationExtract` true) and
`allergy`, a group with the SDC 4.0.0 complex `definitionExtract` (sub-extension `definition` =
`http://hl7.org/fhir/StructureDefinition/AllergyIntolerance`).

| Run | Result |
| --- | --- |
| `extract extract-3` (both answered) | **throws** `IllegalArgumentException: Unable to retrieve definition for item: allergy` |
| `extract extract-4` (only `symptoms`, answered Cough and Fever) | two Observations, **both with id `extract-extract-4.symptoms`**, values `valueCodeableConcept` Cough and Fever |
| `extract extract-noq` (its Questionnaire, `…/Questionnaire/missing`, doesn't exist) | **throws** `IllegalArgumentException: Unable to retrieve Questionnaire code map for Observation based extraction` |

## 7. Questionnaire generation

`run.sh . generate probe-observation` (a differential-only Observation profile: `code` with a pattern,
`effective[x]` 1..1 dateTime, `value[x]` 1..1 Quantity, `note` mustSupport 0..*), with `supportedOnly` and
`minimalOnly` false, returns a Questionnaire with id `probe-observation`, status `active`, and one group
item `1` (`definition` the profile url, text `ProbeObservation`) carrying the
`sdc-questionnaire-definitionExtract` extension **twice**, each a valueCanonical of the profile url. Its
children are `1.1` (`Observation.effective[x]`, dateTime, required) and `1.2` (`Observation.value[x]`,
quantity, required), each with `definition` `<profile url>#<element id>` and `text` the element path. There
is no item for `code` (it has a pattern value) or `note`.
