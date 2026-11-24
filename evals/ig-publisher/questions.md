# IG Publisher Skill Test Questions

Questions that check whether an agent configures, runs and debugs the HL7 IG Publisher correctly at
IG Publisher 3.0.4 with cqf.fhir.template 1.0.0. The answer key is in [answers.md](answers.md). Keep
it out of any copy of the skill given to an agent under test.

## Configuration

### CF-01. A comment at the top of ig.ini

A developer adds `; Build settings for our IG` as the first line of a working `ig.ini`. The next
build stops with "The IG Publisher was unable to find an ig.ini". Why?

### CF-02. An unpinned template

An `ig.ini` says `template = cqf.fhir.template`. What version does the publisher use, and what
should it say instead? Does that also fix the version of fhir.base.template?

### CF-03. Where CQL comes from

A new IG on cqf.fhir.template puts its CQL in `input/cql`, like other measure IGs do. The build
compiles none of it and reports nothing about CQL. What's missing?

### CF-04. Adding a resource folder

An IG adds `path-resource` = `input/my-resources`. Does that stop the publisher loading resources from
the template's default folders such as `input/resources` and `input/examples`?

## The CQL loader

### CQ-01. Which translator

Which CQL-to-ELM translator version does IG Publisher 3.0.4 compile CQL with, and how do you find out
which publisher version built a given IG's output?

### CQ-02. Sub-folders

An IG has `path-binary` = `input/cql`, with libraries in `input/cql/measures/` and
`input/cql/helpers/`. What gets compiled? Is adding both sub-folders as `path-binary` a good fix?

### CQ-03. Inline CQL

Every Library in an IG has its CQL inline as base64 `data`. `qa.html` lists only "CQL source was not
associated with a library resource in the IG." for each `.cql` file. Does that mean the CQL compiles
cleanly? What will the published Libraries contain?

### CQ-04. An ig-loader attachment with a content type

A Library's content is `[{"id": "ig-loader-Screening.cql", "contentType": "text/cql"}]`. Does
IG Publisher 3.0.4 load the file into it? Would 3.0.1 have?

### CQ-05. "ELM generation failed"

The build log says "CQL Translation succeeded for file … but ELM generation failed with the following
error: Unknown FHIRTypes code 'Any'" for most libraries. `qa.html` shows no CQL error. What happened,
what is the effect, and what in the CQL tends to cause it?

## Running and QA

### RN-01. A green CI build with errors

A CI job runs `java -jar publisher.jar -ig .` and passes, but `qa.html` reports 40 errors. Why did it
pass, and how should the job fail on errors?

### RN-02. Suppressing an error

A developer adds an error's exact text, with a reason, to `input/ignoreWarnings.txt`. The next build
still counts it as an error. Is the file wrong?

### RN-03. After an upgrade

After moving an IG from IG Publisher 3.0.1 to 3.0.4, 72 warnings about the result type of an SDE
definition reappear, though `ignoreWarnings.txt` still has the line that hid them. What is the likely
cause, and how would you catch this after the next upgrade?

### RN-04. A proxy

A build behind a corporate proxy uses `-proxy=proxy.example.org:8080`, as the help text shows, and
still can't reach the internet. Why?

## Terminology and templates

### TX-01. A private terminology server

A team adds `-tx https://tx.example.org/fhir` to its build. With IG Publisher 3.0.4, what changes
besides which server is called?

### TX-02. Expansion parameters

An IG resource at `input/my-ig.xml` sets `path-expansion-params` to
`resources/parameters/expansion.json`. Which file does the publisher read?

### TX-03. Pinned versions

An IG sets `pin-canonicals` = `pin-all` and `pin-manifest` = `manifest`. Its input
`Parameters-manifest.json` has one parameter. Where are the versions the build pinned recorded?

### TP-01. A custom Measure narrative after a template upgrade

An IG has its own `Measure.liquid` in `input/my-liquid`, set as `path-liquid`. After upgrading from
`cqf.fhir.template#0.7.1` to `#1.0.0`, the Measure pages no longer use it. Why, and what are the
options?

### TP-02. Working on the template

A template maintainer points an IG at a local copy of the template they're changing
(`template = ../my-template` in `ig.ini`) and builds with IG Publisher 3.0.5. The build stops at once,
saying the template "runs scripts, and it is not a trusted template". It built with 3.0.4. Why, and what
do they do? Would `template = cqf.fhir.template#dev` run its scripts on the ci-build?

## Versions

### VR-01. A newer publisher

A team's `qa.txt` says "IG Publisher Version: 3.0.7". Someone asks whether an `ig-loader-`
attachment that carries a `contentType` still gets its CQL loaded. How should the answer be reached?

## Debugging

### DB-01. Review this set-up

An R4 measure IG fails to publish any ELM. Find every problem:

```ini
# Measure IG
[IG]
ig = input/measure-ig.xml
template = cqf.fhir.template
```

```xml
<!-- in input/measure-ig.xml, inside <definition> -->
<parameter>
  <code value="path-binary"/>
  <value value="input/cql"/>
</parameter>
```

The CQL is in `input/cql/libraries/Screening.cql`, which declares `library Screening`. The Library:

```json
{
  "resourceType": "Library",
  "id": "screening-logic",
  "url": "http://example.org/fhir/Library/screening-logic",
  "name": "Screening",
  "content": [ { "id": "ig-loader-Screening.cql", "data": "" } ]
}
```

The Measure has `"library": ["http://example.org/fhir/Library/screening-logic"]`.

## Task

### TK-01. Set up an IG that compiles a measure's CQL

Create a new folder `tk-01/` holding an R4 (FHIR 4.0.1) IG for IG Publisher 3.0.4 on the CQF
template, so that a build compiles the CQL and publishes it, with ELM, in the measure's Library:

- `ig.ini` and the ImplementationGuide resource (JSON or XML).
- `input/cql/ExampleScreening.cql`: a library named `ExampleScreening` using FHIR 4.0.1, with a
  "Measurement Period" parameter and "Initial Population", "Denominator" and "Numerator" definitions
  for adults with a body weight Observation (LOINC 29463-7) in the measurement period.
- A Library resource for it and a proportion Measure that uses it, under `input/resources/`.
- `input/ignoreWarnings.txt`, suppressing, with a reason, the three warnings the validator gives for
  the Measure's population criteria: "The code provided (text/cql-identifier) could not be validated
  against the maximum value set http://www.rfc-editor.org/bcp/bcp13.txt…".

Use only synthetic content. If you can, run the publisher and check that the Library gets ELM.
