# US Core Skill Trigger Prompts

Prompts for checking when the `uscore` skill loads. Run each one in a fresh session with the skill
installed and no other instructions, and record whether the skill loaded.

## Should load the skill

1. Which elements are Must Support in the US Core Patient profile?
2. How do I record a patient's race in US Core?
3. What changed in US Core 9.0.0 for patient sex and gender identity?
4. What does the USCDI flag mean on a US Core element?
5. Which US Core profile should an encounter diagnosis use?
6. How do I send a mandatory US Core element when the value is unknown?
7. Check this Patient against US Core 6.1.0.

## Should not load the skill

1. Write CQL that finds active conditions using USCoreElements.
2. What's the cardinality of Observation.subject in base FHIR R4?
3. Is patient-genderIdentity from the FHIR Extensions Pack deprecated?
4. Write a FSH profile of Observation.
5. Package this CQL library as a FHIR Library.
6. Fix this JavaScript build error.

In the should-not list, prompt 1 belongs to the `us-cql-ig` skill, prompt 2 to `fhir`, prompt 3 to
`fhir-extensions`, prompt 4 to `fsh` and prompt 5 to `cql-ig`.
