# Period

**ID** `Period` | **URL** `http://hl7.org/fhir/StructureDefinition/Period` | **Status** active
**Base** `Element` | **Derivation** specialization | **Kind** complex-type
**Version** 4.0.1 | **Publisher** HL7 FHIR Standard | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Base StructureDefinition for Period Type: A time period defined by a start and end date and optionally time.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Period` | 0..* | `Period` |  |  | Time range defined by start and end date/time |
| `Period.start` | 0..1 | `dateTime` | summary |  | Starting time with inclusive boundary |
| `Period.end` | 0..1 | `dateTime` | summary |  | End time with inclusive boundary, if not ongoing |

Elements defined in ancestors: `Period.id`, `Period.extension`

## Slices and fixed values

| Path | Card | Type | Fixed / pattern | Slicing |
| :--- | :--- | :--- | :--- | :--- |
| `Period.extension` | 0..* | `Extension` | — | discriminator value@url, rules=open |

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `Period` | `per-1` | error | If present, start SHALL have a lower value than end | `start.hasValue().not() or end.hasValue().not() or (start <= end)` |
