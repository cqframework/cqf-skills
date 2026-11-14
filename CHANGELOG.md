# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- `madie` skill, in the `cql` plugin, for QI-Core test cases and measure CQL in MADiE, from
  raleigh-claude-skills at `8224e28`, originally written by raleigh-g-thompson. Changes on import:
  - MADiE has no releases, so the skill is pinned to `develop` commits of its repositories from
    2026-11-14, and every behaviour is cited to that code. `scripts/check_release.py` compares each
    cited range with the current branch and runs in the weekly release check, which opens an issue
    only when cited code changes.
  - Corrections against the code: the export file name uses the eCQM abbreviated title and has no
    fixed series list; `testCaseId` in `.madie` is MADiE's own id and isn't read on import (it isn't
    an md5 of the patient id); import matches test cases by patient id and updates an existing one;
    a parent folder in the zip makes it unimportable; MADiE turns transaction bundles into
    collections and drops the MeasureReport after reading the expected values; export gives every
    resource except the Patient a new id; the exported MeasureReport uses the CQM IG's
    `cqm-testcase` profile with a contained Parameters resource, not `test-case-cqfm` with an
    Organization.
  - Corrections to the resource notes: QI-Core Simple Observation has a value and no fixed
    category; `verificationStatus` needn't be `confirmed`; DeviceRequest's `code[x]` may be a
    reference; the profiles differ between QI-Core 4.1.1 and 6.0.0.
  - Added what MADiE checks and rewrites in measure CQL (library line, FHIRHelpers alias, value set
    versions and URLs, library names) and its default CQL templates. CQL style is left to `cms-qmd`.
  - Removed one project's conventions that MADiE doesn't need: deterministic resource ids, an
    md5-derived `testCaseId`, reusing patient ids, and a mandatory change summary file, and the
    follow-up window example. Bonnie-style series names are kept as an optional convention.
  - New `scripts/check_test_cases.py` checks a test case zip or folder against MADiE's import rules.
  - Added from the CQL skill in cqframework/dqm-content-cms-2026: MADiE runs test cases in the
    browser with fqm-execution (the JavaScript engine), with the Patient's id replaced by the test
    case's internal id; engine differences and code systems MADiE lacks, as observed there; finding
    test resources by identifier key; and testing a shared library with a Cohort measure on a
    `_Passed` define.

- `vscode-cql` skill, in the `cql` plugin, for the VS Code CQL extension (`cqframework.cql`) 1.0.0 and
  cql-language-server 5.0.0, from raleigh-claude-skills at `8224e28`, originally written by
  raleigh-g-thompson. Changes on import:
  - Re-pinned from the extension wiki as captured on 2026-08-22 to the 1.0.0 releases. Every
    behaviour is cited to the extension or language server code at those tags, or to the wiki at its
    1.0.0 update, where the wiki is right.
  - Corrections against the code, including: the default result format is `flat`, not individual;
    the extension has no VS Code settings; Bundles in test case folders are ignored; Execute CQL gets
    no value sets without an `ig.ini`; one bad parameter value drops every configured parameter; the
    CQL Explorer and Execute CQL find test cases differently; a `launch.json` needs the `.cql` file's
    URI, `libraryName` and `fhirVersion`; the debugger's scopes; packaging is `tsc`, not esbuild; Java
    17, not 11.
  - The wiki says `dev` dependencies are built in memory and no stub is written to
    `~/.fhir/packages`; at 5.0.0 the server still writes an empty `<pkg>#current` stub. The skill
    follows the code and flags the stub.
  - `resources/commands.md` is generated from the extension's `package.json` by
    `scripts/gen_reference.py`.
  - `scripts/check_release.py` follows new extension and server releases and wiki changes, and runs
    in the weekly release check. `scripts/lint_skill_vscql.py` checks citations against clones made by
    `scripts/fetch-sources.sh`.
  - New evals in `evals/vscode-cql/`.
- The weekly release check (`.github/workflows/release-check.yml`, renamed from
  `ig-publisher-release-check.yml`) now runs every skill's `scripts/check_release.py`, with one issue
  per skill labelled `<skill>-release`.
- `ig-publisher` cites vscode-cql 1.0.0 instead of an unreleased branch commit, and the `cql` skill
  names the translator versions IG Publisher 3.0.4 and the VS Code extension use.
- `ig-publisher` skill, in the `fhir-ig` plugin, for configuring, running and debugging the HL7 IG
  Publisher, from raleigh-claude-skills at `8224e28`, originally written by raleigh-g-thompson.
  Changes on import:
  - Re-pinned from IG Publisher 3.0.1, org.hl7.fhir.core 7.0.2 and the 0.7.1/0.8.1 templates to
    IG Publisher 3.0.4, org.hl7.fhir.core 7.0.6, cqf.fhir.template 1.0.0 and fhir.base.template
    1.0.0. Every source-line citation was moved to the new tags and re-checked.
  - A new probe build (`resources/probes/2026-11-14/`) on 3.0.4 confirms the CQL loader findings
    with the 4.9.0 translator, and finds that fhir.base.template 1.0.0 now ships Liquid narratives,
    that 3.0.4 rewords a CQL warning so an `ignoreWarnings.txt` line written for 3.0.1 stops
    matching, and that `-package-cache-folder` is not used for every package. The cause of the
    "Unknown FHIRTypes code 'Any'" ELM failure is traced in the source.
  - New flags (`-ecosystem`, `-threads`), the terminology ecosystem and the change to `-tx`.
  - When an IG was built with a different publisher version, the skill now says to check each cited
    claim against the source at that version on GitHub. `SOURCES.md` gives the URL forms and the
    full path behind every elided citation.
  - The local copies under `resources/sources/` are only for maintainers (the linter and the
    parameter-page generator). They are built by `scripts/fetch-sources.sh` and not committed. The
    cache folder can be set with `IGPUB_SKILL_CACHE`.
  - `scripts/check_release.py` compares the pins with the latest IG Publisher, core, template and
    tools IG releases, and reports which citations a re-pin must re-read. A weekly workflow
    (`.github/workflows/release-check.yml`) runs it and opens or updates an issue
    labelled `ig-publisher-release` when a newer release is out.
  - `scripts/lint_skill.py` is a shared copy of the `cql` skill's linter, checked by
    `validate_skills.py`.
  - New evals in `evals/ig-publisher/`.
- `usqualitycore` skill, in the `fhir` plugin, for US Quality Core 0.5.0
  (`fhir.onc.us-quality-core`), and `cms-qmd` skill, in the `cql` plugin, for the CMS FHIR Quality
  Measure Development IG. They replace the `usqualitycore`, `usqualitycore-clinical-patterns` and
  `usqualitycore-claims-patterns` skills in raleigh-claude-skills at `8224e28`, originally
  written by raleigh-g-thompson. Changes on import:
  - `usqualitycore`: the profile tables are a local knowledge base built by `scripts/build-kb.sh`
    with the USCDI+ Quality flag. `scripts/build-ig.py` regenerates the committed pages
    (FHIR/us-quality-core at the 0.5.0 release, including the QDM 5.6 mapping), the condensed
    USQualityCore ModelInfo and USQualityCoreCommon from the pinned sources (CC0).
  - `cms-qmd`: `scripts/build-ig.py` regenerates every page of the IG and its shared CQL libraries
    from cqframework/cms-qmd at a pinned commit of the continuous build (0.8.0-cibuild), replacing
    the source's summaries of the Pattern Index.
  - Checked with the CQL-to-ELM translator 3.29.0. A library needs `using FHIR` alongside the
    derived model for the FHIRHelpers conversions to apply, and then unqualified class names
    resolve to base FHIR. Several retrieves in CQMCommon, CQMConcepts and CQMElements do this.
  - New evals in `evals/usqualitycore/` and `evals/cms-qmd/`.
- The `us-cql-ig` skill says to keep `using FHIR` alongside `using USCore`, and the `cql` skill
  points to `cms-qmd` for measure authoring patterns.
- `uscore` skill, in the `fhir` plugin, for US Core 6.1.0 and 9.0.0 (`hl7.fhir.us.core`). It was
  split from the `uscore` skill in raleigh-claude-skills at `8224e28`, originally written by
  raleigh-g-thompson, which mixed US Core profile tables with CQL patterns. Changes on import:
  - The profile tables are a local knowledge base built by `scripts/build-kb.sh` with the shared
    converter, for 6.1.0 and the current 9.0.0 (the source had 6.1.0 and 7.0.0).
  - SKILL.md covers Must Support, Additional USCDI Requirements, missing data and bindings, with
    9.0.0's CONF numbers, and the 6.1.0 to 9.0.0 changes, such as `Patient.gender` becoming
    optional and the sex and gender identity extensions being replaced.
  - New evals in `evals/uscore/`.
- `us-cql-ig` skill, in the `cql` plugin, for the Common CQL Artifacts for FHIR (US-Based) IG
  (`hl7.fhir.us.cql` 2.0.0), the CQL half of the source `uscore` skill. `scripts/build-ig.py`
  regenerates the committed pages, libraries (USCoreCommon, USCoreElements,
  CumulativeMedicationDuration, QICoreCommon and C4BBCommon) and the condensed USCore ModelInfo
  from the pinned package and HL7/us-cql-ig source (CC0). CQL was checked with the CQL-to-ELM
  translator 3.29.0, which showed that many USCore classes have no primary code path and that
  unqualified class names shared with FHIR resolve to FHIR. New evals in `evals/us-cql-ig/`, with
  a grader that reads translated ELM.
- The shared converter's compact renderings now show the standards status and status reason in
  each header, and its package-mode index has a Status column and names the right script.
- `cql-ig` skill, in the `cql` plugin, for the Using CQL With FHIR IG (`hl7.fhir.uv.cql` 2.0.0).
  It covers the IG's conformance requirements for CQL against FHIR and for packaging CQL in FHIR
  Library resources, the CQL-to-FHIR type mapping, `$cql` and `Library/$evaluate`, and the FHIR
  authoring patterns. `scripts/build-ig.py` regenerates the committed references from the pinned
  package and the HL7/cql-ig source at tag 2.0.0 (both CC0-1.0): the IG's narrative pages, the
  published FHIRHelpers and FHIRCommon CQL, and the FHIR ModelInfo condensed to one Markdown file
  per resource. The IG's profiles, operations and examples are rendered into a local knowledge
  base by `scripts/build-kb.sh`, with the shared converter. New evals in `evals/cql-ig/`.
- `fsh` skill, in the `fhir-ig` plugin, imported from raleigh-claude-skills at `8224e28`, originally
  written by raleigh-g-thompson. Changes on import:
  - The FSH 3.0.0 language reference is regenerated from the HL7 specification source
    (HL7/fhir-shorthand at tag 3.0.0, CC0-1.0) by `scripts/build-spec.py`, one file per section,
    with links between sections and the trial-use and optional markers kept. The source's copy had
    lost table cells and markers in conversion.
  - New guidance on the SUSHI workflow and on mistakes that SUSHI rejects or that compile to the
    wrong thing, each checked with SUSHI 3.21.0.
  - The SUSHI project notes were rewritten and checked against SUSHI 3.21.0, and no longer refer
    to skills that this repository doesn't have.
  - New evals in `evals/fsh/`, with a grader that checks the JSON SUSHI generates.
- `fhir-extensions` skill, in the `fhir` plugin: a locally built knowledge base of the FHIR
  Extensions Pack for R4 (`hl7.fhir.uv.extensions.r4` 5.4.0), with guidance on checking an
  extension's status, context and value type, and on writing extensions in JSON. New evals in
  `evals/fhir-extensions/`.
- The shared profile converter (in `crmi`, `cpg` and `fhir-extensions`) now shows each
  StructureDefinition's standards status, maturity (FMM) and work group, and why a deprecated
  artifact was deprecated (the replacement is named for 103 of the 106 deprecated extensions). For
  extensions it also shows the contexts they may be used in.
- `crmi` and `cpg` skills, in the `clinical-reasoning` plugin. They were split from the
  `fhir-profiles-cpg-crmi` skill in raleigh-claude-skills at `8224e28`, originally written by
  raleigh-g-thompson. Changes on import:
  - One skill per IG: `crmi` covers CRMI 2.0.0, and `cpg` covers CPG 2.0.0. Each includes FHIR
    Extensions (R4) 5.4.0 for the `cqf-` and `artifact-` extensions its profiles use. The source
    covered CPG 1.0.0, CRMI 1.0.0 and extensions.r4 5.2.0. Both skills note that CPG 2.0.0 dropped
    CPG 1.0.0's shareable and publishable artifact profiles, and that CRMI 2.0.0 defines them.
  - `crmi`'s SKILL.md explains that CRMI 2.0.0 capability profiles each derive from the base
    resource and are claimed together.
  - Each knowledge base is built locally by the skill's `scripts/build-kb.sh` from pinned packages,
    instead of committing about 24 MB of renderings and a 6 MB source tarball. This also replaces
    the stale committed renderings, which had broken binding cells, doubled slice names and
    truncated text.
  - Each skill has its own copy of the converter, so it can be installed on its own.
    `validate_skills.py` checks that the copies match.
  - `format-guide.md` now matches the converter's current output.
  - The converter now renders OperationDefinition parameter documentation. It used to read a
    `description` field that R4 doesn't have, so all 270 parameters across the 24
    OperationDefinitions had empty descriptions.
  - New evals in `evals/crmi/` and `evals/cpg/`, each with questions, an answer key, a graded task
    (`grade_library.py` and `grade_plandefinition.py`, tested in CI), and trigger prompts.
  - References to skills outside this repository are removed.
- `fhir` skill, imported from raleigh-claude-skills at `8224e28`, originally written by
  raleigh-g-thompson. Changes on import:
  - References to skills outside this repository are removed.
  - The description of the element tables now matches the generated files.
  - The element tables (`hl7.fhir.r4.core@4.0.1`) are committed as generated. Their generator is
    shared tooling that will come in with the model skills.
  - New evals in `evals/fhir/`: element-definition and bundle questions with an answer key, a
    graded transaction-bundle task (`grade_bundle.py`, tested in CI), and trigger prompts.
- `cql-mcp` plugin. It references cqframework/cql-mcp at `v0.1.0-rc.2`, installing that repository's
  `cql-mcp` skill and registering its MCP server. The `cql` skill now uses the `cql_*` tools to
  compile, inspect and run repros when the server is available.
- Repository structure, marketplace manifest, skill template, and validation tooling.
- `cql` skill, imported from raleigh-claude-skills at `8224e28`, originally written by
  raleigh-g-thompson. Changes on import:
  - The CQL spec copy is built locally by `scripts/fetch-spec.sh` rather than committed (HL7
    content).
  - The CQL Formatting and Usage Wiki copy is removed. Authoring patterns now point to the CMS
    Quality Measure Development IG (`CMSQMD`), and existing wiki citations refer to the published
    wiki.
  - References to skills outside this repository are removed.
  - Evals moved to `evals/cql/`.
  - `lint_skill.py` no longer assumes personal default paths.
  - Conformance tests come only from cqframework/cql-tests, now pinned at `5747d2b`. The
    out-of-date suites published with the spec are no longer built or cited, and lint rule C8
    rejects citations of them. Running the suite with cql-tests-runner is documented in
    `resources/spec/README.md`.
