# questionnaire Skill Trigger Prompts

Prompts for checking when the `questionnaire` skill loads. Run each one in a fresh session with the
skill installed and no other instructions, and record whether it loaded.

## Should load the skill

1. Build a FHIR Questionnaire for a PHQ-9 depression screen.
2. Pre-fill this Questionnaire's weight item from the patient's latest Observation with CQL.
3. Why does $populate on our HAPI server return an empty QuestionnaireResponse?
4. Which SDC extension makes an item's answer a calculated value?
5. Turn this completed QuestionnaireResponse into Observations with $extract.
6. Show this question only when the previous answer is "yes".

## Should not load the skill

1. Write a PlanDefinition that proposes an HbA1c test for adults.
2. Write the CQL for "most recent body weight".
3. Encode this CQL library as a FHIR Library resource.
4. What are the cardinalities of the Observation resource's elements in R4?
5. Write a FSH profile of Observation.

In the should-not list, prompt 1 belongs to the `plan-definition` skill, prompt 2 to `cql`, prompt 3 to
`cql-ig`, prompt 4 to `fhir` and prompt 5 to `fsh`.
