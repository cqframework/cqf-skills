# Device

**ID** `Device` | **URL** `http://hl7.org/fhir/StructureDefinition/Device` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Orders and Observations) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

A type of a manufactured item that is used in the provision of healthcare without being substantially changed through that activity. The device may be a medical or non-medical device.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Device` | 0..* | `Device` |  |  | Item used in healthcare |
| `Device.identifier` | 0..* | `Identifier` |  |  | Instance identifier |
| `Device.definition` | 0..1 | `Reference(DeviceDefinition)` |  |  | The reference to the definition for the device |
| `Device.udiCarrier` | 0..* | `BackboneElement` | summary |  | Unique Device Identifier (UDI) Barcode string |
| `Device.udiCarrier.deviceIdentifier` | 0..1 | `string` | summary |  | Mandatory fixed portion of UDI |
| `Device.udiCarrier.issuer` | 0..1 | `uri` |  |  | UDI Issuing Organization |
| `Device.udiCarrier.jurisdiction` | 0..1 | `uri` |  |  | Regional UDI authority |
| `Device.udiCarrier.carrierAIDC` | 0..1 | `base64Binary` | summary |  | UDI Machine Readable Barcode String |
| `Device.udiCarrier.carrierHRF` | 0..1 | `string` | summary |  | UDI Human Readable Barcode String |
| `Device.udiCarrier.entryType` | 0..1 | `code` |  | required→udi-entry-type@4.0.1 | barcode \| rfid \| manual + |
| `Device.status` | 0..1 | `code` | modifier summary | required→device-status@4.0.1 | active \| inactive \| entered-in-error \| unknown |
| `Device.statusReason` | 0..* | `CodeableConcept` |  | extensible→device-status-reason | online \| paused \| standby \| offline \| not-ready \| transduc-discon \| hw-discon \| off |
| `Device.distinctIdentifier` | 0..1 | `string` |  |  | The distinct identification string |
| `Device.manufacturer` | 0..1 | `string` |  |  | Name of device manufacturer |
| `Device.manufactureDate` | 0..1 | `dateTime` |  |  | Date when the device was made |
| `Device.expirationDate` | 0..1 | `dateTime` |  |  | Date and time of expiry of this device (if applicable) |
| `Device.lotNumber` | 0..1 | `string` |  |  | Lot number of manufacture |
| `Device.serialNumber` | 0..1 | `string` |  |  | Serial number assigned by the manufacturer |
| `Device.deviceName` | 0..* | `BackboneElement` |  |  | The name of the device as given by the manufacturer |
| `Device.deviceName.name` | 1..1 | `string` |  |  | The name of the device |
| `Device.deviceName.type` | 1..1 | `code` |  | required→device-nametype@4.0.1 | udi-label-name \| user-friendly-name \| patient-reported-name \| manufacturer-name \| model-name \| other |
| `Device.modelNumber` | 0..1 | `string` |  |  | The model number for the device |
| `Device.partNumber` | 0..1 | `string` |  |  | The part number of the device |
| `Device.type` | 0..1 | `CodeableConcept` |  | example→device-type | The kind or type of device |
| `Device.specialization` | 0..* | `BackboneElement` |  |  | The capabilities supported on a device, the standards to which the device conforms for a particular purpose, and used f… |
| `Device.specialization.systemType` | 1..1 | `CodeableConcept` |  |  | The standard that is used to operate and communicate |
| `Device.specialization.version` | 0..1 | `string` |  |  | The version of the standard that is used to operate and communicate |
| `Device.version` | 0..* | `BackboneElement` |  |  | The actual design of the device or software version running on the device |
| `Device.version.type` | 0..1 | `CodeableConcept` |  |  | The type of the device version |
| `Device.version.component` | 0..1 | `Identifier` |  |  | A single component of the device version |
| `Device.version.value` | 1..1 | `string` |  |  | The version text |
| `Device.property` | 0..* | `BackboneElement` |  |  | The actual configuration settings of a device as it actually operates, e.g., regulation status, time properties |
| `Device.property.type` | 1..1 | `CodeableConcept` |  |  | Code that specifies the property DeviceDefinitionPropetyCode (Extensible) |
| `Device.property.valueQuantity` | 0..* | `Quantity` |  |  | Property value as a quantity |
| `Device.property.valueCode` | 0..* | `CodeableConcept` |  |  | Property value as a code, e.g., NTP4 (synced to NTP) |
| `Device.patient` | 0..1 | `Reference(Patient)` |  |  | Patient to whom Device is affixed |
| `Device.owner` | 0..1 | `Reference(Organization)` |  |  | Organization responsible for device |
| `Device.contact` | 0..* | `ContactPoint` |  |  | Details for human/organization for support |
| `Device.location` | 0..1 | `Reference(Location)` |  |  | Where the device is found |
| `Device.url` | 0..1 | `uri` |  |  | Network address to contact device |
| `Device.note` | 0..* | `Annotation` |  |  | Device notes and comments |
| `Device.safety` | 0..* | `CodeableConcept` | summary |  | Safety Characteristics of Device |
| `Device.parent` | 0..1 | `Reference(Device)` |  |  | The parent device |

Elements defined in ancestors: `Device.id`, `Device.meta`, `Device.implicitRules`, `Device.language`, `Device.text`, `Device.contained`, `Device.extension`, `Device.modifierExtension`, `Device.udiCarrier.id`, `Device.udiCarrier.extension`, `Device.udiCarrier.modifierExtension`, `Device.deviceName.id`, `Device.deviceName.extension`, `Device.deviceName.modifierExtension`, `Device.specialization.id`, `Device.specialization.extension`, `Device.specialization.modifierExtension`, `Device.version.id`, `Device.version.extension`, `Device.version.modifierExtension`, `Device.property.id`, `Device.property.extension`, `Device.property.modifierExtension`

## Invariants

_No profile-specific invariants._
