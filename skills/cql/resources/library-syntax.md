# CQL Library Syntax Reference

Baseline: CQL 1.5.3. Untagged statements hold in 1.4, 1.5.3 and 2.0.0.
Sources: CQL-1.4, CQL-1.5.3, CQL-2.0.0, PROBES-2026-10-22

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
