# CQL Skill Held-Out Questions

Answer each question as you would for a colleague debugging a CQL library on a CQL 1.5 engine
(translator and engine 5.4.0). For every claim about what CQL means, quote the spec with its
version and section. Say which layer each behaviour belongs to: spec, translator, engine,
environment or data model. Say "the spec is silent" where it is. Where an engine result differs
from the spec, say so, and give a workaround.

## HO-1. Touching intervals

What do `Interval[1, 5] overlaps Interval[5, 10]` and `Interval[1, 5) overlaps Interval[5, 10]`
return? Does `Interval[1, 5) meets Interval[5, 10]`, and does `Interval[1, 5] meets
Interval[5, 10]`?

## HO-2. A month that isn't a month

What do `months between @2026-01-31 and @2026-02-28` and
`difference in months between @2026-01-31 and @2026-02-28` return, and why do they differ?

## HO-3. A list of an Integer and a Decimal

What is the type of `{ 1, 2.0 }`? What do `First({ 1, 2.0 }) is Integer` and
`First({ 1, 2.0 }) is Decimal` return?

## HO-4. Joining strings with nulls

What should `Combine({ 'a', null, 'b' }, '-')` and `Combine({ 'a', 'b' }, null as String)` return
on a 1.5 engine? Does the answer depend on the CQL version? What would you check before trusting
an engine's result here?

## HO-5. Union, nulls and counting

What does `{ null as Integer, 1 } union { null as Integer }` return, and what is
`Count` of that result?

## HO-6. Substring at the end

What do `Substring('abc', 2)`, `Substring('abc', 3)` and `Substring('abc', 5)` return?

## HO-7. A Date against a DateTime

What do `@2026-01-15 = @2026-01-15T00:00:00.000-04:00` and
`@2026-01-15 same day as @2026-01-15T10:00:00.000-04:00` return? Would the first answer differ
under CQL 1.4?

## HO-8. A probe that changes between machines

A probe library comparing a Date with a DateTime returns `true` on your machine and `null` on a
colleague's. Neither of you changed the CQL. Classify the problem, say what you would record about
each run, and say how you would rewrite the probe so that it gives the same answer everywhere.
