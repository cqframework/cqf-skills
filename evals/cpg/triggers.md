# CPG Skill Trigger Prompts

Prompts for checking when the `cpg` skill loads. Run each one in a fresh session with the skill
installed and no other instructions, and record whether the skill loaded.

## Should load the skill

1. What's the difference between cpg-recommendationdefinition and cpg-strategydefinition?
2. Which extensions does CPG use to express the strength and direction of a recommendation?
3. How do I define a case feature in CPG?
4. Write a PlanDefinition that conforms to the CPG recommendation definition profile.
5. Our guideline still claims cpg-shareableplandefinition. Is that still in CPG?
6. What can a CPG recommendation's action definition point to?
7. Which values does the cqf-knowledgeRepresentationLevel extension allow?

## Should not load the skill

1. What does CRMI's $package operation return?
2. What's the cardinality of Observation.subject in base FHIR R4?
3. Write a CQL expression for the measurement period.
4. Which elements does the US Core Patient profile require?
5. Fix the syntax error in this FHIR Shorthand (FSH) file.
6. Write a transaction bundle that upserts a Patient.

In the should-not list, prompt 1 belongs to the `crmi` skill and prompt 2 to the `fhir` skill. In
the should-load list, prompt 5 may also load `crmi`, which is fine.
