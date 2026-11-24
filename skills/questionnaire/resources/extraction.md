# $extract and Questionnaire Generation

Baseline: SDC 4.0.0 on FHIR R4 (4.0.1); clinical-reasoning 4.16.0 for the reference implementation.
Sources: SDC-4.0.0, CR-4.16.0, PROBES-2026-11-14

How SDC turns a completed QuestionnaireResponse into other resources, what clinical-reasoning (HAPI FHIR)
does with `$extract`, and how it generates a Questionnaire from a profile.

## Extraction, as SDC defines it

Four methods: observation-based, definition-based, template-based and StructureMap-based
[src: SDC-4.0.0 extraction.html#design].

| Method | Questionnaire markup |
| --- | --- |
| Observation-based | `item.code` plus `sdc-questionnaire-observationExtract` (boolean, or in 4.0.0 a relationship code: `component`, `member`, `derived`, `independent`), on the item, an ancestor or the Questionnaire [src: SDC-4.0.0 extraction.html#obs-extract] |
| Definition-based | `item.definition` = `<profile canonical>[|version]#<element id>`, and `sdc-questionnaire-definitionExtract` on the Questionnaire or a group: a complex extension with `definition` (the profile, 1..1) and optional `fullUrl`, `ifNoneMatch`, `ifModifiedSince`, `ifMatch`, `ifNoneExist`. Fixed or computed values use `definitionExtractValue` [src: SDC-4.0.0 extraction.html#definition-extract] [src: SDC-4.0.0 package/StructureDefinition-sdc-questionnaire-definitionExtract.json] |
| Template-based (new in 4.0.0) | `sdc-questionnaire-templateExtract` pointing to a contained resource used as a template; FHIRPath only [src: SDC-4.0.0 extraction.html#template-extract] |
| StructureMap-based | `sdc-questionnaire-targetStructureMap` |

`sdc-questionnaire-itemExtractionContext`, the definition-based marker in SDC 3.0.0, is retired in 4.0.0
"in favor of the DefinitionExtract extension" [src: SDC-4.0.0 expressions.html#itemExtractionContext].

**Observation-based rules** [src: SDC-4.0.0 extraction.html#obs-extract]:

| Observation | From |
| --- | --- |
| `status` | `final` |
| `category` | inferred, or from `sdc-questionnaire-observation-extract-category` |
| `code` | all of `item.code` |
| `subject`, `encounter`, `basedOn`, `partOf` | the QuestionnaireResponse's |
| `effectiveDateTime`, `issued` | `QuestionnaireResponse.authored` |
| `performer` | `QuestionnaireResponse.author` |
| `value[x]` | the answer (a Quantity when the item has a `questionnaire-unit`) |
| `derivedFrom` | the QuestionnaireResponse |

Each answer is a separate Observation; unanswered items produce none; display items can't be extracted.

**$extract** (`QuestionnaireResponse/$extract` and `QuestionnaireResponse/[id]/$extract`): inputs
`questionnaire-response` and `questionnaire`, outputs `return` (a resource, or a transaction Bundle) and
`issues` [src: SDC-4.0.0 package/OperationDefinition-QuestionnaireResponse-extract.json].
Observation- and definition-based extraction "will always produce a 'transaction' Bundle", and the
operation doesn't store anything: the caller posts the Bundle
[src: SDC-4.0.0 extraction.html#output-expectations] [src: SDC-4.0.0 extraction.html#service].

## clinical-reasoning ($extract on HAPI FHIR)

**Operation.** `QuestionnaireResponse/[id]/$extract` takes `questionnaire` (a resource), `parameters`,
`useServerData` and `data`; the type-level form adds `questionnaire-response`
[src: CR-4.16.0 cqf-fhir-cr-hapi/…/r4/questionnaireresponse/QuestionnaireResponseExtractProvider.java:41-50].
Without `questionnaire`, it looks for a contained one, then the canonical in `QuestionnaireResponse.questionnaire`
[src: CR-4.16.0 cqf-fhir-cr/…/questionnaireresponse/QuestionnaireResponseProcessor.java:73-100].

**Result.** A transaction Bundle `extract-<response id>`; every entry is a POST, with no `fullUrl`
[src: CR-4.16.0 cqf-fhir-cr/…/extract/ExtractProcessor.java:38-70]. Errors aren't reported as `issues`: the
operation throws [src: PROBES-2026-11-14 RESULTS.md §6].

**Method choice.** If the Questionnaire or response root has `definitionExtract` or
`itemExtractionContext`, the whole response becomes one definition-based resource; otherwise each item is
extracted on its own: definition-based if it has those extensions or a `definition`, observation-based
otherwise [src: CR-4.16.0 cqf-fhir-cr/…/extract/ExtractProcessor.java:38-70]. Template- and
StructureMap-based extraction aren't implemented.

**Observation-based**, and how it differs from SDC:

- `observationExtract` is **not checked**: every answered item with a `code` becomes an Observation
  [src: CR-4.16.0 cqf-fhir-cr/…/extract/ProcessItem.java:20-58] [src: PROBES-2026-11-14 RESULTS.md §6].
  To keep an item out, leave out its `code`.
- The default category has the system **`http://hl7.org/fhir/observation-category`**, not R4's
  `http://terminology.hl7.org/CodeSystem/observation-category`
  [src: CR-4.16.0 cqf-fhir-utility/…/utility/Constants.kt:182-185]; an
  `observation-extract-category` extension is read from the response item, not the Questionnaire item
  [src: CR-4.16.0 cqf-fhir-cr/…/extract/ProcessItem.java:20-58].
- The other fields follow SDC: status `final`, subject, encounter, basedOn, partOf, effective and issued
  from `authored`, performer from `author`, derivedFrom the response. Each Observation has id
  `extract-<response id>.<linkId>` and an extension
  `http://hl7.org/fhir/uv/sdc/StructureDefinition/derivedFromLinkId` (not defined in SDC 4.0.0)
  [src: CR-4.16.0 cqf-fhir-cr/…/extract/ObservationResolver.java:44-81].
- A repeating item's answers become Observations with the **same id**
  [src: PROBES-2026-11-14 RESULTS.md §6].
- The answer is copied as the value, apart from Coding (to CodeableConcept), date (to dateTime), and a
  decimal or integer on an item with `questionnaire-unit` (to Quantity)
  [src: CR-4.16.0 cqf-fhir-cr/…/extract/ObservationResolver.java:83-116]. A **decimal** answer without a
  unit gives `valueDecimal`, which R4 Observation doesn't allow: HAPI then can't serialize the Bundle
  [src: PROBES-2026-11-14 RESULTS.md §6]. Give extracted decimal items a `questionnaire-unit`, or make
  them `quantity` items.
- An answer with nested items isn't extracted itself; its children are
  [src: CR-4.16.0 cqf-fhir-cr/…/extract/ProcessItem.java:20-58].
- Without the Questionnaire, extraction throws ("Unable to retrieve Questionnaire code map")
  [src: PROBES-2026-11-14 RESULTS.md §6].

**Definition-based**, and how it differs from SDC:

- `definitionExtract` and `itemExtractionContext` are read only as **primitive** values: a profile URL
  (containing `/`) or a resource type [src: CR-4.16.0 cqf-fhir-cr/…/extract/ProcessDefinitionItem.java:142-159].
  The SDC 4.0.0 complex form throws "Unable to retrieve definition for item"
  [src: PROBES-2026-11-14 RESULTS.md §6]. For this server, write SDC 3.0.0's
  `itemExtractionContext` with `valueCode` (a resource type) or a canonical.
- The resource is POSTed; `fullUrl`, conditional and update options aren't supported, and the subject
  isn't set: the probe's AllergyIntolerance had no `patient` [src: PROBES-2026-11-14 RESULTS.md §6]. Set
  it with a `definitionExtractValue` or an item whose `definition` is the subject element.
- The profile is looked up in the server; for a base resource, the base StructureDefinition must be there
  [src: PROBES-2026-11-14 RESULTS.md §6].
- `$extract` doesn't use the Questionnaire's `cqf-library`
  [src: CR-4.16.0 cqf-fhir-cr/…/extract/ExtractRequest.java:56-61], so a CQL `definitionExtractValue`
  needs `Expression.reference`. `text/fhirpath` runs on HAPI's FHIRPath engine against the response.

## Questionnaire generation

clinical-reasoning's `StructureDefinition/$questionnaire` (type level only) takes `resource` (a
StructureDefinition), `url` (profile urls), `supportedOnly`, `minimalOnly`, `contentEndpoint` and
`terminologyEndpoint`, and returns a Questionnaire
[src: CR-4.16.0 cqf-fhir-cr-hapi/…/r4/structuredefinition/StructureDefinitionQuestionnaireProvider.java:45-56].
For a profile it makes one group item (`definition` the profile url) with a child per element:

- `definition` `<profile url>#<element id>`, `required` from `min > 0`, `repeats` from `max`, `text` the
  element's label, short or path, and type from the element type.
- Elements with a fixed or pattern value get no item: they are applied at extraction.
- The group carries `definitionExtract` as a canonical (SDC 3.0.0 style), in the probe twice.

[src: PROBES-2026-11-14 RESULTS.md §7]

In the probe, with both flags false, only the required elements of a differential-only profile became
items; a mustSupport `note` didn't [src: PROBES-2026-11-14 RESULTS.md §7]. PlanDefinition `$r5.apply`
uses the same generator for action `input` profiles, and from 4.16.0 groups an action's items when it
has more than one (see the `plan-definition` skill).
