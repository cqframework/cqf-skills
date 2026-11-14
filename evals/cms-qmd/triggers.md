# CMS QMD Skill Trigger Prompts

Prompts for checking when the `cms-qmd` skill loads. Run each one in a fresh session with the skill
installed and no other instructions, and record whether the skill loaded.

## Should load the skill

1. How should a CMS eCQM decide a condition was active during the measurement period?
2. Review this CMS measure CQL for pattern problems.
3. What are the logic layers for CMS measure CQL?
4. Which CQMElements function gives hospitalization length of stay?
5. How do I refactor a QI-Core measure to US Quality Core?
6. Should my measure use a negation profile for "no statin ordered"?

## Should not load the skill

1. Which US Quality Core profiles must a server support?
2. What's the primary code path for MedicationRequest in the base FHIR ModelInfo?
3. Write CQL that finds active conditions using USCoreElements.
4. Package this CQL library as a FHIR Library resource.
5. What does the CQL `properly includes` operator return for intervals with open boundaries?
6. Fix this JavaScript build error.

In the should-not list, prompt 1 belongs to the `usqualitycore` skill, prompts 2 and 4 to `cql-ig`,
prompt 3 to `us-cql-ig` and prompt 5 to `cql`.
