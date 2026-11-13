# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

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
