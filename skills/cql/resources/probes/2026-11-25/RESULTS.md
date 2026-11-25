# Probe results, 2026-11-25

Run with translator and engine **5.5.0** and clinical reasoning 4.13.0, through cql-language-server
5.0.0 (the versions the VS Code CQL extension 1.0.0 uses), by cql-mcp 0.1.0-rc.2's `cql_execute`
with `modelUri` set to `data/` and `contextValues` `["probe-patient"]`. Unlike the 2026-11-14
probes, these read patient data, so they test retrieves. The library compiled in a FHIR IG project
whose packages include US Quality Core 0.5.0. Run twice, with identical output.

## Profile retrieves and `meta.profile`

[`testProfileRetrieve.cql`](testProfileRetrieve.cql) retrieves the patient's MedicationRequests as base
FHIR and as two US Quality Core profiles. The data, in [`data/probe-patient/`](data/probe-patient/),
has four MedicationRequests:

| Resource | `meta.profile` | `doNotPerform` |
| --- | --- | --- |
| `requested` | us-quality-core-medicationrequest | absent |
| `not-requested` | us-quality-core-medicationnotrequested | true |
| `no-profile` | none | absent |
| `do-not-perform-requested-profile` | us-quality-core-medicationrequest | true |

The US Quality Core MedicationRequest profile fixes `doNotPerform` to false, and MedicationNotRequested
fixes it to true, so the last two separate filtering by the declared profile from filtering by the
profile's fixed values.

| Expression | Output |
| --- | --- |
| `[FHIR.MedicationRequest] R return R.id` | `[id#not-requested, id#requested, id#do-not-perform-requested-profile, id#no-profile]` |
| `[USQualityCore.MedicationRequest] R return R.id` | `[id#requested, id#do-not-perform-requested-profile]` |
| `[USQualityCore.MedicationNotRequested] R return R.id` | `[id#not-requested]` |

**Settles:** with this engine and repository, a retrieve of a profile returns exactly the resources
whose `meta.profile` declares that profile. A resource that conforms but doesn't declare it
(`no-profile`) isn't returned, and one that declares it but breaks its fixed values
(`do-not-perform-requested-profile`) is. A base FHIR retrieve returns all of them. The same was
observed with engine 4.9.0 in cqframework/dqm-content-cms-2026 (DQMCMS-739494f).
