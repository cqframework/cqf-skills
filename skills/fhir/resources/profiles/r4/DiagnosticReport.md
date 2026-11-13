# DiagnosticReport

**ID** `DiagnosticReport` | **URL** `http://hl7.org/fhir/StructureDefinition/DiagnosticReport` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Orders and Observations) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

The findings and interpretation of diagnostic tests performed on patients, groups of patients, devices, and locations, and/or specimens derived from these. The report includes clinical context such as requesting and provider information, and some mix of atomic results, images, textual and coded interpretations, and formatted representation of diagnostic reports.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DiagnosticReport` | 0..* | `DiagnosticReport` |  |  | A Diagnostic report - a combination of request information, atomic results, images, interpretation, as well as formatte… |
| `DiagnosticReport.identifier` | 0..* | `Identifier` | summary |  | Business identifier for report |
| `DiagnosticReport.basedOn` | 0..* | `Reference(CarePlan \| ImmunizationRecommendation \| MedicationRequest \| NutritionOrder \| ServiceRequest)` |  |  | What was requested |
| `DiagnosticReport.status` | 1..1 | `code` | modifier summary | required→diagnostic-report-status@4.0.1 | registered \| partial \| preliminary \| final + |
| `DiagnosticReport.category` | 0..* | `CodeableConcept` | summary | example→diagnostic-service-sections | Service category |
| `DiagnosticReport.code` | 1..1 | `CodeableConcept` | summary | preferred→report-codes | Name/Code for this diagnostic report |
| `DiagnosticReport.subject` | 0..1 | `Reference(Patient \| Group \| Device \| Location)` | summary |  | The subject of the report - usually, but not always, the patient |
| `DiagnosticReport.encounter` | 0..1 | `Reference(Encounter)` | summary |  | Health care event when test ordered |
| `DiagnosticReport.effective[x]` | 0..1 | `dateTime, Period` | summary |  | Clinically relevant time/time-period for report |
| `DiagnosticReport.issued` | 0..1 | `instant` | summary |  | DateTime this version was made |
| `DiagnosticReport.performer` | 0..* | `Reference(Practitioner \| PractitionerRole \| Organization \| CareTeam)` | summary |  | Responsible Diagnostic Service |
| `DiagnosticReport.resultsInterpreter` | 0..* | `Reference(Practitioner \| PractitionerRole \| Organization \| CareTeam)` | summary |  | Primary result interpreter |
| `DiagnosticReport.specimen` | 0..* | `Reference(Specimen)` |  |  | Specimens this report is based on |
| `DiagnosticReport.result` | 0..* | `Reference(Observation)` |  |  | Observations |
| `DiagnosticReport.imagingStudy` | 0..* | `Reference(ImagingStudy)` |  |  | Reference to full details of imaging associated with the diagnostic report |
| `DiagnosticReport.media` | 0..* | `BackboneElement` | summary |  | Key images associated with this report |
| `DiagnosticReport.media.comment` | 0..1 | `string` |  |  | Comment about the image (e.g. explanation) |
| `DiagnosticReport.media.link` | 1..1 | `Reference(Media)` | summary |  | Reference to the image source |
| `DiagnosticReport.conclusion` | 0..1 | `string` |  |  | Clinical conclusion (interpretation) of test results |
| `DiagnosticReport.conclusionCode` | 0..* | `CodeableConcept` |  | example→clinical-findings | Codes for the clinical conclusion of test results |
| `DiagnosticReport.presentedForm` | 0..* | `Attachment` |  |  | Entire report as issued |

Elements defined in ancestors: `DiagnosticReport.id`, `DiagnosticReport.meta`, `DiagnosticReport.implicitRules`, `DiagnosticReport.language`, `DiagnosticReport.text`, `DiagnosticReport.contained`, `DiagnosticReport.extension`, `DiagnosticReport.modifierExtension`, `DiagnosticReport.media.id`, `DiagnosticReport.media.extension`, `DiagnosticReport.media.modifierExtension`

## Invariants

_No profile-specific invariants._
