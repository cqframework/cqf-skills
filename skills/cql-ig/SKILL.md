---
name: cql-ig
description: Applies the Using CQL With FHIR IG (hl7.fhir.uv.cql 2.0.0), which publishes the FHIR ModelInfo, FHIRHelpers and FHIRCommon. Covers its conformance rules for CQL written against FHIR, packaging CQL as a FHIR Library (CQLLibrary and ELM profiles, relatedArtifact, parameters, dataRequirement), the CQL-to-FHIR type mapping, $cql and Library/$evaluate, and FHIR authoring patterns (primitives, choices, extensions, missing data, negation). Use when CQL uses FHIR, a FHIR Library carries CQL, or someone asks what FHIRHelpers, FHIRCommon or the FHIR ModelInfo provide.
license: Apache-2.0
---

# Using CQL With FHIR

The Using CQL With FHIR IG (`hl7.fhir.uv.cql`) says how CQL is written against FHIR and how it is
carried in FHIR resources. It also publishes the shared pieces that CQL against FHIR depends on:
the FHIR ModelInfo (the CQL model of FHIR R4), FHIRHelpers (conversions between FHIR and CQL
types) and FHIRCommon (common codes and fluent functions). This skill covers version 2.0.0 (STU2,
FHIR R4), the current release. A 3.0.0 ballot exists, but this skill doesn't cover it.

For CQL language semantics, see the `cql` skill. For the `cqf-` extensions this IG uses, see the
`fhir-extensions` skill. For CRMI and CPG artifact profiles, see the `crmi` and `cpg` skills.

## Reference

| Path | Contents |
| --- | --- |
| [resources/pages/README.md](resources/pages/README.md) | The IG's narrative pages: Using CQL, Patterns, Conformance, Using ELM, Using ModelInfo, Operations |
| [resources/libraries/README.md](resources/libraries/README.md) | FHIRHelpers, FHIRCommon and their test libraries, as published CQL |
| [resources/modelinfo/README.md](resources/modelinfo/README.md) | The FHIR ModelInfo: contexts, primary code paths, conversions, and every type's elements |
| `resources/profiles/concise/` | The IG's profiles, operations and examples, rendered. Build with `bash scripts/build-kb.sh`; the format is in [format-guide.md](resources/format-guide.md). |

`scripts/build-ig.py` regenerates the committed pages, libraries and ModelInfo from the pinned
package and IG source (all CC0). The knowledge base under `resources/profiles/` is built
locally and not committed.

Conformance requirements are numbered by page: 2.x in `pages/using-cql.md`, 4.x in
`pages/conformance.md`, 5.x in `pages/using-elm.md` and 6.x in `pages/using-modelinfo.md`. Cite
them by number. To list them all:
`grep -h -A3 '^\*\*Conformance Requirement' resources/pages/*.md`

## Writing CQL against FHIR

These are the Using CQL requirements (2.x). Follow them in any CQL a FHIR artifact uses.

```cql
library ExampleScreening version '1.0.0'

using FHIR version '4.0.1'

include FHIRHelpers version '4.0.1' called FHIRHelpers
include FHIRCommon version '2.0.0' called FC

codesystem "LOINC": 'http://loinc.org'
valueset "Diabetes": 'http://example.org/fhir/ValueSet/diabetes'
code "HbA1c": '4548-4' from "LOINC" display 'Hemoglobin A1c'

context Patient

define "Active Diabetes":
  [Condition: "Diabetes"] C
    where C.isActive()
```

- **Library name (2.1):** alphanumeric only, with no underscores, and unquoted. The version
  SHOULD be `major.minor.patch` (2.2). A namespace SHOULD be used, and its root SHALL match the
  root of the Library resource's URL (2.4).
- **Model (2.5):** `using FHIR version '4.0.1'`. The version is required.
- **Includes (2.3):** every `include` SHALL have a `called` alias. Include FHIRHelpers with its
  version, because the ModelInfo's implicit conversions call it. Without it, any comparison of a
  FHIR element to a CQL value fails with "Could not resolve library name FHIRHelpers".
- **Code systems and value sets (2.6, 2.7):** identify them by canonical URL. Put a value set
  version in the `version` clause (2.8). A code system version follows FHIR's form, such as
  `version 'http://snomed.info/sct/731000124108/version/20250301'` for SNOMED CT.
- **Membership (2.9, 2.10):** test with `in "Value Set"`, one value set at a time, rather than a
  union of expansions, and don't test membership against strings.
- **Codes (2.11):** a direct-reference code's identifier SHALL NOT be a URI and SHOULD be the code
  from the code system.
- **Concepts (2.12):** a `concept` SHALL NOT stand in for a value set.
- **Names (2.13 to 2.16):** library-level identifiers are descriptive Initial Case, quoted if
  needed. Type names are PascalCase and unquoted. Elements are camelCase and unquoted. Aliases are
  PascalCase and arguments camelCase, and neither is quoted.

## FHIR in CQL

The FHIR ModelInfo is how CQL sees FHIR. Check it, not the FHIR spec, for the CQL type of an
element.

- **Primitives:** a FHIR `string` is the type `FHIR.string`, whose value is in `.value`. The
  ModelInfo declares implicit conversions to System types through FHIRHelpers
  ([conversions.md](resources/modelinfo/conversions.md)), so `Patient.gender = 'female'` works.
  Code-bound elements have generated types, such as `FHIR.ObservationStatus`, that convert to
  `System.String`.
- **Choices:** `value[x]` is the element `value` with type `Choice<...>`, so narrow it with
  `as` or `is` (`O.value as Quantity`). FHIRCommon's `toInterval()` turns `effective`, `onset`
  and similar choices into an interval.
- **Retrieves:** `[Condition: "Diabetes"]` filters on the type's primary code path (`code` for
  Condition, `medication` for MedicationRequest). Check the path in the ModelInfo README before
  relying on a terminology retrieve. A type with no primary code path, such as AuditEvent, needs
  an explicit path: `[AuditEvent: type in "Value Set"]`. Without one, the translator only warns
  ("does not have a primary code path defined"). The ELM retrieve then has codes but no
  `codeProperty`, so which element an engine filters on is undefined.
- **Contexts:** Patient, Practitioner, Device, Encounter and RelatedPerson. Each resource lists the
  elements that relate it to each context.
- **Extensions and slices:** reach them by filtering `extension` on `url`, or `component` on
  `code`, inside a fluent function. FHIRCommon provides `ext()`, `exts()`, `modifierExt()` and
  `modifierExts()` for extensions.
- **Missing data:** absent elements are `null`, and `null` in a `where` acts as false. Write
  `MR.doNotPerform is not true` rather than `= false`. Treat a status of `unknown` as missing.
- **Negation:** look for "documented as not done, with a reason" only when the reason is part of
  the intent. Otherwise use absence of evidence. `pages/patterns.md` (Negation in FHIR) has the
  patterns for each case.
- **FHIRCommon** (version 2.0.0) has Condition and AllergyIntolerance status functions
  (`isActive()`, `verified()`, `confirmed()`), Observation category and status functions
  (`isLaboratory()`, `resulted()`), `mostRecent()`, `references()` and codes for common status
  values. Read [FHIRCommon.cql](resources/libraries/FHIRCommon.cql) for the exact definitions
  before relying on one. For example, `isActive()` on a Condition means a clinical status of
  active, recurrence or relapse.

## Packaging CQL in a FHIR Library

Requirements 4.x and 5.x. The IG's example Libraries don't meet all of these (they omit the
ModelInfo `depends-on`, the `cqf-cqlType` extensions and `called` aliases), so follow the
requirements rather than copying the examples.

- **Profile (4.1):** a Library carrying CQL SHALL conform to CQLLibrary
  (`http://hl7.org/fhir/uv/cql/StructureDefinition/cql-library`). It needs exactly one content
  item whose type starts with `text/cql` (clb-1), with `data` or a `url` (clb-2). Its `type` is
  `logic-library`. A Library carrying ELM conforms to ELMJSONLibrary or ELMXMLLibrary (5.1).
- **Identity (4.2):** `url` is `{namespace URL}/Library/{library name}`, `name` is the CQL library
  name (64 characters or fewer, and preferably 30 or fewer), and `version` is the CQL version.
- **CQL version (4.6):** state it in the media type, `text/cql; version=1.5`, giving the major and
  minor version of a published CQL release. If you do, say it in the narrative too.
- **Dependencies (4.5):** a `relatedArtifact` of type `depends-on` for each `using`, `include`,
  code system and value set. The published canonicals are
  `http://hl7.org/fhir/uv/cql/Library/FHIR-ModelInfo|4.0.1` and
  `http://hl7.org/fhir/uv/cql/Library/FHIRHelpers|4.0.1`. The examples on the conformance page
  give older `http://hl7.org/fhir/Library/...` URLs.
- **Parameters (4.4):** a `parameter` with `use: in` for each CQL parameter, and `use: out` for
  every top-level expression, regardless of access level. A list result has `max: "*"`. Give the
  CQL type in the `cqf-cqlType` extension (for example `List<FHIR.Observation>`).
- **Data requirements (4.4):** a `dataRequirement` for each retrieve. The retrieve's type goes in
  `type`, its profile in `profile`, its code path in `codeFilter.path`, and its value set in
  `codeFilter.valueSet` (or its codes in `codeFilter.code`).
- **Translator options (5.2, 5.3):** use EnableAnnotations, EnableLocators, DisableListDemotion and
  DisableListPromotion, a SignatureLevel of `Overloads` or `All`, and not
  DisableMethodInvocation. Record the options with the `cqf-cqlOptions` extension, which points
  to a contained CQLOptions Parameters resource.

## Results and operations

- **Type mapping (4.3):** `System.Boolean` maps to `boolean`, `Integer` to `integer`, `Decimal` to
  `decimal`, `String` to `string`, `Date` to `date`, `DateTime` to `dateTime`, `Time` to `time`,
  `Quantity` to `Quantity`, `Ratio` to `Ratio`, `Code` to `Coding`, `Concept` to
  `CodeableConcept`, `Interval<Date>` and `Interval<DateTime>` to `Period`, and
  `Interval<Quantity>` to `Range`. In R4, `System.Long` maps to `string`.
- **Results in Parameters:** a list is one repeated parameter per item. A tuple is a parameter
  with `part`s. A nested list uses parts named `element`. An empty list or empty tuple is a
  `_valueBoolean` that carries the `cqf-isEmptyList` or `cqf-isEmptyTuple` extension.
- **`$cql`** (system level): evaluates one CQL expression (`expression`, 1..1, which is an
  expression, not a library) with optional `subject`, `parameters`, `library`, `data` and
  endpoints. It returns the result in `return`.
- **`Library/$evaluate`** (type or instance level): evaluates a library, identified by `url` or
  `library` at the type level. `expression` names which definitions to evaluate (all public ones
  by default), and `includePrivate` adds the private ones. `return` is a Parameters resource with
  one parameter per expression.

The parameter tables are in the knowledge base (`OperationDefinition-cql-cql.md`,
`OperationDefinition-cql-library-evaluate.md`), and `pages/operations.md` has worked examples.

## ModelInfo for profiles

To give CQL a model of an IG's profiles, ModelInfo is generated from the StructureDefinitions
(`pages/using-modelinfo.md`). The settings go in a CQLModelInfoSettings Parameters resource, and
the `cqf-modelInfo-*` extensions adjust each profile (its label, primary code path, whether it is
retrievable and whether it is included). A ModelInfo Library conforms to CQLModelInfo, with `url`
`{model namespace URL}/Library/{model name}-ModelInfo` (6.1).
