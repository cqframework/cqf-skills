# Patient

**ID** `Patient` | **URL** `http://hl7.org/fhir/StructureDefinition/Patient` | **Status** active
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Patient Administration) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Demographics and other administrative information about an individual or animal receiving care or other health-related services.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Patient` | 0..* | `Patient` |  |  | Information about an individual or animal receiving health care services |
| `Patient.identifier` | 0..* | `Identifier` | summary |  | An identifier for this patient |
| `Patient.active` | 0..1 | `boolean` | modifier summary |  | Whether this patient's record is in active use |
| `Patient.name` | 0..* | `HumanName` | summary |  | A name associated with the patient |
| `Patient.telecom` | 0..* | `ContactPoint` | summary |  | A contact detail for the individual |
| `Patient.gender` | 0..1 | `code` | summary | required→administrative-gender@4.0.1 | male \| female \| other \| unknown |
| `Patient.birthDate` | 0..1 | `date` | summary |  | The date of birth for the individual |
| `Patient.deceased[x]` | 0..1 | `boolean, dateTime` | modifier summary |  | Indicates if the individual is deceased or not |
| `Patient.address` | 0..* | `Address` | summary |  | An address for the individual |
| `Patient.maritalStatus` | 0..1 | `CodeableConcept` |  | extensible→marital-status | Marital (civil) status of a patient |
| `Patient.multipleBirth[x]` | 0..1 | `boolean, integer` |  |  | Whether patient is part of a multiple birth |
| `Patient.photo` | 0..* | `Attachment` |  |  | Image of the patient |
| `Patient.contact` | 0..* | `BackboneElement` |  |  | A contact party (e.g. guardian, partner, friend) for the patient |
| `Patient.contact.relationship` | 0..* | `CodeableConcept` |  | extensible→patient-contactrelationship | The kind of relationship |
| `Patient.contact.name` | 0..1 | `HumanName` |  |  | A name associated with the contact person |
| `Patient.contact.telecom` | 0..* | `ContactPoint` |  |  | A contact detail for the person |
| `Patient.contact.address` | 0..1 | `Address` |  |  | Address for the contact person |
| `Patient.contact.gender` | 0..1 | `code` |  | required→administrative-gender@4.0.1 | male \| female \| other \| unknown |
| `Patient.contact.organization` | 0..1 | `Reference(Organization)` |  |  | Organization that is associated with the contact |
| `Patient.contact.period` | 0..1 | `Period` |  |  | The period during which this contact person or organization is valid to be contacted relating to this patient |
| `Patient.communication` | 0..* | `BackboneElement` |  |  | A language which may be used to communicate with the patient about his or her health |
| `Patient.communication.language` | 1..1 | `CodeableConcept` |  | preferred→languages | The language which can be used to communicate with the patient about his or her health |
| `Patient.communication.preferred` | 0..1 | `boolean` |  |  | Language preference indicator |
| `Patient.generalPractitioner` | 0..* | `Reference(Organization \| Practitioner \| PractitionerRole)` |  |  | Patient's nominated primary care provider |
| `Patient.managingOrganization` | 0..1 | `Reference(Organization)` | summary |  | Organization that is the custodian of the patient record |
| `Patient.link` | 0..* | `BackboneElement` | modifier summary |  | Link to another patient resource that concerns the same actual person |
| `Patient.link.other` | 1..1 | `Reference(Patient \| RelatedPerson)` | summary |  | The other patient or related person resource that the link refers to |
| `Patient.link.type` | 1..1 | `code` | summary | required→link-type@4.0.1 | replaced-by \| replaces \| refer \| seealso |

Elements defined in ancestors: `Patient.id`, `Patient.meta`, `Patient.implicitRules`, `Patient.language`, `Patient.text`, `Patient.contained`, `Patient.extension`, `Patient.modifierExtension`, `Patient.contact.id`, `Patient.contact.extension`, `Patient.contact.modifierExtension`, `Patient.communication.id`, `Patient.communication.extension`, `Patient.communication.modifierExtension`, `Patient.link.id`, `Patient.link.extension`, `Patient.link.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `Patient.contact` | `pat-1` | error | SHALL at least contain a contact's details or a reference to an organization | `name.exists() or telecom.exists() or address.exists() or organization.exists()` |
