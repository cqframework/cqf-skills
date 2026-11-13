# CQL Type System

Baseline: CQL 1.5.3. Untagged statements hold in 1.4, 1.5.3 and 2.0.0.
Sources: CQL-1.4, CQL-1.5.3, CQL-2.0.0, CQL-TESTS, CQFW-5.4.0, PROBES-2026-10-22, CQLWIKI

Type testing, casting, choice types, conversion precedence, implicit and explicit conversion,
tuples, and list, set-operator and conditional typing. Source IDs are defined in
[SOURCES.md](SOURCES.md). How the cqframework translator resolves overloads for `Choice`
arguments is in [types-and-engine.md](types-and-engine.md); this file covers what the spec says
about the types themselves, and what that translator and engine were observed to do.

The spec text below is the rule. Blocks marked **Gotcha** record where translator or engine 5.4.0
departs from it, fills a gap in it, or depends on a setting, each with a workaround; see
[diagnosing.md](diagnosing.md) for how the layer was decided.

Observed behaviour below comes from translator and engine 5.4.0 through a language server that
compiles with `signatureLevel="All"` and list promotion and demotion disabled
[src: PROBES-2026-10-22 RESULTS.md §1].

## Type testing: `is`

The CQL Reference defines `is` against the run-time type, including derived types (same in 2.0)
[src: CQL-1.5.3 09-b-cqlreference > Type Operators > Is]:

> "If the run-time type of the argument is the same as or derived from the type being tested, the
> result of the operator is true; otherwise, the result is false."

**1.4:** "If the run-time type of the argument is of the type being tested, the result of the
operator is true; otherwise, the result is false."
[src: CQL-1.4 09-b-cqlreference > Type Operators > Is] The ELM `Is` definition keeps that 1.4
wording in all three versions ("If the run-time type of the argument is of the type being tested")
[src: CQL-1.5.3 04-logicalspecification > Type Operators > Is].

Subtyping is defined in the Developer's Guide (same in 1.4, 2.0; 1.4 differs in markup only)
[src: CQL-1.5.3 03-developersguide > Types > Type Testing]:

- For a type T' derived from T, two definitions hold: identity ("T is T") and subtype ("T' is T").
- `Interval<P'>` is a subtype of `Interval<P>`, and `List<E'>` of `List<E>`, when `P'` and `E'`
  derive from `P` and `E`.
- A tuple type T' is a subtype of T "if and only if" the element counts are equal and "For each
  element in T, there is one element in T' with the same name, and the type of the matching element
  in T' is a subtype of the type of the element in T."

### `null` and `is`

**2.0:** "the expression null is Integer returns false. Similarly, because as is strictly a
compile-time consideration (i.e. treat this value as a value of this type), the expression (null as
Integer) is Integer is equivalent to null is Integer and also returns flase." (sic)
[src: CQL-2.0.0 09-b-cqlreference > Type Operators > Is]
1.4 and 1.5.3 are silent on `null is T`: neither their `Is` entries nor Type Testing mention null.
For a 1.5 engine the accurate finding is: 1.5.3 is silent, and 2.0.0 clarifies that it is false.

Observed: `null is Integer` and `(null as Integer) is Integer` both return `false`
[src: PROBES-2026-10-22 RESULTS.md §7].

### Tuples with a null element

The spec is silent on whether a tuple with a null element passes a tuple type test. Searched:
Type Testing, Type Operators > Is (CQL Reference and ELM) and Structured Values > Tuple, in 1.4,
1.5.3 and 2.0.0. The tuple subtyping rule above is stated over element *types*, and no text gives
the run-time type of a tuple value whose element is null.

#### Gotcha: a tuple with a null element fails a tuple type test

- **Symptom:** `Tuple { v: null } is Tuple { v Integer }` and
  `Tuple { v: null as Integer } is Tuple { v Integer }` both return `false`.
- **Probe:** `testTsTupleIs`, against the control `Tuple { v: 1 } is Tuple { v Integer }`, which
  returns `true` [src: PROBES-2026-10-22 RESULTS.md §8].
- **Spec:** silent (sections searched above).
- **Well-formed?** Yes.
- **Layer:** spec gap; the engine's choice fills it.
- **Evidence:** no text gives the run-time type of a tuple whose element is null.
- **Workaround:** test the element, not the tuple: `T.v is null or T.v is Integer` is `true` for
  the same tuple [src: PROBES-2026-10-22 RESULTS.md §41].
- **Affects:** engine 5.4.0.

That run-time failure matters when a set operator casts a list: see
[A typed null element can drop a whole operand](#a-typed-null-element-can-drop-a-whole-operand).

### Conformance tests

`IntegerIsInteger` (`5 is Integer` → `true`) and `StringIsInteger` (`'5' is Integer` → `false`)
[src: CQL-TESTS CqlTypeOperatorsTest.xml IntegerIsInteger]
[src: CQL-TESTS CqlTypeOperatorsTest.xml StringIsInteger]. No test covers `null is T`, tuple type
tests or choice types.

## Casting: `as` and `cast`

`as` treats a value as a more specific type and gives `null` on a mismatch; `cast` throws
(same in 1.4, 2.0) [src: CQL-1.5.3 09-b-cqlreference > Type Operators > As]. The 1.4 text differs in
example quoting only:

> "If the argument is not of the specified type at run-time the result is null. The cast prefix
> indicates that if the argument is not of the specified type at run-time then an exception is
> thrown."

The Developer's Guide says the same: "Casting is the operation of treating a value of some base
type as a more specific type at run-time." and "If the run-time type of the value is not of the
type specified in the as operator, the result is null." (same in 1.4, 2.0)
[src: CQL-1.5.3 03-developersguide > Types > Casting]. In ELM both are `As`, with `strict` true for
`cast`: "If the argument is not of the specified type, and the strict attribute is false (the
default), the result is null." [src: CQL-1.5.3 04-logicalspecification > Type Operators > As]

**2.0:** the `Is` entry calls `as` "strictly a compile-time consideration (i.e. treat this value as
a value of this type)" [src: CQL-2.0.0 09-b-cqlreference > Type Operators > Is]. The 2.0.0 `As` and
Casting sections still describe a run-time check. Report both texts if a question turns on it.

The spec is silent on narrowing: no section of 1.4, 1.5.3 or 2.0.0 says that `X is T` changes the
static type of `X` in a following branch. The translator does not narrow; see
[types-and-engine.md](types-and-engine.md).

Observed (translator and engine behaviour) [src: PROBES-2026-10-22 RESULTS.md §12]:

| CQL | ELM | Result |
| --- | --- | --- |
| `v as Integer`, `v` a `Choice<Integer, String>` holding `'a'` | `As` | `null` |
| `cast v as Integer`, same value | `As` with `strict="true"` | run-time error: `Cannot cast 'a' to …` |
| either, holding `1` (controls) | as above | `1` |

`as` to a type outside a choice: the spec does not say whether `v as Decimal`, with `v` a
`Choice<Integer, String>`, is a compile error; Casting speaks of treating a value "as a more
specific type", which Decimal is not. Translator 5.4.0 rejects it at compile time: `Expression of
type 'choice<System.Integer,System.String>' cannot be cast as a value of type 'System.Decimal'.`
(translator behaviour; `v as Integer` gives `1` and `null` as expected)
[src: PROBES-2026-10-22 RESULTS.md §51]. Use a component type, then convert: `ToDecimal(v as
Integer)` gives a Decimal, or `null` for `'a'` [src: PROBES-2026-10-22 RESULTS.md §52].

Conformance tests: `AsQuantity`, `CastAsQuantity`, `AsDateTime` cover the matching case only
[src: CQL-TESTS CqlTypeOperatorsTest.xml AsQuantity]
[src: CQL-TESTS CqlTypeOperatorsTest.xml CastAsQuantity]. No test covers a mismatch.

### Implicit casting of `null`

"CQL also supports the notion of implicit casting to prevent the need to cast a null literal to a
specific type." For `5 * null`, "CQL implicitly casts the Any to Integer." (same in 1.4, 2.0; 2.0
fixes a typo) [src: CQL-1.5.3 03-developersguide > Types > Casting > Implicit Casting]
"The type of the null selector is Any." (same in 1.4, 2.0)
[src: CQL-1.5.3 03-developersguide > Types > Type Inference > Literals and Selectors]

Observed: `5 * null` compiles to `Multiply(5, As(Null))` and returns `null`
[src: PROBES-2026-10-22 RESULTS.md §12].

## Choice types

A choice type is a compile-time construct
[src: CQL-1.5.3 05-languagesemantics > Expression Language Semantics > Data Model > Choice Types]:

> "A given value at run-time will always be of a specific type, so a choice type is only a
> compile-time construct that allows for data models that contain elements with multiple possible
> types, or for the results of expressions where the result may be any of a possible set of types
> (e.g. a union of different types)."

Use of a choice value, from the Developer's Guide (**2.0:** adds the overload note below)
[src: CQL-1.5.3 03-developersguide > Types > Choice Types]:

- "An expression of a choice type can be used anywhere that a value of any of its component types
  is expected, and an implicit cast will be used to restrict the choice type to the correct
  component type."
- "The semantics for casting will result in a null if the run-time value of the element is not of
  the appropriate type."
- "For union, this means that the inputs can be lists of different types of elements, and the type
  of the result is now a choice type with components of each of the input types."
- "For intersect, this means the inputs can be lists of different types of elements, and the type
  of the result is a choice with only the types that are common between the input types."
- "For except, … the result will be the same type as the left input."

**2.0:** for overloads `Foo(t Integer)` and `Foo(t Choice<Integer, Decimal>)`, "Doing so results in
a potentially ambiguous overload and should be discouraged." and "Implementations should provide a
warning when this type of overload is detected."
[src: CQL-2.0.0 03-developersguide > Types > Choice Types]

The spec is silent on:

- a conversion from `Choice<A, B>` to a supertype of a component that is not itself a component;
- run-time dispatch over a choice's components (the only run-time resolution text is ELM
  FunctionRef, "If no signature is specified, the run-time types of the operands should be used to
  resolve any overload." (same in 1.4, 2.0)
  [src: CQL-1.5.3 04-logicalspecification > Reusing Logic > FunctionRef]);
- the result type of `intersect` when the inputs share no type.

How the translator binds a `Choice` argument to overloads (exact components only, silent `As`,
ambiguity errors) is translator behaviour, with run probes, in
[types-and-engine.md](types-and-engine.md).

### Set operators: observed typing

Translator behaviour [src: PROBES-2026-10-22 RESULTS.md §10]. When the operands' element types
differ, the translator types `union`, `intersect` **and** `except` as a list of a Choice, wraps
each operand in `As`, and does not apply implicit conversions to the elements:

| CQL | ELM result type | Result |
| --- | --- | --- |
| `{ 1 } union { 'a' }` | `List<Choice<Integer, String>>` | `[1, a]` (as printed) |
| `{ 1 } intersect { 'a' }` | `List<Choice<Integer, String>>` | `[]` |
| `{ 1 } except { 'a' }` | `List<Choice<Integer, String>>` | `[1]` |
| `{ 1.0 } union { 1 }` | `List<Choice<Decimal, Integer>>` | `[1.0, 1]` |
| `{ 1 } intersect { 1.0 }` | `List<Choice<Decimal, Integer>>` | `[]` |
| `{ 1, 2 } except { 1.0 }` | `List<Choice<Decimal, Integer>>` | `[1, 2]` |
| `{ 1 } union { 2 }` (control) | `List<Integer>` | `[1, 2]` |

Compared with the Developer's Guide text above, the `intersect` and `except` result types differ
from what it describes ("only the types that are common"; "the same type as the left input"). The
spec is silent on whether an implicit conversion such as Integer to Decimal applies to the elements
of the list operands of `union`, `intersect` and `except`. (The list-selector rule under
[List selectors](#list-selectors) covers conversion between elements inside one selector only.)
Searched: Choice Types, Implicit Conversions, Conversion Precedence and the List Operators entries
for Union, Intersect and Except, in all three versions.

#### Gotcha: set operators don't convert element types

- **Symptom:** `1 = 1.0`, `1 in { 1.0 }` and `{ 1 } = { 1.0 }` are all `true`, because the
  translator inserts `ToDecimal` (for the list comparison, inside a query over the elements). But
  `{ 1 } intersect { 1.0 }` is empty and `{ 1.0 } union { 1 }` keeps both values.
- **Probe:** the table above, against the control `{ 1 } union { 2 }`
  [src: PROBES-2026-10-22 RESULTS.md §10].
- **Spec:** silent on converting the elements of set-operator operands (searched above). The
  `intersect` and `except` result types also differ from the Developer's Guide description.
- **Well-formed?** Yes.
- **Layer:** spec gap for the element conversion; translator for the `intersect` and `except`
  result types.
- **Evidence:** the ELM wraps each operand in `As` to a list of a Choice, with no `ToDecimal`.
- **Workaround:** normalise element types before the set operation. Both of these give `[1]`, typed
  `List<Decimal>` [src: PROBES-2026-10-22 RESULTS.md §13]:

  ```cql
  List<Decimal> { 1 } intersect { 1.0 }
  (({ 1 }) X return ToDecimal(X)) intersect { 1.0 }  // the list selector needs parentheses
  ```

- **Affects:** translator 5.4.0.

Authoring idiom (guide text, not spec): when the intent is *the subject has a related X*, relate
the lists with `with … such that` or `exists (…)` instead of unioning lists of different types. A
2017 answer about a union of encounters and other event types puts it as: "What needs to happen is
these need to be related to the encounter, most likely using a with clause"
[src: CQLWIKI QA-Trying-to-Union-Different-Types.md]. Its examples use QDM.

### A typed null element can drop a whole operand

Observed, translator typing combined with engine behaviour [src: PROBES-2026-10-22 RESULTS.md §14].
Each branch below is a list of two tuples `Tuple { d: <DateTime>, v: … }`, unioned with
`{ Tuple { d: <DateTime>, v: 1.5 } }`:

| Second tuple in the first branch | First branch type | Union | `Count` |
| --- | --- | --- | --- |
| `v: 2` (control) | `List<Tuple{d DateTime, v Integer}>` | `As` on both operands, list of a Choice | `3` |
| `v: null as Integer` | `List<Tuple{d DateTime, v Integer}>` | `As` on both operands, list of a Choice | `1` |
| `v: null` | `List<Tuple{d DateTime, v Any}>` | no `As`: `Tuple{… v Any}` is a supertype | `3` |

#### Gotcha: a typed null tuple element drops the whole union operand

- **Symptom:** with the typed null, both Integer tuples are lost, including the one with `v: 1`. No
  diagnostic is reported. An untyped null hides the problem, because it widens the element type to
  `Any` and no cast is applied.
- **Probe:** `testTsUnionNullElem`, the table above, against `v: 2`
  [src: PROBES-2026-10-22 RESULTS.md §14].
- **Spec:** silent on both the null-element type test and the element conversion.
- **Well-formed?** Yes.
- **Layer:** spec gap, where translator typing and engine type testing combine: the `As` over the
  whole list operand fails at run time, because a tuple with a null element fails the type test (see
  [Tuples with a null element](#tuples-with-a-null-element)), and the operand contributes nothing.
- **Evidence:** the ELM `As` on both operands; the §8 type test.
- **Workaround:** normalise the tuple type before the union:
  `(L X return Tuple { d: X.d, v: ToDecimal(X.v) }) union R` gives all three tuples
  [src: PROBES-2026-10-22 RESULTS.md §33].
- **Affects:** translator and engine 5.4.0.

## Conversion precedence

When an invocation could resolve to more than one overload, "the following precedence is applied"
(same in 1.4, 2.0) [src: CQL-1.5.3 03-developersguide > Types > Conversion Precedence]:

1. Exact match
2. Subtype
3. Compatible ("e.g., the invocation type is Any")
4. Cast ("e.g., the invocation type is a choice that includes the declared type")
5. Implicit Conversion To Simple Type
6. Implicit Conversion To Class Type
7. Interval Promotion
8. List Demotion
9. Interval Demotion
10. List Promotion

"When determining a conversion path from an invocation signature to a declared signature, the
least converting overall conversion path is used." The ambiguity rule is in Function Resolution:
"If multiple signatures have the same number of required conversions, an ambiguous resolution error
is thrown, and the author must provide an explicit cast or conversion to resolve the ambiguity."
[src: CQL-1.5.3 03-developersguide > Libraries > Function Resolution]

**1.4:** the Conversion Precedence section ends after the list
[src: CQL-1.4 03-developersguide > Types > Conversion Precedence]. Version 1.5.3 adds:

- "Class and tuple types are compatible if the elements of one type are a subset of the elements of
  the other, by name. Choice types are compatible if the choices of one type are a subset of the
  choices of the other."
- A type precedence for overloads that differ by type category, in the order simple types, tuples,
  classes, intervals, lists, choices. Its example is `Interval[1, null] properly includes null`,
  where "the point overload is chosen".

Observed: `Interval[1, null] properly includes null` compiles to `ProperContains` (the point
overload) and returns `null` [src: PROBES-2026-10-22 RESULTS.md §12]. Translator behaviour: the
translator scores a choice-to-component match as Compatible (2) rather than Cast, then breaks score
ties by type precedence
[src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/model/ConversionMap.kt:26-27]
[src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/model/ConversionMap.kt:413]
[src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/model/OperatorMap.kt:85-117].

## Implicit and explicit conversion

**Implicit conversions.** Table 3-J lists the implicit conversions
[src: CQL-1.5.3 03-developersguide > Types > Conversion > Implicit Conversions]:

| From | Implicitly to |
| --- | --- |
| Integer | Long (1.5+), Decimal, Quantity |
| Long (1.5+) | Decimal, Quantity |
| Decimal | Quantity |
| Date | DateTime |
| Code | Concept |
| ValueSet (1.5+) | List<Code> |

Also: "CQL defines implicit conversion of a named structured type to its equivalent tuple type",
but "the opposite implicit conversion, from a tuple to a named structured type, does not occur";
`convert` can do it, and "requires that the set of elements in the tuple type be the same set or a
subset of the elements in the structured type." And: "specific data models may introduce
conversions, including implicit conversions." Model conversions (for example from model primitives
to System types) come from the model, not from this table.

Example: in `1 * 1.0` "the language will implicitly convert the type of the 1 to Decimal by
inserting a ToDecimal invocation". Observed: `1 = 1.0` compiles to `Equal(ToDecimal(1), 1.0)`
[src: PROBES-2026-10-22 RESULTS.md §10].

The spec is silent on conversions of a tuple type to another tuple type whose element types are
convertible. Table 3-J has no tuple rows. Observed: `{ Tuple { v: 1 } } union { Tuple { v: 1.5 } }`
is typed `List<Choice<Tuple{v:Decimal}, Tuple{v:Integer}>>`, with no conversion
[src: PROBES-2026-10-22 RESULTS.md §10].

**Explicit conversion.** "If the conversion cannot be performed, the result is null.", and
`convert 'Foo' to Integer` "will result in null."
[src: CQL-1.5.3 03-developersguide > Types > Conversion > Explicit Conversion] (see Version
differences). Table 3-I lists the conversion operators that `convert` invokes.

CQL-TESTS expects `null` for `convert 'foo' to Integer`, matching the spec text
[src: CQL-TESTS CqlTypeOperatorsTest.xml StringToIntegerError]. Observed: `null`
[src: PROBES-2026-10-22 RESULTS.md §12].

**Version differences**

| Topic | 1.4 | 1.5.3 | 2.0.0 |
| --- | --- | --- | --- |
| Long conversions | no Long type | Integer→Long, Long→Decimal, Long→Quantity implicit; ToLong, ToInteger(Long) explicit | same as 1.5.3 |
| Boolean conversions | String→Boolean only | adds ToBoolean(Integer, Long, Decimal), ToInteger(Boolean), ToLong(Boolean), ToDecimal(Boolean) | same as 1.5.3 |
| ValueSet → List<Code> | not listed | implicit | implicit |
| ToDateTime(Date) | "all time components set to 0" | "all time components unspecified" | same as 1.5.3 |
| No conversion needed | silent | silent | "all the conversion operations are defined to return the input value if no conversion is required" |
| Transitivity | silent | silent | "Implicit conversion in CQL is not transitive." |
| Number to Quantity | silent | silent | "the resulting quantity will have the default unit 1", which may not compare with calendar units |

Sources: [src: CQL-1.4 03-developersguide > Types > Conversion > Implicit Conversions]
[src: CQL-2.0.0 03-developersguide > Types > Conversion > Implicit Conversions]
[src: CQL-1.4 03-developersguide > Types > Conversion > Explicit Conversion]
[src: CQL-2.0.0 03-developersguide > Types > Conversion > Explicit Conversion].

## Tuples

- **Subtyping:** see [Type testing](#type-testing-is).
- **Selector type:** "For a tuple selector, the type is constructed from the elements in the tuple
  selector." (same in 1.4, 2.0)
  [src: CQL-1.5.3 03-developersguide > Types > Type Inference > Literals and Selectors]
- **Compatibility:** "Class and tuple types are compatible if the elements of one type are a subset
  of the elements of the other, by name." (1.5+)
  [src: CQL-1.5.3 03-developersguide > Types > Conversion Precedence]
- **Structured types:** implicit conversion to the equivalent tuple, explicit conversion back; see
  [Implicit conversions](#implicit-and-explicit-conversion).
- **Null elements:** spec silent on type tests; see
  [Tuples with a null element](#tuples-with-a-null-element).
- **Differently typed tuples in one list:** typed as a Choice of the tuple types, without converting
  element types (observed; see [Implicit conversions](#implicit-and-explicit-conversion)).

## List and conditional typing

### List selectors

From the Developer's Guide (same in 1.4, 2.0)
[src: CQL-1.5.3 03-developersguide > Types > Type Inference > Literals and Selectors]:

> "If the type of the list is inferred, the type of the first element is used initially, and
> subsequent elements in the list are required to be of the inferred type of the first element,
> with the exception that if a subsequent element is a supertype of the initial element, or if the
> initial element is convertible to the type of a subsequent element, the type of the subsequent
> element will become the new inferred element type for the list."

For an empty list with no type specifier the type is `List<Any>`. The ELM List selector is stricter:
"the static type of the first argument determines the type of the resulting list, and each
subsequent argument must be of that same type."
[src: CQL-1.5.3 04-logicalspecification > List Operators > List]

Observed [src: PROBES-2026-10-22 RESULTS.md §9]:

| CQL | ELM result type | Note |
| --- | --- | --- |
| `{ 1, 1.5 }`, `{ 1.5, 1 }` | `List<Decimal>` | `ToDecimal` inserted on `1`, either order |
| `{ }` | `List<Any>` | matches the text |
| `{ 1, 'a' }` | `List<Any>` | compiles with no diagnostic |
| `{ 1, 2.0 }` | `List<Decimal>` | `First({ 1, 2.0 }) is Decimal` is `true`, `is Integer` `false` [src: PROBES-2026-10-22 RESULTS.md §56] |

`{ 1, 'a' }` meets neither exception in the quoted rule (String is not a supertype of Integer, and
Integer does not convert to String). The rule says such elements are "required" to match, so the
text implies an error.

#### Gotcha: `{ 1, 'a' }` compiles to `List<Any>`

- **Symptom:** a list of mixed, unrelated element types compiles with no diagnostic.
- **Probe:** `testTsListMixed`, against the control `{ 1, 2 }`
  [src: PROBES-2026-10-22 RESULTS.md §9].
- **Spec:** decides: later elements are "required" to match (quoted above).
- **Well-formed?** No: an author error that the translator accepts.
- **Layer:** translator (leniency).
- **Evidence:** the ELM result type is `List<System.Any>`, with no conversion and no error.
- **Workaround:** keep lists homogeneous, or declare the type:
  `List<Choice<Integer, String>> { 1, 'a' }` [src: PROBES-2026-10-22 RESULTS.md §33].
- **Affects:** translator 5.4.0.

### Conditional expressions

ELM `If`: "The static type of the then argument determines the result type of the conditional, and
the else argument must be of that same type." (same in 1.4, 2.0; 1.4 differs in figure captions
only) [src: CQL-1.5.3 04-logicalspecification > Conditional Operators > If]. ELM `Case` says the
same for every `then` and the `else`
[src: CQL-1.5.3 04-logicalspecification > Conditional Operators > Case].

(2.0+) The 2.0.0 Developer's Guide relaxes this: "if the result type is a supertype of the inferred
type, or if the inferred type is convertible to the result type, the type of the subsequent element
becomes the new inferred element type for the expression. Otherwise, the result type of the
subsequent expression is added to the choice of possible types." It also says "systems should issue
a warning when none of the branches are choice types, but the inferred type of the overall
conditional is a choice type" (message `003-10000`)
[src: CQL-2.0.0 03-developersguide > Conditional Expressions > Type Inference of Conditional Expressions].

#### Gotcha: `if` with unrelated branch types compiles to a Choice at 1.5

- **Symptom:** at compatibility level 1.5, `if true then 1 else 'a'` compiles to
  `Choice<Integer, String>`, with `As` on each branch, and no diagnostic.
- **Probe:** `testTsIfMixed`, against `if true then 1 else 1.5`, which is `Decimal`, with
  `ToDecimal` on the `then` branch [src: PROBES-2026-10-22 RESULTS.md §11].
- **Spec:** changed between versions: the ELM `If` rule above for 1.5.3; (2.0+) the Choice, with a
  warning.
- **Well-formed?** Not at 1.5; valid at 2.0.
- **Layer:** translator (version gotcha): it applies the 2.0.0 rule at 1.5, without the 2.0.0
  warning.
- **Evidence:** the translator builds the Choice in `ensureCompatibleTypes`
  [src: CQFW-5.4.0 cql-to-elm/src/commonMain/kotlin/org/cqframework/cql/cql2elm/LibraryBuilder.kt:2210-2222],
  and the message code `003-10000` does not occur in the v5.4.0 source.
- **Workaround:** give both branches one type, for example by converting or casting one branch.
- **Affects:** translator 5.4.0 at compatibility level 1.5.

### Queries

The result type of a query follows its sources and `return` clause; `let`, `with`, `without` and
`where` "do not impact the type of the result" (same in 1.4, 2.0)
[src: CQL-1.5.3 03-developersguide > Types > Type Inference > Queries]. (1.5+) "If an aggregate
clause is used, the result type of the query is the result type of the aggregate expression".

### Promotion and demotion

"Promotion is used to implicitly convert a value to a list of values of that type", and demotion
extracts a single value "using singleton from". "environments may choose whether or not to support
these features of the language."
[src: CQL-1.5.3 03-developersguide > Types > Promotion and Demotion] (1.5+) The translator options
are named: "implementations may choose to enable or disable this language feature using the
disable-list-promotion and disable-list-demotion options."
[src: CQL-1.5.3 06-translationsemantics > CQL-to-ELM > Translation Options > Disable List Promotion and Demotion]
The language server used for the probes compiles with both disabled, so its results can differ from
an environment that enables them [src: PROBES-2026-10-22 RESULTS.md §1].

#### Gotcha: list promotion is disabled in the language server

- **Symptom:** `exists false` fails to compile: `Could not resolve call to operator Exists with
  signature (System.Boolean).`
- **Probe:** `testExistsBoolean`, against `exists { false }`, which is `true`
  [src: PROBES-2026-10-22 RESULTS.md §15].
- **Spec:** decides that environments may choose (quoted above).
- **Well-formed?** Only where list promotion is enabled.
- **Layer:** environment (the language server's translator options).
- **Evidence:** the language server compiles with `DisableListPromotion` and `DisableListDemotion`
  [src: PROBES-2026-10-22 RESULTS.md §1].
- **Workaround:** don't rely on promotion or demotion. For a Boolean, write `X is true`; use
  `exists { X }` only if a one-element list is really meant.
- **Affects:** CQL language server 4.11.0-SNAPSHOT; other environments may enable both.

## Where the spec is silent

Each of these was searched in 1.4, 1.5.3 and 2.0.0:

| Question | Finding |
| --- | --- |
| `null is T` | silent in 1.4 and 1.5.3; 2.0.0: `false` |
| A tuple with a null element under `is` | silent in all three |
| Narrowing after `X is T` | silent in all three |
| `Choice<A, B>` to a supertype of a component | silent in all three |
| Implicit conversion of the elements of set-operator operands, and of one tuple type to another | silent in all three |
| `intersect` of lists with no common type | silent in all three |
| Whether `as` to a type that is neither a component nor a subtype is a compile error | silent in all three; translator 5.4.0 rejects it |
| The run-time type of an interval with a null bound, under `is` | silent in all three; see [intervals.md](intervals.md#type-tests-on-an-interval-with-a-null-bound) |
