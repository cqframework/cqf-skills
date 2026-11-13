---
name: fhir
description: Use when working with FHIR R4 resources or bundles — bundle types, transaction patterns, resource IDs, meta.profile, references, terminology system URIs, and per-resource element, cardinality and binding tables for the base R4 resources and data types under `resources/profiles/r4/`.
license: Apache-2.0
---

FHIR R4 (4.0.1) is the base standard for this work. This skill covers base FHIR R4: resources,
bundles and the base resource definitions. Profiles from implementation guides (US Core, QI-Core,
US Quality Core, CPG, CRMI) add their own constraints, so check the IG for those.

## Spec Reference

- FHIR R4: https://hl7.org/fhir/R4/
- Content captured: 2026-04-28, FHIR R4

## Supporting Files

For base FHIR R4 profile patterns, example resources and terminology system URIs: see [profiles.md](resources/profiles.md)
For per-resource element tables: see [resources/profiles/r4/README.md](resources/profiles/r4/README.md)

## Element tables

Per-resource element tables for cardinality, type, flags (mustSupport, modifier, summary) and
binding lookup, for 42 base resources and 9 complex data types.

- Open the index, [resources/profiles/r4/README.md](resources/profiles/r4/README.md), first to find
  a resource or type by id, and read its legend for the table tokens.
- Then read the one file you need, `resources/profiles/r4/{id}.md`, for example
  `resources/profiles/r4/Condition.md`. Never load the whole directory.
- Each file has a header (URL, status, base, version, package), then `## Description`,
  `## Elements` (one row per element: path, cardinality, type, flags, binding, description) and
  `## Invariants`. Data types with slicing or fixed values also have `## Slices and fixed values`.
- Elements inherited from `Resource`, `DomainResource` or `Element` aren't repeated. Look them up
  in the base type.
- The tables are generated from the `hl7.fhir.r4.core@4.0.1` package. Don't edit them by hand.
  Regenerate them instead.

## Bundle Types

| Type | Use |
|------|-----|
| `transaction` | Batch with atomicity; each entry has `request.method` + `request.url` |
| `batch` | Batch without atomicity guarantee |
| `document` | Clinical document; first entry must be a `Composition` |
| `collection` | Passive container; no request semantics |

## Transaction Bundle Entry Pattern

```json
{
  "fullUrl": "https://example.org/{ResourceType}/{id}",
  "resource": {
    "resourceType": "...",
    "id": "..."
  },
  "request": {
    "method": "PUT",
    "url": "{ResourceType}/{id}"
  }
}
```

- `fullUrl` must be a valid URI; by convention matches `{ResourceType}/{id}`
- `request.method`: `PUT` for upsert by id, `POST` for server-assigned id
- `request.url`: relative resource reference, e.g., `Patient/abc123`

## Resource ID Conventions

- Use UUIDs for resource IDs in test/synthetic data
- For reproducible bundles use deterministic UUIDs (Python: `uuid.uuid5` with fixed namespace)
- Avoid sequential integers — they collide across systems

## Key Resource Elements

**Meta.profile**: declare the profile the resource conforms to (QI-Core shown as an example):
```json
"meta": {
  "profile": ["http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-patient"]
}
```

**References**: use relative references within a bundle:
```json
"subject": { "reference": "Patient/abc123" }
```
