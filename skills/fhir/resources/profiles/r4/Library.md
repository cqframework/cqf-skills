# Library

**ID** `Library` | **URL** `http://hl7.org/fhir/StructureDefinition/Library` | **Status** draft
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Clinical Decision Support) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

The Library resource is a general-purpose container for knowledge asset definitions. It can be used to describe and expose existing knowledge assets such as logic libraries and information model descriptions, as well as to describe a collection of knowledge assets.

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Library` | 0..* | `Library` |  |  | Represents a library of quality improvement components |
| `Library.url` | 0..1 | `uri` | summary |  | Canonical identifier for this library, represented as a URI (globally unique) |
| `Library.identifier` | 0..* | `Identifier` | summary |  | Additional identifier for the library |
| `Library.version` | 0..1 | `string` | summary |  | Business version of the library |
| `Library.name` | 0..1 | `string` | summary |  | Name for this library (computer friendly) |
| `Library.title` | 0..1 | `string` | summary |  | Name for this library (human friendly) |
| `Library.subtitle` | 0..1 | `string` |  |  | Subordinate title of the library |
| `Library.status` | 1..1 | `code` | modifier summary | required→publication-status@4.0.1 | draft \| active \| retired \| unknown |
| `Library.experimental` | 0..1 | `boolean` | summary |  | For testing purposes, not real usage |
| `Library.type` | 1..1 | `CodeableConcept` | summary | extensible→library-type | logic-library \| model-definition \| asset-collection \| module-definition |
| `Library.subject[x]` | 0..1 | `CodeableConcept, Reference(Group)` |  | extensible→subject-type | Type of individual the library content is focused on |
| `Library.date` | 0..1 | `dateTime` | summary |  | Date last changed |
| `Library.publisher` | 0..1 | `string` | summary |  | Name of the publisher (organization or individual) |
| `Library.contact` | 0..* | `ContactDetail` | summary |  | Contact details for the publisher |
| `Library.description` | 0..1 | `markdown` | summary |  | Natural language description of the library |
| `Library.useContext` | 0..* | `UsageContext` | summary |  | The context that the content is intended to support |
| `Library.jurisdiction` | 0..* | `CodeableConcept` | summary | extensible→jurisdiction | Intended jurisdiction for library (if applicable) |
| `Library.purpose` | 0..1 | `markdown` |  |  | Why this library is defined |
| `Library.usage` | 0..1 | `string` |  |  | Describes the clinical usage of the library |
| `Library.copyright` | 0..1 | `markdown` |  |  | Use and/or publishing restrictions |
| `Library.approvalDate` | 0..1 | `date` |  |  | When the library was approved by publisher |
| `Library.lastReviewDate` | 0..1 | `date` |  |  | When the library was last reviewed |
| `Library.effectivePeriod` | 0..1 | `Period` | summary |  | When the library is expected to be used |
| `Library.topic` | 0..* | `CodeableConcept` |  | example→definition-topic | E.g. Education, Treatment, Assessment, etc. |
| `Library.author` | 0..* | `ContactDetail` |  |  | Who authored the content |
| `Library.editor` | 0..* | `ContactDetail` |  |  | Who edited the content |
| `Library.reviewer` | 0..* | `ContactDetail` |  |  | Who reviewed the content |
| `Library.endorser` | 0..* | `ContactDetail` |  |  | Who endorsed the content |
| `Library.relatedArtifact` | 0..* | `RelatedArtifact` |  |  | Additional documentation, citations, etc. |
| `Library.parameter` | 0..* | `ParameterDefinition` |  |  | Parameters defined by the library |
| `Library.dataRequirement` | 0..* | `DataRequirement` |  |  | What data is referenced by this library |
| `Library.content` | 0..* | `Attachment` | summary |  | Contents of the library, either embedded or referenced |

Elements defined in ancestors: `Library.id`, `Library.meta`, `Library.implicitRules`, `Library.language`, `Library.text`, `Library.contained`, `Library.extension`, `Library.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `Library` | `lib-0` | warning | Name should be usable as an identifier for the module by machine processing applications such as code generation | `name.matches('[A-Z]([A-Za-z0-9_]){0,254}')` |
