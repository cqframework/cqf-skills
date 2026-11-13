# Held-Out Grades

I graded against the amended key (`heldout/answers.md`). I checked every spec quote and every extra
version claim against the skill's local spec copy.

## Summary

| Question | Grade | Reason |
| --- | --- | --- |
| HO-1 | PASS | All four values are right. The reasons use `end of Interval[1, 5)` = predecessor 4, with the End, Overlaps and Meets quotes (1.5.3). |
| HO-2 | PASS | Gives 0 and 1, explained as whole calendar months vs boundaries crossed, with Duration and Difference quotes. It doesn't treat the two as the same operation. It proposes a probe rather than asserting the engine result. |
| HO-3 | PASS | `List<Decimal>`, the `ToDecimal` conversion, `is Integer` false and `is Decimal` true. Quotes the list-inference rule and Is (1.5.3), and notes the display-only `1`. |
| HO-4 | PASS | Gives the 1.5.3 spec values (`'a-b'`, `'ab'`) with the quote, and notes the 1.4 reference's null-separator difference and the 1.4 reference/ELM contradiction. Says to probe the engine rather than trust it (the full-PASS criterion). It didn't know the engine returns null; the key expected that gap. |
| HO-5 | PASS | Two elements with one null kept, and Count 1. Quotes both Union ("null elements are considered equal") and Count ("non-null elements"). |
| HO-6 | PASS | Gives `'c'`, null and null. Calls index 3 a prose gap and cites the evidence the key asks for: SubstringAB2 gives null; SubstringEmptyAnd0 is inconsistent. |
| HO-7 | PASS | `=` is null for the unspecified-time reason (1.5.3 ToDateTime and Equal quotes). `same day as` is true. The 1.4 "time components set to zero" difference is quoted, with the offset caveat. |
| HO-8 | PASS | Classified as environment (the evaluation-timestamp offset), not an engine bug or spec gap. Records versions, options, timestamp/offset and TZ. Fix: explicit offsets, avoid `Now()`/`Today()`/`TimeOfDay()`, use `same day as`, pin the timestamp. |

**Totals:** 8 PASS, 0 PARTIAL, 0 FAIL.

No cross-cutting fail condition was triggered:

- Every semantics claim presented as spec carries a verbatim quote with a version and section.
- Engine observations are labelled PROBES and kept separate from spec claims.
- All version tags check out.

## Quote check

`check_citations.py` reported OK=39, WRONG-VERSION=1, NOT-FOUND=2, BAD-URL=0. All three flags are
false positives:

- **Line 236, NOT-FOUND [1.4], "joins nulls as empty strings":** this is the answer's own phrase
  describing a probe outcome, not a spec quote.
- **Line 482, NOT-FOUND [1.4], "same calendar day as written":** this is the answer's own phrase
  for the user's intent, not a spec quote.
- **Line 482, WRONG-VERSION [1.4] (found in 1.5.3), "When extracting the Date or Time from a
  DateTime value, ...":** the answer links it to the N1A (1.5.3) DateTime Component From section.
  It is verbatim at `1.5.3/sections/09-b-cqlreference/114-datetime-component-from.md:33`. The
  checker inferred 1.4 from an earlier tag on the line; the attribution is correct. This is a
  checker limitation.

I also verified the extra version claims that the checker can't see:

- **HO-2:** "immediately following calendar date" is in 1.4 and 1.5.3 `014-definition-1.md`.
  2.0.0 changes it to "last calendar date of the ending calendar month". The 2.0.0 Scenario 2
  formula (`... - 1`) is unchanged. So the answer's "2.0.0 contradicts itself" is correct.
- **HO-1:** 2.0.0 adds "particularly when those boundaries are `null`" to the interval operators.
  Confirmed.
- **HO-4:** the 1.4 ELM Combine text ("or any element in the source list of strings is null, the
  result is null") is at `1.4/sections/04-logicalspecification/124-combine.md:21`. Confirmed.
- **HO-6:** the "ommitted" typo appears only in 1.4 `140-substring.md` among the section texts (it
  persists in the XSDs). Confirmed.
- **HO-7:** the Author's Guide normalisation sentence ("but only when the comparison precision is
  hours, ...") is in `1.5.3/sections/02-authorsguide/043-comparing-dates-and-times.md:38`.
  Confirmed.

## Key issues

None of the key's values are contradicted. Two correct findings go beyond the key; neither changes
a grade:

- **HO-2:** the 2.0.0 month Definition changed to "last calendar date" while its Scenario 2 formula
  didn't, so under 2.0.0 the duration answer is ambiguous (0 or 1). The key's version note doesn't
  cover this. The answer is correct (verified). The key could add it as a 2.0.0 version note.
- **HO-7:** the answer notes that, under the Author's Guide normalisation sentence, the `=` result
  at an evaluation offset other than -04:00 could be `false` rather than `null`. The key says only
  "environment-dependent". The answer hedges this as partly a spec gap, which is a fair reading,
  not an error.

## Skill gaps

These are what the skill would need for answers that state engine results rather than only
proposing probes. The answers passed without them.

1. **Combine null handling in engine 5.4.0:** the engine returns null for a null element and for a
   null separator, against the 1.5.3 text. It fails cql-tests `CombineWithNulls` and
   `CombineNullSeparator`. The workaround is `Combine((L) X where X is not null, Coalesce(Sep, ''))`.
   The key expected this gap.
2. **Month duration at end of month:** no probe was recorded for `months between @2026-01-31 and
   @2026-02-28` (engine gives 0, the 1.5.3 reading). The answer couldn't tell whether the engine
   follows 1.5.3 or 2.0.0 here, given the recorded years case (§24) that followed 2.0.0.
3. **Probes not recorded for these exact cases:**
   - closed vs half-open `meets`/`overlaps` (HO-1);
   - `is` on an element of a mixed Integer/Decimal list (HO-3);
   - list `union` with nulls plus `Count` (HO-5);
   - `Substring` at index = length (HO-6);
   - Date `=` DateTime at midnight with an explicit offset (HO-7).

   All match the spec on 5.4.0. Recording them would let answers confirm conformance instead of
   deferring to a probe.
4. **Checker:** `check_citations.py` takes its version from the nearest earlier version tag rather
   than from the quote's own link (an N1A URL means 1.5.3), which gives false WRONG-VERSION flags.
