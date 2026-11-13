# Dosage

**ID** `Dosage` | **URL** `http://hl7.org/fhir/StructureDefinition/Dosage` | **Status** draft
**Base** `BackboneElement` | **Derivation** specialization | **Kind** complex-type
**Version** 4.0.1 | **Publisher** HL7 FHIR Standard | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Base StructureDefinition for Dosage Type: Indicates how the medication is/was taken or should be taken by the patient.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Dosage` | 0..* | `Dosage` |  |  | How the medication is/was taken or should be taken |
| `Dosage.sequence` | 0..1 | `integer` | summary |  | The order of the dosage instructions |
| `Dosage.text` | 0..1 | `string` | summary |  | Free text dosage instructions e.g. SIG |
| `Dosage.additionalInstruction` | 0..* | `CodeableConcept` | summary | example→additional-instruction-codes | Supplemental instruction or warnings to the patient - e.g. "with meals", "may cause drowsiness" |
| `Dosage.patientInstruction` | 0..1 | `string` | summary |  | Patient or consumer oriented instructions |
| `Dosage.timing` | 0..1 | `Timing` | summary |  | When medication should be administered |
| `Dosage.asNeeded[x]` | 0..1 | `boolean, CodeableConcept` | summary | example→medication-as-needed-reason | Take "as needed" (for x) |
| `Dosage.site` | 0..1 | `CodeableConcept` | summary | example→approach-site-codes | Body site to administer to |
| `Dosage.route` | 0..1 | `CodeableConcept` | summary | example→route-codes | How drug should enter body |
| `Dosage.method` | 0..1 | `CodeableConcept` | summary | example→administration-method-codes | Technique for administering medication |
| `Dosage.doseAndRate` | 0..* | `Element` | summary |  | Amount of medication administered |
| `Dosage.doseAndRate.type` | 0..1 | `CodeableConcept` | summary | example→dose-rate-type | The kind of dose or rate specified |
| `Dosage.doseAndRate.dose[x]` | 0..1 | `Range, Quantity(SimpleQuantity)` | summary |  | Amount of medication per dose |
| `Dosage.doseAndRate.rate[x]` | 0..1 | `Ratio, Range, Quantity(SimpleQuantity)` | summary |  | Amount of medication per unit of time |
| `Dosage.maxDosePerPeriod` | 0..1 | `Ratio` | summary |  | Upper limit on medication per unit of time |
| `Dosage.maxDosePerAdministration` | 0..1 | `Quantity(SimpleQuantity)` | summary |  | Upper limit on medication per administration |
| `Dosage.maxDosePerLifetime` | 0..1 | `Quantity(SimpleQuantity)` | summary |  | Upper limit on medication per lifetime of the patient |

Elements defined in ancestors: `Dosage.id`, `Dosage.extension`, `Dosage.modifierExtension`, `Dosage.doseAndRate.id`, `Dosage.doseAndRate.extension`

## Slices and fixed values

| Path | Card | Type | Fixed / pattern | Slicing |
| :--- | :--- | :--- | :--- | :--- |
| `Dosage.extension` | 0..* | `Extension` | — | discriminator value@url, rules=open |
| `Dosage.doseAndRate.extension` | 0..* | `Extension` | — | discriminator value@url, rules=open |

## Invariants

_No profile-specific invariants._
