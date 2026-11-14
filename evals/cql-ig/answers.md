# CQL IG Skill Test Questions: Answer Key

Expected answers for [questions.md](questions.md). Don't give this file to an agent under test.

Facts come from Using CQL With FHIR 2.0.0, as rendered in the `cql-ig` skill: the pages in
`resources/pages/`, the libraries in `resources/libraries/`, the ModelInfo in
`resources/modelinfo/`, and the operation definitions in the knowledge base
(`resources/profiles/concise/`, built by `scripts/build-kb.sh`). Translator behaviour was checked
with the CQL-to-ELM translator 3.29.0. Each answer gives the expected facts, the source, what a
passing answer must and must not say, and where the skill covers it ("Skill").

## Lookups

### LK-01. FHIRHelpers and FHIRCommon

- **Expected:** FHIRHelpers is `http://hl7.org/fhir/uv/cql/Library/FHIRHelpers`, version 4.0.1.
  FHIRCommon is `http://hl7.org/fhir/uv/cql/Library/FHIRCommon`, version 2.0.0, and it includes
  FHIRHelpers 4.0.1. FHIRHelpers is versioned with the FHIR version it supports, because it is tied
  to the FHIR ModelInfo (also 4.0.1). FHIRCommon has the IG's version.
- **Source:** `libraries/README.md`; `pages/patterns.md` (Primitives).
- **Pass if:** both URLs and versions are right, and it explains that FHIRHelpers tracks FHIR.
- **Fail if:** it gives `fhir.cqf.common` or `http://fhir.org/guides/cqf/common` URLs as current,
  or gives FHIRHelpers version 2.0.0.
- **Skill:** `SKILL.md` Packaging CQL in a FHIR Library (Dependencies).

### LK-02. Primary code paths

- **Expected:** MedicationRequest: `medication`. DeviceUseStatement: `device.code`. AuditEvent has
  no primary code path, so the translator warns that the retrieve "does not have a primary code
  path defined". The ELM retrieve has the value set but no `codeProperty`, so the filter element is
  undefined. Write `[AuditEvent: type in "Some Value Set"]` instead.
- **Source:** `modelinfo/README.md` (Resources); translator 3.29.0.
- **Pass if:** both paths are right, and it says AuditEvent needs an explicit code path.
- **Fail if:** it says MedicationRequest filters on `code`, or that the AuditEvent retrieve
  filters on some element by default.
- **Skill:** `SKILL.md` FHIR in CQL (Retrieves).

### LK-03. A choice element

- **Expected:** `Choice<FHIR.dateTime, FHIR.Period, FHIR.Timing, FHIR.instant>`. Normalize it to
  an interval before comparing, either with FHIRCommon's fluent `toInterval()`
  (`O.effective.toInterval() during "Measurement Period"`) or by testing each type with `is` and
  `as`, as in the Patterns page.
- **Source:** `modelinfo/resources/Observation.md`; `pages/patterns.md` (Choices);
  `libraries/FHIRCommon.cql` (`toInterval`).
- **Pass if:** the four types are listed and the comparison handles more than one of them.
- **Fail if:** it treats `effective` as always a `dateTime`, or writes `effective[x]` or
  `effectiveDateTime` in CQL.
- **Skill:** `SKILL.md` FHIR in CQL (Choices); `modelinfo/`.

## Conformance

### CF-01. Library names

- **Expected:** No. The library identifier SHALL contain only alphanumeric characters and SHALL
  NOT contain underscores (2.1). A version belongs in the `version` clause, not the name (2.2).
  For example, `library DiabetesScreening version '2.0.0'`.
- **Source:** `pages/using-cql.md`, Conformance Requirements 2.1 and 2.2.
- **Pass if:** it rejects the underscores, citing 2.1, and moves the version out of the name.
- **Fail if:** it accepts the name because CQL itself allows underscores.
- **Skill:** `SKILL.md` Writing CQL against FHIR (Library name).

### CF-02. Library resource identity

- **Expected:** `url` `http://example.org/fhir/Library/Common`, `name` `Common`, `version`
  `2.0.0` (4.2). The namespace root matches the Library URL root (2.4).
- **Source:** `pages/conformance.md` 4.2; `pages/using-cql.md` 2.4.
- **Pass if:** all three are right.
- **Skill:** `SKILL.md` Packaging CQL in a FHIR Library (Identity).

### CF-03. Includes

- **Expected:** No. Every included library SHALL have a `called` clause (2.3), so it should be
  `include FHIRHelpers version '4.0.1' called FHIRHelpers`. Without FHIRHelpers, the implicit
  conversions in the ModelInfo can't be resolved, and translation fails with "Could not resolve
  library name FHIRHelpers".
- **Source:** `pages/using-cql.md` 2.3; `pages/patterns.md` (Primitives); translator 3.29.0.
- **Pass if:** it requires `called`, citing 2.3, and says translation fails without FHIRHelpers.
- **Fail if:** it calls the include fine because the IG's own examples omit `called`.
- **Skill:** `SKILL.md` Writing CQL against FHIR (Includes).

### CF-04. Type mapping

- **Expected:** `System.Long` maps to `string` in R4 (`integer64` in R5 and later).
  `Interval<System.DateTime>` maps to `Period`, and `Interval<System.Quantity>` to `Range`.
- **Source:** `pages/conformance.md` 4.3.
- **Pass if:** all three are right.
- **Fail if:** it maps `Long` to `integer` or `integer64` for R4.
- **Skill:** `SKILL.md` Results and operations (Type mapping).

### CF-05. Translator options

- **Expected:** SHOULD use EnableAnnotations, EnableLocators, DisableListDemotion and
  DisableListPromotion, with a SignatureLevel of `Overloads` or `All`. MAY use
  EnableDateRangeOptimization and EnableResultTypes. SHOULD NOT use DisableMethodInvocation,
  EnableDetailedErrors or DisableListTraversal.
- **Source:** `pages/using-elm.md` 5.2.
- **Pass if:** it gives the SHOULD set and names DisableMethodInvocation as not to be used.
- **Partial if:** it misses the SignatureLevel, or one of the SHOULD NOT options other than
  DisableMethodInvocation.
- **Skill:** `SKILL.md` Packaging CQL in a FHIR Library (Translator options).

## Patterns

### PT-01. A missing boolean

- **Expected:** If `doNotPerform` is absent, the comparison is `null`, and `null` in a `where`
  clause acts as false, so requests without the element are dropped. Write
  `where MR.doNotPerform is not true`.
- **Source:** `pages/patterns.md` (Missing Information).
- **Pass if:** it explains the null and gives `is not true` or an equivalent that keeps absent
  values.
- **Skill:** `SKILL.md` FHIR in CQL (Missing data).

### PT-02. Active conditions

- **Expected:** `clinicalStatus` is equivalent (`~`) to `active`, `recurrence` or `relapse` from
  `http://terminology.hl7.org/CodeSystem/condition-clinical`. It does not look at
  `verificationStatus`. That is what `isVerified()` and `isConfirmed()` do.
- **Source:** `libraries/FHIRCommon.cql` (`isActive`).
- **Pass if:** all three codes, and it says verification status isn't checked.
- **Fail if:** it says `isActive()` only checks for `active`, or that it also excludes refuted
  conditions.
- **Skill:** `SKILL.md` FHIR in CQL (FHIRCommon).

## Operations

### OP-01. Evaluating results

- **Expected:** The list of three Observations is three parameters with the same name, each with
  a `resource`. The empty list is a single parameter with `_valueBoolean` carrying the
  `cqf-isEmptyList` extension set to true. `$cql` is a system-level operation that evaluates one
  CQL expression (`expression`, 1..1, not a library) and returns the result in `return`.
  `Library/$evaluate` runs at the type level (with `url` or `library`) or the instance level,
  evaluates the named expressions or all public ones (adding private ones with
  `includePrivate`), and returns a Parameters resource in `return`.
- **Source:** `pages/conformance.md` (FHIR Type Mapping); `OperationDefinition-cql-cql.md` and
  `OperationDefinition-cql-library-evaluate.md` in the knowledge base.
- **Pass if:** both representations are right and the operation differences are stated.
- **Fail if:** it represents the list as one parameter holding a Bundle, or the empty list by
  omitting the parameter.
- **Skill:** `SKILL.md` Results and operations.

## Tasks

### TK-01. Packaging a library

Grade the saved Library with [grade_library.py](grade_library.py)
(`python grade_library.py library.json`), then read it. [reference/](reference/) has a passing
answer.

- **Script checks** (each must pass):
  - `url` `http://example.org/fhir/Library/DiabetesScreening`, `name` `DiabetesScreening`,
    `version` `1.0.0`.
  - A `status`, and `type` `logic-library`.
  - Exactly one content item with a `text/cql` type, whose `data` is the base64 of the CQL.
  - `depends-on` related artifacts for the FHIR ModelInfo 4.0.1, FHIRHelpers 4.0.1, LOINC and the
    Diabetes value set. The `http://hl7.org/fhir/uv/cql/Library/` and older
    `http://hl7.org/fhir/Library/` forms are both accepted for the libraries.
  - An input parameter `Measurement Period` of type `Period`. Outputs `Has Diabetes`
    (`boolean`, max 1) and `HbA1c Results` (`Observation`, max `*`). No other outputs except an
    optional `Patient`.
  - Data requirements for Condition (code filtered by the value set) and Observation (code
    filtered by LOINC 4548-4).
- **Better answers also** claim the CQLLibrary profile, give the CQL version
  (`text/cql; version=1.5`), and carry `cqf-cqlType` on the parameters.
- **Fail if:** the script fails.
- **Skill:** `SKILL.md` Packaging CQL in a FHIR Library.
