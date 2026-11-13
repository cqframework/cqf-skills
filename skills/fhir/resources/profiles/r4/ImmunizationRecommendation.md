# ImmunizationRecommendation

**ID** `ImmunizationRecommendation` | **URL** `http://hl7.org/fhir/StructureDefinition/ImmunizationRecommendation` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Public Health and Emergency Response) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

A patient's point-in-time set of recommendations (i.e. forecasting) according to a published schedule with optional supporting justification.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ImmunizationRecommendation` | 0..* | `ImmunizationRecommendation` |  |  | Guidance or advice relating to an immunization |
| `ImmunizationRecommendation.identifier` | 0..* | `Identifier` | summary |  | Business identifier |
| `ImmunizationRecommendation.patient` | 1..1 | `Reference(Patient)` | summary |  | Who this profile is for |
| `ImmunizationRecommendation.date` | 1..1 | `dateTime` | summary |  | Date recommendation(s) created |
| `ImmunizationRecommendation.authority` | 0..1 | `Reference(Organization)` |  |  | Who is responsible for protocol |
| `ImmunizationRecommendation.recommendation` | 1..* | `BackboneElement` | summary |  | Vaccine administration recommendations |
| `ImmunizationRecommendation.recommendation.vaccineCode` | 0..* | `CodeableConcept` | summary | example→vaccine-code | Vaccine or vaccine group recommendation applies to |
| `ImmunizationRecommendation.recommendation.targetDisease` | 0..1 | `CodeableConcept` | summary | example→immunization-recommendation-target-disease | Disease to be immunized against |
| `ImmunizationRecommendation.recommendation.contraindicatedVaccineCode` | 0..* | `CodeableConcept` | summary | example→vaccine-code | Vaccine which is contraindicated to fulfill the recommendation |
| `ImmunizationRecommendation.recommendation.forecastStatus` | 1..1 | `CodeableConcept` | modifier summary | example→immunization-recommendation-status | Vaccine recommendation status |
| `ImmunizationRecommendation.recommendation.forecastReason` | 0..* | `CodeableConcept` | summary | example→immunization-recommendation-reason | Vaccine administration status reason |
| `ImmunizationRecommendation.recommendation.dateCriterion` | 0..* | `BackboneElement` |  |  | Dates governing proposed immunization |
| `ImmunizationRecommendation.recommendation.dateCriterion.code` | 1..1 | `CodeableConcept` |  | example→immunization-recommendation-date-criterion | Type of date |
| `ImmunizationRecommendation.recommendation.dateCriterion.value` | 1..1 | `dateTime` |  |  | Recommended date |
| `ImmunizationRecommendation.recommendation.description` | 0..1 | `string` |  |  | Protocol details |
| `ImmunizationRecommendation.recommendation.series` | 0..1 | `string` |  |  | Name of vaccination series |
| `ImmunizationRecommendation.recommendation.doseNumber[x]` | 0..1 | `positiveInt, string` | summary |  | Recommended dose number within series |
| `ImmunizationRecommendation.recommendation.seriesDoses[x]` | 0..1 | `positiveInt, string` |  |  | Recommended number of doses for immunity |
| `ImmunizationRecommendation.recommendation.supportingImmunization` | 0..* | `Reference(Immunization \| ImmunizationEvaluation)` |  |  | Past immunizations supporting recommendation |
| `ImmunizationRecommendation.recommendation.supportingPatientInformation` | 0..* | `Reference(Resource)` |  |  | Patient observations supporting recommendation |

Elements defined in ancestors: `ImmunizationRecommendation.id`, `ImmunizationRecommendation.meta`, `ImmunizationRecommendation.implicitRules`, `ImmunizationRecommendation.language`, `ImmunizationRecommendation.text`, `ImmunizationRecommendation.contained`, `ImmunizationRecommendation.extension`, `ImmunizationRecommendation.modifierExtension`, `ImmunizationRecommendation.recommendation.id`, `ImmunizationRecommendation.recommendation.extension`, `ImmunizationRecommendation.recommendation.modifierExtension`, `ImmunizationRecommendation.recommendation.dateCriterion.id`, `ImmunizationRecommendation.recommendation.dateCriterion.extension`, `ImmunizationRecommendation.recommendation.dateCriterion.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `ImmunizationRecommendation.recommendation` | `imr-1` | error | One of vaccineCode or targetDisease SHALL be present | `vaccineCode.exists() or targetDisease.exists()` |
