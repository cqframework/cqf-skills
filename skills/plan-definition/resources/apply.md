# $apply: Specification and Reference Implementation

Baseline: FHIR R4 (4.0.1), CPG 2.0.0, FHIR R5, and clinical-reasoning 4.16.0 (the reference implementation, in HAPI FHIR; the VS Code CQL language server 5.0.0 uses 4.13.0, which differs where noted). Untagged statements hold at these versions only.
Sources: FHIR-R4, FHIR-R5, CPG-2.0.0, CR-4.16.0, PROBES-2026-11-14, PROBES-2026-11-24

What `PlanDefinition/$apply` should do, in R4, CPG 2.0.0 and R5, and what clinical-reasoning 4.16.0
actually does, verified by running it ([probes/2026-11-14/RESULTS.md](probes/2026-11-14/RESULTS.md), on
4.13.0, and [probes/2026-11-24/RESULTS.md](probes/2026-11-24/RESULTS.md), which re-ran them on 4.16.0
with the same results).
The specification's processing description "is not prescriptive"; where the implementation differs, the
difference is listed as a gotcha.

## Parameters and result, by specification

| | R4 | CPG 2.0.0 | R5 |
| --- | --- | --- | --- |
| Definition | `planDefinition` or instance | adds `url`, `version` | adds `url`, `version` |
| `subject` | 1..* string: Patient, Practitioner, Organization, Location, Device or Group | same | same |
| Context | `encounter`, `practitioner`, `organization` (string); `userType`, `userLanguage`, `userTaskContext`, `setting`, `settingContext` (**CodeableConcept**) | same | same |
| CQL parameters | none | `parameters` (Parameters) | none |
| Data | none | `useServerData` (default true), `data` (Bundle), `prefetchData` (key, descriptor, data), `dataEndpoint`, `terminologyEndpoint`, `artifactEndpointConfiguration` | none |
| Result | **CarePlan** 1..1, "a single activity represented by a RequestGroup" | **Bundle** 0..*, one per subject; transient | **Bundle** 0..*, first entry a RequestOrchestration; transient |

[src: FHIR-R4 plandefinition-operation-apply.html#12.18.9.1]
[src: CPG-2.0.0 OperationDefinition-cpg-plandefinition-apply.html]
[src: FHIR-R5 plandefinition-operation-apply.html#12.23.10.1]

`data` and `prefetchData` are exclusive in CPG; data comes from them first, then the server unless
`useServerData` is false, then `dataEndpoint`. A repeated entry in `parameters` becomes a CQL List.
CPG also adds `mergeNestedCarePlans`. No version of `$apply` returns a GuidanceResponse.

## Processing, by specification

R4 describes the steps [src: FHIR-R4 plandefinition.html#12.18.3.3]:

1. Create a CarePlan that `instantiates` the PlanDefinition, with its goals.
2. Create a RequestGroup and add it as the CarePlan's activity.
3. For each action, evaluate its applicability conditions; skip it unless they're all true.
4. For an applicable action, create a RequestGroup action with the same id; copy title, description,
   textEquivalent and timing; carry start and stop conditions forward.
5. If its definition is an ActivityDefinition, apply it and reference the result from the action
   (contained, or persisted), as an option. A PlanDefinition is applied in turn; a Questionnaire is set
   as the action's resource.
6. For a group action, process the children; choosing among them by the behaviors "may require input
   from a user".
7. Apply dynamicValues: the ActivityDefinition's, then the action's [src: FHIR-R4 plandefinition.html#12.18.3.4].

CPG makes the result transient ("none of the resources created by the operation are persisted"), with
the RequestGroup's intent `proposal` and every referenced request's intent `option`
[src: CPG-2.0.0 documentation-approach-09-methods-of-implementation.html#plandefinition-processing-semantics].

## What clinical-reasoning 4.16.0 does

### Operations and result

- **`$apply` returns a CarePlan** with a contained RequestGroup (status `active`, intent `proposal`) as
  its activity, the goals contained as Goal resources, and every generated request contained
  [src: CR-4.16.0 cqf-fhir-cr/…/plandefinition/apply/ApplyProcessor.java:92-101]
  [src: CR-4.16.0 cqf-fhir-cr/…/plandefinition/apply/ResponseBuilder.java:58-84]
  [src: PROBES-2026-11-14 RESULTS.md §1].
- **`$r5.apply`** is the CPG/R5-style variant. It returns a **Parameters** resource with a `return`
  part per subject, each a Bundle holding the RequestGroup and the generated resources as separate entries
  [src: CR-4.16.0 cqf-fhir-cr/…/plandefinition/PlanDefinitionProcessor.java:414-438]
  [src: CR-4.16.0 cqf-fhir-cr/…/plandefinition/apply/ApplyProcessor.java:103-122]
  [src: PROBES-2026-11-14 RESULTS.md §4]. On an R5 server, `$apply` goes this way
  [src: CR-4.16.0 cqf-fhir-cr/…/plandefinition/PlanDefinitionProcessor.java:286-305].
- **`$r5.apply` builds a Questionnaire from the actions' `input` profiles**: a group item per profile,
  with a child per required element (an input's `cpg-inputText` extension replaces the item's text),
  and a profile already in the Questionnaire isn't added again. When
  one action adds more than one item, 4.16.0 wraps them in a group whose text is the action's title (or
  description) and renumbers their linkIds under it (`2.1`, `2.1.1`…); 4.13.0 added them all at the top
  level. R4 `$apply` builds no Questionnaire
  [src: CR-4.16.0 cqf-fhir-cr/…/plandefinition/apply/ProcessAction.java:113-181]
  [src: PROBES-2026-11-24 RESULTS.md §2].
- **Parameters** accepted by the HAPI operation: the R4 set plus CPG's `parameters`, `useServerData`
  (default true), `data`, `prefetchData`, `dataEndpoint`, `contentEndpoint` and `terminologyEndpoint`
  [src: CR-4.16.0 cqf-fhir-cr-hapi/…/r4/plandefinition/PlanDefinitionApplyProvider.java:78-119]. `subject`
  is required, and a bare id is taken as `Patient/<id>`
  [src: CR-4.16.0 cqf-fhir-cr/…/plandefinition/PlanDefinitionProcessor.java:148-160].
- **`userType`, `userTaskContext`, `setting` and `settingContext` are accepted but unused**;
  `userLanguage` only sets `RequestGroup.language`, and `organization` the RequestGroup's author
  [src: CR-4.16.0 cqf-fhir-cr/…/plandefinition/apply/ResponseBuilder.java:58-84].
- The subject, encounter and practitioner are read from the data and passed to CQL as `%subject`,
  `%encounter` and `%practitioner` [src: CR-4.16.0 cqf-fhir-cr/…/common/InputParameterResolver.java:95-124].

### Expressions and libraries

- **The libraries** are the PlanDefinition's `library` entries plus any `cqf-library` extensions, keyed
  by the **last segment of the canonical** (`.../Library/ExampleRules` → `ExampleRules`)
  [src: CR-4.16.0 cqf-fhir-utility/…/adapter/r4/PlanDefinitionAdapter.kt:205-214].
- **Languages** [src: CR-4.16.0 cqf-fhir-utility/…/utility/CqfExpression.kt:64-82]:
  - `text/cql-expression`, `text/cql.expression`, `text/fhirpath`, and `text/cql` with a `.` in the
    expression and no `reference`, are wrapped in a generated CQL library (`define "return": <expression>`)
    that includes FHIRHelpers and the referenced libraries
    [src: CR-4.16.0 cqf-fhir-cql/…/cql/LibraryConstructor.kt:17-32].
  - **So `text/fhirpath` is run by the CQL engine, not a FHIRPath engine.** Where FHIRPath and CQL
    differ, it gets the CQL answer: `'abc'.matches('b')` is true in FHIRPath (partial matching) but false
    here [src: PROBES-2026-11-14 RESULTS.md §2].
  - **Anything else is a named expression**: `text/cql-identifier`, `text/cql` without a dot, and any
    unrecognised language, which isn't rejected [src: PROBES-2026-11-14 RESULTS.md §1]. It's looked up in
    the library `expression.reference` names, otherwise in **the first library** of the map, otherwise
    the call fails ("No Library reference found…").
  - The map holds `library` in declaration order, then any `cqf-library` extensions, so "first" is the
    first library declared [src: CR-4.16.0 cqf-fhir-utility/…/adapter/r4/PlanDefinitionAdapter.kt:205-214]
    [src: PROBES-2026-11-24 RESULTS.md §1]. In 4.13.0 the map was unordered, so which library was used
    wasn't defined [src: PROBES-2026-11-14 RESULTS.md §3]. Give `expression.reference` whenever a
    PlanDefinition has more than one library.

### Conditions

[src: CR-4.16.0 cqf-fhir-cr/…/plandefinition/apply/ProcessAction.java:62-81]
[src: CR-4.16.0 cqf-fhir-cr/…/plandefinition/apply/ProcessAction.java:183-233]

- **Only `applicability` conditions are evaluated**; `start` and `stop` are copied to the RequestGroup
  action without being evaluated, as the specification intends
  [src: CR-4.16.0 cqf-fhir-utility/…/adapter/IPlanDefinitionActionAdapter.kt:46-51].
- **Any condition false**: the action is dropped. A **non-Boolean** result counts as false.
- **All conditions true**: the action, its definition, its dynamicValues and its children are processed.
- **A condition null, or that throws, and none false**: the action is **kept** in the RequestGroup, but
  its definition, dynamicValues, extensions and child actions are **skipped**. The specification would
  drop it. An error is also recorded (below) [src: PROBES-2026-11-14 RESULTS.md §1].
- Each condition copied to the RequestGroup action carries a `cpg-action-condition-result` extension:
  the Boolean result, or a `data-absent-reason` of `asked-unknown` for null
  [src: CR-4.16.0 cqf-fhir-utility/…/adapter/r4/RequestActionAdapter.kt:148-168].
- **Children** are processed only when the parent's conditions are all true. A `cqf-applicabilityBehavior`
  extension of `any` on the parent stops at the first child that applies
  [src: CR-4.16.0 cqf-fhir-cr/…/plandefinition/apply/ProcessAction.java:83-111]
  [src: CR-4.16.0 cqf-fhir-utility/…/adapter/IPlanDefinitionActionAdapter.kt:76-98].

### Definitions, dynamicValues and behaviors

- **definitionCanonical** [src: CR-4.16.0 cqf-fhir-cr/…/plandefinition/apply/ProcessDefinition.java:107-111]:
  an ActivityDefinition is applied ([activitydefinition.md](activitydefinition.md)); a PlanDefinition is
  applied as a nested RequestGroup; **anything else, including a Questionnaire, is contained as is**
  [src: CR-4.16.0 cqf-fhir-cr/…/plandefinition/apply/ProcessDefinition.java:205-208]. A canonical that
  matches more than one resource fails the whole operation; give the version
  [src: CR-4.16.0 cqf-fhir-cr/…/plandefinition/apply/ProcessDefinition.java:145-152]. A generated
  resource's id is `<action id>-<definition id>`.
- **dynamicValue** [src: CR-4.16.0 cqf-fhir-cr/…/common/DynamicValueProcessor.java:94-134]: `%` is
  stripped from the path; a path starting `action.`, or any path on an action with no generated
  resource, sets the RequestGroup action (so `%action.description` and `action.description` both work);
  other paths set the generated resource. Paths are a small dotted subset, not full FHIRPath:
  `name[n]` with one digit, `extension('url')`
  [src: CR-4.16.0 cqf-fhir-utility/…/adapter/BaseAdapter.kt:118-129]. Expressions see `%context` (the
  definition), `%resource` (the generated resource) and `%action` (the RequestGroup action)
  [src: CR-4.16.0 cqf-fhir-cr/…/common/DynamicValueProcessor.java:138-169].
- **Copied to the RequestGroup action:** id, title, description, textEquivalent, the first code,
  documentation, timing, type, priority, `selectionBehavior`, conditions and relatedAction
  [src: CR-4.16.0 cqf-fhir-cr/…/plandefinition/apply/ProcessAction.java:235-260].
- **Not copied:** `groupingBehavior`, `requiredBehavior`, `precheckBehavior`, `cardinalityBehavior`,
  participant, trigger, reason, goalId, input and output. **No behavior is enforced**: every applicable
  child of an `exactly-one` group is in the result, for the consumer to choose from
  [src: PROBES-2026-11-14 RESULTS.md §1].
- **Goals** become Goal resources (lifecycle `proposed`) with the subject; their targets are copied, not
  evaluated [src: CR-4.16.0 cqf-fhir-cr/…/plandefinition/apply/ProcessGoal.java:49-71].

### Errors

Most failures are recorded, not thrown: the messages go into an OperationOutcome contained in the
RequestGroup (id `apply-outcome-<id>`), referenced by a `cqf-messages` extension on the RequestGroup and
the CarePlan [src: CR-4.16.0 cqf-fhir-cr/…/common/IOperationRequest.java:42-61]
[src: PROBES-2026-11-14 RESULTS.md §1]. Check for `cqf-messages` before trusting a result. Ambiguous
canonicals throw.

## Running $apply locally

`scripts/apply/` runs clinical-reasoning 4.16.0 on a folder in IG layout (`input/resources` for the
definitions and libraries, `input/tests` for the patient's data, `input/vocabulary`), the layout the VS
Code CQL extension uses. It needs Java 17+ and Maven:

```bash
scripts/apply/run.sh <project folder> plan <PlanDefinition id> Patient/<id>      # $apply
scripts/apply/run.sh <project folder> r5 <PlanDefinition id> Patient/<id>        # $r5.apply
scripts/apply/run.sh <project folder> activity <ActivityDefinition id> Patient/<id>
```

It prints the result as JSON. A Library's CQL must be in its `content` (base64 `data`), as in the probes
([probes/2026-11-14/input/](probes/2026-11-14/input/resources)). To check the CQL itself against the test
data first, use the VS Code CQL extension (the `vscode-cql` skill), which runs the same CQL engine family.
