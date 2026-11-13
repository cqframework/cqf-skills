# PractitionerRole

**ID** `PractitionerRole` | **URL** `http://hl7.org/fhir/StructureDefinition/PractitionerRole` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Patient Administration) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

A specific set of Roles/Locations/specialties/services that a practitioner may perform at an organization for a period of time.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `PractitionerRole` | 0..* | `PractitionerRole` |  |  | Roles/organizations the practitioner is associated with |
| `PractitionerRole.identifier` | 0..* | `Identifier` | summary |  | Business Identifiers that are specific to a role/location |
| `PractitionerRole.active` | 0..1 | `boolean` | summary |  | Whether this practitioner role record is in active use |
| `PractitionerRole.period` | 0..1 | `Period` | summary |  | The period during which the practitioner is authorized to perform in these role(s) |
| `PractitionerRole.practitioner` | 0..1 | `Reference(Practitioner)` | summary |  | Practitioner that is able to provide the defined services for the organization |
| `PractitionerRole.organization` | 0..1 | `Reference(Organization)` | summary |  | Organization where the roles are available |
| `PractitionerRole.code` | 0..* | `CodeableConcept` | summary | example→practitioner-role | Roles which this practitioner may perform |
| `PractitionerRole.specialty` | 0..* | `CodeableConcept` | summary | preferred→c80-practice-codes | Specific specialty of the practitioner |
| `PractitionerRole.location` | 0..* | `Reference(Location)` | summary |  | The location(s) at which this practitioner provides care |
| `PractitionerRole.healthcareService` | 0..* | `Reference(HealthcareService)` |  |  | The list of healthcare services that this worker provides for this role's Organization/Location(s) |
| `PractitionerRole.telecom` | 0..* | `ContactPoint` | summary |  | Contact details that are specific to the role/location/service |
| `PractitionerRole.availableTime` | 0..* | `BackboneElement` |  |  | Times the Service Site is available |
| `PractitionerRole.availableTime.daysOfWeek` | 0..* | `code` |  | required→days-of-week@4.0.1 | mon \| tue \| wed \| thu \| fri \| sat \| sun |
| `PractitionerRole.availableTime.allDay` | 0..1 | `boolean` |  |  | Always available? e.g. 24 hour service |
| `PractitionerRole.availableTime.availableStartTime` | 0..1 | `time` |  |  | Opening time of day (ignored if allDay = true) |
| `PractitionerRole.availableTime.availableEndTime` | 0..1 | `time` |  |  | Closing time of day (ignored if allDay = true) |
| `PractitionerRole.notAvailable` | 0..* | `BackboneElement` |  |  | Not available during this time due to provided reason |
| `PractitionerRole.notAvailable.description` | 1..1 | `string` |  |  | Reason presented to the user explaining why time not available |
| `PractitionerRole.notAvailable.during` | 0..1 | `Period` |  |  | Service not available from this date |
| `PractitionerRole.availabilityExceptions` | 0..1 | `string` |  |  | Description of availability exceptions |
| `PractitionerRole.endpoint` | 0..* | `Reference(Endpoint)` |  |  | Technical endpoints providing access to services operated for the practitioner with this role |

Elements defined in ancestors: `PractitionerRole.id`, `PractitionerRole.meta`, `PractitionerRole.implicitRules`, `PractitionerRole.language`, `PractitionerRole.text`, `PractitionerRole.contained`, `PractitionerRole.extension`, `PractitionerRole.modifierExtension`, `PractitionerRole.availableTime.id`, `PractitionerRole.availableTime.extension`, `PractitionerRole.availableTime.modifierExtension`, `PractitionerRole.notAvailable.id`, `PractitionerRole.notAvailable.extension`, `PractitionerRole.notAvailable.modifierExtension`

## Invariants

_No profile-specific invariants._
