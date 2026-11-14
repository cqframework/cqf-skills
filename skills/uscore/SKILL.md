---
name: uscore
description: Looks up and applies US Core profiles (hl7.fhir.us.core 6.1.0 and 9.0.0), including element cardinality, Must Support, Additional USCDI Requirements, bindings, US Core extensions (race, ethnicity, sex, tribal affiliation), missing-data rules, and what changed between 6.1.0 and 9.0.0. Use when building or checking FHIR resources against US Core, choosing a US Core profile, or answering which elements US Core requires. For CQL against US Core, use the us-cql-ig skill.
license: Apache-2.0
---

# US Core

US Core (`hl7.fhir.us.core`) is the base set of FHIR R4 profiles for US healthcare data exchange
and ONC Health IT Certification. It maps the USCDI data classes to FHIR. This skill covers two
releases:

- **6.1.0** (USCDI v3). The Common CQL Artifacts IG (see the `us-cql-ig` skill) and US Quality
  Core build on this release.
- **9.0.0**, the current release.

When a question doesn't name a version, ask which one, or answer for both and say where they
differ. For base FHIR R4 resources, see the `fhir` skill. For the HL7 standard extensions, see the
`fhir-extensions` skill.

## Knowledge base

Build it once with `bash scripts/build-kb.sh`. It downloads both packages and renders one element
table per profile and extension into `resources/profiles/6.1.0/` and `resources/profiles/9.0.0/`,
named by id (for example `us-core-patient.md`). The output is generated and not committed.

- Start with the version's `README.md`. It lists every profile and extension with its base and
  status. `retired (deprecated)` marks an artifact that shouldn't be used for new content.
- In a profile file, read `## Changes from base` first: it lists what US Core constrains. Flags
  are `MS` (Must Support), `USCDI` (an Additional USCDI Requirement), `modifier` and `summary`.
- A deprecated extension's header has a **Status Reason** line naming its replacement.
- The format is described in [resources/format-guide.md](resources/format-guide.md)
  (Other output styles).

To compare versions, open the same file in both folders, for example
`resources/profiles/6.1.0/us-core-patient.md` and `resources/profiles/9.0.0/us-core-patient.md`.

## Requirements to apply

These come from the US Core Must Support and General Requirements pages, and are the same in
substance in both versions. The CONF numbers are 9.0.0's; 6.1.0 doesn't number its requirements.

- **Mandatory** elements have min 1, and the data is expected to be present. Must Support
  elements: Responders SHALL be able to populate them (CONF-0075), and Requestors SHALL process
  them without failing (CONF-0076). If data for an element is absent and the reason is unknown,
  leave the element out (CONF-0078), and read a missing element as "not present" (CONF-0079).
- **Additional USCDI Requirements** (the `USCDI` flag) are optional elements that implementers
  seeking ONC certification SHALL treat as Must Support (CONF-0083, CONF-0084). Otherwise they are
  optional.
- **Missing data in a mandatory element:**
  - Non-coded: put the `data-absent-reason` extension, code `unknown`, on the element (CONF-0041).
    For example, `name: [{extension: [{url: ".../data-absent-reason", valueCode: "unknown"}]}]`.
  - Coded, with an example, preferred or extensible binding: send text only if that's all you have
    (CONF-0042). Otherwise send the value set's "unknown" code, or `unknown` from the
    DataAbsentReason code system (CONF-0044, CONF-0045).
  - Coded, with a required binding: use the value set's "unknown" code if it has one (CONF-0046).
    Otherwise a real code from the value set is needed, or the instance doesn't conform
    (CONF-0047). These elements have no "unknown" code: `AllergyIntolerance.clinicalStatus`,
    `Condition.clinicalStatus`, `DocumentReference.status`, `Immunization.status`,
    `Goal.lifecycleStatus`, `MedicationRequest.intent` and `ServiceRequest.intent`.
- **Required binding:** at least one coding SHALL come from the value set, and text alone isn't
  valid (CONF-0018 to CONF-0020).
- **Extensible binding:** use a code from the value set when a suitable concept exists. Otherwise
  use another code, or text only (CONF-0023, CONF-0024).
- **Modifiers:** not every modifier element is Must Support, and US Core doesn't require support
  for those that aren't (for example `implicitRules`, `modifierExtension` and `Patient.active`).
  Logic that reads US Core data still has to account for them, because a modifier changes what
  the resource means.
- **Conformance claims:** a server lists the profiles it supports in
  `CapabilityStatement.rest.resource.supportedProfile` (CONF-0016). These pages don't require
  instances to carry `meta.profile`.

## Patient demographics extensions

| Data | 6.1.0 | 9.0.0 |
| --- | --- | --- |
| Race, ethnicity | `us-core-race`, `us-core-ethnicity`: complex, with `ombCategory`, `detailed` and a required `text` | Same. Race allows 6 `ombCategory` codes (5 in 6.1.0). |
| Sex | `us-core-sex` (`Patient.extension:sex`) | `us-core-individual-sex`, a `valueCoding` with an extensible binding (the package's example uses SNOMED CT). `us-core-sex` is deprecated. |
| Birth sex | `us-core-birthsex` on Patient | Not in the Patient profile. The extension remains, with standards status informative. |
| Gender identity | `us-core-genderIdentity` on Patient | Not in the Patient profile. `us-core-genderIdentity` is deprecated in favour of the HL7 `individual-genderIdentity` extension. |
| Interpreter needed | none | `us-core-interpreter-needed` (`interpreterRequired`) |
| `Patient.gender` | 1..1, Must Support | 0..1, not Must Support |

Race and ethnicity codes are CDC Race and Ethnicity codes (`urn:oid:2.16.840.1.113883.6.238`).
Ethnicity allows one `ombCategory`. In 9.0.0, if race's `ombCategory` holds `ASKU` or `UNK`, no
other OMB category may be present (us-core-23). A name needs a `family` or `given` part, or the
data-absent-reason extension (us-core-6).

## Other changes from 6.1.0 to 9.0.0

- **New profiles and extensions:** ADI DocumentReference, ADI documentation Observation, Average
  Blood Pressure, Care Experience Preference, Treatment Intervention Preference, Device,
  FamilyMemberHistory, Medication Adherence, and the authentication-time,
  familymemberhistory-recorder, individual-sex and interpreter-needed extensions.
- **Removed:** the Implantable Device profile. 9.0.0 has a general US Core Device Profile instead.
- Check `## Changes from base` in both versions before reusing an instance written for one
  version against the other. The Patient changes above are the most common source of failure.

## CQL

CQL against US Core needs a model of its profiles. The Common CQL Artifacts IG publishes
`USCore-ModelInfo` 6.1.0-derived together with the USCoreCommon and USCoreElements libraries, and
US Core 9.0.0 publishes its own `USCore-ModelInfo` (version 9.0.0) as an example Library. See the
`us-cql-ig` skill.
