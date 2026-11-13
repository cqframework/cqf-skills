# Guides

Guide sources are informative: they show how experienced authors write CQL. They never define
what the language means. Source IDs are in [SOURCES.md](../SOURCES.md).

## CMS Quality Measure Development IG (`CMSQMD`)

The authoring patterns once kept in the CQL Formatting and Usage Wiki are now maintained in the
CMS Quality Measure Development Implementation Guide:

- Published (CI build): <https://build.fhir.org/ig/cqframework/cms-qmd/branches/main/>
- Source: <https://github.com/cqframework/cms-qmd> (Apache-2.0)

Pages to start from:

| Page | What it covers |
| --- | --- |
| [Patterns](https://build.fhir.org/ig/cqframework/cms-qmd/branches/main/patterns.html) | Overview of the authoring guidance and the model it assumes |
| [Measure Guidance](https://build.fhir.org/ig/cqframework/cms-qmd/branches/main/measure_guidance.html) | Style and naming conventions for measure logic |
| [FHIR Patterns](https://build.fhir.org/ig/cqframework/cms-qmd/branches/main/pattern_fhir.html) | Cardinality, must support, modifiers, accessing data, terminology use |
| [Logic Layers](https://build.fhir.org/ig/cqframework/cms-qmd/branches/main/pattern_layers.html) | Organizing logic as Concepts, Elements, Inferences and Criteria |
| [Pattern Index](https://build.fhir.org/ig/cqframework/cms-qmd/branches/main/pattern_index.html) | Every data element and pattern, by clinical area |
| [Known Issues](https://build.fhir.org/ig/cqframework/cms-qmd/branches/main/knownissues.html) | Known issues affecting how measures are expressed |

Model-independent patterns (primitives, choices, missing information, date and time precision,
timezone offsets, time-valued quantities) are in the Patterns page of
[Using CQL with FHIR](https://hl7.org/fhir/uv/cql/), and the CMS QMD IG links to them.

The IG targets US Quality Core on FHIR R4 (4.0.1). Its model-specific patterns apply only to
libraries that use that model. This skill draws on the IG only for model-independent language
guidance.

## CQL Formatting and Usage Wiki (`CQLWIKI`)

The cqframework community's CQL Formatting and Usage Wiki ("Cooking with CQL") collected expert
idioms, Q&A from the Cooking with CQL sessions, and worked pitfalls written between 2016 and 2026.
Its content is now maintained in the CMS QMD IG. A few topic files still cite individual Q&A pages
at wiki commit `cc3c351` (2026-10-16). Each `[src: CQLWIKI <Page>.md]` citation resolves to
`https://github.com/cqframework/CQL-Formatting-and-Usage-Wiki/wiki/<Page>`. Use CMSQMD for new
citations.

## Rules for using guide sources

- **Cite them for how CQL is written,** not for what CQL means: idioms, common mistakes, and worked
  explanations. Use `[src: CMSQMD <page>.html#<anchor>]` or `[src: CQLWIKI <Page>.md]`.
- **Never cite them for semantics.** Where a guide and the target version's spec text differ,
  quote both, record the difference, and treat the spec text as authoritative.
- **Check the date and the model first.** Note when the page was written and the model it targets
  (QDM, a QI-Core version, US Quality Core, FHIR). If you need the CQL version in force on that
  date, take it from the spec copy's version history in [spec/README.md](../spec/README.md); don't
  guess.
- **Check the environment it assumes.** An answer can depend on translator options such as list
  promotion, which not every environment enables.

## Example: right in its context, misleading out of it

The wiki page
[QA-Exists-Returns-True-For-Lists-With-False-or-Null](https://github.com/cqframework/CQL-Formatting-and-Usage-Wiki/wiki/QA-Exists-Returns-True-For-Lists-With-False-or-Null)
(2017-10-12) answers:

> When calling an "exists" on something that returns "false", you will always get a true result
> back.

- The page states the result but not the mechanism. A single Boolean is not a list, so `exists`
  accepts it only through list promotion: "Whenever an operation that expects a list-valued
  argument is passed a single value, the single value may be promoted to a list" (CQL 1.5.3,
  Developer's Guide, Promotion and Demotion). Environments "may choose whether or not to support"
  promotion.
- With list promotion disabled, `exists false` does not compile:
  `Could not resolve call to operator Exists with signature (System.Boolean).`
  ([probe §15](../probes/2026-10-22/RESULTS.md)).
- The title's "null" case is wrong for any list of nulls: `exists` "returns true if the list
  contains any non-null elements" (CQL 1.5.3, List Operators, Exists; same in 1.4 and 2.0.0), so
  `exists { null }` is `false`. That was also observed.
