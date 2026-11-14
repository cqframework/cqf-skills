# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

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
