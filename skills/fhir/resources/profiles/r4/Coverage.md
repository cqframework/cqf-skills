# Coverage

**ID** `Coverage` | **URL** `http://hl7.org/fhir/StructureDefinition/Coverage` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Financial Management) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Financial instrument which may be used to reimburse or pay for health care products and services. Includes both insurance and self-payment.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Coverage` | 0..* | `Coverage` |  |  | Insurance or medical plan or a payment agreement |
| `Coverage.identifier` | 0..* | `Identifier` | summary |  | Business Identifier for the coverage |
| `Coverage.status` | 1..1 | `code` | modifier summary | required→fm-status@4.0.1 | active \| cancelled \| draft \| entered-in-error |
| `Coverage.type` | 0..1 | `CodeableConcept` | summary | preferred→coverage-type | Coverage category such as medical or accident |
| `Coverage.policyHolder` | 0..1 | `Reference(Patient \| RelatedPerson \| Organization)` | summary |  | Owner of the policy |
| `Coverage.subscriber` | 0..1 | `Reference(Patient \| RelatedPerson)` | summary |  | Subscriber to the policy |
| `Coverage.subscriberId` | 0..1 | `string` | summary |  | ID assigned to the subscriber |
| `Coverage.beneficiary` | 1..1 | `Reference(Patient)` | summary |  | Plan beneficiary |
| `Coverage.dependent` | 0..1 | `string` | summary |  | Dependent number |
| `Coverage.relationship` | 0..1 | `CodeableConcept` |  | extensible→subscriber-relationship | Beneficiary relationship to the subscriber |
| `Coverage.period` | 0..1 | `Period` | summary |  | Coverage start and end dates |
| `Coverage.payor` | 1..* | `Reference(Organization \| Patient \| RelatedPerson)` | summary |  | Issuer of the policy |
| `Coverage.class` | 0..* | `BackboneElement` |  |  | Additional coverage classifications |
| `Coverage.class.type` | 1..1 | `CodeableConcept` | summary | extensible→coverage-class | Type of class such as 'group' or 'plan' |
| `Coverage.class.value` | 1..1 | `string` | summary |  | Value associated with the type |
| `Coverage.class.name` | 0..1 | `string` | summary |  | Human readable description of the type and value |
| `Coverage.order` | 0..1 | `positiveInt` | summary |  | Relative order of the coverage |
| `Coverage.network` | 0..1 | `string` | summary |  | Insurer network |
| `Coverage.costToBeneficiary` | 0..* | `BackboneElement` |  |  | Patient payments for services/products |
| `Coverage.costToBeneficiary.type` | 0..1 | `CodeableConcept` | summary | extensible→coverage-copay-type | Cost category |
| `Coverage.costToBeneficiary.value[x]` | 1..1 | `Quantity(SimpleQuantity), Money` | summary |  | The amount or percentage due from the beneficiary |
| `Coverage.costToBeneficiary.exception` | 0..* | `BackboneElement` |  |  | Exceptions for patient payments |
| `Coverage.costToBeneficiary.exception.type` | 1..1 | `CodeableConcept` | summary | example→coverage-financial-exception | Exception category |
| `Coverage.costToBeneficiary.exception.period` | 0..1 | `Period` | summary |  | The effective period of the exception |
| `Coverage.subrogation` | 0..1 | `boolean` |  |  | Reimbursement to insurer |
| `Coverage.contract` | 0..* | `Reference(Contract)` |  |  | Contract details |

Elements defined in ancestors: `Coverage.id`, `Coverage.meta`, `Coverage.implicitRules`, `Coverage.language`, `Coverage.text`, `Coverage.contained`, `Coverage.extension`, `Coverage.modifierExtension`, `Coverage.class.id`, `Coverage.class.extension`, `Coverage.class.modifierExtension`, `Coverage.costToBeneficiary.id`, `Coverage.costToBeneficiary.extension`, `Coverage.costToBeneficiary.modifierExtension`, `Coverage.costToBeneficiary.exception.id`, `Coverage.costToBeneficiary.exception.extension`, `Coverage.costToBeneficiary.exception.modifierExtension`

## Invariants

_No profile-specific invariants._
