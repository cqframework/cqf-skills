---
name: cql
description: Use when authoring, reviewing, or debugging CQL libraries — syntax, library declarations, versioning, model-agnostic expression and function patterns — and whenever a question turns on what the CQL specification says (operator, null, type-testing, conversion or ELM semantics); builds and searches a verbatim local copy of the CQL 1.4, 1.5.3 and 2.0.0 specs with per-version change lists and conformance tests
license: Apache-2.0
---

CQL (Clinical Quality Language) is an HL7 specification for expressing clinical logic in quality measures and decision support.

This skill covers model-agnostic CQL. For patterns that depend on a data model (FHIR, US Core,
US Quality Core) in quality measures, use the CMS Quality Measure Development IG; see
[resources/guides/README.md](resources/guides/README.md).

## Spec Reference

A verbatim, section-split copy of the spec, by version, lives in
[resources/spec/](resources/spec/README.md). Search it with `grep`; don't fetch cql.hl7.org,
because web fetches truncate and paraphrase.

The spec text is HL7 content and is not distributed with this skill, so the copy is built locally.
If `resources/spec/1.5.3/INDEX.md` does not exist, build it once by running
`bash scripts/fetch-spec.sh` from the skill folder. It needs bash, curl, tar, `python3` and network
access to GitHub, and takes about a minute. If it can't be built, say so, then quote from
cql.hl7.org and note that the quote came from a web fetch.

| Version | Release | Published at |
| --- | --- | --- |
| 1.4 | Release 1 STU 4 | <https://cql.hl7.org/STU4/> |
| 1.5.3 | Release 1 Errata 2 (normative) | <https://cql.hl7.org/N1A/> |
| 2.0.0 | R2 STU 1 (trial-use; current site) | <https://cql.hl7.org/> |

Each has its ELM schema, and there is a section-level change list between consecutive versions.
The conformance tests are the current suite from
[cqframework/cql-tests](https://github.com/cqframework/cql-tests) (`resources/spec/cql-tests/`).
The tests published with the spec are out of date: don't use or cite them. **Most engines implement 1.5 or 1.4, not 2.0.** The cqframework translator
defaults to `compatibilityLevel` `"1.5"`. Answer against the version the engine targets; see
[Which version applies](resources/spec/README.md#which-version-applies).

The rest of this skill was written on 2026-04-28 against CQL 1.5. Where it disagrees with
`resources/spec/`, the spec copy wins.

## Order of Authority

1. **The spec, for the engine's target version, decides what CQL means.** Quote it.
2. **Patterns show how to write it, within the spec:** expert idioms and the authoring patterns in
   the CMS Quality Measure Development IG ([resources/guides/README.md](resources/guides/README.md)).
   A pattern never overrides the spec.
3. **Translator and engine observations are gotchas only:** places where an implementation departs
   from the spec or depends on a setting. Each gotcha comes with a spec-correct workaround. An
   observation is never evidence of what CQL means.

To decide which layer a surprising result belongs to (engine, translator, author error, spec gap,
environment or model layer), follow [resources/diagnosing.md](resources/diagnosing.md).

## Feature Availability

Source IDs are defined in [resources/SOURCES.md](resources/SOURCES.md).

| Feature | First version | Status |
| --- | --- | --- |
| Related-context retrieve (`["Mother" -> Observation]`) [src: CQL-1.4 03-developersguide > Related Context Retrieves] | 1.4 | — |
| Retrieve search paths, `include`, `reverseInclude` [src: CQL-1.5.3 03-developersguide > Related Context Retrieves] | 1.5 | trial-use |
| Fluent functions [src: CQL-1.5.3 03-developersguide > Defining Functions > Fluent Functions] | 1.5 | trial-use |
| Aggregate clause [src: CQL-1.5.3 03-developersguide > Aggregate Queries] | 1.5 | trial-use |
| `Long` type [src: CQL-1.5.3 09-b-cqlreference > Types > Long] | 1.5 | trial-use |
| Comment tags [src: CQL-1.5.3 03-developersguide > Lexical Elements > Comments > Tags] | 1.5 | trial-use |
| `CodeSystem`, `ValueSet`, `Vocabulary` types [src: CQL-1.5.3 09-b-cqlreference > Types > ValueSet] | 1.5 | trial-use |
| `ExpandValueSet` [src: CQL-1.5.3 09-b-cqlreference > Clinical Operators > ExpandValueSet (ValueSet)] | 1.5 | trial-use |
| `expand` on a single `Interval<T>` [src: CQL-1.5.3 09-b-cqlreference > Interval Operators > Expand] | 1.5 | trial-use |
| CQL `Slice` function (ELM `Slice` exists in 1.4) [src: CQL-2.0.0 09-b-cqlreference > List Operators > Slice] | 2.0 | trial-use |
| Comment tag value optional [src: CQL-2.0.0 03-developersguide > Lexical Elements > Comments > Tags] | 2.0 | trial-use |

## Evidence Rules for Language Semantics

Most of our wrong conclusions came from asserting what CQL means without reading what the spec
says. Before stating how an operator, type test, conversion, or null case behaves:

1. **Quote the spec section verbatim, with its version and URL** (format in
   [resources/spec/README.md](resources/spec/README.md#citing-the-spec)). A paraphrase or a
   summary from memory does not count.
2. **Use the engine's target version** (usually 1.5.3, sometimes 1.4). If the section appears in a
   `CHANGES-*.md` list, say what the other versions say too. Text found only in 2.0.0 is a
   clarification, not evidence of what a 1.5 engine must do.
3. **Look for a conformance test** in `resources/spec/cql-tests/`, the current
   cqframework/cql-tests suite, whatever version the engine targets. Never use the test suites
   published with the spec (the `tests.zip` on cql.hl7.org, or HL7/cql `tests/`): they are out of
   date and contradict the spec in places. If no test exists, say so. To check what an engine
   actually does against the suite, run it with
   [cql-tests-runner](https://github.com/cqframework/cql-tests-runner); see
   [Running the conformance tests](resources/spec/README.md#running-the-conformance-tests).
4. **If the spec is silent, say so** and name the sections you searched. "Silent" is a finding;
   reasoning that sounds plausible is not the spec.
5. **Keep three claims apart:** what the spec says, what the translator emits (read the ELM), and
   what the engine does (run it). Engine source, translator source and past upstream fixes are
   evidence of behavior only, never of what the spec requires.
6. **Run every repro before relying on it,** with a control that differs in exactly one thing.
   Paste the actual output. After editing a probe file, save it under a new library and file name
   before reading its ELM: the language server's ELM view has returned the previous version's ELM
   after an edit.
7. **Guide text supports idioms and pitfalls, never semantics.** A `guide` source such as the CMS
   Quality Measure Development IG shows how authors write CQL; check its date, model and assumed
   translator options, and let the spec win where they differ. See
   [resources/guides/README.md](resources/guides/README.md).

## Supporting Files

For library syntax, declarations, and versioning: see [library-syntax.md](resources/library-syntax.md)
For type testing, casting, choice types, conversions, tuples, and list and conditional typing: see [type-system.md](resources/type-system.md)
For interval bounds, null bounds, the maximum interval and invalid intervals: see [intervals.md](resources/intervals.md)
For date/time precision, timezone offsets, duration vs difference, time units and calendar arithmetic: see [datetime.md](resources/datetime.md)
For null semantics by operator family (logic, equality, arithmetic, conditionals, queries, membership): see [nulls.md](resources/nulls.md)
For singleton from, duplicates and set operators, query shapes, multi-source queries, relationships, sorting and empty lists: see [lists-queries.md](resources/lists-queries.md)
For operators, type system, and built-in functions: see [operators.md](resources/operators.md)
For how CQL types, the translator and the engine relate (casting, overloads, `Choice` arguments): see [types-and-engine.md](resources/types-and-engine.md)
For the verbatim spec, ELM schema, conformance tests and running them: see [resources/spec/README.md](resources/spec/README.md)
To diagnose a surprising result (six questions and verdicts, with worked examples): see [resources/diagnosing.md](resources/diagnosing.md)
For the source IDs used in `[src: …]` citations: see [resources/SOURCES.md](resources/SOURCES.md)
For recorded probe runs (CQL, outputs, configuration): see [resources/probes/](resources/probes/2026-10-22/RESULTS.md)
For authoring patterns and worked pitfalls (informative; never semantics): see [resources/guides/README.md](resources/guides/README.md)
To check citation and version-tag conventions: `python3 scripts/lint_skill.py` (tests: `scripts/test_lint_skill.py`); to check spec quotes: `python3 scripts/check_citations.py <file.md>`
To see what really changed in a cited section before tagging it: `python3 scripts/section_diff.py 'page|Heading > Path'`; to re-wrap long prose without changing text: `python3 scripts/reflow_md.py <file.md>`

## Types and the Translator

Two rules that explain many surprising CQL results. They describe the **cqframework translator**
(v5.4.0), not spec requirements; the spec is silent on the first and on part of the second. Full
detail: [types-and-engine.md](resources/types-and-engine.md).

- **`when X is T then …` does not narrow `X`** (translator behaviour; no spec text mentions
  narrowing). Inside the branch `X` keeps its declared type, and every call there is resolved
  against it. Cast explicitly: `(X as T).someFunction()`.
- **In the translator, a `Choice<…>` argument matches only the exact component types it lists**
  (the spec defines a choice-to-component cast and is silent on a supertype of a component). A
  component that is a *subtype* of an overload's parameter does not make that overload applicable,
  yet the argument is still accepted for a parameter that equals just one component — so a call
  can silently narrow to one overload (`As X`, `null` for the other branch). Two overloads, each
  equal to a *different* component, tie and raise an ambiguity error instead. Making the component
  test subtype-aware is **not** enough on its own: scoring still prefers the exact-component match.

## Known Gotchas

Where translator or engine 5.4.0, or the language server, departs from the spec, fills a gap in
it, or depends on a setting. Each link leads to a block with the probe, the spec text, the layer
and a workaround. Silent wrong values come first.

Every translator and engine observation in this skill is on 5.4.0. Other tools bundle other
versions: IG Publisher 3.0.1 compiles CQL with cqframework 3.29.0, so the ELM in a package it builds
can differ from these probes (for example `Choice`/`As` emission, `if`-branch typing or list
typing). None of these gotchas was probed on 3.29.0.

- **Integer and Long overflow wraps**, including `Sum` (engine):
  [nulls.md](resources/nulls.md#gotcha-integer-and-long-overflow-wraps-instead-of-returning-null)
- **A typed null tuple element drops a whole union operand** (spec gap):
  [type-system.md](resources/type-system.md#gotcha-a-typed-null-tuple-element-drops-the-whole-union-operand)
- **Set operators don't convert element types**, so `{ 1 } intersect { 1.0 }` is empty (spec gap,
  translator): [type-system.md](resources/type-system.md#gotcha-set-operators-dont-convert-element-types)
- **`Interval[null, null]` is null**, not the maximum interval (engine):
  [intervals.md](resources/intervals.md#gotcha-an-interval-with-both-bounds-null-evaluates-to-null)
- **Milliseconds against no milliseconds compare as null** (engine):
  [datetime.md](resources/datetime.md#gotcha-a-value-with-milliseconds-and-one-without-compare-as-null)
- **Calendar quantities in different units compare as null** (engine):
  [datetime.md](resources/datetime.md#gotcha-calendar-quantities-in-different-units-compare-as-null)
- **`Combine` returns null for a null element or a null separator** (engine):
  [nulls.md](resources/nulls.md#gotcha-combine-returns-null-for-a-null-element-or-a-null-separator)
- **`=` with an empty list is null** (engine):
  [lists-queries.md](resources/lists-queries.md#gotcha--with-an-empty-list-is-null)
- **Tuple `=` with a null element on one side is null** (spec gap):
  [nulls.md](resources/nulls.md#gotcha-tuple--with-a-null-element-on-one-side-is-null)
- **A tuple with a null element fails a tuple type test** (spec gap):
  [type-system.md](resources/type-system.md#gotcha-a-tuple-with-a-null-element-fails-a-tuple-type-test)
- **An interval with a null bound fails `is Interval<T>`** (spec gap; engine choice):
  [intervals.md](resources/intervals.md#gotcha-an-interval-with-a-null-bound-fails-is-intervalt)
- **A `Choice` overload beats an `Any` overload** (translator):
  [types-and-engine.md](resources/types-and-engine.md#gotcha-a-choice-overload-beats-an-any-overload)
- **`{ 1, 'a' }` compiles to `List<Any>`** (translator leniency; author error):
  [type-system.md](resources/type-system.md#gotcha--1-a--compiles-to-listany)
- **`if` with unrelated branch types compiles to a Choice at 1.5** (translator; version gotcha):
  [type-system.md](resources/type-system.md#gotcha-if-with-unrelated-branch-types-compiles-to-a-choice-at-15)
- **A Date bound with a DateTime bound can be an invalid interval**, depending on the evaluation
  offset (spec gap, environment):
  [intervals.md](resources/intervals.md#gotcha-a-date-bound-with-a-datetime-bound-can-be-an-invalid-interval)
- **One run-time error fails every define in the run** (environment):
  [intervals.md](resources/intervals.md#gotcha-one-run-time-error-fails-every-define-in-the-run)
- **A UCUM unit in date arithmetic is a run-time error** (engine):
  [datetime.md](resources/datetime.md#gotcha-a-ucum-unit-in-date-arithmetic-is-a-run-time-error)
- **`$this` alone in `sort by` fails at run time** (engine):
  [lists-queries.md](resources/lists-queries.md#gotcha-this-alone-in-sort-by-fails-at-run-time)
- **Untyped `null = null` does not compile** (translator):
  [nulls.md](resources/nulls.md#gotcha-untyped-null--null-does-not-compile)
- **List promotion is disabled in the language server**, so `exists false` does not compile
  (environment):
  [type-system.md](resources/type-system.md#gotcha-list-promotion-is-disabled-in-the-language-server)
- **The invalid-interval message prints the raw bounds** (engine):
  [intervals.md](resources/intervals.md#gotcha-the-invalid-interval-message-prints-the-raw-bounds)
- **Printed values hide open bounds and offsets** (environment):
  [intervals.md](resources/intervals.md#gotcha-printed-intervals-show-the-predecessor-of-an-open-bound),
  [datetime.md](resources/datetime.md#gotcha-printed-datetimes-omit-the-offset)

Translator behaviour around `Choice` arguments and narrowing is under
[Types and the Translator](#types-and-the-translator).
