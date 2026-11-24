# plan-definition Skill Test Questions: Answer Key

Expected answers for [questions.md](questions.md). Don't give this file to an agent under test.

Facts are as the `plan-definition` skill records them for FHIR R4, CPG 2.0.0 and clinical-reasoning
4.16.0 (checked by running it). Several contradict the skill's original source; those are marked.

## Expressions and libraries

### EX-01. Language codes

- **Expected:** not an R4 code: R4's are `text/cql`, `text/fhirpath` and `application/x-fhir-query`, and
  `text/cql` covers both inline CQL and a named expression. `text/cql-identifier` (a named expression)
  and `text/cql-expression` (inline) come from R4B and R5. The binding is extensible and CPG uses them,
  so they're fine on R4. The reference implementation treats `text/cql-identifier` as a named expression.
- **Pass if:** not an R4 code but usable; text/cql is both in R4.
- **Fail if:** it says R4 `text/cql` means inline only (the original source's claim).
- **Skill:** `resources/plandefinition.md` (Expressions and libraries).

### EX-02. Two libraries

- **Expected:** the first library declared in `library`: with no `reference`, the server uses the first
  library in declaration order (4.13.0 picked one arbitrarily). Still set `expression.reference` to the
  intended library's canonical (or keep one library, as CPG requires). The spec says to qualify
  (`"Lib".Expr`) with several libraries and to reference at most one.
- **Pass if:** the first declared, and use `reference` or one library. **Partial if:** "undefined" (the
  4.13.0 behaviour) with the same advice.
- **Skill:** `resources/apply.md` (Expressions and libraries).

### EX-03. FHIRPath

- **Expected:** clinical-reasoning evaluates `text/fhirpath` by wrapping it in a CQL library, so it gets
  CQL semantics: `matches` is a whole-string match on the CQL engine, a partial match in FHIRPath.
- **Pass if:** run by the CQL engine.
- **Skill:** `resources/apply.md`.

## Conditions and behaviors

### CO-01. A null condition

- **Expected:** that's the implementation: a null (or failing) applicability condition, with none false,
  keeps the action but skips its definition, dynamicValues and children. Only false drops it. Make the
  CQL return false rather than null (e.g. handle missing data), and check `cqf-messages` for errors.
- **Pass if:** null keeps the action without its definition.
- **Skill:** `resources/apply.md` (Conditions).

### CO-02. Start conditions

- **Expected:** only `applicability` decides inclusion; `start` and `stop` conditions are carried to the
  RequestGroup action, to be evaluated later, as the spec says.
- **Pass if:** start isn't evaluated at apply time.
- **Skill:** `resources/plandefinition.md` (Conditions).

### BE-01. Exactly one

- **Expected:** nothing: behaviors aren't enforced by `$apply`; the RequestGroup offers every applicable
  child and copies `selectionBehavior`, for the consumer (a person or UI) to choose. The other behaviors
  aren't even copied by clinical-reasoning.
- **Pass if:** behaviors describe the choice, not filter it.
- **Skill:** `resources/apply.md`, `resources/plandefinition.md` (Behaviors).

### BE-02. Optional choice

- **Expected:** a group action with `selectionBehavior: at-most-one` and `requiredBehavior: could`, the
  three orders as children.
- **Pass if:** at-most-one on the group, optional.
- **Fail if:** selectionBehavior on the children.
- **Skill:** `resources/plandefinition.md` (Behaviors).

## dynamicValue

### DV-01. A path

- **Expected:** no; the path is relative to the generated resource: `priority`.
- **Fail if:** it accepts the type-prefixed path (the original source's example).
- **Skill:** `resources/plandefinition.md` (dynamicValue).

### DV-02. The card text

- **Expected:** a dynamicValue with path `%action.description` (or `action.description`, which
  clinical-reasoning also accepts), or `action.title`.
- **Skill:** `resources/plandefinition.md`, `resources/apply.md`.

## $apply

### AP-01. The result

- **Expected:** R4: a CarePlan whose activity is a RequestGroup. CPG 2.0.0: a Bundle per subject,
  transient. HAPI `$apply`: a CarePlan with the RequestGroup and generated resources contained.
  `$r5.apply`: a Parameters resource with a `return` Bundle per subject.
- **Fail if:** a GuidanceResponse.
- **Skill:** `resources/apply.md`.

### AP-02. GuidanceResponse

- **Expected:** no. No version of `$apply` returns a GuidanceResponse; data-required is a GuidanceResponse
  status for decision-support services, not an `$apply` result.
- **Fail if:** yes (the original source's claim).
- **Skill:** SKILL.md (Quick Reference), `resources/apply.md`.

### AP-03. Errors

- **Expected:** in an OperationOutcome contained in the RequestGroup (`apply-outcome-<id>`), referenced by
  `cqf-messages` extensions on the RequestGroup and CarePlan. A failing condition keeps the action
  without its resource.
- **Skill:** `resources/apply.md` (Errors).

### AP-04. Context parameters

- **Expected:** clinical-reasoning 4.16.0 accepts them but doesn't use them; they never reach the CQL.
  (They're CodeableConcepts.) Pass what the CQL needs in `parameters`, a CPG addition the server supports.
- **Pass if:** ignored, and use `parameters`.
- **Skill:** `resources/apply.md`.

## ActivityDefinition

### AD-01. Status and intent

- **Expected:** R4 says the created resource is `draft`, and within a RequestGroup the requests are
  options (CPG: intent `option`). clinical-reasoning sets `active`, and `order` unless `intent` is given.
  Set `intent` on the ActivityDefinition (e.g. `proposal`), and status with a dynamicValue if needed.
- **Skill:** `resources/activitydefinition.md`.

### AD-02. dynamicValue library

- **Expected:** an ActivityDefinition's dynamicValues are evaluated with the ActivityDefinition's own
  `library`, not the PlanDefinition's. Add `library` to the ActivityDefinition.
- **Skill:** `resources/activitydefinition.md`.

## Triggers

### TR-01. Trigger types

- **Expected:** `named-event` (e.g. the CDS Hooks `order-select` or `order-sign` hook) or a data trigger
  such as `data-added`. There's no `data-requested`. How a trigger causes `$apply` isn't specified.
- **Fail if:** it accepts `data-requested` (the original source's list).
- **Skill:** `resources/plandefinition.md` (Triggers and relatedAction).

## Versions

### VR-01. An older version

- **Expected:** no: in 4.13.0 the libraries are held in an unordered map, so which library an
  unqualified expression uses isn't defined (the 2026-11-14 probe happened to get the first); from
  4.16.0 it is the first declared. Set `reference` so the content behaves the same in both.
- **Pass if:** not guaranteed in 4.13.0, and set `reference`.
- **Skill:** SKILL.md (When the Implementation Version Differs).

## Task

### TK-01. An HbA1c follow-up rule

Run `python grade_plandefinition.py <answer>/tk-01`. It checks:

- one PlanDefinition, ActivityDefinition and Library;
- the PlanDefinition: url, version, `active`, type `eca-rule`, exactly one library that resolves, one
  action with applicability conditions, `definitionCanonical` to the ActivityDefinition, a dynamicValue
  on `action.description`, relative paths;
- the expressions: named (`text/cql-identifier` or `text/cql`) and defined in the Library, whose CQL is in
  its content, retrieves HbA1c Observations, looks back 6 months and is limited to adults;
- the ActivityDefinition: ServiceRequest, LOINC 4548-4, a proposing intent, its own library if it has
  dynamicValues, url and version;
- the test data: two patients and an HbA1c Observation.

For a full check, run the skill's `scripts/apply/run.sh <answer>/tk-01 plan <PlanDefinition id>
Patient/<id>` for each patient: the patient who needs the test gets a ServiceRequest and the reason on the
action; the other gets an empty RequestGroup; neither has `cqf-messages`.

- **Pass if:** every check passes. **Partial if:** one fails.
- **Reference:** [reference/tk-01/](reference/tk-01/), run with clinical-reasoning 4.13.0 on 2026-11-14, and
  with 4.16.0 on 2026-11-24 with the same results:
  `Patient/due` gets the ServiceRequest (intent `proposal`); `Patient/recent` (HbA1c on 2026-11-01) gets
  none. The recent result stays within 6 months until 2027-05-01.
