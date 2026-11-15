# Probe results, 2026-11-14

Run with clinical-reasoning **4.13.0** (`org.opencds.cqf.fhir:cqf-fhir-cr`, which brings the CQL
translator and engine 5.4.0 and HAPI FHIR 8.12.0), through `scripts/apply/run.sh`, on the project in
this folder: `input/resources/` holds the definitions and libraries (CQL base64 in `Library.content`),
`input/tests/Patient-adult-1.json` the patient (born 1980). Every run's subject is `Patient/adult-1`.

Definitions:

- `Library/ExampleRules`: `"Is Adult"` (true), `"Is Child"` (false), `"Null Result"` (null),
  `"Not Boolean"` (`'yes'`), `"Message"` (`'Hello Ada'`), `"Priority"` (`'urgent'`), `"Throws"`
  (`singleton from { 1, 2 }`, a run-time error).
- `Library/OtherRules`: `"Is Adult"` (false).
- `PlanDefinition/probe`: one action per case below, `library` = ExampleRules.
- `PlanDefinition/two-libs`: `library` = ExampleRules then OtherRules.
- `ActivityDefinition/send-message` (CommunicationRequest, `code.text`, a `priority` dynamicValue,
  `library` = ExampleRules); `ActivityDefinition/order-test` (ServiceRequest, LOINC 4548-4).
- `Questionnaire/q1`.

## 1. PlanDefinition/probe, `$apply`

`run.sh . plan probe Patient/adult-1` returns a **CarePlan** (status `active`, intent `proposal`,
`instantiatesCanonical` = the PlanDefinition with `|1.0.0`), whose activity references the contained
RequestGroup `#probe` (status `active`, intent `proposal`). Contained: the RequestGroup, Goal `1`
(lifecycle `proposed`, subject the patient), CommunicationRequest `adult-send-message`, Questionnaire
`questionnaire-q1` and OperationOutcome `apply-outcome-probe`; the CarePlan and RequestGroup both carry a
`cqf-messages` extension referencing it.

| Action | Condition(s) | In the RequestGroup? | Notes |
| --- | --- | --- | --- |
| `adult` | `Is Adult` (true) | yes, `resource` `#adult-send-message` | condition result `true`; PD dynamicValue `action.description` set the action's description to `Hello Ada`; the CommunicationRequest has status `active`, `priority` `urgent` (AD and PD dynamicValues), payload `Please schedule a follow-up visit` (from `code.text`), subject the patient |
| `child` | `Is Child` (false) | **no** | |
| `null` | `Null Result` (null) | **yes, without its definition or child action** | condition result `data-absent-reason` `asked-unknown` |
| `notbool` | `Not Boolean` (`'yes'`) | **no** | logged: "returned a non-boolean value: StringType" |
| `start-false` | `Is Child` as `kind: start` | yes | the start condition is copied without a result |
| `two` | `Is Adult` and `Null Result` | yes, without definition or children | results `true` and `asked-unknown` |
| `fhirpath` | `today() > @2000-01-01`, `text/fhirpath` | yes | result `true` |
| `fhirpath-matches` | `'abc'.matches('b')`, `text/fhirpath` | **no** | see §2 |
| `cqlexpr` | `AgeInYears() >= 18`, `text/cql-expression` | yes | result `true` |
| `throws` | `Throws` | **yes, without definition or children** | result `asked-unknown`; OperationOutcome issue "Condition expression 'Throws' encountered exception: Expected a list with at most one element, but found a list with multiple elements." |
| `badlang` | `Is Adult`, language `text/x-made-up` | yes | result `true`: treated as a named expression |
| `group` | none; `selectionBehavior: exactly-one`, `requiredBehavior: must`, `groupingBehavior: logical-group`, `cardinalityBehavior: single`, `precheckBehavior: yes`, a `named-event` trigger; children `g1`, `g2` | yes | only `selectionBehavior` is copied; **both** children are present; no trigger |
| `questionnaire` | none; `definitionCanonical` Questionnaire/q1 | yes, `resource` `#questionnaire-q1` | the Questionnaire itself is contained |

## 2. `text/fhirpath` runs through CQL

In FHIRPath, `matches` is a partial match, so `'abc'.matches('b')` is `true`. The action with that
condition was dropped (§1), so the condition evaluated to `false`: the CQL engine 5.4.0 matches the whole
string. The expression was evaluated as CQL, not FHIRPath.

## 3. PlanDefinition/two-libs: library selection

| Action | Condition | Result |
| --- | --- | --- |
| `noref` | `Is Adult`, no `reference` | in the RequestGroup, result `true`: resolved against ExampleRules |
| `ref-other` | `Is Adult`, `reference` = OtherRules | **dropped**: resolved against OtherRules (`false`) |

With no `reference`, this run used ExampleRules, the first declared. In 4.13.0 the map of libraries is
unordered, so that isn't guaranteed.

## 4. PlanDefinition/probe, `$r5.apply`

`run.sh . r5 probe Patient/adult-1` returns a **Parameters** resource with one `return` part, a Bundle
whose entries are the RequestGroup (with the OperationOutcome contained and `resource-pertainsToGoal`
extensions), Goal `1`, CommunicationRequest `adult-send-message` and Questionnaire `questionnaire-q1`.
The actions are as in §1, and `action.resource` references have no `#`.

## 5. ActivityDefinition/order-test, `$apply`

`run.sh . activity order-test Patient/adult-1` returns a **ServiceRequest**: id `order-test`, status
`active`, intent `order`, the code, subject the patient, `instantiatesCanonical` with `|1.0.0`.
