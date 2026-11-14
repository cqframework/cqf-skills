# IG Publisher Skill Trigger Prompts

Prompts for checking when the `ig-publisher` skill loads. Run each one in a fresh session with the
skill installed and no other instructions, and record whether the skill loaded.

## Should load the skill

1. My IG build says "The IG Publisher was unable to find an ig.ini". What's wrong?
2. Why doesn't the IG Publisher compile the CQL in my input/cql folder?
3. How do I suppress a warning in qa.html?
4. Which parameters go in ig.ini and which in the ImplementationGuide resource?
5. My CI build of a FHIR IG passes even though the QA report has errors.
6. How do I make the publisher use our own terminology server?
7. After updating the template, my custom Liquid narrative for Measure isn't used.

## Should not load the skill

1. Write a FSH profile of Observation that requires a component.
2. What's the cardinality of Observation.subject in base FHIR R4?
3. Write a CQL expression for the measurement period.
4. Where is the FHIR ModelInfo for CQL published?
5. Which profile should a shareable Library claim under CRMI?
6. Fix this Jekyll site that won't build.

In the should-not list, prompt 1 belongs to the `fsh` skill, prompt 2 to the `fhir` skill, prompt 3
to the `cql` skill, prompt 4 to the `cql-ig` skill and prompt 5 to the `crmi` skill.
