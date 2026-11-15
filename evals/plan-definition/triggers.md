# plan-definition Skill Trigger Prompts

Prompts for checking when the `plan-definition` skill loads. Run each one in a fresh session with the
skill installed and no other instructions, and record whether the skill loaded.

## Should load the skill

1. Write a PlanDefinition ECA rule that proposes a flu vaccine for adults who haven't had one this season.
2. Why did $apply return all three options of my exactly-one group?
3. What does PlanDefinition/$apply return on a HAPI FHIR server?
4. How do I set a dynamicValue on the RequestGroup action instead of the ServiceRequest?
5. My ActivityDefinition $apply gives intent `order`; I wanted a proposal.
6. Test my PlanDefinition locally against a sample patient.

## Should not load the skill

1. Which CPG profile should a recommendation PlanDefinition claim, and what does it require?
2. Package this PlanDefinition and its dependencies with $package.
3. Write the CQL for "no HbA1c in the last 6 months".
4. Encode this CQL library as a FHIR Library resource.
5. Write a FSH profile of PlanDefinition.

In the should-not list, prompt 1 belongs to the `cpg` skill, prompt 2 to `crmi`, prompt 3 to `cql`,
prompt 4 to `cql-ig` and prompt 5 to `fsh`.
