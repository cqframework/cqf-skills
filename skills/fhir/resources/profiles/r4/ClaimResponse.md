# ClaimResponse

**ID** `ClaimResponse` | **URL** `http://hl7.org/fhir/StructureDefinition/ClaimResponse` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Financial Management) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

This resource provides the adjudication details from the processing of a Claim resource.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ClaimResponse` | 0..* | `ClaimResponse` |  |  | Response to a claim predetermination or preauthorization |
| `ClaimResponse.identifier` | 0..* | `Identifier` |  |  | Business Identifier for a claim response |
| `ClaimResponse.status` | 1..1 | `code` | modifier summary | required→fm-status@4.0.1 | active \| cancelled \| draft \| entered-in-error |
| `ClaimResponse.type` | 1..1 | `CodeableConcept` | summary | extensible→claim-type | More granular claim type |
| `ClaimResponse.subType` | 0..1 | `CodeableConcept` |  | example→claim-subtype | More granular claim type |
| `ClaimResponse.use` | 1..1 | `code` | summary | required→claim-use@4.0.1 | claim \| preauthorization \| predetermination |
| `ClaimResponse.patient` | 1..1 | `Reference(Patient)` | summary |  | The recipient of the products and services |
| `ClaimResponse.created` | 1..1 | `dateTime` | summary |  | Response creation date |
| `ClaimResponse.insurer` | 1..1 | `Reference(Organization)` | summary |  | Party responsible for reimbursement |
| `ClaimResponse.requestor` | 0..1 | `Reference(Practitioner \| PractitionerRole \| Organization)` |  |  | Party responsible for the claim |
| `ClaimResponse.request` | 0..1 | `Reference(Claim)` | summary |  | Id of resource triggering adjudication |
| `ClaimResponse.outcome` | 1..1 | `code` | summary | required→remittance-outcome@4.0.1 | queued \| complete \| error \| partial |
| `ClaimResponse.disposition` | 0..1 | `string` |  |  | Disposition Message |
| `ClaimResponse.preAuthRef` | 0..1 | `string` |  |  | Preauthorization reference |
| `ClaimResponse.preAuthPeriod` | 0..1 | `Period` |  |  | Preauthorization reference effective period |
| `ClaimResponse.payeeType` | 0..1 | `CodeableConcept` |  | example→payeetype | Party to be paid any benefits payable |
| `ClaimResponse.item` | 0..* | `BackboneElement` |  |  | Adjudication for claim line items |
| `ClaimResponse.item.itemSequence` | 1..1 | `positiveInt` |  |  | Claim item instance identifier |
| `ClaimResponse.item.noteNumber` | 0..* | `positiveInt` |  |  | Applicable note numbers |
| `ClaimResponse.item.adjudication` | 1..* | `BackboneElement` |  |  | Adjudication details |
| `ClaimResponse.item.adjudication.category` | 1..1 | `CodeableConcept` |  | example→adjudication | Type of adjudication information |
| `ClaimResponse.item.adjudication.reason` | 0..1 | `CodeableConcept` |  | example→adjudication-reason | Explanation of adjudication outcome |
| `ClaimResponse.item.adjudication.amount` | 0..1 | `Money` |  |  | Monetary amount |
| `ClaimResponse.item.adjudication.value` | 0..1 | `decimal` |  |  | Non-monetary value |
| `ClaimResponse.item.detail` | 0..* | `BackboneElement` |  |  | Adjudication for claim details |
| `ClaimResponse.item.detail.detailSequence` | 1..1 | `positiveInt` |  |  | Claim detail instance identifier |
| `ClaimResponse.item.detail.noteNumber` | 0..* | `positiveInt` |  |  | Applicable note numbers |
| `ClaimResponse.item.detail.adjudication` | 1..* | `see ClaimResponse.item.adjudication` |  |  | Detail level adjudication details |
| `ClaimResponse.item.detail.subDetail` | 0..* | `BackboneElement` |  |  | Adjudication for claim sub-details |
| `ClaimResponse.item.detail.subDetail.subDetailSequence` | 1..1 | `positiveInt` |  |  | Claim sub-detail instance identifier |
| `ClaimResponse.item.detail.subDetail.noteNumber` | 0..* | `positiveInt` |  |  | Applicable note numbers |
| `ClaimResponse.item.detail.subDetail.adjudication` | 0..* | `see ClaimResponse.item.adjudication` |  |  | Subdetail level adjudication details |
| `ClaimResponse.addItem` | 0..* | `BackboneElement` |  |  | Insurer added line items |
| `ClaimResponse.addItem.itemSequence` | 0..* | `positiveInt` |  |  | Item sequence number |
| `ClaimResponse.addItem.detailSequence` | 0..* | `positiveInt` |  |  | Detail sequence number |
| `ClaimResponse.addItem.subdetailSequence` | 0..* | `positiveInt` |  |  | Subdetail sequence number |
| `ClaimResponse.addItem.provider` | 0..* | `Reference(Practitioner \| PractitionerRole \| Organization)` |  |  | Authorized providers |
| `ClaimResponse.addItem.productOrService` | 1..1 | `CodeableConcept` |  | example→service-uscls | Billing, service, product, or drug code |
| `ClaimResponse.addItem.modifier` | 0..* | `CodeableConcept` |  | example→claim-modifiers | Service/Product billing modifiers |
| `ClaimResponse.addItem.programCode` | 0..* | `CodeableConcept` |  | example→ex-program-code | Program the product or service is provided under |
| `ClaimResponse.addItem.serviced[x]` | 0..1 | `date, Period` |  |  | Date or dates of service or product delivery |
| `ClaimResponse.addItem.location[x]` | 0..1 | `CodeableConcept, Address, Reference(Location)` |  | example→service-place | Place of service or where product was supplied |
| `ClaimResponse.addItem.quantity` | 0..1 | `Quantity(SimpleQuantity)` |  |  | Count of products or services |
| `ClaimResponse.addItem.unitPrice` | 0..1 | `Money` |  |  | Fee, charge or cost per item |
| `ClaimResponse.addItem.factor` | 0..1 | `decimal` |  |  | Price scaling factor |
| `ClaimResponse.addItem.net` | 0..1 | `Money` |  |  | Total item cost |
| `ClaimResponse.addItem.bodySite` | 0..1 | `CodeableConcept` |  | example→tooth | Anatomical location |
| `ClaimResponse.addItem.subSite` | 0..* | `CodeableConcept` |  | example→surface | Anatomical sub-location |
| `ClaimResponse.addItem.noteNumber` | 0..* | `positiveInt` |  |  | Applicable note numbers |
| `ClaimResponse.addItem.adjudication` | 1..* | `see ClaimResponse.item.adjudication` |  |  | Added items adjudication |
| `ClaimResponse.addItem.detail` | 0..* | `BackboneElement` |  |  | Insurer added line details |
| `ClaimResponse.addItem.detail.productOrService` | 1..1 | `CodeableConcept` |  | example→service-uscls | Billing, service, product, or drug code |
| `ClaimResponse.addItem.detail.modifier` | 0..* | `CodeableConcept` |  | example→claim-modifiers | Service/Product billing modifiers |
| `ClaimResponse.addItem.detail.quantity` | 0..1 | `Quantity(SimpleQuantity)` |  |  | Count of products or services |
| `ClaimResponse.addItem.detail.unitPrice` | 0..1 | `Money` |  |  | Fee, charge or cost per item |
| `ClaimResponse.addItem.detail.factor` | 0..1 | `decimal` |  |  | Price scaling factor |
| `ClaimResponse.addItem.detail.net` | 0..1 | `Money` |  |  | Total item cost |
| `ClaimResponse.addItem.detail.noteNumber` | 0..* | `positiveInt` |  |  | Applicable note numbers |
| `ClaimResponse.addItem.detail.adjudication` | 1..* | `see ClaimResponse.item.adjudication` |  |  | Added items detail adjudication |
| `ClaimResponse.addItem.detail.subDetail` | 0..* | `BackboneElement` |  |  | Insurer added line items |
| `ClaimResponse.addItem.detail.subDetail.productOrService` | 1..1 | `CodeableConcept` |  | example→service-uscls | Billing, service, product, or drug code |
| `ClaimResponse.addItem.detail.subDetail.modifier` | 0..* | `CodeableConcept` |  | example→claim-modifiers | Service/Product billing modifiers |
| `ClaimResponse.addItem.detail.subDetail.quantity` | 0..1 | `Quantity(SimpleQuantity)` |  |  | Count of products or services |
| `ClaimResponse.addItem.detail.subDetail.unitPrice` | 0..1 | `Money` |  |  | Fee, charge or cost per item |
| `ClaimResponse.addItem.detail.subDetail.factor` | 0..1 | `decimal` |  |  | Price scaling factor |
| `ClaimResponse.addItem.detail.subDetail.net` | 0..1 | `Money` |  |  | Total item cost |
| `ClaimResponse.addItem.detail.subDetail.noteNumber` | 0..* | `positiveInt` |  |  | Applicable note numbers |
| `ClaimResponse.addItem.detail.subDetail.adjudication` | 1..* | `see ClaimResponse.item.adjudication` |  |  | Added items detail adjudication |
| `ClaimResponse.adjudication` | 0..* | `see ClaimResponse.item.adjudication` |  |  | Header-level adjudication |
| `ClaimResponse.total` | 0..* | `BackboneElement` | summary |  | Adjudication totals |
| `ClaimResponse.total.category` | 1..1 | `CodeableConcept` | summary | example→adjudication | Type of adjudication information |
| `ClaimResponse.total.amount` | 1..1 | `Money` | summary |  | Financial total for the category |
| `ClaimResponse.payment` | 0..1 | `BackboneElement` |  |  | Payment Details |
| `ClaimResponse.payment.type` | 1..1 | `CodeableConcept` |  | example→ex-paymenttype | Partial or complete payment |
| `ClaimResponse.payment.adjustment` | 0..1 | `Money` |  |  | Payment adjustment for non-claim issues |
| `ClaimResponse.payment.adjustmentReason` | 0..1 | `CodeableConcept` |  | example→payment-adjustment-reason | Explanation for the adjustment |
| `ClaimResponse.payment.date` | 0..1 | `date` |  |  | Expected date of payment |
| `ClaimResponse.payment.amount` | 1..1 | `Money` |  |  | Payable amount after adjustment |
| `ClaimResponse.payment.identifier` | 0..1 | `Identifier` |  |  | Business identifier for the payment |
| `ClaimResponse.fundsReserve` | 0..1 | `CodeableConcept` |  | example→fundsreserve | Funds reserved status |
| `ClaimResponse.formCode` | 0..1 | `CodeableConcept` |  | example→forms | Printed form identifier |
| `ClaimResponse.form` | 0..1 | `Attachment` |  |  | Printed reference or actual form |
| `ClaimResponse.processNote` | 0..* | `BackboneElement` |  |  | Note concerning adjudication |
| `ClaimResponse.processNote.number` | 0..1 | `positiveInt` |  |  | Note instance identifier |
| `ClaimResponse.processNote.type` | 0..1 | `code` |  | required→note-type@4.0.1 | display \| print \| printoper |
| `ClaimResponse.processNote.text` | 1..1 | `string` |  |  | Note explanatory text |
| `ClaimResponse.processNote.language` | 0..1 | `CodeableConcept` |  | preferred→languages | Language of the text |
| `ClaimResponse.communicationRequest` | 0..* | `Reference(CommunicationRequest)` |  |  | Request for additional information |
| `ClaimResponse.insurance` | 0..* | `BackboneElement` |  |  | Patient insurance information |
| `ClaimResponse.insurance.sequence` | 1..1 | `positiveInt` |  |  | Insurance instance identifier |
| `ClaimResponse.insurance.focal` | 1..1 | `boolean` |  |  | Coverage to be used for adjudication |
| `ClaimResponse.insurance.coverage` | 1..1 | `Reference(Coverage)` |  |  | Insurance information |
| `ClaimResponse.insurance.businessArrangement` | 0..1 | `string` |  |  | Additional provider contract number |
| `ClaimResponse.insurance.claimResponse` | 0..1 | `Reference(ClaimResponse)` |  |  | Adjudication results |
| `ClaimResponse.error` | 0..* | `BackboneElement` |  |  | Processing errors |
| `ClaimResponse.error.itemSequence` | 0..1 | `positiveInt` |  |  | Item sequence number |
| `ClaimResponse.error.detailSequence` | 0..1 | `positiveInt` |  |  | Detail sequence number |
| `ClaimResponse.error.subDetailSequence` | 0..1 | `positiveInt` |  |  | Subdetail sequence number |
| `ClaimResponse.error.code` | 1..1 | `CodeableConcept` |  | example→adjudication-error | Error code detailing processing issues |

Elements defined in ancestors: `ClaimResponse.id`, `ClaimResponse.meta`, `ClaimResponse.implicitRules`, `ClaimResponse.language`, `ClaimResponse.text`, `ClaimResponse.contained`, `ClaimResponse.extension`, `ClaimResponse.modifierExtension`, `ClaimResponse.item.id`, `ClaimResponse.item.extension`, `ClaimResponse.item.modifierExtension`, `ClaimResponse.item.adjudication.id`, `ClaimResponse.item.adjudication.extension`, `ClaimResponse.item.adjudication.modifierExtension`, `ClaimResponse.item.detail.id`, `ClaimResponse.item.detail.extension`, `ClaimResponse.item.detail.modifierExtension`, `ClaimResponse.item.detail.subDetail.id`, `ClaimResponse.item.detail.subDetail.extension`, `ClaimResponse.item.detail.subDetail.modifierExtension`, `ClaimResponse.addItem.id`, `ClaimResponse.addItem.extension`, `ClaimResponse.addItem.modifierExtension`, `ClaimResponse.addItem.detail.id`, `ClaimResponse.addItem.detail.extension`, `ClaimResponse.addItem.detail.modifierExtension`, `ClaimResponse.addItem.detail.subDetail.id`, `ClaimResponse.addItem.detail.subDetail.extension`, `ClaimResponse.addItem.detail.subDetail.modifierExtension`, `ClaimResponse.total.id`, `ClaimResponse.total.extension`, `ClaimResponse.total.modifierExtension`, `ClaimResponse.payment.id`, `ClaimResponse.payment.extension`, `ClaimResponse.payment.modifierExtension`, `ClaimResponse.processNote.id`, `ClaimResponse.processNote.extension`, `ClaimResponse.processNote.modifierExtension`, `ClaimResponse.insurance.id`, `ClaimResponse.insurance.extension`, `ClaimResponse.insurance.modifierExtension`, `ClaimResponse.error.id`, `ClaimResponse.error.extension`, `ClaimResponse.error.modifierExtension`

## Invariants

_No profile-specific invariants._
