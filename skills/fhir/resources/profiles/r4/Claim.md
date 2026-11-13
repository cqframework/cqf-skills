# Claim

**ID** `Claim` | **URL** `http://hl7.org/fhir/StructureDefinition/Claim` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Financial Management) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

A provider issued list of professional services and products which have been provided, or are to be provided, to a patient which is sent to an insurer for reimbursement.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Claim` | 0..* | `Claim` |  |  | Claim, Pre-determination or Pre-authorization |
| `Claim.identifier` | 0..* | `Identifier` |  |  | Business Identifier for claim |
| `Claim.status` | 1..1 | `code` | modifier summary | required→fm-status@4.0.1 | active \| cancelled \| draft \| entered-in-error |
| `Claim.type` | 1..1 | `CodeableConcept` | summary | extensible→claim-type | Category or discipline |
| `Claim.subType` | 0..1 | `CodeableConcept` |  | example→claim-subtype | More granular claim type |
| `Claim.use` | 1..1 | `code` | summary | required→claim-use@4.0.1 | claim \| preauthorization \| predetermination |
| `Claim.patient` | 1..1 | `Reference(Patient)` | summary |  | The recipient of the products and services |
| `Claim.billablePeriod` | 0..1 | `Period` | summary |  | Relevant time frame for the claim |
| `Claim.created` | 1..1 | `dateTime` | summary |  | Resource creation date |
| `Claim.enterer` | 0..1 | `Reference(Practitioner \| PractitionerRole)` |  |  | Author of the claim |
| `Claim.insurer` | 0..1 | `Reference(Organization)` | summary |  | Target |
| `Claim.provider` | 1..1 | `Reference(Practitioner \| PractitionerRole \| Organization)` | summary |  | Party responsible for the claim |
| `Claim.priority` | 1..1 | `CodeableConcept` | summary | example→process-priority | Desired processing ugency |
| `Claim.fundsReserve` | 0..1 | `CodeableConcept` |  | example→fundsreserve | For whom to reserve funds |
| `Claim.related` | 0..* | `BackboneElement` |  |  | Prior or corollary claims |
| `Claim.related.claim` | 0..1 | `Reference(Claim)` |  |  | Reference to the related claim |
| `Claim.related.relationship` | 0..1 | `CodeableConcept` |  | example→related-claim-relationship | How the reference claim is related |
| `Claim.related.reference` | 0..1 | `Identifier` |  |  | File or case reference |
| `Claim.prescription` | 0..1 | `Reference(DeviceRequest \| MedicationRequest \| VisionPrescription)` |  |  | Prescription authorizing services and products |
| `Claim.originalPrescription` | 0..1 | `Reference(DeviceRequest \| MedicationRequest \| VisionPrescription)` |  |  | Original prescription if superseded by fulfiller |
| `Claim.payee` | 0..1 | `BackboneElement` |  |  | Recipient of benefits payable |
| `Claim.payee.type` | 1..1 | `CodeableConcept` |  | example→payeetype | Category of recipient |
| `Claim.payee.party` | 0..1 | `Reference(Practitioner \| PractitionerRole \| Organization \| Patient \| RelatedPerson)` |  |  | Recipient reference |
| `Claim.referral` | 0..1 | `Reference(ServiceRequest)` |  |  | Treatment referral |
| `Claim.facility` | 0..1 | `Reference(Location)` |  |  | Servicing facility |
| `Claim.careTeam` | 0..* | `BackboneElement` |  |  | Members of the care team |
| `Claim.careTeam.sequence` | 1..1 | `positiveInt` |  |  | Order of care team |
| `Claim.careTeam.provider` | 1..1 | `Reference(Practitioner \| PractitionerRole \| Organization)` |  |  | Practitioner or organization |
| `Claim.careTeam.responsible` | 0..1 | `boolean` |  |  | Indicator of the lead practitioner |
| `Claim.careTeam.role` | 0..1 | `CodeableConcept` |  | example→claim-careteamrole | Function within the team |
| `Claim.careTeam.qualification` | 0..1 | `CodeableConcept` |  | example→provider-qualification | Practitioner credential or specialization |
| `Claim.supportingInfo` | 0..* | `BackboneElement` |  |  | Supporting information |
| `Claim.supportingInfo.sequence` | 1..1 | `positiveInt` |  |  | Information instance identifier |
| `Claim.supportingInfo.category` | 1..1 | `CodeableConcept` |  | example→claim-informationcategory | Classification of the supplied information |
| `Claim.supportingInfo.code` | 0..1 | `CodeableConcept` |  | example→claim-exception | Type of information |
| `Claim.supportingInfo.timing[x]` | 0..1 | `date, Period` |  |  | When it occurred |
| `Claim.supportingInfo.value[x]` | 0..1 | `boolean, string, Quantity, Attachment, Reference(Resource)` |  |  | Data to be provided |
| `Claim.supportingInfo.reason` | 0..1 | `CodeableConcept` |  | example→missing-tooth-reason | Explanation for the information |
| `Claim.diagnosis` | 0..* | `BackboneElement` |  |  | Pertinent diagnosis information |
| `Claim.diagnosis.sequence` | 1..1 | `positiveInt` |  |  | Diagnosis instance identifier |
| `Claim.diagnosis.diagnosis[x]` | 1..1 | `CodeableConcept, Reference(Condition)` |  | example→icd-10 | Nature of illness or problem |
| `Claim.diagnosis.type` | 0..* | `CodeableConcept` |  | example→ex-diagnosistype | Timing or nature of the diagnosis |
| `Claim.diagnosis.onAdmission` | 0..1 | `CodeableConcept` |  | example→ex-diagnosis-on-admission | Present on admission |
| `Claim.diagnosis.packageCode` | 0..1 | `CodeableConcept` |  | example→ex-diagnosisrelatedgroup | Package billing code |
| `Claim.procedure` | 0..* | `BackboneElement` |  |  | Clinical procedures performed |
| `Claim.procedure.sequence` | 1..1 | `positiveInt` |  |  | Procedure instance identifier |
| `Claim.procedure.type` | 0..* | `CodeableConcept` |  | example→ex-procedure-type | Category of Procedure |
| `Claim.procedure.date` | 0..1 | `dateTime` |  |  | When the procedure was performed |
| `Claim.procedure.procedure[x]` | 1..1 | `CodeableConcept, Reference(Procedure)` |  | example→icd-10-procedures | Specific clinical procedure |
| `Claim.procedure.udi` | 0..* | `Reference(Device)` |  |  | Unique device identifier |
| `Claim.insurance` | 1..* | `BackboneElement` | summary |  | Patient insurance information |
| `Claim.insurance.sequence` | 1..1 | `positiveInt` | summary |  | Insurance instance identifier |
| `Claim.insurance.focal` | 1..1 | `boolean` | summary |  | Coverage to be used for adjudication |
| `Claim.insurance.identifier` | 0..1 | `Identifier` |  |  | Pre-assigned Claim number |
| `Claim.insurance.coverage` | 1..1 | `Reference(Coverage)` | summary |  | Insurance information |
| `Claim.insurance.businessArrangement` | 0..1 | `string` |  |  | Additional provider contract number |
| `Claim.insurance.preAuthRef` | 0..* | `string` |  |  | Prior authorization reference number |
| `Claim.insurance.claimResponse` | 0..1 | `Reference(ClaimResponse)` |  |  | Adjudication results |
| `Claim.accident` | 0..1 | `BackboneElement` |  |  | Details of the event |
| `Claim.accident.date` | 1..1 | `date` |  |  | When the incident occurred |
| `Claim.accident.type` | 0..1 | `CodeableConcept` |  | extensible→v3-ActIncidentCode | The nature of the accident |
| `Claim.accident.location[x]` | 0..1 | `Address, Reference(Location)` |  |  | Where the event occurred |
| `Claim.item` | 0..* | `BackboneElement` |  |  | Product or service provided |
| `Claim.item.sequence` | 1..1 | `positiveInt` |  |  | Item instance identifier |
| `Claim.item.careTeamSequence` | 0..* | `positiveInt` |  |  | Applicable careTeam members |
| `Claim.item.diagnosisSequence` | 0..* | `positiveInt` |  |  | Applicable diagnoses |
| `Claim.item.procedureSequence` | 0..* | `positiveInt` |  |  | Applicable procedures |
| `Claim.item.informationSequence` | 0..* | `positiveInt` |  |  | Applicable exception and supporting information |
| `Claim.item.revenue` | 0..1 | `CodeableConcept` |  | example→ex-revenue-center | Revenue or cost center code |
| `Claim.item.category` | 0..1 | `CodeableConcept` |  | example→ex-benefitcategory | Benefit classification |
| `Claim.item.productOrService` | 1..1 | `CodeableConcept` |  | example→service-uscls | Billing, service, product, or drug code |
| `Claim.item.modifier` | 0..* | `CodeableConcept` |  | example→claim-modifiers | Product or service billing modifiers |
| `Claim.item.programCode` | 0..* | `CodeableConcept` |  | example→ex-program-code | Program the product or service is provided under |
| `Claim.item.serviced[x]` | 0..1 | `date, Period` |  |  | Date or dates of service or product delivery |
| `Claim.item.location[x]` | 0..1 | `CodeableConcept, Address, Reference(Location)` |  | example→service-place | Place of service or where product was supplied |
| `Claim.item.quantity` | 0..1 | `Quantity(SimpleQuantity)` |  |  | Count of products or services |
| `Claim.item.unitPrice` | 0..1 | `Money` |  |  | Fee, charge or cost per item |
| `Claim.item.factor` | 0..1 | `decimal` |  |  | Price scaling factor |
| `Claim.item.net` | 0..1 | `Money` |  |  | Total item cost |
| `Claim.item.udi` | 0..* | `Reference(Device)` |  |  | Unique device identifier |
| `Claim.item.bodySite` | 0..1 | `CodeableConcept` |  | example→tooth | Anatomical location |
| `Claim.item.subSite` | 0..* | `CodeableConcept` |  | example→surface | Anatomical sub-location |
| `Claim.item.encounter` | 0..* | `Reference(Encounter)` |  |  | Encounters related to this billed item |
| `Claim.item.detail` | 0..* | `BackboneElement` |  |  | Product or service provided |
| `Claim.item.detail.sequence` | 1..1 | `positiveInt` |  |  | Item instance identifier |
| `Claim.item.detail.revenue` | 0..1 | `CodeableConcept` |  | example→ex-revenue-center | Revenue or cost center code |
| `Claim.item.detail.category` | 0..1 | `CodeableConcept` |  | example→ex-benefitcategory | Benefit classification |
| `Claim.item.detail.productOrService` | 1..1 | `CodeableConcept` |  | example→service-uscls | Billing, service, product, or drug code |
| `Claim.item.detail.modifier` | 0..* | `CodeableConcept` |  | example→claim-modifiers | Service/Product billing modifiers |
| `Claim.item.detail.programCode` | 0..* | `CodeableConcept` |  | example→ex-program-code | Program the product or service is provided under |
| `Claim.item.detail.quantity` | 0..1 | `Quantity(SimpleQuantity)` |  |  | Count of products or services |
| `Claim.item.detail.unitPrice` | 0..1 | `Money` |  |  | Fee, charge or cost per item |
| `Claim.item.detail.factor` | 0..1 | `decimal` |  |  | Price scaling factor |
| `Claim.item.detail.net` | 0..1 | `Money` |  |  | Total item cost |
| `Claim.item.detail.udi` | 0..* | `Reference(Device)` |  |  | Unique device identifier |
| `Claim.item.detail.subDetail` | 0..* | `BackboneElement` |  |  | Product or service provided |
| `Claim.item.detail.subDetail.sequence` | 1..1 | `positiveInt` |  |  | Item instance identifier |
| `Claim.item.detail.subDetail.revenue` | 0..1 | `CodeableConcept` |  | example→ex-revenue-center | Revenue or cost center code |
| `Claim.item.detail.subDetail.category` | 0..1 | `CodeableConcept` |  | example→ex-benefitcategory | Benefit classification |
| `Claim.item.detail.subDetail.productOrService` | 1..1 | `CodeableConcept` |  | example→service-uscls | Billing, service, product, or drug code |
| `Claim.item.detail.subDetail.modifier` | 0..* | `CodeableConcept` |  | example→claim-modifiers | Service/Product billing modifiers |
| `Claim.item.detail.subDetail.programCode` | 0..* | `CodeableConcept` |  | example→ex-program-code | Program the product or service is provided under |
| `Claim.item.detail.subDetail.quantity` | 0..1 | `Quantity(SimpleQuantity)` |  |  | Count of products or services |
| `Claim.item.detail.subDetail.unitPrice` | 0..1 | `Money` |  |  | Fee, charge or cost per item |
| `Claim.item.detail.subDetail.factor` | 0..1 | `decimal` |  |  | Price scaling factor |
| `Claim.item.detail.subDetail.net` | 0..1 | `Money` |  |  | Total item cost |
| `Claim.item.detail.subDetail.udi` | 0..* | `Reference(Device)` |  |  | Unique device identifier |
| `Claim.total` | 0..1 | `Money` |  |  | Total claim cost |

Elements defined in ancestors: `Claim.id`, `Claim.meta`, `Claim.implicitRules`, `Claim.language`, `Claim.text`, `Claim.contained`, `Claim.extension`, `Claim.modifierExtension`, `Claim.related.id`, `Claim.related.extension`, `Claim.related.modifierExtension`, `Claim.payee.id`, `Claim.payee.extension`, `Claim.payee.modifierExtension`, `Claim.careTeam.id`, `Claim.careTeam.extension`, `Claim.careTeam.modifierExtension`, `Claim.supportingInfo.id`, `Claim.supportingInfo.extension`, `Claim.supportingInfo.modifierExtension`, `Claim.diagnosis.id`, `Claim.diagnosis.extension`, `Claim.diagnosis.modifierExtension`, `Claim.procedure.id`, `Claim.procedure.extension`, `Claim.procedure.modifierExtension`, `Claim.insurance.id`, `Claim.insurance.extension`, `Claim.insurance.modifierExtension`, `Claim.accident.id`, `Claim.accident.extension`, `Claim.accident.modifierExtension`, `Claim.item.id`, `Claim.item.extension`, `Claim.item.modifierExtension`, `Claim.item.detail.id`, `Claim.item.detail.extension`, `Claim.item.detail.modifierExtension`, `Claim.item.detail.subDetail.id`, `Claim.item.detail.subDetail.extension`, `Claim.item.detail.subDetail.modifierExtension`

## Invariants

_No profile-specific invariants._
