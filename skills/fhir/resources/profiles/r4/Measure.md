# Measure

**ID** `Measure` | **URL** `http://hl7.org/fhir/StructureDefinition/Measure` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Clinical Quality Information) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

The Measure resource provides the definition of a quality measure.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Measure` | 0..* | `Measure` |  |  | A quality measure definition |
| `Measure.url` | 0..1 | `uri` | summary |  | Canonical identifier for this measure, represented as a URI (globally unique) |
| `Measure.identifier` | 0..* | `Identifier` | summary |  | Additional identifier for the measure |
| `Measure.version` | 0..1 | `string` | summary |  | Business version of the measure |
| `Measure.name` | 0..1 | `string` | summary |  | Name for this measure (computer friendly) |
| `Measure.title` | 0..1 | `string` | summary |  | Name for this measure (human friendly) |
| `Measure.subtitle` | 0..1 | `string` |  |  | Subordinate title of the measure |
| `Measure.status` | 1..1 | `code` | modifier summary | required→publication-status@4.0.1 | draft \| active \| retired \| unknown |
| `Measure.experimental` | 0..1 | `boolean` | summary |  | For testing purposes, not real usage |
| `Measure.subject[x]` | 0..1 | `CodeableConcept, Reference(Group)` |  | extensible→subject-type | E.g. Patient, Practitioner, RelatedPerson, Organization, Location, Device |
| `Measure.date` | 0..1 | `dateTime` | summary |  | Date last changed |
| `Measure.publisher` | 0..1 | `string` | summary |  | Name of the publisher (organization or individual) |
| `Measure.contact` | 0..* | `ContactDetail` | summary |  | Contact details for the publisher |
| `Measure.description` | 0..1 | `markdown` | summary |  | Natural language description of the measure |
| `Measure.useContext` | 0..* | `UsageContext` | summary |  | The context that the content is intended to support |
| `Measure.jurisdiction` | 0..* | `CodeableConcept` | summary | extensible→jurisdiction | Intended jurisdiction for measure (if applicable) |
| `Measure.purpose` | 0..1 | `markdown` |  |  | Why this measure is defined |
| `Measure.usage` | 0..1 | `string` |  |  | Describes the clinical usage of the measure |
| `Measure.copyright` | 0..1 | `markdown` |  |  | Use and/or publishing restrictions |
| `Measure.approvalDate` | 0..1 | `date` |  |  | When the measure was approved by publisher |
| `Measure.lastReviewDate` | 0..1 | `date` |  |  | When the measure was last reviewed |
| `Measure.effectivePeriod` | 0..1 | `Period` | summary |  | When the measure is expected to be used |
| `Measure.topic` | 0..* | `CodeableConcept` |  | example→definition-topic | The category of the measure, such as Education, Treatment, Assessment, etc. |
| `Measure.author` | 0..* | `ContactDetail` |  |  | Who authored the content |
| `Measure.editor` | 0..* | `ContactDetail` |  |  | Who edited the content |
| `Measure.reviewer` | 0..* | `ContactDetail` |  |  | Who reviewed the content |
| `Measure.endorser` | 0..* | `ContactDetail` |  |  | Who endorsed the content |
| `Measure.relatedArtifact` | 0..* | `RelatedArtifact` |  |  | Additional documentation, citations, etc. |
| `Measure.library` | 0..* | `canonical(Library)` |  |  | Logic used by the measure |
| `Measure.disclaimer` | 0..1 | `markdown` | summary |  | Disclaimer for use of the measure or its referenced content |
| `Measure.scoring` | 0..1 | `CodeableConcept` | summary | extensible→measure-scoring | proportion \| ratio \| continuous-variable \| cohort |
| `Measure.compositeScoring` | 0..1 | `CodeableConcept` | summary | extensible→composite-measure-scoring | opportunity \| all-or-nothing \| linear \| weighted |
| `Measure.type` | 0..* | `CodeableConcept` | summary | extensible→measure-type | process \| outcome \| structure \| patient-reported-outcome \| composite |
| `Measure.riskAdjustment` | 0..1 | `string` | summary |  | How risk adjustment is applied for this measure |
| `Measure.rateAggregation` | 0..1 | `string` | summary |  | How is rate aggregation performed for this measure |
| `Measure.rationale` | 0..1 | `markdown` | summary |  | Detailed description of why the measure exists |
| `Measure.clinicalRecommendationStatement` | 0..1 | `markdown` | summary |  | Summary of clinical guidelines |
| `Measure.improvementNotation` | 0..1 | `CodeableConcept` | summary | required→measure-improvement-notation@4.0.1 | increase \| decrease |
| `Measure.definition` | 0..* | `markdown` | summary |  | Defined terms used in the measure documentation |
| `Measure.guidance` | 0..1 | `markdown` | summary |  | Additional guidance for implementers |
| `Measure.group` | 0..* | `BackboneElement` |  |  | Population criteria group |
| `Measure.group.code` | 0..1 | `CodeableConcept` |  |  | Meaning of the group |
| `Measure.group.description` | 0..1 | `string` |  |  | Summary description |
| `Measure.group.population` | 0..* | `BackboneElement` |  |  | Population criteria |
| `Measure.group.population.code` | 0..1 | `CodeableConcept` |  | extensible→measure-population | initial-population \| numerator \| numerator-exclusion \| denominator \| denominator-exclusion \| denominator-exception \| measure-population \| measure-population-exclusion \| measure-observation |
| `Measure.group.population.description` | 0..1 | `string` |  |  | The human readable description of this population criteria |
| `Measure.group.population.criteria` | 1..1 | `Expression` |  |  | The criteria that defines this population |
| `Measure.group.stratifier` | 0..* | `BackboneElement` |  |  | Stratifier criteria for the measure |
| `Measure.group.stratifier.code` | 0..1 | `CodeableConcept` |  |  | Meaning of the stratifier |
| `Measure.group.stratifier.description` | 0..1 | `string` |  |  | The human readable description of this stratifier |
| `Measure.group.stratifier.criteria` | 0..1 | `Expression` |  |  | How the measure should be stratified |
| `Measure.group.stratifier.component` | 0..* | `BackboneElement` |  |  | Stratifier criteria component for the measure |
| `Measure.group.stratifier.component.code` | 0..1 | `CodeableConcept` |  |  | Meaning of the stratifier component |
| `Measure.group.stratifier.component.description` | 0..1 | `string` |  |  | The human readable description of this stratifier component |
| `Measure.group.stratifier.component.criteria` | 1..1 | `Expression` |  |  | Component of how the measure should be stratified |
| `Measure.supplementalData` | 0..* | `BackboneElement` |  |  | What other data should be reported with the measure |
| `Measure.supplementalData.code` | 0..1 | `CodeableConcept` |  |  | Meaning of the supplemental data |
| `Measure.supplementalData.usage` | 0..* | `CodeableConcept` |  | extensible→measure-data-usage | supplemental-data \| risk-adjustment-factor |
| `Measure.supplementalData.description` | 0..1 | `string` |  |  | The human readable description of this supplemental data |
| `Measure.supplementalData.criteria` | 1..1 | `Expression` |  |  | Expression describing additional data to be reported |

Elements defined in ancestors: `Measure.id`, `Measure.meta`, `Measure.implicitRules`, `Measure.language`, `Measure.text`, `Measure.contained`, `Measure.extension`, `Measure.modifierExtension`, `Measure.group.id`, `Measure.group.extension`, `Measure.group.modifierExtension`, `Measure.group.population.id`, `Measure.group.population.extension`, `Measure.group.population.modifierExtension`, `Measure.group.stratifier.id`, `Measure.group.stratifier.extension`, `Measure.group.stratifier.modifierExtension`, `Measure.group.stratifier.component.id`, `Measure.group.stratifier.component.extension`, `Measure.group.stratifier.component.modifierExtension`, `Measure.supplementalData.id`, `Measure.supplementalData.extension`, `Measure.supplementalData.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `Measure` | `mea-0` | warning | Name should be usable as an identifier for the module by machine processing applications such as code generation | `name.matches('[A-Z]([A-Za-z0-9_]){0,254}')` |
| `Measure` | `mea-1` | error | Stratifier SHALL be either a single criteria or a set of criteria components | `group.stratifier.all((code \| description \| criteria).exists() xor component.exists())` |
