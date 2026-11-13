# MeasureReport

**ID** `MeasureReport` | **URL** `http://hl7.org/fhir/StructureDefinition/MeasureReport` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Clinical Quality Information) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

The MeasureReport resource contains the results of the calculation of a measure; and optionally a reference to the resources involved in that calculation.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `MeasureReport` | 0..* | `MeasureReport` |  |  | Results of a measure evaluation |
| `MeasureReport.identifier` | 0..* | `Identifier` | summary |  | Additional identifier for the MeasureReport |
| `MeasureReport.status` | 1..1 | `code` | modifier summary | required→measure-report-status@4.0.1 | complete \| pending \| error |
| `MeasureReport.type` | 1..1 | `code` | summary | required→measure-report-type@4.0.1 | individual \| subject-list \| summary \| data-collection |
| `MeasureReport.measure` | 1..1 | `canonical(Measure)` | summary |  | What measure was calculated |
| `MeasureReport.subject` | 0..1 | `Reference(Patient \| Practitioner \| PractitionerRole \| Location \| Device \| RelatedPerson \| Group)` | summary |  | What individual(s) the report is for |
| `MeasureReport.date` | 0..1 | `dateTime` | summary |  | When the report was generated |
| `MeasureReport.reporter` | 0..1 | `Reference(Practitioner \| PractitionerRole \| Location \| Organization)` | summary |  | Who is reporting the data |
| `MeasureReport.period` | 1..1 | `Period` | summary |  | What period the report covers |
| `MeasureReport.improvementNotation` | 0..1 | `CodeableConcept` | modifier summary | required→measure-improvement-notation@4.0.1 | increase \| decrease |
| `MeasureReport.group` | 0..* | `BackboneElement` |  |  | Measure results for each group |
| `MeasureReport.group.code` | 0..1 | `CodeableConcept` | summary |  | Meaning of the group |
| `MeasureReport.group.population` | 0..* | `BackboneElement` |  |  | The populations in the group |
| `MeasureReport.group.population.code` | 0..1 | `CodeableConcept` | summary | extensible→measure-population | initial-population \| numerator \| numerator-exclusion \| denominator \| denominator-exclusion \| denominator-exception \| measure-population \| measure-population-exclusion \| measure-observation |
| `MeasureReport.group.population.count` | 0..1 | `integer` |  |  | Size of the population |
| `MeasureReport.group.population.subjectResults` | 0..1 | `Reference(List)` |  |  | For subject-list reports, the subject results in this population |
| `MeasureReport.group.measureScore` | 0..1 | `Quantity` | summary |  | What score this group achieved |
| `MeasureReport.group.stratifier` | 0..* | `BackboneElement` |  |  | Stratification results |
| `MeasureReport.group.stratifier.code` | 0..* | `CodeableConcept` |  |  | What stratifier of the group |
| `MeasureReport.group.stratifier.stratum` | 0..* | `BackboneElement` |  |  | Stratum results, one for each unique value, or set of values, in the stratifier, or stratifier components |
| `MeasureReport.group.stratifier.stratum.value` | 0..1 | `CodeableConcept` |  |  | The stratum value, e.g. male |
| `MeasureReport.group.stratifier.stratum.component` | 0..* | `BackboneElement` |  |  | Stratifier component values |
| `MeasureReport.group.stratifier.stratum.component.code` | 1..1 | `CodeableConcept` |  |  | What stratifier component of the group |
| `MeasureReport.group.stratifier.stratum.component.value` | 1..1 | `CodeableConcept` |  |  | The stratum component value, e.g. male |
| `MeasureReport.group.stratifier.stratum.population` | 0..* | `BackboneElement` |  |  | Population results in this stratum |
| `MeasureReport.group.stratifier.stratum.population.code` | 0..1 | `CodeableConcept` |  | extensible→measure-population | initial-population \| numerator \| numerator-exclusion \| denominator \| denominator-exclusion \| denominator-exception \| measure-population \| measure-population-exclusion \| measure-observation |
| `MeasureReport.group.stratifier.stratum.population.count` | 0..1 | `integer` |  |  | Size of the population |
| `MeasureReport.group.stratifier.stratum.population.subjectResults` | 0..1 | `Reference(List)` |  |  | For subject-list reports, the subject results in this population |
| `MeasureReport.group.stratifier.stratum.measureScore` | 0..1 | `Quantity` |  |  | What score this stratum achieved |
| `MeasureReport.evaluatedResource` | 0..* | `Reference(Resource)` |  |  | What data was used to calculate the measure score |

Elements defined in ancestors: `MeasureReport.id`, `MeasureReport.meta`, `MeasureReport.implicitRules`, `MeasureReport.language`, `MeasureReport.text`, `MeasureReport.contained`, `MeasureReport.extension`, `MeasureReport.modifierExtension`, `MeasureReport.group.id`, `MeasureReport.group.extension`, `MeasureReport.group.modifierExtension`, `MeasureReport.group.population.id`, `MeasureReport.group.population.extension`, `MeasureReport.group.population.modifierExtension`, `MeasureReport.group.stratifier.id`, `MeasureReport.group.stratifier.extension`, `MeasureReport.group.stratifier.modifierExtension`, `MeasureReport.group.stratifier.stratum.id`, `MeasureReport.group.stratifier.stratum.extension`, `MeasureReport.group.stratifier.stratum.modifierExtension`, `MeasureReport.group.stratifier.stratum.component.id`, `MeasureReport.group.stratifier.stratum.component.extension`, `MeasureReport.group.stratifier.stratum.component.modifierExtension`, `MeasureReport.group.stratifier.stratum.population.id`, `MeasureReport.group.stratifier.stratum.population.extension`, `MeasureReport.group.stratifier.stratum.population.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `MeasureReport` | `mrp-1` | error | Measure Reports used for data collection SHALL NOT communicate group and score information | `(type != 'data-collection') or group.exists().not()` |
| `MeasureReport` | `mrp-2` | error | Stratifiers SHALL be either a single criteria or a set of criteria components | `group.stratifier.stratum.all(value.exists() xor component.exists())` |
