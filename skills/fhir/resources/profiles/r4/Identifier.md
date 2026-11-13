# Identifier

**ID** `Identifier` | **URL** `http://hl7.org/fhir/StructureDefinition/Identifier` | **Status** active
**Base** `Element` | **Derivation** specialization | **Kind** complex-type
**Version** 4.0.1 | **Publisher** HL7 FHIR Standard | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Base StructureDefinition for Identifier Type: An identifier - identifies some entity uniquely and unambiguously. Typically this is used for business identifiers.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Identifier` | 0..* | `Identifier` |  |  | An identifier intended for computation |
| `Identifier.use` | 0..1 | `code` | modifier summary | required→identifier-use@4.0.1 | usual \| official \| temp \| secondary \| old (If known) |
| `Identifier.type` | 0..1 | `CodeableConcept` | summary | extensible→identifier-type | Description of identifier |
| `Identifier.system` | 0..1 | `uri` | summary |  | The namespace for the identifier value |
| `Identifier.value` | 0..1 | `string` | summary |  | The value that is unique |
| `Identifier.period` | 0..1 | `Period` | summary |  | Time period when id is/was valid for use |
| `Identifier.assigner` | 0..1 | `Reference(Organization)` | summary |  | Organization that issued id (may be just text) |

Elements defined in ancestors: `Identifier.id`, `Identifier.extension`

## Slices and fixed values

| Path | Card | Type | Fixed / pattern | Slicing |
| :--- | :--- | :--- | :--- | :--- |
| `Identifier.extension` | 0..* | `Extension` | — | discriminator value@url, rules=open |

## Invariants

_No profile-specific invariants._
