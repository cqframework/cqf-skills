# PlanDefinition: Structure and Meaning

Baseline: FHIR R4 (4.0.1) and CPG 2.0.0. Untagged statements hold in R4.
Sources: FHIR-R4, FHIR-R4B, FHIR-R5, CPG-2.0.0

What a PlanDefinition's elements mean, as the R4 specification defines them, with CPG 2.0.0's added
rules. How `$apply` processes them, in the specification and in the reference implementation, is in
[apply.md](apply.md). Element cardinalities and bindings are in the `fhir` skill's element tables and,
for CPG profiles, the `cpg` skill.

## The resource

A PlanDefinition is "a pre-defined group of actions to be taken in particular circumstances". Applying
it to a subject "typically produces request resources… grouped within a CarePlan and/or RequestGroup"
[src: FHIR-R4 plandefinition.html#12.18.1]. Top-level elements to know:

| Element | Notes |
| --- | --- |
| `url`, `version`, `name`, `status` | `status` 1..1: draft, active, retired, unknown. Others refer to it by `url`, optionally `url|version` [src: FHIR-R4 references.html#canonical] |
| `type` | `plan-definition-type` (extensible): `order-set`, `clinical-protocol`, `eca-rule` ("[on Event] if Condition then Action"), `workflow-definition` [src: FHIR-R4 valueset-plan-definition-type.html] |
| `subject[x]` | CodeableConcept or Reference(Group); "If this is not specified, it is assumed to be Patient" [src: FHIR-R4 package/StructureDefinition-PlanDefinition.json] |
| `library` | 0..* canonical(Library): the logic the expressions use (below) |
| `goal` | Goals the plan aims at; actions point to them with `goalId` |
| `action` | The actions, nestable (below) |

CPG adds profiles with stricter rules. Its computable PlanDefinition requires `type` and at least one
`action`, and allows at most one `library`. A recommendation is an `eca-rule` and can't reference other
PlanDefinitions, a strategy is a `workflow-definition`, and a pathway is a `clinical-protocol`
[src: CPG-2.0.0 package/StructureDefinition-cpg-computableplandefinition.json]
[src: CPG-2.0.0 documentation-approach-09-methods-of-implementation.html#recommendations-strategies-and-pathways].
The `cpg` skill has the profiles.

## Actions

`action` is recursive: an action can hold `action[]`, and "the behavior of this action determines the
functionality of the sub-actions" [src: FHIR-R4 plandefinition-definitions.html#PlanDefinition.action.action].

| Element | Meaning |
| --- | --- |
| `id` | Referenced by `relatedAction`; the generated RequestGroup action takes the same id |
| `title`, `description`, `textEquivalent` | `textEquivalent` is for "when the definition is consumed by a system that might not be capable of interpreting it dynamically" |
| `code`, `reason`, `documentation`, `goalId` | `goalId` (not `goal`) points to `PlanDefinition.goal.id` |
| `priority` | routine, urgent, asap, stat |
| `trigger` | When the action applies (TriggerDefinition; below) |
| `condition` | When the action applies, and when it starts and stops (below) |
| `input`, `output` | DataRequirements. In CPG recommendations, `input` is the pertinent positives and negatives and `output` the evidence to attach |
| `relatedAction` | Ordering against other actions (below) |
| `timing[x]` | dateTime, Age, Period, Duration, Range or Timing |
| `participant` | `type` (patient, practitioner, related-person, device) and `role` |
| `type` | create, update, remove, fire-event |
| `subject[x]` | "The subject of an action overrides the subject at a parent action or on the root" [src: FHIR-R4 plandefinition-definitions.html#PlanDefinition.action.subject_x_] |
| behaviors | `groupingBehavior`, `selectionBehavior`, `requiredBehavior`, `precheckBehavior`, `cardinalityBehavior` (below) |
| `definition[x]` | canonical(ActivityDefinition, PlanDefinition or Questionnaire), or uri: what to create |
| `transform` | StructureMap applied to the definition's result |
| `dynamicValue` | Values computed at apply time (below) |

[src: FHIR-R4 package/StructureDefinition-PlanDefinition.json]

## Behaviors

Behaviors are set on a **group** action and govern its child actions.

| Behavior | Codes and meaning |
| --- | --- |
| `groupingBehavior` | `visual-group` (display as a visual group); `logical-group` (a logical grouping, which may or may not be shown as a visual group); `sentence-group` (alternative actions on the same target that differ only in detail, such as two dosing options for one drug; such a group almost always has selection `at-most-one`, or `exactly-one` if required) [src: FHIR-R4 valueset-action-grouping-behavior.html] |
| `selectionBehavior` | `any`, `all` (all, "as a single unit"), `all-or-none`, `exactly-one` (one, and "SHALL NOT choose none"), `at-most-one`, `one-or-more` [src: FHIR-R4 valueset-action-selection-behavior.html] |
| `requiredBehavior` | `must`, `could`, `must-unless-documented` [src: FHIR-R4 valueset-action-required-behavior.html] |
| `precheckBehavior` | `yes`, `no`: whether the action is selected by default [src: FHIR-R4 valueset-action-precheck-behavior.html] |
| `cardinalityBehavior` | `single`, `multiple`: whether it may be selected more than once [src: FHIR-R4 valueset-action-cardinality-behavior.html] |

`selectionBehavior` is about how many children may be chosen, and `requiredBehavior` about whether the
action itself must be done: an optional group of mutually exclusive choices is
`requiredBehavior: could` with `selectionBehavior: at-most-one`. CPG strategy and pathway profiles don't
allow the grouping, required, precheck and cardinality behaviors
[src: CPG-2.0.0 package/StructureDefinition-cpg-strategydefinition.json].

## Conditions

```json
"condition": [{
  "kind": "applicability",
  "expression": { "language": "text/cql-identifier", "expression": "Is Eligible" }
}]
```

- **Kinds:** `applicability` (whether the action applies), `start`, `stop`
  [src: FHIR-R4 valueset-action-condition-kind.html]. Applicability is evaluated when the definition is
  applied; start and stop "are carried through application and used to describe enter/exit criteria"
  [src: FHIR-R4 plandefinition-definitions.html#PlanDefinition.action.condition.kind].
- **Several conditions** of a kind are combined with AND: "the overall condition is true only if all the
  conditions are true" [src: FHIR-R4 plandefinition-definitions.html#PlanDefinition.action.condition].
  Child actions are only considered when their parent applies
  [src: FHIR-R4 plandefinition.html#12.18.3.3].

## Expressions and libraries

An `Expression` has `language` (1..1), `expression`, `reference`, `name` and `description`
[src: FHIR-R4 package/StructureDefinition-Expression.json]. The languages differ by FHIR version:

| Version | Codes |
| --- | --- |
| R4 | `text/cql`, `text/fhirpath`, `application/x-fhir-query` (extensible binding) [src: FHIR-R4 valueset-expression-language.html] |
| R4B | adds `text/cql-identifier` ("a valid Clinical Quality Language identifier") and `text/cql-expression` [src: FHIR-R4B valueset-expression-language.html] |
| R5 | as R4B, with `text/x-fhir-query` for FHIR queries and the system `urn:ietf:bcp:13` [src: FHIR-R5 valueset-expression-language.html] |

In R4, `text/cql` covers both an inline expression and the name of an expression in a library: the
specification's own example uses `language="text/cql"`, `expression="RiskAssessmentScore"`
[src: FHIR-R4 clinicalreasoning-topics-using-expressions.html#14.1.1.3]. CPG's examples, and most
current content on R4, use `text/cql-identifier` for a named expression and `text/cql-expression` for
inline CQL; the binding is extensible, so R4 content may use them. `text/cql.identifier` (with a dot)
isn't a code in any version.

**Which library.** A named expression is looked up in a library the resource references in `library`.
With one library, the expression "is evaluated as though it is in scope in that library"; with several,
qualify it with the library name (`"Lib".Expr`), and a resource "SHOULD reference at most one library"
[src: FHIR-R4 clinicalreasoning-topics-using-expressions.html#14.1.1.3]. CPG's computable profiles allow
one. `Expression.reference` can also point at the library (see [apply.md](apply.md) for how the reference
implementation uses it). Packaging CQL as a Library is covered by the `cql-ig` and `crmi` skills.

## dynamicValue

```json
"dynamicValue": [{
  "path": "priority",
  "expression": { "language": "text/cql-identifier", "expression": "Order Priority" }
}]
```

- **`path`** is a Simple FHIRPath, relative to the resource being created: `priority`, `timing.event`,
  `reasonCode`, not `ServiceRequest.priority` [src: FHIR-R4 plandefinition-definitions.html#PlanDefinition.action.dynamicValue.path].
  `%action.<element>` sets an element of the generated RequestGroup action instead, such as
  `%action.description` [src: FHIR-R4 plandefinition.html#12.18.3.3].
- With no `definition`, "a dynamicValue with a root ($this) path can be used to define the entire
  resource" [src: FHIR-R4 plandefinition-definitions.html#PlanDefinition.action.definition_x_].
- **Order:** the ActivityDefinition's dynamicValues are applied first, then the PlanDefinition action's,
  in document order, after any `transform` [src: FHIR-R4 plandefinition.html#12.18.3.4].
- The `$apply` parameters are available to expressions as `%subject`, `%encounter`, `%practitioner`
  and so on [src: FHIR-R4 plandefinition.html#12.18.3.3].

## Triggers and relatedAction

- **Trigger types:** `named-event` (with `name`, such as a CDS Hooks hook name), `periodic` (with
  `timing[x]`), `data-changed`, with its children `data-added`, `data-modified` and `data-removed`,
  `data-accessed` and `data-access-ended` [src: FHIR-R4 valueset-trigger-type.html]. A trigger means "the
  PlanDefinition apply process should be performed"; how that happens "is not prescribed"
  [src: FHIR-R4 clinicalreasoning-knowledge-artifact-representation.html#trigger-definitions]. CPG: only
  one action may specify a trigger [src: CPG-2.0.0 documentation-approach-09-methods-of-implementation.html#plandefinition-processing-semantics].
- **relatedAction** links to another action by `actionId` with a `relationship` (`before-start`,
  `before`, `before-end`, `concurrent-with-start`, `concurrent`, `concurrent-with-end`, `after-start`,
  `after`, `after-end`) and an optional `offset[x]` [src: FHIR-R4 valueset-action-relationship-type.html].
  With several, "all actions are dependencies"
  [src: FHIR-R4 plandefinition-definitions.html#PlanDefinition.action.relatedAction].
- **Order of actions.** In CPG, "no assumption of sequence of execution" comes from the order of
  `action` elements: sequence comes from relatedAction, and only `before-start` may be used
  [src: CPG-2.0.0 documentation-approach-09-methods-of-implementation.html#plandefinition-processing-semantics].
