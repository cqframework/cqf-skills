# FHIR Skill Trigger Prompts

Prompts for checking when the `fhir` skill loads. Run each one in a fresh session with the skill
installed and no other instructions, and record whether the skill loaded.

## Should load the skill

1. Write a FHIR R4 transaction bundle that upserts a Patient and a Condition linked to it.
2. What's the cardinality of Observation.subject in FHIR R4?
3. Is Encounter.class a CodeableConcept or a Coding in R4?
4. My FHIR server rejects this bundle with "bdl-3". What does that mean?
5. How do I declare that a Patient resource conforms to a profile? Show me the meta.profile field.
6. Which binding strength does Condition.clinicalStatus have, and to which value set?
7. Should I use a relative reference or a urn:uuid reference between entries in my transaction
   bundle?
8. Generate synthetic FHIR test data for a patient with diabetes and an HbA1c result.

## Should not load the skill

1. Write a CQL expression that finds encounters during the measurement period.
2. Fix the syntax error in this FHIR Shorthand (FSH) profile definition.
3. What goes in `ig.ini` for the IG Publisher?
4. Explain the segments of an HL7 v2 ADT^A01 message.
5. Write a SQL query that counts patients by birth year.
6. What does the SMART on FHIR authorization flow look like for a backend service?

Prompts 2 and 3 name FHIR tooling that other skills cover. Loading the `fhir` skill there doesn't
make the answer wrong, but it shows the description is too broad.
