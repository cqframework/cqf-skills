# Measure CQL in MADiE

Baseline: MADiE `develop` as of 2026-11-14 (commits in SOURCES.md), for US Quality Core 0.5.0 measures. Untagged statements hold at these commits only.
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

- **A missing `using` statement** is an error, and a FHIR-based measure can't use `QDM`
  [src: MEASURE-18c8d4d src/…/editor/MeasureEditor.tsx:284-302]
  [src: MEASURE-18c8d4d src/…/editor/MeasureEditor.tsx:516]. Nothing else checks that a US Quality Core
  measure's `using` names US Quality Core: keep the three `using` lines of the template (below).
- **Value set URLs.** Write value sets as VSAC FHIR URLs, `http://cts.nlm.nih.gov/fhir/ValueSet/<OID>`.
  The editor looks every value set up in VSAC by the OID it takes from the URL
  [src: EDITOR-e2635c7 src/validations/valuesetValidation.ts:7-51]; its explicit check of the URL form
  runs only for libraries whose first `using` is `QICore`
  [src: EDITOR-e2635c7 src/validations/valuesetValidation.ts:53-66], and the server's check of the prefix
  [src: MSVC-251a73d src/…/services/TerminologyValidationService.java:94-103] runs when a measure is
  created [src: MSVC-251a73d src/…/services/MeasureService.java:139-143]. `urn:oid:` value sets, used in
  the CQL specification's examples, won't resolve.
- **Codes.** Each `code` declaration is checked against MADiE's terminology service, and one invalid
  code fails the check [src: MSVC-251a73d src/…/services/TerminologyValidationService.java:47-59]. A
  code from a code system MADiE doesn't have fails, even when the CQL compiles and runs locally. Code
  systems found missing in practice: HL7 v2-0074 (diagnostic service section) and the US Core care plan
  category [src: DQMCMS-757d7c6 .claude/skills/cql/SKILL.md:238-252]. Before declaring codes from a less
  common code system, check that MADiE accepts it; until it does, comment the `codesystem` and `code`
  declarations out, with the logic that uses them.

## The default CQL

A new measure created with default CQL starts from a template for its model
[src: MSVC-251a73d src/…/services/MeasureService.java:167-207]. For US Quality Core 0.5.0
[src: MSVC-251a73d src/test/resources/USQC050_CQLTemplate.txt:1-12], shown here with the measure's library
name filled in:

```cql
library ExampleFollowUp version '0.0.000'

using USQualityCore version '0.5.0'
using USCore version '6.1.0-derived'
using FHIR version '4.0.1'

include hl7.fhir.uv.cql.FHIRHelpers version '4.0.1' called FHIRHelpers
include hl7.fhir.uv.cql.FHIRCommon version '2.0.0' called FHIRCommon

parameter "Measurement Period" Interval<DateTime>

context Patient
```

Unlike the QI-Core templates, it has no supplemental data element definitions or CQMCommon include; add
the CMS libraries the measure uses (see the `cms-qmd` skill). This is the copy kept in measure-service's
tests; the live templates are loaded from configuration
[src: MSVC-251a73d src/…/services/CqlTemplateConfigService.java:34-41], so production may differ.

## Drafting a QI-Core measure as US Quality Core

A QI-Core 6.0.0 measure can be drafted as a US Quality Core 0.5.0 measure, and a US Quality Core
measure only as US Quality Core [src: MEASURE-18c8d4d src/components/common/draftMeasureDialog/DraftMeasureDialog.tsx:150-162].
When the model changes, MADiE rewrites `using QICore version '…'` to
`using USQualityCore version '0.5.0'` and adds `using USCore version '6.1.0-derived'` and
`using FHIR version '4.0.1'` if they're missing
[src: MSVC-251a73d src/…/services/VersionService.java:294-298]
[src: MSVC-251a73d src/…/services/VersionService.java:360-398]. It changes nothing else: `include`s of
QI-Core libraries (QICoreCommon, the QI-Core CQMCommon and FHIRHelpers), type names qualified with
`QICore.`, and the profiles in the test cases all have to be converted by hand.

## No return-type check

For QI-Core measures MADiE checks that each population definition's result type fits the group's
population basis; it doesn't for US Quality Core measures
[src: MSVC-251a73d src/…/utils/MeasureUtil.java:65-72]. A definition returning a list of encounters
mapped to a boolean-basis group (or the reverse) isn't flagged, so check the population basis yourself.

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
   it. `scripts/new_test_case.py` without `--populations` writes this MeasureReport with the case's
   Patient. Locally, check each test rather than just `_Passed` with the `cql` skill's
   `check_test_library.py`.

A measure itself needs no test library: its test cases carry the expected count of each population.
