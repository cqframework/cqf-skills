# Immunization

**ID** `Immunization` | **URL** `http://hl7.org/fhir/StructureDefinition/Immunization` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Public Health and Emergency Response) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Describes the event of a patient being administered a vaccine or a record of an immunization as reported by a patient, a clinician or another party.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Immunization` | 0..* | `Immunization` |  |  | Immunization event information |
| `Immunization.identifier` | 0..* | `Identifier` |  |  | Business identifier |
| `Immunization.status` | 1..1 | `code` | modifier summary | required→immunization-status@4.0.1 | completed \| entered-in-error \| not-done |
| `Immunization.statusReason` | 0..1 | `CodeableConcept` |  | example→immunization-status-reason | Reason not done |
| `Immunization.vaccineCode` | 1..1 | `CodeableConcept` | summary | example→vaccine-code | Vaccine product administered |
| `Immunization.patient` | 1..1 | `Reference(Patient)` | summary |  | Who was immunized |
| `Immunization.encounter` | 0..1 | `Reference(Encounter)` |  |  | Encounter immunization was part of |
| `Immunization.occurrence[x]` | 1..1 | `dateTime, string` | summary |  | Vaccine administration date |
| `Immunization.recorded` | 0..1 | `dateTime` |  |  | When the immunization was first captured in the subject's record |
| `Immunization.primarySource` | 0..1 | `boolean` | summary |  | Indicates context the data was recorded in |
| `Immunization.reportOrigin` | 0..1 | `CodeableConcept` |  | example→immunization-origin | Indicates the source of a secondarily reported record |
| `Immunization.location` | 0..1 | `Reference(Location)` |  |  | Where immunization occurred |
| `Immunization.manufacturer` | 0..1 | `Reference(Organization)` |  |  | Vaccine manufacturer |
| `Immunization.lotNumber` | 0..1 | `string` |  |  | Vaccine lot number |
| `Immunization.expirationDate` | 0..1 | `date` |  |  | Vaccine expiration date |
| `Immunization.site` | 0..1 | `CodeableConcept` |  | example→immunization-site | Body site vaccine was administered |
| `Immunization.route` | 0..1 | `CodeableConcept` |  | example→immunization-route | How vaccine entered body |
| `Immunization.doseQuantity` | 0..1 | `Quantity(SimpleQuantity)` |  |  | Amount of vaccine administered |
| `Immunization.performer` | 0..* | `BackboneElement` | summary |  | Who performed event |
| `Immunization.performer.function` | 0..1 | `CodeableConcept` | summary | extensible→immunization-function | What type of performance was done |
| `Immunization.performer.actor` | 1..1 | `Reference(Practitioner \| PractitionerRole \| Organization)` | summary |  | Individual or organization who was performing |
| `Immunization.note` | 0..* | `Annotation` | summary |  | Additional immunization notes |
| `Immunization.reasonCode` | 0..* | `CodeableConcept` |  | example→immunization-reason | Why immunization occurred |
| `Immunization.reasonReference` | 0..* | `Reference(Condition \| Observation \| DiagnosticReport)` |  |  | Why immunization occurred |
| `Immunization.isSubpotent` | 0..1 | `boolean` | modifier summary |  | Dose potency |
| `Immunization.subpotentReason` | 0..* | `CodeableConcept` |  | example→immunization-subpotent-reason | Reason for being subpotent |
| `Immunization.education` | 0..* | `BackboneElement` |  |  | Educational material presented to patient |
| `Immunization.education.documentType` | 0..1 | `string` |  |  | Educational material document identifier |
| `Immunization.education.reference` | 0..1 | `uri` |  |  | Educational material reference pointer |
| `Immunization.education.publicationDate` | 0..1 | `dateTime` |  |  | Educational material publication date |
| `Immunization.education.presentationDate` | 0..1 | `dateTime` |  |  | Educational material presentation date |
| `Immunization.programEligibility` | 0..* | `CodeableConcept` |  | example→immunization-program-eligibility | Patient eligibility for a vaccination program |
| `Immunization.fundingSource` | 0..1 | `CodeableConcept` |  | example→immunization-funding-source | Funding source for the vaccine |
| `Immunization.reaction` | 0..* | `BackboneElement` |  |  | Details of a reaction that follows immunization |
| `Immunization.reaction.date` | 0..1 | `dateTime` |  |  | When reaction started |
| `Immunization.reaction.detail` | 0..1 | `Reference(Observation)` |  |  | Additional information on reaction |
| `Immunization.reaction.reported` | 0..1 | `boolean` |  |  | Indicates self-reported reaction |
| `Immunization.protocolApplied` | 0..* | `BackboneElement` |  |  | Protocol followed by the provider |
| `Immunization.protocolApplied.series` | 0..1 | `string` |  |  | Name of vaccine series |
| `Immunization.protocolApplied.authority` | 0..1 | `Reference(Organization)` |  |  | Who is responsible for publishing the recommendations |
| `Immunization.protocolApplied.targetDisease` | 0..* | `CodeableConcept` |  | example→immunization-target-disease | Vaccine preventatable disease being targetted |
| `Immunization.protocolApplied.doseNumber[x]` | 1..1 | `positiveInt, string` |  |  | Dose number within series |
| `Immunization.protocolApplied.seriesDoses[x]` | 0..1 | `positiveInt, string` |  |  | Recommended number of doses for immunity |

Elements defined in ancestors: `Immunization.id`, `Immunization.meta`, `Immunization.implicitRules`, `Immunization.language`, `Immunization.text`, `Immunization.contained`, `Immunization.extension`, `Immunization.modifierExtension`, `Immunization.performer.id`, `Immunization.performer.extension`, `Immunization.performer.modifierExtension`, `Immunization.education.id`, `Immunization.education.extension`, `Immunization.education.modifierExtension`, `Immunization.reaction.id`, `Immunization.reaction.extension`, `Immunization.reaction.modifierExtension`, `Immunization.protocolApplied.id`, `Immunization.protocolApplied.extension`, `Immunization.protocolApplied.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `Immunization.education` | `imm-1` | error | One of documentType or reference SHALL be present | `documentType.exists() or reference.exists()` |
