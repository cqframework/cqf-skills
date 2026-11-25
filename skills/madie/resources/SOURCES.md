# Sources

Registry of every source the skill's resource files cite. Cite a claim inline as
`[src: ID path:line[-line]]`, with the path relative to the repository root at the pinned commit, or
`[src: ID file]` for a file in a FHIR package. A `…` elides the middle of a path; the rest must match one
file (full paths are listed below).

MADiE has no releases: each repository is developed on its `develop` branch and deployed from there in
sprints. The MADiE sources are pinned to `develop` commits of 2026-11-14. Production may be a sprint
behind them.

| ID | Kind | Status | Version | Pinned locator | Published URL | Local copy | Retrieved |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MEASURE-18c8d4d | implementation-source | n/a | madie-measure (measure and test case screens) `develop`, 2026-11-12 | MeasureAuthoringTool/madie-measure@18c8d4db1cfe94730474daa425b11cd551cfecd9 | <https://github.com/MeasureAuthoringTool/madie-measure/tree/18c8d4db1cfe94730474daa425b11cd551cfecd9> | none (the fetch script caches a clone) | 2026-11-14 |
| MSVC-251a73d | implementation-source | n/a | measure-service (measures, test cases, import) `develop`, 2026-11-10 | MeasureAuthoringTool/measure-service@251a73d9197a48dc1608acb418d4419cf9e548ac | <https://github.com/MeasureAuthoringTool/measure-service/tree/251a73d9197a48dc1608acb418d4419cf9e548ac> | none (the fetch script caches a clone) | 2026-11-14 |
| FHIRSVC-51b9b37 | implementation-source | n/a | madie-fhir-service (validation, test case export) `develop`, 2026-11-13 | MeasureAuthoringTool/madie-fhir-service@51b9b37ab5543ace25f0aae10211da966f18c456 | <https://github.com/MeasureAuthoringTool/madie-fhir-service/tree/51b9b37ab5543ace25f0aae10211da966f18c456> | none (the fetch script caches a clone) | 2026-11-14 |
| PKGUTIL-dd71537 | implementation-source | n/a | packaging-utility (export zips) `develop`, 2026-11-12 | MeasureAuthoringTool/packaging-utility@dd71537d6eea7253fcd77444f86f2eec4970ebd1 | <https://github.com/MeasureAuthoringTool/packaging-utility/tree/dd71537d6eea7253fcd77444f86f2eec4970ebd1> | none (the fetch script caches a clone) | 2026-11-14 |
| JMODELS-49ffdec | implementation-source | n/a | madie-java-models (server data model) `develop`, 2026-11-12 | MeasureAuthoringTool/madie-java-models@49ffdec50b29635bbe2e88a6a4fbbdd3c75f4af2 | <https://github.com/MeasureAuthoringTool/madie-java-models/tree/49ffdec50b29635bbe2e88a6a4fbbdd3c75f4af2> | none (the fetch script caches a clone) | 2026-11-14 |
| TSMODELS-960ea63 | implementation-source | n/a | madie-models (browser data model) `main`, 2026-10-29, the branch it's published from | MeasureAuthoringTool/madie-models@960ea6339f0e00178d32c14684fa9e65bd26f589 | <https://github.com/MeasureAuthoringTool/madie-models/tree/960ea6339f0e00178d32c14684fa9e65bd26f589> | none (the fetch script caches a clone) | 2026-11-14 |
| EDITOR-e2635c7 | implementation-source | n/a | madie-editor (CQL editor) `develop`, 2026-11-12 | MeasureAuthoringTool/madie-editor@e2635c76318164a282fcad7e8c204b4bbc7a822d | <https://github.com/MeasureAuthoringTool/madie-editor/tree/e2635c76318164a282fcad7e8c204b4bbc7a822d> | none (the fetch script caches a clone) | 2026-11-14 |
| DQMCMS-757d7c6 | observed-behavior | n/a | The CMS 2026 dQM content repository's CQL skill, recording what its authors observed testing shared libraries in MADiE (engine differences, code systems MADiE lacks, the Cohort-measure test pattern) | cqframework/dqm-content-cms-2026@757d7c6fd01998287d622d03fb02e133c700e22a | <https://github.com/cqframework/dqm-content-cms-2026/blob/757d7c6fd01998287d622d03fb02e133c700e22a/.claude/skills/cql/SKILL.md> | none (the fetch script caches a clone) | 2026-11-14 |
| VSCQL-855eac7 | implementation-source | n/a | vscode-cql 1.0.0, the VS Code CQL extension (tag `v1.0.0`) | cqframework/vscode-cql@855eac7b5f21c788d0e0e856d741cadc35e6bda9 | <https://github.com/cqframework/vscode-cql/tree/v1.0.0> | none (the fetch script caches a clone) | 2026-11-14 |
| CQLLS-68e601f | implementation-source | n/a | cql-language-server 5.0.0, the server vscode-cql 1.0.0 runs (tag `v5.0.0`) | cqframework/cql-language-server@68e601fa6b8ef7df99f8ef29b86d4464d94bd400 | <https://github.com/cqframework/cql-language-server/tree/v5.0.0> | none (the fetch script caches a clone) | 2026-11-14 |
| FQM-8f1038a | implementation-source | n/a | fqm-execution 1.8.6, the engine MADiE runs test cases with (tag `v1.8.6`) | projecttacoma/fqm-execution@8f1038add3658f720b1b851100b50454e40a431d | <https://github.com/projecttacoma/fqm-execution/tree/v1.8.6> | none (the fetch script caches a clone) | 2026-11-14 |
| CQLMCP-a2895f0 | implementation-source | n/a | cql-mcp 0.1.0-rc.2, the CQL MCP server, for its test-run records (tag `v0.1.0-rc.2`) | cqframework/cql-mcp@a2895f0ca2632845b305e70e274bce7c447cfbcf | <https://github.com/cqframework/cql-mcp/tree/v0.1.0-rc.2> | none (the fetch script caches a clone) | 2026-11-25 |
| CQLTESTS-5747d2b | test-suite | informative | cqframework/cql-tests, the CQL conformance tests, `main` | cqframework/cql-tests@5747d2b72f29d733fbc114383c4a15a30999ffaf | <https://github.com/cqframework/cql-tests> | none (the fetch script caches a clone) | 2026-11-14 |
| USQC-0.5.0 | package | trial-use | fhir.onc.us-quality-core 0.5.0 (US Quality Core) | fhir.onc.us-quality-core#0.5.0 | <https://fhir.org/guides/onc/us-quality-core/0.5.0/> | none | 2026-11-14 |
| CQLIG-2.0.0 | package | trial-use | hl7.fhir.uv.cql 2.0.0 (Using CQL With FHIR), for the FHIRCommon 2.0.0 library | hl7.fhir.uv.cql#2.0.0 | <https://hl7.org/fhir/uv/cql/STU2/> | none | 2026-11-14 |
| CQM-2.0.0 | package | trial-use | hl7.fhir.uv.cqm 2.0.0 (Quality Measures IG), for the `cqm-testcase` profile | hl7.fhir.uv.cqm#2.0.0 | <https://hl7.org/fhir/uv/cqm/STU2/> | none | 2026-11-14 |

## Looking up a citation

No local copy is needed to check a claim. Read a citation at its pinned commit, or at the current
`develop`, on GitHub:

| Source | URL |
| --- | --- |
| MADiE repositories | `https://github.com/MeasureAuthoringTool/<repo>/blob/<commit or develop>/<path>#L<a>-L<b>` (`main` for madie-models, which has no `develop`) |
| DQMCMS | `https://github.com/cqframework/dqm-content-cms-2026/blob/<commit or main>/<path>#L<a>-L<b>` |
| VSCQL, CQLLS, FQM, CQLMCP | `https://github.com/<repo>/blob/v<version>/<path>#L<a>-L<b>` (tags are `v` plus the version) |
| CQLTESTS | `https://github.com/cqframework/cql-tests/blob/<commit or main>/<path>#L<a>-L<b>` |
| Packages | `https://packages.fhir.org/<package>/<version>` (a tgz), or the published IG's page for the profile |

Line numbers move between commits, so at `develop` find the cited code by its content near the cited
lines.

**Cited files.** The full paths behind each `…`:

| Source | Path |
| --- | --- |
| MEASURE | `src/components/editMeasure/editor/MeasureEditor.tsx` |
| MEASURE | `src/components/editMeasure/testCases/api/CalculationService.ts` |
| MEASURE | `src/components/editMeasure/testCases/api/fhirDefinitionServiceUtilities.tsx` |
| MEASURE | `src/components/editMeasure/testCases/components/createTestCase/TestCaseSeries.tsx` |
| MEASURE | `src/components/editMeasure/testCases/components/editTestCase/qiCore/EditTestCase.tsx` |
| MEASURE | `src/components/editMeasure/testCases/components/testCaseLanding/common/ActionCenter/ActionCenter.tsx` |
| MEASURE | `src/components/editMeasure/testCases/components/testCaseLanding/common/import/TestCaseImportDialog.tsx` |
| MEASURE | `src/components/editMeasure/testCases/components/testCaseLanding/qiCore/TestCaseList.tsx` |
| MEASURE | `src/components/editMeasure/testCases/util/QiCoreTestCaseHelper.ts` |
| MEASURE | `src/components/editMeasure/testCases/util/checkSpecialCharacters.ts` |
| MSVC | `src/main/java/cms/gov/madie/measure/resources/ExportController.java` |
| MSVC | `src/main/java/cms/gov/madie/measure/resources/TestCaseController.java` |
| MSVC | `src/main/java/cms/gov/madie/measure/services/CqlTemplateConfigService.java` |
| MSVC | `src/main/java/cms/gov/madie/measure/services/MeasureService.java` |
| MSVC | `src/main/java/cms/gov/madie/measure/services/TerminologyValidationService.java` |
| MSVC | `src/main/java/cms/gov/madie/measure/services/TestCaseService.java` |
| MSVC | `src/main/java/cms/gov/madie/measure/services/VersionService.java` |
| MSVC | `src/main/java/cms/gov/madie/measure/utils/JsonUtil.java` |
| MSVC | `src/main/java/cms/gov/madie/measure/utils/MeasureUtil.java` |
| MSVC | `src/main/java/cms/gov/madie/measure/utils/TestCaseServiceUtil.java` |
| FHIRSVC | `src/main/java/gov/cms/madie/madiefhirservice/config/HapiFhirConfig.java` |
| FHIRSVC | `src/main/java/gov/cms/madie/madiefhirservice/constants/UriConstants.java` |
| FHIRSVC | `src/main/java/gov/cms/madie/madiefhirservice/resources/TestCaseBundleController.java` |
| FHIRSVC | `src/main/java/gov/cms/madie/madiefhirservice/services/ResourceValidationService.java` |
| FHIRSVC | `src/main/java/gov/cms/madie/madiefhirservice/services/TestCaseBundleService.java` |
| FHIRSVC | `src/main/java/gov/cms/madie/madiefhirservice/utils/ExportFileNamesUtil.java` |
| FHIRSVC | `src/main/java/gov/cms/madie/madiefhirservice/utils/FhirResourceHelpers.java` |
| PKGUTIL | `src/main/java/gov/cms/madie/packaging/utils/PackagingUtilityFactory.java` |
| PKGUTIL | `src/main/java/gov/cms/madie/packaging/utils/qicore411/PackagingUtilityImpl.java` |
| PKGUTIL | `src/main/java/gov/cms/madie/packaging/utils/usqualitycore/PackagingUtilityImpl.java` |
| CQLLS | `ls/server/src/main/kotlin/org/opencds/cqf/cql/ls/server/command/CqlEvaluator.kt` |
| CQLLS | `ls/server/src/main/kotlin/org/opencds/cqf/cql/ls/server/repository/ig/standard/IgStandardRepository.kt` |
| JMODELS | `src/main/java/gov/cms/madie/models/common/ModelType.java` |
| JMODELS | `src/main/java/gov/cms/madie/models/common/Version.java` |
| JMODELS | `src/main/java/gov/cms/madie/models/dto/TestCaseExportMetaData.java` |
| JMODELS | `src/main/java/gov/cms/madie/models/measure/Measure.java` |
| JMODELS | `src/main/java/gov/cms/madie/models/measure/PopulationType.java` |
| JMODELS | `src/main/java/gov/cms/madie/models/measure/TestCase.java` |
| JMODELS | `src/main/java/gov/cms/madie/models/validators/ValidLibraryNameValidator.java` |
