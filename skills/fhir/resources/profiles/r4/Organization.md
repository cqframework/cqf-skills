# Organization

**ID** `Organization` | **URL** `http://hl7.org/fhir/StructureDefinition/Organization` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Patient Administration) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

A formally or informally recognized grouping of people or organizations formed for the purpose of achieving some form of collective action. Includes companies, institutions, corporations, departments, community groups, healthcare practice groups, payer/insurer, etc.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Organization` | 0..* | `Organization` |  |  | A grouping of people or organizations with a common purpose |
| `Organization.identifier` | 0..* | `Identifier` | summary |  | Identifies this organization across multiple systems |
| `Organization.active` | 0..1 | `boolean` | modifier summary |  | Whether the organization's record is still in active use |
| `Organization.type` | 0..* | `CodeableConcept` | summary | example→organization-type | Kind of organization |
| `Organization.name` | 0..1 | `string` | summary |  | Name used for the organization |
| `Organization.alias` | 0..* | `string` |  |  | A list of alternate names that the organization is known as, or was known as in the past |
| `Organization.telecom` | 0..* | `ContactPoint` |  |  | A contact detail for the organization |
| `Organization.address` | 0..* | `Address` |  |  | An address for the organization |
| `Organization.partOf` | 0..1 | `Reference(Organization)` | summary |  | The organization of which this organization forms a part |
| `Organization.contact` | 0..* | `BackboneElement` |  |  | Contact for the organization for a certain purpose |
| `Organization.contact.purpose` | 0..1 | `CodeableConcept` |  | extensible→contactentity-type | The type of contact |
| `Organization.contact.name` | 0..1 | `HumanName` |  |  | A name associated with the contact |
| `Organization.contact.telecom` | 0..* | `ContactPoint` |  |  | Contact details (telephone, email, etc.) for a contact |
| `Organization.contact.address` | 0..1 | `Address` |  |  | Visiting or postal addresses for the contact |
| `Organization.endpoint` | 0..* | `Reference(Endpoint)` |  |  | Technical endpoints providing access to services operated for the organization |

Elements defined in ancestors: `Organization.id`, `Organization.meta`, `Organization.implicitRules`, `Organization.language`, `Organization.text`, `Organization.contained`, `Organization.extension`, `Organization.modifierExtension`, `Organization.contact.id`, `Organization.contact.extension`, `Organization.contact.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `Organization` | `org-1` | error | The organization SHALL at least have a name or an identifier, and possibly more than one | `(identifier.count() + name.count()) > 0` |
| `Organization.telecom` | `org-3` | error | The telecom of an organization can never be of use 'home' | `where(use = 'home').empty()` |
| `Organization.address` | `org-2` | error | An address of an organization can never be of use 'home' | `where(use = 'home').empty()` |
