# US Quality Core 0.5.0: Libraries

The CQL source of the libraries published in the `fhir.onc.us-quality-core` 0.5.0 package (CC0-1.0), taken from each Library resource's `text/cql` content. The package also carries their ELM, which isn't copied here. FHIRHelpers and FHIRCommon come from the Using CQL With FHIR IG (see the `cql-ig` skill), and USCoreCommon and USCoreElements from the US CQL IG (see the `us-cql-ig` skill).

| File | Canonical URL | Version | Depends on | Lines |
| --- | --- | --- | --- | --- |
| [USQualityCoreCommon.cql](USQualityCoreCommon.cql) | `http://fhir.org/guides/onc/us-quality-core/Library/USQualityCoreCommon` | 0.5.0 | USQualityCore-ModelInfo|0.5.0, FHIRHelpers|4.0.1, FHIRCommon|2.0.0 | 225 |
| [USQualityCoreCommonTests.cql](USQualityCoreCommonTests.cql) | `http://fhir.org/guides/onc/us-quality-core/Library/USQualityCoreCommonTests` | 0.5.0 | USQualityCore-ModelInfo|0.5.0, USQualityCoreCommon | 410 |

The model definition, `http://fhir.org/guides/onc/us-quality-core/Library/USQualityCore-ModelInfo` version 0.5.0, is condensed in [../modelinfo/README.md](../modelinfo/README.md).
