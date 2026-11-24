# Expressions, Behavior Extensions and $populate

Baseline: SDC 4.0.0 on FHIR R4 (4.0.1); clinical-reasoning 4.16.0 for the reference implementation.
Sources: FHIR-R4, FHIR-R5, SDC-4.0.0, SDC-3.0.0, EXT-5.3.0, CR-4.16.0, PROBES-2026-11-14, PROBES-2026-11-24

How SDC adds computable behavior to a Questionnaire, how `$populate` pre-fills a QuestionnaireResponse
as SDC defines it, and what clinical-reasoning (HAPI FHIR's implementation) actually does.

## Extensions

SDC's extensions are `http://hl7.org/fhir/uv/sdc/StructureDefinition/<name>`; core extensions are
`http://hl7.org/fhir/StructureDefinition/<name>`. In SDC 4.0.0 the core ones come from the extensions pack
5.3.0-ballot-tc1 [src: SDC-4.0.0 package/StructureDefinition-sdc-questionnaire-launchContext.json]
[src: EXT-5.3.0 package/StructureDefinition-variable.json].

| Extension | Value | On | Meaning |
| --- | --- | --- | --- |
| `cqf-library` (core) | canonical(Library) | Questionnaire | A library the expressions can use [src: SDC-4.0.0 expressions.html#cqf-library] |
| `sdc-questionnaire-launchContext` | complex: `name` Coding, `type` code 1..*, `description`, `multiplesAllowed` | Questionnaire | A resource the form expects from its launch, available as `%<name>` (below) |
| `variable` (core) | Expression, `name` required | Questionnaire, item | A named value for other expressions [src: SDC-4.0.0 expressions.html#variable] |
| `sdc-questionnaire-initialExpression` | Expression | item | The initial answer, evaluated once at population. Not on groups |
| `sdc-questionnaire-calculatedExpression` | Expression | item | An answer recalculated as the form changes |
| `sdc-questionnaire-candidateExpression` | Expression | item | Candidate answers to choose from |
| `sdc-questionnaire-answerExpression` | Expression | item | The allowed answers, instead of answerOption or answerValueSet |
| `sdc-questionnaire-enableWhenExpression` | Expression | item | Enables the item when true; FHIRPath or CQL, not a FHIR query |
| `sdc-questionnaire-itemPopulationContext` | Expression, `name` required | Questionnaire, item | The resources a group is populated from: one group repetition per result, each available to child expressions as `%<name>` |
| `cqf-expression` (core) | Expression | elements of an item | A computed value for `required`, `repeats`, `readOnly`, `text`, `answerValueSet`, min and max values [src: SDC-4.0.0 behavior.html#cqf-expression] |
| `questionnaire-hidden` (core) | boolean | item | Not shown to the user; still populated and extracted |
| `sdc-questionnaire-observationLinkPeriod` | Duration | item (and, from 4.0.0, the Questionnaire) | Observation-based population: how recent an Observation may be |

[src: SDC-4.0.0 expressions.html#table] [src: SDC-4.0.0 expressions.html#itemPopulationContext]

**Calculated values.** The answer-calculating extension is `calculatedExpression`. `cqf-calculatedValue`
is not used anywhere in SDC 4.0.0, which replaced it with `cqf-expression`
[src: SDC-4.0.0 changes.html#4.0.0]. In R4 core its value is a string, not an Expression
[src: FHIR-R4 package/StructureDefinition-cqf-calculatedValue.json]. A user may override a calculated
answer, and once they have, it "SHOULD no longer be changed"
[src: SDC-4.0.0 expressions.html#calculatedExpression].

## Expression languages

An Expression has `language`, `expression`, `name` and `reference`. SDC uses three languages: FHIR query
(`application/x-fhir-query`), FHIRPath (`text/fhirpath`) and CQL [src: SDC-4.0.0 expressions.html#language].

- **CQL.** `text/cql-identifier` names a definition in a library; `text/cql-expression` is inline CQL
  [src: SDC-4.0.0 expressions.html#language]. R4's code system has only `text/cql`, `text/fhirpath` and
  `application/x-fhir-query`, but the binding is extensible; the two CQL codes come from R5
  [src: FHIR-R4 package/CodeSystem-expression-language.json]
  [src: FHIR-R5 valueset-expression-language.html#urn-ietf-bcp-13-text-cql-identifier].
- **FHIR query** only where the result is a Reference (or a variable): initialExpression "should always
  be a FHIRPath or CQL expression … unless the element has a type of Reference"
  [src: SDC-4.0.0 populate.html#exp-pop]. R5 spells it `text/x-fhir-query`; SDC on R4 uses
  `application/x-fhir-query`.

**Libraries.** List each library with `cqf-library` on the Questionnaire. "CQL identifiers SHALL be
prefixed with the Library.name (with a . separator) if there is more than one Library in scope", and inline
CQL that uses library content is always qualified [src: SDC-4.0.0 expressions.html#cql-in-expressions].
A library parameter whose name matches a launch context receives it; other parameters "will generally
not be made available" [src: SDC-4.0.0 populate.html#cql-execution-context].

## Variables and launch context

- **Built in**: `%resource` (the QuestionnaireResponse), `%context` (the response item for the
  expression's item, or the response at the root), `%questionnaire`, and `%qitem` (the Questionnaire item,
  FHIRPath only). Reserved names can't be redefined [src: SDC-4.0.0 expressions.html#fhirpath].
  `%subject` and `%patient` are not built in: a form gets the patient through a launch context.
- **launchContext** declares a resource the form needs, by a Coding `name` and one or more resource
  `type`s:

```json
{
  "url": "http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire-launchContext",
  "extension": [
    { "url": "name", "valueCoding": { "system": "http://hl7.org/fhir/uv/sdc/CodeSystem/launchContext", "code": "patient" } },
    { "url": "type", "valueCode": "Patient" }
  ]
}
```

  The codes in 4.0.0 are `patient`, `encounter`, `location`, `user`, `study` and, new in 4.0.0,
  `clinical` (which may be a collection); the binding is extensible
  [src: SDC-4.0.0 package/CodeSystem-launchContext.json] [src: SDC-3.0.0 package/CodeSystem-launchContext.json].
  Expressions use it as `%patient` (FHIRPath) or through a library parameter named `patient` (CQL).
- **Order of evaluation**: launch contexts, then the Questionnaire's variables in order of appearance
  [src: SDC-4.0.0 populate.html#exp-pop].

## Population, as SDC defines it

SDC has three population methods: observation-based, expression-based and StructureMap-based; a
StructureMap, if present, takes precedence and the others are ignored [src: SDC-4.0.0 populate.html#design].

- **Observation-based**: an item with `code` and `observationLinkPeriod` gets the value of the most recent
  Observation with that code (status final, amended or corrected) within the period; non-repeating items
  only [src: SDC-4.0.0 populate.html#obs-pop].
- **Expression-based** [src: SDC-4.0.0 populate.html#exp-pop]:
  - `initialExpression` and `itemPopulationContext` are each evaluated once.
  - The result's type must fit the item. The exceptions are: a Resource for a reference item (it becomes a
    Reference), a Quantity for an integer or decimal item with a unit, and a `code` for a coding item when
    it resolves uniquely. Anything else is an error.
  - More results than the item allows: the filler may not populate it, may treat the results as candidates,
    or may populate them and flag them.
  - An empty result "SHALL be treated as 'not answered'" [src: SDC-4.0.0 populate.html#caveats].

### $populate

`Questionnaire/$populate` and `Questionnaire/[id]/$populate`
[src: SDC-4.0.0 package/OperationDefinition-Questionnaire-populate.json]:

| Parameter | Card. | Type | Notes |
| --- | --- | --- | --- |
| `identifier` | 0..1 | Identifier | |
| `questionnaire` | 0..1 | uri, Reference or Questionnaire | One polymorphic parameter in 4.0.0 |
| `subject` | 0..1 | Reference | 1..1 in 3.0.0 |
| `context` | 0..* | `name` string 1..1, `content` Reference or Resource 1..* | `name` "SHALL correspond to a launchContext or variable declared at the root" |
| `dataEndpoint` | 0..1 | uri, Reference or Endpoint | |
| `data` | 0..1 | Bundle | |
| `local` | 0..1 | boolean | |
| `response` (out) | 1..1 | QuestionnaireResponse | |
| `issues` (out) | 0..1 | OperationOutcome | |

- `context.name` is a **string** matching the launchContext code (`patient`), not a Coding.
- SDC 3.0.0 had separate `canonical`, `questionnaireRef` and `launchContext` parameters. 4.0.0 merged them
  into `questionnaire` and `context`; some prose still says `questionnaireRef`
  [src: SDC-4.0.0 changes.html#4.0.0] [src: SDC-3.0.0 package/OperationDefinition-Questionnaire-populate.json].
- The response has "one item for every item in the source Questionnaire", with defaults and computed
  values as answers; SDC doesn't fix the response's status
  [src: SDC-4.0.0 package/OperationDefinition-Questionnaire-populate.json]. A response item has no
  `initial` [src: FHIR-R4 package/StructureDefinition-QuestionnaireResponse.json].
- With two out parameters, the result is a Parameters resource. A bare resource is returned only when the
  operation's single out parameter is named `return` [src: FHIR-R4 operations.html#response].

```json
{
  "resourceType": "Parameters",
  "parameter": [
    { "name": "subject", "valueReference": { "reference": "Patient/example" } },
    { "name": "context", "part": [
      { "name": "name", "valueString": "patient" },
      { "name": "content", "valueReference": { "reference": "Patient/example" } }
    ] }
  ]
}
```

## clinical-reasoning ($populate on HAPI FHIR)

What clinical-reasoning 4.16.0 does, from its code and the probes in `resources/probes/2026-11-14/` (run
on 4.13.0, and re-run on 4.16.0 in `resources/probes/2026-11-24/` with the same results except where
noted). Where it differs from SDC, content written for SDC can behave differently on a HAPI FHIR server.

**Operation.** The R4 provider accepts `subject` (string or Reference), `context`, `local`,
`useServerData`, `data` (or `bundle`) and `dataEndpoint`, `contentEndpoint` and `terminologyEndpoint`, and
returns the QuestionnaireResponse itself, not Parameters
[src: CR-4.16.0 cqf-fhir-cr-hapi/…/r4/questionnaire/QuestionnairePopulateProvider.java:64-89].

**The response** has id `<questionnaire id>-<subject id>`, `questionnaire` = `url|version`, status
`in-progress` and `authored` now. The Questionnaire is not contained
[src: CR-4.16.0 cqf-fhir-cr/…/populate/PopulateRequest.java:179-190]. Errors are issues in a contained
OperationOutcome referenced by a `cqf-messages` extension, not an `issues` parameter. Each item answered
from an expression gets the extension `questionnaireresponse-author`, a Reference to
`http://cqframework.org/fhir/Device/clinical-quality-language` [src: PROBES-2026-11-14 RESULTS.md §1].

**What it reads and ignores.**

| SDC feature | clinical-reasoning 4.16.0 |
| --- | --- |
| `initialExpression` | Yes. A `cqf-expression` on the item takes precedence over it [src: CR-4.16.0 cqf-fhir-cr/…/common/ExpressionProcessor.java:155-163] |
| static `initial` | Copied as answers [src: CR-4.16.0 cqf-fhir-cr/…/populate/ItemProcessor.java:213-239] |
| `itemPopulationContext` on a group | Yes: one group repetition per result, with `%<name>` bound in child expressions [src: PROBES-2026-11-14 RESULTS.md §1] |
| `launchContext` | Yes, matched to `context` by its `name` code (below) |
| `calculatedExpression`, `cqf-calculatedValue` | **No**: no answer [src: PROBES-2026-11-14 RESULTS.md §1] |
| `variable` | **No**: root variables aren't evaluated [src: CR-4.16.0 cqf-fhir-cr/…/populate/PopulateProcessor.java:30-45] |
| `enableWhen`, `enableWhenExpression` | **No**: disabled items are populated [src: PROBES-2026-11-14 RESULTS.md §1] |
| `candidateExpression`, `answerExpression` | Not read by the population code |
| Observation-based (`observationLinkPeriod`) | **No** [src: PROBES-2026-11-14 RESULTS.md §1] |
| `questionnaire-hidden` | Ignored: hidden items are populated like others [src: PROBES-2026-11-14 RESULTS.md §1] |

**Expressions all run as CQL.** `text/cql-expression` and `text/fhirpath` expressions are wrapped in a
generated CQL library as `define "return": <expression>`, with the Questionnaire's libraries included and
the parameters declared as `"%name"` [src: CR-4.16.0 cqf-fhir-utility/…/utility/CqfExpression.kt:64-82]
[src: CR-4.16.0 cqf-fhir-cql/…/cql/LibraryConstructor.kt:17-32]
[src: CR-4.16.0 cqf-fhir-cql/…/cql/LibraryConstructor.kt:63-99]. FHIRPath that is also valid CQL, such as
`%patient.name.given.first()`, works; where the two differ, CQL wins: `'abc'.matches('b')` gives false (a
partial match, true, in FHIRPath) [src: PROBES-2026-11-14 RESULTS.md §3].

**Which library.** A `text/cql-identifier` uses `Expression.reference` if present; otherwise the first
`cqf-library` library, in declaration order [src: CR-4.16.0 cqf-fhir-utility/…/utility/CqfExpression.kt:64-82]
[src: CR-4.16.0 cqf-fhir-utility/…/adapter/IKnowledgeArtifactAdapter.kt:264-273]. With PopRules then
OtherRules, both defining `"Given Name"`, 4.16.0 answered from PopRules [src: PROBES-2026-11-24 RESULTS.md §2].
4.13.0 (the VS Code CQL extension's version) held the libraries in an unordered map, so the choice was
arbitrary; its probe used the second one declared [src: PROBES-2026-11-14 RESULTS.md §4]. A qualified identifier
(`OtherRules."Given Name"`), as SDC requires with several libraries, fails: it is looked up as one name in
the chosen library [src: PROBES-2026-11-14 RESULTS.md §1]. With several libraries, write
`text/cql-expression` `OtherRules."Given Name"` (which works and conforms), or set `reference`.

**Subject and launch context.**

- The subject is the `content` of the `context` named `patient`; failing that, of the **first** `context`
  whatever its name; only then the `subject` parameter
  [src: CR-4.16.0 cqf-fhir-cr/…/populate/PopulateRequest.java:77-106]. Passing only an `encounter`
  context makes the Encounter the subject, and nothing is populated, with no error
  [src: PROBES-2026-11-14 RESULTS.md §2].
- A launchContext binds `%<code>` and the capitalised CQL parameter name (`Patient`) to the matching
  `context` content. Its `name` must be a Coding, and a launchContext without `name` or `type` is an error
  [src: CR-4.16.0 cqf-fhir-cr/…/common/InputParameterResolver.java:130-166].
- `%patient` resolves only when the request has a `context` named `patient`; with only `subject`, an
  expression using it fails to compile. `%subject` is never bound [src: PROBES-2026-11-14 RESULTS.md §2].
  In CQL, use the library's `Patient` context instead: it is always the subject.

**Answers.**

- Every result becomes an answer, even on a **non-repeating** item: a list of two values gives two answers
  [src: CR-4.16.0 cqf-fhir-cr/…/populate/ItemProcessor.java:201-211]. Return a single value for a
  non-repeating item (`First(…)`, `Last(…)`).
- Results are not converted to the item's type, except that a CodeableConcept becomes its first Coding,
  and an enumerated `code`, id or Identifier becomes a string
  [src: CR-4.16.0 cqf-fhir-cr/…/common/ItemValueTransformer.java:35-49]. So a FHIR `code` (such as
  `Patient.gender`) on a choice item gives `valueString`, and a String result on an integer item gives
  `valueString` [src: PROBES-2026-11-14 RESULTS.md §1]. Return a Coding or a System Code for choice items.
- A Resource result throws, and the whole top-level item is dropped from the response
  [src: PROBES-2026-11-14 RESULTS.md §5]. Return a Reference-typed value instead.
- A run-time error or an unknown definition leaves the item unanswered with an issue; a null leaves it
  unanswered with no issue [src: PROBES-2026-11-14 RESULTS.md §1].
- Children of a question are populated under its `answer.item` [src: PROBES-2026-11-14 RESULTS.md §1].
