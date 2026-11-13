# FHIR Skill Test Questions: Answer Key

Expected answers for [questions.md](questions.md). Don't give this file to an agent under test.

Each answer gives the expected facts, the source that decides them, what a passing answer must and
must not say, and where the skill covers it ("Skill"), for tracing a failed answer to a gap. Facts
come from the R4 (4.0.1) definitions. The skill's element tables under
`skills/fhir/resources/profiles/r4/` are generated from `hl7.fhir.r4.core@4.0.1`. A table row is
written here as `Resource.element card type flags binding`.

An answer fails if it gives a cardinality, type or binding from another FHIR version (most often
R5) or from an IG profile as the base R4 rule, or if it invents an invariant.

## Element definitions

### EL-01. Encounter class

- **Expected:** `Encounter.class` is `1..1` `Coding` (a single Coding, not a CodeableConcept and
  not a list), with an extensible binding to `v3-ActEncounterCode`. Inpatient:
  `"class": { "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "IMP" }`.
- **Source:** `Encounter.class 1..1 Coding summary extensible→v3-ActEncounterCode`.
- **Pass if:** it says `1..1 Coding` and writes `class` as a single object.
- **Fail if:** it writes `class` as an array or a CodeableConcept (the R5 shape is
  `0..* CodeableConcept`), or says it's optional.
- **Skill:** `resources/profiles/r4/Encounter.md`; example in `resources/profiles.md`.

### EL-02. A minimal Observation

- **Expected:** only `status` (`1..1 code`, required binding to `observation-status`) and `code`
  (`1..1 CodeableConcept`). `subject` is `0..1` in base R4, so it isn't required. Profiles such as
  US Core make it required.
- **Source:** `Observation.status 1..1 code modifier summary required→observation-status@4.0.1`,
  `Observation.code 1..1 CodeableConcept`, `Observation.subject 0..1`.
- **Pass if:** it names exactly `status` and `code`, and says `subject` is optional in base R4.
- **Fail if:** it lists `subject`, `effective[x]` or `category` as required by base R4.
- **Skill:** `resources/profiles/r4/Observation.md`.

### EL-03. A minimal MedicationRequest

- **Expected:** `status` (`1..1`, modifier), `intent` (`1..1`, modifier), `medication[x]` (`1..1`,
  `CodeableConcept` or `Reference(Medication)`) and `subject` (`1..1`,
  `Reference(Patient | Group)`). `status` and `intent` are the modifiers.
- **Source:** `MedicationRequest.status 1..1 code modifier`, `MedicationRequest.intent 1..1 code
  modifier`, `MedicationRequest.medication[x] 1..1 CodeableConcept, Reference(Medication)`,
  `MedicationRequest.subject 1..1 Reference(Patient | Group)`.
- **Pass if:** it names all four and identifies `status` and `intent` as modifiers.
- **Fail if:** it misses `intent` or `subject`, or calls `authoredOn` required (it's `0..1`).
- **Skill:** `resources/profiles/r4/MedicationRequest.md`.

### EL-04. Condition status rules

- **Expected:** No. `con-5` (error): "Condition.clinicalStatus SHALL NOT be present if verification
  Status is entered-in-error". For an abated condition, `con-4` (error) requires `clinicalStatus`
  to be `inactive`, `resolved` or `remission`. `clinicalStatus` and `verificationStatus` are both
  modifiers with required bindings.
- **Source:** `Condition.md` Invariants: `con-4`, `con-5`. (`con-3`, a warning, requires
  `clinicalStatus` on a problem-list item unless it was entered in error.)
- **Pass if:** it answers no, citing `con-5`, and gives the three values, citing `con-4`.
- **Fail if:** it allows `active`, `recurrence` or `relapse` for an abated condition.
- **Skill:** `resources/profiles/r4/Condition.md`.

### EL-05. Immunization status and date

- **Expected:** `status` codes are `completed`, `entered-in-error` and `not-done` (required
  binding, modifier). The administration date is `occurrence[x]`, `1..1`, either `dateTime` or
  `string`.
- **Source:** `Immunization.status 1..1 code modifier summary required→immunization-status@4.0.1`,
  `Immunization.occurrence[x] 1..1 dateTime, string`.
- **Pass if:** it gives the three codes with `not-done` hyphenated, and `occurrence[x]` as required
  with both types.
- **Fail if:** it names `date` or `occurrenceDateTime` as the only form, or says the date is
  optional.
- **Skill:** `resources/profiles/r4/Immunization.md`.

### EL-06. Choice elements

- **Expected:** `Procedure.performed[x]`: `dateTime`, `Period`, `string`, `Age`, `Range`.
  `Patient.deceased[x]`: `boolean` or `dateTime`. Yes, it's a modifier.
- **Source:** `Procedure.performed[x] 0..1 dateTime, Period, string, Age, Range`,
  `Patient.deceased[x] 0..1 boolean, dateTime modifier summary`.
- **Pass if:** both type lists are complete and exact, and it says `deceased[x]` is a modifier.
- **Skill:** `resources/profiles/r4/Procedure.md`, `resources/profiles/r4/Patient.md`.

### EL-07. Coverage

- **Expected:** `status` `1..1` (modifier, required binding to `fm-status`), `beneficiary` `1..1`
  `Reference(Patient)`, and `payor` `1..*` `Reference(Organization | Patient | RelatedPerson)`.
- **Source:** `Coverage.status 1..1`, `Coverage.beneficiary 1..1`, `Coverage.payor 1..*`.
- **Pass if:** it names all three with their cardinalities, `payor` as `1..*`.
- **Skill:** `resources/profiles/r4/Coverage.md`.

## Bundles

### BD-01. Request entries

- **Expected:** `request` is required in `batch`, `transaction` and `history` bundles and is not
  allowed in any other type (`bdl-3`, error). So the `collection` bundle is invalid. Likewise,
  `response` is required in `batch-response`, `transaction-response` and `history` (`bdl-4`).
- **Source:** `Bundle.md` Invariants: `bdl-3`: "entry.request mandatory for
  batch/transaction/history, otherwise prohibited".
- **Pass if:** it names the three types, says the collection bundle is invalid, and cites `bdl-3`
  or quotes its rule.
- **Fail if:** it says `request` is only ignored in a collection.
- **Skill:** `SKILL.md` Bundle Types; `resources/profiles/r4/Bundle.md`.

### BD-02. Creating resources that reference each other

- **Expected:** Give each new resource a `fullUrl` of `urn:uuid:<uuid>` and a `request` of
  `POST` to the resource type (`Patient`, `Condition`). Write the Condition's `subject.reference`
  as the Patient entry's `urn:uuid:` fullUrl. The server assigns ids and rewrites matching
  references in the bundle to the new ids.
- **Source:** R4 Bundle, "Resource URL & Uniqueness rules in a bundle": "For transactions and
  batches, entries MAY not have fullURLs when the entry.request.method = POST, and the resource has
  no identity. Note that even in this case, there may still be a fullURL in a transaction on a POST
  so that relationships between resources can be represented"
  (<https://hl7.org/fhir/R4/bundle.html>). R4 RESTful API, transaction processing: "When
  processing a "POST" (create), the full URL is treated as the id of the resource on the source,
  and is ignored; the server generates an id for the resource", and "Servers SHALL replace all
  matching links in the bundle" (<https://hl7.org/fhir/R4/http.html>).
- **Pass if:** it uses `urn:uuid:` fullUrls, `POST`, and a `urn:uuid:` reference, and says the
  server rewrites the reference.
- **Fail if:** it references `Patient/<id>` for an id the server hasn't assigned yet, or says a
  POST entry must not have a fullUrl.
- **Skill:** gap. `SKILL.md` covers PUT upserts with `{ResourceType}/{id}` fullUrls and relative
  references, but not `urn:uuid:` references for server-assigned ids. A miss here points at that
  gap, not at the agent.

### BD-03. Document bundles

- **Expected:** an `identifier` with both `system` and `value` (`bdl-9`), a `timestamp`
  (`bdl-10`), and a Composition as the first entry's resource (`bdl-11`). Every entry has a
  `fullUrl`, and none has `request` (`bdl-3`).
- **Source:** `Bundle.md` Invariants: `bdl-9`, `bdl-10`, `bdl-11`, `bdl-3`.
- **Pass if:** it names the identifier, the timestamp and the first-entry Composition.
- **Fail if:** it names only the Composition.
- **Skill:** `SKILL.md` Bundle Types (the Composition only); `resources/profiles/r4/Bundle.md`.

### BD-04. fullUrl rules

- **Expected:** Not normally. `bdl-7` requires fullUrls to be unique, unless entries with the same
  fullUrl have different `meta.versionId` (and history bundles are exempt). No: `bdl-8` says
  "fullUrl cannot be a version specific reference", so `/_history/` isn't allowed.
- **Source:** `Bundle.md` Invariants: `bdl-7`, `bdl-8`.
- **Pass if:** it gives both rules, including the `versionId` exception.
- **Skill:** `resources/profiles/r4/Bundle.md`.

## Tasks

### TK-01. A transaction bundle

Grade the saved bundle with [grade_bundle.py](grade_bundle.py), then grade the explanation.

- **Script checks** (each must pass):
  - `type` is `transaction`, with exactly four entries: Patient, Encounter, Condition and
    Observation.
  - Each entry has a `resource`, a `fullUrl` and a `request`. `request.method` is `PUT` and
    `request.url` is `{ResourceType}/{id}`.
  - Each `fullUrl` ends in `{ResourceType}/{id}` (or is `urn:uuid:{id}`), and fullUrls are unique.
  - Each resource id is a UUID.
  - Every reference resolves to another entry in the bundle.
  - Required base R4 elements are present: `Encounter.status` and `Encounter.class`, with `class` a
    single Coding object. `Condition.subject`. `Observation.status` and `Observation.code`.
  - The values asked for: `Encounter.status` `finished` with class `IMP`. Condition clinical
    status `active` and verification status `confirmed`, with `encounter` set. Observation status
    `final`, with code `4548-4`.
- **Explanation:** says how the ids were made reproducible, for example name-based UUIDs
  (`uuid.uuid5`) from a fixed namespace and a stable key per resource.
- **Fail if:** the script fails, or the ids are random UUIDs (`uuid4`) or sequential integers.
- **Skill:** `SKILL.md` Transaction Bundle Entry Pattern and Resource ID Conventions;
  `resources/profiles.md`.
