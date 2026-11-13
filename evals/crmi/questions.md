# CRMI Skill Test Questions

Questions that check whether an agent answers from the current CRMI 2.0.0 and FHIR Extensions (R4)
5.4.0 definitions, rather than from memory of earlier versions. The answer key is in
[answers.md](answers.md). Keep it out of any copy of the skill given to an agent under test.

Answer for CRMI 2.0.0 and FHIR Extensions (R4) 5.4.0 unless a question says otherwise. Give
canonical URLs in full, cardinalities as `min..max`, and say which IG and version each answer comes
from.

## Versions

### VR-01. An older CPG profile

Our IG's PlanDefinitions and Libraries claim `cpg-publishableplandefinition` and
`cpg-publishablelibrary`. Are those current profiles? What should the artifacts claim instead?

## Profiles

### PR-01. A shareable Library

Which elements does `crmi-shareablelibrary` require, and with what cardinality? Is `name`
required?

### PR-02. Publishable without shareable

A Library claims only `crmi-publishablelibrary`. Must it have a `url` and a `version`? Which
elements does that profile require on its own?

## Extensions

### EX-01. Knowledge capability

What's the canonical URL of the extension that declares an artifact's knowledge capability, what
type is its value, and which values are allowed?

### EX-02. Copyright label

Which extension carries a short copyright label for an artifact, and what is its value type? Does
`crmi-publishablelibrary` mark it mustSupport?

## Operations

### OP-01. $package

What's the canonical URL of CRMI's `$package` operation? Can it be invoked at the system, type and
instance levels? What does it return, and what is the first resource in the result?

## Tasks

### TK-01. A shareable, publishable logic library

Write a FHIR R4 Library resource, as JSON, for a CQL logic library named `DiabetesScreening`,
version `1.0.0`, with canonical URL `http://example.org/fhir/Library/DiabetesScreening`. It must
conform to both the CRMI 2.0.0 shareable and publishable Library profiles, declare those two
knowledge capabilities with the knowledge capability extension, and include its CQL source as
`text/cql` content. Save it as `library.json`.
