# Sources

Registry of every source the skill's resource files cite. Cite a claim inline as
`[src: ID locator]`:

- a specification page, with its section number or anchor: `[src: SDC-4.0.0 populate.html#exp-pop]`;
- a file in a FHIR package: `[src: FHIR-R4 package/StructureDefinition-Questionnaire.json]`;
- clinical-reasoning code, by path and lines at the pinned commit:
  `[src: CR-4.13.0 cqf-fhir-cr/…/populate/ItemProcessor.java:201-211]` (a `…` elides the middle of a path;
  full paths are listed below);
- the probe runs: `[src: PROBES-2026-11-14 RESULTS.md §1]`.

| ID | Kind | Status | Version | Pinned locator | Published URL | Local copy | Retrieved |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FHIR-R4 | spec | trial-use | FHIR R4 4.0.1 (Questionnaire and QuestionnaireResponse are trial-use) | hl7.fhir.r4.core#4.0.1 | <https://hl7.org/fhir/R4/> | none | 2026-11-14 |
| FHIR-R5 | spec | trial-use | FHIR R5 5.0.0, for what changed in Questionnaire | hl7.fhir.r5.core#5.0.0 | <https://hl7.org/fhir/R5/> | none | 2026-11-14 |
| SDC-4.0.0 | spec | trial-use | Structured Data Capture 4.0.0 (STU4), for FHIR R4 | hl7.fhir.uv.sdc#4.0.0 | <https://hl7.org/fhir/uv/sdc/STU4/> | none | 2026-11-14 |
| SDC-3.0.0 | spec | trial-use | Structured Data Capture 3.0.0 (STU3), for what changed in 4.0.0 | hl7.fhir.uv.sdc#3.0.0 | <https://hl7.org/fhir/uv/sdc/STU3/> | none | 2026-11-14 |
| EXT-5.3.0 | spec | trial-use | FHIR Extensions Pack for R4, 5.3.0-ballot-tc1, the version SDC 4.0.0 depends on | hl7.fhir.uv.extensions.r4#5.3.0-ballot-tc1 | <https://hl7.org/fhir/extensions/> | none | 2026-11-14 |
| CR-4.13.0 | implementation-source | n/a | clinical-reasoning (cqf-fhir-cr) 4.13.0, released 2026-10-01, the version cql-language-server 5.0.0 uses | cqframework/clinical-reasoning@ccba474a2fba73329353b41d270f9d0001d6cb52 | <https://github.com/cqframework/clinical-reasoning/tree/v4.13.0> | none (the fetch script caches a clone) | 2026-11-14 |
| PROBES-2026-11-14 | observed-behavior | n/a | clinical-reasoning 4.13.0 (CQL translator and engine 5.4.0), run with `scripts/sdc/` | `resources/probes/2026-11-14/` | none | `resources/probes/2026-11-14/` | 2026-11-14 |

## Reading a citation

| Source | URL |
| --- | --- |
| FHIR-R4, FHIR-R5 | `https://hl7.org/fhir/<R4|R5>/<page>`; package files at `https://packages.fhir.org/hl7.fhir.<r4|r5>.core/<version>` |
| SDC-4.0.0, SDC-3.0.0 | `https://hl7.org/fhir/uv/sdc/<STU4|STU3>/<page>` (for STU4, the pages are under `en/`: `https://hl7.org/fhir/uv/sdc/STU4/en/<page>`); package at `https://packages.fhir.org/hl7.fhir.uv.sdc/<version>` |
| EXT-5.3.0 | package at `https://packages.fhir.org/hl7.fhir.uv.extensions.r4/5.3.0-ballot-tc1` |
| CR-4.13.0 | `https://github.com/cqframework/clinical-reasoning/blob/v<version>/<path>#L<a>-L<b>` |

For another clinical-reasoning release, read the same file at its tag and find the code by its content
near the cited lines. The release a HAPI FHIR server uses is in its dependencies (`cqf-fhir-cr`).

**Cited files.** The full paths behind each `…`:

| Source | Path |
| --- | --- |
| CR | `cqf-fhir-cr-hapi/src/main/java/org/opencds/cqf/fhir/cr/hapi/r4/questionnaire/QuestionnairePopulateProvider.java` |
| CR | `cqf-fhir-cr-hapi/src/main/java/org/opencds/cqf/fhir/cr/hapi/r4/questionnaireresponse/QuestionnaireResponseExtractProvider.java` |
| CR | `cqf-fhir-cr-hapi/src/main/java/org/opencds/cqf/fhir/cr/hapi/r4/structuredefinition/StructureDefinitionQuestionnaireProvider.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/common/ExpressionProcessor.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/common/InputParameterResolver.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/common/ItemValueTransformer.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/questionnaire/populate/ItemProcessor.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/questionnaire/populate/PopulateProcessor.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/questionnaire/populate/PopulateRequest.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/questionnaireresponse/QuestionnaireResponseProcessor.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/questionnaireresponse/extract/ExtractProcessor.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/questionnaireresponse/extract/ExtractRequest.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/questionnaireresponse/extract/ObservationResolver.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/questionnaireresponse/extract/ProcessDefinitionItem.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/questionnaireresponse/extract/ProcessItem.java` |
| CR | `cqf-fhir-cql/src/main/java/org/opencds/cqf/fhir/cql/LibraryConstructor.kt` |
| CR | `cqf-fhir-utility/src/main/java/org/opencds/cqf/fhir/utility/Constants.kt` |
| CR | `cqf-fhir-utility/src/main/java/org/opencds/cqf/fhir/utility/CqfExpression.kt` |
| CR | `cqf-fhir-utility/src/main/java/org/opencds/cqf/fhir/utility/adapter/IKnowledgeArtifactAdapter.java` |
