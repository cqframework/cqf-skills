# Answers: CQL Skill Held-Out Questions

Target: a CQL 1.5 engine (translator and engine 5.4.0, `compatibilityLevel` "1.5"), so 1.5.3 is
the governing text. 1.4 and 2.0.0 are quoted where the change lists show a difference. Sources are
the skill's verbatim spec copy, its conformance tests, and the recorded probes
(`resources/probes/2026-10-22/RESULTS.md`, cited as "PROBES §n"). I ran no CQL. Where I would
want engine confirmation, I say which probe I would run and do not guess the result.

## HO-1

**Answer (spec, 1.5.3):**

| Expression | Result | Why |
| --- | --- | --- |
| `Interval[1, 5] overlaps Interval[5, 10]` | `true` | end 5 >= start 5, and start 1 <= end 10 |
| `Interval[1, 5) overlaps Interval[5, 10]` | `false` | end of `[1, 5)` is 4; 4 >= 5 is false; the intervals share no point |
| `Interval[1, 5) meets Interval[5, 10]` | `true` | end 4 = predecessor(5) = 4 |
| `Interval[1, 5] meets Interval[5, 10]` | `false` | end 5 is not predecessor(5) = 4, and start 1 is not successor(10) = 11 |

For integer intervals, closed intervals that touch at a shared point *overlap* and do not *meet*.
Intervals that are adjacent with no shared point *meet* and do not *overlap*.

**Spec text:**

> CQL 1.5.3, [Interval Operators > Overlaps](https://cql.hl7.org/N1A/09-b-cqlreference.html#overlaps):
> "The overlaps operator returns true if the first interval overlaps the second. More precisely,
> if the starting or ending point of either interval is in the other, or if the ending point of
> the first interval is greater than or equal to the starting point of the second interval, and
> the starting point of the first interval is less than or equal to the ending point of the second
> interval." … "This operator uses the semantics described in the Start and End operators to
> determine interval boundaries."

> CQL 1.5.3, [Interval Operators > Meets](https://cql.hl7.org/N1A/09-b-cqlreference.html#meets):
> "In other words, if the ending point of the first interval is equal to the predecessor of the
> starting point of the second, or if the starting point of the first interval is equal to the
> successor of the ending point of the second."

> CQL 1.5.3, [Interval Operators > End](https://cql.hl7.org/N1A/09-b-cqlreference.html#end): "If
> the high boundary of the interval is open, this operator returns the predecessor of the high
> value of the interval."

The ELM definitions say the same thing
([04-logicalspecification Meets / Overlaps](https://cql.hl7.org/N1A/04-logicalspecification.html#meets)).

**Versions:** 1.4 has the same Overlaps and Meets wording; its diffs are quoting and markup only.
2.0.0 adds "particularly when those boundaries are `null`" and a paragraph on DateTime
seconds/milliseconds comparison. Neither changes these integer cases.

**Conformance tests:** CQL-TESTS `IntegerIntervalOverlapsTrue3`, `Interval[10, 15] overlaps
Interval[4, 10]`, expects `true`. That is the touching-closed case in mirror image. No test in
1.4, 1.5.3 or cql-tests covers a half-open interval touching a closed one, or `meets` on two closed
intervals that share an endpoint.

**Layer:** spec; the spec decides all four cases. There is no recorded probe. To confirm the
engine, I would run one library with the four expressions plus `end of Interval[1, 5)` as a
control. The control checks that the engine applies the predecessor. Read `end of` rather than the
printed interval, because the language server prints the predecessor of an open bound (the
intervals.md display gotcha).

## HO-2

**Answer (spec, 1.5.3):** `months between @2026-01-31 and @2026-02-28` is `0`, and
`difference in months between @2026-01-31 and @2026-02-28` is `1`.

- **Duration** counts *whole calendar months*. In 1.5.3 a month starting on 31 January ends on the
  "immediately following calendar date" after the non-existent 31 February, which is 1 March. On
  28 February, less than one month has passed, so the result is 0. The appendix formula gives the
  same answer: day(date 2) = 28 < day(date 1) = 31, so the result is
  `(2026 - 2026) * 12 + (2 - 1) - 1 = 0`.
- **Difference** counts *month boundaries crossed*. One boundary (1 February) lies between the two
  dates, so the result is 1.

**Spec text:**

> CQL 1.5.3, [Date and Time Operators > Duration](https://cql.hl7.org/N1A/09-b-cqlreference.html#duration):
> "The _duration-_between operator returns the number of whole calendar periods for the specified
> precision between the first and second arguments. … The result of this operation is always an
> integer; any fractional periods are dropped."

> CQL 1.5.3, [Date and Time Operators > Difference](https://cql.hl7.org/N1A/09-b-cqlreference.html#difference):
> "The _difference-_between operator returns the number of boundaries crossed for the specified
> precision between the first and second arguments."

> CQL 1.5.3, [Calculating Duration in Months > Definition](https://cql.hl7.org/N1A/15-h-timeintervalcalculations.html#definition-1):
> "A month in CQL is defined as the duration of any time interval which starts at a certain time of
> day at a certain calendar day of the calendar month and ends at: … The same time of day at the
> immediately following calendar date of the ending calendar month, if the same calendar date of
> the ending month in the ending year does not exist."

> CQL 1.5.3, [Calculating Duration in Months > Examples > Scenario 2](https://cql.hl7.org/N1A/15-h-timeintervalcalculations.html#scenario-2-1):
> "When day (day 2) < day (date 1) … Duration (months) = (year (date 2) - year (date 1)) * 12 +
> (month (date 2) - month (date 1)) - 1"

> CQL 1.5.3, [Difference Calculations](https://cql.hl7.org/N1A/15-h-timeintervalcalculations.html#difference-calculations):
> "Difference calculations are performed by truncating the datetime values at the next precision,
> and then performing the corresponding duration calculation on the truncated values."

Truncated to months, the two dates are 2026-01 and 2026-02, which gives 1.

**Versions:**

- **1.4:** the month Definition reads the same as 1.5.3 ("immediately following calendar date").
- **2.0.0:** the Definition changes to "The same time of day at the last calendar date of the
  ending calendar month, if the same calendar date of the ending month in the ending year does not
  exist." Under that rule, a month from 31 January ends on 28 February, so `months between` would
  be **1**. However, 2.0.0's Scenario 2 formula is unchanged and still gives 0, so 2.0.0
  contradicts itself here.

**Related caution (1.5.3):** date arithmetic clamps to month end. The 1.5.3 Date/Time Arithmetic
table says "If the resulting date is not a valid date in the resulting year, the last day of the
resulting calendar month is used". So `@2026-01-31 + 1 month` is `@2026-02-28`, yet `months
between` those same two dates is 0. Under the 1.5.3 text, adding a month and measuring a month are
not inverses.

**Evidence and engine:** the 1.5.3 test `DateTimeDurationBetweenMonth`, `months between @2014-01-31
and @2014-02-01`, expects `0`. PROBES §24 shows engine 5.4.0 returning `0` (duration) and `1`
(difference) for 31 January to 1 February. That probe does not reach the 28 February boundary. For
the analogous year case, the engine followed the **2.0.0** reading: `years between @2012-02-29 and
@2014-02-28` returned 2 (PROBES §24). So I cannot predict whether the engine returns 0 or 1 here.

**Probe I would run:** `months between @2026-01-31 and @2026-02-28` with these controls:

- `months between @2026-01-31 and @2026-03-01`: 1 under 1.5.3.
- `months between @2026-01-28 and @2026-02-28`: 1 under both versions.
- `difference in months between @2026-01-31 and @2026-02-28`.

If the engine returns 1 for the first expression, that is a version gotcha: the engine is applying
the 2.0.0 Definition at a 1.5 target.

**Layer:** spec for the meaning, with a version difference in the month definition. The engine
behaviour at this boundary is unrecorded.

**Workaround:** if the measure means "at least one month", say which convention you want. Either
compare dates directly (`@2026-02-28 >= @2026-01-31 + 1 month`, which uses the arithmetic
clamping), or use `difference in months` when you want calendar-month boundaries.

## HO-3

**Answer:**

- `{ 1, 2.0 }` is a `List<Decimal>`. The Integer `1` is implicitly converted with `ToDecimal`, so
  the list holds the Decimals 1.0 and 2.0.
- `First({ 1, 2.0 }) is Integer` is `false`.
- `First({ 1, 2.0 }) is Decimal` is `true`.

**Spec text (list typing):**

> CQL 1.5.3, [Types > Type Inference > Literals and Selectors](https://cql.hl7.org/N1A/03-developersguide.html#literals-and-selectors):
> "If the type of the list is inferred, the type of the first element is used initially, and
> subsequent elements in the list are required to be of the inferred type of the first element,
> with the exception that if a subsequent element is a supertype of the initial element, or if the
> initial element is convertible to the type of a subsequent element, the type of the subsequent
> element will become the new inferred element type for the list."

Integer converts implicitly to Decimal (Table 3-J,
[Implicit Conversions](https://cql.hl7.org/N1A/03-developersguide.html#implicit-conversions)), and
the spec describes the mechanism: "the language will implicitly convert the type of the 1 to
Decimal by inserting a ToDecimal invocation."

**Spec text (type test):**

> CQL 1.5.3, [Type Operators > Is](https://cql.hl7.org/N1A/09-b-cqlreference.html#is): "If the
> run-time type of the argument is the same as or derived from the type being tested, the result of
> the operator is true; otherwise, the result is false."

Integer is not derived from Decimal: "All the system-defined types derive directly from System.Any"
(CQL 1.5.3, [Types > System-Defined Types](https://cql.hl7.org/N1A/03-developersguide.html#system-defined-types)).
`First` "returns the first element in a list"
([List Operators > First](https://cql.hl7.org/N1A/09-b-cqlreference.html#first)). That element is
the converted Decimal 1.0, so its run-time type is Decimal.

**Versions:** the list-selector rule is the same in 1.4 and 2.0.0. 1.4's `Is` reads "If the
run-time type of the argument is of the type being tested". Without the "derived from" clause, the
answer is the same here.

**Evidence:** PROBES §9 records that `{ 1, 1.5 }` and `{ 1.5, 1 }` compile to `List<System.Decimal>`
with `ToDecimal` over `1`. That is translator behaviour matching the spec. The probes also note
that the language server prints the Decimal `1` as `1`, so the printed output does not show the
type. No conformance test covers `is` on an element of a mixed Integer/Decimal list.

**Probe I would run:** the two `is` expressions, plus `First({ 1, 2 }) is Integer` as a control.
I would also read the ELM to confirm the `ToDecimal` on the first element. I have no recorded run
of the `is` tests themselves.

**Layer:** spec decides; the translator's typing is recorded as matching.

## HO-4

**Answer, 1.5 engine (spec 1.5.3):**

- `Combine({ 'a', null, 'b' }, '-')` should be `'a-b'`: null elements are ignored.
- `Combine({ 'a', 'b' }, null as String)` should be `'ab'`: a null separator is ignored.

**Spec text:**

> CQL 1.5.3, [String Operators > Combine](https://cql.hl7.org/N1A/09-b-cqlreference.html#combine):
> "If the source argument is null, or the source list is empty, the result is null. If the
> separator argument is null, it is ignored. For consistency with aggregate operator behavior, null
> elements in the input list are ignored."

The 1.5.3 ELM definition ([04-logicalspecification Combine](https://cql.hl7.org/N1A/04-logicalspecification.html#combine))
has the same three sentences.

The spec says ignored elements are dropped. It does not spell out that no separator is emitted for
them; `'a-b'` is the natural reading, not a quoted rule.

**Yes, the answer depends on the version:**

- **1.4, CQL Reference** ([Combine](https://cql.hl7.org/STU4/09-b-cqlreference.html#combine)):
  "If either argument is null, or the source list is empty, the result is null. For consistency
  with aggregate operator behavior, null elements in the input list are ignored." So the null
  separator gives **`null`**, and the null element is ignored, giving `'a-b'`.
- **1.4, ELM** ([Combine](https://cql.hl7.org/STU4/04-logicalspecification.html#combine)): "If
  either argument is null, or any element in the source list of strings is null, the result is
  null." This contradicts 1.4's own CQL Reference: under it, the null element also gives
  **`null`**. So 1.4 contradicts itself on null elements (a spec gap at 1.4).
- **2.0.0:** Combine is not in the 1.5.3-to-2.0.0 change list, so its text matches 1.5.3.

**Conformance tests:**

- The 1.5.3 suite has `CombineNull`, `CombineEmptyList`, `CombineABC` and `CombineABCSepDash`, but
  no null-element or null-separator test.
- CQL-TESTS adds `CombineWithNulls` (`Combine({'a', 'b', 'c', null})` gives `'abc'`) and
  `CombineNullSeparator` (`Combine({'a', 'b', 'c'}, null)` gives `'abc'`). Both match the 1.5.3
  text.
- No test anywhere covers a null element in the *middle* of a list *with* a separator. That is the
  case where an implementation could wrongly produce `'a--b'`.

**What I would check before trusting an engine's result:**

1. **Which rule the engine implements.** A 1.4-era implementation, or one written from the 1.4 ELM
   text, returns `null` for one or both expressions.
2. **The ELM.** It should be `Combine` with a `separator` child. The separator should be
   `As String` over `Null`, and the list should be `List<String>` with the null cast to String. A
   different overload or a missing conversion would be a translator issue, not the engine.
3. **The middle-null case.** Compare `'a-b'` against `'a--b'`. Run controls:
   `Combine({ 'a', 'b' }, '-')`, `Combine({ 'a', 'b', null }, '-')` and
   `Combine({ null, 'a', 'b' }, '-')`. These separate "skips nulls" from "joins nulls as empty
   strings".
4. **The run configuration.** Record the engine and translator versions and the compatibility
   level, run each probe twice, and keep the output.

Neither expression is recorded in the skill's probes. Run the probe above before relying on the
engine.

**Layer:** spec (1.5.3 decides). It is a version gotcha against 1.4, and 1.4 is internally
inconsistent.

## HO-5

**Answer:** `{ null as Integer, 1 } union { null as Integer }` returns a list with one null and
the 1, that is `{ null, 1 }`. The spec sets no order. `Count` of the result is **1**.

**Spec text:**

> CQL 1.5.3, [List Operators > Union](https://cql.hl7.org/N1A/09-b-cqlreference.html#union-1):
> "The union operator for lists returns a list with all unique elements from both arguments. The
> union operator is defined as a set operation, meaning that duplicates are eliminated; … In
> addition, there is no expectation that the order of elements in the inputs will be preserved in
> the results. This operator uses equality semantics with the exception that null elements are
> considered equal."

The two nulls are therefore one duplicate, and one null remains.

> CQL 1.5.3, [Aggregate Functions > Count](https://cql.hl7.org/N1A/09-b-cqlreference.html#count):
> "The Count operator returns the number of non-null elements in the source. If the list contains
> no non-null elements, the result is 0."

The remaining null is not counted, so the count is 1, even though the list has two elements.

**Versions:**

- 1.4: List Union and Count differ in quoting and markup only.
- 2.0.0: adds the `union all` and `union all ordered` forms, which keep duplicates. Plain `union`
  is unchanged.

**Conformance tests:** 1.5.3 `UnionListNullAndListNull`, `{ null } union { null }`, expects
`{null}`; CQL-TESTS has the same test. This supports "nulls are considered equal". 1.5.3 `Count0`
shows `Count({ null, null, null })` is 0.

**Engine evidence:** these probes are related but are not this exact expression.

- PROBES §29: `distinct { null, null, 1 }` gives `[null, 1]`.
- PROBES §29: `{ null, 1, 3 } intersect { null, 3, 7 }` gives `[null, 3]`.
- PROBES §30: `Count({ null, 1 })` gives 1.

To confirm, I would run the union itself, `Count(...)` of it, and `Length(...)` of it as a control
that counts nulls. I would expect 2 for `Length`, but I have not run it.

**Layer:** spec decides.

**Pitfall:** if the intent is "how many elements", use `Length`. `Count` skips nulls.

## HO-6

**Answer (spec 1.5.3, with the tests):**

| Expression | Result |
| --- | --- |
| `Substring('abc', 2)` | `'c'` |
| `Substring('abc', 3)` | `null`: start index equal to the length is out of range, per the tests; the prose does not define "out of range" |
| `Substring('abc', 5)` | `null` |

**Spec text:**

> CQL 1.5.3, [String Operators > Substring](https://cql.hl7.org/N1A/09-b-cqlreference.html#substring):
> "The Substring operator returns the string within stringToSub, starting at the 0-based index
> startIndex, and consisting of length characters. If length is omitted, the substring returned
> starts at startIndex and continues to the end of stringToSub. If stringToSub or startIndex is
> null, or startIndex is out of range, the result is null."

Its examples include `Substring('ABCDE', 14) // null`.

**Where the spec is silent:** the prose does not say whether `startIndex = Length(stringToSub)` is
"out of range" or returns an empty string. The conformance tests settle the case in practice, but
they are informative only:

- The 1.4 and 1.5.3 suites and CQL-TESTS all have `SubstringAB2`: `Substring('ab', 2)` gives
  `null`. That is the same shape as `Substring('abc', 3)`.
- CQL-TESTS also has `SubstringEmptyAnd0`: `Substring('', 0)` gives `''`. There, a start index
  equal to the length (0) is *not* treated as out of range.

So the test suites are not consistent with each other on "index equals length". The empty string is
the exception.

**Versions:** the same in 1.4, 1.5.3 and 2.0.0. The only change is a typo fix in the 1.4 ELM text
("ommitted").

**Layer:** spec for indices 2 and 5. For index 3, it is a spec gap filled by informative tests.
No probe is recorded. I would run all three expressions with controls `Substring('ab', 2)` and
`Substring('', 0)` to see which convention the engine follows.

**Workaround:** if the code depends on the boundary, guard it explicitly:
`if start < Length(s) then Substring(s, start) else ''`, or whatever value you actually intend.

## HO-7

**Answer, CQL 1.5.3:**

- `@2026-01-15 = @2026-01-15T00:00:00.000-04:00` is **`null`**. This holds at an evaluation offset
  of `-04:00`; at other offsets see the offset dependence below.
- `@2026-01-15 same day as @2026-01-15T10:00:00.000-04:00` is **`true`**, whatever the evaluation
  offset.

**Why the first is null.** The Date is implicitly converted to DateTime with `ToDateTime` (Table
3-J lists Date to DateTime as implicit, in 1.4 and 1.5.3). In 1.5.3 that conversion leaves the time
unspecified:

> CQL 1.5.3, [Type Operators > ToDateTime](https://cql.hl7.org/N1A/09-b-cqlreference.html#todatetime):
> "For the Date overload, the result will be a DateTime with the time components unspecified,
> except for the timezone offset, which will be set to the timezone offset of the evaluation
> request timestamp."

> CQL 1.5.3, [Comparison Operators > Equal](https://cql.hl7.org/N1A/09-b-cqlreference.html#equal):
> "For Date, DateTime, and Time values, the comparison is performed by considering each precision
> in order, beginning with years (or hours for time values). If the values are the same, comparison
> proceeds to the next precision; if the values are different, the comparison stops and the result
> is false. If one input has a value for the precision and the other does not, the comparison stops
> and the result is null"

Year, month and day match. At hour, the left side has no value and the right side has 00, so the
result is null.

**Offset dependence (1.5.3).** The Equal entry says nothing about timezone normalisation. The
Author's Guide ([Comparing Dates and Times](https://cql.hl7.org/N1A/02-authorsguide.html#comparing-dates-and-times))
says: "When comparing DateTime values with different timezone offsets, implementations should
normalize to the timezone offset of the evaluation request timestamp, but only when the comparison
precision is hours, minutes, seconds, or milliseconds."

If the evaluation offset is, for example, `-05:00` and that normalisation applies, the right side
becomes 23:00 on 14 January. The day then differs, and the result is `false`, not `null`. The
Equal entry itself does not decide this, so it is partly a spec gap and partly environment.

**Why the second is true.**

> CQL 1.5.3, [Date and Time Operators > Same As](https://cql.hl7.org/N1A/09-b-cqlreference.html#same-as-1):
> "if the specified precision has been reached, the comparison stops and the result is true." …
> "When this operator is called with both Date and DateTime inputs, the Date values will be
> implicitly converted to DateTime as defined by the ToDateTime operator. When comparing DateTime
> values with different timezone offsets, implementations should normalize to the timezone offset
> of the evaluation request timestamp, but only when the comparison precision is hours, minutes,
> seconds, or milliseconds."

At day precision there is no normalisation. Year, month and day (2026-01-15) match, so the result
is true.

**Under CQL 1.4, the first answer differs.**

> CQL 1.4, [Type Operators > ToDateTime](https://cql.hl7.org/STU4/09-b-cqlreference.html#todatetime):
> "For the Date overload, the result will be a DateTime with the time components set to zero,
> except for the timezone offset, which will be set to the timezone offset of the evaluation
> request timestamp."

So under 1.4, the Date becomes `2026-01-15T00:00:00.000` at the evaluation offset.

- At an evaluation offset of `-04:00`, that is exactly the right-hand value, and the result is
  **`true`**, not `null`.
- At any other offset, the result is `false`: under normalisation, it is a different instant.

The 1.4 Same As text matches 1.5.3, so the second answer is `true` under 1.4 too. 2.0.0 changes
Same As's "implementations should normalize" to "the values are normalized", which does not affect
the day-precision case.

**Engine evidence:** these probes ran at evaluation offset `-04:00`.

- PROBES §23: `@2026-01-15 = @2026-01-15T10:00:00Z` gives `null`. This matches the 1.5.3
  unspecified-time rule.
- PROBES §23: `@2026-01-15 same day as @2026-01-15T10:00:00Z` gives `true`.
- PROBES §23: `@2026-01-15T23:30:00-05:00 same day as @2026-01-16T04:30:00Z` gives `false`. This
  shows the engine does not normalise at day precision.

The exact expressions in this question were not probed. I would run them at `-04:00`, together
with the control `@2026-01-15T00:00:00.000-04:00 = @2026-01-15T00:00:00.000-04:00`. I would then
re-run them at a different evaluation offset; `cql_execute` takes no timestamp, so that means a
different machine TZ or a harness that sets the evaluation timestamp. I would also read the ELM to
confirm `ToDateTime` over the Date.

Note that engine 5.4.0 implements its own `ToDateTime`. Setting `compatibilityLevel` to 1.4 changes
translation, not this run-time rule, so "the 1.4 answer" is a statement about the spec, not
something a compatibility switch reproduces.

**Layer:** spec (1.5.3 decides the `-04:00` case). It is a version gotcha against 1.4, and
environment (the evaluation offset) for the other offsets.

## HO-8

**Classification: environment.** The most likely cause is a different evaluation-request offset:
the machine time zone, or a different DST period on the run date. The spec makes the offset part
of the meaning of the comparison:

- CQL 1.5.3, [Types > DateTime](https://cql.hl7.org/N1A/09-b-cqlreference.html#datetime): "If no
  timezone offset is specified, the timezone offset of the evaluation request timestamp is
  assumed."
- CQL 1.5.3, [ToDateTime](https://cql.hl7.org/N1A/09-b-cqlreference.html#todatetime): a converted
  Date gets "the timezone offset of the evaluation request timestamp".

A Date compared with a DateTime is a day-precision value at *your* offset, compared with an instant
that is normalised to *your* offset at hour precision and finer. Whether the day matches, and
whether the unknown hour makes the result null, can depend on the machine.

The skill records an instance at offset `-04:00`: `@2026-01-15 < @2026-01-16T00:00:00Z` gives
`null` (PROBES §23). datetime.md notes the same expression is `true` at `+00:00`, because the
right-hand side is then midnight on the 16th rather than 20:00 on the 15th. The same mechanism
makes `Interval[@2026-01-01, @2026-01-02T00:00:00Z]` a run-time error at `-04:00` (PROBES §46).

Two things follow from Diagnosing Q2 and Q6:

- How an environment chooses the evaluation offset is outside the spec; datetime.md lists it under
  "Where the spec is silent".
- The Date-against-DateTime comparison partly depends on the Author's Guide normalisation sentence
  rather than on the Equal entry.

So this is not an engine or translator defect: the result follows from a setting. Before settling
on that, rule out the other differences between the two runs:

- engine or translator version;
- `compatibilityLevel`: a 1.4-style "time components set to zero" ToDateTime would make the Date
  midnight;
- translator options;
- a different harness, such as `cql_execute` against a CLI or server with an explicit timestamp.

**What I would record for each run:**

1. The evaluation-request timestamp and its offset. With `cql_execute` this is the machine's local
   offset, since it takes no timestamp parameter. Also record the OS time zone (or `TZ`) and the
   run date, because DST changes the offset.
2. Translator, engine, language server and clinical-reasoning versions (for example translator
   5.4.0, engine 5.4.0, clinicalReasoning 4.13.0, languageServer 4.11.0-SNAPSHOT).
3. The ELM header: `compatibilityLevel`, `signatureLevel` and `translatorOptions`. Also record the
   ELM of the comparison, to confirm `ToDateTime` over the Date and which operator was chosen. Read
   it from a freshly named library, because the ELM view can be stale after an edit.
4. The harness and command, the exact CQL, and the raw output of two runs. Read offsets with
   `timezoneoffset from`, not from printed DateTimes, which omit the offset.
5. A control that differs in one thing: the same comparison with the DateTime written at your own
   offset.

**How I would rewrite the probe to give the same answer everywhere:**

- **Don't mix Date and DateTime.** Compare like with like, at the same precision and with explicit
  offsets on every DateTime. Examples: `@2026-01-15T00:00:00.000Z <= @2026-01-16T00:00:00.000Z`,
  or two Dates, `@2026-01-15 < @2026-01-16`.
- **If the question is really "same calendar day as written",** use a day-precision operator such
  as `@2026-01-15 same day as X`. Per Same As, normalisation applies "only when the comparison
  precision is hours, minutes, seconds, or milliseconds", and the engine was observed not to
  normalise at day precision (PROBES §23). Don't use `date from X` for this:
  ["When extracting the Date or Time from a DateTime value, implementations should normalize to the timezone offset of the evaluation request timestamp"](https://cql.hl7.org/N1A/09-b-cqlreference.html#datetime-component-from),
  so it is offset-dependent too.
- **Never rely on an implicit offset.** Avoid offset-less DateTime literals, `Now()`, `Today()` and
  `TimeOfDay()`.
- **If a mixed comparison is the thing under test,** pin the evaluation timestamp in a harness that
  accepts one, and record it with the result.

**Layer:** environment (the evaluation offset), on top of a spec rule that makes the result
depend on that offset. Check the version and compatibility level before concluding.
