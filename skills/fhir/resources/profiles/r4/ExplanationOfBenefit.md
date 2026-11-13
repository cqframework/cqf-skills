# ExplanationOfBenefit

**ID** `ExplanationOfBenefit` | **URL** `http://hl7.org/fhir/StructureDefinition/ExplanationOfBenefit` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Financial Management) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

This resource provides: the claim details; adjudication details from the processing of a Claim; and optionally account balance information, for informing the subscriber of the benefits provided.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ExplanationOfBenefit` | 0..* | `ExplanationOfBenefit` |  |  | Explanation of Benefit resource |
| `ExplanationOfBenefit.identifier` | 0..* | `Identifier` |  |  | Business Identifier for the resource |
| `ExplanationOfBenefit.status` | 1..1 | `code` | modifier summary | required→explanationofbenefit-status@4.0.1 | active \| cancelled \| draft \| entered-in-error |
| `ExplanationOfBenefit.type` | 1..1 | `CodeableConcept` | summary | extensible→claim-type | Category or discipline |
| `ExplanationOfBenefit.subType` | 0..1 | `CodeableConcept` |  | example→claim-subtype | More granular claim type |
| `ExplanationOfBenefit.use` | 1..1 | `code` | summary | required→claim-use@4.0.1 | claim \| preauthorization \| predetermination |
| `ExplanationOfBenefit.patient` | 1..1 | `Reference(Patient)` | summary |  | The recipient of the products and services |
| `ExplanationOfBenefit.billablePeriod` | 0..1 | `Period` | summary |  | Relevant time frame for the claim |
| `ExplanationOfBenefit.created` | 1..1 | `dateTime` | summary |  | Response creation date |
| `ExplanationOfBenefit.enterer` | 0..1 | `Reference(Practitioner \| PractitionerRole)` |  |  | Author of the claim |
| `ExplanationOfBenefit.insurer` | 1..1 | `Reference(Organization)` | summary |  | Party responsible for reimbursement |
| `ExplanationOfBenefit.provider` | 1..1 | `Reference(Practitioner \| PractitionerRole \| Organization)` | summary |  | Party responsible for the claim |
| `ExplanationOfBenefit.priority` | 0..1 | `CodeableConcept` |  | example→processpriority | Desired processing urgency |
| `ExplanationOfBenefit.fundsReserveRequested` | 0..1 | `CodeableConcept` |  | example→fundsreserve | For whom to reserve funds |
| `ExplanationOfBenefit.fundsReserve` | 0..1 | `CodeableConcept` |  | example→fundsreserve | Funds reserved status |
| `ExplanationOfBenefit.related` | 0..* | `BackboneElement` |  |  | Prior or corollary claims |
| `ExplanationOfBenefit.related.claim` | 0..1 | `Reference(Claim)` |  |  | Reference to the related claim |
| `ExplanationOfBenefit.related.relationship` | 0..1 | `CodeableConcept` |  | example→related-claim-relationship | How the reference claim is related |
| `ExplanationOfBenefit.related.reference` | 0..1 | `Identifier` |  |  | File or case reference |
| `ExplanationOfBenefit.prescription` | 0..1 | `Reference(MedicationRequest \| VisionPrescription)` |  |  | Prescription authorizing services or products |
| `ExplanationOfBenefit.originalPrescription` | 0..1 | `Reference(MedicationRequest)` |  |  | Original prescription if superceded by fulfiller |
| `ExplanationOfBenefit.payee` | 0..1 | `BackboneElement` |  |  | Recipient of benefits payable |
| `ExplanationOfBenefit.payee.type` | 0..1 | `CodeableConcept` |  | example→payeetype | Category of recipient |
| `ExplanationOfBenefit.payee.party` | 0..1 | `Reference(Practitioner \| PractitionerRole \| Organization \| Patient \| RelatedPerson)` |  |  | Recipient reference |
| `ExplanationOfBenefit.referral` | 0..1 | `Reference(ServiceRequest)` |  |  | Treatment Referral |
| `ExplanationOfBenefit.facility` | 0..1 | `Reference(Location)` |  |  | Servicing Facility |
| `ExplanationOfBenefit.claim` | 0..1 | `Reference(Claim)` |  |  | Claim reference |
| `ExplanationOfBenefit.claimResponse` | 0..1 | `Reference(ClaimResponse)` |  |  | Claim response reference |
| `ExplanationOfBenefit.outcome` | 1..1 | `code` | summary | required→remittance-outcome@4.0.1 | queued \| complete \| error \| partial |
| `ExplanationOfBenefit.disposition` | 0..1 | `string` |  |  | Disposition Message |
| `ExplanationOfBenefit.preAuthRef` | 0..* | `string` |  |  | Preauthorization reference |
| `ExplanationOfBenefit.preAuthRefPeriod` | 0..* | `Period` |  |  | Preauthorization in-effect period |
| `ExplanationOfBenefit.careTeam` | 0..* | `BackboneElement` |  |  | Care Team members |
| `ExplanationOfBenefit.careTeam.sequence` | 1..1 | `positiveInt` |  |  | Order of care team |
| `ExplanationOfBenefit.careTeam.provider` | 1..1 | `Reference(Practitioner \| PractitionerRole \| Organization)` |  |  | Practitioner or organization |
| `ExplanationOfBenefit.careTeam.responsible` | 0..1 | `boolean` |  |  | Indicator of the lead practitioner |
| `ExplanationOfBenefit.careTeam.role` | 0..1 | `CodeableConcept` |  | example→claim-careteamrole | Function within the team |
| `ExplanationOfBenefit.careTeam.qualification` | 0..1 | `CodeableConcept` |  | example→provider-qualification | Practitioner credential or specialization |
| `ExplanationOfBenefit.supportingInfo` | 0..* | `BackboneElement` |  |  | Supporting information |
| `ExplanationOfBenefit.supportingInfo.sequence` | 1..1 | `positiveInt` |  |  | Information instance identifier |
| `ExplanationOfBenefit.supportingInfo.category` | 1..1 | `CodeableConcept` |  | example→claim-informationcategory | Classification of the supplied information |
| `ExplanationOfBenefit.supportingInfo.code` | 0..1 | `CodeableConcept` |  | example→claim-exception | Type of information |
| `ExplanationOfBenefit.supportingInfo.timing[x]` | 0..1 | `date, Period` |  |  | When it occurred |
| `ExplanationOfBenefit.supportingInfo.value[x]` | 0..1 | `boolean, string, Quantity, Attachment, Reference(Resource)` |  |  | Data to be provided |
| `ExplanationOfBenefit.supportingInfo.reason` | 0..1 | `Coding` |  | example→missing-tooth-reason | Explanation for the information |
| `ExplanationOfBenefit.diagnosis` | 0..* | `BackboneElement` |  |  | Pertinent diagnosis information |
| `ExplanationOfBenefit.diagnosis.sequence` | 1..1 | `positiveInt` |  |  | Diagnosis instance identifier |
| `ExplanationOfBenefit.diagnosis.diagnosis[x]` | 1..1 | `CodeableConcept, Reference(Condition)` |  | example→icd-10 | Nature of illness or problem |
| `ExplanationOfBenefit.diagnosis.type` | 0..* | `CodeableConcept` |  | example→ex-diagnosistype | Timing or nature of the diagnosis |
| `ExplanationOfBenefit.diagnosis.onAdmission` | 0..1 | `CodeableConcept` |  | example→ex-diagnosis-on-admission | Present on admission |
| `ExplanationOfBenefit.diagnosis.packageCode` | 0..1 | `CodeableConcept` |  | example→ex-diagnosisrelatedgroup | Package billing code |
| `ExplanationOfBenefit.procedure` | 0..* | `BackboneElement` |  |  | Clinical procedures performed |
| `ExplanationOfBenefit.procedure.sequence` | 1..1 | `positiveInt` |  |  | Procedure instance identifier |
| `ExplanationOfBenefit.procedure.type` | 0..* | `CodeableConcept` |  | example→ex-procedure-type | Category of Procedure |
| `ExplanationOfBenefit.procedure.date` | 0..1 | `dateTime` |  |  | When the procedure was performed |
| `ExplanationOfBenefit.procedure.procedure[x]` | 1..1 | `CodeableConcept, Reference(Procedure)` |  | example→icd-10-procedures | Specific clinical procedure |
| `ExplanationOfBenefit.procedure.udi` | 0..* | `Reference(Device)` |  |  | Unique device identifier |
| `ExplanationOfBenefit.precedence` | 0..1 | `positiveInt` |  |  | Precedence (primary, secondary, etc.) |
| `ExplanationOfBenefit.insurance` | 1..* | `BackboneElement` | summary |  | Patient insurance information |
| `ExplanationOfBenefit.insurance.focal` | 1..1 | `boolean` | summary |  | Coverage to be used for adjudication |
| `ExplanationOfBenefit.insurance.coverage` | 1..1 | `Reference(Coverage)` | summary |  | Insurance information |
| `ExplanationOfBenefit.insurance.preAuthRef` | 0..* | `string` |  |  | Prior authorization reference number |
| `ExplanationOfBenefit.accident` | 0..1 | `BackboneElement` |  |  | Details of the event |
| `ExplanationOfBenefit.accident.date` | 0..1 | `date` |  |  | When the incident occurred |
| `ExplanationOfBenefit.accident.type` | 0..1 | `CodeableConcept` |  | extensible→v3-ActIncidentCode | The nature of the accident |
| `ExplanationOfBenefit.accident.location[x]` | 0..1 | `Address, Reference(Location)` |  |  | Where the event occurred |
| `ExplanationOfBenefit.item` | 0..* | `BackboneElement` |  |  | Product or service provided |
| `ExplanationOfBenefit.item.sequence` | 1..1 | `positiveInt` |  |  | Item instance identifier |
| `ExplanationOfBenefit.item.careTeamSequence` | 0..* | `positiveInt` |  |  | Applicable care team members |
| `ExplanationOfBenefit.item.diagnosisSequence` | 0..* | `positiveInt` |  |  | Applicable diagnoses |
| `ExplanationOfBenefit.item.procedureSequence` | 0..* | `positiveInt` |  |  | Applicable procedures |
| `ExplanationOfBenefit.item.informationSequence` | 0..* | `positiveInt` |  |  | Applicable exception and supporting information |
| `ExplanationOfBenefit.item.revenue` | 0..1 | `CodeableConcept` |  | example→ex-revenue-center | Revenue or cost center code |
| `ExplanationOfBenefit.item.category` | 0..1 | `CodeableConcept` |  | example→ex-benefitcategory | Benefit classification |
| `ExplanationOfBenefit.item.productOrService` | 1..1 | `CodeableConcept` |  | example→service-uscls | Billing, service, product, or drug code |
| `ExplanationOfBenefit.item.modifier` | 0..* | `CodeableConcept` |  | example→claim-modifiers | Product or service billing modifiers |
| `ExplanationOfBenefit.item.programCode` | 0..* | `CodeableConcept` |  | example→ex-program-code | Program the product or service is provided under |
| `ExplanationOfBenefit.item.serviced[x]` | 0..1 | `date, Period` |  |  | Date or dates of service or product delivery |
| `ExplanationOfBenefit.item.location[x]` | 0..1 | `CodeableConcept, Address, Reference(Location)` |  | example→service-place | Place of service or where product was supplied |
| `ExplanationOfBenefit.item.quantity` | 0..1 | `Quantity(SimpleQuantity)` |  |  | Count of products or services |
| `ExplanationOfBenefit.item.unitPrice` | 0..1 | `Money` |  |  | Fee, charge or cost per item |
| `ExplanationOfBenefit.item.factor` | 0..1 | `decimal` |  |  | Price scaling factor |
| `ExplanationOfBenefit.item.net` | 0..1 | `Money` |  |  | Total item cost |
| `ExplanationOfBenefit.item.udi` | 0..* | `Reference(Device)` |  |  | Unique device identifier |
| `ExplanationOfBenefit.item.bodySite` | 0..1 | `CodeableConcept` |  | example→tooth | Anatomical location |
| `ExplanationOfBenefit.item.subSite` | 0..* | `CodeableConcept` |  | example→surface | Anatomical sub-location |
| `ExplanationOfBenefit.item.encounter` | 0..* | `Reference(Encounter)` |  |  | Encounters related to this billed item |
| `ExplanationOfBenefit.item.noteNumber` | 0..* | `positiveInt` |  |  | Applicable note numbers |
| `ExplanationOfBenefit.item.adjudication` | 0..* | `BackboneElement` |  |  | Adjudication details |
| `ExplanationOfBenefit.item.adjudication.category` | 1..1 | `CodeableConcept` |  | example→adjudication | Type of adjudication information |
| `ExplanationOfBenefit.item.adjudication.reason` | 0..1 | `CodeableConcept` |  | example→adjudication-reason | Explanation of adjudication outcome |
| `ExplanationOfBenefit.item.adjudication.amount` | 0..1 | `Money` |  |  | Monetary amount |
| `ExplanationOfBenefit.item.adjudication.value` | 0..1 | `decimal` |  |  | Non-monitary value |
| `ExplanationOfBenefit.item.detail` | 0..* | `BackboneElement` |  |  | Additional items |
| `ExplanationOfBenefit.item.detail.sequence` | 1..1 | `positiveInt` |  |  | Product or service provided |
| `ExplanationOfBenefit.item.detail.revenue` | 0..1 | `CodeableConcept` |  | example→ex-revenue-center | Revenue or cost center code |
| `ExplanationOfBenefit.item.detail.category` | 0..1 | `CodeableConcept` |  | example→ex-benefitcategory | Benefit classification |
| `ExplanationOfBenefit.item.detail.productOrService` | 1..1 | `CodeableConcept` |  | example→service-uscls | Billing, service, product, or drug code |
| `ExplanationOfBenefit.item.detail.modifier` | 0..* | `CodeableConcept` |  | example→claim-modifiers | Service/Product billing modifiers |
| `ExplanationOfBenefit.item.detail.programCode` | 0..* | `CodeableConcept` |  | example→ex-program-code | Program the product or service is provided under |
| `ExplanationOfBenefit.item.detail.quantity` | 0..1 | `Quantity(SimpleQuantity)` |  |  | Count of products or services |
| `ExplanationOfBenefit.item.detail.unitPrice` | 0..1 | `Money` |  |  | Fee, charge or cost per item |
| `ExplanationOfBenefit.item.detail.factor` | 0..1 | `decimal` |  |  | Price scaling factor |
| `ExplanationOfBenefit.item.detail.net` | 0..1 | `Money` |  |  | Total item cost |
| `ExplanationOfBenefit.item.detail.udi` | 0..* | `Reference(Device)` |  |  | Unique device identifier |
| `ExplanationOfBenefit.item.detail.noteNumber` | 0..* | `positiveInt` |  |  | Applicable note numbers |
| `ExplanationOfBenefit.item.detail.adjudication` | 0..* | `see ExplanationOfBenefit.item.adjudication` |  |  | Detail level adjudication details |
| `ExplanationOfBenefit.item.detail.subDetail` | 0..* | `BackboneElement` |  |  | Additional items |
| `ExplanationOfBenefit.item.detail.subDetail.sequence` | 1..1 | `positiveInt` |  |  | Product or service provided |
| `ExplanationOfBenefit.item.detail.subDetail.revenue` | 0..1 | `CodeableConcept` |  | example→ex-revenue-center | Revenue or cost center code |
| `ExplanationOfBenefit.item.detail.subDetail.category` | 0..1 | `CodeableConcept` |  | example→ex-benefitcategory | Benefit classification |
| `ExplanationOfBenefit.item.detail.subDetail.productOrService` | 1..1 | `CodeableConcept` |  | example→service-uscls | Billing, service, product, or drug code |
| `ExplanationOfBenefit.item.detail.subDetail.modifier` | 0..* | `CodeableConcept` |  | example→claim-modifiers | Service/Product billing modifiers |
| `ExplanationOfBenefit.item.detail.subDetail.programCode` | 0..* | `CodeableConcept` |  | example→ex-program-code | Program the product or service is provided under |
| `ExplanationOfBenefit.item.detail.subDetail.quantity` | 0..1 | `Quantity(SimpleQuantity)` |  |  | Count of products or services |
| `ExplanationOfBenefit.item.detail.subDetail.unitPrice` | 0..1 | `Money` |  |  | Fee, charge or cost per item |
| `ExplanationOfBenefit.item.detail.subDetail.factor` | 0..1 | `decimal` |  |  | Price scaling factor |
| `ExplanationOfBenefit.item.detail.subDetail.net` | 0..1 | `Money` |  |  | Total item cost |
| `ExplanationOfBenefit.item.detail.subDetail.udi` | 0..* | `Reference(Device)` |  |  | Unique device identifier |
| `ExplanationOfBenefit.item.detail.subDetail.noteNumber` | 0..* | `positiveInt` |  |  | Applicable note numbers |
| `ExplanationOfBenefit.item.detail.subDetail.adjudication` | 0..* | `see ExplanationOfBenefit.item.adjudication` |  |  | Subdetail level adjudication details |
| `ExplanationOfBenefit.addItem` | 0..* | `BackboneElement` |  |  | Insurer added line items |
| `ExplanationOfBenefit.addItem.itemSequence` | 0..* | `positiveInt` |  |  | Item sequence number |
| `ExplanationOfBenefit.addItem.detailSequence` | 0..* | `positiveInt` |  |  | Detail sequence number |
| `ExplanationOfBenefit.addItem.subDetailSequence` | 0..* | `positiveInt` |  |  | Subdetail sequence number |
| `ExplanationOfBenefit.addItem.provider` | 0..* | `Reference(Practitioner \| PractitionerRole \| Organization)` |  |  | Authorized providers |
| `ExplanationOfBenefit.addItem.productOrService` | 1..1 | `CodeableConcept` |  | example→service-uscls | Billing, service, product, or drug code |
| `ExplanationOfBenefit.addItem.modifier` | 0..* | `CodeableConcept` |  | example→claim-modifiers | Service/Product billing modifiers |
| `ExplanationOfBenefit.addItem.programCode` | 0..* | `CodeableConcept` |  | example→ex-program-code | Program the product or service is provided under |
| `ExplanationOfBenefit.addItem.serviced[x]` | 0..1 | `date, Period` |  |  | Date or dates of service or product delivery |
| `ExplanationOfBenefit.addItem.location[x]` | 0..1 | `CodeableConcept, Address, Reference(Location)` |  | example→service-place | Place of service or where product was supplied |
| `ExplanationOfBenefit.addItem.quantity` | 0..1 | `Quantity(SimpleQuantity)` |  |  | Count of products or services |
| `ExplanationOfBenefit.addItem.unitPrice` | 0..1 | `Money` |  |  | Fee, charge or cost per item |
| `ExplanationOfBenefit.addItem.factor` | 0..1 | `decimal` |  |  | Price scaling factor |
| `ExplanationOfBenefit.addItem.net` | 0..1 | `Money` |  |  | Total item cost |
| `ExplanationOfBenefit.addItem.bodySite` | 0..1 | `CodeableConcept` |  | example→tooth | Anatomical location |
| `ExplanationOfBenefit.addItem.subSite` | 0..* | `CodeableConcept` |  | example→surface | Anatomical sub-location |
| `ExplanationOfBenefit.addItem.noteNumber` | 0..* | `positiveInt` |  |  | Applicable note numbers |
| `ExplanationOfBenefit.addItem.adjudication` | 0..* | `see ExplanationOfBenefit.item.adjudication` |  |  | Added items adjudication |
| `ExplanationOfBenefit.addItem.detail` | 0..* | `BackboneElement` |  |  | Insurer added line items |
| `ExplanationOfBenefit.addItem.detail.productOrService` | 1..1 | `CodeableConcept` |  | example→service-uscls | Billing, service, product, or drug code |
| `ExplanationOfBenefit.addItem.detail.modifier` | 0..* | `CodeableConcept` |  | example→claim-modifiers | Service/Product billing modifiers |
| `ExplanationOfBenefit.addItem.detail.quantity` | 0..1 | `Quantity(SimpleQuantity)` |  |  | Count of products or services |
| `ExplanationOfBenefit.addItem.detail.unitPrice` | 0..1 | `Money` |  |  | Fee, charge or cost per item |
| `ExplanationOfBenefit.addItem.detail.factor` | 0..1 | `decimal` |  |  | Price scaling factor |
| `ExplanationOfBenefit.addItem.detail.net` | 0..1 | `Money` |  |  | Total item cost |
| `ExplanationOfBenefit.addItem.detail.noteNumber` | 0..* | `positiveInt` |  |  | Applicable note numbers |
| `ExplanationOfBenefit.addItem.detail.adjudication` | 0..* | `see ExplanationOfBenefit.item.adjudication` |  |  | Added items adjudication |
| `ExplanationOfBenefit.addItem.detail.subDetail` | 0..* | `BackboneElement` |  |  | Insurer added line items |
| `ExplanationOfBenefit.addItem.detail.subDetail.productOrService` | 1..1 | `CodeableConcept` |  | example→service-uscls | Billing, service, product, or drug code |
| `ExplanationOfBenefit.addItem.detail.subDetail.modifier` | 0..* | `CodeableConcept` |  | example→claim-modifiers | Service/Product billing modifiers |
| `ExplanationOfBenefit.addItem.detail.subDetail.quantity` | 0..1 | `Quantity(SimpleQuantity)` |  |  | Count of products or services |
| `ExplanationOfBenefit.addItem.detail.subDetail.unitPrice` | 0..1 | `Money` |  |  | Fee, charge or cost per item |
| `ExplanationOfBenefit.addItem.detail.subDetail.factor` | 0..1 | `decimal` |  |  | Price scaling factor |
| `ExplanationOfBenefit.addItem.detail.subDetail.net` | 0..1 | `Money` |  |  | Total item cost |
| `ExplanationOfBenefit.addItem.detail.subDetail.noteNumber` | 0..* | `positiveInt` |  |  | Applicable note numbers |
| `ExplanationOfBenefit.addItem.detail.subDetail.adjudication` | 0..* | `see ExplanationOfBenefit.item.adjudication` |  |  | Added items adjudication |
| `ExplanationOfBenefit.adjudication` | 0..* | `see ExplanationOfBenefit.item.adjudication` |  |  | Header-level adjudication |
| `ExplanationOfBenefit.total` | 0..* | `BackboneElement` | summary |  | Adjudication totals |
| `ExplanationOfBenefit.total.category` | 1..1 | `CodeableConcept` | summary | example→adjudication | Type of adjudication information |
| `ExplanationOfBenefit.total.amount` | 1..1 | `Money` | summary |  | Financial total for the category |
| `ExplanationOfBenefit.payment` | 0..1 | `BackboneElement` |  |  | Payment Details |
| `ExplanationOfBenefit.payment.type` | 0..1 | `CodeableConcept` |  | example→ex-paymenttype | Partial or complete payment |
| `ExplanationOfBenefit.payment.adjustment` | 0..1 | `Money` |  |  | Payment adjustment for non-claim issues |
| `ExplanationOfBenefit.payment.adjustmentReason` | 0..1 | `CodeableConcept` |  | example→payment-adjustment-reason | Explanation for the variance |
| `ExplanationOfBenefit.payment.date` | 0..1 | `date` |  |  | Expected date of payment |
| `ExplanationOfBenefit.payment.amount` | 0..1 | `Money` |  |  | Payable amount after adjustment |
| `ExplanationOfBenefit.payment.identifier` | 0..1 | `Identifier` |  |  | Business identifier for the payment |
| `ExplanationOfBenefit.formCode` | 0..1 | `CodeableConcept` |  | example→forms | Printed form identifier |
| `ExplanationOfBenefit.form` | 0..1 | `Attachment` |  |  | Printed reference or actual form |
| `ExplanationOfBenefit.processNote` | 0..* | `BackboneElement` |  |  | Note concerning adjudication |
| `ExplanationOfBenefit.processNote.number` | 0..1 | `positiveInt` |  |  | Note instance identifier |
| `ExplanationOfBenefit.processNote.type` | 0..1 | `code` |  | required→note-type@4.0.1 | display \| print \| printoper |
| `ExplanationOfBenefit.processNote.text` | 0..1 | `string` |  |  | Note explanatory text |
| `ExplanationOfBenefit.processNote.language` | 0..1 | `CodeableConcept` |  | preferred→languages | Language of the text |
| `ExplanationOfBenefit.benefitPeriod` | 0..1 | `Period` |  |  | When the benefits are applicable |
| `ExplanationOfBenefit.benefitBalance` | 0..* | `BackboneElement` |  |  | Balance by Benefit Category |
| `ExplanationOfBenefit.benefitBalance.category` | 1..1 | `CodeableConcept` |  | example→ex-benefitcategory | Benefit classification |
| `ExplanationOfBenefit.benefitBalance.excluded` | 0..1 | `boolean` |  |  | Excluded from the plan |
| `ExplanationOfBenefit.benefitBalance.name` | 0..1 | `string` |  |  | Short name for the benefit |
| `ExplanationOfBenefit.benefitBalance.description` | 0..1 | `string` |  |  | Description of the benefit or services covered |
| `ExplanationOfBenefit.benefitBalance.network` | 0..1 | `CodeableConcept` |  | example→benefit-network | In or out of network |
| `ExplanationOfBenefit.benefitBalance.unit` | 0..1 | `CodeableConcept` |  | example→benefit-unit | Individual or family |
| `ExplanationOfBenefit.benefitBalance.term` | 0..1 | `CodeableConcept` |  | example→benefit-term | Annual or lifetime |
| `ExplanationOfBenefit.benefitBalance.financial` | 0..* | `BackboneElement` |  |  | Benefit Summary |
| `ExplanationOfBenefit.benefitBalance.financial.type` | 1..1 | `CodeableConcept` |  | example→benefit-type | Benefit classification |
| `ExplanationOfBenefit.benefitBalance.financial.allowed[x]` | 0..1 | `unsignedInt, string, Money` |  |  | Benefits allowed |
| `ExplanationOfBenefit.benefitBalance.financial.used[x]` | 0..1 | `unsignedInt, Money` |  |  | Benefits used |

Elements defined in ancestors: `ExplanationOfBenefit.id`, `ExplanationOfBenefit.meta`, `ExplanationOfBenefit.implicitRules`, `ExplanationOfBenefit.language`, `ExplanationOfBenefit.text`, `ExplanationOfBenefit.contained`, `ExplanationOfBenefit.extension`, `ExplanationOfBenefit.modifierExtension`, `ExplanationOfBenefit.related.id`, `ExplanationOfBenefit.related.extension`, `ExplanationOfBenefit.related.modifierExtension`, `ExplanationOfBenefit.payee.id`, `ExplanationOfBenefit.payee.extension`, `ExplanationOfBenefit.payee.modifierExtension`, `ExplanationOfBenefit.careTeam.id`, `ExplanationOfBenefit.careTeam.extension`, `ExplanationOfBenefit.careTeam.modifierExtension`, `ExplanationOfBenefit.supportingInfo.id`, `ExplanationOfBenefit.supportingInfo.extension`, `ExplanationOfBenefit.supportingInfo.modifierExtension`, `ExplanationOfBenefit.diagnosis.id`, `ExplanationOfBenefit.diagnosis.extension`, `ExplanationOfBenefit.diagnosis.modifierExtension`, `ExplanationOfBenefit.procedure.id`, `ExplanationOfBenefit.procedure.extension`, `ExplanationOfBenefit.procedure.modifierExtension`, `ExplanationOfBenefit.insurance.id`, `ExplanationOfBenefit.insurance.extension`, `ExplanationOfBenefit.insurance.modifierExtension`, `ExplanationOfBenefit.accident.id`, `ExplanationOfBenefit.accident.extension`, `ExplanationOfBenefit.accident.modifierExtension`, `ExplanationOfBenefit.item.id`, `ExplanationOfBenefit.item.extension`, `ExplanationOfBenefit.item.modifierExtension`, `ExplanationOfBenefit.item.adjudication.id`, `ExplanationOfBenefit.item.adjudication.extension`, `ExplanationOfBenefit.item.adjudication.modifierExtension`, `ExplanationOfBenefit.item.detail.id`, `ExplanationOfBenefit.item.detail.extension`, `ExplanationOfBenefit.item.detail.modifierExtension`, `ExplanationOfBenefit.item.detail.subDetail.id`, `ExplanationOfBenefit.item.detail.subDetail.extension`, `ExplanationOfBenefit.item.detail.subDetail.modifierExtension`, `ExplanationOfBenefit.addItem.id`, `ExplanationOfBenefit.addItem.extension`, `ExplanationOfBenefit.addItem.modifierExtension`, `ExplanationOfBenefit.addItem.detail.id`, `ExplanationOfBenefit.addItem.detail.extension`, `ExplanationOfBenefit.addItem.detail.modifierExtension`, `ExplanationOfBenefit.addItem.detail.subDetail.id`, `ExplanationOfBenefit.addItem.detail.subDetail.extension`, `ExplanationOfBenefit.addItem.detail.subDetail.modifierExtension`, `ExplanationOfBenefit.total.id`, `ExplanationOfBenefit.total.extension`, `ExplanationOfBenefit.total.modifierExtension`, `ExplanationOfBenefit.payment.id`, `ExplanationOfBenefit.payment.extension`, `ExplanationOfBenefit.payment.modifierExtension`, `ExplanationOfBenefit.processNote.id`, `ExplanationOfBenefit.processNote.extension`, `ExplanationOfBenefit.processNote.modifierExtension`, `ExplanationOfBenefit.benefitBalance.id`, `ExplanationOfBenefit.benefitBalance.extension`, `ExplanationOfBenefit.benefitBalance.modifierExtension`, `ExplanationOfBenefit.benefitBalance.financial.id`, `ExplanationOfBenefit.benefitBalance.financial.extension`, `ExplanationOfBenefit.benefitBalance.financial.modifierExtension`

## Invariants

_No profile-specific invariants._
