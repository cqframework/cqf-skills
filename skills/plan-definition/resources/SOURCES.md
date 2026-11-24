# Sources

Registry of every source the skill's resource files cite. Cite a claim inline as
`[src: ID locator]`:

- a specification page, with its section number or anchor: `[src: FHIR-R4 plandefinition.html#12.18.3.3]`;
- a file in a FHIR package: `[src: FHIR-R4 package/StructureDefinition-PlanDefinition.json]`;
- clinical-reasoning code, by path and lines at the pinned commit:
  `[src: CR-4.16.0 cqf-fhir-cr/…/apply/ProcessAction.java:62-81]` (a `…` elides the middle of a path; full
  paths are listed below);
- the probe runs: `[src: PROBES-2026-11-14 RESULTS.md §1]`.

| ID | Kind | Status | Version | Pinned locator | Published URL | Local copy | Retrieved |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FHIR-R4 | spec | trial-use | FHIR R4 4.0.1 (PlanDefinition and ActivityDefinition are trial-use) | hl7.fhir.r4.core#4.0.1 | <https://hl7.org/fhir/R4/> | none | 2026-11-14 |
| FHIR-R4B | spec | trial-use | FHIR R4B 4.3.0, for the expression language codes | hl7.fhir.r4b.core#4.3.0 | <https://hl7.org/fhir/R4B/> | none | 2026-11-14 |
| FHIR-R5 | spec | trial-use | FHIR R5 5.0.0, for $apply and the expression language codes | hl7.fhir.r5.core#5.0.0 | <https://hl7.org/fhir/R5/> | none | 2026-11-14 |
| CPG-2.0.0 | spec | trial-use | Clinical Practice Guidelines 2.0.0 (STU2) | hl7.fhir.uv.cpg#2.0.0 | <https://hl7.org/fhir/uv/cpg/STU2/> | none | 2026-11-14 |
| CR-4.16.0 | implementation-source | n/a | clinical-reasoning (cqf-fhir-cr) 4.16.0, released 2026-11-21, with the CQL translator and engine 5.7.0 and HAPI FHIR 9.0.0 (cql-language-server 5.0.0 still uses 4.13.0) | cqframework/clinical-reasoning@472ae350d14831e340136d41e9dd7183deab5e78 | <https://github.com/cqframework/clinical-reasoning/tree/v4.16.0> | none (the fetch script caches a clone) | 2026-11-14 |
| PROBES-2026-11-14 | observed-behavior | n/a | clinical-reasoning 4.13.0 (CQL translator and engine 5.4.0), run with `scripts/apply/` | `resources/probes/2026-11-14/` | none | `resources/probes/2026-11-14/` | 2026-11-14 |
| PROBES-2026-11-24 | observed-behavior | n/a | clinical-reasoning 4.16.0 (CQL translator and engine 5.7.0, HAPI FHIR 9.0.0), run with `scripts/apply/`: the 2026-11-14 probes again, compared with 4.13.0, and new ones | `resources/probes/2026-11-24/` | none | `resources/probes/2026-11-24/` | 2026-11-24 |

## Reading a citation

| Source | URL |
| --- | --- |
| FHIR-R4, FHIR-R4B, FHIR-R5 | `https://hl7.org/fhir/<R4|R4B|R5>/<page>`; package files at `https://packages.fhir.org/hl7.fhir.<r4|r4b|r5>.core/<version>` |
| CPG-2.0.0 | `https://hl7.org/fhir/uv/cpg/STU2/<page>`; package at `https://packages.fhir.org/hl7.fhir.uv.cpg/2.0.0` (the `cpg` skill builds a local copy) |
| CR-4.16.0 | `https://github.com/cqframework/clinical-reasoning/blob/v<version>/<path>#L<a>-L<b>` |

For another clinical-reasoning release, read the same file at its tag and find the code by its content
near the cited lines. The release a HAPI FHIR server uses is in its dependencies (`cqf-fhir-cr`).

**Cited files.** The full paths behind each `…`:

| Source | Path |
| --- | --- |
| CR | `cqf-fhir-cr-hapi/src/main/java/org/opencds/cqf/fhir/cr/hapi/r4/plandefinition/PlanDefinitionApplyProvider.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/activitydefinition/apply/ApplyRequest.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/activitydefinition/apply/resolvers/R4ResolverFactory.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/activitydefinition/apply/resolvers/r4/ServiceRequestResolver.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/common/DynamicValueProcessor.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/common/InputParameterResolver.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/common/IOperationRequest.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/plandefinition/PlanDefinitionProcessor.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/plandefinition/apply/ApplyProcessor.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/plandefinition/apply/ProcessAction.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/plandefinition/apply/ProcessDefinition.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/plandefinition/apply/ProcessGoal.java` |
| CR | `cqf-fhir-cr/src/main/java/org/opencds/cqf/fhir/cr/plandefinition/apply/ResponseBuilder.java` |
| CR | `cqf-fhir-cql/src/main/java/org/opencds/cqf/fhir/cql/LibraryConstructor.kt` |
| CR | `cqf-fhir-utility/src/main/java/org/opencds/cqf/fhir/utility/CqfExpression.kt` |
| CR | `cqf-fhir-utility/src/main/java/org/opencds/cqf/fhir/utility/adapter/BaseAdapter.kt` |
| CR | `cqf-fhir-utility/src/main/java/org/opencds/cqf/fhir/utility/adapter/IPlanDefinitionActionAdapter.kt` |
| CR | `cqf-fhir-utility/src/main/java/org/opencds/cqf/fhir/utility/adapter/r4/PlanDefinitionAdapter.kt` |
| CR | `cqf-fhir-utility/src/main/java/org/opencds/cqf/fhir/utility/adapter/r4/RequestActionAdapter.kt` |
