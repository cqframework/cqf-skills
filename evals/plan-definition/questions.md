# plan-definition Skill Test Questions

Questions for an agent working with PlanDefinitions. Answer each in a few sentences, as you would to a
knowledge engineer. Then do task TK-01. The answer key is in `answers.md`; don't read it.

## Expressions and libraries

**EX-01. Language codes.** Our content is FHIR R4. Is `text/cql-identifier` a valid expression
language, and what's the difference from `text/cql`?

**EX-02. Two libraries.** A PlanDefinition lists two libraries in `library`, and a condition uses
`"expression": "Is Eligible"` with no `reference`. Both libraries define `"Is Eligible"`. Which one does
a HAPI FHIR server (clinical-reasoning 4.16.0) use?

**EX-03. FHIRPath.** I wrote a condition with `"language": "text/fhirpath"` that uses `matches()`. It
behaves differently on a HAPI FHIR server than in a FHIRPath evaluator. Why?

## Conditions and behaviors

**CO-01. A null condition.** On a HAPI FHIR server, an action whose applicability condition returns null
still appears in the RequestGroup, but without its ServiceRequest. Is that a bug in my content?

**CO-02. Start conditions.** I gave an action a `start` condition that's false, and `$apply` still
included the action. Why?

**BE-01. Exactly one.** My group action has `selectionBehavior: exactly-one`, yet `$apply` returned all
three child actions. What went wrong?

**BE-02. Optional choice.** How do I express "the clinician may pick at most one of these three orders,
or none"?

## dynamicValue

**DV-01. A path.** Is `"path": "ServiceRequest.priority"` right for a dynamicValue on an action whose
definition is a ServiceRequest ActivityDefinition?

**DV-02. The card text.** How do I set the text of the RequestGroup action itself, rather than an element
of the generated request?

## $apply

**AP-01. The result.** What does `PlanDefinition/$apply` return in R4, in CPG 2.0.0, and from a HAPI FHIR
server's `$apply` and `$r5.apply`?

**AP-02. GuidanceResponse.** Will `$apply` give me a GuidanceResponse with status `data-required` when
data is missing?

**AP-03. Errors.** `$apply` returned a CarePlan with no error, but one action is missing its resource.
Where would the error be?

**AP-04. Context parameters.** We pass `setting` and `userType` to `$apply` so our CQL can tailor the
recommendation. How do we read them in the CQL?

## ActivityDefinition

**AD-01. Status and intent.** Applying our ServiceRequest ActivityDefinition from a PlanDefinition on a
HAPI FHIR server gives status `active` and intent `order`. The R4 spec says something else. What, and
what should we do?

**AD-02. dynamicValue library.** Our ActivityDefinition's dynamicValue names `"Order Priority"`, defined
in the PlanDefinition's library, and it comes back null. Why?

## Triggers

**TR-01. Trigger types.** Which trigger type should a rule use to fire when a medication is ordered, and
is `data-requested` a valid type?

## Versions

**VR-01. An older version.** The VS Code CQL extension 1.0.0 runs clinical-reasoning 4.13.0. Does what
the skill says about unqualified expressions with several libraries hold there?

## Task

**TK-01. An HbA1c follow-up rule.** Write, in IG layout (`input/resources/`, `input/tests/`), a
PlanDefinition (an ECA rule), an ActivityDefinition and a Library (CQL in its content) for: "For an adult
with no hemoglobin A1c result (LOINC 4548-4) in the last 6 months, propose ordering an HbA1c test, and
say why on the RequestGroup action." Add two synthetic test patients, one who needs the test and one with
a recent result. Use canonicals under `http://example.org/fhir`.
