# Practitioner

**ID** `Practitioner` | **URL** `http://hl7.org/fhir/StructureDefinition/Practitioner` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Patient Administration) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

A person who is directly or indirectly involved in the provisioning of healthcare.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Practitioner` | 0..* | `Practitioner` |  |  | A person with a formal responsibility in the provisioning of healthcare or related services |
| `Practitioner.identifier` | 0..* | `Identifier` | summary |  | An identifier for the person as this agent |
| `Practitioner.active` | 0..1 | `boolean` | summary |  | Whether this practitioner's record is in active use |
| `Practitioner.name` | 0..* | `HumanName` | summary |  | The name(s) associated with the practitioner |
| `Practitioner.telecom` | 0..* | `ContactPoint` | summary |  | A contact detail for the practitioner (that apply to all roles) |
| `Practitioner.address` | 0..* | `Address` | summary |  | Address(es) of the practitioner that are not role specific (typically home address) |
| `Practitioner.gender` | 0..1 | `code` | summary | required→administrative-gender@4.0.1 | male \| female \| other \| unknown |
| `Practitioner.birthDate` | 0..1 | `date` | summary |  | The date on which the practitioner was born |
| `Practitioner.photo` | 0..* | `Attachment` |  |  | Image of the person |
| `Practitioner.qualification` | 0..* | `BackboneElement` |  |  | Certification, licenses, or training pertaining to the provision of care |
| `Practitioner.qualification.identifier` | 0..* | `Identifier` |  |  | An identifier for this qualification for the practitioner |
| `Practitioner.qualification.code` | 1..1 | `CodeableConcept` |  | example→v2-2.7-0360 | Coded representation of the qualification |
| `Practitioner.qualification.period` | 0..1 | `Period` |  |  | Period during which the qualification is valid |
| `Practitioner.qualification.issuer` | 0..1 | `Reference(Organization)` |  |  | Organization that regulates and issues the qualification |
| `Practitioner.communication` | 0..* | `CodeableConcept` |  | preferred→languages | A language the practitioner can use in patient communication |

Elements defined in ancestors: `Practitioner.id`, `Practitioner.meta`, `Practitioner.implicitRules`, `Practitioner.language`, `Practitioner.text`, `Practitioner.contained`, `Practitioner.extension`, `Practitioner.modifierExtension`, `Practitioner.qualification.id`, `Practitioner.qualification.extension`, `Practitioner.qualification.modifierExtension`

## Invariants

_No profile-specific invariants._
