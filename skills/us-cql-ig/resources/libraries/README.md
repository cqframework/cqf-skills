# Common CQL Artifacts for FHIR (US-Based) 2.0.0: Libraries

The CQL source of the libraries published in the `hl7.fhir.us.cql` 2.0.0 package (CC0-1.0), taken from each Library resource's `text/cql` content. The package also carries their ELM, which isn't copied here. FHIRHelpers and FHIRCommon come from the Using CQL With FHIR IG (`hl7.fhir.uv.cql`); see the `cql-ig` skill.

| File | Canonical URL | Version | Depends on | Lines |
| --- | --- | --- | --- | --- |
| [USCoreCommon.cql](USCoreCommon.cql) | `http://hl7.org/fhir/us/cql/Library/USCoreCommon` | 2.0.0 | FHIRHelpers|4.0.1, FHIRCommon|2.0.0 | 251 |
| [USCoreElements.cql](USCoreElements.cql) | `http://hl7.org/fhir/us/cql/Library/USCoreElements` | 2.0.0 | FHIRHelpers|4.0.1, FHIRCommon|2.0.0, USCoreCommon|2.0.0 | 755 |
| [CumulativeMedicationDuration.cql](CumulativeMedicationDuration.cql) | `http://hl7.org/fhir/us/cql/Library/CumulativeMedicationDuration` | 2.0.0 | FHIRHelpers|4.0.1, FHIRCommon|2.0.0 | 751 |
| [QICoreCommon.cql](QICoreCommon.cql) | `http://hl7.org/fhir/us/cql/Library/QICoreCommon` | 2.0.0 | FHIRHelpers|4.0.1, FHIRCommon|2.0.0 | 381 |
| [C4BBCommon.cql](C4BBCommon.cql) | `http://hl7.org/fhir/us/cql/Library/C4BBCommon` | 2.0.0 | C4BB-ModelInfo|2.2.0-derived | 8 |
| [USCoreTests.cql](USCoreTests.cql) | `http://hl7.org/fhir/us/cql/Library/USCoreTests` | 2.0.0 | FHIRHelpers|4.0.1 | 84 |
| [USCoreCommonTests.cql](USCoreCommonTests.cql) | `http://hl7.org/fhir/us/cql/Library/USCoreCommonTests` | 2.0.0 | USCoreCommon|2.0.0 | 87 |
| [USCoreElementsTests.cql](USCoreElementsTests.cql) | `http://hl7.org/fhir/us/cql/Library/USCoreElementsTests` | 2.0.0 | FHIRHelpers|4.0.1, FHIRCommon|2.0.0, USCoreCommon|2.0.0, USCoreElements|2.0.0 | 209 |
| [CumulativeMedicationDurationTests.cql](CumulativeMedicationDurationTests.cql) | `http://hl7.org/fhir/us/cql/Library/CumulativeMedicationDurationTests` | 2.0.0 | FHIRHelpers|4.0.1, CumulativeMedicationDuration|2.0.0 | 133 |
| [QICoreCommonTests.cql](QICoreCommonTests.cql) | `http://hl7.org/fhir/us/cql/Library/QICoreCommonTests` | 2.0.0 | QICoreCommon | 410 |

The package also publishes these model definitions. Only USCore's is condensed in this skill (see [../modelinfo/README.md](../modelinfo/README.md)).

| ModelInfo Library | Version |
| --- | --- |
| `http://hl7.org/fhir/us/cql/Library/USCore-ModelInfo` | 6.1.0-derived |
| `http://hl7.org/fhir/us/cql/Library/QICore-ModelInfo` | 6.0.0-derived |
| `http://hl7.org/fhir/us/cql/Library/C4BB-ModelInfo` | 2.2.0-derived |
