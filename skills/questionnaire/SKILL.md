---
name: questionnaire
description: Author, review, populate and extract FHIR R4 Questionnaires and QuestionnaireResponses — items, enableWhen, answerOption and answerValueSet, SDC 4.0.0 expressions (launchContext, variable, initialExpression, calculatedExpression, itemPopulationContext), CQL libraries, $populate, $extract and Questionnaire generation — as R4 and SDC define them and as the clinical-reasoning reference implementation (HAPI FHIR) actually runs them. Includes a script to run $populate and $extract locally. Use for writing or explaining Questionnaires, choosing expression languages, and predicting or debugging $populate and $extract results.
license: Apache-2.0
---

# Questionnaire and SDC

A Questionnaire is a form definition; a QuestionnaireResponse holds the answers. Structured Data Capture
(SDC) adds expressions that compute answers, a `$populate` operation that pre-fills a response from the
patient's record, and a `$extract` operation that turns answers into resources. This skill covers them in
three layers that don't always agree: FHIR R4, SDC 4.0.0, and clinical-reasoning, the implementation in
HAPI FHIR.

Related skills: `cql` (the language), `cql-ig` and `crmi` (packaging CQL as a Library), `plan-definition`
(PlanDefinitions whose actions reference Questionnaires), `cpg` (CPG's Questionnaire profiles), `fhir`
(base R4 element tables), `fsh` (authoring Questionnaires as FSH instances). Payer forms for prior
authorization (Da Vinci DTR) build on SDC, but DTR's rules are not covered here.

## Versions

| Source | Version |
| --- | --- |
| FHIR | R4 4.0.1 (with R5 where Questionnaire changed) |
| SDC | 4.0.0 (STU4, for R4), with what changed from 3.0.0 |
| clinical-reasoning (`cqf-fhir-cr`) | 4.16.0 (2026-11-21); cql-language-server 5.0.0, in the VS Code CQL extension, still uses 4.13.0 (see below) |

## When the Implementation Version Differs

Behavior of the reference implementation is cited to its code at 4.16.0 (the `CR-4.16.0` citations) and
checked by running it (`resources/probes/2026-11-14/` on 4.13.0, re-run on 4.16.0 in
`resources/probes/2026-11-24/`). Every 2026-11-14 probe gave the same result on 4.16.0 but one: with
several `cqf-library` libraries and no `Expression.reference`, 4.16.0 uses the first declared, where
4.13.0 (and so the VS Code CQL extension 1.0.0) picks one arbitrarily. For another release:

1. Find the server's `cqf-fhir-cr` version (for HAPI FHIR, its release notes or dependencies).
2. Read the cited code at that tag on GitHub ([SOURCES.md](resources/SOURCES.md)), finding it by content
   near the cited lines; or change the version in `scripts/sdc/pom.xml` and run the content locally.
3. Answer from that version, saying so.

## Quick Reference

```json
{
  "resourceType": "Questionnaire",
  "url": "http://example.org/fhir/Questionnaire/intake",
  "version": "1.0.0",
  "name": "Intake",
  "status": "active",
  "subjectType": ["Patient"],
  "extension": [
    { "url": "http://hl7.org/fhir/StructureDefinition/cqf-library",
      "valueCanonical": "http://example.org/fhir/Library/IntakeLogic|1.0.0" },
    { "url": "http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire-launchContext",
      "extension": [
        { "url": "name", "valueCoding": { "system": "http://hl7.org/fhir/uv/sdc/CodeSystem/launchContext", "code": "patient" } },
        { "url": "type", "valueCode": "Patient" } ] }
  ],
  "item": [{
    "linkId": "weight",
    "text": "Body weight",
    "type": "quantity",
    "code": [{ "system": "http://loinc.org", "code": "29463-7" }],
    "extension": [{
      "url": "http://hl7.org/fhir/uv/sdc/StructureDefinition/sdc-questionnaire-initialExpression",
      "valueExpression": { "language": "text/cql-identifier", "expression": "Last Weight" }
    }]
  }, {
    "linkId": "smoker", "text": "Do you smoke?", "type": "boolean"
  }, {
    "linkId": "packs", "text": "Packs per day", "type": "integer",
    "enableWhen": [{ "question": "smoker", "operator": "=", "answerBoolean": true }]
  }]
}
```

- **Items:** every item has a unique `linkId` and a `type`. Questions may have child items, not only
  groups; display items can't. R4 has `choice` and `open-choice`; R5 replaces them with `coding`.
- **enableWhen:** with more than one condition, set `enableBehavior` (`all` or `any`); `exists` takes
  `answerBoolean`. A disabled item stores no answers.
- **Expressions:** `text/cql-identifier` names a definition in a `cqf-library`; `text/cql-expression` is
  inline CQL; `text/fhirpath` is FHIRPath. With more than one library, qualify CQL names (`Lib."Def"`).
- **Calculated answers** use `sdc-questionnaire-calculatedExpression`; `cqf-calculatedValue` isn't used in
  SDC 4.0.0.
- **`$populate`** takes `subject` and `context` parts with a string `name` matching a launchContext code
  (`patient`) and a `content` Reference, and returns a QuestionnaireResponse with answers, never `initial`.
- **`$extract`** returns a transaction Bundle for observation- and definition-based extraction; it stores
  nothing.

## Known Gotchas

In clinical-reasoning 4.16.0 (each verified by running it):

- **Every expression runs as CQL**, `text/fhirpath` included: FHIRPath that is also CQL works, but
  FHIRPath semantics (such as partial `matches`) don't hold.
- **`%patient` needs a `context` named `patient`** in the request, and `%subject` is never bound. In a CQL
  library, use the `Patient` context, which is always the subject.
- **The first `context` becomes the subject** when none is named `patient`, overriding `subject`: an
  `encounter` context alone yields an empty response with no error.
- **A qualified `text/cql-identifier` (`Lib."Def"`) fails**, and with several libraries an unqualified
  one uses the first library declared (an arbitrary one in 4.13.0). Use `text/cql-expression`
  `Lib."Def"`, or `Expression.reference`.
- **A list result gives several answers even on a non-repeating item**; results aren't converted to the
  item's type (a FHIR `code` gives `valueString` on a choice item); a Resource result drops the whole item.
- **Not implemented in `$populate`:** `calculatedExpression`, `variable`, `enableWhen` (disabled items are
  populated), `enableWhenExpression`, `candidateExpression`, `answerExpression` and observation-based
  population.
- **`$extract` ignores `observationExtract`**: every answered coded item becomes an Observation. A decimal
  answer without a `questionnaire-unit` makes an invalid `valueDecimal`; repeated answers get the same
  Observation id; the default category uses the old system `http://hl7.org/fhir/observation-category`.
- **SDC 4.0.0's complex `definitionExtract` makes `$extract` throw**; the implementation reads only a
  primitive `definitionExtract` or `itemExtractionContext`, and doesn't set the subject.
- **Errors in `$populate`** are issues in a contained OperationOutcome (a `cqf-messages` extension), and
  the item is left unanswered; `$populate` returns the bare QuestionnaireResponse, not Parameters.

In the specifications:

- **An empty result is "not answered"**, and a result must fit the item's type, with three exceptions
  (Resource to Reference, Quantity to a number with a unit, code to Coding).
- **que-12's R4 expression only fires for three or more enableWhens**; the rule applies from two.
- **`$populate` changed in SDC 4.0.0**: one `questionnaire` parameter, no `launchContext` parameter,
  `subject` optional. The `launchContext` codes gained `clinical`.
- **itemExtractionContext is retired** in SDC 4.0.0 in favor of `definitionExtract`.

## Running $populate and $extract Locally

`scripts/sdc/run.sh` runs clinical-reasoning 4.16.0 on a folder in IG layout (`input/resources/` for the
Questionnaire, Libraries with CQL in `Library.content` and profiles; `input/tests/` for patient data and
QuestionnaireResponses) and prints the result. It needs Java 17+ and Maven; the first run downloads the
dependencies.

```sh
scripts/sdc/run.sh <project> populate <Questionnaire id> Patient/<id> [patient=Patient/<id> ...]
scripts/sdc/run.sh <project> extract <QuestionnaireResponse id>
scripts/sdc/run.sh <project> generate <StructureDefinition id>
```

Each `name=Type/id` becomes a `$populate` `context` parameter. Pass `patient=Patient/<id>` when the
Questionnaire uses `%patient`. If the output starts with `THROWS` or `INVALID`, the operation failed or
produced a resource HAPI can't serialize.

## Supporting Files

| File | Contents |
| --- | --- |
| [resources/questionnaire.md](resources/questionnaire.md) | Item types, invariants, answerOption and answerValueSet, enableWhen, QuestionnaireResponse rules |
| [resources/population.md](resources/population.md) | SDC extensions, expression languages, libraries, launch context, `$populate`, and what clinical-reasoning does |
| [resources/extraction.md](resources/extraction.md) | Extraction methods, `$extract`, what clinical-reasoning does, Questionnaire generation |
| [resources/SOURCES.md](resources/SOURCES.md) | The pinned sources and how to read a citation |
| [resources/probes/2026-11-14/](resources/probes/2026-11-14/RESULTS.md) | The probe project and what the operations returned for it (4.13.0) |
| [resources/probes/2026-11-24/](resources/probes/2026-11-24/RESULTS.md) | The same probes on 4.16.0, compared with 4.13.0 |
| [scripts/sdc/](scripts/sdc/run.sh) | Runs `$populate`, `$extract` and generation with clinical-reasoning 4.16.0 (Java 17+, Maven) |

For maintainers: `scripts/fetch-sources.sh` caches the clinical-reasoning clone,
`scripts/lint_skill_questionnaire.py` checks citations, and `scripts/check_release.py` reports which
citations a new release touches.
