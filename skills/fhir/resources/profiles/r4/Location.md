# Location

**ID** `Location` | **URL** `http://hl7.org/fhir/StructureDefinition/Location` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Patient Administration) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

Details and position information for a physical place where services are provided and resources and participants may be stored, found, contained, or accommodated.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Location` | 0..* | `Location` |  |  | Details and position information for a physical place |
| `Location.identifier` | 0..* | `Identifier` | summary |  | Unique code or number identifying the location to its users |
| `Location.status` | 0..1 | `code` | modifier summary | required→location-status@4.0.1 | active \| suspended \| inactive |
| `Location.operationalStatus` | 0..1 | `Coding` | summary | preferred→v2-0116 | The operational status of the location (typically only for a bed/room) |
| `Location.name` | 0..1 | `string` | summary |  | Name of the location as used by humans |
| `Location.alias` | 0..* | `string` |  |  | A list of alternate names that the location is known as, or was known as, in the past |
| `Location.description` | 0..1 | `string` | summary |  | Additional details about the location that could be displayed as further information to identify the location beyond it… |
| `Location.mode` | 0..1 | `code` | summary | required→location-mode@4.0.1 | instance \| kind |
| `Location.type` | 0..* | `CodeableConcept` | summary | extensible→v3-ServiceDeliveryLocationRoleType | Type of function performed |
| `Location.telecom` | 0..* | `ContactPoint` |  |  | Contact details of the location |
| `Location.address` | 0..1 | `Address` |  |  | Physical location |
| `Location.physicalType` | 0..1 | `CodeableConcept` | summary | example→location-physical-type | Physical form of the location |
| `Location.position` | 0..1 | `BackboneElement` |  |  | The absolute geographic location |
| `Location.position.longitude` | 1..1 | `decimal` |  |  | Longitude with WGS84 datum |
| `Location.position.latitude` | 1..1 | `decimal` |  |  | Latitude with WGS84 datum |
| `Location.position.altitude` | 0..1 | `decimal` |  |  | Altitude with WGS84 datum |
| `Location.managingOrganization` | 0..1 | `Reference(Organization)` | summary |  | Organization responsible for provisioning and upkeep |
| `Location.partOf` | 0..1 | `Reference(Location)` |  |  | Another Location this one is physically a part of |
| `Location.hoursOfOperation` | 0..* | `BackboneElement` |  |  | What days/times during a week is this location usually open |
| `Location.hoursOfOperation.daysOfWeek` | 0..* | `code` |  | required→days-of-week@4.0.1 | mon \| tue \| wed \| thu \| fri \| sat \| sun |
| `Location.hoursOfOperation.allDay` | 0..1 | `boolean` |  |  | The Location is open all day |
| `Location.hoursOfOperation.openingTime` | 0..1 | `time` |  |  | Time that the Location opens |
| `Location.hoursOfOperation.closingTime` | 0..1 | `time` |  |  | Time that the Location closes |
| `Location.availabilityExceptions` | 0..1 | `string` |  |  | Description of availability exceptions |
| `Location.endpoint` | 0..* | `Reference(Endpoint)` |  |  | Technical endpoints providing access to services operated for the location |

Elements defined in ancestors: `Location.id`, `Location.meta`, `Location.implicitRules`, `Location.language`, `Location.text`, `Location.contained`, `Location.extension`, `Location.modifierExtension`, `Location.position.id`, `Location.position.extension`, `Location.position.modifierExtension`, `Location.hoursOfOperation.id`, `Location.hoursOfOperation.extension`, `Location.hoursOfOperation.modifierExtension`

## Invariants

_No profile-specific invariants._
