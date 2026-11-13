# Reference

**ID** `Reference` | **URL** `http://hl7.org/fhir/StructureDefinition/Reference` | **Status** active
**Base** `Element` | **Derivation** specialization | **Kind** complex-type
**Version** 4.0.1 | **Publisher** HL7 FHIR Standard | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Base StructureDefinition for Reference Type: A reference from one resource to another.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Reference` | 0..* | `Reference` |  |  | A reference from one resource to another |
| `Reference.reference` | 0..1 | `string` | summary |  | Literal reference, Relative, internal or absolute URL |
| `Reference.type` | 0..1 | `uri` | summary | extensible→resource-types | Type the reference refers to (e.g. "Patient") |
| `Reference.identifier` | 0..1 | `Identifier` | summary |  | Logical reference, when literal reference is not known |
| `Reference.display` | 0..1 | `string` | summary |  | Text alternative for the resource |

Elements defined in ancestors: `Reference.id`, `Reference.extension`

## Slices and fixed values

| Path | Card | Type | Fixed / pattern | Slicing |
| :--- | :--- | :--- | :--- | :--- |
| `Reference.extension` | 0..* | `Extension` | — | discriminator value@url, rules=open |

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `Reference` | `ref-1` | error | SHALL have a contained resource if a local reference is provided | `reference.startsWith('#').not() or (reference.substring(1).trace('url') in %rootResource.contained.id.trace('ids'))` |
