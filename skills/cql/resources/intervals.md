# CQL Intervals: Bounds, Null Bounds and Validity

Baseline: CQL 1.5.3. Untagged statements hold in 1.4, 1.5.3 and 2.0.0.
Sources: CQL-1.4, CQL-1.5.3, CQL-2.0.0, CQL-TESTS, CQFW-5.4.0, PROBES-2026-10-22, CQLWIKI

Open and closed bounds, null bounds, the "maximum" and "unknown" intervals, invalid intervals, and
how interval operators treat null bounds. Source IDs are in [SOURCES.md](SOURCES.md). The interval
operators themselves (`before`, `meets`, `starts`, `union`, …) are summarised in
[operators.md](operators.md#timing--interval-operators).

Observed behaviour comes from translator and engine 5.4.0 through a language server that compiles
with list promotion and demotion disabled [src: PROBES-2026-10-22 RESULTS.md §1].

## Bounds

"inclusive (closed) boundaries are indicated with square brackets, and exclusive (open) boundaries
are indicated with parentheses" (same in 1.4, 2.0)
[src: CQL-1.5.3 02-authorsguide > Values > Interval Values]. `start of` and `end of` apply the
bracket; the `low` and `high` properties do not: `start of` an open low bound "returns the successor
of the low value of the interval", and `end of` an open high bound returns "the predecessor of the
high value" (same in 1.4) [src: CQL-1.5.3 09-b-cqlreference > Interval Operators > Start]
[src: CQL-1.5.3 09-b-cqlreference > Interval Operators > End].

Touching intervals follow the same rule. `meets` and `overlaps` read bounds through `start of` and
`end of`: "This operator uses the semantics described in the Start and End operators to determine
interval boundaries." (same in 1.4; **2.0:** adds a note on null boundaries)
[src: CQL-1.5.3 09-b-cqlreference > Interval Operators > Meets]. Observed, as specified
[src: PROBES-2026-10-22 RESULTS.md §55]:

| CQL | Result |
| --- | --- |
| `Interval[1, 5] overlaps Interval[5, 10]` | `true` |
| `Interval[1, 5) overlaps Interval[5, 10]` | `false` |
| `Interval[1, 5) meets Interval[5, 10]` | `true` (the end of the first is 4) |
| `Interval[1, 5] meets Interval[5, 10]` | `false` (they share 5) |

#### Gotcha: printed intervals show the predecessor of an open bound

- **Symptom:** `Interval[@2026-01-01T15:00, @2026-01-01T15:01)` prints as
  `[2026-01-01T15:00, 2026-01-01T15:00)`.
- **Probe:** `testIvMinuteBounds`: `.low` is `15:00`, `.high` is `15:01`, `end of` is `15:00`; the
  closed form prints `[…15:00, …15:01]` [src: PROBES-2026-10-22 RESULTS.md §19].
- **Spec:** silent on how an interval is displayed.
- **Well-formed?** Yes.
- **Layer:** environment (the language server's display of results).
- **Evidence:** the value's `.high` differs from the printed bound.
- **Workaround:** read bounds with `.low`, `.high`, `start of` and `end of`, not from the printed
  value.
- **Affects:** CQL language server 4.11.0-SNAPSHOT output.

## Bound types

ELM `Interval`: "The static type of the low bound determines the type of the interval, and the high
bound must be of the same type." (same in 1.4, 2.0)
[src: CQL-1.5.3 04-logicalspecification > Interval Operators > Interval]. Implicit conversion still
applies: Date converts to DateTime (same in 1.4, 2.0 for this row)
[src: CQL-1.5.3 03-developersguide > Types > Conversion > Implicit Conversions], and the Date takes
"the time components unspecified" (**1.4:** "the time components set to zero")
[src: CQL-1.5.3 09-b-cqlreference > Type Operators > ToDateTime]
[src: CQL-1.4 09-b-cqlreference > Type Operators > ToDateTime].

Observed [src: PROBES-2026-10-22 RESULTS.md §46]: `Interval[1, 'a']` fails to compile
(`Low and high boundary values of an interval must be of the same type.`), against `Interval[1, 2]`;
`Interval[@2026-01-01, @2026-01-02T00:00:00Z]` compiles to an `Interval<DateTime>` with `ToDateTime`
over the low bound.

#### Gotcha: a Date bound with a DateTime bound can be an invalid interval

- **Symptom:** at evaluation offset `-04:00`, `Interval[@2026-01-01, @2026-01-02T00:00:00Z]` fails
  at run time with `Invalid Interval - the ending boundary (@2026-01-02T00:00:00) must be greater
  than or equal to the starting boundary (@2026-01-01).`
- **Probe:** `testTqIntervalMixedDate`, against `testTqIntervalMixedDateLocal` (the high bound at
  `-04:00`) and `testTqIntervalMixedDateLater` (a later day), which both build the interval;
  `@2026-01-01 <= @2026-01-02T00:00:00Z` is `null` [src: PROBES-2026-10-22 RESULTS.md §46].
- **Spec:** the end "must be greater than or equal to the starting boundary" (above); silent on a
  comparison that is null. At 1.5.3 it is null: normalised to `-04:00`, the high bound is 20:00 on
  1 January, the day matches, and the converted Date has no hour. **1.4:** the Date is midnight, so
  the interval is valid.
- **Well-formed?** Yes.
- **Layer:** spec gap; the engine treats a null bound comparison as invalid, and whether it is null
  depends on the evaluation offset (environment).
- **Evidence:** the ELM is correct; the controls differ by one value each.
- **Workaround:** give both bounds the same type and precision, with explicit offsets, for example
  two DateTimes such as `Interval[@2026-03-01T00:00:00Z, @2026-04-01T00:00:00Z]`
  [src: PROBES-2026-10-22 RESULTS.md §48].
- **Affects:** engine 5.4.0; depends on the evaluation offset.

## A null bound: `Interval[x, null]` vs `Interval[x, null)`

The bracket decides what a null bound means. These two intervals are not the same value.

From the ELM Interval selector
[src: CQL-1.5.3 04-logicalspecification > Interval Operators > Interval]:

> "If the high bound of the interval is null and open, the high bound of the interval is unknown
> and represented as an uncertainty from the low boundary (inclusive) to the maximum value for the
> point type; computations involving the high boundary may result in null."
>
> "If the high bound of the interval is null and closed, the interval is interpreted to end at the
> maximum value of the point type, and computations involving the high boundary will be performed
> with that interpretation."

The low bound is symmetric (minimum value of the point type).

From `End` in the CQL Reference: "If the high boundary of the interval is open, this operator
returns the predecessor of the high value of the interval. Note that if the high value of the
interval is null, the result is null." and, for a closed bound, "Otherwise, the result is the
maximum value of the point type of the interval." (same in 1.4; **2.0:** see below)
[src: CQL-1.5.3 09-b-cqlreference > Interval Operators > End].

**Version differences**

| Topic | 1.4 | 1.5.3 | 2.0.0 |
| --- | --- | --- | --- |
| ELM selector, open null bound | "interpreted as unknown, and computations involving the low boundary will result in null" | "interpreted as unknown and represented as an uncertainty …; computations involving the low boundary may result in null" | same as 1.5.3 |
| `start of` / `end of`, open null bound | null | null | "returns an uncertainty", e.g. `end of Interval[1, null)` is `uncertainty[1, 2147483647]` |
| `start of` / `end of`, closed null bound | minimum / maximum of the point type | same | same; adds that if the point type is "unknown, a choice of types, or Any" the result is null |

Sources: [src: CQL-1.4 04-logicalspecification > Interval Operators > Interval]
[src: CQL-2.0.0 04-logicalspecification > Interval Operators > Interval]
[src: CQL-1.4 09-b-cqlreference > Interval Operators > End]
[src: CQL-2.0.0 09-b-cqlreference > Interval Operators > End]
[src: CQL-2.0.0 09-b-cqlreference > Interval Operators > Start].

The formal ELM `End` operator decides it for 1.5.3, in the same words as the CQL Reference: "If the
high boundary of the interval is open, this operator returns the Predecessor of the high value of
the interval. Note that if the high value of the interval is null, the result is null." (same in
1.4; **2.0:** returns an uncertainty)
[src: CQL-1.5.3 04-logicalspecification > Interval Operators > End]. The selector's "may result in
null" is consistent with that. So at 1.5.3 `end of Interval[x, null)` is null; at 2.0.0 it is an
uncertainty. This is a version difference, not a gap.

Observed, as the 1.5.3 text says [src: PROBES-2026-10-22 RESULTS.md §16]:

| CQL | Result |
| --- | --- |
| `end of Interval[@2025-01-01T00:00:00, null]` | `9999-12-31T23:59:59.999+00:00` |
| `end of Interval[@2025-01-01T00:00:00, null)` | `null` |
| `end of Interval[1, null]` / `end of Interval[1, null)` | `2147483647` / `null` |
| `start of Interval[null, 5]` / `start of Interval(null, 5]` | `-2147483648` / `null` |
| `Interval[x, null].high` and `Interval[x, null).high` | `null` (raw bound, either bracket) |

## Operators with a null bound

For `in` (and `during` with a point), the 1.5.3 text says: "For closed interval boundaries, if the
interval boundary is null, the result of the boundary comparison is considered true." and "If the
first argument is null, the result is null. If the second argument is null, the result is false."
(same in 1.4, which has the same null rules; 1.5.3 adds `during` as an alias and rewords the
inclusion condition; **2.0:** adds that comparisons follow the point type's semantics)
[src: CQL-1.5.3 09-b-cqlreference > Interval Operators > In].

Observed [src: PROBES-2026-10-22 RESULTS.md §16]:

| CQL | Closed `null]` | Open `null)` |
| --- | --- | --- |
| `@2026-06-01 during Interval[@2025-01-01, null…` | `true` | `null` |
| `Interval[@2026-02-01, @2026-03-01] during Interval[@2025-01-01, null…` | `true` | `null` |
| `Interval[@2026-02-01, @2026-03-01] overlaps Interval[@2025-01-01, null…` | `true` | `null` |
| `end of Interval[@2025-01-01, null…] after @2026-12-31` | `true` | `null` |
| `Interval[@2024-02-01, @2024-03-01] overlaps Interval[@2025-01-01, null)` | — | `false` |

The last row shows that an open null bound gives `null` only when the unknown bound matters: an
interval that ends before the known low bound does not overlap, whatever the high bound is.

With the null-ended interval on the left, the same holds: for
`Interval[@2026-03-01T00:00:00Z, null…] during Interval[@2026-01-01T00:00:00Z, @2026-12-31T00:00:00Z]`
the closed form is `false` (its end is the maximum, outside the window) and the open form is `null`
[src: PROBES-2026-10-22 RESULTS.md §48].

The trap: an interval built from a start-only period. If a library builds `Interval[start, null]`,
the event runs to the end of time and is `during` any later window; if it builds `Interval[start,
null)`, the same questions return `null`, and a `where` treats `null` as false. Check which bracket
the conversion function uses before reasoning about results.

## Type tests on an interval with a null bound

`is` tests the run-time type: "If the run-time type of the argument is the same as or derived from
the type being tested, the result of the operator is true" (**1.4:** "is of the type being tested")
[src: CQL-1.5.3 09-b-cqlreference > Type Operators > Is]. The selector rule above fixes the static
type of `Interval[1, null]` as `Interval<Integer>`, but no text gives the run-time type of an
interval value with a null bound, and a static type does not decide `is` for a null: (2.0+) "the
expression (null as Integer) is Integer is equivalent to null is Integer and also returns flase."
(sic) [src: CQL-2.0.0 09-b-cqlreference > Type Operators > Is]. A derivation of `true` from the
selector rule is an inference, not spec text.

#### Gotcha: an interval with a null bound fails `is Interval<T>`

- **Symptom:** `Interval[1, null] is Interval<Integer>` is `false`, open or closed. Logic that tests
  the type before using the interval skips it silently.
- **Probe:** `testTqIntervalNullBoundIs`, against `Interval[1, 5] is Interval<Integer>`, which is
  `true` [src: PROBES-2026-10-22 RESULTS.md §47].
- **Spec:** silent (above).
- **Well-formed?** Yes.
- **Layer:** spec gap; engine 5.4.0's choice.
- **Evidence:** the engine tests both bounds against the point type, and a null bound fails
  [src: CQFW-5.4.0 engine/src/commonMain/kotlin/org/opencds/cqf/cql/engine/elm/executing/IsEvaluator.kt:104-121].
  Upstream changed this after 5.4.0 so that the bound that is present decides, in a commit dated
  2026-10-08 that is in no release yet. With both bounds null the result is also `false`, because
  the engine treats that interval as null (below).
- **Workaround:** test the bound that is present instead of the interval: `Interval[1, null].low is
  Integer` is `true` [src: PROBES-2026-10-22 RESULTS.md §52]. Or avoid the type test where the
  static type already says it.
- **Affects:** engine 5.4.0.

## Both bounds null: the maximum and the unknown interval

The spec text gives `Interval[null, null]` a meaning: both bounds closed and null means minimum to
maximum. **2.0:** names it: "attempting to extract a point from the maximum interval"
(`Interval[null, null]`) "will result in an error"
[src: CQL-2.0.0 09-b-cqlreference > Interval Operators > Point From]. 1.4 and 1.5.3 do not name it.

CQL-TESTS follows the spec text. Tests are informative, and the spec text is authoritative
([spec/README.md](spec/README.md#citing-the-spec)):

| Expression | CQL-TESTS |
| --- | --- |
| `5 in Interval[null, null]` | `true` |
| `Interval[null, null] overlaps Interval[1, 10]` | `true` |
| `Interval[null, null] union Interval[1, 10]` | `Interval[null, null]` |
| `point from Interval[null, null]` | error |
| `Interval[1, 10] intersect Interval[5, null)` | `Interval[5, null)` |

No CQL-TESTS test evaluates `Interval[null, null]` on its own.

Sources: [src: CQL-TESTS CqlIntervalOperatorsTest.xml TestIntegerInMaxIntervalTrue]
[src: CQL-TESTS CqlIntervalOperatorsTest.xml TestMaxIntervalOverlapsTrue]
[src: CQL-TESTS CqlIntervalOperatorsTest.xml TestUnionMaxInterval]
[src: CQL-TESTS CqlIntervalOperatorsTest.xml TestPointFromMaxIntervalError]
[src: CQL-TESTS CqlIntervalOperatorsTest.xml TestIntersectNull].

#### Gotcha: an interval with both bounds null evaluates to null

- **Symptom:** `5 in Interval[null as Integer, null as Integer]` is `false`, and `overlaps`,
  `starts`, `union`, `start of` and `point from` on it are all `null`, whether the brackets are open
  or closed and whether the nulls are typed.
- **Probe:** `testIvSuiteDisputes`, `testIvTypedMax`, `testIvPointFromMax`; a single null bound is
  not affected [src: PROBES-2026-10-22 RESULTS.md §17].
- **Spec:** decides. Closed null bounds mean the minimum and maximum of the point type
  (same in 1.4; **2.0:** names the result the maximum interval, above)
  [src: CQL-1.5.3 04-logicalspecification > Interval Operators > Interval].
- **Well-formed?** Yes.
- **Layer:** engine. The ELM is a correct `Interval` with two `Null` bounds.
- **Evidence:** the engine returns null by design, with a TODO
  [src: CQFW-5.4.0 engine/src/commonMain/kotlin/org/opencds/cqf/cql/engine/elm/executing/IntervalEvaluator.kt:41-47];
  CQL-TESTS expects the spec's answers (table above).
- **Workaround:** write the bounds: `Interval[minimum Integer, maximum Integer]` (`5 in` it is
  `true`; the Date form works too) [src: PROBES-2026-10-22 RESULTS.md §33]. When one bound is a
  value, a single null bound is fine.
- **Affects:** engine 5.4.0.

The source:

```kotlin
// An interval with no boundaries is not an interval
// TODO: the spec states that it is possible to have an interval with null boundaries, but
// the ELM is not
// providing a way to get the Interval type
if (low == null && high == null) {
    return null
}
```

This engine therefore matches neither the spec text nor CQL-TESTS on the maximum interval. A single
null bound is not affected: `Interval[1, 10] intersect Interval[5, null)` gives `[5, null)`, as
CQL-TESTS expects.

## Invalid intervals and unit intervals

"the ending boundary must be greater than or equal to the starting boundary to construct a valid
interval. Attempting to specify an invalid Interval will result in a run-time error." The examples
include "Interval[1, 1) // Invalid interval, conflicting to say it both includes and excludes 1"
and "Interval[1, 1] // Unit interval containing only the point 1" (same in 1.4, 2.0)
[src: CQL-1.5.3 02-authorsguide > Values > Interval Values].

Observed [src: PROBES-2026-10-22 RESULTS.md §18]: `Interval[1, 1)`, `Interval[1, -1]` and
`Interval[@2026-01-01T15:00, @2026-01-01T15:00)` each raise the run-time error
`Invalid Interval - the ending boundary (…) must be greater than or equal to the starting boundary (…).`;
`Interval[1, 1]` is valid and `point from Interval[1, 1]` is `1`. The check compares `start` and
`end`, that is after applying successor and predecessor, so a half-open interval whose bounds are
equal fails
[src: CQFW-5.4.0 engine/src/commonMain/kotlin/org/opencds/cqf/cql/engine/runtime/Interval.kt:55-69].

The trap: computed bounds. An expression that builds `Interval[a, b)` from values that can be equal
(for example a same-day start and end, or a duration of zero) fails at run time for those inputs.
Pattern: use a closed bound, or guard it:
`if a < b then Interval[a, b) else Interval[a, b]` [src: PROBES-2026-10-22 RESULTS.md §42].

#### Gotcha: the invalid-interval message prints the raw bounds

- **Symptom:** `Interval[1, 1)` fails with `(1) must be greater than or equal to … (1)`, which looks
  satisfied.
- **Probe:** `testIvHalfOpenUnit` [src: PROBES-2026-10-22 RESULTS.md §18].
- **Spec:** the run-time error is required; its wording is not specified.
- **Well-formed?** No: the interval is invalid by the Author's Guide rule above.
- **Layer:** engine (message only; the error itself is correct).
- **Evidence:** the check compares the adjusted end (the predecessor of an open high bound, here 0)
  but prints the raw bounds (`runtime/Interval.kt:55-69`, cited above).
- **Workaround:** don't "fix" an interval whose printed bounds look correct; check its brackets.
- **Affects:** engine 5.4.0.

#### Gotcha: one run-time error fails every define in the run

- **Symptom:** a library with `"Fine": 1 + 1`, `Interval[1, 1)` and `"AlsoFine": 2 + 2` returns only
  the error, with no value for `Fine` or `AlsoFine`. For a patient whose data collapses computed
  bounds, this looks like a whole-case crash rather than one wrong value.
- **Probe:** `testIvOneBadDefine`, against the same library with `]` for `)`
  [src: PROBES-2026-10-22 RESULTS.md §21].
- **Spec:** requires the run-time error; silent on how an environment reports other expressions in
  the same evaluation.
- **Well-formed?** No, for the define that builds the invalid interval.
- **Layer:** environment (how `cql_execute` reports a failed library evaluation).
- **Evidence:** the control, which differs by one bracket, returns all three values.
- **Workaround:** guard computed bounds as above, so the error cannot occur
  [src: PROBES-2026-10-22 RESULTS.md §42].
- **Affects:** `cql_execute` through CQL language server 4.11.0-SNAPSHOT, engine 5.4.0.

## Pitfalls from the CQL Formatting and Usage Wiki

Guide text, not spec. Each page's date is from the wiki manifest.

- **`start` instead of `starts`** (2017-10-12). In the 2017 answer, a misspelled `start` was
  "basically a no-op", and with an interval in a `before`, "it chooses the end of the interval to do
  the comparison." [src: CQLWIKI QA-Keyword-Starts-vs-Start.md] Observed on translator 5.4.0: the
  misspelling is now a compile error (`Syntax error at start`), both at top level and inside a
  query; the second half still holds:
  `Interval[@2026-01-01, @2026-01-10] 3 days or less before @2026-01-03` is `false`, because the end
  (January 10) is compared [src: PROBES-2026-10-22 RESULTS.md §20].
- **Collapse with a closed null end** (Cooking with CQL session 50, 2021; page dated 2026-04-26).
  The session's results show a closed null end collapsing to the end of time,
  `Test1=[Interval[2021-01-06, 9999-12-31]]`
  [src: CQLWIKI Cooking-with-CQL-Q&A-Date-and-Time-Calculations.md]. Observed: the same; with an
  open null end the intervals are not merged [src: PROBES-2026-10-22 RESULTS.md §20].
- **An interval with null for both bounds** (session 48, 2020; page dated 2026-04-26). The answer
  says such an interval "is not a null interval; it is an interval with null boundaries"
  [src: CQLWIKI Cooking-with-CQL-Q&A-Date-and-Time-Calculations.md]. That agrees with the spec text,
  but not with this engine, which returns `null` for it (see above).

## Where the spec is silent

Each was searched in 1.4, 1.5.3 and 2.0.0:

| Question | Finding |
| --- | --- |
| How a printed interval should show an open bound | silent (tooling) |
| A compile-time check for `Interval[a, a)` | silent; the Author's Guide describes a run-time error only |
| The run-time type of an interval with a null bound, under `is` | silent; see [Type tests on an interval with a null bound](#type-tests-on-an-interval-with-a-null-bound) |
| Whether an interval whose bound comparison is null is valid | silent; see [Bound types](#bound-types) |
