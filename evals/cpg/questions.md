# CPG Skill Test Questions

Questions that check whether an agent answers from the current CPG 2.0.0 and FHIR Extensions (R4)
5.4.0 definitions, rather than from memory of CPG 1.0.0. The answer key is in
[answers.md](answers.md). Keep it out of any copy of the skill given to an agent under test.

Answer for CPG 2.0.0 and FHIR Extensions (R4) 5.4.0 unless a question says otherwise. Give canonical
URLs in full, cardinalities as `min..max`, and say which IG and version each answer comes from.

## Versions

### VR-01. Moving a recommendation to CPG 2.0.0

A recommendation PlanDefinition built against CPG 1.0.0 claims `cpg-shareableplandefinition` and
`cpg-recommendationdefinition`. Which of those exist in CPG 2.0.0, and what should it claim
instead of the one that doesn't?

## Profiles

### PR-01. Recommendation, strategy and pathway

What distinguishes `cpg-recommendationdefinition`, `cpg-strategydefinition` and
`cpg-pathwaydefinition`, and what do they share?

### PR-02. What a recommendation's action can point to

What may `PlanDefinition.action.definition[x]` reference in `cpg-recommendationdefinition`, and how
does that differ from `cpg-computableplandefinition`?

### PR-03. Rating a recommendation

Which extensions does `cpg-recommendationdefinition` mark mustSupport on `PlanDefinition.action` for
expressing the strength, direction and evidence of a recommendation? Give each canonical URL. Which
values may the direction take?

### PR-04. Case feature definitions

What does `cpg-casefeaturedefinition` profile, and which values does it fix?

## Extensions

### EX-01. Knowledge representation level

Which extension records the knowledge representation level of an artifact, and what are its
allowed values?

## Tasks

### TK-01. A recommendation definition

Write a FHIR R4 PlanDefinition, as JSON, that conforms to the CPG 2.0.0 recommendation definition
profile. It recommends offering diabetes screening to adults with risk factors, uses logic from
the Library `http://example.org/fhir/Library/DiabetesScreening`, and has one action whose
direction of recommendation is "for" and whose definition is the ActivityDefinition
`http://example.org/fhir/ActivityDefinition/OfferDiabetesScreening`. Save it as
`plandefinition.json`.
