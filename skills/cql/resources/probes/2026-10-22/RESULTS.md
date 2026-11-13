# Probe results, 2026-10-22

Run with the CQL language server's execute command (`cql_execute`, only `cqlFile` set, absolute
path) from a scratch folder that the language server loads, then deleted from there. The probe
sources are the `.cql` files beside this file. Versions reported by every run: translator 5.4.0,
engine 5.4.0, clinicalReasoning 4.13.0, languageServer 4.11.0-SNAPSHOT.

Each library was executed twice, and both runs gave identical output. ELM was inspected once per
library with `cql_view_elm`.

**Language-server compile options differ from the translator defaults.** Every ELM header reads
`signatureLevel="All"`, `translatorOptions="EnableAnnotations,EnableLocators,DisableListDemotion,DisableListPromotion,EnableResultTypes"`.
The translator default is `signatureLevel = Overloads` (`CqlCompilerOptions.kt:37`). None of the
probes below depend on list promotion or demotion.

## 1. The types-and-engine.md repro

| Library | Differs from previous by | Output (both runs) |
| --- | --- | --- |
| `testReproAsWritten` | verbatim repro + `library` line | `Could not find type for model: null and name: Condition, … name: AllergyIntolerance …` (no `using`) |
| `testReproUsingFhir` | + `using FHIR version '4.0.1'` | `Call to operator f(choice<FHIR.AllergyIntolerance,FHIR.Condition>) is ambiguous with: - f(FHIR.Condition) - f(FHIR.AllergyIntolerance)` |
| `testReproFluent` | + `fluent` on both `f` | same ambiguity error |

**Settles:** the repro's comment "binds f(AllergyIntolerance), unconditional As, no warning" is
false. Two overloads that each equal a component give an ambiguity error. With `using FHIR`, the
non-fluent version reports the ambiguity, not a fluent-syntax error, so resolution fails first.

## 2. System-types replacement

`g(v Choice<Integer, String>): v.f()`:

| Library | Overloads of `f` | Output (both runs) | ELM for `v.f()` |
| --- | --- | --- | --- |
| `testChoiceTwoExact` | `f(Integer)`, `f(String)` | `Call to operator f(choice<System.Integer,System.String>) is ambiguous with: - f(System.String) - f(System.Integer), Internal error: could not determine result type` | — |
| `testChoiceOneExact` | `f(Integer)` only (control: drops `f(String)`) | `Int` = `int`, `Str` = `null-int` | `<signature name="t:Integer"/><operand asType="t:Integer" xsi:type="As">` (no `strict`) |
| `testChoiceConvertible` | `f(Decimal)` only | `Int` = `dec`, `Str` = `null-dec` | `ToDecimal` over `<operand asType="t:Integer" xsi:type="As">`; no `Case` |
| `testChoiceAny` | `k(x Any)` | `Str` = `any` | operand is the bare `OperandRef v`; no `As` |

**Settles:**

- Silent narrowing reproduces with System types only. `g('a')` passes `null` to `f(Integer)`.
- A component convertible to the parameter (Integer → Decimal) is narrowed then converted:
  `ToDecimal(As Integer)`. No run-time dispatch over the alternatives.
- `Any` accepts a Choice by subtyping, with no cast.

## 3. Subtype vs supertype parameters (FHIR, no profiles)

`g(event Choice<FHIR.Condition, FHIR.AllergyIntolerance>): event.f()`:

| Library | Overloads of `f` | Output (both runs) | ELM |
| --- | --- | --- | --- |
| `testChoiceSubtypeSilent` | `f(FHIR.AllergyIntolerance)`, `f(FHIR.DomainResource)` | compiles, no diagnostics | `<signature name="fhir:AllergyIntolerance"/><operand asType="fhir:AllergyIntolerance" xsi:type="As">` |
| `testChoiceSupertypeOnly` | `f(FHIR.DomainResource)` only | `Could not resolve call to operator f with signature (choice<FHIR.AllergyIntolerance,FHIR.Condition>).` | — |

**Settles:**

- A supertype of every component (`DomainResource`) is not a candidate. The overload equal to one
  component wins silently, so a Condition argument reaches `f` as `null`.
- Component order is not preserved. `Choice<FHIR.Condition, FHIR.AllergyIntolerance>` is printed
  and serialised as `AllergyIntolerance, Condition`.

## 4. `case when … is` does not narrow

| Library | `then` branch | Output (both runs) | ELM `then` |
| --- | --- | --- | --- |
| `testNoNarrowing` | `r.f()` | compiles | `FunctionRef f`, `<signature name="fhir:DomainResource"/>`, operand bare `OperandRef r` |
| `testNoNarrowingCast` | `(r as FHIR.Condition).f()` (control) | compiles | `FunctionRef f`, `<signature name="fhir:Condition"/>`, operand `As … strict="false"` |

**Settles:** the `is` guard does not change the static type of `r` in the branch; an explicit cast
does.

## 5. Retrieve followed by a fluent call

| Library | Expression | Output (both runs) |
| --- | --- | --- |
| `testRetrieveFluentBare` | `[Condition].c()` | `Syntax error at .` |
| `testRetrieveFluentParen` | `([Condition]).c()` (control) | `A` = `[]` |

**Settles:** the grammar reading. A retrieve must be parenthesised before a fluent call. The "Not
yet confirmed" note in library-syntax.md can be replaced by this result.

## 6. Run-time variant of section 3

`testChoiceSubtypeRuntime`: the overloads `f(FHIR.AllergyIntolerance)` (returns `'null-allergy'` for
a null operand, else `'allergy'`) and `f(FHIR.DomainResource)`. Suggested by a reviewer who had run
it separately; re-run here twice with identical output.

| Expression | Output |
| --- | --- |
| `g(Condition { id: id { value: 'c1' } })` | `null-allergy` |
| `g(AllergyIntolerance { id: id { value: 'a1' } })` | `allergy` |
| `(Condition { id: id { value: 'c2' } }).f()` (control: no Choice) | `domain` |

**Settles:** the same kind of Condition value reaches `f(DomainResource)` when passed directly. It
reaches `f(AllergyIntolerance)` as `null` when passed through `Choice<Condition,
AllergyIntolerance>`.

## 7. Type testing with null

`testTsNullIs` (both runs identical):

| Expression | Output |
| --- | --- |
| `null is Integer` | `false` |
| `(null as Integer) is Integer` | `false` |
| `5 is Integer` (control) | `true` |
| `(5 as Integer) is Integer` (control) | `true` |

## 8. Tuple type tests

`testTsTupleIs` (both runs identical). The translator emits `Is` over the `Tuple` selector; for
`v: null as Integer` the element is `As` over `Null`.

| Expression | Output |
| --- | --- |
| `Tuple { v: null } is Tuple { v Integer }` | `false` |
| `Tuple { v: null as Integer } is Tuple { v Integer }` | `false` |
| `Tuple { v: 1 } is Tuple { v Integer }` (control) | `true` |
| `Tuple { v: 'a' } is Tuple { v Integer }` | `false` |

## 9. List selector inference

`testTsListInfer`, `testTsListMixed` (both runs identical), with the result types from the ELM:

| Expression | ELM result type | ELM detail | Output |
| --- | --- | --- | --- |
| `{ 1, 1.5 }` | `List<System.Decimal>` | `ToDecimal` over `1` | `[1, 1.5]` |
| `{ 1.5, 1 }` | `List<System.Decimal>` | `ToDecimal` over `1` | `[1.5, 1]` |
| `{ }` | `List<System.Any>` | — | `[]` |
| `{ 1, 2 }` (control) | `List<System.Integer>` | — | `[1, 2]` |
| `{ 1, 'a' }` | `List<System.Any>` | no conversion, no error | `[1, a]` |

The language server prints the Decimal `1` as `1`.

## 10. Set operators on lists of different types

`testTsSetOps`, `testTsSetOpsConv`, `testTsElemConv` (both runs identical). In every row with a
Choice result type, each operand is wrapped in `As` (to the list-of-choice type) and no `ToDecimal`
is inserted.

| Expression | ELM result type | Output |
| --- | --- | --- |
| `{ 1 } union { 'a' }` | `List<Choice<System.Integer,System.String>>` | `[1, a]` |
| `{ 1 } intersect { 'a' }` | `List<Choice<System.Integer,System.String>>` | `[]` |
| `{ 1 } except { 'a' }` | `List<Choice<System.Integer,System.String>>` | `[1]` |
| `{ 1 } union { 2 }` (control) | `List<System.Integer>` | `[1, 2]` |
| `{ 1 } union { 1.5 }` | `List<Choice<System.Decimal,System.Integer>>` | `[1, 1.5]` |
| `{ 1.0 } union { 1 }` | `List<Choice<System.Decimal,System.Integer>>` | `[1.0, 1]` |
| `{ 1 } intersect { 1.0 }` | `List<Choice<System.Decimal,System.Integer>>` | `[]` |
| `{ 1, 2 } except { 1.0 }` | `List<Choice<System.Decimal,System.Integer>>` | `[1, 2]` |
| `{ Tuple { v: 1 } } union { Tuple { v: 1.5 } }` | `List<Choice<Tuple{v:System.Decimal},Tuple{v:System.Integer}>>` | both tuples |
| `{ Tuple { v: 1 } } union { Tuple { v: 'a' } }` | `List<Choice<Tuple{v:System.Integer},Tuple{v:System.String}>>` | both tuples |
| `{ Tuple { v: 1 } } union { Tuple { v: 2 } }` (control) | `List<Tuple{v:System.Integer}>` | both tuples |

Controls where the conversion is applied:

| Expression | ELM | Output |
| --- | --- | --- |
| `1 = 1.0` | `Equal(ToDecimal(1), 1.0)` | `true` |
| `1 in { 1.0 }` | `In(ToDecimal(1), List)` | `true` |
| `{ 1 } = { 1.0 }` | `Equal` over a `Query` returning `ToDecimal(X)` | `true` |

**Settles:** for `union`, `intersect` and `except`, operands whose element types differ become a
list of a Choice, even when one element type converts implicitly to the other. Values of different
run-time types then never match, so `{ 1 } intersect { 1.0 }` is empty. `=` and `in` apply the
conversion.

## 11. Conditional expressions with different branch types

`testTsIfMixed`, `testTsIfConvertible` (both runs identical):

| Expression | ELM result type | ELM detail | Output |
| --- | --- | --- | --- |
| `if true then 1 else 'a'` | `Choice<System.Integer,System.String>` | `As` over each branch | `1` |
| `if true then 1 else 1.5` (control) | `System.Decimal` | `ToDecimal` over `1` | `1` |

No diagnostic was returned. The translator builds the Choice in `ensureCompatibleTypes`
(`LibraryBuilder.kt:2210-2222` at v5.4.0), and the 2.0.0 message code `003-10000` does not occur in
the v5.4.0 source.

## 12. Casts, conversion and implicit null casting

`testTsCasts`, `testTsStrictCast`, `testTsStrictCastOk` (both runs identical):

| Expression | ELM | Output |
| --- | --- | --- |
| `g('a')`, `g(v Choice<Integer, String>): v as Integer` | `As` | `null` |
| `g(1)` (control) | `As` | `1` |
| `h('a')`, `h(v Choice<Integer, String>): cast v as Integer` | `As` with `strict="true"` | run-time error `Cannot cast 'a' to org.hl7.elm.r1.NamedTypeSpecifier@e4cca031.` |
| `h(1)` (control, separate library) | `As` with `strict="true"` | `1` |
| `5 * null` | `Multiply(5, As(Null))` | `null` |
| `convert 'foo' to Integer` | `ToInteger('foo')` | `null` |
| `convert '5' to Integer` (control) | `ToInteger('5')` | `5` |
| `Interval[1, null] properly includes null` | `ProperContains` (point overload), right operand `As(Null)` | `null` |

## 13. Normalising element types before a set operator

`testTsNormalise` (both runs identical). An earlier draft of this probe,
`({ 1 } X return ToDecimal(X)) intersect { 1.0 }` with no parentheses around the list selector,
fails with `Syntax error at X`; a list selector must be parenthesised to be a query source.

| Expression | ELM result type | Output |
| --- | --- | --- |
| `(({ 1 }) X return ToDecimal(X)) intersect { 1.0 }` | `List<System.Decimal>` (the `return` is `distinct` by default) | `[1]` |
| `List<Decimal> { 1 } intersect { 1.0 }` | `List<System.Decimal>`, `ToDecimal` inside the selector | `[1]` |
| `{ 1 } intersect { 1.0 }` (control) | `List<Choice<System.Decimal,System.Integer>>` | `[]` |

**Tooling caveat:** `cql_view_elm` returned a stale AST for this file after it was edited; it showed
the previous version. The ELM above comes from an identical copy saved under a new library name.
Re-check ELM after editing a probe.

## 14. A null tuple element and a choice-typed union

`testTsUnionNullElem`: suggested by a reviewer who had run a similar probe separately; re-run here
twice with identical output. Each `*Branch` define is a list of two tuples
`Tuple { d: <DateTime>, v: … }`; the second branch, `DecimalBranch`, has one tuple with `v: 1.5`.

| First branch, second tuple | First branch ELM type | Union ELM | `Count` of the union |
| --- | --- | --- | --- |
| `v: null as Integer` | `List<Tuple{d:DateTime,v:Integer}>` | `As` on both operands, `List<Choice<Tuple{…v:Decimal},Tuple{…v:Integer}>>` | `1` |
| `v: null` | `List<Tuple{d:DateTime,v:Any}>` | no `As`; result `List<Tuple{d:DateTime,v:Any}>` | `3` |
| `v: 2` (control) | `List<Tuple{d:DateTime,v:Integer}>` | `As` on both operands, same Choice type | `3` |

With the typed null, the union holds only the `DecimalBranch` tuple. Both tuples of the Integer
branch are lost, including the one with `v: 1`: the `As` over the whole list operand fails, so the
operand contributes nothing. With the untyped null, the branch infers `v: Any`, a supertype of the
other tuple type, so no cast is applied and all three tuples survive.

**Settles:** a typed null element in a list that a choice-typed set operator casts can make that
whole operand disappear, with no diagnostic; an untyped null hides the problem by widening the
element type to `Any`. Engine behaviour combined with translator typing; see §8 and §10.

## 15. `exists` on a Boolean and on lists of false or null

`testExistsBoolean`, `testExistsList` (both runs identical). The language server compiles with list
promotion disabled (§1).

| Expression | Output |
| --- | --- |
| `exists false` | compile error: `Could not resolve call to operator Exists with signature (System.Boolean).` |
| `exists { false }` (control) | `true` |
| `exists { null }` | `false` |

**Settles:** with list promotion disabled, `exists` does not accept a single Boolean. A list
holding `false` exists (it has a non-null element); a list holding only `null` does not. A result
of `true` for `exists false` needs list promotion, which wraps `false` in a list.

## 16. A single null bound, open or closed

`testIvNullBounds`, `testIvNullOps` (both runs identical).

| Expression | Output |
| --- | --- |
| `end of Interval[1, null]` | `2147483647` |
| `end of Interval[1, null)` | `null` |
| `start of Interval[null, 5]` | `-2147483648` |
| `start of Interval(null, 5]` | `null` |
| `end of Interval[@2025-01-01T00:00:00, null]` | `9999-12-31T23:59:59.999+00:00` |
| `end of Interval[@2025-01-01T00:00:00, null)` | `null` |
| `end of Interval[@2025-01-01T00:00:00, @2025-12-31T00:00:00]` (control) | `2025-12-31T00:00:00` |
| `Interval[@2025-01-01T00:00:00, null].high` and `….null).high` | `null` (the raw bound) |
| `@2026-06-01 during Interval[@2025-01-01, null]` | `true` |
| `@2026-06-01 during Interval[@2025-01-01, null)` | `null` |
| `@2026-06-01 during Interval[@2025-01-01, @2026-12-31]` (control) | `true` |
| `Interval[@2026-02-01, @2026-03-01] during Interval[@2025-01-01, null]` | `true` |
| `Interval[@2026-02-01, @2026-03-01] during Interval[@2025-01-01, null)` | `null` |
| `Interval[@2026-02-01, @2026-03-01] overlaps Interval[@2025-01-01, null]` | `true` |
| `Interval[@2026-02-01, @2026-03-01] overlaps Interval[@2025-01-01, null)` | `null` |
| `Interval[@2024-02-01, @2024-03-01] overlaps Interval[@2025-01-01, null)` | `false` |
| `end of Interval[@2025-01-01, null] after @2026-12-31` | `true` |
| `end of Interval[@2025-01-01, null) after @2026-12-31` | `null` |

**Settles:** this engine follows the 1.5.3 Start/End text: a closed null bound is the point type's
minimum or maximum, an open null bound is `null` (not the 2.0.0 uncertainty). An open null bound
makes `during`, `overlaps` and `after` null unless the known bound alone decides the answer.

## 17. Both bounds null

`testIvSuiteDisputes`, `testIvTypedMax`, `testIvPointFromMax`, `testIvPointFromTypedMax` (both runs
identical). The translator types the untyped selectors `Interval<Any>`.

| Expression | Output |
| --- | --- |
| `Interval[null, null]` | `null` |
| `Interval[null as Integer, null as Integer]` | `null` |
| `5 in Interval[null, null]`, and with `null as Integer` bounds | `false` |
| `5 in Interval(null, null)`, and with `null as Integer` bounds | `false` |
| `Interval[null, null] overlaps Interval[1, 10]`, and typed | `null` |
| `Interval(null, null) overlaps Interval[1, 10]`, and typed | `null` |
| `Interval[null, null] starts Interval[1, 10]`, and typed | `null` |
| `Interval[null, null] union Interval[1, 10]`, and typed | `null` |
| `start of Interval[null, null]`, and typed | `null` |
| `point from Interval[null, null]`, and typed | `null` |
| `collapse { Interval(null, null) }` | `[]` |
| `Interval[1, 10] intersect Interval[5, null)` | `[5, null)` |
| `Interval(null, 5] meets after Interval[11, null)` | `false` |

**Settles:** the engine turns any interval whose bounds are both null into a null interval, so the
closed-null "maximum interval" never exists at run time. Source: `IntervalEvaluator.kt:41-47` at
v5.4.0, with the comment "An interval with no boundaries is not an interval" and a TODO noting that
the spec allows such intervals.

## 18. Invalid intervals

`testIvHalfOpenUnit`, `testIvReversed`, `testIvHalfOpenUnitDT`, `testIvUnit` (both runs identical).
Each error library holds only the failing define.

| Expression | Output |
| --- | --- |
| `Interval[1, 1)` | run-time error `Invalid Interval - the ending boundary (1) must be greater than or equal to the starting boundary (1).` |
| `Interval[1, -1]` | run-time error, same message with `(-1)` and `(1)` |
| `Interval[@2026-01-01T15:00, @2026-01-01T15:00)` | run-time error, same message |
| `Interval[1, 1]` (control) | `[1, 1]` |
| `point from Interval[1, 1]` (control) | `1` |
| `Interval[@2026-01-01T15:00, @2026-01-01T15:01)` (control) | valid (see §19) |

The messages carry no "loaded, but had errors" prefix, so they are run-time errors, raised in
`runtime/Interval.kt:55-69` at v5.4.0, which compares `start` and `end` (after successor and
predecessor).

## 19. Display of open bounds (tooling caveat)

`testIvMinuteBounds` (both runs identical). The language server prints
`Interval[@2026-01-01T15:00, @2026-01-01T15:01)` as `[2026-01-01T15:00, 2026-01-01T15:00)`.
`.low` is `15:00`, `.high` is `15:01` and `end of` is `15:00`; the closed form prints
`[…15:00, …15:01]`. The printed interval shows the predecessor with an open bracket. Read bounds with
`.low`, `.high`, `start of` and `end of`, not from the printed value.

## 20. Guide claims about intervals, re-run

`testIvWikiCollapse`, `testIvStartsKeyword`, `testIvStartsControl`, `testIvStartsInQuery`,
`testIvStartsInQueryCtl` (both runs identical).

| Expression | Output |
| --- | --- |
| `collapse { Interval[@2021-01-06, @2021-01-08], Interval[@2021-01-08, null] }` | `[[2021-01-06, 9999-12-31]]` |
| the same plus `Interval[@2021-01-15, @2021-01-18]` | `[[2021-01-06, 9999-12-31]]` |
| the same with `Interval[@2021-01-08, null)` | `[[2021-01-06, 2021-01-08], [2021-01-08, null)]` |
| `Interval[@2026-01-01, @2026-01-10] start 3 days or less before @2026-01-03` | compile error `Syntax error at start` |
| the same inside a query `with … such that E start 3 days or less before start of A` | compile error `Syntax error at start, …` |
| `… starts 3 days or less before @2026-01-03` (control) | `true`; in the query, the row is kept |
| `Interval[@2026-01-01, @2026-01-10] 3 days or less before @2026-01-03` | `false` (the end, Jan 10, is compared) |

## 21. One invalid interval fails the whole library run

`testIvOneBadDefine`, `testIvOneBadDefineCtl` (both runs identical). Suggested by a reviewer who had
run it separately; re-run here.

| Library | Defines | `cql_execute` output |
| --- | --- | --- |
| `testIvOneBadDefine` | `"Fine": 1 + 1`, `"HalfOpenEqual": Interval[1, 1)`, `"AlsoFine": 2 + 2` | only the error `Invalid Interval - the ending boundary (1) must be greater than or equal to the starting boundary (1).`; no values for `Fine` or `AlsoFine` |
| `testIvOneBadDefineCtl` (control: `]` for `)`) | the same, with `Interval[1, 1]` | `Fine` = `2`, `HalfOpenEqual` = `[1, 1]`, `AlsoFine` = `4` |

**Settles:** observed through `cql_execute` (language server 4.11.0-SNAPSHOT, translator and engine
5.4.0): a run-time error in one define stops the whole library evaluation, so no define in that
library reports a value.

## Date and time probes: environment

Sections 22 to 26 ran on 2026-10-22 on a machine at offset `-04:00` (EDT). `cql_execute` takes no
evaluation-request timestamp parameter, so the evaluation offset is the machine's; section 23
shows it directly (`@2026-01-15T10:00:00 = @2026-01-15T10:00:00-04:00` is `true`). Literals carry
explicit offsets except where the missing offset is the thing tested. No probe uses `Now()`,
`Today()` or `TimeOfDay()`. Every library ran twice with identical output. One ELM view
(`testDtUnits`) was again stale after an edit (see §13); the unit nodes it showed do not depend on
the edit.

## 22. Precision

`testDtPrecision`, `testDtFollowup`.

| Expression | Output |
| --- | --- |
| `@2026-01 = @2026-01-15` | `null` |
| `@2026 < @2026-02-15` | `null` |
| `@2025 < @2026-02-15` (control) | `true` |
| `@2026-01 same month as @2026-01-15` | `true` |
| `@2026-01 same day as @2026-01-15` | `null` |
| `@2026-01-15 same day as @2026-01-15` (control) | `true` |
| `@2026-01-01 <= @2026-01` | `null` |
| `@2026-01 >= @2026-01-01` | `null` |
| `@2026-01 <= @2026-12-31` | `true` |
| `@2026-01-15 in Interval[@2026-01-01, @2026-01-31]` | `true` |
| `@2026-01 in Interval[@2026-01-15, @2026-02-15]` | `null` |
| `@2026-01 during Interval[@2026-01-01, @2026-12-31]` | `null` |
| `Date(2014, 7, 15) after hour of DateTime(2014, 7, 11, 14, 0, 0)` (the 1.5.3 Author's Guide example, documented as null) | `true` |
| `@2026-01-15 after hour of @2026-01-14T10:00:00Z` | `true` |
| `@2024-11-15T12:30:00.0Z = @2024-11-15T12:30:00Z` | `null` |
| `@2024-11-15T12:30:00.0 = @2024-11-15T12:30:00` (2.0.0 example, documented true) | `null` |
| `@2024-11-15T12:30:00.5 = @2024-11-15T12:30:00` (2.0.0 example, documented false) | `null` |
| `@2024-11-15T12:30:00.5 = @2024-11-14T12:30` (2.0.0 example, documented null) | `false` |
| `@2024-11-15T12:30:00.5Z = @2024-11-15T12:30Z` | `null` |

## 23. Timezone offsets

`testDtTimezone`, `testDtFollowup` (evaluation offset `-04:00`).

| Expression | Output |
| --- | --- |
| `@2012-03-10T10:20:00.999+07:00 = @2012-03-10T09:20:00.999+06:00` | `true` |
| `@2012-03-10T10:20:00.999+07:00 = @2012-03-10T10:20:00.999+06:00` | `false` |
| `@2026-01-15T23:30:00-05:00 = @2026-01-16T04:30:00Z` (same instant) | `true` |
| `@2026-01-15T23:30:00-05:00 same day as @2026-01-16T04:30:00Z` | `false` |
| `day from @2026-01-15T23:30:00-05:00` | `15` |
| `@2026-01-15T10:00:00 = @2026-01-15T10:00:00Z` | `false` |
| `@2026-01-15T10:00:00 = @2026-01-15T10:00:00-04:00` | `true` |
| `@2026-01-15T10:00:00 = @2026-01-15T10:00:00-05:00` | `false` |
| `@2026-01-15 = @2026-01-15T10:00:00Z` | `null` |
| `@2026-01-15 same day as @2026-01-15T10:00:00Z` | `true` |
| `@2026-01-15 < @2026-01-16T00:00:00Z` | `null` |
| `@2026-01-15 < @2026-01-16T00:00:00-04:00` | `true` |

## 24. Duration and difference

`testDtDuration`.

| Expression | Output |
| --- | --- |
| `months between @2014-01-31 and @2014-02-01` | `0` |
| `difference in months between @2014-01-31 and @2014-02-01` | `1` |
| `years between @2011-12-31 and @2012-01-01` | `0` |
| `difference in years between @2011-12-31 and @2012-01-01` | `1` |
| `years between @2012-02-29 and @2014-02-28` | `2` |
| `days between @2014-01-15 and @2014-02` | `[17, 44]` |
| `… > 2`, `… > 20`, `… > 50` | `true`, `null`, `false` |
| `hours between @2017-03-12T01:00:00-07:00 and @2017-03-12T03:00:00-06:00` | `1` |
| `days between @2017-03-12T00:00:00-07:00 and @2017-03-13T00:00:00-06:00` | `1` |
| `difference in days between` the same | `1` |

## 25. Quantities and units

`testDtUnits`, `testDtAddUcumDays`, `testDtAddUcumMonth`, `testDtAddCalendarDays`. The ELM keeps the
units as written (`'month'`, `'days'`, `'d'`, `'mo'`); the translator does no unit conversion.

| Expression | Output |
| --- | --- |
| `1 year = 12 months` | `null` |
| `1 day = 24 hours` | `null` |
| `1 month = 30 days` | `null` |
| `1 month ~ 30 days` | `false` |
| `1 'mo' = 1 month` | `null` |
| `1 'mo' ~ 1 month` | `true` |
| `1 'd' = 1 day` | `true` |
| `5 days > 3` (ELM: `ToQuantity(3)`) | `null` |
| `@2026-01-01 + 30 'd'` | run-time error `Invalid precision: d` |
| `@2026-01-01 + 1 'mo'` | run-time error `Invalid precision: mo` |
| `@2026-01-01 + 30 days` (control) | `2026-01-31` |

Sources at v5.4.0: `runtime/Precision.kt:105-127` maps a unit to a precision only by name prefix
(`year`, `month`, `day`, …) and throws `Invalid precision` otherwise; `runtime/Quantity.kt:40-45`
compares quantities only when their units are in the same keyword family, and returns null otherwise.

## 26. Date and time arithmetic

`testDtArithmetic`, `testDtAddHourToDate`, `testDtFollowup`.

| Expression | Output |
| --- | --- |
| `@2024-01-31 + 1 month` | `2024-02-29` |
| `@2023-01-31 + 1 month` | `2023-02-28` |
| `@2024-02-29 + 1 year` | `2025-02-28` |
| `@2024-03-31 - 1 month` | `2024-02-29` |
| `@2024-01-31 + 1 month + 1 month` | `2024-03-29` |
| `@2024-01-31 + 2 months` | `2024-03-31` |
| `DateTime(2014) + 18 months` | `2015` |
| `@2016-01-01 - 1.1 years` | `2015-01-01` |
| `@T23:30:00 + 1 hour` | `T00:30:00` |
| `@2026-01-01 + 1 hour` | `2026-01-01` (no error) |
| `@2026-01-31T10:00:00-05:00 + 1 month` | printed `2026-02-28T10:00:00`; `timezoneoffset from` it is `-5.0` |

The printed DateTime omits the offset; read offsets with `timezoneoffset from`.

## 27. Logical operators and null tests

`testNlLogic` (both runs identical).

| Expression | Output |
| --- | --- |
| `null and false` / `null and true` | `false` / `null` |
| `null or true` / `null or false` | `true` / `null` |
| `null xor true` | `null` |
| `not null` | `null` |
| `false implies null` / `null implies true` / `null implies false` | `true` / `true` / `null` |
| `(null as Boolean) is true` / `is false` | `false` / `false` |
| `null is null` | `true` |

All null operands are `null as Boolean`, except in `null is null`.

## 28. Equality and equivalence

`testNlEquality`, `testNlUntypedNullEq`, `testNlUntypedNullEquiv`, `testNlTypedNullEq` (both runs
identical).

| Expression | Output |
| --- | --- |
| `null = null` (untyped) | compile error `Call to operator Equal(System.Any, System.Any) is ambiguous with: …` |
| `null ~ null` (untyped) | compile error `Call to operator Equivalent(System.Any, System.Any) is ambiguous with: …` |
| `(null as Integer) = (null as Integer)` | `null` |
| `(null as Integer) ~ (null as Integer)` | `true` |
| `1 = null` / `1 ~ null` | `null` / `false` |
| `1 != null` / `1 !~ null` | `null` / `true` |
| `'' ~ (null as String)` | `false` |
| `{ null } = { null }` / `{ null, 1 } = { null, 1 }` | `true` / `true` |
| `{ null, 1 } ~ { null, 1 }` | `true` |
| `Tuple { x: 1, y: null } = Tuple { x: 1, y: null }` | `true` |
| `Tuple { x: 1, y: 1 } = Tuple { x: null, y: 1 }` | `null` |
| `Tuple { x: 1, y: 1 } = Tuple { x: null, y: 2 }` | `null` |
| `Tuple { x: 1, y: null } ~ Tuple { x: 1, y: null }` | `true` |
| `Tuple { x: 1, y: 1 } ~ Tuple { x: null, y: 1 }` | `false` |

## 29. Membership and list set operators

`testNlMembership` (both runs identical).

| Expression | Output |
| --- | --- |
| `null in { 1, null }` / `null in { 1, 2 }` | `true` / `false` |
| `5 in (null as List<Integer>)` | `false` |
| `{ 1, null } contains null` / `{ 1, 2 } contains null` | `true` / `false` |
| `(null as List<Integer>) contains 4` | `false` |
| `(null as List<Integer>) union { 4, 5 }` | `[4, 5]` |
| `{ 1, 3 } intersect (null as List<Integer>)` | `null` |
| `(null as List<Integer>) except { 1 }` | `null` |
| `{ 1, 3 } except (null as List<Integer>)` | `[1, 3]` |
| `{ null, 1, 3 } intersect { null, 3, 7 }` | `[null, 3]` |
| `distinct { null, null, 1 }` | `[null, 1]` |

## 30. Arithmetic, strings and aggregates

`testNlArith`, `testNlOverflow` (both runs identical).

| Expression | Output |
| --- | --- |
| `1 + (null as Integer)` | `null` |
| `5 / 0`, `5 div 0`, `5 mod 0` | `null`, `null`, `null` |
| `'a' + (null as String)` / `'a' & (null as String)` | `null` / `a` |
| `Length(null as String)` | `null` |
| `Count({ null, 1 })` / `Sum({ null as Integer, null as Integer })` | `1` / `null` |
| `2147483647 + 1` and `(maximum Integer) + 1` | `-2147483648` |
| `-2147483648 - 1` | `2147483647` |
| `2147483647 * 2` | `-2` |
| `9223372036854775807L + 1L` | `-9223372036854775808` |
| `2147483646 + 1` (control) | `2147483647` |

**Settles:** Integer and Long arithmetic wraps on overflow instead of returning null.
`AddEvaluator.kt:34-37` at v5.4.0 adds with plain Kotlin `Int` and `Long` arithmetic.

## 31. Conditionals and Coalesce

`testNlConditional` (both runs identical).

| Expression | Output |
| --- | --- |
| `if (null as Boolean) then 1 else 2` | `2` |
| `case when (null as Boolean) then 1 else 2 end` | `2` |
| `case (null as Integer) when 5 then 1 else 2 end` | `2` |
| `case 5 when (null as Integer) then 1 when 5 then 3 else 2 end` | `3` |
| `Coalesce(null, null, 3)` / `Coalesce({ null, 2, 3 })` | `3` / `2` |
| `Coalesce(null as Integer, null as Integer)` | `null` |

## 32. Nulls in queries

`testNlQuery` (both runs identical).

| Expression | Output |
| --- | --- |
| `({ 1, null, 3 }) X where X > 1` | `[3]` |
| `({ 1, null, 3 }) X where not (X > 1)` | `[1]` |
| `({ 3, null, 1 }) X sort asc` / `sort desc` | `[null, 1, 3]` / `[3, 1, null]` |
| `({ 1, null, null }) X return X` | `[1, null]` |
| `({ 1, null, null }) X return all X` | `[1, null, null]` |
| `(null as List<Integer>) X return X` | `null` |
| `(List<Integer> { }) X return X` | `[]` |
| `exists (({ 1, 2 }) X return (null as Integer))` | `false` |

## 33. Workarounds for recorded gotchas

`testWaOverflow2`, `testWaTypedList`, `testWaMaxInterval`, `testWaTupleUnion` (both runs
identical). A first draft of the overflow probe used `{ 2147483647, 1 } X return …` without
parentheses and failed with `Syntax error at X` (see §13); `testWaOverflow2` is the corrected file.

| Expression | Output |
| --- | --- |
| `2147483647 + 1` (the gotcha) | `-2147483648` |
| `ToLong(2147483647) + 1` | `2147483648` |
| `ToDecimal(2147483647) + 1` | `2147483648` |
| `Sum({ 2147483647, 1 })` (the gotcha, in an aggregate) | `-2147483648` |
| `Sum(({ 2147483647, 1 }) X return all ToDecimal(X))` | `2147483648` |
| `{ 1, 'a' }` (the gotcha) | ELM `List<System.Any>` |
| `List<Choice<Integer, String>> { 1, 'a' }` | ELM `List<Choice<System.Integer,System.String>>`, an `As` on each element |
| `5 in Interval[null as Integer, null as Integer]` (the gotcha) | `false` |
| `5 in Interval[minimum Integer, maximum Integer]` | `true` |
| `@2026-06-01 in Interval[minimum Date, maximum Date]` | `true` |
| `5 in Interval[minimum Integer, null as Integer]` | `true` |
| `Count("TypedNullBranch" union "DecimalBranch")` (the gotcha, §14) | `1` |
| `Count(("TypedNullBranch" X return Tuple { d: X.d, v: ToDecimal(X.v) }) union "DecimalBranch")` | `3` |

**Settles:** each workaround gives the spec's answer on this engine. Aggregates wrap too: `Sum` of
Integers overflows like `+`.

## 34. `singleton from`

`testLqSingleton`, `testLqSingletonMany` (both runs identical).

| Expression | Output |
| --- | --- |
| `singleton from List<Integer> { }` | `null` |
| `singleton from { 1 }` | `1` |
| `singleton from (null as List<Integer>)` | `null` |
| `singleton from { null as Integer }` | `null` |
| `singleton from { 1, 2 }` (own library) | run-time error `Expected a list with at most one element, but found a list with multiple elements.` |

## 35. Duplicates: queries and list operators

`testLqDistinct` (both runs identical). ELM: the queries without a `return` clause have no
`ReturnClause`; `return X` and `return distinct X` compile to `ReturnClause (distinct)`;
`return all X` to `ReturnClause` without `distinct`.

| Expression | Output |
| --- | --- |
| `({ 1, 1, 2 }) X` (no `return`) | `[1, 1, 2]` |
| `({ 1, 1, 2 }) X where X > 0` (no `return`) | `[1, 1, 2]` |
| `({ 1, 1, 2 }) X return X` | `[1, 2]` |
| `({ 1, 1, 2 }) X return all X` | `[1, 1, 2]` |
| `({ 1, 1, 2 }) X return distinct X` | `[1, 2]` |
| `distinct { 1, 1, null, null }` | `[1, null]` |
| `{ 1, 1, 2 } union { 2, 3 }` | `[1, 2, 3]` |
| `{ 1, 1, 2 } intersect { 1, 1 }` | `[1]` |
| `{ 1, 1, 2 } except { 2 }` | `[1]` |
| `flatten { { 1, 1 }, { 1 } }` | `[1, 1, 1]` |

## 36. Multi-source queries

`testLqMultiSource` (both runs identical).

| Expression | Output |
| --- | --- |
| `from ({ 1, 2 }) A, ({ 10, 20 }) B return all A + B` | `[11, 21, 12, 22]` |
| `Count(` the same `)` | `4` |
| `from ({ 1, 2 }) A, (5) B return all A + B` | `[6, 7]` |
| `from (1) A, (2) B return A + B` | `3` (a single value, not a list) |
| `from ({ 1, 2 }) A, (List<Integer> { }) B return all A` | `[]` |
| `from ({ 1, 2 }) A, (null as List<Integer>) B return all A` | `[]` |
| `from (null as List<Integer>) A, (null as List<Integer>) B return all A` | `null` |

## 37. `with` and `without`

`testLqRelationships` (both runs identical).

| Expression | Output |
| --- | --- |
| `({ 1, 2 }) X with (List<Integer> { }) Y such that Y = X` | `[]` |
| `({ 1, 2 }) X without (List<Integer> { }) Y such that Y = X` | `[1, 2]` |
| `({ 1, 2 }) X with ({ 2, 3 }) Y such that Y = X` | `[2]` |
| `({ 1, 2 }) X without ({ 2, 3 }) Y such that Y = X` | `[1]` |
| `… with ({ 2 }) Y such that (null as Boolean)` | `[]` |
| `… without ({ 2 }) Y such that (null as Boolean)` | `[1, 2]` |

## 38. Sorting

`testLqSort2`, `testLqSortAlias`, `testLqSortThis`, `testLqSortThisTuple`, `testLqSortUntypedNull`
(both runs identical). An earlier draft, `testLqSort`, combined the untyped-null case with the
others and failed to compile as a whole.

| Expression | Output |
| --- | --- |
| `({ 3, 1, 2 }) X sort asc` | `[1, 2, 3]` |
| `({ Tuple { a: 2 }, Tuple { a: 1 } }) T sort by a` | `a: 1`, then `a: 2` |
| `({ … a: 2, a: 1, a: null as Integer }) T sort by a desc` | `a: 2`, `a: 1`, `a: null` |
| `… T sort by T.a` | compile error `Could not resolve identifier T in the current library.` |
| `({ 3, 1, 2 }) X sort by $this desc` | run-time error `Could not resolve path '$this' on 3.` |
| `({ Tuple { a: 2 }, Tuple { a: 1 } }) T sort by $this.a` | `a: 1`, then `a: 2` |
| `({ Tuple { a: 2 }, Tuple { a: null } }) T sort by a` | compile error `Call to operator Less(System.Any, System.Any) is ambiguous with: …` |

## 39. Empty lists and indexing

`testLqEmpty`, `testLqEmptyEquiv` (both runs identical).

| Expression | Output |
| --- | --- |
| `List<Integer> { } = List<Integer> { }` | `null` |
| `List<Integer> { } = { 1 }` | `null` |
| `List<Integer> { } ~ List<Integer> { }` | `true` |
| `{ 1 } = { 1 }` (control) | `true` |
| `First(List<Integer> { })`, `Sum(List<Integer> { })` | `null`, `null` |
| `Count(List<Integer> { })`, `exists List<Integer> { }` | `0`, `false` |
| `{ 1, 2 }[5]`, `{ 1, 2 }[-1]` | `null`, `null` |
| `{ }` | `[]` |

`EqualEvaluator.kt:262-268` at v5.4.0 returns null when either list is empty, before comparing.

## 40. Guarding `singleton from`

`testWaSingletonGuard` (both runs identical).

| Expression | Output |
| --- | --- |
| `if Count("Many") = 1 then singleton from "Many" else null`, `"Many"` = `{ 1, 2 }` | `null` (no error) |
| the same with `"One"` = `{ 7 }` | `7` |

**Settles:** the `then` branch is not evaluated when the condition is false, so the guard avoids the
run-time error of §34.

## 41. Testing a tuple element instead of the tuple

`testWaTupleElementTest` (both runs identical).

| Expression | Output |
| --- | --- |
| `Tuple { v: null as Integer } is Tuple { v Integer }` (the gotcha, §8) | `false` |
| `T.v is null or T.v is Integer` for the same tuple | `true` |

## 42. Guarding a computed half-open interval

`testWaIntervalGuard` (both runs identical), with `"A"` = `"B"` = `1`.

| Expression | Output |
| --- | --- |
| `if "A" < "B" then Interval["A", "B") else Interval["A", "B"]` | `[1, 1]` |
| `"AlsoFine": 2 + 2` in the same library | `4` (the library run completes) |

**Settles:** the guard avoids the run-time error of §18 and §21 when the bounds are equal.

## 43. Milliseconds against no milliseconds: workarounds

`testDtMsWorkaround` (both runs identical; no model).

| Expression | Output |
| --- | --- |
| `@2024-11-15T12:30:00.0Z = @2024-11-15T12:30:00.0Z` (control) | `true` |
| `@2024-11-15T12:30:00.0Z = @2024-11-15T12:30:00Z` (the gotcha, §22) | `null` |
| `@2024-11-15T12:30:00.0Z ~ @2024-11-15T12:30:00Z` | `false` |
| `@2024-11-15T12:30:00.0Z same second as @2024-11-15T12:30:00Z` | `true` |
| `@2024-11-15T12:30:00.5Z same second as @2024-11-15T12:30:00Z` | `true` |
| `@2024-11-15T12:30:00.0Z same minute as @2024-11-15T12:30:00Z` | `true` |
| `duration in milliseconds between @2024-11-15T12:30:00.0Z and @2024-11-15T12:30:00Z` | `[0, 999]` |

**Settles:** `same second as` compares through seconds and ignores milliseconds, so it decides
where `=` gives null, and it also treats `.5` as the same second as `:00`. The engine treats a value
without milliseconds as uncertain over 0 to 999 milliseconds.

## 44. Calendar-unit quantities in the same unit

`testDtUnitWorkaround` (both runs identical; no model).

| Expression | Output |
| --- | --- |
| `1 year = 12 months` (the gotcha, §25) | `null` |
| `12 months = 12 months` | `true` |
| `1 day = 24 hours` (the gotcha, §25) | `null` |
| `24 hours = 24 hours` | `true` |

**Settles:** written in one calendar unit, the comparison decides.

## Test-question probes: environment

Sections 45 to 52 ran on 2026-10-22, at offset `-04:00`, with no model. Every library ran twice with identical output.
A library expected to fail to compile is kept apart from its control.

## 45. A query over a single null source

`testTqNullSingletonSource`.

| Expression | Output |
| --- | --- |
| `(null as DateTime) X return if X is null then 1 else 2` | `null` |
| `(@2026-01-01T00:00:00Z) X return if X is null then 1 else 2` (control) | `2` |

**Settles:** the `return` clause is not evaluated over a null singleton source; the query is null.

## 46. Interval bound types

`testTqIntervalMixedString`, `testTqIntervalSameInteger`, `testTqIntervalMixedDate`,
`testTqIntervalMixedDateLocal`, `testTqIntervalMixedDateLater`. The ELM for
`Interval[@2026-01-01, @2026-01-02T00:00:00Z]` is an `Interval` of `DateTime`, with `ToDateTime`
over the Date low bound.

| Expression | Output |
| --- | --- |
| `Interval[1, 'a']` | compile error: `Low and high boundary values of an interval must be of the same type.` |
| `Interval[1, 2]` (control) | `[1, 2]` |
| `Interval[@2026-01-01, @2026-01-02T00:00:00Z]` | run-time error: `Invalid Interval - the ending boundary (@2026-01-02T00:00:00) must be greater than or equal to the starting boundary (@2026-01-01).` |
| `Interval[@2026-01-01, @2026-01-02T00:00:00-04:00]` (control: the evaluation offset) | `[2026-01-01, 2026-01-02T00:00:00]` |
| `Interval[@2026-01-01, @2026-01-05T00:00:00Z]` (control: a later day) | `[2026-01-01, 2026-01-05T00:00:00]` |
| `@2026-01-01 <= @2026-01-02T00:00:00Z` | `null` |

**Settles:** an Integer and a String bound do not compile. A Date and a DateTime bound compile,
with the Date converted. The run-time error is offset-dependent: at `-04:00`, `…T00:00:00Z` is
20:00 on 1 January, the day matches and the hour is unknown on the Date side, so `low <= high` is
null, and the engine treats a null bound comparison as invalid.

## 47. Type tests and boundaries of intervals with null bounds

`testTqIntervalNullBoundIs`. The ELM for `Interval[1, null]` has `As Integer` over `Null` on the
high bound and result type `Interval<Integer>`.

| Expression | Output |
| --- | --- |
| `Interval[1, 5] is Interval<Integer>` (control) | `true` |
| `Interval[1, null] is Interval<Integer>` | `false` |
| `Interval[1, null) is Interval<Integer>` | `false` |
| `Interval[null as Integer, null as Integer] is Interval<Integer>` | `false` |
| `start of Interval(null as Integer, null as Integer)` | `null` |
| `end of Interval(null as Integer, null as Integer)` | `null` |

**Settles:** on engine 5.4.0 an interval with any null bound fails an `Interval<Integer>` type
test.

## 48. A closed null end

`testTqClosedNullEnd`.

| Expression | Output |
| --- | --- |
| `end of Interval[@2025-12-31T00:00:00Z, null]` | `9999-12-31T23:59:59.999+00:00` |
| `Interval[@2025-12-31T00:00:00Z, null] overlaps Interval[@2026-01-01T00:00:00Z, @2026-12-31T00:00:00Z]` | `true` |
| `Interval[@2026-03-01T00:00:00Z, null] during Interval[@2026-01-01T00:00:00Z, @2026-12-31T00:00:00Z]` | `false` |
| `Interval[@2026-03-01T00:00:00Z, @2026-04-01T00:00:00Z] during …` (control) | `true` |
| `Interval[@2026-03-01T00:00:00Z, null) during …` | `null` |

**Settles:** a closed null end is the maximum DateTime, so `during` a bounded interval is false;
an open null end is unknown, so it is null.

## 49. Same-day durations and a descending interval

`testTqSameDayDays`, `testTqDescendingInterval`, `testTqAscendingInterval`.

| Expression | Output |
| --- | --- |
| `days between @2026-01-01T15:00:00Z and @2026-01-01T19:00:00Z` | `0` |
| `days between @2026-01-01T15:00:00Z and @2026-01-02T19:00:00Z` (control) | `1` |
| `difference in days between @2026-01-01T15:00:00Z and @2026-01-01T19:00:00Z` | `0` |
| `Interval[1, 0]` | run-time error: `Invalid Interval - the ending boundary (0) must be greater than or equal to the starting boundary (1).` |
| `Interval[0, 1]` (control) | `[0, 1]` |

**Settles:** a same-day duration in days is 0, so an interval built as `Interval[1, days]` is
descending for stays under a day.

## 50. An `Any` overload against a `Choice` overload

`testTqAnyVsChoiceOverload`, `testTqAnyOnlyOverload`.

| Overloads | Call | Output |
| --- | --- | --- |
| `f(x Any)`, `f(x Choice<Integer, String>)` | `f(5)` | `choice` |
| `f(x Any)` only (control) | `f(5)` | `any` |

**Settles:** translator 5.4.0 prefers the Choice overload for an Integer argument.

## 51. `as` to a type outside the choice

`testTqAsNonComponent`, `testTqAsComponent`.

| Expression (`v` is `Choice<Integer, String>`) | Output |
| --- | --- |
| `v as Decimal` | compile error: `Expression of type 'choice<System.Integer,System.String>' cannot be cast as a value of type 'System.Decimal'.` |
| `v as Integer`, `v` holding `1` (control) | `1` |
| `v as Integer`, `v` holding `'a'` | `null` |

**Settles:** the translator rejects `as` to a type that is not a component; the error is a compile
error ("loaded, but had errors"), not a run-time one.

## 52. Workarounds for the interval type test and a cast outside the choice

`testTqWaIntervalLow`, `testTqWaAsThenConvert` (both runs identical; no model).

| Expression | Output |
| --- | --- |
| `Interval[1, null] is Interval<Integer>` (the gotcha, §47) | `false` |
| `Interval[1, null].low is Integer` | `true` |
| `Interval[1, null).low is Integer` | `true` |
| `ToDecimal(v as Integer)`, `v` a `Choice<Integer, String>` holding `1` | `1` (a Decimal, printed as `1`) |
| the same, holding `'a'` | `null` |

**Settles:** testing the bound that is present decides where the interval type test does not; a
cast to a component followed by a conversion compiles where `v as Decimal` does not (§51).

## Held-out follow-up probes: environment

Sections 53 to 59 re-run, with added controls, cases that a held-out question round left to "would
probe". They ran on 2026-10-22, at offset `-04:00`, with no model. Every library ran twice with
identical output.

## 53. `Combine` with null elements and a null separator

`testHoCombine`, `testHoCombineWa`.

| Expression | Output |
| --- | --- |
| `Combine({ 'a', 'b' }, '-')` (control) | `a-b` |
| `Combine({ 'a', 'b' })` (control) | `ab` |
| `Combine({ 'a', null, 'b' }, '-')` | `null` |
| `Combine({ 'a', null, 'b' })` | `null` |
| `Combine({ 'a', 'b' }, null as String)` | `null` |
| `Combine({ 'a', null, 'b' }, null)` | `null` |
| `Combine((L) X where X is not null, Coalesce(Sep, ''))`, `L` = `{ 'a', null, 'b' }`, `Sep` null | `ab` |
| `Combine((L) X where X is not null, Coalesce('-', ''))` | `a-b` |
| `Combine(L, '-')` (the gotcha, same `L`) | `null` |

Source at v5.4.0: `CombineEvaluator.kt:20-34` returns null for a null separator and for any null
element.

**Settles:** engine 5.4.0 returns null where 1.5.3 says nulls are ignored; filtering the nulls and
coalescing the separator gives the 1.5.3 result.

## 54. Months at the end of a month

`testHoMonths`.

| Expression | Output |
| --- | --- |
| `months between @2026-01-31 and @2026-02-28` | `0` |
| `difference in months between @2026-01-31 and @2026-02-28` | `1` |
| `months between @2026-01-15 and @2026-02-15` (control) | `1` |
| `difference in months between @2026-01-15 and @2026-02-15` (control) | `1` |
| `months between @2026-01-31 and @2026-03-01` | `1` |

**Settles:** the engine follows the 1.5.3 month definition (a month from 31 January ends on
1 March), not the 2.0.0 one (the last day of February).

## 55. Touching intervals

`testHoIntervalTouch`.

| Expression | Output |
| --- | --- |
| `Interval[1, 5] overlaps Interval[5, 10]` | `true` |
| `Interval[1, 5) overlaps Interval[5, 10]` | `false` |
| `Interval[1, 5) meets Interval[5, 10]` | `true` |
| `Interval[1, 5] meets Interval[5, 10]` | `false` |
| `Interval[1, 4] meets Interval[5, 10]` (control) | `true` |

**Settles:** as specified; `meets` and `overlaps` read bounds through `start of` and `end of`.

## 56. A list of an Integer and a Decimal

`testHoMixedList`.

| Expression | Output |
| --- | --- |
| `{ 1, 2.0 }` | `[1, 2.0]` |
| `First({ 1, 2.0 }) is Integer` | `false` |
| `First({ 1, 2.0 }) is Decimal` | `true` |
| `First({ 1, 2 }) is Integer` (control) | `true` |

**Settles:** the Integer element is converted to Decimal (§9); the language server prints it as `1`.

## 57. Union with nulls, and `Count`

`testHoUnionNulls`.

| Expression | Output |
| --- | --- |
| `{ null as Integer, 1 } union { null as Integer }` | `[null, 1]` |
| `Count({ null as Integer, 1 } union { null as Integer })` | `1` |
| `Count({ 1 } union { 2 })` (control) | `2` |

**Settles:** as specified: the nulls are one element in the union, and `Count` skips it.

## 58. `Substring` at the end of the string

`testHoSubstring`.

| Expression | Output |
| --- | --- |
| `Substring('abc', 0)` (control) | `abc` |
| `Substring('abc', 2)` | `c` |
| `Substring('abc', 3)` | `null` |
| `Substring('abc', 5)` | `null` |

**Settles:** the engine treats a start index equal to the length as out of range.

## 59. A Date against a DateTime at midnight

`testHoDateDateTime`.

| Expression | Output |
| --- | --- |
| `@2026-01-15 = @2026-01-15` (control) | `true` |
| `@2026-01-15T00:00:00.000-04:00 = @2026-01-15T00:00:00.000-04:00` (control) | `true` |
| `@2026-01-15 = @2026-01-15T00:00:00.000-04:00` | `null` |
| `@2026-01-15 same day as @2026-01-15T10:00:00.000-04:00` | `true` |

**Settles:** even at midnight in the evaluation offset, the converted Date has no time, so `=` is
null.

## 60. `is` and `as` against QI-Core profiles (QI-Core 6.0.0)

Run on 2026-10-23 with `using QICore version '6.0.0'`, the modelinfo bundled with translator 5.4.0,
with the user's approval for this model. Every library ran twice with identical output.
`ConditionProblemsHealthConcerns { id: 'c1' }` does not compile (`Target Mapping in instance
selectors not yet supported`), so the run-time cases build a FHIR `Condition` in a library that
uses both models.

`testQcIsElm` (ELM only):

| CQL (`c` declared `ConditionProblemsHealthConcerns`) | ELM |
| --- | --- |
| `c is ConditionEncounterDiagnosis` | `Is` with `isTypeSpecifier` `{http://hl7.org/fhir}Condition` |
| `c is ConditionProblemsHealthConcerns` | `Is` with `isTypeSpecifier` `{http://hl7.org/fhir}Condition` |
| the operand `c` | `operandTypeSpecifier` `{http://hl7.org/fhir}Condition` |

`testQcAsSibling`, against `testQcAsSelf`:

| CQL | Output |
| --- | --- |
| `c as ConditionEncounterDiagnosis` | compile error: `Expression of type 'QICore Condition Problems Health Concerns' cannot be cast as a value of type 'QICore Condition Encounter Diagnosis'.` |
| `c as ConditionProblemsHealthConcerns` (control) | compiles |

`testQcIsRuntime` (`using FHIR version '4.0.1'` and `using QICore version '6.0.0'`):

| Expression | Output |
| --- | --- |
| `FHIR.Condition { id: … }` (no `meta.profile`) `is QICore.ConditionProblemsHealthConcerns` | `true` |
| the same `is QICore.ConditionEncounterDiagnosis` | `true` |
| the same `is QICore.AllergyIntolerance` (control) | `false` |
| a `FHIR.Condition` with `meta.profile` set to the problems-list profile URL, `is QICore.ConditionProblemsHealthConcerns` | `true` |
| the same, `is QICore.ConditionEncounterDiagnosis` | `true` |

**Settles:** `is` against a QI-Core profile compiles to a test of the profile's FHIR `target` type,
so at run time it cannot tell sibling profiles apart and ignores `meta.profile`. `as` between
sibling profiles is rejected at compile time, while `is` between them compiles and is always true
for a Condition.

## 61. A category test as a profile discriminator, and what the profile retrieves carry

Run on 2026-10-23, QI-Core 6.0.0 for the retrieves; the category test uses `using FHIR` only. Every
library ran twice with identical output.

`testQcCategory`: `HasCategory(c, code)` is true when some `c.category` coding has that code. The
`FHIR.Condition` values are built with instance selectors.

| Condition built with | `HasCategory(…, 'problem-list-item')` | `HasCategory(…, 'encounter-diagnosis')` |
| --- | --- | --- |
| category `problem-list-item` | `true` | `false` |
| category `encounter-diagnosis` | `false` | `true` |
| no category (control) | `false` | `false` |
| both categories | `true` | `true` |

`testQcRetrieves` (ELM, and one run):

| Expression | Result |
| --- | --- |
| `[ConditionProblemsHealthConcerns]` | `Retrieve` of `fhir:Condition`, `templateId` `http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-condition-problems-health-concerns` |
| `[ConditionEncounterDiagnosis]` | `Retrieve` of `fhir:Condition`, `templateId` `…/qicore-condition-encounter-diagnosis` |
| `[Condition]` | compile error: `Could not resolve type name Condition.` (the define is a `Null` in the ELM) |

The `[Condition]` error fails the whole library run, so the two profile retrieves were read from the
ELM of the same file rather than run.

**Settles:** a category test separates the two kinds only when each Condition carries exactly one of
the categories; a Condition with both, or with neither, is a test on the data and not a profile
test. The retrieves carry the profile URL as `templateId`. Under QI-Core 6.0.0, `[Condition]` does
not compile (the modelinfo has no `QICore.Condition`).

## 62. The 7-day follow-up window

Run on 2026-10-23. Every library ran twice with identical output. `testMdWindowFhir` and
`testMdWindowQuoted` use `using FHIR version '4.0.1'` and `include FHIRHelpers version '4.0.1'`.

| Library | Expression | Output |
| --- | --- | --- |
| `testMdWindowOrig` | `Interval[start of Encounter.period, end of Encounter.period + 7 days]`, with `Encounter` the type name | compile error: `Could not resolve identifier Encounter in the current library.` |
| `testMdWindowSystemB` | `FollowUpWindow(P Interval<DateTime>)` = `Interval[start of P, end of P + 7 days]`, for `[2025-01-17T10:00Z, 2025-01-17T14:00Z]` | `[2025-01-17T10:00, 2025-01-24T14:00]` |
| | `@2025-01-20T14:00Z in` the window | `true` |
| | `@2025-01-24T14:00Z in` the window (the seventh day) | `true` |
| | `@2025-01-24T14:00:00.001Z in` the window | `false` |
| | `@2025-01-17T09:59:59.999Z in` the window (before the stay) | `false` |
| | `end of Stay + 7 days` | `2025-01-24T14:00` (`end of` binds before `+`) |
| `testMdWindowGrouped` | `end of (Stay + 7 days)` | compile error: `Could not resolve call to operator Add with signature (interval<System.DateTime>, System.Quantity).` |
| `testMdWindowFhir` | `FollowUpWindow(E FHIR.Encounter)` with `E.period` set from 10:00 to 14:00 | `[2025-01-17T10:00, 2025-01-24T14:00]` |
| `testMdWindowQuoted` | the same as a quoted function name, `"Follow-up Window"(Visit)` | `[2025-01-17T10:00, 2025-01-24T14:00]` |
| | `@2025-01-17T15:00Z during "Follow-up Window"(Visit)` | `true` |

**Settles:** a type name is not a value, so the unaliased form does not compile. The window is a
closed interval that includes the seventh day's end instant. A first version of
`testMdWindowSystem` also held the grouped form and failed as a whole; the grouped form is in its
own library, `testMdWindowGrouped`.
