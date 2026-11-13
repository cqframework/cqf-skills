# Bundle

**ID** `Bundle` | **URL** `http://hl7.org/fhir/StructureDefinition/Bundle` | **Status** active
**Base** `Resource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (FHIR Infrastructure) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

A container for a collection of resources.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Bundle` | 0..* | `Bundle` |  |  | Contains a collection of resources |
| `Bundle.identifier` | 0..1 | `Identifier` | summary |  | Persistent identifier for the bundle |
| `Bundle.type` | 1..1 | `code` | summary | required→bundle-type@4.0.1 | document \| message \| transaction \| transaction-response \| batch \| batch-response \| history \| searchset \| collection |
| `Bundle.timestamp` | 0..1 | `instant` | summary |  | When the bundle was assembled |
| `Bundle.total` | 0..1 | `unsignedInt` | summary |  | If search, the total number of matches |
| `Bundle.link` | 0..* | `BackboneElement` | summary |  | Links related to this Bundle |
| `Bundle.link.relation` | 1..1 | `string` | summary |  | See http://www.iana.org/assignments/link-relations/link-relations.xhtml#link-relations-1 |
| `Bundle.link.url` | 1..1 | `uri` | summary |  | Reference details for the link |
| `Bundle.entry` | 0..* | `BackboneElement` | summary |  | Entry in the bundle - will have a resource or information |
| `Bundle.entry.link` | 0..* | `see Bundle.link` | summary |  | Links related to this entry |
| `Bundle.entry.fullUrl` | 0..1 | `uri` | summary |  | URI for resource (Absolute URL server address or URI for UUID/OID) |
| `Bundle.entry.resource` | 0..1 | `Resource` | summary |  | A resource in the bundle |
| `Bundle.entry.search` | 0..1 | `BackboneElement` | summary |  | Search related information |
| `Bundle.entry.search.mode` | 0..1 | `code` | summary | required→search-entry-mode@4.0.1 | match \| include \| outcome - why this is in the result set |
| `Bundle.entry.search.score` | 0..1 | `decimal` | summary |  | Search ranking (between 0 and 1) |
| `Bundle.entry.request` | 0..1 | `BackboneElement` | summary |  | Additional execution information (transaction/batch/history) |
| `Bundle.entry.request.method` | 1..1 | `code` | summary | required→http-verb@4.0.1 | GET \| HEAD \| POST \| PUT \| DELETE \| PATCH |
| `Bundle.entry.request.url` | 1..1 | `uri` | summary |  | URL for HTTP equivalent of this entry |
| `Bundle.entry.request.ifNoneMatch` | 0..1 | `string` | summary |  | For managing cache currency |
| `Bundle.entry.request.ifModifiedSince` | 0..1 | `instant` | summary |  | For managing cache currency |
| `Bundle.entry.request.ifMatch` | 0..1 | `string` | summary |  | For managing update contention |
| `Bundle.entry.request.ifNoneExist` | 0..1 | `string` | summary |  | For conditional creates |
| `Bundle.entry.response` | 0..1 | `BackboneElement` | summary |  | Results of execution (transaction/batch/history) |
| `Bundle.entry.response.status` | 1..1 | `string` | summary |  | Status response code (text optional) |
| `Bundle.entry.response.location` | 0..1 | `uri` | summary |  | The location (if the operation returns a location) |
| `Bundle.entry.response.etag` | 0..1 | `string` | summary |  | The Etag for the resource (if relevant) |
| `Bundle.entry.response.lastModified` | 0..1 | `instant` | summary |  | Server's date time modified |
| `Bundle.entry.response.outcome` | 0..1 | `Resource` | summary |  | OperationOutcome with hints and warnings (for batch/transaction) |
| `Bundle.signature` | 0..1 | `Signature` | summary |  | Digital Signature |

Elements defined in ancestors: `Bundle.id`, `Bundle.meta`, `Bundle.implicitRules`, `Bundle.language`, `Bundle.link.id`, `Bundle.link.extension`, `Bundle.link.modifierExtension`, `Bundle.entry.id`, `Bundle.entry.extension`, `Bundle.entry.modifierExtension`, `Bundle.entry.search.id`, `Bundle.entry.search.extension`, `Bundle.entry.search.modifierExtension`, `Bundle.entry.request.id`, `Bundle.entry.request.extension`, `Bundle.entry.request.modifierExtension`, `Bundle.entry.response.id`, `Bundle.entry.response.extension`, `Bundle.entry.response.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `Bundle` | `bdl-1` | error | total only when a search or history | `total.empty() or (type = 'searchset') or (type = 'history')` |
| `Bundle` | `bdl-2` | error | entry.search only when a search | `entry.search.empty() or (type = 'searchset')` |
| `Bundle` | `bdl-3` | error | entry.request mandatory for batch/transaction/history, otherwise prohibited | `entry.all(request.exists() = (%resource.type = 'batch' or %resource.type = 'transaction' or %resource.type = 'history'))` |
| `Bundle` | `bdl-4` | error | entry.response mandatory for batch-response/transaction-response/history, otherwise prohibited | `entry.all(response.exists() = (%resource.type = 'batch-response' or %resource.type = 'transaction-response' or %resource.type = 'history'))` |
| `Bundle` | `bdl-7` | error | FullUrl must be unique in a bundle, or else entries with the same fullUrl must have different meta.versionId (except in history bundles) | `(type = 'history') or entry.where(fullUrl.exists()).select(fullUrl&resource.meta.versionId).isDistinct()` |
| `Bundle` | `bdl-9` | error | A document must have an identifier with a system and a value | `type = 'document' implies (identifier.system.exists() and identifier.value.exists())` |
| `Bundle` | `bdl-10` | error | A document must have a date | `type = 'document' implies (timestamp.hasValue())` |
| `Bundle` | `bdl-11` | error | A document must have a Composition as the first resource | `type = 'document' implies entry.first().resource.is(Composition)` |
| `Bundle` | `bdl-12` | error | A message must have a MessageHeader as the first resource | `type = 'message' implies entry.first().resource.is(MessageHeader)` |
| `Bundle.entry` | `bdl-5` | error | must be a resource unless there's a request or response | `resource.exists() or request.exists() or response.exists()` |
| `Bundle.entry` | `bdl-8` | error | fullUrl cannot be a version specific reference | `fullUrl.contains('/_history/').not()` |
