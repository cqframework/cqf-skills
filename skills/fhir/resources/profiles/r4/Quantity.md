# Quantity

**ID** `Quantity` | **URL** `http://hl7.org/fhir/StructureDefinition/Quantity` | **Status** active
**Base** `Element` | **Derivation** specialization | **Kind** complex-type
**Version** 4.0.1 | **Publisher** HL7 FHIR Standard | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Base StructureDefinition for Quantity Type: A measured amount (or an amount that can potentially be measured). Note that measured amounts include amounts that are not precisely quantified, including amounts involving arbitrary units and floating currencies.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Quantity` | 0..* | `Quantity` |  |  | A measured or measurable amount |
| `Quantity.value` | 0..1 | `decimal` | summary |  | Numerical value (with implicit precision) |
| `Quantity.comparator` | 0..1 | `code` | modifier summary | required→quantity-comparator@4.0.1 | < \| <= \| >= \| > - how to understand the value |
| `Quantity.unit` | 0..1 | `string` | summary |  | Unit representation |
| `Quantity.system` | 0..1 | `uri` | summary |  | System that defines coded unit form |
| `Quantity.code` | 0..1 | `code` | summary |  | Coded form of the unit |

Elements defined in ancestors: `Quantity.id`, `Quantity.extension`

## Slices and fixed values

| Path | Card | Type | Fixed / pattern | Slicing |
| :--- | :--- | :--- | :--- | :--- |
| `Quantity.extension` | 0..* | `Extension` | — | discriminator value@url, rules=open |

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `Quantity` | `qty-3` | error | If a code for the unit is present, the system SHALL also be present | `code.empty() or system.exists()` |
