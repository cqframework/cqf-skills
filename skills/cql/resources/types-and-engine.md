# Types, the Translator, and the Engine

Baseline: CQL 1.5.3. Untagged statements hold in 1.4, 1.5.3 and 2.0.0.
Sources: CQL-1.5.3, CQL-2.0.0, CQFW-5.4.0, PROBES-2026-10-22

How CQL's static type system relates to what the cqframework translator emits and its engine
executes: casting, overload resolution and `Choice`-typed arguments.

Source citations are to `clinical_quality_language` at tag `v5.4.0`, read with
`git show v5.4.0:<path>`. The files cited are unchanged at `fb8055df5` (v5.4.0 plus 4 commits). They
show what this implementation does, not what the spec requires.

That is one translator version. IG Publisher 3.0.1 compiles CQL with cqframework 3.29.0, and nothing
here was checked against it. When the published ELM is what counts, read that ELM, or compile
against the publisher's translator, rather than assume the 5.4.0 behaviour below.

## Consequences for authors

1. **`when X is T then …` does not narrow `X`** (translator behaviour; the spec is silent). Inside
   the branch, `X` keeps its declared type and every call in the branch is resolved against that
   declared type. The word "narrow" appears in no section of 1.4, 1.5.3 or 2.0.0; the cqframework
   translator parses `when` and `then` independently
   [src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/Cql2ElmVisitor.kt:2795-2798],
   and a probe confirms it [src: PROBES-2026-10-22 RESULTS.md §4]. This is the single most common
   author trap: the branch reads as if the guard constrained the value, and it does not.
2. **Cast explicitly when you need the narrower type.** To call a function declared on a narrower
   type, write the cast:

   ```cql
   (X as T).someFunction()
   ```

   Without it, resolution happens on the declared type.

## Overload resolution: static in the cqframework translator, not by spec rule

The spec does not require static resolution. ELM FunctionRef, `signature` (same in 1.4, 2.0): "If no
signature is specified, the run-time types of the operands should be used to resolve any overload."
[src: CQL-1.5.3 04-logicalspecification > Reusing Logic > FunctionRef] The cqframework translator
emits signatures by default (`signatureLevel = SignatureLevel.Overloads`)
[src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/CqlCompilerOptions.kt:37],
so its engine resolves statically; the engine also has a run-time fallback
[src: CQFW-5.4.0 engine/src/commonMain/kotlin/org/opencds/cqf/cql/engine/elm/executing/FunctionRefEvaluator.kt:131-133].

In the translator, applicability is decided from the argument's **declared** type.
`OperatorEntry.resolve` tries an exact match, sub-signatures and a supertype signature first
[src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/model/OperatorEntry.kt:84-110],
then `Signature.isConvertibleTo`: an operand fits when `argType.isSubTypeOf(paramType)` — or a
conversion exists
[src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/model/Signature.kt:50-55].
So for a plain (non-`Choice`) argument, full subtype conversion applies: a value of a subtype
reaches a function whose parameter is the supertype.

## Choice-type arguments: the sharp edge

A `ChoiceType` has `baseType = Any` and does not override `isSubTypeOf`, so
`choiceType.isSubTypeOf(param)` is false for every parameter type except `System.Any`, and the
argument falls through to the conversion machinery
[src: CQFW-5.4.0 cql/src/commonMain/kotlin/org/hl7/cql/model/ChoiceType.kt:15]
[src: CQFW-5.4.0 cql/src/commonMain/kotlin/org/hl7/cql/model/BaseDataType.kt:18]. There, two
predicates decide applicability — and both are subtype-blind:

- `ConversionMap.findCompatibleConversion` accepts the whole choice for `param` whenever
  `choiceType.isCompatibleWith(param)`, which for a class parameter means `param` **equals one of
  the components** (`ChoiceType.isCompatibleWith` asks `param.isCompatibleWith(component)`, and for
  class types that is equality). It returns a plain `Conversion.Cast`, so the call site becomes an
  unconditional `As param`
  [src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/model/ConversionMap.kt:94-95]
  [src: CQFW-5.4.0 cql/src/commonMain/kotlin/org/hl7/cql/model/ChoiceType.kt:41].
- `ConversionMap.findChoiceConversion` (the fallback for when the above fails) *does* iterate the
  components — but tests each with `findConversion`, which has no `isSubTypeOf` test of its own.
  Subtyping is applied one layer **up**, in `Signature.isConvertibleTo`, which this path never
  calls. So a component that is merely a subtype of the parameter does not qualify
  [src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/model/ConversionMap.kt:107-109].

**Net rule: a `Choice` argument fits only those parameter types that are *equal* to one of its
components — never a supertype of one.** If `B` is a subtype of `C`, then `Choice<A, B>` matches a
parameter of type `A` but not one of type `C`, even though its `B` component *is* a `C`
(translator behaviour, observed in [src: PROBES-2026-10-22 RESULTS.md §2]
[src: PROBES-2026-10-22 RESULTS.md §3]). The spec defines a cast from a choice to a component it
includes and is silent on a supertype of a component (same in 1.4)
[src: CQL-1.5.3 03-developersguide > Types > Conversion Precedence]; see
[type-system.md](type-system.md#choice-types).

Two consequences:

- Exactly one component equals the parameter → the call resolves to that overload and the translator
  emits an unconditional narrowing (`As A`), which is `null` at runtime for a value
  of the other component type. Silent.
- Two overloads, each equal to a *different* component → both are candidates, the scores tie, the
  type-precedence tie-break
  [src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/model/OperatorMap.kt:85-103]
  ties too for two class parameters, and an **ambiguity error** is raised
  [src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/model/OperatorMap.kt:106-117].
  Loud and safe. This matches the spec's rule that equal conversion counts are "an ambiguous
  resolution error" [src: CQL-1.5.3 03-developersguide > Libraries > Function Resolution].

The trigger for the silent case is specifically that the component is a *strict subtype* of the
parameter: had the choice listed the base type itself, the call would have resolved.

### Why making the components subtype-aware is not the fix

Fixing the component test alone changes nothing observable. Scoring
(`ConversionMap.getConversionScore`) gives the exact-component binding `Compatible` (2), because
`callOperand.isCompatibleWith(operand)` is true for a choice containing that component; the subtype
binding would score `ChoiceNarrowingCast` = `Cast` + the inner conversion (3 + 3 = 6)
[src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/model/ConversionMap.kt:26-27]
[src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/model/ConversionMap.kt:413]
[src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/model/Conversion.kt:58-59].
Selection takes the lowest score, breaks ties by type precedence, and raises an error only if that
ties too, so the exact-component overload still wins. The fix has to change **candidacy or scoring**
(the single call site of `isConvertibleTo` is `OperatorEntry.getConversions`
[src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/model/OperatorEntry.kt:161]),
e.g. reject a candidate whose parameter cannot accept every component of the choice, or report
reachability via different components as ambiguous.

### Repros (run)

Run on 2026-10-22 with `cql_execute` against translator 5.4.0, engine 5.4.0, through CQL language
server 4.11.0-SNAPSHOT [src: PROBES-2026-10-22 RESULTS.md §1] [src: PROBES-2026-10-22 RESULTS.md §2]
[src: PROBES-2026-10-22 RESULTS.md §3] [src: PROBES-2026-10-22 RESULTS.md §6]. Each was run twice,
with identical output. **Configuration:** the language server compiles with `signatureLevel="All"`
and `DisableListPromotion,DisableListDemotion`, not the translator defaults
(`signatureLevel = Overloads`), so every call in the ELM carried a signature. None of the cases
depend on list promotion.

**System types, no model.** One overload equal to a component binds silently:

```cql
define fluent function f(x Integer): if x is null then 'null-int' else 'int'

define function g(v Choice<Integer, String>): v.f()

define "Int": g(1)     // 'int'
define "Str": g('a')   // 'null-int': the String became null
```

The ELM for `v.f()` is `<signature name="t:Integer"/>` over `<operand asType="t:Integer"
xsi:type="As">`, with no `strict`, and the translator reports no diagnostic. Add
`define fluent function f(x String): 'string'` and the call fails instead: `Call to operator
f(choice<System.Integer,System.String>) is ambiguous with: - f(System.String) - f(System.Integer)`.

Two more System-type cases with the same `g`:

- `f(x Decimal)` alone: the ELM is `ToDecimal` over `As Integer`, with no `Case` over the
  alternatives. `g(1)` gives `'dec'`; `g('a')` reaches `f` as `null`.
- `k(x Any)` with `g(v Choice<Integer, String>): k(v)`: passes the operand with no `As`.

**FHIR, run time.** A supertype that accepts every component is not a candidate; an overload equal
to one component wins silently:

```cql
using FHIR version '4.0.1'

define fluent function f(x FHIR.AllergyIntolerance): if x is null then 'null-allergy' else 'allergy'
define fluent function f(x FHIR.DomainResource): 'domain'

define function g(event Choice<FHIR.Condition, FHIR.AllergyIntolerance>): event.f()

define "Cond": g(Condition { id: id { value: 'c1' } })              // 'null-allergy'
define "Allergy": g(AllergyIntolerance { id: id { value: 'a1' } })  // 'allergy'
define "BareCond": (Condition { id: id { value: 'c2' } }).f()        // 'domain'
```

The same kind of Condition value reaches `f(DomainResource)` directly, but reaches
`f(AllergyIntolerance)` as `null` through the choice. With only `f(x FHIR.DomainResource)`, the call
fails: `Could not resolve call to operator f with signature
(choice<FHIR.AllergyIntolerance,FHIR.Condition>).` Two overloads that each equal a different
component (`f(FHIR.Condition)` and `f(FHIR.AllergyIntolerance)`) give the ambiguity error, fluent or
not.

`ChoiceType.flattenChoices()` sorts the components by `toString()`, so component order — and any
notion of a "first member" — is never meaningful
[src: CQFW-5.4.0 cql/src/commonMain/kotlin/org/hl7/cql/model/ChoiceType.kt:93-95]. The probes show
it: `Choice<FHIR.Condition, FHIR.AllergyIntolerance>` is serialised and reported as
`choice<FHIR.AllergyIntolerance,FHIR.Condition>`.

### An `Any` overload against a `Choice` overload

The spec places `f(x Any)` for an Integer argument: "All other types derive from System.Any" (same
in 1.4, 2.0) [src: CQL-1.5.3 03-developersguide > Types > System-Defined Types], so it matches by
"Subtype – If the invocation type is a subtype of the declared type of the argument" (precedence 2;
same in 1.4) [src: CQL-1.5.3 03-developersguide > Types > Conversion Precedence]. It does not place
`f(x Choice<Integer, String>)`: Cast (4) runs from a choice to a component, the other way. (1.5+)
"Choice types are compatible if the choices of one type are a subset of the choices of the other"
speaks of two choice types; reading a plain type as a one-element choice is not stated.

#### Gotcha: a `Choice` overload beats an `Any` overload

- **Symptom:** with `f(x Any)` and `f(x Choice<Integer, String>)`, `f(5)` calls the Choice one.
- **Probe:** `testTqAnyVsChoiceOverload`, against `testTqAnyOnlyOverload` (only `f(x Any)`), which
  gives `'any'` [src: PROBES-2026-10-22 RESULTS.md §50].
- **Spec:** does not decide for the Choice overload (above); the text supports `f(x Any)`, or no
  ranking.
- **Well-formed?** Yes.
- **Layer:** translator.
- **Evidence:** the result `'choice'`; the scoring described under
  [Why making the components subtype-aware is not the fix](#why-making-the-components-subtype-aware-is-not-the-fix).
- **Workaround:** don't overload one name on `Any` and on a `Choice`; give the functions different
  names. (2.0+) The spec discourages a similar pair, `Foo(Integer)` with
  `Foo(Choice<Integer, Decimal>)` [src: CQL-2.0.0 03-developersguide > Types > Choice Types].
- **Affects:** translator 5.4.0.

## Authoring rules that follow

- Cast before calling a base-typed function on a `Choice` argument.
- Never rely on `when X is T` (or `if X is T`) for narrowing.
- When a call on a `Choice` silently binds to one branch and the other branch returns null, suspect
  this mechanism **before** suspecting the engine — the engine is doing exactly what the ELM says.

## Where the machinery lives

Paths are relative to the `clinical_quality_language` checkout root at tag `v5.4.0` (5.1.0 moved
the modules to the top level; 5.0.x and older tags prefix them with `Src/java/`).

- **Type system** — `cql/src/commonMain/kotlin/org/hl7/cql/model/`:
  `BaseDataType.kt` (the `isSubTypeOf`/`isCompatibleWith` definitions), `ClassType.kt`,
  `ChoiceType.kt` (`isCompatibleWith`, `flattenChoices`), `ProfileType.kt` (used only for
  QDM-style `ProfileInfo`), `DataType.kt`.
- **Applicability** — `cql-to-elm/…/cql2elm/model/Signature.kt` (`isConvertibleTo`; the one
  `isSubTypeOf` short-circuit) and `OperatorEntry.kt` (`getConversions`, the sole call site).
- **Conversions** — `cql-to-elm/…/cql2elm/model/ConversionMap.kt` (`findConversion`,
  `findCompatibleConversion`, `findChoiceConversion`, `findTargetChoiceConversion`,
  `getConversionScore`) and `Conversion.kt` (`Conversion.Cast`, `Conversion.ChoiceNarrowingCast`).
- **Selection** — `cql-to-elm/…/cql2elm/model/OperatorMap.kt` (`resolveOperator`; lowest score wins,
  then type precedence breaks ties, a remaining tie is an error) and `LibraryBuilder.kt`
  (`convertExpression`, which turns a `Conversion.Cast` into `As`
  [src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/LibraryBuilder.kt:2039-2050]).
  `lowestScoringInvocation` in `LibraryBuilder.kt` is used only for
  `includes`/`contains`/`in`/`included in`, not for function selection
  [src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/LibraryBuilder.kt:1145].
- `Conversion.ChoiceNarrowingCast` exists to narrow a choice across a *convertible* component: it
  records which component matched and can emit a `Case` over the alternatives. An *equal* component
  never needs it, because `findCompatibleConversion` answers first with a bare `Cast`
  [src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/model/ConversionMap.kt:114]
  [src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/LibraryBuilder.kt:2055-2078].

## Open question

Whether `Choice<…>` → *supertype of a component* is a valid implicit conversion is unresolved. The
Developer's Guide (Choice Types; Conversion Precedence, item 4 "Cast") describes converting a choice
to **its components**; the spec is silent on whether a component's supertypes qualify either as a
target or as a candidate (same in 1.4; **2.0:** adds only a note discouraging overloads such as
`Foo(Integer)` alongside `Foo(Choice<Integer, Decimal>)`)
[src: CQL-1.5.3 03-developersguide > Types > Choice Types]
[src: CQL-1.5.3 03-developersguide > Types > Conversion Precedence]
[src: CQL-2.0.0 03-developersguide > Types > Choice Types]. The deeper open question is what the
translator *should* do when one candidate is reachable only by narrowing to a single component: an
error, or a runtime dispatch. The spec has relevant text on both: ELM FunctionRef allows run-time
resolution when no signature is given (see above), and the Developer's Guide Function Resolution
says "If multiple signatures have the same number of required conversions, an ambiguous resolution
error is thrown" [src: CQL-1.5.3 03-developersguide > Libraries > Function Resolution]. Note the
current behaviour is silent either way; the observed behavior above holds regardless of how that
policy question is settled.

