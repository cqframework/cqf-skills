# CQL Skill Test Questions: Answer Key

Baseline: CQL 1.5.3. Untagged statements hold in 1.4, 1.5.3 and 2.0.0.
Sources: CQL-1.4, CQL-1.5.3, CQL-2.0.0, CQL-TESTS, CQFW-5.4.0, PROBES-2026-10-22

Expected answers for [questions.md](questions.md). Don't give this file to an agent under test.
Source IDs are in [SOURCES.md](../resources/SOURCES.md). Each answer gives the expected facts, the
spec text that decides them, the probe that shows the engine, the layer, and what a passing answer
must and must not say. "Skill" names where the skill covers it, for tracing a failed answer to a
gap.

An answer fails if it states a semantic rule without spec text, presents engine or translator
behaviour as the spec, or names a layer that the cited evidence does not support.

## Type testing and choice types

### TQ-01. Null in type tests

- **Expected:** `(null as Integer) is Integer` is `false` on the engine. 1.4 and 1.5.3 are silent
  on `null is T`; (2.0+) the text says it is false. The spec is silent on whether a tuple with a
  null element passes a tuple type test; the engine says `false`. The union is typed
  `List<Choice<Tuple{v Decimal}, Tuple{v Integer}>>`: no Integer-to-Decimal conversion is applied
  to the tuple elements, and the spec is silent on such a conversion.
- **Spec:** (2.0+) "the expression null is Integer returns false"
  [src: CQL-2.0.0 09-b-cqlreference > Type Operators > Is].
- **Observed:** [src: PROBES-2026-10-22 RESULTS.md §7] [src: PROBES-2026-10-22 RESULTS.md §8]
  [src: PROBES-2026-10-22 RESULTS.md §10].
- **Layer:** spec gap for the tuple test; engine choice fills it. Translator typing for the union.
- **Pass if:** it separates 1.5.3 silence from the 2.0.0 clarification, says the tuple case is
  silent rather than citing a rule that "null carries no type", and does not claim the elements are
  converted.
- **Skill:** [type-system.md](../resources/type-system.md#null-and-is),
  [type-system.md](../resources/type-system.md#tuples-with-a-null-element).

### TQ-02. Union of different element types

- **Expected:** `List<Choice<Integer, String>>`. Passing an element to `f(x Integer)` applies an
  implicit cast to the component type, which gives `null` for the `'a'` element.
- **Spec:** "For union, this means that the inputs can be lists of different types of elements,
  and the type of the result is now a choice type with components of each of the input types." and
  "The semantics for casting will result in a null if the run-time value of the element is not of
  the appropriate type." (same in 1.4; **2.0:** adds an overload note)
  [src: CQL-1.5.3 03-developersguide > Types > Choice Types].
- **Observed:** [src: PROBES-2026-10-22 RESULTS.md §10] [src: PROBES-2026-10-22 RESULTS.md §2].
- **Layer:** the silent null is what the spec describes; not a defect.
- **Pass if:** it quotes the Choice Types text and calls the null spec behaviour.
- **Skill:** [type-system.md](../resources/type-system.md#choice-types).

### TQ-03. Two overloads, one Choice argument

- **Expected:** both overloads are reachable by a Cast (precedence 4), with the same number of
  conversions, so the call is ambiguous and the spec requires an error. The translator reports
  `Call to operator f(choice<System.Integer,System.String>) is ambiguous`. With only
  `f(x Integer)`, the call binds with an `As`, and `'a'` reaches `f` as `null`.
- **Spec:** "Cast - If the invocation type can be cast to the declare type (e.g., the invocation
  type is a choice that includes the declared type)" (same in 1.4, 2.0)
  [src: CQL-1.5.3 03-developersguide > Types > Conversion Precedence]; "If multiple signatures have
  the same number of required conversions, an ambiguous resolution error is thrown"
  [src: CQL-1.5.3 03-developersguide > Libraries > Function Resolution]. The spec is silent on
  run-time dispatch over a choice's components.
- **Observed:** [src: PROBES-2026-10-22 RESULTS.md §2].
- **Layer:** translator, conforming.
- **Pass if:** it cites conversion precedence and the ambiguity rule, and does not claim the spec
  requires run-time dispatch.
- **Skill:** [types-and-engine.md](../resources/types-and-engine.md), SKILL.md "Types and the
  Translator".

### TQ-04. A Choice and a common supertype

- **Expected:** no. The spec defines a cast from a choice to one of its components; it is silent
  on converting a choice to a supertype of its components that is not itself a component. On
  translator 5.4.0, such a supertype is not a candidate for a model class (a `DomainResource`
  overload is not applicable to `Choice<Condition, AllergyIntolerance>`), while `Any` accepts a
  Choice by subtyping.
- **Spec:** silent; see the Choice Types and Conversion Precedence text above.
- **Observed:** [src: PROBES-2026-10-22 RESULTS.md §2] [src: PROBES-2026-10-22 RESULTS.md §3].
- **Layer:** spec gap; translator behaviour.
- **Pass if:** it says "the spec is silent" and recommends an explicit cast or a Choice overload,
  and does not cite a library's explicit Choice overload as evidence of implicit widening.
- **Skill:** [type-system.md](../resources/type-system.md#where-the-spec-is-silent).

### TQ-05. An `Any` overload against a `Choice` overload

- **Expected:** the spec does not decide for the Choice overload. Integer derives from `Any`, so
  `f(x Any)` matches by Subtype (precedence 2). A value of a component type passed to a Choice
  parameter is not one of the ten listed categories (Cast is the reverse direction, from a choice
  to a component). The 1.5.3 sentence "Choice types are compatible if the choices of one type are a
  subset of the choices of the other" could be read as covering this, if a plain type counted as a
  one-element choice; the spec does not say so. Translator 5.4.0 calls the Choice overload
  (`'choice'`).
- **Spec:** "All other types derive from System.Any" (same in 1.4, 2.0)
  [src: CQL-1.5.3 03-developersguide > Types > System-Defined Types]; "Subtype – If the invocation
  type is a subtype of the declared type of the argument"
  [src: CQL-1.5.3 03-developersguide > Types > Conversion Precedence].
- **Observed:** [src: PROBES-2026-10-22 RESULTS.md §50].
- **Layer:** translator behaviour where the text does not place one candidate.
- **Pass if:** it does not claim the spec ranks the Choice overload higher, and recommends not
  overloading on `Any` and a Choice.
- **Skill:** gap if the skill has no entry; see
  [types-and-engine.md](../resources/types-and-engine.md).

### TQ-06. `as` to a type outside the choice

- **Expected:** translator 5.4.0 rejects it at compile time: `Expression of type
  'choice<System.Integer,System.String>' cannot be cast as a value of type 'System.Decimal'.`
  The output starts "loaded, but had errors", which marks a compile error. `as` describes "treating
  a value of some base type as a more specific type"; Decimal is not a component, and the spec does
  not say whether such a cast is a compile error. `v as Integer` is valid and gives `null` for
  `'a'`.
- **Spec:** "Casting is the operation of treating a value of some base type as a more specific type
  at run-time." (same in 1.4, 2.0) [src: CQL-1.5.3 03-developersguide > Types > Casting].
- **Observed:** [src: PROBES-2026-10-22 RESULTS.md §51].
- **Layer:** translator (the error), not engine.
- **Pass if:** it calls the error a translator error, and does not state a spec rule that `as` may
  only narrow to a listed component.
- **Skill:** [type-system.md](../resources/type-system.md#casting-as-and-cast).

## Diagnosis method

### TQ-07. Where an overload error comes from

- **Expected:** the compiled ELM. Read the `FunctionRef`: its `signature` and the operand types
  (`As`, `asType`, result types). If the ELM already carries the wrong or indistinguishable types,
  the translator lost the distinction, even when the engine throws the error. Read the ELM from a
  freshly named file.
- **Spec:** the ELM is defined by the Logical Specification (Q4 in the skill's method).
- **Layer:** decided by the ELM, not by where the exception is thrown.
- **Pass if:** it says the throw site is not the defect site and points at the ELM signature.
- **Skill:** [diagnosing.md](../resources/diagnosing.md#q4-does-the-elm-say-what-the-spec-says).

### TQ-08. Two engines agree

- **Expected:** it shows what the engines do, not what the spec requires or what the expected
  result is. Both may share a translator, a data path or broken data. It does not rule out an
  engine, translator, data or expected-value error.
- **Pass if:** it says agreement is not evidence about the spec or the expected value.
- **Skill:** [diagnosing.md](../resources/diagnosing.md#q5-corroborate).

### TQ-09. A good control

- **Expected:** reduce to System types where possible; the control differs from the probe in
  exactly one thing; use explicit types and timezone offsets and avoid `Now()` and `Today()`; run
  each twice; record the CQL, the output and the configuration (translator options, evaluation
  offset). Keep libraries expected to fail to compile apart from their controls.
- **Pass if:** it names the one-difference control and recording both runs.
- **Skill:**
  [diagnosing.md](../resources/diagnosing.md#q1-does-it-reproduce-without-the-data-model), SKILL.md
  evidence rules.

### TQ-10. Model types

- **Expected:** no. The CQL spec defines System types only; a model's types and its conversions to
  System types come from the model (its model information and any helper library). The spec allows
  that: "specific data models may introduce conversions, including implicit conversions."
  (same in 1.4, 2.0) Which
  conversions apply, and when, is a model question for the model's documentation or skill.
- **Spec:** [src: CQL-1.5.3 03-developersguide > Types > Conversion > Implicit Conversions].
- **Pass if:** it says the CQL spec does not answer it and points to the model layer.
- **Skill:** [type-system.md](../resources/type-system.md#implicit-and-explicit-conversion),
  [datetime.md](../resources/datetime.md).

## Queries and lists

### TQ-11. A query over a null source

- **Expected:** `null`. The `return` clause is not evaluated. A source holding a value gives `2`.
- **Spec:** (1.5+) "If all the sources of a query evaluate to null, the result is null"
  [src: CQL-1.5.3 03-developersguide > Non-Retrieve Queries].
- **Observed:** [src: PROBES-2026-10-22 RESULTS.md §45].
- **Layer:** engine conforms.
- **Pass if:** it quotes this sentence and does not call the null an engine defect.
- **Skill:** [lists-queries.md](../resources/lists-queries.md#multi-source-queries),
  [nulls.md](../resources/nulls.md#queries).

### TQ-12. `singleton from`

- **Expected:** `null` for the empty list; a run-time error for two elements.
- **Spec:** "If the source list is empty, the result is null. If the source list contains one
  element, that element is returned. If the list contains more than one element, a run-time error is
  thrown." (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > List Operators > Singleton From].
- **Observed:** [src: PROBES-2026-10-22 RESULTS.md §34].
- **Pass if:** both cases are right, with the quote.
- **Skill:** [lists-queries.md](../resources/lists-queries.md#singleton-from).

### TQ-13. Comparing empty lists

- **Expected:** the spec gives `true`; engine 5.4.0 gives `null` (engine defect). Use
  `not exists L`, `Count(L) = 0` or `~`.
- **Observed:** [src: PROBES-2026-10-22 RESULTS.md §39];
  [src: CQL-TESTS CqlListOperatorsTest.xml EqualEmptyListAndEmptyList].
- **Pass if:** it separates the spec answer from the engine's.
- **Skill:** [lists-queries.md](../resources/lists-queries.md#gotcha--with-an-empty-list-is-null).

## Intervals

### TQ-14. Open and closed null bounds

- **Expected:** at 1.5.3 the open form gives `null` and the closed form gives the maximum DateTime.
  An open null bound is unknown; a closed one is the maximum of the point type. **2.0:** `end of`
  the open form returns an uncertainty instead of null.
- **Spec:** "If the high bound of the interval is null and closed, the interval is interpreted to
  end at the maximum value of the point type" (same in 1.4; **2.0:** "for the point type", same
  meaning)
  [src: CQL-1.5.3 04-logicalspecification > Interval Operators > Interval]; "Note that if the high
  value of the interval is null, the result is null." (same in 1.4; **2.0:** an uncertainty)
  [src: CQL-1.5.3 04-logicalspecification > Interval Operators > End].
- **Observed:** [src: PROBES-2026-10-22 RESULTS.md §16].
- **Pass if:** it says the two values differ by rule, and notes the 2.0 change.
- **Skill:** [intervals.md](../resources/intervals.md).

### TQ-15. An empty half-open interval

- **Expected:** no; it is invalid, and building it is a run-time error.
- **Spec:** "Attempting to specify an invalid Interval will result in a run-time error." with the
  example `Interval[1, 1) // Invalid interval, conflicting to say it both includes and excludes 1`
  (same in 1.4, 2.0) [src: CQL-1.5.3 02-authorsguide > Values > Interval Values].
- **Observed:** [src: PROBES-2026-10-22 RESULTS.md §18].
- **Pass if:** it quotes the invalid-interval rule; it fails if it calls the interval a valid empty
  interval.
- **Skill:** [intervals.md](../resources/intervals.md#invalid-intervals-and-unit-intervals).

### TQ-16. Both bounds null

- **Expected:** `start of` the open form is `null` at 1.5.3 ("if the low value of the interval is
  null, the result is null"; same in 1.4; **2.0:** an uncertainty), and the engine agrees. For the
  closed form the spec makes the interval run from the minimum to the maximum Integer, so `5 in` it
  is `true`; engine 5.4.0 treats any interval with both bounds null as null and returns `false`. The
  closed-null rule is the same in 1.4 and 2.0 (2.0 differs in wording only).
- **Spec:** [src: CQL-1.5.3 04-logicalspecification > Interval Operators > Start];
  [src: CQL-1.5.3 04-logicalspecification > Interval Operators > Interval].
- **Observed:** [src: PROBES-2026-10-22 RESULTS.md §17] [src: PROBES-2026-10-22 RESULTS.md §47].
- **Layer:** engine defect for the closed form.
- **Pass if:** it separates open from closed and the spec from the engine.
- **Skill:**
  [intervals.md](../resources/intervals.md#gotcha-an-interval-with-both-bounds-null-evaluates-to-null).

### TQ-17. The type of an interval with a null bound

- **Expected:** no sentence gives the run-time type of an interval value with a null bound. The
  selector fixes the static type ("The static type of the low bound determines the type of the
  interval", above), and `is` tests the run-time type, but static type does not decide `is` for a
  null: (2.0+) "(null as Integer) is Integer is equivalent to null is Integer and also returns
  flase" (sic). So the spec is silent, and an answer that derives `true` from the selector rule is
  an inference, not spec text. Engine 5.4.0 returns `false` for `Interval[1, null]`, open or
  closed, because it tests both bounds against the point type and a null bound fails; with both
  bounds null the engine's null interval gives `false` too. `Interval[1, 5]` gives `true`.
- **Spec:** "If the run-time type of the argument is the same as or derived from the type being
  tested, the result of the operator is true" (**1.4:** "is of the type being tested")
  [src: CQL-1.5.3 09-b-cqlreference > Type Operators > Is]
  [src: CQL-2.0.0 09-b-cqlreference > Type Operators > Is].
- **Observed:** [src: PROBES-2026-10-22 RESULTS.md §47]; the branch that tests both bounds
  [src: CQFW-5.4.0 engine/src/commonMain/kotlin/org/opencds/cqf/cql/engine/elm/executing/IsEvaluator.kt:104-121].
  Upstream changed this after 5.4.0 so that the bound that is present decides, in a commit dated
  2026-10-08 that is in no release yet.
- **Layer:** spec gap; engine 5.4.0's choice, which upstream maintainers have since changed.
- **Pass if:** it reports the 5.4.0 result and does not present a reading as a spec sentence. A
  derivation from the selector rule passes if it is labelled as an inference.
- **Skill:** gap if the skill has no entry.

### TQ-18. Mixed bound types

- **Expected:** `Interval[1, 'a']` is invalid ("the high bound must be of the same type"), and the
  translator rejects it. A Date and a DateTime bound are valid: Date converts implicitly to
  DateTime, and the ELM has `ToDateTime` over the low bound. It can still fail at run time: the
  engine raises "Invalid Interval" when `low <= high` is null. At evaluation offset `-04:00`,
  `@2026-01-02T00:00:00Z` is 20:00 on 1 January, the day matches the Date, the hour is unknown, so
  the comparison is null. With the evaluation offset or a later day it works. The spec requires the
  end to be "greater than or equal to" the start and is silent on a null comparison. The null
  comes from 1.5.3's `ToDateTime` of a Date leaving "the time components unspecified" (same in
  2.0); **1.4:** "the time components set to zero", so the Date is midnight, `low <= high` is true
  and the interval is valid [src: CQL-1.5.3 09-b-cqlreference > Type Operators > ToDateTime]
  [src: CQL-1.4 09-b-cqlreference > Type Operators > ToDateTime].
- **Spec:** "The static type of the low bound determines the type of the interval, and the high
  bound must be of the same type." (same in 1.4, 2.0)
  [src: CQL-1.5.3 04-logicalspecification > Interval Operators > Interval].
- **Observed:** [src: PROBES-2026-10-22 RESULTS.md §46].
- **Layer:** author error for the first; for the second, a version gotcha: valid at 1.4, and at
  1.5.3 a spec gap with an environment-dependent engine choice.
- **Pass if:** it gets both compile answers and, for full credit, names the offset-dependent
  run-time failure.
- **Skill:** gap if the skill has no entry.

### TQ-19. A closed null end in timing comparisons

- **Expected:** the maximum DateTime, `9999-12-31T23:59:59.999`. `during` a bounded interval is
  `false`, because the end is not inside it; with an open null end it is `null`. `overlaps` a later
  bounded interval is `true`.
- **Spec:** the closed-null rule quoted under TQ-14.
- **Observed:** [src: PROBES-2026-10-22 RESULTS.md §48].
- **Pass if:** it gives false for the closed form and null for the open one, from the bracket rule.
- **Skill:** [intervals.md](../resources/intervals.md).

### TQ-20. A same-day length of stay

- **Expected:** `0`, since `duration` counts whole calendar periods. `Interval[1, 0]` is invalid and
  raises a run-time error. That is correct engine behaviour; the error is in the logic that builds
  the interval.
- **Spec:** "returns the number of whole calendar periods for the specified precision between the
  first and second arguments" (same in 1.4; **2.0:** adds offset normalisation)
  [src: CQL-1.5.3 09-b-cqlreference > Date and Time Operators > Duration];
  the invalid-interval rule under TQ-15.
- **Observed:** [src: PROBES-2026-10-22 RESULTS.md §49].
- **Layer:** spec behaviour for both the `0` and the error; the author error is in building the
  interval.
- **Pass if:** it does not blame the engine for the error.
- **Skill:** [datetime.md](../resources/datetime.md#duration-vs-difference),
  [intervals.md](../resources/intervals.md#invalid-intervals-and-unit-intervals).

## Arithmetic, dates and times

### TQ-21. Integer overflow

- **Expected:** the spec says `null`; engine 5.4.0 returns `-2147483648`. Compute in Decimal, or in
  Long within its range.
- **Spec:** "If the result of the addition cannot be represented (i.e. arithmetic overflow), the
  result is null." (same in 1.4, 2.0)
  [src: CQL-1.5.3 09-b-cqlreference > Arithmetic Operators > Add].
- **Observed:** [src: PROBES-2026-10-22 RESULTS.md §30] [src: PROBES-2026-10-22 RESULTS.md §33].
- **Skill:**
  [nulls.md](../resources/nulls.md#gotcha-integer-and-long-overflow-wraps-instead-of-returning-null).

### TQ-22. Precision comparisons

- **Expected:** `true`. The ELM `After` compares precision by precision and stops at the first
  difference; the day (15 after 11) differs before the hour is reached. The Author's Guide says the
  result is null; the formal text governs, so the guide example is wrong (same in 1.4; **2.0:** adds
  the seconds-and-milliseconds note).
- **Spec:** [src: CQL-1.5.3 04-logicalspecification > Interval Operators > After].
- **Observed:** [src: PROBES-2026-10-22 RESULTS.md §22].
- **Pass if:** it answers from the formal `After` text, not the guide example.
- **Skill:** [datetime.md](../resources/datetime.md#comparing-values-of-different-precision).

### TQ-23. Milliseconds

- **Expected:** the spec gives `true` (seconds and milliseconds are one decimal precision, and
  `0.0` equals `0`); engine 5.4.0 gives `null`.
- **Spec:** the combined-precision rule (same in 1.4, 2.0)
  [src: CQL-1.5.3 04-logicalspecification > Comparison Operators > Equal].
- **Observed:** [src: PROBES-2026-10-22 RESULTS.md §43].
- **Skill:**
  [datetime.md](../resources/datetime.md#gotcha-a-value-with-milliseconds-and-one-without-compare-as-null).
