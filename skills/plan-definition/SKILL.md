---
name: plan-definition
description: Author, review, apply and debug FHIR R4 PlanDefinition and ActivityDefinition resources — ECA rules, order sets, protocols, actions, conditions, behaviors, dynamicValues, CQL expressions and libraries — and the $apply operation, as R4, CPG 2.0.0 and R5 define it and as the clinical-reasoning reference implementation (HAPI FHIR) actually runs it. Includes a script to run $apply locally. Use for writing or explaining PlanDefinitions and ActivityDefinitions, predicting or debugging an $apply result, and choosing expression languages.
license: Apache-2.0
---

# PlanDefinition and $apply

A PlanDefinition is a computable plan: actions with conditions, behaviors and definitions, applied to
a subject with `$apply` to produce proposed requests. An ActivityDefinition is the template for one
request. This skill covers both, and `$apply`, in three layers that don't always agree: the FHIR R4
specification, the CPG 2.0.0 IG, and clinical-reasoning, the reference implementation in HAPI FHIR.

Related skills: `cpg` (CPG profiles and extensions), `crmi` (artifact profiles, packaging and
`$data-requirements`), `cql-ig` (packaging CQL as a Library), `cql` (the language), `fhir` (base R4
element tables), `vscode-cql` (running the CQL against test data).

## Versions

| Source | Version |
| --- | --- |
| FHIR | R4 4.0.1 (with R4B and R5 where they differ) |
| CPG | 2.0.0 (STU2) |
| clinical-reasoning (`cqf-fhir-cr`) | 4.13.0, the release cql-language-server 5.0.0 uses; 4.15.0 is out (see below) |

## When the Implementation Version Differs

Behaviour of the reference implementation is cited to its code at 4.13.0 (the `CR-4.13.0` citations) and
checked by running it (`resources/probes/2026-11-14/`). Between 4.13.0 and 4.15.0 the apply path
changed only in Questionnaire generation for `$r5.apply` and in which library an unqualified expression
uses (4.15.0 keeps declaration order). For another release:

1. Find the server's `cqf-fhir-cr` version (for HAPI FHIR, its release notes or dependencies).
2. Read the cited code at that tag on GitHub ([SOURCES.md](resources/SOURCES.md)), finding it by content
   near the cited lines; or change the version in `scripts/apply/pom.xml` and run the content locally.
3. Answer from that version, saying so.

## Quick Reference

```json
{
  "resourceType": "PlanDefinition",
  "url": "http://example.org/fhir/PlanDefinition/follow-up",
  "version": "1.0.0",
  "status": "active",
  "type": { "coding": [{ "system": "http://terminology.hl7.org/CodeSystem/plan-definition-type", "code": "eca-rule" }] },
  "library": ["http://example.org/fhir/Library/FollowUpRules"],
  "action": [{
    "id": "follow-up",
    "title": "Schedule a follow-up visit",
    "condition": [{
      "kind": "applicability",
      "expression": { "language": "text/cql-identifier", "expression": "Needs Follow Up" }
    }],
    "definitionCanonical": "http://example.org/fhir/ActivityDefinition/follow-up-visit|1.0.0",
    "dynamicValue": [{
      "path": "action.description",
      "expression": { "language": "text/cql-identifier", "expression": "Follow Up Reason" }
    }]
  }]
}
```

- **Expressions:** name an expression in the PlanDefinition's one `library` with `text/cql-identifier`
  (R4B/R5 code; R4 itself uses `text/cql` for both named and inline CQL). With more than one library,
  set `expression.reference` to the library's canonical.
- **Conditions:** only `applicability` decides whether an action applies; several are ANDed.
- **dynamicValue paths** are relative to the generated resource (`priority`), or `%action.x` /
  `action.x` for the RequestGroup action.
- **Results:** R4 `$apply` returns a CarePlan holding a RequestGroup; CPG 2.0.0 and R5 return a Bundle
  per subject; clinical-reasoning's `$r5.apply` returns Parameters holding such Bundles. None returns a
  GuidanceResponse.
- **Run it locally:** `scripts/apply/run.sh <project> plan <PlanDefinition id> Patient/<id>`
  ([apply.md](resources/apply.md#running-apply-locally)).

## Known Gotchas

In clinical-reasoning 4.13.0 (each verified by running it):

- **A null or failing condition keeps the action, but drops its definition and children**; only a
  false condition removes it. Check the RequestGroup for actions with no `resource`, and for a
  `cqf-messages` extension, which holds the errors.
- **`text/fhirpath` is evaluated by the CQL engine**, so FHIRPath-only semantics (such as partial
  `matches`) don't hold.
- **Any unknown expression language is treated as a named expression**, not rejected.
- **With several libraries and no `expression.reference`, which library is used isn't defined** (the
  first in an unordered map).
- **Behaviors aren't enforced**: every applicable child of an `exactly-one` group is returned; only
  `selectionBehavior` is copied to the RequestGroup.
- **A Questionnaire definition is contained as is**, not wrapped in a Task.
- **ActivityDefinition requests default to status `active`** (ServiceRequest and MedicationRequest
  intent `order`), not the specification's `draft`/`option`; many kinds come out empty unless
  dynamicValues fill them; `transform` isn't applied.
- **An ActivityDefinition's dynamicValues use its own `library`**, not the PlanDefinition's.
- **`userType`, `userTaskContext`, `setting` and `settingContext` are ignored.**
- **A canonical matching several resources fails the whole operation**: version your canonicals.

In the specifications:

- **`text/cql-identifier` and `text/cql-expression` aren't R4 codes** (they're R4B/R5); the binding is
  extensible, and CPG uses them. `text/cql.identifier` isn't a code anywhere.
- **`selectionBehavior` is on the group**, not its children; `requiredBehavior` is a different question.
- **Trigger types** are `named-event`, `periodic`, `data-changed` (and `data-added`, `data-modified`,
  `data-removed`), `data-accessed`, `data-access-ended`; there's no `data-requested`.
- **`userType` and the other context parameters are CodeableConcepts**, and `parameters` is a CPG
  addition, not an R4 one.

## Supporting Files

| File | Contents |
| --- | --- |
| [resources/plandefinition.md](resources/plandefinition.md) | Elements, actions, behaviors, conditions, expressions and libraries, dynamicValue, triggers, relatedAction |
| [resources/activitydefinition.md](resources/activitydefinition.md) | Elements, and applying one in the specification and in clinical-reasoning |
| [resources/apply.md](resources/apply.md) | `$apply` parameters and results (R4, CPG, R5), the specification's processing, what clinical-reasoning does, and running it locally |
| [resources/SOURCES.md](resources/SOURCES.md) | The pinned sources and how to read a citation |
| [resources/probes/2026-11-14/](resources/probes/2026-11-14/RESULTS.md) | The probe project and what `$apply` returned for it |
| [scripts/apply/](scripts/apply/run.sh) | Runs `$apply` with clinical-reasoning 4.13.0 (Java 17+, Maven) |

For maintainers: `scripts/fetch-sources.sh` caches the clinical-reasoning clone,
`scripts/lint_skill_pd.py` checks citations, and `scripts/check_release.py` reports which citations a new
release touches.
