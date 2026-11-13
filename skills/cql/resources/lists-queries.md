# CQL Lists and Queries

Baseline: CQL 1.5.3. Untagged statements hold in 1.4, 1.5.3 and 2.0.0.
Sources: CQL-1.5.3, CQL-2.0.0, CQL-TESTS, CQFW-5.4.0, PROBES-2026-10-22, CQLWIKI

`singleton from`, duplicates and the set operators, empty lists, query result shapes, multi-source
queries, relationships and sorting. Source IDs are in [SOURCES.md](SOURCES.md). Null handling in
these operators is in [nulls.md](nulls.md#list-membership-and-set-operators); typing of set
operators over different element types is in
[type-system.md](type-system.md#set-operators-observed-typing).

The spec text below is the rule. Blocks marked **Gotcha** record where translator or engine 5.4.0
departs from it or depends on a setting, each with a workaround; see
[diagnosing.md](diagnosing.md) for how the layer was decided.

## `singleton from`

"If the source list is empty, the result is null. If the source list contains one element, that
element is returned. If the list contains more than one element, a run-time error is thrown." and
"If the source list is null, the result is null." (same in 1.4, 2.0)
[src: CQL-1.5.3 09-b-cqlreference > List Operators > Singleton From].

Observed: as specified; `singleton from { 1, 2 }` raises `Expected a list with at most one element,
but found a list with multiple elements.` [src: PROBES-2026-10-22 RESULTS.md §34]. A run-time error
stops the whole library run ([intervals.md](intervals.md#invalid-intervals-and-unit-intervals)), so
guard data that can hold several matches: `if Count(L) = 1 then singleton from L else null`
[src: PROBES-2026-10-22 RESULTS.md §40], or use
`First` with a `sort` when one of several is wanted.

## Duplicates and the set operators

`union` "returns a list with all unique elements from both arguments", "duplicates are eliminated".
`intersect` and `except` are "defined with set semantics, meaning that each element will appear in
the result at most once" (same in 1.4; **2.0:** adds `union all`, `intersect all` and `except all`
forms that keep duplicates) [src: CQL-1.5.3 09-b-cqlreference > List Operators > Union]
[src: CQL-1.5.3 09-b-cqlreference > List Operators > Intersect]
[src: CQL-1.5.3 09-b-cqlreference > List Operators > Except]. None promises an order: "there is no
expectation that the order of elements in the inputs will be preserved in the results."

Observed: `{ 1, 1, 2 } union { 2, 3 }` is `[1, 2, 3]`; `intersect` and `except` drop duplicates
too; `flatten` keeps them [src: PROBES-2026-10-22 RESULTS.md §35]. When element types differ, the
operands are typed as a list of a Choice and no implicit conversion applies, so `{ 1 } intersect
{ 1.0 }` is empty ([type-system.md](type-system.md#set-operators-observed-typing)).

## Queries: result shape and duplicates

The result type follows the sources and the `return` clause
([type-system.md](type-system.md#queries)). For duplicates, Language Semantics says: "If neither all
or distinct is specified, distinct is the default behavior." (same in 1.4, 2.0)
[src: CQL-1.5.3 05-languagesemantics > Query Evaluation > Iteration > Return Clause]. The Author's
Guide puts it more generally: "By default, a query returns a list of distinct results, suppressing
duplicates. To include duplicates, use the all keyword in the return clause." (same in 1.4, 2.0;
1.4 differs in wording) [src: CQL-1.5.3 02-authorsguide > Queries > Shaping].

The formal semantics decides the case with no `return` clause: "If the return clause is specified,
use a ForEach to produce the result of the return. If the return clause specifies Distinct, also
attach a Distinct operation to the result." (same in 1.4, 2.0; 1.5.3 adds the aggregate step)
[src: CQL-1.5.3 05-languagesemantics > Query Evaluation > Implementing Query Evaluation]. So a
query without `return` keeps duplicates, and `return X` is distinct by default. The Author's Guide
sentence reads as broader than this; the formal pages govern
([spec/README.md](spec/README.md#pages-worth-knowing)).

Observed, as specified [src: PROBES-2026-10-22 RESULTS.md §35]:

| CQL | Result |
| --- | --- |
| `({ 1, 1, 2 }) X where X > 0` (no `return`) | `[1, 1, 2]` |
| `({ 1, 1, 2 }) X return X` | `[1, 2]` |
| `({ 1, 1, 2 }) X return all X` | `[1, 1, 2]` |

Pattern: write the `return` you mean. Use `return X` (or `distinct ( … )`) when duplicates must go,
and `return all X` when they must stay.

## Multi-source queries

"Conceptually, this step involves generating the cartesian product of all the sources involved"
(same in 1.4, 2.0) [src: CQL-1.5.3 05-languagesemantics > Query Evaluation > Evaluate Sources].
(1.5+) "Note that if any query source in a multi-source query is list-valued, the result is a list,
even if other sources are singleton." and "If all the sources of a query evaluate to null, the
result is null" [src: CQL-1.5.3 03-developersguide > Non-Retrieve Queries].

Observed [src: PROBES-2026-10-22 RESULTS.md §36]:

| CQL | Result |
| --- | --- |
| `from ({ 1, 2 }) A, ({ 10, 20 }) B return all A + B` | `[11, 21, 12, 22]` (4 rows) |
| `from ({ 1, 2 }) A, (5) B return all A + B` | `[6, 7]` |
| `from (1) A, (2) B return A + B` | `3` (a single value) |
| `from ({ 1, 2 }) A, (List<Integer> { }) B return all A` | `[]` |
| `from ({ 1, 2 }) A, (null as List<Integer>) B return all A` | `[]` |
| both sources null | `null` |
| `(null as DateTime) X return if X is null then 1 else 2` (one null source) | `null`: the `return` is not evaluated [src: PROBES-2026-10-22 RESULTS.md §45] |

So an empty source empties the whole product, and one null source behaves as empty. Authoring
pattern (guide text, page dated 2017-10-12): a multi-source `from` over two event lists "will return
results only in the case that there are both"; to express "either", split it into separate
expressions related with `with` [src: CQLWIKI QA-Multi-Source-Query-Uses-Cartesian-Products.md].

## Relationships: `with` and `without`

`with` keeps elements that have a related element meeting `such that`; `without` keeps those that
have none (same in 1.4; **2.0:** adds "It is worth noting that the with and without clauses are
shorthand for equivalent exists and not exists expressions", and "if there are no related elements
in a with clause … the result of the with relationship is false, while if there are no related
elements in a without clause, the result of the without relationship is true.")
[src: CQL-1.5.3 02-authorsguide > Queries > Relationships]
[src: CQL-2.0.0 02-authorsguide > Queries > Relationships].

Observed, consistent with the 2.0.0 clarification [src: PROBES-2026-10-22 RESULTS.md §37]: an empty
related source gives `[]` under `with` and every element under `without`; a null `such that`
condition counts as no match, so `with` excludes and `without` keeps.

Authoring pattern (guide text, 2017-10-12): intersecting two lists of different events is empty
when each returns a different kind of element; relate them with `with … such that` instead
[src: CQLWIKI QA-First-and-Intersect.md].

## Sorting

"Because the sort applies after the query results have been determined, alias references are
neither required nor allowed in the sort." (same in 1.4, 2.0); "If no ascending or descending
specifier is provided, the order is ascending."; nulls "are considered lower than any non-null
value" (**1.4:** "they are sorted first"); and (1.5+) "Within the expressions of a sort clause, the
iteration accessor $this may be used to access the current iteration element"
[src: CQL-1.5.3 02-authorsguide > Queries > Sorting]. Without a sort clause, "the order of the
result is unprescribed and is implementation specific" (**1.4:** "undefined and may vary by
implementation").

Observed [src: PROBES-2026-10-22 RESULTS.md §38]: `sort asc`, `sort by a` on tuples and
`sort by a desc` with a typed null element behave as specified (null last when descending);
`sort by T.a` fails to compile (`Could not resolve identifier T`), as the alias rule says; and
sorting tuples whose element is an untyped `null` fails to compile (`Less(System.Any, System.Any)
is ambiguous`) — type the null.

Authoring patterns (guide text, 2017-10-12): "Your sort clause is incorrect because it is evaluated
on the result of the query" [src: CQLWIKI QA-Validation-Error-Due-to-Aliases-in-Sort-By.md]; for a
choice-typed element, cast it to the type to sort by: `sort by (result as Quantity) desc`
[src: CQLWIKI QA-Specifying-Type-For-Sort-By.md].

#### Gotcha: `$this` alone in `sort by` fails at run time

- **Symptom:** `({ 3, 1, 2 }) X sort by $this desc` compiles, then fails with `Could not resolve
  path '$this' on 3.`
- **Probe:** `testLqSortThis`, against `testLqSortThisTuple` (`sort by $this.a` on tuples, which
  works) [src: PROBES-2026-10-22 RESULTS.md §38].
- **Spec:** (1.5+) `$this` "may be used to access the current iteration element" in a sort clause
  [src: CQL-1.5.3 02-authorsguide > Queries > Sorting].
- **Well-formed?** Yes.
- **Layer:** engine (the run-time error is raised by evaluation; the expression compiled).
- **Evidence:** the error is a run-time message, without the "loaded, but had errors" prefix of a
  compile error.
- **Workaround:** for a list of simple values, use `sort asc` or `sort desc`; for tuples or
  classes, sort by the element name (`sort by a`) or `$this.a`.
- **Affects:** engine 5.4.0.

## Empty lists and indexing

An empty list with no type specifier is `List<Any>`
([type-system.md](type-system.md#list-selectors)). List equality is true "if and only if the lists
contain elements of the same type, have the same number of elements, and for each element in the
lists, in order, the elements are equal" (same in 1.4, 2.0)
[src: CQL-1.5.3 09-b-cqlreference > Comparison Operators > Equal]. The indexer: "If the index is
less than 0, or greater than the number of elements in the list, the result is null." (same in 1.4,
2.0) [src: CQL-1.5.3 09-b-cqlreference > List Operators > Indexer].

Observed: `First` and `Sum` of an empty list are `null`; `Count` is `0`; `exists` is `false`;
`{ 1, 2 }[5]` and `{ 1, 2 }[-1]` are `null` [src: PROBES-2026-10-22 RESULTS.md §39].

#### Gotcha: `=` with an empty list is null

- **Symptom:** `List<Integer> { } = List<Integer> { }` is `null`, and so is
  `List<Integer> { } = { 1 }`.
- **Probe:** `testLqEmpty`, `testLqEmptyEquiv`, with `{ 1 } = { 1 }` as the control
  [src: PROBES-2026-10-22 RESULTS.md §39].
- **Spec:** the definition above makes two empty lists equal (same type, same count, no element
  differs) and an empty list unequal to `{ 1 }`. CQL-TESTS expects `true` for `{} = {}`
  [src: CQL-TESTS CqlListOperatorsTest.xml EqualEmptyListAndEmptyList].
- **Well-formed?** Yes.
- **Layer:** engine. The ELM is a plain `Equal` of two `List` nodes.
- **Evidence:** the list comparison returns null as soon as either list is empty
  [src: CQFW-5.4.0 engine/src/commonMain/kotlin/org/opencds/cqf/cql/engine/elm/executing/EqualEvaluator.kt:262-268].
- **Workaround:** to test for an empty list, use `not exists L` or `Count(L) = 0`; to compare two
  lists that may be empty, use `~` (`List<Integer> { } ~ List<Integer> { }` is `true`), noting that
  `~` also changes string, quantity and null semantics
  ([nulls.md](nulls.md#equality-and-equivalence)).
- **Affects:** engine 5.4.0.

## Where the spec is silent

Each was searched in 1.4, 1.5.3 and 2.0.0:

| Question | Finding |
| --- | --- |
| The order of a query's results without `sort` | "unprescribed and is implementation specific" |
| The order of elements after `union`, `intersect` or `except` | "no expectation that the order … will be preserved" |
