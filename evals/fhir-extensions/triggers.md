# FHIR Extensions Skill Trigger Prompts

Prompts for checking when the `fhir-extensions` skill loads. Run each one in a fresh session with
the skill installed and no other instructions, and record whether the skill loaded.

## Should load the skill

1. Is there a standard FHIR extension for a patient's place of birth?
2. What's the URL of the data-absent-reason extension, and how do I put it on birthDate?
3. Is patient-genderIdentity still the extension to use?
4. Which standard extensions can I use on Condition?
5. What value type does the condition-assertedDate extension take?
6. How is the patient-nationality extension structured?
7. Which FHIR extensions are deprecated, and what replaced them?

## Should not load the skill

1. What's the cardinality of Observation.subject in base FHIR R4?
2. Which extensions does the US Core Patient profile require?
3. Which profile should a shareable PlanDefinition claim under CRMI?
4. Write a CQL expression for the measurement period.
5. Fix the syntax error in this FHIR Shorthand (FSH) file.
6. Write a transaction bundle that upserts a Patient.

In the should-not list, prompt 1 belongs to the `fhir` skill and prompt 3 to the `crmi` skill.
Prompt 2 is about US Core's own profile, not the Extensions Pack.
