# US Quality Core Skill Trigger Prompts

Prompts for checking when the `usqualitycore` skill loads. Run each one in a fresh session with
the skill installed and no other instructions, and record whether the skill loaded.

## Should load the skill

1. Which US Quality Core profiles must a server support?
2. How do I record a procedure that wasn't done in US Quality Core?
3. What does the USCDI+ Quality flag mean?
4. What does QDM "Encounter, Performed" map to in US Quality Core?
5. Write CQL with `using USQualityCore version '0.5.0'` that retrieves inpatient encounters.
6. Is the Communication profile in scope for US Quality Core conformance?

## Should not load the skill

1. Which elements are Must Support in the US Core 9.0.0 Patient profile?
2. How should a CMS measure handle encounters with a condition, per the CMS QMD patterns?
3. What does FHIRCommon's isActive() check on a Condition?
4. Write a FSH profile of Observation.
5. What's the cardinality of Observation.subject in base FHIR R4?
6. Fix this Python script that parses JSON.

In the should-not list, prompt 1 belongs to the `uscore` skill, prompt 2 to `cms-qmd`, prompt 3 to
`cql-ig`, prompt 4 to `fsh` and prompt 5 to `fhir`.
