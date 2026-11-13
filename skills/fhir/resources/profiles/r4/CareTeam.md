# CareTeam

**ID** `CareTeam` | **URL** `http://hl7.org/fhir/StructureDefinition/CareTeam` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Patient Care) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

The Care Team includes all the people and organizations who plan to participate in the coordination and delivery of care for a patient.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `CareTeam` | 0..* | `CareTeam` |  |  | Planned participants in the coordination and delivery of care for a patient or group |
| `CareTeam.identifier` | 0..* | `Identifier` | summary |  | External Ids for this team |
| `CareTeam.status` | 0..1 | `code` | modifier summary | required→care-team-status@4.0.1 | proposed \| active \| suspended \| inactive \| entered-in-error |
| `CareTeam.category` | 0..* | `CodeableConcept` | summary | example→care-team-category | Type of team |
| `CareTeam.name` | 0..1 | `string` | summary |  | Name of the team, such as crisis assessment team |
| `CareTeam.subject` | 0..1 | `Reference(Patient \| Group)` | summary |  | Who care team is for |
| `CareTeam.encounter` | 0..1 | `Reference(Encounter)` | summary |  | Encounter created as part of |
| `CareTeam.period` | 0..1 | `Period` | summary |  | Time period team covers |
| `CareTeam.participant` | 0..* | `BackboneElement` |  |  | Members of the team |
| `CareTeam.participant.role` | 0..* | `CodeableConcept` | summary | example→participant-role | Type of involvement |
| `CareTeam.participant.member` | 0..1 | `Reference(Practitioner \| PractitionerRole \| RelatedPerson \| Patient \| Organization \| CareTeam)` | summary |  | Who is involved |
| `CareTeam.participant.onBehalfOf` | 0..1 | `Reference(Organization)` | summary |  | Organization of the practitioner |
| `CareTeam.participant.period` | 0..1 | `Period` |  |  | Time period of participant |
| `CareTeam.reasonCode` | 0..* | `CodeableConcept` |  | example→clinical-findings | Why the care team exists |
| `CareTeam.reasonReference` | 0..* | `Reference(Condition)` |  |  | Why the care team exists |
| `CareTeam.managingOrganization` | 0..* | `Reference(Organization)` | summary |  | Organization responsible for the care team |
| `CareTeam.telecom` | 0..* | `ContactPoint` |  |  | A contact detail for the care team (that applies to all members) |
| `CareTeam.note` | 0..* | `Annotation` |  |  | Comments made about the CareTeam |

Elements defined in ancestors: `CareTeam.id`, `CareTeam.meta`, `CareTeam.implicitRules`, `CareTeam.language`, `CareTeam.text`, `CareTeam.contained`, `CareTeam.extension`, `CareTeam.modifierExtension`, `CareTeam.participant.id`, `CareTeam.participant.extension`, `CareTeam.participant.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `CareTeam.participant` | `ctm-1` | error | CareTeam.participant.onBehalfOf can only be populated when CareTeam.participant.member is a Practitioner | `onBehalfOf.exists() implies (member.resolve().iif(empty(), true, ofType(Practitioner).exists()))` |
