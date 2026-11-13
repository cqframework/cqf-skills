# Annotation

**ID** `Annotation` | **URL** `http://hl7.org/fhir/StructureDefinition/Annotation` | **Status** active
**Base** `Element` | **Derivation** specialization | **Kind** complex-type
**Version** 4.0.1 | **Publisher** HL7 FHIR Standard | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Base StructureDefinition for Annotation Type: A text note which also contains information about who made the statement and when.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Annotation` | 0..* | `Annotation` |  |  | Text node with attribution |
| `Annotation.author[x]` | 0..1 | `Reference(Practitioner \| Patient \| RelatedPerson \| Organization), string` | summary |  | Individual responsible for the annotation |
| `Annotation.time` | 0..1 | `dateTime` | summary |  | When the annotation was made |
| `Annotation.text` | 1..1 | `markdown` | summary |  | The annotation - text content (as markdown) |

Elements defined in ancestors: `Annotation.id`, `Annotation.extension`

## Slices and fixed values

| Path | Card | Type | Fixed / pattern | Slicing |
| :--- | :--- | :--- | :--- | :--- |
| `Annotation.extension` | 0..* | `Extension` | — | discriminator value@url, rules=open |

## Invariants

_No profile-specific invariants._
