# FSH Skill Test Questions

Questions that check whether an agent writes FHIR Shorthand that follows the FSH 3.0.0
specification and compiles cleanly with SUSHI 3.x. The answer key is in [answers.md](answers.md).
Keep it out of any copy of the skill given to an agent under test.

Answer for FSH 3.0.0 and FHIR R4. Give FSH rules exactly as you would write them in a `.fsh` file.

## Syntax

### SY-01. Assigning a code in a profile

In a profile of Observation, what does `* code = http://loinc.org#85354-9` put in the generated
StructureDefinition? How would you instead require that `code` contain exactly that coding and
nothing else, and is that a good idea?

### SY-02. Several reference targets

Write the rule that restricts `Observation.subject` in a profile to a Patient or a Group.

### SY-03. A standard extension in a profile

Write the rule that adds `http://hl7.org/fhir/StructureDefinition/patient-birthPlace` to a Patient
profile as an optional, must-support extension, and then the rule in an instance of that profile
that sets the city to Lisbon.

### SY-04. Repeating elements in an instance

In a Patient instance, write rules for two names, "Ana Silva" and "Ana Souza", without numeric
array indices.

### SY-05. A comma in a rule set argument

A parameterized rule set `Note(text)` contains `* note[+].text = "{text}"`. How do you insert it
with the text `one, two (draft)`?

### SY-06. Instance usage

You define a SearchParameter as an `Instance` in your FSH project. What `Usage` should it have,
and what is the default?

### SY-07. A FHIRPath extension context

Write the declaration and keywords for an extension `AssertedBy` that may be used on the `code`
element of a Condition or an Observation, given as a single FHIRPath context.

## Debugging

### DB-01. A SUSHI build with errors

SUSHI reports errors for this profile. What is wrong, and what is the corrected FSH?

```
Extension: ReviewedBy
Id: reviewed-by
Context: Observation
* value[x] only Reference(Practitioner)

Profile: ReviewedObservation
Parent: Observation
Id: reviewed-observation
* extension contains ReviewedBy 0..1
* component contains systolic 1..1
* component[systolic].code = http://loinc.org#8480-6
* subject only Reference(Patient) or Reference(Group)
```

## Tasks

### TK-01. A blood pressure profile

Write a FSH project for FHIR R4 with canonical `http://example.org/fhir/fsh-eval` that defines:

- a code system with id `bp-method` and codes `auto` ("Automated cuff") and `manual` ("Manual
  auscultation"), and a value set with id `bp-method` containing all its codes
- an extension with id `reviewed-by`, used on Observation, whose value is a reference to a
  Practitioner
- a profile of Observation with id `simple-bp`, in which:
  - `code` is LOINC `85354-9`
  - `subject` is required and references only a Patient
  - `method` is required and bound to the `bp-method` value set with required strength
  - the `reviewed-by` extension is allowed at most once and is must-support
  - `component` is sliced by `code`, with exactly one systolic (LOINC `8480-6`) and exactly one
    diastolic (LOINC `8462-4`) component, each with a `valueQuantity` in UCUM `mm[Hg]`
- an example instance of the profile with id `example-bp`, with a reading of 120/80 mm[Hg]

Save the FSH under `input/fsh/` with a `sushi-config.yaml`, and run SUSHI if you can.
