# US Core Skill Test Questions: Answer Key

Expected answers for [questions.md](questions.md). Don't give this file to an agent under test.

Facts come from the packages `hl7.fhir.us.core` 6.1.0 and 9.0.0, as rendered in the `uscore`
skill's knowledge base (`resources/profiles/<version>/`, built by `scripts/build-kb.sh`), and from
the US Core Must Support and General Requirements pages (the CONF numbers are 9.0.0's). A source
written as `9.0.0/us-core-patient` is that file in the knowledge base. Each answer gives the
expected facts, the source, what a passing answer must and must not say, and where the skill covers
it ("Skill").

## Lookups

### LK-01. Two Condition profiles

- **Expected:** An encounter diagnosis claims the US Core Condition Encounter Diagnosis Profile
  (`http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition-encounter-diagnosis`). A
  problem-list item claims the US Core Condition Problems and Health Concerns Profile
  (`http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition-problems-health-concerns`).
  Both exist in 6.1.0 and 9.0.0.
- **Source:** `6.1.0/README`, `9.0.0/README`.
- **Pass if:** both profiles and URLs are right.
- **Fail if:** it names a single `us-core-condition` profile, which is what older US Core
  releases had.
- **Skill:** `SKILL.md` Knowledge base.

### LK-02. The sex extension

- **Expected:** `http://hl7.org/fhir/us/core/StructureDefinition/us-core-individual-sex`, a
  `valueCoding` (1..1) with an extensible binding, in the Patient profile as `extension:sex`. The
  6.1.0 extension, `us-core-sex`, is retired with standards status deprecated, and its status
  reason points to the individual-sex extension.
- **Source:** `9.0.0/us-core-individual-sex`, `9.0.0/us-core-sex`, `9.0.0/us-core-patient`.
- **Pass if:** it names `us-core-individual-sex` with a Coding value and says `us-core-sex` is
  deprecated.
- **Fail if:** it recommends `us-core-sex` or `us-core-birthsex` for 9.0.0.
- **Skill:** `SKILL.md` Patient demographics extensions.

### LK-03. Gender identity

- **Expected:** `us-core-genderIdentity` is retired and deprecated in 9.0.0, is no longer in the
  Patient profile, and SHOULD NOT be used for new content. Use the HL7 extension
  `http://hl7.org/fhir/StructureDefinition/individual-genderIdentity`, a complex extension with a
  `value` sub-extension.
- **Source:** `9.0.0/us-core-genderIdentity` (Status Reason), `9.0.0/us-core-patient`.
- **Pass if:** it says the extension is deprecated and names `individual-genderIdentity`.
- **Fail if:** it says to keep using `us-core-genderIdentity`.
- **Skill:** `SKILL.md` Patient demographics extensions.

## Requirements

### RQ-01. Additional USCDI Requirements

- **Expected:** The element isn't Must Support or mandatory, but it represents a USCDI data element
  needed for ONC Health IT Certification. Implementers seeking certification SHALL treat it as Must
  Support (CONF-0083, CONF-0084). For anyone else it is optional.
- **Source:** Must Support page, Additional USCDI Requirements; `9.0.0/us-core-patient`.
- **Pass if:** it ties the flag to certification and says it is otherwise optional.
- **Fail if:** it says USCDI elements are always Must Support or mandatory.
- **Skill:** `SKILL.md` Requirements to apply.

### RQ-02. A missing mandatory status

- **Expected:** No. `Condition.clinicalStatus` has a required binding with no "unknown" code, so a
  code from the value set is needed, or the instance doesn't conform (CONF-0047). A DataAbsentReason
  code isn't allowed. US Core says a read of such a resource returns HTTP 404 with an
  OperationOutcome (CONF-0048), and a search leaves it out of the results.
- **Source:** General Requirements page, Missing Data.
- **Pass if:** it says no, explains why, and gives the 404 or exclusion behaviour.
- **Fail if:** it recommends sending `unknown` or a made-up status.
- **Skill:** `SKILL.md` Requirements to apply (Missing data).

### RQ-03. Text-only codes

- **Expected:** `AllergyIntolerance.code` (extensible): text only is allowed when there's no code
  (CONF-0042, CONF-0027). `AllergyIntolerance.clinicalStatus` (required): text only is not valid,
  and at least one coding must come from the value set (CONF-0018 to CONF-0020).
- **Source:** General Requirements page, Using Codes in US Core Profiles.
- **Pass if:** both are right.
- **Skill:** `SKILL.md` Requirements to apply.

## Versions

### VR-01. Unknown administrative gender

- **Expected:** 6.1.0: `Patient.gender` is 1..1 and Must Support with a required binding, so send
  the value set's `unknown` code. 9.0.0: `Patient.gender` is 0..1 and not Must Support, so leave it
  out (CONF-0078).
- **Source:** `6.1.0/us-core-patient`, `9.0.0/us-core-patient`; Missing Data.
- **Pass if:** both versions are right.
- **Fail if:** it uses a data-absent-reason extension for 6.1.0 (the value set has `unknown`), or
  sends `unknown` in 9.0.0 as though gender were still required.
- **Skill:** `SKILL.md` Patient demographics extensions, Requirements to apply.

### VR-02. New and removed profiles

- **Expected:** Added (any three): ADI DocumentReference, Observation ADI documentation, Average
  Blood Pressure, Care Experience Preference, Treatment Intervention Preference, Device,
  FamilyMemberHistory, Medication Adherence. Removed: Implantable Device; 9.0.0 has the general US
  Core Device Profile instead.
- **Source:** comparing `6.1.0/README` and `9.0.0/README`.
- **Pass if:** three real additions and Implantable Device.
- **Skill:** `SKILL.md` Other changes from 6.1.0 to 9.0.0.

## Tasks

### TK-01. A US Core 9.0.0 Patient

Grade the saved Patient with [grade_patient.py](grade_patient.py)
(`python grade_patient.py patient.json`), then read it.

- **Script checks** (each must pass):
  - An identifier with a system and the value `MRN-48213`, the name Maria Reyes, and birthDate
    1984-03-07.
  - `us-core-race` as a complex extension with `ombCategory` 2106-3 from
    `urn:oid:2.16.840.1.113883.6.238`, plus `text`.
  - `us-core-ethnicity` with `ombCategory` 2135-2, plus `text`.
  - `us-core-individual-sex` with `valueCoding` SNOMED CT 248152002.
  - `us-core-interpreter-needed` with a `valueCoding`.
  - HL7 `individual-genderIdentity` with a `value` sub-extension. Neither `us-core-sex` nor
    `us-core-genderIdentity` is used.
  - No `gender` and no `_gender`.
- **Read for:** the interpreter code, which should come from the extension's required value set.
  The package's example Patient uses SNOMED CT 373066001.
- **Fail if:** the script fails.
- **Skill:** `SKILL.md` Patient demographics extensions, Requirements to apply.
