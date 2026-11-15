# CQL Library Syntax Reference

Baseline: CQL 1.5.3. Untagged statements hold in 1.4, 1.5.3 and 2.0.0.
Sources: CQL-1.4, CQL-1.5.3, CQL-2.0.0, PROBES-2026-10-22, PROBES-2026-11-14

Library structure and declarations, from the Author's Guide, Developer's Guide and CQL Grammar.
Source IDs are defined in [SOURCES.md](SOURCES.md).

---

## Library Declaration

```cql
library LibraryName version '1.0.000'
```

- One library per CQL file
- Library identifiers must be unique within a namespace
- Circular references are prohibited
- References are not transitive — each library must explicitly include what it uses
- "all references to the same library use the same version"

These rules are the same in 1.4 [src: CQL-1.5.3 03-developersguide > Libraries]. **2.0:** "A given
library SHALL NOT include multiple versions of the same library", and how to handle a conflict
arriving through different included libraries "is up to the implementation environment"
[src: CQL-2.0.0 03-developersguide > Libraries].

## Using (Data Model)

```cql
using FHIR version '4.0.1'
using QDM version '5.4'
```

- Data model identifiers must be unique among models and libraries
- Data model references must be declared locally — not inherited from referenced libraries
- The version is optional. "If a version is specified, then the environment must ensure that the
  version specifier matches the version of the data model supplied. If no data model matching the
  requested version is present, an error is thrown."

(same in 1.4) [src: CQL-1.5.3 03-developersguide > Data Models]. **2.0:** replaces the uniqueness
rule: a model's local identifier must be unqualified and "unique within the artifact". It also adds
trial-use model namespaces and `called` aliases, and says "Multiple versions of the same model SHALL
NOT be referenced in the same library." [src: CQL-2.0.0 03-developersguide > Data Models]

## Include

```cql
include Global.Common version '1.0.000' called Common
include SupplementalDataElements version '3.4.000' called SDE
```

- `called` clause sets the local alias; omit to use the unqualified library identifier
- Access included library members via alias: `Common.Foo()`
- Version specifier is optional; without one, "it is up to the implementation environment to
  provide the most appropriate version". Always giving one is a convention, not a spec rule

(same in 1.4) [src: CQL-1.5.3 03-developersguide > Libraries]
[src: CQL-1.5.3 02-authorsguide > Declarations > Libraries]

## Parameter Declarations

```cql
parameter Threshold Integer
parameter Range Interval<Integer>
parameter Demographics Tuple { address String, city String }
parameter Points List<Integer>
parameter ChoiceValue Choice<Integer, String>

parameter "Measurement Period" Interval<DateTime>
  default Interval[@2025-01-01T00:00:00.000, @2026-01-01T00:00:00.000)
```

## Context Declaration

```cql
context Patient
context Practitioner
```

Specifies the subject of clinical data retrieval. Models define the available contexts, and "should
identify a default context that is used when authors do not declare a specific context. When no
context is specified in the library, and the model has not declared a default context, the default
context is Unfiltered." (same in 1.4, 2.0) [src: CQL-1.5.3 02-authorsguide > Declarations > Context]

## ValueSet Declarations

```cql
valueset "Female Administrative Sex": 'urn:oid:2.16.840.1.113883.3.560.100.2'
valueset "Acute Pharyngitis": 'urn:oid:2.16.840.1.113883.3.464.1003.102.12.1011'
```

## CodeSystem Declarations

```cql
codesystem "SNOMED": 'http://snomed.info/sct'
codesystem "LOINC": 'http://loinc.org'
codesystem "ActCode": 'http://terminology.hl7.org/CodeSystem/v3-ActCode'
```

## Code and Concept Declarations

```cql
code "Acute Pharyngitis Code": '363746003' from "SNOMED" display 'Acute pharyngitis (disorder)'
concept "Diabetes Mellitus": { "Diabetes ICD9", "Diabetes ICD10" } display 'Diabetes Mellitus'
```

A `concept` **declaration** lists code declarations by name, but a `Concept` **selector** takes only
Code selectors: `Concept { Code '2345-7' from "LOINC" }`. The grammar is
`'Concept' '{' codeSelector (',' codeSelector)* '}'` (same in 1.4; **2.0:** also allows an empty
`Concept { }`) [src: CQL-1.5.3 08-a-cqlsyntax > Terms] [src: CQL-2.0.0 08-a-cqlsyntax > Terms], so `Concept { "Glucose" }` is a syntax error. Observed on
translator 5.5.0: `Syntax error at }` [src: PROBES-2026-11-14 RESULTS.md §5].

## Expression Definitions

```cql
define "Encounters": [Encounter: "Inpatient"]
define "Has Diabetes": exists([Condition: "Diabetes"])
```

- Support forward declarations provided no circular dependencies exist (same in 2.0; **1.4:**
  lacks the 1.5.3 identifier-hiding rules for aliases, operands and lets)
  [src: CQL-1.5.3 03-developersguide > Libraries > Identifier Resolution]
- Default access modifier is `public` (same in 1.4, 2.0)
  [src: CQL-1.5.3 03-developersguide > Libraries > Access Modifiers]

```cql
define public "Public Expression": 1 + 1
define private "PrivateHelper": true
```

The modifier follows `define` (grammar: `'define' accessModifier? identifier ':' expression`). For
`parameter`, `codesystem`, `valueset`, `code` and `concept` it comes first: `private parameter …`.
(same in 1.4, 2.0; 1.5.3 adds `fluent` to the function rule)
[src: CQL-1.5.3 08-a-cqlsyntax > Statements]

## Function Definitions

```cql
define function "CumulativeDuration"(Intervals List<Interval<DateTime>>):
  Sum((collapse Intervals) X return all duration in days of X)
```

**Fluent functions** (1.5+, trial-use) — invoked with dot notation
[src: CQL-1.5.3 03-developersguide > Defining Functions > Fluent Functions]:

```cql
define fluent function "confirmed"(Conditions List<Condition>):
  Conditions C where C.verificationStatus ~ "Condition Confirmed"

// Usage:
([Condition]).confirmed()
```

By the 1.5.3 grammar a retrieve is an `expression`, not an `expressionTerm`, and dot invocation
needs an `expressionTerm`, so a retrieve must be parenthesised. Observed on translator 5.4.0:
`[Condition].c()` gives `Syntax error at .`; `([Condition]).c()` compiles
[src: PROBES-2026-10-22 RESULTS.md §5].

Fluent-function gotchas (1.5+, trial-use), observed on translator 5.5.0:

- **Only dot syntax.** The spec says a fluent call gives "the same" result "as if the functions had
  been invoked normally", and shows the normal call `activeOrRecurring(confirmed(Conditions))`
  [src: CQL-1.5.3 03-developersguide > Defining Functions > Fluent Functions]. The translator rejects
  a normal call to a fluent function, qualified or not: `Operator tag with signature
  (System.Integer) is a fluent function and can only be invoked with fluent syntax.`
  [src: PROBES-2026-11-14 RESULTS.md §2]. Define a non-fluent function if both forms are needed.
- **Resolved across included libraries by include order.** A dot call isn't qualified with a
  library alias, and the spec doesn't say how it is resolved when several included libraries define
  a matching function. The translator takes the **first included library with a compatible
  overload**, even when a later one has an exact match, with no warning: with `LibB`'s
  `widen(Decimal)` included before `LibA`'s `widen(Integer)`, `1.widen()` converts the argument and
  calls `LibB`'s [src: PROBES-2026-11-14 RESULTS.md §2]. Don't define a fluent function with the name
  of one a commonly co-included library (FHIRCommon, QICoreCommon, CQMCommon…) already defines
  unless the definitions are identical; when a function works in one library and not another,
  compare their includes and include order.
- **FHIRPath names are taken.** A dot call named after a FHIRPath function is translated to the CQL
  operator the FHIRPath translation appendix gives (for example `X.toString()` to `ToString(X)`)
  [src: CQL-1.5.3 16-i-fhirpathtranslation > .toString()] [src: CQL-1.5.3 03-developersguide > Using FHIRPath > Method Invocation],
  before any user fluent function of that name is considered: a fluent `toString` is never called,
  and `true.toBoolean()` fails with `Could not resolve call to operator ToBoolean with signature
  (System.Boolean)` [src: PROBES-2026-11-14 RESULTS.md §3]. Use other names, such as `toFHIRString`.
  (1.5+) Disabling method invocation disables fluent functions too
  [src: CQL-1.5.3 06-translationsemantics > CQL-to-ELM > Translation Options > Disable Method Invocation].
- **Duplicate signatures aren't reported.** Two functions with the same name and signature compile
  without a diagnostic and calls use the first, while a duplicate `define` is an error
  (`Identifier X is already in use in this library.`) [src: PROBES-2026-11-14 RESULTS.md §4]. Check by
  eye when reviewing a library.

**External functions** — implemented by the host environment:

```cql
define function "IsSubsumedBy"(code Code, subsumingCode Code)
  returns Boolean : external
```

The return type is required. The spec warns that "the use of external functions is discouraged"
because they are implementation specific (same in 1.4, where the text sits under Defining
Functions) [src: CQL-1.5.3 03-developersguide > Defining Functions > External Functions]
[src: CQL-1.4 03-developersguide > Defining Functions].

## Retrieve Expressions

```cql
[Encounter: "Inpatient"]
[Condition: "Diabetes"]
[Observation: "HbA1c Value"]
```

**Related context retrieves** (same in 1.4, 2.0; the expression before `->` must return a single
value, not a list) [src: CQL-1.5.3 03-developersguide > Related Context Retrieves]. (1.5+,
trial-use) search paths, `include` and `reverseInclude` on a retrieve:

```cql
["Mother" -> "Observation": "Estimated Due Date"]
```

## Type Specifiers

With a data model in use, an unqualified type name in a selector can resolve to the model's type
rather than the System one. Observed on translator 5.5.0: with `using FHIR`,
`Quantity { value: 4.0, unit: 'mg' }` is a `FHIR.Quantity` selector and fails with `Expected an
expression of type 'decimal',but found an expression of type 'System.Decimal'.`; without a model it
is a System Quantity [src: PROBES-2026-11-14 RESULTS.md §5]. Write `System.Quantity { … }`, or a
quantity literal such as `4.0 'mg'`.

```cql
parameter Name String
parameter Values List<Integer>
parameter Range Interval<DateTime>
parameter Data Tuple { name String, age Integer }
parameter Mixed Choice<Integer, String>
```

## Identifier Rules

| Style | Syntax | Use |
|-------|--------|-----|
| Simple | `MyIdentifier` | Starts with letter/underscore, alphanumeric + underscore |
| Quoted | `"My Expression"` | Double-quotes; case-sensitive; allows spaces |
| Delimited | `` `My Identifier` `` | Backticks; allows spaces and commas |

All three kinds are case-sensitive: "double-quoted and delimited identifiers are still
case-sensitive" (same in 1.4, 2.0)
[src: CQL-1.5.3 03-developersguide > Lexical Elements > Identifiers].

Reserved words: "identifiers that clash with a reserved word can be double-quoted or surrounded by
backticks". "most reserved words may still be used as identifiers if the usage is unambiguous", but
"named expressions, terminology declarations, aliases, and let clauses cannot use keywords or
reserved words as identifiers" (unquoted). (1.5+) `aggregate` is a reserved word
[src: CQL-1.5.3 03-developersguide > Lexical Elements > Reserved Words]:

```cql
define "exists": true
```

Translator 5.5.0 warns when a string literal is spelled like a definition's name, `String literal
'Foo' matches the identifier Foo. Consider whether the identifier was intended instead.`: a
reminder that single quotes make a string and double quotes an identifier
[src: PROBES-2026-11-14 RESULTS.md §6].

## Query Syntax

```cql
// Single-source
[Encounter: "Inpatient"] E
  where E.length <= 120 days
    and E.period ends during MeasurementPeriod

// Multi-source with let
from "Encounters" E,
     "Warfarin Therapy" W
let overlapDays: duration in days of (W.effectiveTime intersect E.period)
where W.effectiveTime starts during E.period
return E
```

**Query sources.** A query source is a retrieve, a qualified identifier (a definition, alias or
property path such as `C.item`), or a parenthesised expression (same in 1.4, 2.0)
[src: CQL-1.5.3 08-a-cqlsyntax > Queries]. So a function call or a list literal must be
parenthesised: `(F(x)) X where …`, `(E.includedEncounters()) I`, `({ 'a', 'b' }) U return …`. Observed
on translator 5.5.0: `F(1) X return X` and `{ 1, 2 } X return X` give `Syntax error at X`
[src: PROBES-2026-11-14 RESULTS.md §1]. A property path needs no parentheses, also inside a function
call (`Count(T.item I return I.a)`) or after `flatten`.

## Aggregate Clause (1.5+, trial-use)

```cql
define FactorialOfFive:
  ({ 1, 2, 3, 4, 5 }) Num
    aggregate Result starting 1: Result * Num
```

(1.5+, trial-use) [src: CQL-1.5.3 03-developersguide > Aggregate Queries]
Syntax: `aggregate [all|distinct] <alias> [starting <value>]: <expression>`. It replaces `return`.
The starting value must be a literal, a quantity, or a parenthesised expression. Without `starting`,
"the aggregation result is initially `null`".

## Comment Tags (1.5+, trial-use)

Tag syntax in 1.5.3: `@`, an unquoted identifier, a colon (1.5+, trial-use)
[src: CQL-1.5.3 03-developersguide > Lexical Elements > Comments > Tags]. **2.0:** the tag is
"optionally followed by a colon (:) and a string value", so `@inclusion` alone is a tag
[src: CQL-2.0.0 03-developersguide > Lexical Elements > Comments > Tags].

```cql
/*
@author: Author Name
@description: Calculates cumulative interval duration
@comment: Collapses overlapping intervals first
*/
define function "CumulativeDuration"(Intervals List<Interval<DateTime>>):
  Sum((collapse Intervals) X return all duration in days of X)
```
