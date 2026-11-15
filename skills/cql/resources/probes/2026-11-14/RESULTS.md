# Probe results, 2026-11-14

Run with translator and engine **5.5.0** (`org.cqframework:cql-to-elm-jvm`, `engine-jvm`,
`engine-fhir`, from Maven Central), the versions cql-language-server 5.0.0 and the VS Code CQL
extension 1.0.0 use. The harness is in `harness/`: `Probe.java` translates each library with the
translator's default options, prints every error and warning with its line, then evaluates each
expression definition with the engine (FHIR R4 model resolver, no data, no terminology).
`Elm.java` prints a library's ELM. Every ELM header reads `signatureLevel="Overloads"`,
`translatorOptions="EnableAnnotations,EnableLocators,DisableListDemotion,DisableListPromotion"`.
The probe sources are the `.cql` files beside this file. All libraries were run twice, with
identical output.

These probes check pitfalls recorded in the CQL skill of cqframework/dqm-content-cms-2026
(`.claude/skills/cql/SKILL.md` at `757d7c6`), observed there with the VS Code extension.

## 1. Query sources

| Library | Expression | Output |
| --- | --- | --- |
| `testListLiteralSource` | `{ 1, 2, 2 } X return X` | `Syntax error at X` |
| `testListLiteralSourceParen` | `({ 1, 2, 2 }) X return X` | `{ 1, 2 }` |
| | `({ 1, 2, 2 }) X return all X` | `{ 1, 2, 2 }` |
| `testCallSource` | `F(1) X return X + 10` | `Syntax error at X` |
| `testCallSourceParen` | `(F(1)) X return X + 10` | `{ 11, 12 }` |
| `testPathSourceInCall` | `T.item I return I.a` | `{ 1, 2 }` |
| | `Count(T.item I return I.a)` | `2` |
| `testFlattenPathSource` | `flatten (T.item I return I.a)` | `{ 1, 2, 3 }` |

**Settles:** a function invocation or a list literal can't be a query source without parentheses.
A property path can, also inside a function call or after `flatten`; the claim that
`flatten (C.item I return …)` is a syntax error isn't reproduced at 5.5.0.

## 2. Fluent functions

`LibA` and `LibB` each define `fluent function tag(x Integer)` (returning `'A'`, `'B'`); `LibA`
defines `widen(x Integer)` returning `'A-Integer'` and `LibB` defines `widen(x Decimal)` returning
`'B-Decimal'`.

| Library | Includes, in order | Expression | Output |
| --- | --- | --- | --- |
| `testFluentTwoLibraries` | `LibA`, `LibB` | `1.tag()` | `'A'` |
| | | `1.widen()` | `'A-Integer'` |
| | | `1.0.widen()` | `'B-Decimal'` |
| `testFluentTwoLibrariesReversed` | `LibB`, `LibA` | `1.tag()` | `'B'` |
| | | `1.widen()` | `'B-Decimal'` |
| `testFluentNonFluentCall` | `LibA` | `A.tag(1)` | `Operator tag with signature (System.Integer) is a fluent function and can only be invoked with fluent syntax.` |
| `testFluentLocalNormalCall` | none (`tag` defined locally) | `tag(1)` | same error |
| | | `1.tag()` (same library) | not evaluated: the library has the error above |

No warning in any of these.

**Settles:** a fluent call is resolved against the included libraries **in include order**: the first
library with a compatible overload wins, even when a later library has an exact match. With `LibB`
first, `1.widen()` converts the Integer to Decimal and calls `LibB`'s function although `LibA` has
`widen(Integer)`. A fluent function can't be called with ordinary call syntax, qualified or not.

## 3. Fluent functions named like FHIRPath functions

| Library | Definitions | Output |
| --- | --- | --- |
| `testFhirPathMethodName` | `fluent function toString(x Integer): 'mine'`; `5.toString()` | `'5'` |
| `testFhirPathMethodNameBoolean` | `fluent function toBoolean(b Boolean): b`; `true.toBoolean()` | `Could not resolve call to operator ToBoolean with signature (System.Boolean).` |
| `testFhirPathMethodNameOther` | `fluent function toFHIRString(x Integer): 'mine'`; `5.toFHIRString()` | `'mine'` |

**Settles:** a dot call whose name is a FHIRPath function is translated to the CQL operator, and the
user's fluent function of that name is never called.

## 4. Duplicate definitions

| Library | Definitions | Output |
| --- | --- | --- |
| `testDuplicateFunction` | `function f(x Integer): 1` and `function f(x Integer): 2`; `f(0)` | `1`, no diagnostic |
| `testDuplicateDefine` | `define X: 1` and `define X: 2` | `Identifier X is already in use in this library.` |

## 5. Selectors

| Library | Expression | Output |
| --- | --- | --- |
| `testQuantitySelectorFhir` (`using FHIR`, FHIRHelpers) | `Quantity { value: 4.0, unit: 'mg' }` | `Expected an expression of type 'decimal',but found an expression of type 'System.Decimal'.` |
| `testQuantitySelectorNoModel` | same, no `using` | `4.0 'mg'` |
| `testConceptSelectorRef` | `Concept { "Glucose" }` (`"Glucose"` a `code` declaration) | `Syntax error at }` |
| `testConceptSelectorLiteral` | `Concept { Code '2345-7' from "LOINC" }` | a Concept with that code |

**Settles:** with `using FHIR`, an unqualified `Quantity` selector is `FHIR.Quantity`. A Concept
selector takes Code selectors, not references to `code` declarations.

## 6. A string literal that names a definition

`testStringMatchesIdentifier`: `define "Foo": 1` then `define Bar: 'Foo'` gives the warning
`String literal 'Foo' matches the identifier Foo. Consider whether the identifier was intended
instead.` `Bar` is the string `'Foo'`.

## 7. AllTrue, Trim and Matches

| Library | Expression | Output |
| --- | --- | --- |
| `testAllTrueNull` | `AllTrue({ true, null as Boolean })` | `true` |
| | `AllTrue({ null as Boolean })` | `true` |
| | `true and (null as Boolean)` | `null` |
| `testTrim` | `Trim(' a ')` | `Could not resolve call to operator Trim with signature (System.String).` |
| `testMatchesPartial` | `Matches('abc', 'b')` | `false` |
| | `Matches('abc1def', '\\d')` | `false` |
| | `Matches('abc1def', '.*\\d.*')` | `true` |
| | `Matches('1,2three', '\\w+')` | `false` |
| `testBlankMatches` | `Matches('', '\\s*')`, `Matches('   ', '\\s*')` | `true`, `true` |
| | `Matches(' a ', '\\s*')` | `false` |

**Settles:** the engine matches the **whole** string. The specification (1.5.3 and 2.0.0) says
`Matches` uses partial matching, under which `Matches('abc', 'b')` is true. The 1.5.3 example
`Matches('1,2three', '\\w+')` = false fits whole-string matching; 2.0.0 changed it to
`'^\\w+$'`. No cqframework/cql-tests test distinguishes the two readings.

## 8. Code equivalence and case

`testCodeEquivalenceCase`, both codes from `http://terminology.hl7.org/CodeSystem/v2-0074`:

| Expression | Output |
| --- | --- |
| `Code 'lab' from "V2-0074" ~ Code 'LAB' from "V2-0074"` | `true` |
| `Code 'lab' from "V2-0074" = Code 'LAB' from "V2-0074"` | `false` |
| `'lab' ~ 'LAB'` | `true` |

## 9. Claims not reproduced

| Library | Claim | Output at 5.5.0 |
| --- | --- | --- |
| `testFhirEmptyString` | `FHIR.string { value: '' }` reads back with a null `.value` | `.value` is `''`; `is null` is `false`; `' '` stays `' '` |
| `testBackboneId` | setting `id` on a backbone element (`FHIR.Observation.Component { id: 'x' }`) fails at run time | evaluates; `.id` is `'x'` |

Both were observed through the VS Code extension's execution, with data loaded from files, which
this harness doesn't reproduce.
