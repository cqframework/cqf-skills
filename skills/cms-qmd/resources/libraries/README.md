# CMS FHIR Quality Measure Development IG (0.8.0-cibuild): Libraries

The shared CQL libraries in [cqframework/cms-qmd](https://github.com/cqframework/cms-qmd/tree/9bcc541e1ca4e12488fbca4e108727108be8c1aa/input/cql), as written. CQMCommon is being refactored into CQMConcepts, CQMElements and CQMInferences; see [../pages/refactored_index.md](../pages/refactored_index.md). FHIRHelpers and FHIRCommon come from the `cql-ig` skill, USCoreCommon and USCoreElements from `us-cql-ig`, and the USQualityCore model from `usqualitycore`.

| File | Version | Models | Includes | Lines |
| --- | --- | --- | --- | --- |
| [CQMCommon.cql](CQMCommon.cql) | 5.2.000 | USQualityCore 0.5.0, USCore 6.1.0-derived, FHIR 4.0.1 | FHIRHelpers 4.0.1, FHIRCommon 2.0.0, USCoreCommon 2.0.0, USCoreElements 2.0.0 | 184 |
| [CQMConcepts.cql](CQMConcepts.cql) | 0.5.000 | USQualityCore 0.5.0, USCore 6.1.0-derived, FHIR 4.0.1 | FHIRHelpers 4.0.1, FHIRCommon 2.0.0, USCoreCommon 2.0.0 | 559 |
| [CQMElements.cql](CQMElements.cql) | 0.5.000 | USQualityCore 0.5.0, USCore 6.1.0-derived, FHIR 4.0.1 | FHIRHelpers 4.0.1, FHIRCommon 2.0.0, CQMConcepts 0.5.000, FHIRBuilders 0.1.000 | 333 |
| [CQMInferences.cql](CQMInferences.cql) | 0.5.000 | USQualityCore 0.5.0, USCore 6.1.0-derived, FHIR 4.0.1 | FHIRHelpers 4.0.1, FHIRCommon 2.0.0, CQMElements 0.5.000 | 42 |
| [ClaimCommon.cql](ClaimCommon.cql) | 0.5.000 | FHIR 4.0.1 | FHIRHelpers 4.0.1 | 510 |
| [ClaimElements.cql](ClaimElements.cql) | 0.5.000 | USQualityCore 0.5.0, USCore 6.1.0-derived, FHIR 4.0.1 | FHIRHelpers 4.0.1, FHIRCommon 2.0.0, ClaimCommon 0.5.000 | 230 |
| [MedicationCommon.cql](MedicationCommon.cql) | 0.2.000 | FHIR 4.0.1 | FHIRHelpers 4.0.1 | 471 |
| [FHIRBuilders.cql](FHIRBuilders.cql) | 0.1.000 | FHIR 4.0.1 | FHIRHelpers 4.0.1, FHIRCommon 2.0.0 | 329 |
