# US CQL IG Skill Trigger Prompts

Prompts for checking when the `us-cql-ig` skill loads. Run each one in a fresh session with the
skill installed and no other instructions, and record whether the skill loaded.

## Should load the skill

1. Write CQL that finds a patient's active confirmed problem list items using USCoreElements.
2. What `using` declaration do I need for the USCore model in CQL?
3. How do I get a patient's race in CQL against US Core?
4. Why does `[BloodPressureProfile: "BP Codes"]` give a warning about a primary code path?
5. Which USCoreCommon function returns the patient's sex?
6. How do I name definitions in a shared US Core CQL library?
7. What does CumulativeMedicationDuration compute?

## Should not load the skill

1. Which elements are Must Support in the US Core Patient profile?
2. What does FHIRCommon's isActive() check on a Condition?
3. What does the CQL `properly includes` operator return for intervals with open boundaries?
4. Package this CQL library as a FHIR Library resource.
5. Write a FSH profile of Observation.
6. Fix this Python script that parses JSON.

In the should-not list, prompt 1 belongs to the `uscore` skill, prompts 2 and 4 to `cql-ig`,
prompt 3 to `cql` and prompt 5 to `fsh`.
