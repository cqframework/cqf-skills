# Timing

**ID** `Timing` | **URL** `http://hl7.org/fhir/StructureDefinition/Timing` | **Status** active
**Base** `BackboneElement` | **Derivation** specialization | **Kind** complex-type
**Version** 4.0.1 | **Publisher** HL7 FHIR Standard | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Base StructureDefinition for Timing Type: Specifies an event that may occur multiple times. Timing schedules are used to record when things are planned, expected or requested to occur. The most common usage is in dosage instructions for medications. They are also used when planning care of various kinds, and may be used for reporting the schedule to which past regular activities were carried out.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Timing` | 0..* | `Timing` |  |  | A timing schedule that specifies an event that may occur multiple times |
| `Timing.event` | 0..* | `dateTime` | summary |  | When the event occurs |
| `Timing.repeat` | 0..1 | `Element` | summary |  | When the event is to occur |
| `Timing.repeat.bounds[x]` | 0..1 | `Duration, Range, Period` | summary |  | Length/Range of lengths, or (Start and/or end) limits |
| `Timing.repeat.count` | 0..1 | `positiveInt` | summary |  | Number of times to repeat |
| `Timing.repeat.countMax` | 0..1 | `positiveInt` | summary |  | Maximum number of times to repeat |
| `Timing.repeat.duration` | 0..1 | `decimal` | summary |  | How long when it happens |
| `Timing.repeat.durationMax` | 0..1 | `decimal` | summary |  | How long when it happens (Max) |
| `Timing.repeat.durationUnit` | 0..1 | `code` | summary | required→units-of-time@4.0.1 | s \| min \| h \| d \| wk \| mo \| a - unit of time (UCUM) |
| `Timing.repeat.frequency` | 0..1 | `positiveInt` | summary |  | Event occurs frequency times per period |
| `Timing.repeat.frequencyMax` | 0..1 | `positiveInt` | summary |  | Event occurs up to frequencyMax times per period |
| `Timing.repeat.period` | 0..1 | `decimal` | summary |  | Event occurs frequency times per period |
| `Timing.repeat.periodMax` | 0..1 | `decimal` | summary |  | Upper limit of period (3-4 hours) |
| `Timing.repeat.periodUnit` | 0..1 | `code` | summary | required→units-of-time@4.0.1 | s \| min \| h \| d \| wk \| mo \| a - unit of time (UCUM) |
| `Timing.repeat.dayOfWeek` | 0..* | `code` | summary | required→days-of-week@4.0.1 | mon \| tue \| wed \| thu \| fri \| sat \| sun |
| `Timing.repeat.timeOfDay` | 0..* | `time` | summary |  | Time of day for action |
| `Timing.repeat.when` | 0..* | `code` | summary | required→event-timing@4.0.1 | Code for time period of occurrence |
| `Timing.repeat.offset` | 0..1 | `unsignedInt` | summary |  | Minutes from event (before or after) |
| `Timing.code` | 0..1 | `CodeableConcept` | summary | preferred→timing-abbreviation | BID \| TID \| QID \| AM \| PM \| QD \| QOD \| + |

Elements defined in ancestors: `Timing.id`, `Timing.extension`, `Timing.modifierExtension`, `Timing.repeat.id`, `Timing.repeat.extension`

## Slices and fixed values

| Path | Card | Type | Fixed / pattern | Slicing |
| :--- | :--- | :--- | :--- | :--- |
| `Timing.extension` | 0..* | `Extension` | — | discriminator value@url, rules=open |
| `Timing.repeat.extension` | 0..* | `Extension` | — | discriminator value@url, rules=open |

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `Timing.repeat` | `tim-1` | error | if there's a duration, there needs to be duration units | `duration.empty() or durationUnit.exists()` |
| `Timing.repeat` | `tim-2` | error | if there's a period, there needs to be period units | `period.empty() or periodUnit.exists()` |
| `Timing.repeat` | `tim-4` | error | duration SHALL be a non-negative value | `duration.exists() implies duration >= 0` |
| `Timing.repeat` | `tim-5` | error | period SHALL be a non-negative value | `period.exists() implies period >= 0` |
| `Timing.repeat` | `tim-6` | error | If there's a periodMax, there must be a period | `periodMax.empty() or period.exists()` |
| `Timing.repeat` | `tim-7` | error | If there's a durationMax, there must be a duration | `durationMax.empty() or duration.exists()` |
| `Timing.repeat` | `tim-8` | error | If there's a countMax, there must be a count | `countMax.empty() or count.exists()` |
| `Timing.repeat` | `tim-9` | error | If there's an offset, there must be a when (and not C, CM, CD, CV) | `offset.empty() or (when.exists() and ((when in ('C' \| 'CM' \| 'CD' \| 'CV')).not()))` |
| `Timing.repeat` | `tim-10` | error | If there's a timeOfDay, there cannot be a when, or vice versa | `timeOfDay.empty() or when.empty()` |
