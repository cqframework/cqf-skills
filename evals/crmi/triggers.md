# CRMI Skill Trigger Prompts

Prompts for checking when the `crmi` skill loads. Run each one in a fresh session with the skill
installed and no other instructions, and record whether the skill loaded.

## Should load the skill

1. Which profile should a shareable PlanDefinition claim under CRMI?
2. What's the canonical URL of the cqf-knowledgeCapability extension?
3. What does CRMI's $package operation return?
4. Which elements does crmi-publishablelibrary mark as mustSupport?
5. Our IG still uses cpg-publishablelibrary. What should it use now?
6. Does a publishable Library also have to be shareable?
7. Write a Library that conforms to the CRMI shareable and publishable profiles.

## Should not load the skill

1. What's the cardinality of Observation.subject in base FHIR R4?
2. What's the difference between cpg-recommendationdefinition and cpg-strategydefinition?
3. Write a CQL expression for the measurement period.
4. Which elements does the US Core Patient profile require?
5. Fix the syntax error in this FHIR Shorthand (FSH) file.
6. Write a transaction bundle that upserts a Patient.

In the should-not list, prompt 1 belongs to the `fhir` skill and prompt 2 to the `cpg` skill.
