# CQL IG Skill Trigger Prompts

Prompts for checking when the `cql-ig` skill loads. Run each one in a fresh session with the skill
installed and no other instructions, and record whether the skill loaded.

## Should load the skill

1. How do I package this CQL library as a FHIR Library resource?
2. What does FHIRCommon's isActive() check on a Condition?
3. Which relatedArtifact entries does a CQL Library resource need?
4. What's the primary code path for MedicationRequest in the FHIR ModelInfo?
5. How is an empty list returned from Library/$evaluate?
6. Can my CQL library name contain underscores if it's used in a FHIR artifact?
7. Which translator options should I use when publishing CQL with FHIR?

## Should not load the skill

1. What does the CQL `properly includes` operator return for intervals with open boundaries?
2. Is patient-genderIdentity still the extension to use?
3. Write a FSH profile of Observation.
4. Which profile should a shareable PlanDefinition claim under CRMI?
5. What's the cardinality of Observation.subject in base FHIR R4?
6. Fix this Python script that parses JSON.

In the should-not list, prompt 1 belongs to the `cql` skill, prompt 2 to `fhir-extensions`,
prompt 3 to `fsh`, prompt 4 to `crmi` and prompt 5 to `fhir`.
