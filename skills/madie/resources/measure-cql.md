# Measure CQL in MADiE

Baseline: MADiE `develop` as of 2026-11-14 (commits in SOURCES.md), for QI-Core measures. Untagged statements hold at these commits only.
Sources: MSVC-251a73d, MEASURE-18c8d4d, EDITOR-e2635c7, JMODELS-49ffdec, DQMCMS-757d7c6

What MADiE checks and changes in a measure's CQL. How to write the CQL itself (style, patterns, the
CQMCommon libraries) is in the `cms-qmd` skill, and the language in the `cql` skill.

## Names and versions

- **Library name:** an upper-case letter, then letters and digits only, for FHIR-based models
  [src: JMODELS-49ffdec src/…/validators/ValidLibraryNameValidator.java:36-48], at most 64 characters
  [src: MSVC-251a73d src/…/utils/MeasureUtil.java:59-63]. No underscores, dots or hyphens.
- **Version:** MADiE versions are `major.minor.revision`, always written with a three-digit revision:
  `0.0.000`, `1.2.000` [src: JMODELS-49ffdec src/…/models/common/Version.java:35-42]. A new measure is
  `0.0.000` [src: MSVC-251a73d src/…/services/MeasureService.java:154].

## What MADiE rewrites when CQL is saved

The editor corrects these on save and tells the user
[src: EDITOR-e2635c7 src/madieCqlEditor/MadieCqlEditor.tsx:162-202]
[src: MEASURE-18c8d4d src/…/editor/MeasureEditor.tsx:519-531]:

| What | Becomes | Message |
| --- | --- | --- |
| A `library` line whose name or version differs from the measure's | `library <measure's CQL library name> version '<measure version>'` | "Library statement was incorrect. MADiE has overwritten it." |
| `include FHIRHelpers … called <anything else>` | `called FHIRHelpers` | "FHIRHelpers was incorrectly aliased…" |
| `valueset "X": '…' version '…'` | the same without `version` | "MADiE does not currently support use of value set version directly in CQL…" |

So the `library` line in a measure always matches the measure in MADiE; there's no need to edit it by
hand. When a measure is versioned, MADiE rewrites the version in the `library` line
[src: MSVC-251a73d src/…/services/VersionService.java:199-210].

## What MADiE rejects

- **The `using` statement** must match the measure's model: a QI-Core measure can't use `QDM`, and a
  QDM measure must use `QDM '5.6'`. "Missing a using statement" is an error too
  [src: MEASURE-18c8d4d src/…/editor/MeasureEditor.tsx:284-302]
  [src: MEASURE-18c8d4d src/…/editor/MeasureEditor.tsx:516].
- **Value set URLs.** In a QI-Core measure, a value set must be a VSAC FHIR URL,
  `http://cts.nlm.nih.gov/fhir/ValueSet/<OID>` [src: EDITOR-e2635c7 src/validations/valuesetValidation.ts:53-66].
  The server checks value sets against VSAC with the same prefix
  [src: MSVC-251a73d src/…/services/TerminologyValidationService.java:94-103]. `urn:oid:` value sets,
  used in the CQL specification's examples, aren't accepted.
- **Codes.** Each `code` declaration is checked against MADiE's terminology service, and one invalid
  code fails the check [src: MSVC-251a73d src/…/services/TerminologyValidationService.java:47-59]. A
  code from a code system MADiE doesn't have fails, even when the CQL compiles and runs locally. Code
  systems found missing in practice: HL7 v2-0074 (diagnostic service section) and the US Core care plan
  category [src: DQMCMS-757d7c6 .claude/skills/cql/SKILL.md:238-252]. Before declaring codes from a less
  common code system, check that MADiE accepts it; until it does, comment the `codesystem` and `code`
  declarations out, with the logic that uses them.

## The default CQL

A new measure created with default CQL starts from a template for its model
[src: MSVC-251a73d src/…/services/MeasureService.java:167-207]. For QI-Core 6.0.0
[src: MSVC-251a73d src/test/resources/QICore600_CQLTemplate.txt:1-24], shown here with the measure's
library name filled in:

```cql
library ExampleFollowUp version '0.0.000'

using QICore version '6.0.0'

include CQMCommon version '4.1.000' called CQMCommon
include FHIRHelpers version '4.4.000' called FHIRHelpers
include QICoreCommon version '4.0.000' called QICoreCommon
include SupplementalDataElements version '5.1.000' called SDE

parameter "Measurement Period" Interval<DateTime>

context Patient

define "SDE Ethnicity":
  SDE."SDE Ethnicity"

define "SDE Payer":
  SDE."SDE Payer"

define "SDE Race":
  SDE."SDE Race"

define "SDE Sex":
  SDE."SDE Sex"
```

The QI-Core 4.1.1 template is the same with `using QICore version '4.1.1'`, CQMCommon `2.0.000`,
FHIRHelpers `4.3.000`, QICoreCommon `2.0.000` and SupplementalDataElements `3.4.000`
[src: MSVC-251a73d src/test/resources/QICore411_CQLTemplate.txt:1-8].

These are the copies kept in measure-service's tests; the live templates are loaded from configuration
[src: MSVC-251a73d src/…/services/CqlTemplateConfigService.java:34-41], so the library versions in
production may be newer. Check the versions MADiE offers before pinning includes in a new measure.

## Populations

The population definitions MADiE can map to a measure group are the `PopulationType` values: Initial
Population, Numerator, Numerator Exclusion, Denominator, Denominator Exclusion, Denominator Exception,
Measure Population, Measure Population Exclusion and Measure Observation
[src: JMODELS-49ffdec src/…/models/measure/PopulationType.java:8-32]. Each is mapped to a CQL definition
by name in the measure's population criteria, so the definition names are the author's choice; the
usual names are the population names in double quotes, such as `define "Initial Population":`.

## Testing a shared library in MADiE

MADiE has no place for a library without a measure, but a shared library (such as a set of common
functions) can be tested there with a Cohort measure
[src: DQMCMS-757d7c6 .claude/skills/cql/SKILL.md:74-83] [src: DQMCMS-757d7c6 .claude/skills/cql/SKILL.md:102-127]:

1. Write a test library that includes the library under test and has one Boolean `define Test…:` per
   test, each `true` when it passes, on every case. For a case-specific test, use
   `case "Case" when '<label>' then <assertion> … else true end`, with the label read from the Patient's
   given name. Never `else null`: a null from a broken assertion would then look like "not applicable".
2. Combine them: `define _Passed: TestA and TestB and …`. Use `and`, not `AllTrue({ … })`, because
   `AllTrue` ignores nulls, so a test that came back null would pass.
3. Make the test library a Cohort measure in MADiE, with `_Passed` as the Initial Population (a
   boolean population basis).
4. Give every test case a MeasureReport expecting Initial Population 1 (`Group_1`,
   `InitialPopulation_1`, `count: 1`). A case then passes in MADiE exactly when every test is true for
   it.

A measure itself needs no test library: its test cases carry the expected count of each population.
