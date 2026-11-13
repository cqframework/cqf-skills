# CQL Null Semantics, by Operator Family

Baseline: CQL 1.5.3. Untagged statements hold in 1.4, 1.5.3 and 2.0.0.
Sources: CQL-1.4, CQL-1.5.3, CQL-TESTS, CQFW-5.4.0, PROBES-2026-10-22

How each family of operators treats `null`. Source IDs are in [SOURCES.md](SOURCES.md). Interval
null bounds are in [intervals.md](intervals.md); null in type tests is in
[type-system.md](type-system.md#null-and-is); aggregates and list functions are summarised per
function in [operators.md](operators.md#aggregate-functions).

In 1.5.3, "CQL provides a special construct, null, to represent an unknown or missing value or
result", and "nulls will in general propagate" (same in 1.4; **2.0:** "keyword" for "construct")
[src: CQL-1.5.3 02-authorsguide > Values > Structured Values (Tuples) > Missing Information]. The
exceptions are what this file is about.

Observed behaviour comes from translator and engine 5.4.0 through the language server
[src: PROBES-2026-10-22 RESULTS.md §1].

The spec text below is the rule. Blocks marked **Gotcha** record where translator or engine 5.4.0
departs from it, or where the spec leaves the answer open, each with a workaround; see
[diagnosing.md](diagnosing.md) for how the layer was decided.

## Summary

| Family | Null in | Result | Section |
| --- | --- | --- | --- |
| `and` / `or` | one operand | three-valued: `null and false` = `false`, `null or true` = `true`, otherwise `null` | [Logic](#logical-operators) |
| `not`, `xor`, comparison, arithmetic | any operand | `null` | [Logic](#logical-operators), [Arithmetic](#arithmetic-and-strings) |
| `=` | either operand | `null`; but lists treat null elements as equal | [Equality](#equality-and-equivalence) |
| `~` | either or both | never null: `null ~ null` = `true`, `1 ~ null` = `false` | [Equality](#equality-and-equivalence) |
| `&` | either operand | treated as `''` | [Arithmetic](#arithmetic-and-strings) |
| `is null`, `is true`, `is false`, `Coalesce` | — | never null | [Null tests](#null-tests-and-coalesce) |
| `if` / `case` condition | condition | treated as false | [Conditionals](#conditionals) |
| `where` | condition | element excluded | [Queries](#queries) |
| `in` / `contains` (lists) | the element | `true` if the list holds a null (1.5+) | [Membership](#list-membership-and-set-operators) |
| `union` / `intersect` / `except` | a list | null list = empty for `union` and the right of `except`; `null` for `intersect` and the left of `except` | [Membership](#list-membership-and-set-operators) |
| query source | every source | `null` (1.5+) | [Queries](#queries) |

## Logical operators

`and`: "If either argument is false, the result is false; if both arguments are true, the result is
true; otherwise, the result is null." `or` is the dual: true if either is true, false if both are
false, otherwise null (same in 1.4, 2.0)
[src: CQL-1.5.3 09-b-cqlreference > Logical Operators > And]
[src: CQL-1.5.3 09-b-cqlreference > Logical Operators > Or]. "CQL does not prescribe
short-circuit evaluation of logical operators."

`not`: "Otherwise, the result is null." `xor`: true only if exactly one argument is true and the
other false; "Otherwise, the result is null." `implies`: "If the left operand evaluates to false,
this operator returns true" (same in 1.4, 2.0)
[src: CQL-1.5.3 09-b-cqlreference > Logical Operators > Not]
[src: CQL-1.5.3 09-b-cqlreference > Logical Operators > Xor]
[src: CQL-1.5.3 09-b-cqlreference > Logical Operators > Implies].

Observed: as specified, including `false implies null` = `true`, `null implies true` = `true` and
`null implies false` = `null` [src: PROBES-2026-10-22 RESULTS.md §27].

The trap: `not (X > 1)` is not *everything that is not greater than 1*. When `X` is null both
`X > 1` and `not (X > 1)` are null, so a `where` keeps the element under neither
[src: PROBES-2026-10-22 RESULTS.md §32].

## Equality and equivalence

`=`: "returns true if the arguments are equal; false if the arguments are known unequal, and null
otherwise", and "If either argument is null, the result is null." (same in 2.0 for these
sentences) [src: CQL-1.5.3 09-b-cqlreference > Comparison Operators > Equal]. `!=` is "a shorthand
for invocation of logical negation (not) of the equal operator", so it is null whenever `=` is.

`~`: "returns true if the arguments are equivalent in value, or if they are both null; and false
otherwise", and "this operator will always return true or false, even if either or both of its
arguments are null, or contain null components." (1.5+ for the time-valued quantity rules in the
same section; **2.0:** adds a note on unit conversion steps)
[src: CQL-1.5.3 09-b-cqlreference > Comparison Operators > Equivalent]. "Note that null is not
equivalent to the empty string ('')".

Observed [src: PROBES-2026-10-22 RESULTS.md §28]:

| CQL | `=` | `~` |
| --- | --- | --- |
| `(null as Integer)` with `(null as Integer)` | `null` | `true` |
| `1` with `null` | `null` | `false` |
| `''` with `(null as String)` | — | `false` |
| `{ null, 1 }` with `{ null, 1 }` | `true` | `true` |

#### Gotcha: untyped `null = null` does not compile

- **Symptom:** `null = null` and `null ~ null` fail with `Call to operator
  Equal(System.Any, System.Any) is ambiguous with: …`.
- **Probe:** `testNlUntypedNullEq`, `testNlUntypedNullEquiv`, against `testNlTypedNullEq`
  (`(null as Integer) = (null as Integer)`, which is `null`)
  [src: PROBES-2026-10-22 RESULTS.md §28].
- **Spec:** decides: both appear as examples in the spec (`NullEqualIsNull`,
  `NullEquivalentIsTrue`), under the rule quoted above.
- **Well-formed?** Yes: the spec uses them.
- **Layer:** translator.
- **Evidence:** both are CQL-TESTS tests
  [src: CQL-TESTS CqlComparisonOperatorsTest.xml SimpleEqNullNull]
  [src: CQL-TESTS CqlComparisonOperatorsTest.xml EquivNullNull].
- **Workaround:** type at least one operand: `(null as Integer) = …`.
- **Affects:** translator 5.4.0.

### Lists

`=` on lists compares element by element (same in 1.4, 2.0) "with the exception that null elements
are considered equal" [src: CQL-1.5.3 09-b-cqlreference > Comparison Operators > Equal]. The List
Operators entry for Equal also says "If either argument is null, or contains null elements, the
result is null", so the 1.5.3 CQL Reference contradicts itself; the ELM `Equal`, which governs,
keeps the null-elements exception in all three versions (see
[operators.md](operators.md#list-equality) for the per-version detail and tests). Observed, as the
formal text says: `{ null } = { null }` is `true`.

### Tuples

1.5.3: tuple equality is true "if and only if the tuples are of the same type, and the values for
all elements that have values, by name, are equal, defined as a conjunction of equality
comparisons". **1.4:** the same sentence without "defined as a conjunction of equality comparisons".
1.5.3 adds four examples whose names give the expected results: `TupleEqualBothNullTrue`
(`{ x: 1, y: null } = { x: 1, y: null }`), `TupleEqualBothNullFalse`, `TupleEqualMixedNullNull`
(`{ x: 1, y: 1 } = { x: null, y: 1 }`) and `TupleEqualMixedNullFalse`
(`{ x: 1, y: 1 } = { x: null, y: 2 }`)
[src: CQL-1.5.3 09-b-cqlreference > Comparison Operators > Equal]
[src: CQL-1.4 09-b-cqlreference > Comparison Operators > Equal].

Read literally, 1.5.3's "a conjunction of equality comparisons" makes `TupleEqualBothNullTrue` null
(`null = null` is null); the example name says true. "Elements that have values" makes it true. The
2.0-era tests take the "have values" reading
[src: CQL-TESTS CqlComparisonOperatorsTest.xml TupleEqJohn1John1WithBothNamesNull].

Observed [src: PROBES-2026-10-22 RESULTS.md §28]:

| CQL | Example name | Engine |
| --- | --- | --- |
| `Tuple { x: 1, y: null } = Tuple { x: 1, y: null }` | …BothNullTrue | `true` |
| `Tuple { x: 1, y: 1 } = Tuple { x: null, y: 1 }` | …MixedNullNull | `null` |
| `Tuple { x: 1, y: 1 } = Tuple { x: null, y: 2 }` | …MixedNullFalse | `null` |
| `Tuple { x: 1, y: 1 } ~ Tuple { x: null, y: 1 }` | — | `false` |

#### Gotcha: tuple `=` with a null element on one side is null

- **Symptom:** `Tuple { x: 1, y: 1 } = Tuple { x: null, y: 2 }` is `null`, although `y` already
  differs.
- **Probe:** `testNlEquality`, the table above, against `…BothNullTrue`
  [src: PROBES-2026-10-22 RESULTS.md §28].
- **Spec:** silent or self-contradictory at 1.5.3: as a conjunction, `1 = 2` is false, so
  `null and false` is false, which matches the example name `…MixedNullFalse`; "elements that have
  values" leaves the mixed case open. The ELM `Equal` has the same "conjunction" wording (same in
  2.0; **1.4:** without it) [src: CQL-1.5.3 04-logicalspecification > Comparison Operators > Equal].
- **Well-formed?** Yes.
- **Layer:** spec gap; the engine returns null in both mixed cases.
- **Evidence:** the two readings above give different answers for the same row.
- **Workaround:** use `~` when nulls in tuples should compare; it gives `true` or `false`
  (`false` for the mixed case) [src: PROBES-2026-10-22 RESULTS.md §28].
- **Affects:** engine 5.4.0.

## Arithmetic and strings

Arithmetic: "If either argument is null, the result is null." Division: "If the result of the
division cannot be represented, or the right argument is 0, the result is null." (same in 1.4, 2.0)
[src: CQL-1.5.3 09-b-cqlreference > Arithmetic Operators > Divide]. Overflow: "If the result of the
addition cannot be represented (i.e. arithmetic overflow), the result is null." (1.5+ for the Long
overloads in the same section) [src: CQL-1.5.3 09-b-cqlreference > Arithmetic Operators > Add].

Observed [src: PROBES-2026-10-22 RESULTS.md §30]: `5 / 0`, `5 div 0` and `5 mod 0` are null, as
specified.

#### Gotcha: Integer and Long overflow wraps instead of returning null

- **Symptom:** `2147483647 + 1` and `(maximum Integer) + 1` are `-2147483648`, `2147483647 * 2` is
  `-2`, and `9223372036854775807L + 1L` is `-9223372036854775808`. `Sum` of Integers wraps too. A
  sum of large counts or values can therefore turn negative without warning.
- **Probe:** `testNlOverflow` [src: PROBES-2026-10-22 RESULTS.md §30]; `testWaOverflow2`
  [src: PROBES-2026-10-22 RESULTS.md §33].
- **Spec:** decides: null on overflow (above).
- **Well-formed?** Yes.
- **Layer:** engine. The ELM is a plain `Add` of two Integer literals.
- **Evidence:** CQL-TESTS expects null
  [src: CQL-TESTS CqlArithmeticFunctionsTest.xml AddIntegerOverflow]. The engine adds with plain
  machine integers
  [src: CQFW-5.4.0 engine/src/commonMain/kotlin/org/opencds/cqf/cql/engine/elm/executing/AddEvaluator.kt:34-37].
- **Workaround:** compute in Decimal, or in Long only where values stay within its range (Long wraps
  at its own maximum): `ToDecimal(x) + y`, or `Sum(L X return all ToDecimal(X))`
  [src: PROBES-2026-10-22 RESULTS.md §33].
- **Affects:** engine 5.4.0.

Strings: "When using +, if either argument is null, the result is null. When using &, null arguments
are treated as an empty string ('')." (same in 1.4, 2.0)
[src: CQL-1.5.3 09-b-cqlreference > String Operators > Concatenate]. Observed: `'a' + null` is
`null`, `'a' & null` is `'a'` [src: PROBES-2026-10-22 RESULTS.md §30]. Aggregates skip null
elements: `Count({ null, 1 })` is `1`, and `Sum` of only nulls is `null`
([operators.md](operators.md#aggregate-functions)).

`Combine`: "If the separator argument is null, it is ignored." and "For consistency with aggregate
operator behavior, null elements in the input list are ignored." (same in 2.0; **1.4:** "If either
argument is null, or the source list is empty, the result is null.", so a null separator gives
null) [src: CQL-1.5.3 09-b-cqlreference > String Operators > Combine]
[src: CQL-1.4 09-b-cqlreference > String Operators > Combine]. The 1.4 ELM text also contradicts
the 1.4 reference on elements: "If either argument is null, or any element in the source list of
strings is null, the result is null." (**1.4 only**)
[src: CQL-1.4 04-logicalspecification > String Operators > Combine].

#### Gotcha: `Combine` returns null for a null element or a null separator

- **Symptom:** `Combine({ 'a', null, 'b' }, '-')`, `Combine({ 'a', null, 'b' })` and
  `Combine({ 'a', 'b' }, null as String)` are all `null`. The one-argument form without nulls
  works: `Combine({ 'a', 'b' })` is `ab` [src: PROBES-2026-10-22 RESULTS.md §53].
- **Probe:** `testHoCombine`, against `Combine({ 'a', 'b' }, '-')`, which is `a-b`
  [src: PROBES-2026-10-22 RESULTS.md §53].
- **Spec:** decides at 1.5.3: both are ignored (above). The engine matches the 1.4 ELM text.
- **Well-formed?** Yes.
- **Layer:** engine.
- **Evidence:** the engine returns null for a null separator and for any null element
  [src: CQFW-5.4.0 engine/src/commonMain/kotlin/org/opencds/cqf/cql/engine/elm/executing/CombineEvaluator.kt:20-34];
  CQL-TESTS expects nulls to be ignored [src: CQL-TESTS CqlStringOperatorsTest.xml CombineWithNulls]
  [src: CQL-TESTS CqlStringOperatorsTest.xml CombineNullSeparator].
- **Workaround:** filter the nulls and coalesce the separator:
  `Combine((L) X where X is not null, Coalesce(Sep, ''))` gives `ab` for a null `Sep`, and `a-b`
  with `'-'` [src: PROBES-2026-10-22 RESULTS.md §53].
- **Affects:** engine 5.4.0.

`Substring`: "If stringToSub or startIndex is null, or startIndex is out of range, the result is
null." (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > String Operators > Substring]. The
text does not say whether a start index equal to the length is out of range. The tests disagree:
`Substring('ab', 2)` expects `null` [src: CQL-TESTS CqlStringOperatorsTest.xml SubstringAB2], but
`Substring('', 0)` expects `''` [src: CQL-TESTS CqlStringOperatorsTest.xml SubstringEmptyAnd0].
Observed: `Substring('abc', 2)` is `c`, and `Substring('abc', 3)` and `Substring('abc', 5)` are
`null` [src: PROBES-2026-10-22 RESULTS.md §58].

## Null tests and Coalesce

`is null`, `is true` and `is false` never return null: "If the argument evaluates to true, the
result is true; otherwise, the result is false." (same in 1.4, 2.0)
[src: CQL-1.5.3 09-b-cqlreference > Nullological Operators > IsTrue]
[src: CQL-1.5.3 09-b-cqlreference > Nullological Operators > IsFalse].
`Coalesce` "returns the first non-null result in a list of arguments. If all arguments evaluate to
null, the result is null." (same in 1.4, 2.0)
[src: CQL-1.5.3 09-b-cqlreference > Nullological Operators > Coalesce]. Observed: as specified,
including the list form `Coalesce({ null, 2, 3 })` = `2` [src: PROBES-2026-10-22 RESULTS.md §27]
[src: PROBES-2026-10-22 RESULTS.md §31].

Use `X is true` where a null condition must be explicitly false outside a `where` or `if`, for
example inside `exists` or when returning a Boolean.

## Conditionals

"Note that if the condition evaluates to null, it is interpreted as false." For a selected case,
"if the source expression in a selected case is null, no condition will compare equal and the
result will be the else expression. If any case item is null, it will not compare equal to the
comparand." (same in 1.4, 2.0) [src: CQL-1.5.3 03-developersguide > Conditional Expressions].
Observed: `if (null as Boolean) then 1 else 2` is `2`, a null comparand takes the `else`, and a
null `when` item is skipped [src: PROBES-2026-10-22 RESULTS.md §31].

## Queries

`where`: "If the condition evaluates to true, the element is included. Otherwise, the element is
excluded from the result." (same in 1.4, 2.0)
[src: CQL-1.5.3 05-languagesemantics > Query Evaluation > Iteration > Where Clause].

Null sources (1.5+): "If all the sources of a query evaluate to null, the result is null", for
example a query over `(null as List<…>)` [src: CQL-1.5.3 03-developersguide > Non-Retrieve Queries].
1.4 has no such rule. A `return` clause does not run for a null source.

Sorting, in 1.5.3: "When the data being sorted includes nulls, they are considered lower than any
non-null value" (**1.4:** "they are sorted first"; the effect is the same)
[src: CQL-1.5.3 02-authorsguide > Queries > Sorting].

Observed [src: PROBES-2026-10-22 RESULTS.md §32]:

| CQL | Result |
| --- | --- |
| `({ 1, null, 3 }) X where X > 1` | `[3]` |
| `({ 1, null, 3 }) X where not (X > 1)` | `[1]` (the null is in neither) |
| `({ 3, null, 1 }) X sort asc` / `sort desc` | `[null, 1, 3]` / `[3, 1, null]` |
| `({ 1, null, null }) X return X` / `return all X` | `[1, null]` / `[1, null, null]` |
| `(null as List<Integer>) X return X` / `(List<Integer> { }) X return X` | `null` / `[]` |
| `exists (({ 1, 2 }) X return (null as Integer))` | `false` |

The last row combines two rules: `return` is distinct by default, leaving `{ null }`, and `exists`
counts only non-null elements.

## List membership and set operators

`in`: "If the first argument is null, the result is true if the list contains any null elements,
and false otherwise. If the second argument is null, the result is false." `contains` is the
mirror image (1.5+; **1.4:** a null element gave null: "If the first argument is null, the result is
null" for `in`, and "If the second argument is null, the result is null" for `contains`)
[src: CQL-1.5.3 09-b-cqlreference > List Operators > In]
[src: CQL-1.5.3 09-b-cqlreference > List Operators > Contains]
[src: CQL-1.4 09-b-cqlreference > List Operators > In]
[src: CQL-1.4 09-b-cqlreference > List Operators > Contains].
CQL-TESTS expects `null in { 1, null }` to be `true` (1.5+)
[src: CQL-TESTS CqlListOperatorsTest.xml InNullAnd1Null].

The set operators treat a null list differently each (same in 1.4; **2.0:** adds `all` and
`all ordered` forms) [src: CQL-1.5.3 09-b-cqlreference > List Operators > Union]
[src: CQL-1.5.3 09-b-cqlreference > List Operators > Intersect]
[src: CQL-1.5.3 09-b-cqlreference > List Operators > Except]:

| Operator | Null list | Null elements |
| --- | --- | --- |
| `union` | "considered an empty list" | "null elements are considered equal" |
| `intersect` | "the result is null" | considered equal, so `{ null, 1, 3 } intersect { null, 3, 7 }` is `{ null, 3 }` |
| `except` | left null: "the result is null"; right null: treated "as though the second argument was an empty list" | considered equal |

Observed: as specified [src: PROBES-2026-10-22 RESULTS.md §29]. With nulls in both operands,
`{ null as Integer, 1 } union { null as Integer }` is `[null, 1]`, and `Count` of it is `1`, since
`Count` skips nulls [src: PROBES-2026-10-22 RESULTS.md §57].

## Where the spec is silent or self-contradictory

Each was searched in 1.4, 1.5.3 and 2.0.0:

| Question | Finding |
| --- | --- |
| Whether a `Substring` start index equal to the length is out of range | silent; the tests disagree, and the engine says yes |
| Tuple `=` with a null element on one side only | 1.5.3's "conjunction" wording and its example names disagree; the engine returns null in both mixed cases |
