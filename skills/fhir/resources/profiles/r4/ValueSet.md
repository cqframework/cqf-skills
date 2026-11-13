# ValueSet

**ID** `ValueSet` | **URL** `http://hl7.org/fhir/StructureDefinition/ValueSet` | **Status** active
**Base** `DomainResource` | **Derivation** specialization | **Kind** resource
**Version** 4.0.1 | **Publisher** Health Level Seven International (Vocabulary) | **Package** `hl7.fhir.r4.core@4.0.1`

_Legend: `MS` mustSupport · `modifier` isModifier · `summary` isSummary · `(MS)` in Type applies to that type or target._

## Description

A ValueSet resource instance specifies a set of codes drawn from one or more code systems, intended for use in a particular context. Value sets link between [[[CodeSystem]]] definitions and their use in [coded elements](terminologies.html).

## Elements

| Path | Card | Type | Flags | Binding | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ValueSet` | 0..* | `ValueSet` |  |  | A set of codes drawn from one or more code systems |
| `ValueSet.url` | 0..1 | `uri` | summary |  | Canonical identifier for this value set, represented as a URI (globally unique) |
| `ValueSet.identifier` | 0..* | `Identifier` | summary |  | Additional identifier for the value set (business identifier) |
| `ValueSet.version` | 0..1 | `string` | summary |  | Business version of the value set |
| `ValueSet.name` | 0..1 | `string` | summary |  | Name for this value set (computer friendly) |
| `ValueSet.title` | 0..1 | `string` | summary |  | Name for this value set (human friendly) |
| `ValueSet.status` | 1..1 | `code` | modifier summary | required→publication-status@4.0.1 | draft \| active \| retired \| unknown |
| `ValueSet.experimental` | 0..1 | `boolean` | summary |  | For testing purposes, not real usage |
| `ValueSet.date` | 0..1 | `dateTime` | summary |  | Date last changed |
| `ValueSet.publisher` | 0..1 | `string` | summary |  | Name of the publisher (organization or individual) |
| `ValueSet.contact` | 0..* | `ContactDetail` | summary |  | Contact details for the publisher |
| `ValueSet.description` | 0..1 | `markdown` |  |  | Natural language description of the value set |
| `ValueSet.useContext` | 0..* | `UsageContext` | summary |  | The context that the content is intended to support |
| `ValueSet.jurisdiction` | 0..* | `CodeableConcept` | summary | extensible→jurisdiction | Intended jurisdiction for value set (if applicable) |
| `ValueSet.immutable` | 0..1 | `boolean` | summary |  | Indicates whether or not any change to the content logical definition may occur |
| `ValueSet.purpose` | 0..1 | `markdown` |  |  | Why this value set is defined |
| `ValueSet.copyright` | 0..1 | `markdown` |  |  | Use and/or publishing restrictions |
| `ValueSet.compose` | 0..1 | `BackboneElement` |  |  | Content logical definition of the value set (CLD) |
| `ValueSet.compose.lockedDate` | 0..1 | `date` | summary |  | Fixed date for references with no specified version (transitive) |
| `ValueSet.compose.inactive` | 0..1 | `boolean` | summary |  | Whether inactive codes are in the value set |
| `ValueSet.compose.include` | 1..* | `BackboneElement` | summary |  | Include one or more codes from a code system or other value set(s) |
| `ValueSet.compose.include.system` | 0..1 | `uri` | summary |  | The system the codes come from |
| `ValueSet.compose.include.version` | 0..1 | `string` | summary |  | Specific version of the code system referred to |
| `ValueSet.compose.include.concept` | 0..* | `BackboneElement` |  |  | A concept defined in the system |
| `ValueSet.compose.include.concept.code` | 1..1 | `code` |  |  | Code or expression from system |
| `ValueSet.compose.include.concept.display` | 0..1 | `string` |  |  | Text to display for this code for this value set in this valueset |
| `ValueSet.compose.include.concept.designation` | 0..* | `BackboneElement` |  |  | Additional representations for this concept |
| `ValueSet.compose.include.concept.designation.language` | 0..1 | `code` |  | preferred→languages | Human language of the designation |
| `ValueSet.compose.include.concept.designation.use` | 0..1 | `Coding` |  | extensible→designation-use | Types of uses of designations |
| `ValueSet.compose.include.concept.designation.value` | 1..1 | `string` |  |  | The text value for this designation |
| `ValueSet.compose.include.filter` | 0..* | `BackboneElement` | summary |  | Select codes/concepts by their properties (including relationships) |
| `ValueSet.compose.include.filter.property` | 1..1 | `code` | summary |  | A property/filter defined by the code system |
| `ValueSet.compose.include.filter.op` | 1..1 | `code` | summary | required→filter-operator@4.0.1 | = \| is-a \| descendent-of \| is-not-a \| regex \| in \| not-in \| generalizes \| exists |
| `ValueSet.compose.include.filter.value` | 1..1 | `string` | summary |  | Code from the system, or regex criteria, or boolean value for exists |
| `ValueSet.compose.include.valueSet` | 0..* | `canonical(ValueSet)` | summary |  | Select the contents included in this value set |
| `ValueSet.compose.exclude` | 0..* | `see ValueSet.compose.include` |  |  | Explicitly exclude codes from a code system or other value sets |
| `ValueSet.expansion` | 0..1 | `BackboneElement` |  |  | Used when the value set is "expanded" |
| `ValueSet.expansion.identifier` | 0..1 | `uri` |  |  | Identifies the value set expansion (business identifier) |
| `ValueSet.expansion.timestamp` | 1..1 | `dateTime` |  |  | Time ValueSet expansion happened |
| `ValueSet.expansion.total` | 0..1 | `integer` |  |  | Total number of codes in the expansion |
| `ValueSet.expansion.offset` | 0..1 | `integer` |  |  | Offset at which this resource starts |
| `ValueSet.expansion.parameter` | 0..* | `BackboneElement` |  |  | Parameter that controlled the expansion process |
| `ValueSet.expansion.parameter.name` | 1..1 | `string` |  |  | Name as assigned by the client or server |
| `ValueSet.expansion.parameter.value[x]` | 0..1 | `string, boolean, integer, decimal, uri, code, dateTime` |  |  | Value of the named parameter |
| `ValueSet.expansion.contains` | 0..* | `BackboneElement` |  |  | Codes in the value set |
| `ValueSet.expansion.contains.system` | 0..1 | `uri` |  |  | System value for the code |
| `ValueSet.expansion.contains.abstract` | 0..1 | `boolean` |  |  | If user cannot select this entry |
| `ValueSet.expansion.contains.inactive` | 0..1 | `boolean` |  |  | If concept is inactive in the code system |
| `ValueSet.expansion.contains.version` | 0..1 | `string` |  |  | Version in which this code/display is defined |
| `ValueSet.expansion.contains.code` | 0..1 | `code` |  |  | Code - if blank, this is not a selectable code |
| `ValueSet.expansion.contains.display` | 0..1 | `string` |  |  | User display for the concept |
| `ValueSet.expansion.contains.designation` | 0..* | `see ValueSet.compose.include.concept.designation` |  |  | Additional representations for this item |
| `ValueSet.expansion.contains.contains` | 0..* | `see ValueSet.expansion.contains` |  |  | Codes contained under this entry |

Elements defined in ancestors: `ValueSet.id`, `ValueSet.meta`, `ValueSet.implicitRules`, `ValueSet.language`, `ValueSet.text`, `ValueSet.contained`, `ValueSet.extension`, `ValueSet.modifierExtension`, `ValueSet.compose.id`, `ValueSet.compose.extension`, `ValueSet.compose.modifierExtension`, `ValueSet.compose.include.id`, `ValueSet.compose.include.extension`, `ValueSet.compose.include.modifierExtension`, `ValueSet.compose.include.concept.id`, `ValueSet.compose.include.concept.extension`, `ValueSet.compose.include.concept.modifierExtension`, `ValueSet.compose.include.concept.designation.id`, `ValueSet.compose.include.concept.designation.extension`, `ValueSet.compose.include.concept.designation.modifierExtension`, `ValueSet.compose.include.filter.id`, `ValueSet.compose.include.filter.extension`, `ValueSet.compose.include.filter.modifierExtension`, `ValueSet.expansion.id`, `ValueSet.expansion.extension`, `ValueSet.expansion.modifierExtension`, `ValueSet.expansion.parameter.id`, `ValueSet.expansion.parameter.extension`, `ValueSet.expansion.parameter.modifierExtension`, `ValueSet.expansion.contains.id`, `ValueSet.expansion.contains.extension`, `ValueSet.expansion.contains.modifierExtension`

## Invariants

| Path | Key | Severity | Human | Expression |
| :--- | :--- | :--- | :--- | :--- |
| `ValueSet` | `vsd-0` | warning | Name should be usable as an identifier for the module by machine processing applications such as code generation | `name.matches('[A-Z]([A-Za-z0-9_]){0,254}')` |
| `ValueSet.compose.include` | `vsd-1` | error | A value set include/exclude SHALL have a value set or a system | `valueSet.exists() or system.exists()` |
| `ValueSet.compose.include` | `vsd-2` | error | A value set with concepts or filters SHALL include a system | `(concept.exists() or filter.exists()) implies system.exists()` |
| `ValueSet.compose.include` | `vsd-3` | error | Cannot have both concept and filter | `concept.empty() or filter.empty()` |
| `ValueSet.expansion.contains` | `vsd-6` | error | SHALL have a code or a display | `code.exists() or display.exists()` |
| `ValueSet.expansion.contains` | `vsd-9` | error | Must have a code if not abstract | `code.exists() or abstract = true` |
| `ValueSet.expansion.contains` | `vsd-10` | error | Must have a system if a code is present | `code.empty() or system.exists()` |
