# Held-Out Answer Key

Grader only. Never shown to the answering agent or to the session that maintains the skill until
grading is complete.

Observed results come from `probes/testSupHeldout.cql` and `probes/testSupHeldout2.cql`, run twice
with identical output on 2026-10-22: translator and engine 5.4.0, language server 4.11.0-SNAPSHOT
(`signatureLevel="All"`, list promotion and demotion disabled), machine offset -04:00, no
evaluation timestamp passed. All spec quotes are CQL 1.5.3 unless marked, and were verified
verbatim in the cql skill's local spec copy.

Grade each answer PASS, PARTIAL or FAIL against "Pass if". Record a short reason.
Cross-cutting fail conditions, for any question:
- a semantics claim presented as spec with no quote, or with a quote that isn't in the spec;
- an engine result presented as the spec;
- version tags that are wrong.

## HO-1. Touching intervals

- **Expected:** `Interval[1, 5] overlaps Interval[5, 10]` is `true`;
  `Interval[1, 5) overlaps Interval[5, 10]` is `false`; `Interval[1, 5) meets Interval[5, 10]` is
  `true`; `Interval[1, 5] meets Interval[5, 10]` is `false`. The engine matches.
- **Spec:**
  - Overlaps: "if the starting or ending point of either interval is in the other, or if the ending
    point of the first interval is greater than or equal to the starting point of the second…",
    using "the semantics described in the Start and End operators".
  - Meets: "the first interval ends immediately before the second interval starts, or … starts
    immediately after the second interval ends. In other words, if the ending point of the first
    interval is equal to the predecessor of the starting point of the second…".
  - `end of Interval[1, 5)` is the predecessor 4, so the half-open interval meets 5 and doesn't
    overlap.
- **Layer:** spec decides; the engine conforms.
- **Pass if:** all four values are right, and the answer uses end-of with the open bracket (end = 4)
  as the reason. PARTIAL if the values are right but no spec reason is given.

## HO-2. A month that isn't a month

- **Expected:** `months between` (duration) is `0`; `difference in months between` is `1`. The
  engine matches.
- **Spec:** 1.5.3 Author's Guide, Computing Durations and Differences: "For duration, the
  calculation is performed based on the calendar duration for the precision. For difference, the
  calculation is performed by counting the number of boundaries of the specific precision
  crossed". Jan 31 → Feb 28 is less than a whole calendar month, but it crosses one month boundary.
- **Layer:** spec decides; the engine conforms.
- **Pass if:** both values are right, and the difference is explained as whole calendar months vs
  boundaries crossed. FAIL if it says the two are the same operation.

## HO-3. A list of an Integer and a Decimal

- **Expected:** `List<Decimal>`. The 1 is converted with `ToDecimal`, so `First(...) is Integer` is
  `false` and `is Decimal` is `true`. The engine matches. Printing may show `1`; that's display
  only.
- **Spec:** Developer's Guide, Type Inference > Literals and Selectors: "if the initial element is
  convertible to the type of a subsequent element, the type of the subsequent element will become
  the new inferred element type for the list". The implicit conversion table has Integer →
  Decimal.
- **Layer:** spec decides (an implicit conversion inserted by the translator); the engine conforms.
- **Pass if:** it gives `List<Decimal>`, says the element is converted, and gets both `is` results.
  FAIL if it says `is Integer` is true because "the literal was 1".

## HO-4. Joining strings with nulls

- **Expected on the spec:** `Combine({ 'a', null, 'b' }, '-')` should be `'a-b'`, and
  `Combine({ 'a', 'b' }, null as String)` should be `'ab'`.
- **Observed:** the engine returns `null` for both, and for every other call with a null element
  or a null separator. Without nulls it works (`Combine({ 'a', 'b' }, '-')` = `'a-b'`).
- **Spec and version** (CQL Reference > String Operators > Combine):
  - **1.5.3** ([N1A #combine](https://cql.hl7.org/N1A/09-b-cqlreference.html#combine),
    `09-b-cqlreference.md:2640-2666`): "If the source argument is null, or the source list is
    empty, the result is null."; "If the separator argument is null, it is ignored."; "For
    consistency with aggregate operator behavior, null elements in the input list are ignored."
    Example: `define "CombineWithNulls": Combine({ 'A', 'B', 'C', null }) // 'ABC'`.
  - **2.0.0** ([#combine](https://cql.hl7.org/09-b-cqlreference.html#combine),
    `09-b-cqlreference.md:2718-2744`): the same three sentences and the same example.
  - **1.4** ([STU4 #combine](https://cql.hl7.org/STU4/09-b-cqlreference.html#combine),
    `09-b-cqlreference.adoc:2501-2528`): "If either argument is null, or the source list is empty,
    the result is null."; "For consistency with aggregate operator behavior, null elements in the
    input list are ignored." Example: `define CombineWithNulls: Combine({ 'A', 'B', 'C', null }) //
    'ABC'`. So under 1.4 the first call is also `'a-b'`, and only the null separator gives null.
- **Tests (informative):** the separately maintained 2.0-era suite (`cql-tests`
  `CqlStringOperatorsTest.xml`) has `CombineWithNulls` (`Combine({'a', 'b', 'c', null})` →
  `'abc'`, line 27) and `CombineNullSeparator` (`Combine({'a', 'b', 'c'}, null)` → `'abc'`, line
  33). Neither test is in the suites shipped with 1.4 or 1.5.3. The engine fails both.
- **Layer:** engine defect.
  - The null-element case contradicts the text of all three versions (1.4, 1.5.3 and 2.0.0 each
    say null elements are ignored).
  - The null-separator case matches the 1.4 rule but not the 1.5.3 or 2.0.0 rule (a version
    gotcha on a 1.5 engine).
- **Workaround (probed, `probes/testSupHeldoutWa.cql`):** filter the nulls and coalesce the
  separator: `Combine((L) X where X is not null, Coalesce(Sep, ''))` gives `'ab'` with a null `Sep`,
  and `'a-b'` with `'-'`, where the unfiltered control gives `null`.
- **Pass if:**
  - it gives the spec values from the 1.5.3 text;
  - it notes the 1.4 separator difference;
  - for full PASS, it either knows or says to check the engine (a probe or the conformance tests)
    rather than trusting it.
  PARTIAL if the spec values are right but there's no version note. FAIL if it says null is
  correct on a 1.5 engine.
- **Skill gap expected:** the skill documented Combine's spec rule, but not this engine defect.

## HO-5. Union, nulls and counting

- **Expected:** the union is `{ null, 1 }`: two elements, with one null kept. `Count` of it is `1`.
  The engine matches.
- **Spec:**
  - Union: "This operator uses equality semantics with the exception that null elements are
    considered equal." So the two nulls collapse to one.
  - Count: "The Count operator returns the number of non-null elements in the source."
- **Layer:** spec decides; the engine conforms.
- **Pass if:** both answers are right (two elements, Count 1) with both reasons. FAIL if it says the
  union drops the null, or that Count is 2.

## HO-6. Substring at the end

- **Expected:** `'c'`, `null`, `null`. The engine matches.
- **Spec:** "If stringToSub or startIndex is null, or startIndex is out of range, the result is
  null." Example: `Substring('ABCDE', 14) // null`. The index is 0-based, so index 3 of a
  three-character string is out of range.
- **Layer:** spec decides; the engine conforms.
- **Pass if:** all three are right, and index 3 is out of range, with no empty string. PARTIAL if
  it says "probably empty string, check the engine".

## HO-7. A Date against a DateTime

- **Expected:** the `=` is `null`; `same day as` is `true`. The engine matches.
- **Spec:**
  - The Date is converted implicitly to a DateTime.
  - 1.5.3 ToDateTime: "For the Date overload, the result will be a DateTime with the time components
    unspecified, except for the timezone offset, which will be set to the timezone offset of the
    evaluation request timestamp."
  - Equal: "If one input has a value for the precision and the other does not, the comparison stops
    and the result is null". The hour is unspecified on one side.
  - Same As compares only "to the specified precision", and "if the specified precision has been
    reached, the comparison stops and the result is true". Both have a day.
- **1.4:** ToDateTime sets "the time components set to zero", so the `=` would compare 00:00 with
  00:00. It would be `true` if the offsets also match (the converted offset comes from the
  evaluation timestamp).
- **Layer:** spec decides at 1.5.3; a version difference from 1.4; the offset makes it
  environment-dependent too.
- **Pass if:** `null` and `true`, with the unspecified-time reason, and the 1.4 difference
  identified. PARTIAL if it misses the 1.4 difference. FAIL if it says the `=` is true at 1.5.3.

## HO-8. A probe that changes between machines

- **Expected:**
  - **Classification:** environment, specifically the evaluation timestamp's timezone offset. The
    Date's converted offset (and any DateTime literal without an offset) takes the evaluation
    request's offset, so different machine offsets give different results.
  - **Record:** engine and translator versions, language-server options, the evaluation
    timestamp, or the machine offset if none is passed.
  - **Determinism:** give every DateTime literal an explicit offset; avoid `Now()`, `Today()` and
    `TimeOfDay()`; compare at an explicit precision (`same day as`) where that's what's meant;
    pass a fixed evaluation timestamp if the harness allows it; run twice.
- **Spec:** the ToDateTime offset rule quoted under HO-7, and the 1.5.3 DateTime default: "the
  timezone offset of the evaluation request timestamp is assumed" when no offset is given.
- **Pass if:** it classifies as environment (not an engine defect), names the offset or timestamp,
  and gives at least the explicit-offset fix. FAIL if it calls it an engine bug or a spec gap.
