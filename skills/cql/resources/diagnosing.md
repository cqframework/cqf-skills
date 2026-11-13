# Diagnosing a Surprising CQL Result

Baseline: CQL 1.5.3. Untagged statements hold in 1.4, 1.5.3 and 2.0.0.
Sources: CQL-1.5.3, CQL-2.0.0, CQL-TESTS, CQFW-5.4.0, PROBES-2026-10-22

How to decide whether a surprising result is an engine defect, a translator defect, an author
error, a gap in the spec, an environment setting, or a problem in the model layer. Source IDs are
in [SOURCES.md](SOURCES.md).

Ask the six questions in order, and don't skip to a verdict. Most wrong conclusions came from
naming a layer before reading the spec, or from treating "it compiles" as "it is valid CQL".

## The six questions

### Q1. Does it reproduce without the data model?

Reduce the expression to System types (Integer, String, Date, tuples, lists) and run it with a
control that differs in exactly one thing. If the surprise disappears, the cause is in the model
layer: the modelinfo, its conversions, a helper library such as FHIRHelpers, or the data. Stop
here and diagnose that layer; it is not core CQL.

Write probes with explicit types and offsets, avoid `Now()` and `Today()`, run each twice, and
record the output and the configuration ([probes](probes/2026-10-22/RESULTS.md)).

### Q2. What does the target version's spec say?

Quote it, for the version the engine targets (usually 1.5.3; see
[spec/README.md](spec/README.md#which-version-applies)). One of three outcomes:

- **It decides.** Go to Q3.
- **It is silent, or contradicts itself.** That is a **spec gap**: nobody is wrong. The pattern is
  to avoid depending on the behaviour. Say "the spec is silent" and name the sections searched.
- **It changed between versions.** Check whether the translator applies the newer rule at the older
  compatibility level, and whether the test suites follow the text of their own version.

### Q3. Is the CQL well-formed by the spec?

"It compiles" does not mean it is well-formed. Check:

- **Grammar:** the CQL grammar in `08-a-cqlsyntax`, for example access-modifier placement or a
  parenthesised retrieve before a fluent call ([library-syntax.md](library-syntax.md)).
- **Type rules:** list-selector element types, `if`/`case` branch types at the target version, and
  set-operator element types ([type-system.md](type-system.md#list-and-conditional-typing)).
- **Reliance on options:** list promotion and demotion change which expressions are valid.
- **Untyped nulls** where an overload needs a type.
- **Compiler warnings**, read before results.

If the CQL breaks a spec rule, it is an **author error**, even when the translator accepts it.

### Q4. Does the ELM say what the spec says?

The ELM is the contract between translator and engine, and its semantics are defined in
`04-logicalspecification`. Read it (compiled from a freshly named file; see SKILL.md rule 6).

- Wrong ELM (the wrong overload, a missing conversion, an unexpected `As` or Choice) means a
  **translator** issue.
- Correct ELM evaluated to the wrong value means an **engine** issue.

First tell a compile error from a run-time one. Through `cql_execute` on the language server, a
compile error is prefixed `Library <name> loaded, but had errors:`; a run-time error is the bare
message, such as `Invalid Interval - …` [src: PROBES-2026-10-22 RESULTS.md §51]
[src: PROBES-2026-10-22 RESULTS.md §18]. An error raised while evaluating can still come from the
translator: read the ELM before naming the engine.

### Q5. Corroborate

- A conformance test from CQL-TESTS (cqframework/cql-tests), never from the out-of-date suites
  published with the spec. Tests are informative; a test is strong evidence when it matches the
  spec text, and a disagreement between a test and the text is itself worth reporting. To run the
  suite against an engine, see
  [spec/README.md](spec/README.md#running-the-conformance-tests).
- The code path, at a pinned version (cite the file and line range at the pinned tag).
- Optionally, another engine or version. Agreement between engines shows what they do, never what
  the spec requires.

### Q6. Is it the environment?

Translator options (list promotion and demotion, `signatureLevel`), the evaluation-request
timestamp and its offset, and the harness that runs the library. If the result follows from a
setting, it is an **environment** gotcha for that setting, not a defect.

## Verdicts

| Verdict | Meaning |
| --- | --- |
| Engine defect | The ELM is right and the engine evaluates it contrary to the spec |
| Translator defect | The CQL is well-formed and the ELM does not say what the spec says |
| Author error | The CQL breaks a spec rule, whatever the tools accept |
| Spec gap | The target version's text is silent or contradicts itself; avoid depending on it |
| Environment | The result follows from an option or setting |
| Model layer | The surprise disappears without the data model |

A **version gotcha** is a case where the answer depends on the target version: valid under one
version's text and not another's, or a tool applying one version's rule at another's level.

## Worked examples

Each was probed on translator and engine 5.4.0.

### Integer overflow wraps

`2147483647 + 1` returns `-2147483648`.

- **Q1:** System types only. Reproduces.
- **Q2:** decides. "If the result of the addition cannot be represented (i.e. arithmetic
  overflow), the result is null." (same in 1.4, 2.0)
  [src: CQL-1.5.3 09-b-cqlreference > Arithmetic Operators > Add]
- **Q3:** well-formed.
- **Q4:** the ELM is a plain `Add` of two Integer literals: correct.
- **Q5:** CQL-TESTS expects null [src: CQL-TESTS CqlArithmeticFunctionsTest.xml AddIntegerOverflow];
  the engine adds with plain machine integers
  [src: CQFW-5.4.0 engine/src/commonMain/kotlin/org/opencds/cqf/cql/engine/elm/executing/AddEvaluator.kt:34-37].
- **Verdict: engine defect.** `Sum` of Integers wraps too. Workaround: compute in Decimal, or in
  Long only where values stay within its range (Long wraps at its own maximum), for example
  `ToDecimal(x) + y` or `Sum(L X return all ToDecimal(X))` [src: PROBES-2026-10-22 RESULTS.md §30]
  [src: PROBES-2026-10-22 RESULTS.md §33].

### `{ 1, 'a' }` compiles

The list selector is typed `List<Any>`, with no diagnostic.

- **Q2:** decides. Later elements "are required to be of the inferred type of the first element",
  except a supertype or a type the first converts to (same in 1.4, 2.0)
  [src: CQL-1.5.3 03-developersguide > Types > Type Inference > Literals and Selectors].
- **Q3:** not well-formed: String is neither.
- **Verdict: author error,** with translator leniency. Workaround: keep lists homogeneous, or
  declare the type: `List<Choice<Integer, String>> { 1, 'a' }`
  [src: PROBES-2026-10-22 RESULTS.md §9] [src: PROBES-2026-10-22 RESULTS.md §33].

### `if true then 1 else 'a'` compiles to a Choice

- **Q2:** changed between versions. ELM `If`: "the else argument must be of that same type" (same in
  1.4, 2.0) [src: CQL-1.5.3 04-logicalspecification > Conditional Operators > If]; (2.0+) the
  Developer's Guide lets the result become a Choice and asks for a warning
  [src: CQL-2.0.0 03-developersguide > Conditional Expressions > Type Inference of Conditional Expressions].
- **Q3:** not well-formed at 1.5; valid at 2.0.
- **Q4:** the translator applies the 2.0 rule at compatibility level 1.5, without the warning
  [src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/LibraryBuilder.kt:2210-2222].
- **Verdict: version gotcha** (author error for a 1.5 target, accepted by the translator).
  Workaround: give both branches one type, for example by converting or casting one branch
  [src: PROBES-2026-10-22 RESULTS.md §11].

### Untyped `null = null` does not compile

- **Q2:** decides: "If either argument is null, the result is null.", and the section's own example
  is `null = null` (same in 1.4, 2.0)
  [src: CQL-1.5.3 09-b-cqlreference > Comparison Operators > Equal].
- **Q3:** well-formed: the spec uses it.
- **Q4:** the translator reports `Call to operator Equal(System.Any, System.Any) is ambiguous`.
- **Q5:** CQL-TESTS has it as a test
  [src: CQL-TESTS CqlComparisonOperatorsTest.xml SimpleEqNullNull].
- **Verdict: translator defect.** Workaround: type the null, `(null as Integer) = …`
  [src: PROBES-2026-10-22 RESULTS.md §28].

### `end of Interval[x, null)` is null

- **Q2:** decides at 1.5.3, and changed in 2.0. The ELM `End`: "If the high boundary of the
  interval is open, this operator returns the Predecessor of the high value of the interval. Note
  that if the high value of the interval is null, the result is null." (same in 1.4; **2.0:**
  returns an uncertainty) [src: CQL-1.5.3 04-logicalspecification > Interval Operators > End]. The
  CQL Reference `End` says the same
  [src: CQL-1.5.3 09-b-cqlreference > Interval Operators > End]. The selector's open null bound,
  "represented as an uncertainty", is read against that
  [src: CQL-1.5.3 04-logicalspecification > Interval Operators > Interval].
- **Q4:** the engine follows the 1.5.3 text.
- **Verdict: conforms at 1.5.3; version gotcha.** Workaround: use a closed null bound when
  "ongoing" is meant, or test `X.high is null` explicitly [src: PROBES-2026-10-22 RESULTS.md §16].
  See [intervals.md](intervals.md).

### `Interval[null, null]` evaluates to null

- **Q2:** decides: a closed null bound means the minimum or maximum of the point type
  [src: CQL-1.5.3 04-logicalspecification > Interval Operators > Interval]; **2.0:** names
  `Interval[null, null]` the maximum interval
  [src: CQL-2.0.0 09-b-cqlreference > Interval Operators > Point From].
- **Q3:** well-formed. **Q4:** the ELM is a correct `Interval` with two `Null` bounds.
- **Q5:** the engine returns null by design, with a TODO
  [src: CQFW-5.4.0 engine/src/commonMain/kotlin/org/opencds/cqf/cql/engine/elm/executing/IntervalEvaluator.kt:41-47];
  CQL-TESTS agrees with the spec
  ([intervals.md](intervals.md#both-bounds-null-the-maximum-and-the-unknown-interval)).
- **Verdict: engine defect.** Workaround: `Interval[minimum T, maximum T]`
  [src: PROBES-2026-10-22 RESULTS.md §17] [src: PROBES-2026-10-22 RESULTS.md §33].

### A typed null tuple element drops a whole union operand

`{ Tuple { …, v: 1 }, Tuple { …, v: null as Integer } } union { Tuple { …, v: 1.5 } }` keeps one
tuple instead of three.

- **Q1:** System types only. Reproduces.
- **Q2:** silent on two points (a third is under Q4). The spec defines no tuple type test for a
  null element, and no conversion
  of one tuple type to another ([type-system.md](type-system.md#where-the-spec-is-silent)).
- **Q3:** well-formed.
- **Q4:** the spec gives the union a choice type but does not say how each operand becomes that
  type (same in 1.4; **2.0:** adds an overload note)
  [src: CQL-1.5.3 03-developersguide > Types > Choice Types]; the translator wraps each operand in
  `As`. At run time the engine's type test fails the null-element tuple, so the whole operand is
  cast to null.
- **Verdict: spec gap**, where translator typing and engine type testing combine. Neither layer
  is wrong by the text, which is why arguing "engine or translator" went nowhere: the useful
  answer was "spec gap, avoid it". Workaround: normalise the tuple type before the union,
  `(L X return Tuple { d: X.d, v: ToDecimal(X.v) }) union R`
  [src: PROBES-2026-10-22 RESULTS.md §14] [src: PROBES-2026-10-22 RESULTS.md §33].

### `exists false` does not compile

- **Q2:** decides: `exists` takes a list. A single value reaches a list parameter only by list
  promotion, which "environments may choose whether or not to support"
  [src: CQL-1.5.3 03-developersguide > Types > Promotion and Demotion].
- **Q6:** the language server disables list promotion
  [src: PROBES-2026-10-22 RESULTS.md §1] [src: PROBES-2026-10-22 RESULTS.md §15].
- **Verdict: environment.** Workaround: for a Boolean, write `X is true`; for a value,
  `exists { X }` only if a one-element list is really meant. See
  [guides/README.md](guides/README.md).
