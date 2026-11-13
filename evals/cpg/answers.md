# CPG Skill Test Questions: Answer Key

Expected answers for [questions.md](questions.md). Don't give this file to an agent under test.

Facts come from the packages `hl7.fhir.uv.cpg` 2.0.0 and `hl7.fhir.uv.extensions.r4` 5.4.0, as
rendered in the `cpg` skill's knowledge base (`resources/profiles/concise/`, built by
`scripts/build-kb.sh`). A source written as `cpg_StructureDefinition-cpg-recommendationdefinition`
is the file `hl7.fhir.uv.cpg_StructureDefinition-cpg-recommendationdefinition.md` there. VR-01 also
relies on CRMI 2.0.0 (`hl7.fhir.uv.crmi`). Each answer gives the expected facts, the source, what a
passing answer must and must not say, and where the skill covers it ("Skill").

An answer fails if it presents a CPG 1.0.0 profile as current, invents a profile, extension or
code, or gives a canonical URL that doesn't match the package.

## Versions

### VR-01. Moving a recommendation to CPG 2.0.0

- **Expected:** `cpg-recommendationdefinition` exists in CPG 2.0.0; `cpg-shareableplandefinition`
  doesn't (CPG 2.0.0 dropped CPG 1.0.0's shareable and publishable artifact profiles). Claim
  `http://hl7.org/fhir/uv/crmi/StructureDefinition/crmi-shareableplandefinition` from CRMI 2.0.0
  instead, alongside `cpg-recommendationdefinition`.
- **Source:** `cpg_StructureDefinition-cpg-recommendationdefinition`; no `cpg-shareable*` file in
  the CPG 2.0.0 KB.
- **Pass if:** it keeps `cpg-recommendationdefinition` and replaces the shareable profile with the
  CRMI one.
- **Fail if:** it says both CPG profiles are current, or drops the recommendation profile.
- **Skill:** `SKILL.md` Versions.

## Profiles

### PR-01. Recommendation, strategy and pathway

- **Expected:** All three derive from `cpg-computableplandefinition`, which requires `type` `1..1`
  (mustSupport) and `action` `1..*` (mustSupport). They differ in the pattern on
  `PlanDefinition.type` (system `http://terminology.hl7.org/CodeSystem/plan-definition-type`):
  `cpg-recommendationdefinition` is `eca-rule`, `cpg-strategydefinition` is `workflow-definition`,
  and `cpg-pathwaydefinition` is `clinical-protocol`.
- **Source:** `cpg_StructureDefinition-cpg-recommendationdefinition`,
  `cpg_StructureDefinition-cpg-strategydefinition`, `cpg_StructureDefinition-cpg-pathwaydefinition`
  (Base and Pattern), `cpg_StructureDefinition-cpg-computableplandefinition`.
- **Pass if:** it gives all three type codes correctly and the common base.
- **Skill:** `SKILL.md` Reading a rendering; KB lookup.

### PR-02. What a recommendation's action can point to

- **Expected:** In `cpg-recommendationdefinition`, `action.definition[x]` is `0..1`
  `canonical(cpg-computableactivity | cpg-ordersetdefinition)`, mustSupport. In
  `cpg-computableplandefinition` it is
  `canonical(ActivityDefinition | PlanDefinition | Questionnaire), uri`. So a recommendation's
  action points to a CPG computable activity or order set definition, not to any PlanDefinition,
  Questionnaire or uri.
- **Source:** the `PlanDefinition.action.definition[x]` rows of both profiles.
- **Pass if:** it gives both type lists and the narrowing.
- **Skill:** KB lookup.

### PR-03. Rating a recommendation

- **Expected:** Four mustSupport extensions on `PlanDefinition.action`, each `0..1`:
  - `strengthOfRecommendation`:
    `http://hl7.org/fhir/StructureDefinition/cqf-strengthOfRecommendation` (FHIR Extensions), a
    CodeableConcept with an example binding to `recommendation-strength`.
  - `directionOfRecommendation`:
    `http://hl7.org/fhir/uv/cpg/StructureDefinition/cpg-directionOfRecommendation` (CPG), a
    CodeableConcept with a required binding to `cpg-recommendation-direction-vs`: `for` or
    `against`.
  - `qualityOfEvidence`: `http://hl7.org/fhir/StructureDefinition/cqf-qualityOfEvidence` (FHIR
    Extensions), a CodeableConcept with an example binding to `evidence-quality`.
  - `rating`: `http://hl7.org/fhir/uv/cpg/StructureDefinition/cpg-rating` (CPG), a Quantity, Range
    or Ratio.
- **Source:** `cpg_StructureDefinition-cpg-recommendationdefinition` (action extension slices),
  each extension's file, `cpg_CodeSystem-cpg-recommendation-direction-cs`.
- **Pass if:** it gives the strength, direction and quality extensions with correct URLs (the
  `cqf-` ones from FHIR Extensions, the direction one from CPG) and the codes `for` and `against`.
- **Fail if:** it gives a `cpg-` URL for strength or quality, or a `cqf-` URL for direction.
- **Skill:** KB lookup.

### PR-04. Case feature definitions

- **Expected:** `cpg-casefeaturedefinition`
  (`http://hl7.org/fhir/uv/cpg/StructureDefinition/cpg-casefeaturedefinition`) profiles
  StructureDefinition: a case feature is defined as a profile. It fixes
  `StructureDefinition.kind` to `resource` and `StructureDefinition.derivation` to `constraint`.
- **Source:** `cpg_StructureDefinition-cpg-casefeaturedefinition` (Base, Element Details).
- **Pass if:** it says the base is StructureDefinition and gives both fixed values.
- **Skill:** KB lookup.

## Extensions

### EX-01. Knowledge representation level

- **Expected:** `http://hl7.org/fhir/StructureDefinition/cqf-knowledgeRepresentationLevel` (FHIR
  Extensions 5.4.0), `valueCode` `1..1`, required binding to `knowledge-representation-level`:
  `narrative`, `semi-structured`, `structured` and `executable`.
- **Source:** `extensions.r4_StructureDefinition-cqf-knowledgeRepresentationLevel`,
  `extensions.r4_CodeSystem-knowledge-representation-level`.
- **Pass if:** the URL and all four codes are correct.
- **Skill:** KB lookup.

## Tasks

### TK-01. A recommendation definition

Grade the saved PlanDefinition with [grade_plandefinition.py](grade_plandefinition.py), then read
it.

- **Script checks** (each must pass):
  - `resourceType` is `PlanDefinition`, and `meta.profile` claims
    `http://hl7.org/fhir/uv/cpg/StructureDefinition/cpg-recommendationdefinition` and no CPG 1.0.0
    shareable or publishable profile.
  - `type` has the coding `http://terminology.hl7.org/CodeSystem/plan-definition-type` `eca-rule`.
  - `status` is a publication-status code.
  - `library` includes `http://example.org/fhir/Library/DiabetesScreening`.
  - At least one action. The action has a `cpg-directionOfRecommendation` extension with code
    `for`, and `definitionCanonical`
    `http://example.org/fhir/ActivityDefinition/OfferDiabetesScreening`.
- **Fail if:** the script fails.
- **Skill:** `SKILL.md` Versions; KB lookup of `cpg-recommendationdefinition` and
  `cpg-directionOfRecommendation`.
