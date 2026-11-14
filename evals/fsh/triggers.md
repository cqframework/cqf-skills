# FSH Skill Trigger Prompts

Prompts for checking when the `fsh` skill loads. Run each one in a fresh session with the skill
installed and no other instructions, and record whether the skill loaded.

## Should load the skill

1. Write a FSH profile of Observation that requires a systolic and a diastolic component.
2. SUSHI says "Inline extensions should only be defined in Extensions". What's wrong?
3. How do I add the patient-birthPlace extension to my Patient profile in FHIR Shorthand?
4. Convert this ValueSet JSON to FSH.
5. What's the difference between `=` and `(exactly)` in a FSH profile?
6. How do I pass a value with a comma to a parameterized RuleSet?
7. Which fields does sushi-config.yaml need?

## Should not load the skill

1. What's the cardinality of Observation.subject in base FHIR R4?
2. Is patient-genderIdentity still the extension to use?
3. Write a CQL expression for the measurement period.
4. Which profile should a shareable Library claim under CRMI?
5. Write a transaction bundle that upserts a Patient.
6. Fix this shell script that loops over files.

In the should-not list, prompt 1 belongs to the `fhir` skill, prompt 2 to the `fhir-extensions`
skill and prompt 4 to the `crmi` skill.
