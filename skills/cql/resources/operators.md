# CQL Operators and Functions Reference

Baseline: CQL 1.5.3. Untagged statements hold in 1.4, 1.5.3 and 2.0.0.
Sources: CQL-1.4, CQL-1.5.3, CQL-2.0.0, CQL-TESTS

A summary of the CQL Reference (`09-b-cqlreference`) and related sections. Quote the section file,
not this page, when a result matters. Source IDs are defined in [SOURCES.md](SOURCES.md). For
type testing, casting, choice types and conversion rules see [type-system.md](type-system.md).

---

## Type System

| Type | Description |
|------|-------------|
| `Integer` | 32-bit signed whole numbers (-2³¹ to 2³¹-1) (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > Types > Integer] |
| `Long` | 64-bit signed integers (1.5+, trial-use) [src: CQL-1.5.3 09-b-cqlreference > Types > Long] |
| `Decimal` | Real values; implementations support at least 28 digits of precision and 8 of scale (1.5+ for "at least … may support more"; **1.4:** states a precision of 28 and a scale of 8 without that note) [src: CQL-1.5.3 09-b-cqlreference > Types > Decimal] |
| `String` | Up to 2³¹-1 characters; supports escape sequences (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > Types > String] |
| `Boolean` | `true` / `false`. `null` (unknown) is not a Boolean value; logical operators use three-valued logic [src: CQL-1.5.3 09-b-cqlreference > Types > Boolean] |
| `Date` | `@YYYY-MM-DD`, `@0001-01-01` to `@9999-12-31`; partial precision supported (`@2014`) [src: CQL-1.5.3 09-b-cqlreference > Types > Date] |
| `DateTime` | `@YYYY-MM-DDThh:mm:ss.fff` plus optional offset `Z` or `±hh:mm`. Year-only form is `@2014T`. With no offset, "the timezone offset of the evaluation request timestamp is assumed". **1.4:** the Types entry lacks that sentence, though 1.4 applies the same default in the `DateTime()` selector, `ToDateTime`, `ConvertsToDateTime`, `duration` and `difference`. **2.0:** adds a note on FHIRPath timezone-offset policies [src: CQL-1.5.3 09-b-cqlreference > Types > DateTime] |
| `Time` | `@Thh:mm:ss.fff`; time-of-day only, no offset. **1.4:** "Time values may also optionally indicate an offset" [src: CQL-1.5.3 09-b-cqlreference > Types > Time] |
| `Quantity` | `{value Decimal, unit String}`; unit is UCUM or a calendar keyword (`days`, `months`, …); no unit means `'1'`. **2.0:** "Systems shall not implicitly convert units other than when performing calculations." [src: CQL-1.5.3 09-b-cqlreference > Types > Quantity] |
| `Interval<T>` | Properties `low`, `high`, `lowClosed`, `highClosed` (1.5+): the 1.4 Author's Guide does not mention them; closed `[`/`]`, open `(`/`)` [src: CQL-1.5.3 02-authorsguide > Operations > Timing and Interval Operators > Operating on Intervals] |
| `List<T>` | Ordered, 0-based [src: CQL-1.5.3 05-languagesemantics > Expression Language Semantics > Data Model > Collection Types]. For `=` on lists see [List equality](#list-equality) |
| `Tuple` | Named element structure (same in 1.4, 2.0) [src: CQL-1.5.3 02-authorsguide > Values > Structured Values (Tuples)] |
| `Code` | `{code, system, version, display}` [src: CQL-1.5.3 09-b-cqlreference > Types > Code] |
| `Concept` | `{codes List<Code>, display}`. **2.0:** "The codes element may be an empty list, or it may be null." [src: CQL-1.5.3 09-b-cqlreference > Types > Concept] |

### List equality

The 1.5.3 CQL Reference contradicts itself; the formal ELM text decides (last bullet). The CQL
Reference says both "This operation uses equality semantics, with the exception that nulls are
considered equal." (1.5+) and "If either argument is null, or contains null elements, the result is
null." [src: CQL-1.5.3 09-b-cqlreference > List Operators > Equal]

- **1.4:** the List Operators entry has only the "contains null elements" rule, while the 1.4
  Comparison Operators entry for Equal already says null elements "are considered equal"
  [src: CQL-1.4 09-b-cqlreference > Comparison Operators > Equal], so 1.4 contradicts itself too.
- **2.0:** drops "or contains null elements": "If either argument is null, the result is null."
  [src: CQL-2.0.0 09-b-cqlreference > List Operators > Equal]
- **The formal text decides.** The ELM `Equal`: "For list types, this means that equality returns
  true if and only if the lists contain elements of the same type, have the same number of
  elements, and for each element in the lists, in order, the elements are equal using equality
  semantics, with the exception that null elements are considered equal." (same in 1.4, 2.0)
  [src: CQL-1.5.3 04-logicalspecification > Comparison Operators > Equal]. The formal pages govern
  ([spec/README.md](spec/README.md#pages-worth-knowing)), so `{ null } = { null }` is `true` at
  1.4 and 1.5.3 too. CQL-TESTS agrees
  [src: CQL-TESTS CqlListOperatorsTest.xml EqualNullNull].

---

## Timing & Interval Operators

```cql
// Ordering
A before B          // A ends before B starts
A after B           // A starts after B ends
A meets B           // either direction: A ends immediately before B starts, or starts immediately after B ends
A meets before B    // A ends immediately before B starts (meets after: the reverse)
A overlaps B        // A and B share at least one point
A starts B          // same start, and end of A <= end of B (A is within B)
A ends B            // same end, and start of A >= start of B (A is within B)

// Containment
A during B          // A is fully contained within B
A includes B        // B is fully contained within A

// Modifiers
A before start of B
A after end of B
A within 7 days of B
A 3 days or less before B
```

Definitions (same in 1.4) [src: CQL-1.5.3 09-b-cqlreference > Interval Operators > Before]
[src: CQL-1.5.3 09-b-cqlreference > Interval Operators > After]
[src: CQL-1.5.3 09-b-cqlreference > Interval Operators > Meets]
[src: CQL-1.5.3 09-b-cqlreference > Interval Operators > Overlaps]
[src: CQL-1.5.3 09-b-cqlreference > Interval Operators > Starts]
[src: CQL-1.5.3 09-b-cqlreference > Interval Operators > Ends]. **2.0:** each adds that the Start
and End semantics apply "particularly when those boundaries are null", and that "Comparisons of
values are performed with the same semantics as specified for comparison of the point type".
`Interval[0, 7] starts Interval[0, 6]` is `false`
[src: CQL-TESTS CqlIntervalOperatorsTest.xml IntegerIntervalStartsFalse].

`during` is a synonym for `included in`. For the point form, it "will return null if the first
argument is null, and false if the second argument is null" (1.5+; **1.4:** "If either argument is
null, the result is null.", though 1.4 also notes that "during is a synonym for included in")
[src: CQL-1.5.3 09-b-cqlreference > Interval Operators > Included In]
[src: CQL-1.5.3 09-b-cqlreference > Interval Operators > Includes].

## Interval Construction and Access

```cql
Interval[start, end]     // inclusive on both ends
Interval[start, end)     // inclusive start, exclusive end
Interval(start, end]     // exclusive start, inclusive end
Interval(start, end)     // exclusive on both ends

start of X               // start point; successor of low if the low bound is open
end of X                 // end point; predecessor of high if the high bound is open
X.low, X.high            // raw boundary values, no successor/predecessor
```

`start of Interval(3, 5]` is 4. With a null bound, a closed bound gives the minimum (or maximum)
value of the point type, and an open bound gives null (same in 1.4)
[src: CQL-1.5.3 09-b-cqlreference > Interval Operators > Start]
[src: CQL-1.5.3 09-b-cqlreference > Interval Operators > End]. **2.0:** an open null bound gives
an uncertainty instead of null: `start of Interval(null, 5]` is `uncertainty[-2147483648, 5]`
[src: CQL-2.0.0 09-b-cqlreference > Interval Operators > Start].

## Interval Set Operations

```cql
A intersect B            // overlap region; null if they don't overlap
A union B                // combined region; null if they neither overlap nor meet
A except B               // region in A not in B; null if B is properly inside A without starting or ending it
collapse X               // merge intervals that overlap or meet; also collapse X per <Quantity>
expand X per day         // List<Interval>: unit-size intervals; Interval (1.5, trial-use): List of points
```

(same in 1.4; **2.0:** adds the point-type comparison note)
[src: CQL-1.5.3 09-b-cqlreference > Interval Operators > Intersect]
[src: CQL-1.5.3 09-b-cqlreference > Interval Operators > Union]
[src: CQL-1.5.3 09-b-cqlreference > Interval Operators > Except]. Tests:
[src: CQL-TESTS CqlIntervalOperatorsTest.xml IntegerIntervalIntersectTestNull]
[src: CQL-TESTS CqlIntervalOperatorsTest.xml IntegerIntervalUnionNull]
[src: CQL-TESTS CqlIntervalOperatorsTest.xml IntegerIntervalExceptNull].

`collapse … per` is in 1.4 too; 1.5.3 adds an explanation of how `per` partitions the value space
(same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > Interval Operators > Collapse]. `expand` on a
single `Interval<T>` is (1.5+, trial-use)
[src: CQL-1.5.3 09-b-cqlreference > Interval Operators > Expand].

The 1.5.3 Union text says the result "ends at the latest starting point in either argument". That
is a typo: its example `Interval[1, 5] union Interval[3, 7]` gives `Interval[1, 7]`. 2.0.0 has the
same typo (same in 1.4) [src: CQL-1.5.3 09-b-cqlreference > Interval Operators > Union].
CQL-TESTS separates the two `expand` forms: `expand { Interval[1, 10] }` gives unit intervals and
`expand Interval[1, 10]` gives points (1.5+)
[src: CQL-TESTS CqlIntervalOperatorsTest.xml ExpandInterval]
[src: CQL-TESTS CqlIntervalOperatorsTest.xml ExpandIntegerIntervalOverload].

## Duration and Difference

```cql
duration in days of X              // = duration in days between start of X and end of X (whole days)
days between A and B               // same as duration in days between A and B
difference in days between A and B // number of day boundaries crossed
```

For duration, "the calculation is performed based on the calendar duration for the precision. For
difference, the calculation is performed by counting the number of boundaries of the specific
precision crossed" (same in 1.4, 2.0)
[src: CQL-1.5.3 02-authorsguide > Operations > Date and Time Operators > Computing Durations and Differences].
`duration … of X` is not `width of X`; width is not defined for Date, DateTime or Time intervals
(same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > Interval Operators > Width].

Units: `years`, `months`, `weeks`, `days`, `hours`, `minutes`, `seconds`, `milliseconds`. Date
values allow years to days only; Time values allow hours to milliseconds only. 1.5+: seconds and
milliseconds "are considered a single precision with decimal semantics". **2.0:** offsets "are
normalized to the timezone offset of the evaluation request timestamp" (1.5.3: "implementations
should normalize") [src: CQL-1.5.3 09-b-cqlreference > Date and Time Operators > Duration]
[src: CQL-1.5.3 09-b-cqlreference > Date and Time Operators > Difference]
[src: CQL-TESTS CqlDateTimeOperatorsTest.xml DateTimeDifferenceMonth].

## Date/Time Arithmetic

```cql
@2025-01-01 + 7 days                        // Date + Quantity → Date
@2025-01-01T00:00:00 - 1 month              // DateTime - Quantity → DateTime
difference in days between @2025-01-01 and @2025-06-01   // Integer
```

There is no Date − Date or DateTime − DateTime operator in 1.5.3 or 2.0.0
[src: CQL-1.5.3 09-b-cqlreference > Date and Time Operators > Subtract]
[src: CQL-1.5.3 09-b-cqlreference > Arithmetic Operators > Subtract]. Use `duration … between` or
`difference … between`. Version notes for Add and Subtract: **1.4:** a time-valued quantity was
converted to the most precise value in the first argument, truncating any decimal; 1.5.3 ignores
the decimal portion above seconds. **2.0:** a unit not allowed for the type is an error, and Time
arithmetic wraps around midnight (`@T23:30:00 + 1 hour` is `@T00:30:00`)
[src: CQL-1.5.3 09-b-cqlreference > Date and Time Operators > Add]
[src: CQL-2.0.0 09-b-cqlreference > Date and Time Operators > Add].

---

## Aggregate Functions

| Function | Signature | Notes |
|----------|-----------|-------|
| `Count` | `Count(List<T>) Integer` | Counts non-null elements. Null or all-null source → 0 (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > Aggregate Functions > Count] [src: CQL-TESTS CqlAggregateFunctionsTest.xml CountNullSource] |
| `Sum` | `Sum(List<T>) T`, T = Integer, Long (1.5+), Decimal, Quantity | Ignores nulls. No non-null elements, or null source → null [src: CQL-1.5.3 09-b-cqlreference > Aggregate Functions > Sum] [src: CQL-TESTS CqlAggregateFunctionsTest.xml SumTestNull] |
| `Min` / `Max` | `Min(List<T>) T`, T = Integer, Long (1.5+), Decimal, Quantity, Date, DateTime, Time, String | Ignores nulls. No non-null elements, or null source → null [src: CQL-1.5.3 09-b-cqlreference > Aggregate Functions > Min] [src: CQL-1.5.3 09-b-cqlreference > Aggregate Functions > Max] |
| `Avg` / `Median` | `Avg(List<Decimal>) Decimal`, `Avg(List<Quantity>) Quantity` | Ignores nulls. No non-null elements → null (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > Aggregate Functions > Avg] [src: CQL-1.5.3 09-b-cqlreference > Aggregate Functions > Median] |
| `Mode` | `Mode(List<T>) T` | A single most frequent value, any T (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > Aggregate Functions > Mode] [src: CQL-TESTS CqlAggregateFunctionsTest.xml ModeTestInteger] |
| `StdDev` / `Variance` | `List<Decimal>` → Decimal, `List<Quantity>` → Quantity | Spec says "statistical"; its examples match sample (n-1) values, against `PopulationStdDev` / `PopulationVariance` (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > Aggregate Functions > StdDev] [src: CQL-1.5.3 09-b-cqlreference > Aggregate Functions > Variance] [src: CQL-TESTS CqlAggregateFunctionsTest.xml StdDevTest1] |
| `AllTrue` | `AllTrue(List<Boolean>) Boolean` | True if all non-null elements are true. Empty, all-null or null source → true (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > Aggregate Functions > AllTrue] [src: CQL-TESTS CqlAggregateFunctionsTest.xml AllTrueEmptyList] |
| `AnyTrue` | `AnyTrue(List<Boolean>) Boolean` | True if any non-null element is true. Empty, all-null or null source → false (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > Aggregate Functions > AnyTrue] [src: CQL-TESTS CqlAggregateFunctionsTest.xml AnyTrueEmptyList] |

---

## List Functions

| Function | Signature | Notes |
|----------|-----------|-------|
| `exists` | `exists(List<T>) Boolean` | True if the list has any **non-null** element. `exists {null}` and `exists null` → false (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > List Operators > Exists] [src: CQL-TESTS CqlListOperatorsTest.xml ExistsListNull] |
| `First` | `First(List<T>) T` | First element; null if empty or null (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > List Operators > First] [src: CQL-TESTS CqlListOperatorsTest.xml FirstEmpty] |
| `Last` | `Last(List<T>) T` | Last element; null if empty or null (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > List Operators > Last] [src: CQL-TESTS CqlListOperatorsTest.xml LastEmpty] |
| `Tail` | `Tail(List<T>) List<T>` | All but the first; empty → empty; null → null (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > List Operators > Tail] [src: CQL-TESTS CqlListOperatorsTest.xml TailEmpty] |
| `Skip` / `Take` | `Skip(List<T>, Integer)`, `Take(List<T>, Integer)` | Use these for subsequences in 1.5 (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > List Operators > Skip] [src: CQL-1.5.3 09-b-cqlreference > List Operators > Take]. There is no CQL `Slice` in 1.5.3 (ELM only); (2.0+, trial-use) `Slice(List<T>, startIndex, endIndex)` with an exclusive end [src: CQL-2.0.0 09-b-cqlreference > List Operators > Slice] |
| `IndexOf` | `IndexOf(List<T>, T) Integer` | Zero-based. Not found or empty list → -1. Either argument null → null. (1.5+) "nulls are considered equal" when searching [src: CQL-1.5.3 09-b-cqlreference > List Operators > IndexOf] [src: CQL-TESTS CqlListOperatorsTest.xml IndexOfNullIn1Null] |
| `Length` | `Length(List<T>) Integer` | Number of elements; null list → 0 (but `Length` of a null String → null) (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > List Operators > Length] [src: CQL-TESTS CqlListOperatorsTest.xml LengthNullList] |
| `distinct` | `distinct(List<T>) List<T>` | Removes duplicates; nulls are considered equal, so many nulls → one null (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > List Operators > Distinct] [src: CQL-TESTS CqlListOperatorsTest.xml DistinctNullNullNull] |
| `flatten` | `flatten(List<List<T>>) List<T>` | One level of nesting removed; null elements are kept (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > List Operators > Flatten] [src: CQL-TESTS CqlListOperatorsTest.xml FlattenListNullAndNull] |
| `ToList` | ELM `ToList` | ELM operator behind list promotion, not in the 1.5.3 CQL reference; null → empty list [src: CQL-1.5.3 04-logicalspecification > Type Operators > ToList] |

---

## Null Handling

| Function | Notes |
|----------|-------|
| `is null` | `X is null` → Boolean (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > Nullological Operators > IsNull] |
| `is not null` | `X is not null` → Boolean [src: CQL-1.5.3 03-developersguide > Nullological Operators] |
| `Coalesce(A, B, C)` | Returns first non-null argument. Takes 2 to 5 arguments, or one `List<T>` for more (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > Nullological Operators > Coalesce] |
| Three-valued logic | `null and true = null`; `null and false = false`; `null or true = true`; `null or false = null` (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > Logical Operators > And] [src: CQL-1.5.3 09-b-cqlreference > Logical Operators > Or] |

---

## String Functions

| Function | Notes |
|----------|-------|
| `Length(String)` | Character count (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > String Operators > Length] |
| `Upper(String)` | Uppercase (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > String Operators > Upper] |
| `Lower(String)` | Lowercase (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > String Operators > Lower] |
| `Combine(List<String>, separator)` | Join list to string; separator optional; null elements ignored. 1.5.3 ignores a null separator; **1.4:** "If either argument is null, or the source list is empty, the result is null." [src: CQL-1.5.3 09-b-cqlreference > String Operators > Combine] [src: CQL-TESTS CqlStringOperatorsTest.xml CombineNull] |
| `Split(String, separator)` | Tokenize to list; separator is a plain string (`SplitOnMatches` takes a regex) (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > String Operators > Split] [src: CQL-1.5.3 09-b-cqlreference > String Operators > SplitOnMatches] |
| `PositionOf(pattern, argument)` | **Pattern first.** Zero-based index of first match; -1 if absent; null if either is null. **2.0:** an empty pattern gives 0 [src: CQL-1.5.3 09-b-cqlreference > String Operators > PositionOf] [src: CQL-TESTS CqlStringOperatorsTest.xml PositionOfBInAB] |
| `Substring(source, start, length)` | Extract substring (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > String Operators > Substring] |
| `StartsWith(source, prefix)` | Prefix test (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > String Operators > StartsWith] |
| `EndsWith(source, suffix)` | Suffix test (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > String Operators > EndsWith] |
| `Matches(source, pattern)` | Regex test; (1.5+) the regex uses partial matching, so anchor with `^` and `$` to match the whole string [src: CQL-1.5.3 09-b-cqlreference > String Operators > Matches] |
| `ReplaceMatches(source, pattern, replacement)` | Regex substitution; (1.5+) partial matching, as for `Matches` [src: CQL-1.5.3 09-b-cqlreference > String Operators > ReplaceMatches] |

---

## Type Conversion Functions

| Function | From → To |
|----------|-----------|
| `ToString` | Boolean, Integer, Long (1.5+), Decimal, Quantity, Ratio, Date, DateTime, Time → String [src: CQL-1.5.3 09-b-cqlreference > Type Operators > ToString] |
| `ToInteger` | String → Integer; Boolean and Long overloads are 1.5+ (**1.4:** String only) [src: CQL-1.5.3 09-b-cqlreference > Type Operators > ToInteger] |
| `ToDecimal` | String → Decimal; Boolean overload (1.5+) [src: CQL-1.5.3 09-b-cqlreference > Type Operators > ToDecimal] |
| `ToDateTime` | String, Date → DateTime. From a Date, 1.5.3 leaves the time components "unspecified, except for the timezone offset"; **1.4:** "set to zero" [src: CQL-1.5.3 09-b-cqlreference > Type Operators > ToDateTime] |
| `ToDate` | String, DateTime → Date (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > Type Operators > ToDate] |
| `ToTime` | String → Time (same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > Type Operators > ToTime] |
| `ToQuantity` | String, Integer, Long (1.5+), Decimal, Ratio → Quantity [src: CQL-1.5.3 09-b-cqlreference > Type Operators > ToQuantity] |
| `ToConcept` | Code, List<Code> (1.5+) → Concept [src: CQL-1.5.3 09-b-cqlreference > Type Operators > ToConcept] |
| `convert X to T` | Text: "If there is no valid conversion from the actual value to the target type, the result is null." **2.0:** "if no conversion is required, the convert operator simply returns the input value." CQL-TESTS expects `convert 'foo' to Integer` to be null [src: CQL-1.5.3 09-b-cqlreference > Type Operators > Convert] [src: CQL-TESTS CqlTypeOperatorsTest.xml StringToIntegerError] |

**Feasibility predicates** (1.5.3): `ConvertsToBoolean`, `ConvertsToDate`, `ConvertsToDateTime`,
`ConvertsToDecimal`, `ConvertsToInteger`, `ConvertsToLong`, `ConvertsToQuantity`, `ConvertsToRatio`,
`ConvertsToString`, `ConvertsToTime`. They return `false` when the input can't be converted. Most
say "If the argument is null, the result is null." `ConvertsToInteger` (1.4, 1.5.3, 2.0.0) and
`ConvertsToLong` (1.5.3, 2.0.0; absent in 1.4) are silent on null. **1.4:** each takes a typed
argument (for example `ConvertsToBoolean(argument String)`) and returns true "if its argument can be
converted"; 1.5.3 takes `Any` and returns true "if its argument is or can be converted"
[src: CQL-1.5.3 09-b-cqlreference > Type Operators > ConvertsToBoolean]
[src: CQL-1.4 09-b-cqlreference > Type Operators > ConvertsToBoolean].

---

## Type Testing and Casting

```cql
5 is Integer              // run-time type is T or derived from T → true
X as Integer              // null if the run-time value is not an Integer
cast X as Integer         // run-time error if the value is not an Integer
```

**2.0:** adds that `null is Integer` "returns false"; 1.4 and 1.5.3 are silent
[src: CQL-2.0.0 09-b-cqlreference > Type Operators > Is]. Details, version differences and probe
results: [type-system.md](type-system.md).

---

## Operator Precedence (High → Low)

Primary (`.`, `[]`, `()`) → Conversion → Unary arithmetic → Extraction → Exponentiation → Multiplicative → Additive → Conditional → Unary list → Unary test → Type operators → Unary logical → Between → Binary list → Comparison → Timing phrase → Interval operators → Equality → Membership → Conjunction (`and`) → Disjunction (`or`, `xor`) → Implication (`implies`)

Binary List is `union`, `intersect`, `except` (1.5.3 Table 3-F). **1.4:** Binary List had the
lowest precedence, below `implies`
[src: CQL-1.5.3 03-developersguide > Lexical Elements > Operator Precedence]
[src: CQL-1.4 03-developersguide > Lexical Elements > Operator Precedence].
