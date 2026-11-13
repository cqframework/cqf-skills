# CQL Skill Test Questions

Questions that check whether an agent answers CQL semantics from the spec text, keeps engine and
translator behaviour apart from the spec, and knows where core CQL ends. Each comes from a recorded
misreading in a quality-measure debugging effort, rewritten with System types only, or covers a
recorded engine gotcha. The answer key is in [answers.md](answers.md); keep it out of any copy of
the skill given to an agent under test.

Answer each question as you would for a colleague debugging a CQL library on a CQL 1.5 engine. For
every claim about what CQL means, quote the spec with its version and section. Say which layer each
behaviour belongs to (spec, translator, engine, environment or data model), and say "the spec is
silent" where it is.

## Type testing and choice types

### TQ-01. Null in type tests

What does `(null as Integer) is Integer` return? What does the spec say about
`Tuple { v: null as Integer } is Tuple { v Integer }`? Does
`{ Tuple { v: 1 } } union { Tuple { v: 1.5 } }` produce a list of a Choice type?

### TQ-02. Union of different element types

What is the static type of `{ 1 } union { 'a' }`? When an element of that union is passed to a
function declared `f(x Integer)`, what does the spec say `f` receives for the `'a'` element?

### TQ-03. Two overloads, one Choice argument

Given `define function f(x Integer)` and `define function f(x String)`, and an argument of type
`Choice<Integer, String>`, which overloads does the spec's conversion precedence make applicable,
and what should the translator do? What happens if only `f(x Integer)` is declared and the
argument holds `'a'`?

### TQ-04. A Choice and a common supertype

Does CQL define an implicit conversion from `Choice<A, B>` to `C`, when `A` and `B` are both
subtypes of `C` but `C` is not a component of the choice?

### TQ-05. An `Any` overload against a `Choice` overload

With `define function f(x Any)` and `define function f(x Choice<Integer, String>)`, which does
`f(5)` call according to the spec's conversion precedence, and which does the translator choose?

### TQ-06. `as` to a type outside the choice

`v` has type `Choice<Integer, String>`. Is `v as Decimal` valid CQL? If it fails, is the error the
translator's or the engine's, and how can you tell from the output?

## Diagnosis method

### TQ-07. Where an overload error comes from

A call to an overloaded function fails with "ambiguous" or binds to the wrong overload, and the
error is thrown while the library is being evaluated. Which artifact tells you whether the
translator or the engine lost the distinction, and what in it do you look at?

### TQ-08. Two engines agree

Two CQL engines return the same unexpected value for a test case. What does that rule out, and
what does it not?

### TQ-09. A good control

You want to show that an operator misbehaves. What makes a probe and its control convincing, and
what should you record?

### TQ-10. Model types

Is a data model's `dateTime` type (for example FHIR's) a CQL `DateTime`? Where do implicit
conversions from model types to System types come from, and is that a question the CQL spec
answers?

## Queries and lists

### TQ-11. A query over a null source

What does `(null as DateTime) X return if X is null then 1 else 2` evaluate to, and which spec
sentence decides it?

### TQ-12. `singleton from`

What does `singleton from { }` return, and what does `singleton from { 1, 2 }` do?

### TQ-13. Comparing empty lists

What should `List<Integer> { } = List<Integer> { }` return, and what does engine 5.4.0 return?

## Intervals

### TQ-14. Open and closed null bounds

What do `end of Interval[@2025-01-01T00:00:00Z, null)` and
`end of Interval[@2025-01-01T00:00:00Z, null]` return on a CQL 1.5 engine, and why do they differ?
Does the answer change in CQL 2.0?

### TQ-15. An empty half-open interval

Is `Interval[@2026-01-01T15:00, @2026-01-01T15:00)` a valid interval in CQL?

### TQ-16. Both bounds null

What should `start of Interval(null as Integer, null as Integer)` and
`5 in Interval[null as Integer, null as Integer]` return per the spec, and what does the engine
return?

### TQ-17. The type of an interval with a null bound

Which spec text, if any, defines the run-time type of an interval value whose bound is null? What
does `Interval[1, null] is Interval<Integer>` return on engine 5.4.0?

### TQ-18. Mixed bound types

Is `Interval[1, 'a']` valid CQL? Is `Interval[@2026-01-01, @2026-01-02T00:00:00Z]`? What could make
the second fail when it runs?

### TQ-19. A closed null end in timing comparisons

What is `end of Interval[@2025-12-31T00:00:00Z, null]`? Is
`Interval[@2026-03-01T00:00:00Z, null] during Interval[@2026-01-01T00:00:00Z, @2026-12-31T00:00:00Z]`
true, false or null, and what changes if the null end is open?

### TQ-20. A same-day length of stay

What does `days between @2026-01-01T15:00:00Z and @2026-01-01T19:00:00Z` return, and what happens
if that value is used as the high bound of `Interval[1, days]`?

## Arithmetic, dates and times

### TQ-21. Integer overflow

What should `2147483647 + 1` return, what does engine 5.4.0 return, and how do you avoid
depending on it?

### TQ-22. Precision comparisons

What does `Date(2014, 7, 15) after hour of DateTime(2014, 7, 11, 14, 0, 0)` return? The Author's
Guide gives an answer for this exact expression; is that answer right?

### TQ-23. Milliseconds

What should `@2024-11-15T12:30:00.0Z = @2024-11-15T12:30:00Z` return, and what does engine 5.4.0
return?
