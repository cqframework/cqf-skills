# CodeableConcept

**ID** `CodeableConcept` | **URL** `http://hl7.org/fhir/StructureDefinition/CodeableConcept` | **Status** active
**Base** `Element` | **Derivation** specialization | **Kind** complex-type
**Version** 4.0.1 | **Publisher** HL7 FHIR Standard | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Base StructureDefinition for CodeableConcept Type: A concept that may be defined by a formal reference to a terminology or ontology or may be provided by text.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CodeableConcept` | 0..* | `CodeableConcept` |  |  | Concept - reference to a terminology or just text |
| `CodeableConcept.coding` | 0..* | `Coding` | summary |  | Code defined by a terminology system |
| `CodeableConcept.text` | 0..1 | `string` | summary |  | Plain text representation of the concept |

Elements defined in ancestors: `CodeableConcept.id`, `CodeableConcept.extension`

## Slices and fixed values

| Path | Card | Type | Fixed / pattern | Slicing |
| :--- | :--- | :--- | :--- | :--- |
| `CodeableConcept.extension` | 0..* | `Extension` | — | discriminator value@url, rules=open |

## Invariants

_No profile-specific invariants._
