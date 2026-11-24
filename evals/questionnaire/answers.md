# questionnaire Skill Test Questions: Answer Key

Expected answers for [questions.md](questions.md). Don't give this file to an agent under test.

Facts are as the `questionnaire` skill records them for FHIR R4, SDC 4.0.0 and clinical-reasoning
4.16.0 (checked by running it). Several contradict the skill's original source; those are marked.

## Structure

### ST-01. Nesting

- **Expected:** yes: questions can have child items; only `display` items can't (que-1). In the response,
  a question's children go under each `answer.item`; a group's children go directly under `item`.
- **Pass if:** yes, under `answer.item`.
- **Fail if:** only groups can have children (the original source's claim).
- **Skill:** `resources/questionnaire.md` (Items, QuestionnaireResponse).

### ST-02. Two conditions

- **Expected:** no: `enableBehavior` is required with more than one `enableWhen`. R4's que-12 expression
  tests `count() > 2`, so a validator only flags three or more; R5 fixes it.
- **Pass if:** invalid, with the que-12 explanation. **Partial if:** invalid without the explanation.
- **Skill:** `resources/questionnaire.md` (Invariants).

### ST-03. A default choice

- **Expected:** no: with `answerOption`, `initial` must be absent (que-11). Set `initialSelected: true` on
  the option.
- **Pass if:** `initialSelected`.
- **Skill:** `resources/questionnaire.md` (Invariants).

### ST-04. R5

- **Expected:** R5 replaces both with `coding` plus `answerConstraint` (`optionsOnly`, the default,
  `optionsOrType`, `optionsOrString`; open-choice becomes `optionsOrString`). SDC 4.0.0 offers
  `answerConstraint` in R4 as a cross-version extension.
- **Pass if:** `coding` and `answerConstraint`.
- **Skill:** `resources/questionnaire.md` (Items).

## Expressions

### EX-01. A calculated field

- **Expected:** `sdc-questionnaire-calculatedExpression`. `cqf-calculatedValue` isn't used in SDC 4.0.0
  (replaced by `cqf-expression`), and in R4 its value is a string. A user may override a calculated value,
  after which it "SHOULD no longer be changed". clinical-reasoning's `$populate` doesn't evaluate
  `calculatedExpression`; a form filler does.
- **Pass if:** calculatedExpression, and the user can override.
- **Fail if:** cqf-calculatedValue, or "the user can't override" (both the original source's claims).
- **Skill:** `resources/population.md` (Extensions).

### EX-02. Two libraries

- **Expected:** SDC: with more than one library in scope, qualify CQL identifiers with the library name:
  `OtherLib."Given Name"`. On the server, a qualified `text/cql-identifier` fails (looked up as one name
  in one library), and an unqualified one uses the first library declared (an arbitrary one in 4.13.0).
  What works there and conforms:
  `text/cql-expression` `OtherLib."Given Name"`, or `Expression.reference` to the library.
- **Pass if:** qualify per SDC, and on the server use cql-expression or `reference`.
- **Skill:** `resources/population.md` (Expression languages; clinical-reasoning).

### EX-03. %patient

- **Expected:** the server binds `%patient` only when the `$populate` request has a `context` named
  `patient` with the patient as `content`; with only `subject`, the expression fails to compile. Pass the
  context. Also note the server runs `text/fhirpath` as CQL. (`%subject` is never bound.)
- **Pass if:** pass a `patient` context.
- **Skill:** `resources/population.md` (Subject and launch context).

### EX-04. Launch contexts

- **Expected:** `patient`, `encounter`, `location`, `user`, `study` and, new in 4.0.0, `clinical` (which
  may be a collection); the binding is extensible.
- **Pass if:** includes `clinical`. **Partial if:** the five 3.0.0 codes only (the original source's list).
- **Skill:** `resources/population.md` (Variables and launch context).

## $populate

### PO-01. The request

- **Expected:** a `context` parameter with parts `name` (a **string**, `patient`, matching the
  launchContext code) and `content` (a Reference or the resource). Not a Coding, and not Da Vinci's
  context codes.
- **Pass if:** `name` string `patient`, `content` Reference.
- **Fail if:** `name` as a Coding (the original source's example).
- **Skill:** `resources/population.md` ($populate).

### PO-02. The response

- **Expected:** `answer`. A QuestionnaireResponse item has no `initial`.
- **Pass if:** answer only.
- **Fail if:** "answer or initial" (the original source's claim).
- **Skill:** `resources/population.md` ($populate).

### PO-03. Two answers

- **Expected:** the server makes every result an answer, whatever `repeats` says, so a list result gives
  several answers. SDC says too many results may be left unpopulated, treated as candidates, or flagged.
  Make the definition return one value (`First`, `Last`, `singleton from`).
- **Pass if:** the expression returns a list; return one value.
- **Skill:** `resources/population.md` (Answers).

### PO-04. A gender question

- **Expected:** the server doesn't convert results to the item's type, and turns an enumerated FHIR
  `code` into a string. Return a Coding or a System Code (`Code { system: …, code: … }`) for a choice
  item. (SDC allows a code for a coding item only when it resolves uniquely.)
- **Pass if:** return a Coding/Code.
- **Skill:** `resources/population.md` (Answers).

### PO-05. Disabled items

- **Expected:** no: SDC says no answers are stored for non-enabled content. The server's `$populate`
  ignores `enableWhen` (and `enableWhenExpression`), so disabled items are populated; the form filler or
  the content has to handle it.
- **Pass if:** not per SDC; the server ignores enableWhen.
- **Skill:** `resources/population.md` (What it reads and ignores).

### PO-06. An encounter

- **Expected:** the server takes the subject from the `context` named `patient`, else from the **first**
  `context`, before `subject`. With only an `encounter` context, the Encounter becomes the subject, CQL's
  Patient context finds nothing, and no error is reported. Pass a `patient` context too (first), or drop
  the encounter context.
- **Pass if:** the first context becomes the subject.
- **Skill:** `resources/population.md` (Subject and launch context).

### PO-07. Observation-based population

- **Expected:** no: the server doesn't implement observation-based population. Use an `initialExpression`
  that returns the latest Observation's value.
- **Pass if:** no, use an expression.
- **Skill:** `resources/population.md` (What it reads and ignores).

## $extract

### XT-01. Unwanted Observations

- **Expected:** the server doesn't check `observationExtract`: every answered item with a `code` becomes
  an Observation. Remove `code` from items that shouldn't be extracted (SDC needs `observationExtract`).
- **Pass if:** the flag is ignored; remove the code.
- **Skill:** `resources/extraction.md` (Observation-based).

### XT-02. A failing extract

- **Expected:** the decimal answer is copied as `valueDecimal`, which R4 Observation doesn't allow, so
  HAPI can't serialize the Bundle. Add a `questionnaire-unit` to the item (the value becomes a Quantity),
  or use a `quantity` item.
- **Pass if:** valueDecimal isn't allowed; add a unit or use quantity.
- **Skill:** `resources/extraction.md` (Observation-based).

### XT-03. definitionExtract

- **Expected:** the server reads `definitionExtract` and `itemExtractionContext` only as primitive
  values: a profile canonical or a resource type (SDC 3.0.0 style). Use `itemExtractionContext` with a
  `valueCode` (or a canonical) for that server; it also won't set the subject.
- **Pass if:** primitive only; use the 3.0.0 form.
- **Skill:** `resources/extraction.md` (Definition-based).

### XT-04. Saving

- **Expected:** no: `$extract` returns a transaction Bundle (POST entries on the server); the caller
  posts it.
- **Pass if:** no.
- **Skill:** `resources/extraction.md` (Extraction, as SDC defines it).

## Versions

### VR-01. A newer server

- **Expected:** the skill's behavior is cited to 4.16.0 code; read the same files at the v4.17.0 tag on
  GitHub (finding the code by content), or change the version in `scripts/sdc/pom.xml` and re-run the
  probes or the content (`run.sh` downloads the new version). The 2026-11-24 probes show how: every
  2026-11-14 probe re-run on the new version and compared.
- **Pass if:** check the cited code at that version or run it.
- **Skill:** `SKILL.md` (When the Implementation Version Differs).

## Task

### TK-01. A pre-visit intake form

Run `python grade_questionnaire.py <answer>/tk-01`. It checks:

- one Questionnaire and a Library; url, version, `active`, subjectType Patient; unique linkIds;
  enableWhen rules; an integer item enabled when smoking is true; no initialExpression on groups or
  alongside `initial`;
- one `cqf-library` that resolves; a `patient` launchContext (valueCoding, SDC system, type Patient); CQL
  in the Library's content; only the three expression languages; every `text/cql-identifier` defined in
  the Library and unqualified; no `%subject`; no `cqf-calculatedValue`;
- the weight item: quantity, LOINC 29463-7, `observationExtract`, not repeating, pre-filled from a
  definition that returns one value; a repeating group with a named itemPopulationContext whose children
  use `%<name>`; no other coded item (the server would extract it);
- the test data: a patient, two weights, two conditions, and a completed response for the Questionnaire
  whose linkIds exist and that has no item with both `answer` and `item`.

For a full check, run the skill's `scripts/sdc/run.sh <answer>/tk-01 populate <Questionnaire id>
Patient/<id> patient=Patient/<id>`: the name, the latest weight and one group per active condition are
filled in, with no `cqf-messages`; then `extract <QuestionnaireResponse id>`: one weight Observation, and
nothing else.

- **Pass if:** every check passes and both runs behave. **Partial if:** one check fails.
- **Reference:** [reference/tk-01/](reference/tk-01/), run with clinical-reasoning 4.13.0 on 2026-11-14, and
  with 4.16.0 on 2026-11-24 with the same results:
  `$populate` gives `Rae`, 79.4 kg (the later weight) and two condition groups (Migraine, Asthma; the
  resolved fracture is left out); `$extract` gives one Observation, `extract-intake-1-completed.weight`.
