# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- `vscode-cql` skill: a run-time error in any definition replaces that test case's results with a
  single `Error` entry while other cases still run (from the language server's evaluation code);
  the extension reads a test case MeasureReport's expected populations but never compares them,
  and reads its description only under the CQFM URL; how result values are formatted; pointers to
  the `madie` skill's results checker and the `cql` skill's testing guide; eval questions CF-03 and
  CF-04.
- `cql` skill: pitfalls from the CQL skill in cqframework/dqm-content-cms-2026, each checked with
  translator and engine 5.5.0 (new probe record `resources/probes/2026-11-14/`, with its harness):
  - A fluent call resolves to the first included library with a compatible overload, even over an
    exact match in a later one, without a warning; a fluent function named like a FHIRPath function
    (`toString`, `toBoolean`…) is never called; a fluent function can't be called with ordinary
    call syntax; two functions with the same signature compile without a diagnostic.
  - A function call or list literal as a query source needs parentheses; a `Concept` selector takes
    only Code selectors; with `using FHIR` an unqualified `Quantity` selector is `FHIR.Quantity`; a
    string literal spelled like a definition draws a warning.
  - `Matches` on the engine matches the whole string, though the spec says partial matching (the
    skill previously stated only the spec reading); there is no `Trim`; `AllTrue` ignores nulls;
    `~` on Codes ignores the case of the code (a spec gap).
  - New `resources/testing.md`: unit-testing a library with a CQL test library (test definitions
    combined with `and`, case tests with `else true`, fixture builders, branch coverage).
  - Not reproduced at 5.5.0, so not added: an empty or blank `FHIR.string` reading back as null,
    setting `id` on a backbone element failing at run time, and `flatten (C.item I return …)` being
    a syntax error.
  - Eval questions TQ-24 to TQ-28.

### Added

- `trusted-ig-template` skill, in the `fhir-ig` plugin, for authors and reviewers of IG Publisher
  templates on the trusted list, built on the publisher's `trusted-template-rules.md` (added in
  HL7/fhir-ig-publisher 4e7325f):
  - Each of the twelve rules with its threat model, the safe form and the mistakes that break it; how
    the publisher loads a template chain, decides what is active content and what is trusted, and what
    it gives a template's Ant scripts and pre-process transforms, cited to the publisher's code.
  - Ant and XSLT behaviour the rules depend on, checked with probes (`resources/probes/2026-11-17/`):
    a line break in an IG value adds a property to a `<loadproperties>` file and wins over the
    template's own; `unless="ig.networkprohibited"` never runs; relative paths resolve in the IG's
    folder; pre-process stylesheets can't include, import or read files.
  - `scripts/audit_template.py`, a static audit of a template folder against the rules (A01 to A11),
    with tests; a review checklist for rule 12; a weekly check of the rules file and the cited code.
  - Evals: 15 questions, trigger prompts, and a task to fix a template with ten planted problems, with
    a grader, its tests and a reference answer.
- `questionnaire` skill, in the `clinical-reasoning` plugin, for Questionnaire, QuestionnaireResponse and
  SDC's `$populate` and `$extract`, from raleigh-claude-skills at `8224e28`, originally written by
  raleigh-g-thompson. Changes on import:
  - Grounded in three layers, each cited: FHIR R4 (with R5 where Questionnaire changed), SDC 4.0.0 (the
    source cited an unversioned SDC), and clinical-reasoning 4.13.0, the reference implementation in
    HAPI FHIR, cited to its code and checked by running it (`resources/probes/2026-11-14/`).
  - Corrections: questions, not only groups, can have child items (under `answer.item` in the
    response); `$populate`'s `context.name` is a string matching a launchContext code, not a Coding;
    `$populate` fills `answer`, never `initial`; calculated answers use `calculatedExpression`, not
    `cqf-calculatedValue` (unused in SDC 4.0.0), and a user may override them; SDC 4.0.0 adds the
    `clinical` launch context; R4's que-12 only fires for three or more enableWhens.
  - New: SDC 4.0.0's `$populate` parameters and what changed from 3.0.0, the expression languages and
    library qualification rules, extraction methods and `$extract`, and Questionnaire generation.
  - What clinical-reasoning 4.13.0 does differently, each probed: every expression runs as CQL;
    `%patient` needs a `patient` context and `%subject` is never bound; the first context becomes the
    subject; a qualified `text/cql-identifier` fails; list results give several answers on
    non-repeating items and results aren't converted to the item type; `calculatedExpression`,
    `variable`, `enableWhen` and observation-based population aren't implemented; `$extract` ignores
    `observationExtract`, emits an invalid `valueDecimal` without a unit, reuses Observation ids for
    repeated answers, uses the old observation-category system, and throws on SDC 4.0.0's complex
    `definitionExtract`.
  - Dropped: the Da Vinci DTR and prior-authorization framing.
  - `scripts/sdc/run.sh` runs `$populate`, `$extract` and generation locally; `scripts/check_release.py`
    joins the weekly release check.
  - Evals in `evals/questionnaire/`: questions, an answer key, a graded intake-form task with a reference
    answer, and trigger prompts.
- `plan-definition` skill, in the `clinical-reasoning` plugin, for PlanDefinition, ActivityDefinition and
  `$apply`, from raleigh-claude-skills at `8224e28`, originally written by raleigh-g-thompson. Changes on
  import:
  - Grounded in three layers, each cited: the FHIR R4 specification (with R4B and R5 where they differ),
    CPG 2.0.0, and clinical-reasoning 4.13.0, the reference implementation in HAPI FHIR, cited to its
    code and checked by running it (`resources/probes/2026-11-14/`).
  - Corrections: R4's expression languages are `text/cql`, `text/fhirpath` and
    `application/x-fhir-query` (`text/cql-identifier` is R4B/R5, usable on R4); `$apply` returns a
    CarePlan in R4 and a Bundle per subject in CPG 2.0.0 and R5, never a GuidanceResponse; `userType` and
    the other context parameters are CodeableConcepts, and `parameters` is a CPG addition; dynamicValue
    paths are relative; the grouping behaviors' meanings; trigger types (no `data-requested`); action
    `goalId`; ActivityDefinition `$apply` sets status `draft` and requests within a RequestGroup are
    options.
  - What the implementation does differently: a null or failing condition keeps the action without its
    definition or children; `text/fhirpath` is evaluated by the CQL engine; unknown languages are
    treated as named expressions; with several libraries and no `reference` the library isn't
    defined; behaviors aren't enforced and most aren't copied; a Questionnaire definition is contained
    as is; requests default to status `active` (ServiceRequest intent `order`); several context
    parameters are ignored; errors go to `cqf-messages`.
  - Removed the Da Vinci prior-authorization, CDS Hooks and DTR material (to be done separately if
    wanted) and the Library packaging section (covered by `cql-ig` and `crmi`).
  - New `scripts/apply/` runs `$apply` with clinical-reasoning 4.13.0 on a folder in IG layout;
    `scripts/check_release.py` follows clinical-reasoning releases in the weekly release check.

- `madie` skill, in the `cql` plugin, for US Quality Core 0.5.0 test cases and measure CQL in MADiE,
  from raleigh-claude-skills at `8224e28`, originally written by raleigh-g-thompson. Changes on import:
  - Retargeted from QI-Core to US Quality Core 0.5.0 (MADiE's "US Quality Core v0.5.0" model). MADiE
    treats it differently from QI-Core in places, all recorded: test case JSON isn't rewritten on save
    (Patient id, references, bundle type), validation is against US Quality Core 0.5.0 and US Core
    6.1.0, population return types aren't checked, and the default CQL is the US Quality Core
    template. Drafting a QI-Core 6.0.0 measure as US Quality Core rewrites only its `using` lines.
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
  - Corrections to the resource notes: Simple Observation has a value and no fixed category;
    `verificationStatus` needn't be `confirmed`; DeviceRequest's `code[x]` may be a reference; a
    Patient needs an `identifier` and a `gender`.
  - Added what MADiE checks and rewrites in measure CQL (library line, FHIRHelpers alias, value set
    versions and URLs, library names) and its default CQL templates. CQL style is left to `cms-qmd`.
  - Removed one project's conventions that MADiE doesn't need: deterministic resource ids, an
    md5-derived `testCaseId`, reusing patient ids, and a mandatory change summary file, and the
    follow-up window example. Bonnie-style series names are kept as an optional convention.
  - New `scripts/check_test_cases.py` checks a test case zip or folder against MADiE's import rules.
  - New support for working on MADiE test cases in VS Code, in `resources/vscode.md`:
    `scripts/madie_to_vscode.py` unpacks a MADiE export into the CQL extension's layout (which
    ignores Bundles), `scripts/vscode_to_madie.py` packages VS Code test cases as an importable zip,
    and `scripts/check_results.py` checks Execute CQL results against the MeasureReport expected
    values by applying fqm-execution's population rules and MADiE's comparison. Differences between
    the engines are to be reported as tests in cqframework/cql-tests.
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
