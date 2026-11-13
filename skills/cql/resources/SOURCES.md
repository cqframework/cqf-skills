# Sources

Registry of every source the skill's resource files cite. Cite a claim inline as
`[src: ID locator]`, for example `[src: CQL-1.5.3 09-b-cqlreference > Type Operators > Is]`.

| ID | Kind | Status | Version | Pinned locator | Published URL | Local copy | Retrieved |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CQL-1.4 | spec | trial-use | 1.4, Release 1 STU 4 | HL7/cql@v1.4-release | <https://cql.hl7.org/STU4/> | `resources/spec/1.4/` | 2026-10-22 |
| CQL-1.5.3 | spec | normative | 1.5.3, Release 1 Errata 2 (contains trial-use content, marked in the text) | HL7/cql@v1.5.3 | <https://cql.hl7.org/N1A/> | `resources/spec/1.5.3/` | 2026-10-22 |
| CQL-2.0.0 | spec | trial-use | 2.0.0, R2 STU 1 | HL7/cql@2e191f8f2f96892c1c33fdcdf2f1d210f9df201f | <https://cql.hl7.org/> | `resources/spec/2.0.0/` | 2026-10-22 |
| CQL-TESTS | test-suite | informative | conformance tests, current suite | cqframework/cql-tests@5747d2b72f29d733fbc114383c4a15a30999ffaf | <https://github.com/cqframework/cql-tests> | `resources/spec/cql-tests/` | 2026-11-13 |
| CQFW-5.4.0 | implementation-source | n/a | cqframework translator and engine 5.4.0 | cqframework/clinical_quality_language@v5.4.0 | <https://github.com/cqframework/clinical_quality_language/tree/v5.4.0> | none (read with `git show v5.4.0:<path>` in a local checkout) | 2026-10-22 |
| CQLWIKI | guide | informative | wiki commit cc3c351 (2026-10-16) | cqframework/CQL-Formatting-and-Usage-Wiki.wiki@cc3c3512c0829bf0dad6752123f3ff2ce48ef57d | <https://github.com/cqframework/CQL-Formatting-and-Usage-Wiki/wiki> | none | 2026-10-22 |
| CMSQMD | guide | informative | CMS Quality Measure Development IG, CI build (2026-11-03) | cqframework/cms-qmd@9bcc541e1ca4e12488fbca4e108727108be8c1aa | <https://build.fhir.org/ig/cqframework/cms-qmd/branches/main/> | none | 2026-11-13 |
| PROBES-2026-10-22 | observed-behavior | n/a | translator 5.4.0, engine 5.4.0, CQL language server 4.11.0-SNAPSHOT | `resources/probes/2026-10-22/` | none | `resources/probes/2026-10-22/` | 2026-10-22 |

## Notes

- The spec copies are built locally from these locators by `scripts/fetch-spec.sh` and are not
  distributed with the skill; see [spec/README.md](spec/README.md).
- CQL-TESTS is the only conformance-test source. The test suites published with the spec are out
  of date. They are not built, and they must not be cited, whatever version the engine targets.
- Conformance tests are informative: "The tests defined here are informative, not normative aspects of the
  specification. If there is a discrepancy between the behavior of a test and the specification,
  the specification should be considered the source of truth." (tests page, all three versions).
- CMSQMD is the CMS Quality Measure Development IG, which now maintains the authoring patterns.
  Cite it as `[src: CMSQMD <page>.html]` or `[src: CMSQMD <page>.html#<anchor>]`; see
  [guides/README.md](guides/README.md).
- CQLWIKI is the CQL Formatting and Usage Wiki ("Cooking with CQL"). Its content is now
  maintained in CMSQMD. The wiki stays published, and existing citations of its Q&A pages refer to
  it at the pinned commit. Cite it as `[src: CQLWIKI <Page>.md]` or
  `[src: CQLWIKI <Page>.md#<anchor>]`, for idioms and pitfalls only. Prefer CMSQMD for new
  citations.
- PROBES-2026-10-22 records what one implementation did, with the configuration noted in its
  `RESULTS.md`. It is evidence of behaviour, not of what the spec requires.
