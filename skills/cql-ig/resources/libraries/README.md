# Using CQL With FHIR 2.0.0: Libraries

The CQL source of the libraries published in the `hl7.fhir.uv.cql` 2.0.0 package (CC0-1.0), taken from each Library resource's `text/cql` content. The package also carries their ELM (XML and JSON), which isn't copied here.

| File | Canonical URL | Version | Depends on | Lines |
| --- | --- | --- | --- | --- |
| [FHIRHelpers.cql](FHIRHelpers.cql) | `http://hl7.org/fhir/uv/cql/Library/FHIRHelpers` | 4.0.1 | (none) | 747 |
| [FHIRCommon.cql](FHIRCommon.cql) | `http://hl7.org/fhir/uv/cql/Library/FHIRCommon` | 2.0.0 | FHIRHelpers|4.0.1 | 908 |
| [FHIRHelpersTests.cql](FHIRHelpersTests.cql) | `http://hl7.org/fhir/uv/cql/Library/FHIRHelpersTests` | 2.0.0 | FHIRHelpers|4.0.1 | 188 |
| [FHIRCommonTests.cql](FHIRCommonTests.cql) | `http://hl7.org/fhir/uv/cql/Library/FHIRCommonTests` | 2.0.0 | FHIRHelpers|4.0.1, FHIRCommon | 662 |

Note that FHIRHelpers has version 4.0.1 (it tracks the FHIR version), while FHIRCommon and the test libraries have the IG version, 2.0.0.
