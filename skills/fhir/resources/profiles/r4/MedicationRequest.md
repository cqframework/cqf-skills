# MedicationRequest

**ID** `MedicationRequest` | **URL** `http://hl7.org/fhir/StructureDefinition/MedicationRequest` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Pharmacy) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

An order or request for both supply of the medication and the instructions for administration of the medication to a patient. The resource is called "MedicationRequest" rather than "MedicationPrescription" or "MedicationOrder" to generalize the use across inpatient and outpatient settings, including care plans, etc., and to harmonize with workflow patterns.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `MedicationRequest` | 0..* | `MedicationRequest` |  |  | Ordering of medication for patient or group |
| `MedicationRequest.identifier` | 0..* | `Identifier` |  |  | External ids for this request |
| `MedicationRequest.status` | 1..1 | `code` | modifier summary | required→medicationrequest-status@4.0.1 | active \| on-hold \| cancelled \| completed \| entered-in-error \| stopped \| draft \| unknown |
| `MedicationRequest.statusReason` | 0..1 | `CodeableConcept` |  | example→medicationrequest-status-reason | Reason for current status |
| `MedicationRequest.intent` | 1..1 | `code` | modifier summary | required→medicationrequest-intent@4.0.1 | proposal \| plan \| order \| original-order \| reflex-order \| filler-order \| instance-order \| option |
| `MedicationRequest.category` | 0..* | `CodeableConcept` |  | example→medicationrequest-category | Type of medication usage |
| `MedicationRequest.priority` | 0..1 | `code` | summary | required→request-priority@4.0.1 | routine \| urgent \| asap \| stat |
| `MedicationRequest.doNotPerform` | 0..1 | `boolean` | modifier summary |  | True if request is prohibiting action |
| `MedicationRequest.reported[x]` | 0..1 | `boolean, Reference(Patient \| Practitioner \| PractitionerRole \| RelatedPerson \| Organization)` | summary |  | Reported rather than primary record |
| `MedicationRequest.medication[x]` | 1..1 | `CodeableConcept, Reference(Medication)` | summary | example→medication-codes | Medication to be taken |
| `MedicationRequest.subject` | 1..1 | `Reference(Patient \| Group)` | summary |  | Who or group medication request is for |
| `MedicationRequest.encounter` | 0..1 | `Reference(Encounter)` |  |  | Encounter created as part of encounter/admission/stay |
| `MedicationRequest.supportingInformation` | 0..* | `Reference(Resource)` |  |  | Information to support ordering of the medication |
| `MedicationRequest.authoredOn` | 0..1 | `dateTime` | summary |  | When request was initially authored |
| `MedicationRequest.requester` | 0..1 | `Reference(Practitioner \| PractitionerRole \| Organization \| Patient \| RelatedPerson \| Device)` | summary |  | Who/What requested the Request |
| `MedicationRequest.performer` | 0..1 | `Reference(Practitioner \| PractitionerRole \| Organization \| Patient \| Device \| RelatedPerson \| CareTeam)` |  |  | Intended performer of administration |
| `MedicationRequest.performerType` | 0..1 | `CodeableConcept` | summary | example→performer-role | Desired kind of performer of the medication administration |
| `MedicationRequest.recorder` | 0..1 | `Reference(Practitioner \| PractitionerRole)` |  |  | Person who entered the request |
| `MedicationRequest.reasonCode` | 0..* | `CodeableConcept` |  | example→condition-code | Reason or indication for ordering or not ordering the medication |
| `MedicationRequest.reasonReference` | 0..* | `Reference(Condition \| Observation)` |  |  | Condition or observation that supports why the prescription is being written |
| `MedicationRequest.instantiatesCanonical` | 0..* | `canonical` | summary |  | Instantiates FHIR protocol or definition |
| `MedicationRequest.instantiatesUri` | 0..* | `uri` | summary |  | Instantiates external protocol or definition |
| `MedicationRequest.basedOn` | 0..* | `Reference(CarePlan \| MedicationRequest \| ServiceRequest \| ImmunizationRecommendation)` | summary |  | What request fulfills |
| `MedicationRequest.groupIdentifier` | 0..1 | `Identifier` | summary |  | Composite request this is part of |
| `MedicationRequest.courseOfTherapyType` | 0..1 | `CodeableConcept` |  | example→medicationrequest-course-of-therapy | Overall pattern of medication administration |
| `MedicationRequest.insurance` | 0..* | `Reference(Coverage \| ClaimResponse)` |  |  | Associated insurance coverage |
| `MedicationRequest.note` | 0..* | `Annotation` |  |  | Information about the prescription |
| `MedicationRequest.dosageInstruction` | 0..* | `Dosage` |  |  | How the medication should be taken |
| `MedicationRequest.dispenseRequest` | 0..1 | `BackboneElement` |  |  | Medication supply authorization |
| `MedicationRequest.dispenseRequest.initialFill` | 0..1 | `BackboneElement` |  |  | First fill details |
| `MedicationRequest.dispenseRequest.initialFill.quantity` | 0..1 | `Quantity(SimpleQuantity)` |  |  | First fill quantity |
| `MedicationRequest.dispenseRequest.initialFill.duration` | 0..1 | `Duration` |  |  | First fill duration |
| `MedicationRequest.dispenseRequest.dispenseInterval` | 0..1 | `Duration` |  |  | Minimum period of time between dispenses |
| `MedicationRequest.dispenseRequest.validityPeriod` | 0..1 | `Period` |  |  | Time period supply is authorized for |
| `MedicationRequest.dispenseRequest.numberOfRepeatsAllowed` | 0..1 | `unsignedInt` |  |  | Number of refills authorized |
| `MedicationRequest.dispenseRequest.quantity` | 0..1 | `Quantity(SimpleQuantity)` |  |  | Amount of medication to supply per dispense |
| `MedicationRequest.dispenseRequest.expectedSupplyDuration` | 0..1 | `Duration` |  |  | Number of days supply per dispense |
| `MedicationRequest.dispenseRequest.performer` | 0..1 | `Reference(Organization)` |  |  | Intended dispenser |
| `MedicationRequest.substitution` | 0..1 | `BackboneElement` |  |  | Any restrictions on medication substitution |
| `MedicationRequest.substitution.allowed[x]` | 1..1 | `boolean, CodeableConcept` |  | example→v3-ActSubstanceAdminSubstitutionCode | Whether substitution is allowed or not |
| `MedicationRequest.substitution.reason` | 0..1 | `CodeableConcept` |  | example→v3-SubstanceAdminSubstitutionReason | Why should (not) substitution be made |
| `MedicationRequest.priorPrescription` | 0..1 | `Reference(MedicationRequest)` |  |  | An order/prescription that is being replaced |
| `MedicationRequest.detectedIssue` | 0..* | `Reference(DetectedIssue)` |  |  | Clinical Issue with action |
| `MedicationRequest.eventHistory` | 0..* | `Reference(Provenance)` |  |  | A list of events of interest in the lifecycle |

Elements defined in ancestors: `MedicationRequest.id`, `MedicationRequest.meta`, `MedicationRequest.implicitRules`, `MedicationRequest.language`, `MedicationRequest.text`, `MedicationRequest.contained`, `MedicationRequest.extension`, `MedicationRequest.modifierExtension`, `MedicationRequest.dispenseRequest.id`, `MedicationRequest.dispenseRequest.extension`, `MedicationRequest.dispenseRequest.modifierExtension`, `MedicationRequest.dispenseRequest.initialFill.id`, `MedicationRequest.dispenseRequest.initialFill.extension`, `MedicationRequest.dispenseRequest.initialFill.modifierExtension`, `MedicationRequest.substitution.id`, `MedicationRequest.substitution.extension`, `MedicationRequest.substitution.modifierExtension`

## Invariants

_No profile-specific invariants._
