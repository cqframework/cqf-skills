# Coding

**ID** `Coding` | **URL** `http://hl7.org/fhir/StructureDefinition/Coding` | **Status** active
**Base** `Element` | **Derivation** specialization | **Kind** complex-type
**Version** 4.0.1 | **Publisher** HL7 FHIR Standard | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Base StructureDefinition for Coding Type: A reference to a code defined by a terminology system.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Coding` | 0..* | `Coding` |  |  | A reference to a code defined by a terminology system |
| `Coding.system` | 0..1 | `uri` | summary |  | Identity of the terminology system |
| `Coding.version` | 0..1 | `string` | summary |  | Version of the system - if relevant |
| `Coding.code` | 0..1 | `code` | summary |  | Symbol in syntax defined by the system |
| `Coding.display` | 0..1 | `string` | summary |  | Representation defined by the system |
| `Coding.userSelected` | 0..1 | `boolean` | summary |  | If this coding was chosen directly by the user |

Elements defined in ancestors: `Coding.id`, `Coding.extension`

## Slices and fixed values

| Path | Card | Type | Fixed / pattern | Slicing |
| :--- | :--- | :--- | :--- | :--- |
| `Coding.extension` | 0..* | `Extension` | — | discriminator value@url, rules=open |

## Invariants

_No profile-specific invariants._
