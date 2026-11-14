# US CQL IG Skill Test Questions

Questions that check whether an agent writes CQL against US Core with the Common CQL Artifacts for
FHIR (US-Based) IG (`hl7.fhir.us.cql` 2.0.0): the USCore ModelInfo and the USCoreCommon and
USCoreElements libraries. The answer key is in [answers.md](answers.md). Keep it out of any copy of
the skill given to an agent under test.

Answer for `hl7.fhir.us.cql` 2.0.0 and US Core 6.1.0 unless a question says otherwise.

## Model

### MD-01. The using declaration

What `using` declaration does a library need to use this IG's US Core model, and what does the
`-derived` part of the version mean for the FHIR types and functions you can use?

### MD-02. Blood pressure by value set

An author writes `[BloodPressureProfile: "Blood Pressure Codes"]`. What does the translator do,
and how should the retrieve be written?

### MD-03. Class names

What do you write in a retrieve to get US Core Patient Profile resources, and US Core CareTeam
Profile resources?

### MD-04. US Core 9.0.0

Can this IG's libraries be used with the USCore model that US Core 9.0.0 publishes? Why or why
not?

## Libraries

### LB-01. Patient sex

Which USCoreCommon function should logic use to get a patient's sex so that it works for data
written to US Core 6.1.0 and to later versions, and how does it do that?

### LB-02. Race

How do you get a patient's OMB race categories in CQL with this IG, and why can't you write
`Patient.race`?

### LB-03. Problem list items

How does USCoreElements' `"Active Confirmed Problem List Items"` select its Conditions?

## Patterns

### PT-01. Naming

Following the IG's naming best practices, what is wrong with each of these names, and what would
be better: `"Conditions"` (unfiltered), `"BP"` (the most recent systolic value, as a Quantity),
`"Age"` (an Integer in years), `HeightCalc` (a non-fluent function)?

### PT-02. A syntax error

Why does `[USCore."AllergyIntolerance"].active()` fail to translate, and what are two ways to
write it?

## Tasks

### TK-01. A US Core library

Write a CQL library `HypertensionCheck` version `1.0.0` against the USCore model (6.1.0-derived)
that defines:

- `"Active Confirmed Hypertension Problems"`: Conditions conforming to the US Core Condition
  Problems and Health Concerns Profile with a code in the value set
  `http://example.org/fhir/ValueSet/essential-hypertension` (declare it as
  `"Essential Hypertension"`), whose clinical status is active and whose verification status is
  confirmed
- `"Final Blood Pressure Readings"`: US Core Blood Pressure observations with status `final`
- `"Most Recent Systolic Blood Pressure Quantity"`: the systolic value of the most recent of those
  readings
- `"Patient Race Categories"`: the patient's OMB race category codes

Include FHIRHelpers 4.0.1 and whatever other libraries you use. Save it as `HypertensionCheck.cql`.
