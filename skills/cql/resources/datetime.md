# CQL Dates and Times: Precision, Comparison, Timezones and Arithmetic

Baseline: CQL 1.5.3. Untagged statements hold in 1.4, 1.5.3 and 2.0.0.
Sources: CQL-1.4, CQL-1.5.3, CQL-2.0.0, CQL-TESTS, CQFW-5.4.0, PROBES-2026-10-22, CQLWIKI

Comparison of partial values, timezone offsets, `duration` vs `difference`, time-valued quantities
and units, and calendar arithmetic. Source IDs are in [SOURCES.md](SOURCES.md). The types and
literal formats are in [operators.md](operators.md#type-system); interval bounds are in
[intervals.md](intervals.md). Model date types (for example FHIR's) reach these operators only
through the model's conversions to `System.Date` and `System.DateTime`; those belong to the model
skills.

Observed behaviour comes from translator and engine 5.4.0 through the language server, on a machine
at offset `-04:00`. `cql_execute` has no evaluation-timestamp parameter, so the evaluation offset is
the machine's [src: PROBES-2026-10-22 RESULTS.md §23]. Results that depend on it say so.

The spec text below is the rule. Blocks marked **Gotcha** record where translator or engine 5.4.0
departs from it or depends on a setting, each with a workaround; see
[diagnosing.md](diagnosing.md) for how the layer was decided.

The conformance tests assume a different setting. The spec's tests page says: "Some tests cover
functionality related to calculation and string representation of times, and are built to be run
with an evaluation request timestamp in UTC, to avoid introducing any location dependence to the
tests." (1.5+) [src: CQL-1.5.3 tests > (preamble)]. CQL-TESTS began as a copy of those tests, so
assume the same UTC setting for it. A test whose expected
value depends on the evaluation offset can therefore differ from these probes without either being
wrong. The test disagreement recorded below (`DurationInDaysA`) uses explicit offsets on both sides,
so it is not affected.

## Comparing values of different precision

"CQL treats Date and Time values that are only known to some specific precision as an uncertainty
over the range at the first unspecified precision." So `Date(2014)` reads as "some date within the
year 2014", so `Date(2014) < Date(2014, 2, 15)` "is null because the first date could be any date
within the year 2014"
[src: CQL-1.5.3 02-authorsguide > Operations > Date and Time Operators > Comparing Dates and Times].
The same section gives the procedure: "Date and time comparisons are performed by comparing the
values at each precision, beginning with years, and proceeding to the finest precision specified in
either input, with seconds and milliseconds treated as a single precision using a Decimal." (same in
1.4, 2.0) (1.5+) "Note that when explicitly comparing or calculating at the millisecond precision,
the values are considered separated". **2.0:** adds a pointer to a "Date and Time Considerations"
topic.

`same … as`, `same … or before` and `same … or after` compare to a chosen precision: "same month as
means the same year and the same month". They "may still return null if the Date and Time values
involved have unspecified components at or above the specified comparison precision", with the
example `Date(2014, 7, 15) after hour of DateTime(2014, 7, 11, 14, 0, 0)`, where "The result in this
example is null because the first date has no hour component."

Observed [src: PROBES-2026-10-22 RESULTS.md §22]:

| CQL | Result |
| --- | --- |
| `@2026-01 = @2026-01-15` | `null` |
| `@2026 < @2026-02-15` / `@2025 < @2026-02-15` | `null` / `true` |
| `@2026-01 same month as @2026-01-15` / `same day as` | `true` / `null` |
| `@2026-01-01 <= @2026-01` | `null` |
| `@2026-01 during Interval[@2026-01-01, @2026-12-31]` | `null` |
| `Date(2014, 7, 15) after hour of DateTime(2014, 7, 11, 14, 0, 0)` | `true` (Author's Guide: null; see below) |

The formal operator definitions decide both rows that look surprising, and the engine follows
them ([spec/README.md](spec/README.md#pages-worth-knowing): the formal pages govern):

- **`after hour of`.** The ELM `After` goes precision by precision: "If the values are the same,
  comparison proceeds to the next precision; if the first value is greater than the second, the
  result is true; … if either input has no value for the precision, the comparison stops and the
  result is null" (same in 1.4; **2.0:** adds the seconds-and-milliseconds note)
  [src: CQL-1.5.3 04-logicalspecification > Interval Operators > After]. In the Author's Guide
  example the day differs (15 after 11) before the hour is reached, so the result is `true`. The
  guide's "null because the first date has no hour component" is wrong by the formal text, in all
  three versions.
- **`@2026-01-01 <= @2026-01`.** The ELM `LessOrEqual`: "if one input has a value for the precision
  and the other does not, the comparison stops and the result is null" (same in 1.4, 2.0)
  [src: CQL-1.5.3 04-logicalspecification > Comparison Operators > LessOrEqual]. Year and month are
  equal and the right side has no day, so the result is `null`, although the guide's uncertainty
  reading would suggest `true` (every day in January is on or after January 1). The practical
  effect: a partial date is not `during` an interval that starts inside its own month or year.

### Seconds and milliseconds

1.5.3 treats seconds and milliseconds "as a single precision using a Decimal" (above). **2.0:** adds
examples to Equal: `@2024-11-15T12:30:00.0 = @2024-11-15T12:30:00 // true, RHS interpreted as 00.0`,
`… 12:30:00.5 = … 12:30:00 // false`, and `@2024-11-15T12:30:00.5 = @2024-11-14T12:30 // null`
[src: CQL-2.0.0 09-b-cqlreference > Comparison Operators > Equal]. The third example's dates differ
by a day, so `null` looks like an error in the 2.0.0 text.

The ELM `Equal` already says it for 1.5.3: "For the purposes of comparison, seconds and
milliseconds are combined as a single precision using a decimal, with decimal equality semantics."
(same in 1.4, 2.0) [src: CQL-1.5.3 04-logicalspecification > Comparison Operators > Equal]. So
`:00.0` and `:00` are the decimals `0.0` and `0`, which are equal.

#### Gotcha: a value with milliseconds and one without compare as null

- **Symptom:** `@2024-11-15T12:30:00.0Z = @2024-11-15T12:30:00Z` is `null`; for the three 2.0.0
  examples the engine gives `null`, `null` and `false`.
- **Probe:** `testDtPrecision` [src: PROBES-2026-10-22 RESULTS.md §22]; `testDtMsWorkaround`,
  against `@2024-11-15T12:30:00.0Z = @2024-11-15T12:30:00.0Z`, which is `true`
  [src: PROBES-2026-10-22 RESULTS.md §43].
- **Spec:** decides: one combined precision (above).
- **Well-formed?** Yes.
- **Layer:** engine. It treats a value without milliseconds as uncertain over 0 to 999 milliseconds
  (`duration in milliseconds between` the two is `[0, 999]`), that is, as a separate precision.
- **Evidence:** the ELM is a plain `Equal` of two DateTime literals; `~` gives `false`.
- **Workaround:** when sub-second differences don't matter, compare with `same second as`, which is
  `true` for this pair [src: PROBES-2026-10-22 RESULTS.md §43]. At 1.5.3 it ignores milliseconds
  (it is `true` for `.5` against `:00` too), as 1.5.3 `SameAs` has no milliseconds rule; (2.0+)
  `SameAs` combines seconds and milliseconds, so `.5` would then differ
  [src: CQL-2.0.0 04-logicalspecification > Date and Time Operators > SameAs].
- **Affects:** engine 5.4.0.

## Timezone offsets

### The default offset

"If no timezone offset is specified, the timezone offset of the evaluation request timestamp is
assumed." (1.5+; **1.4:** the Types entry lacks the sentence, though 1.4 applies the same default
in the `DateTime()` selector, `ToDateTime`, `ConvertsToDateTime`, `duration` and `difference`)
[src: CQL-1.5.3 09-b-cqlreference > Types > DateTime]. So a DateTime written without an offset
means a different instant under a different evaluation offset.

Observed, at evaluation offset `-04:00`: `@2026-01-15T10:00:00 = @2026-01-15T10:00:00-04:00` is
`true`, and the same literal compared with `…Z` or `…-05:00` is `false`
[src: PROBES-2026-10-22 RESULTS.md §23]. Write offsets explicitly in tests and fixtures.

### Normalisation, and only at hour precision or finer

From `Same As` (and the other precision operators): "When comparing DateTime values with different
timezone offsets, implementations should normalize to the timezone offset of the evaluation request
timestamp, but only when the comparison precision is hours, minutes, seconds, or milliseconds."
**2.0:** "the values are normalized" instead of "implementations should normalize"
[src: CQL-1.5.3 09-b-cqlreference > Date and Time Operators > Same As]
[src: CQL-2.0.0 09-b-cqlreference > Date and Time Operators > Same As].

So an offset does not move the day for day-precision comparison. Observed
[src: PROBES-2026-10-22 RESULTS.md §23]:

| CQL | Result |
| --- | --- |
| `@2026-01-15T23:30:00-05:00 = @2026-01-16T04:30:00Z` (same instant) | `true` |
| `@2026-01-15T23:30:00-05:00 same day as @2026-01-16T04:30:00Z` | `false` |
| `day from @2026-01-15T23:30:00-05:00` | `15` (as written) |
| `@2012-03-10T10:20:00.999+07:00 = @2012-03-10T09:20:00.999+06:00` | `true` |

### Date against DateTime

In 1.5.3, "When this operator is called with both Date and DateTime inputs, the Date values will be
implicitly converted to DateTime as defined by the ToDateTime operator"
[src: CQL-1.5.3 09-b-cqlreference > Date and Time Operators > Same As]; **2.0:** reads "a mixture
of" for "both". `ToDateTime` of a Date
leaves "the time components unspecified, except for the timezone offset, which will be set to the
timezone offset of the evaluation request timestamp" (**1.4:** "set to zero")
[src: CQL-1.5.3 09-b-cqlreference > Type Operators > ToDateTime]
[src: CQL-1.4 09-b-cqlreference > Type Operators > ToDateTime].

So a Date compared with a DateTime is a day-precision value carrying the evaluation offset, and the
DateTime is normalised to that offset. Observed [src: PROBES-2026-10-22 RESULTS.md §23]:

| CQL | Result |
| --- | --- |
| `@2026-01-15 = @2026-01-15T10:00:00Z` | `null` (time unknown on the left) |
| `@2026-01-15 same day as @2026-01-15T10:00:00Z` | `true` |
| `@2026-01-15 = @2026-01-15T00:00:00.000-04:00` (midnight at the evaluation offset) | `null` [src: PROBES-2026-10-22 RESULTS.md §59] |
| `@2026-01-15 < @2026-01-16T00:00:00-04:00` | `true` |
| `@2026-01-15 < @2026-01-16T00:00:00Z` | `null`: at `-04:00` the right side is 20:00 on the 15th |

The last row depends on the evaluation offset: the same expression is `true` at offset `+00:00`.
Under 1.4's "set to zero" rule the Date would instead be midnight.

## `duration` vs `difference`

"For duration, the calculation is performed based on the calendar duration for the precision. For
difference, the calculation is performed by counting the number of boundaries of the specific
precision crossed" (same in 1.4, 2.0)
[src: CQL-1.5.3 02-authorsguide > Operations > Date and Time Operators > Computing Durations and Differences].
`duration … between` "returns the number of whole calendar periods … any fractional periods are
dropped" (same in 1.4; **2.0:** offsets "are normalized"). (1.5+) Seconds and milliseconds count as
one precision [src: CQL-1.5.3 09-b-cqlreference > Date and Time Operators > Duration].

With imprecise inputs both return an uncertainty: `days between Date(2014, 1, 15) and Date(2014, 2)`
is "no less than 17 days, but no more than 44" (same in 1.4, 2.0)
[src: CQL-1.5.3 05-languagesemantics > Precision-Based Timing > Determining Difference and Duration].

Observed [src: PROBES-2026-10-22 RESULTS.md §24]:

| CQL | `duration` (`… between`) | `difference in …` |
| --- | --- | --- |
| months, @2014-01-31 to @2014-02-01 | `0` | `1` |
| years, @2011-12-31 to @2012-01-01 | `0` | `1` |
| days, @2014-01-15 to @2014-02 | `[17, 44]`; `> 2` true, `> 20` null, `> 50` false | — |
| days, @2017-03-12T00:00:00-07:00 to @2017-03-13T00:00:00-06:00 | `1` | `1` |
| days, @2026-01-01T15:00:00Z to @2026-01-01T19:00:00Z (same day) | `0` | `0` |

The same-day row is from [src: PROBES-2026-10-22 RESULTS.md §49]; a length of stay computed this way
is `0` for stays under a day, so `Interval[1, days]` is then descending and invalid. The
`DurationInDaysA` row is a test-suite disagreement. CQL-TESTS `DurationInDaysA` expects `0`
[src: CQL-TESTS CqlDateTimeOperatorsTest.xml DurationInDaysA]: normalised, the two values are 23
hours apart. The 1.5.3 text normalises "only when the comparison precision is hours, minutes,
seconds, or milliseconds", so at day precision the values are compared as written, giving `1`, as
the engine does. Tests are informative; the spec text is authoritative.

### Year and month length

The duration appendix defines a year that starts on a date that does not exist in the ending year
(February 29) as ending on "The same time of day on the immediately following calendar date of the
next calendar year" — March 1
[src: CQL-1.5.3 15-h-timeintervalcalculations > Calculating Duration in Years > Definition].
**2.0:** "The same time of day on the last day of the same month in the next calendar year" —
February 28
[src: CQL-2.0.0 15-h-timeintervalcalculations > Calculating Duration in Years > Definition]. Months
change the same way
[src: CQL-1.5.3 15-h-timeintervalcalculations > Calculating Duration in Months > Definition]. The
1.5.3 arithmetic table already uses the last day of the month (below), so 1.5.3 is not consistent
with itself here.

Observed: `years between @2012-02-29 and @2014-02-28` is `2`, the 2.0.0 reading, as CQL-TESTS
expects [src: PROBES-2026-10-22 RESULTS.md §24]
[src: CQL-TESTS CqlDateTimeOperatorsTest.xml YearsBetweenLeapYearDatesEquals2].

For months the engine takes the 1.5.3 reading: `months between @2026-01-31 and @2026-02-28` is `0`
(a month from 31 January ends on 1 March), while `difference in months` is `1`; the control
`months between @2026-01-15 and @2026-02-15` is `1`
[src: PROBES-2026-10-22 RESULTS.md §54]. **2.0:** the month definition moves the end to "the last
calendar date of the ending calendar month", which would make this `1`, but the Scenario 2 formula
is unchanged: "Duration (months) = (year (date 2) - year (date 1)) * 12 + (month (date 2) - month
(date 1)) - 1", which gives `0`, so 2.0.0 contradicts itself here
[src: CQL-2.0.0 15-h-timeintervalcalculations > Calculating Duration in Months > Definition]. For a
duration that must count end-of-month spans, compare day counts or use `difference in months`,
which counts boundaries.

## Time-valued quantities and units

`=`: "UCUM definite-time duration quantities above days (and weeks) are not comparable to calendar
duration quantities above days (and weeks)", with conversions such as `1 year = 12 months` and
`1 day = 24 hours`, and "unit conversion between variable length calendar durations (i.e. years and
months) and definite-time durations (i.e. days or below) results in null." (1.5+; **2.0:** adds "and
such comparisons return null", and lists `1 year = 12 months or 365 days` and `1 month = 30 days`
while keeping the "results in null" sentence, so the 2.0.0 text contradicts itself)
[src: CQL-1.5.3 09-b-cqlreference > Comparison Operators > Equal].

`~`: definite and calendar units "are considered equivalent to their calendar duration counterparts"
(`1 month ~ 1 'mo'`), and `1 year ~ 365 days`, `1 month ~ 30 days` (1.5+). **2.0:** adds a note on
conversion steps [src: CQL-1.5.3 09-b-cqlreference > Comparison Operators > Equivalent].

Observed [src: PROBES-2026-10-22 RESULTS.md §25]:

| CQL | 1.5.3 text | Engine |
| --- | --- | --- |
| `1 year = 12 months` | true | `null` |
| `1 day = 24 hours` | true | `null` |
| `1 month = 30 days` | null | `null` |
| `1 month ~ 30 days` | true | `false` |
| `1 'mo' = 1 month` | null | `null` |
| `1 'mo' ~ 1 month` | true | `true` |
| `1 'd' = 1 day` | true | `true` |
| `5 days > 3` | — | `null` |

#### Gotcha: calendar quantities in different units compare as null

- **Symptom:** `1 year = 12 months` and `1 day = 24 hours` are `null`; `1 month ~ 30 days` is
  `false`.
- **Probe:** `testDtUnits` (the table above) [src: PROBES-2026-10-22 RESULTS.md §25];
  `testDtUnitWorkaround`, against `12 months = 12 months`
  [src: PROBES-2026-10-22 RESULTS.md §44].
- **Spec:** (1.5+) decides: the conversions `1 year = 12 months` and `1 day = 24 hours` apply, and
  `~` makes `1 month ~ 30 days` true (above).
- **Well-formed?** Yes.
- **Layer:** engine. The ELM keeps the units as written; the translator does no unit conversion.
- **Evidence:** the engine compares quantities only when both units are in the same keyword family,
  and returns null otherwise
  [src: CQFW-5.4.0 engine/src/commonMain/kotlin/org/opencds/cqf/cql/engine/runtime/Quantity.kt:40-45].
- **Workaround:** write both sides in one calendar unit: `12 months = 12 months` and
  `24 hours = 24 hours` are `true` [src: PROBES-2026-10-22 RESULTS.md §44].
- **Affects:** engine 5.4.0.

`5 days > 3` is null because `3` becomes a Quantity with the default unit. **2.0:** "When implicitly
converting a number to a quantity, the resulting quantity will have the default unit 1. In some
cases, this could result in uncomparable units"
[src: CQL-2.0.0 03-developersguide > Types > Conversion > Implicit Conversions]. Write `3 days`.

## Calendar arithmetic

"If the month and day of the date or time value is not a valid date in the resulting year, the last
day of the calendar month is used", and for months, "If the resulting date is not a valid date in
the resulting year, the last day of the resulting calendar month is used" (1.5+: this table is
absent from the 1.4 Author's Guide)
[src: CQL-1.5.3 02-authorsguide > Operations > Date and Time Operators > Date and Time Arithmetic].
The Language Semantics table gives "DateTime(2012, 2, 29, 0, 0) + 1 year = DateTime(2013, 2, 28, 0,
0)" (same in 1.4)
[src: CQL-1.5.3 05-languagesemantics > Timing Calculations > Date and Time Arithmetic].

Observed [src: PROBES-2026-10-22 RESULTS.md §26]:

| CQL | Result |
| --- | --- |
| `@2024-01-31 + 1 month` / `@2023-01-31 + 1 month` | `2024-02-29` / `2023-02-28` |
| `@2024-02-29 + 1 year` | `2025-02-28` |
| `@2024-03-31 - 1 month` | `2024-02-29` |
| `@2024-01-31 + 1 month + 1 month` | `2024-03-29` |
| `@2024-01-31 + 2 months` | `2024-03-31` |
| `DateTime(2014) + 18 months` / `@2016-01-01 - 1.1 years` | `2015` / `2015-01-01` |

Adding months is not associative at month ends: `+ 1 month + 1 month` is not `+ 2 months`.

**Units in arithmetic.** "the quantity units may be specified in singular, plural, or UCUM form",
but "it is an error to attempt to add a definite-duration time-valued unit above days (and weeks), a
calendar duration must be used" (**1.4:** the decimal-truncation and error rules differ, see
[operators.md](operators.md#datetime-arithmetic); **2.0:** a unit not allowed for the type is an
error, and "As Time is cyclic, the result of overflowing the time value will be wrapped around the
beginning of the day") [src: CQL-1.5.3 09-b-cqlreference > Date and Time Operators > Add]
[src: CQL-2.0.0 09-b-cqlreference > Date and Time Operators > Add].

Observed [src: PROBES-2026-10-22 RESULTS.md §25] [src: PROBES-2026-10-22 RESULTS.md §26]:

| CQL | Result |
| --- | --- |
| `@2026-01-01 + 30 days` | `2026-01-31` |
| `@2026-01-01 + 30 'd'` | run-time error `Invalid precision: d` |
| `@2026-01-01 + 1 'mo'` | run-time error `Invalid precision: mo` |
| `@2026-01-01 + 1 hour` | `2026-01-01` (no error) |
| `@T23:30:00 + 1 hour` | `T00:30:00` (wraps, as 2.0.0 says) |

#### Gotcha: a UCUM unit in date arithmetic is a run-time error

- **Symptom:** `@2026-01-01 + 30 'd'` fails with `Invalid precision: d`. As with any run-time
  error, it stops the whole library run (see
  [intervals.md](intervals.md#invalid-intervals-and-unit-intervals)).
- **Probe:** `testDtAddUcumDays`, against `@2026-01-01 + 30 days`, which is `2026-01-31`
  [src: PROBES-2026-10-22 RESULTS.md §25].
- **Spec:** decides: "the quantity units may be specified in singular, plural, or UCUM form"
  (above). The ELM `Add` is silent on unit forms.
- **Well-formed?** Yes.
- **Layer:** engine.
- **Evidence:** the engine maps a unit to a precision only by its name
  [src: CQFW-5.4.0 engine/src/commonMain/kotlin/org/opencds/cqf/cql/engine/runtime/Precision.kt:105-127].
- **Workaround:** use calendar keywords in date arithmetic (`30 days`, `1 month`).
- **Affects:** engine 5.4.0.

#### Gotcha: printed DateTimes omit the offset

- **Symptom:** `@2026-01-31T10:00:00-05:00 + 1 month` prints as `2026-02-28T10:00:00`.
- **Probe:** `testDtFollowup` [src: PROBES-2026-10-22 RESULTS.md §26].
- **Spec:** silent on how a result is displayed.
- **Well-formed?** Yes.
- **Layer:** environment (the language server's display of results).
- **Evidence:** `timezoneoffset from` the same value is `-5.0`.
- **Workaround:** read offsets with `timezoneoffset from`, not from the printed value.
- **Affects:** CQL language server 4.11.0-SNAPSHOT output.

## Pitfalls from the CQL Formatting and Usage Wiki

Guide text, not spec.

- **`day of` drops the time** (page dated 2017-10-12). For a timing phrase with `day of`, the
  answer says it "makes it so it only pays attention to the date rather than the time"; remove the
  precision to compare times [src: CQLWIKI QA-Using-Just-the-Date-of-a-DateTime.md]. Consistent with
  the precision rules above. The page's examples use QDM.
- **Mixing months and days** (Cooking with CQL session 34, 2019; page dated 2026-04-26): "In order
  to avoid the issue with leap years, you should not combine moths and days and only use days to
  avoid this variability." (sic) [src: CQLWIKI Cooking-with-CQL-Q&A-Date-and-Time-Calculations.md]
  Consistent with the arithmetic above: month arithmetic is calendar arithmetic.
- **Leap years** were also an agenda item in Cooking with CQL session 101 (2026-06-25); the page
  lists the agenda and the recording only [src: CQLWIKI Cooking-with-CQL-Examples.md].

## Where the spec is silent

Each was searched in 1.4, 1.5.3 and 2.0.0:

| Question | Finding |
| --- | --- |
| Whether `Date + 1 hour` is an error | silent in 1.4 and 1.5.3; 2.0.0: an error |
| Overflow of Time arithmetic past midnight | silent in 1.4 and 1.5.3; 2.0.0: wraps |
| How an evaluation environment chooses the evaluation-request offset | silent (environment) |
