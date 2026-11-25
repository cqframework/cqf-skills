# Testing CQL Libraries

Baseline: CQL 1.5.3; translator and engine 5.5.0 for the observed behaviour. Untagged statements hold at these versions.
Sources: CQL-1.5.3, PROBES-2026-11-14, PROBES-2026-11-25, DQMCMS-757d7c6, DQMCMS-739494f

A way to unit-test a CQL library with CQL: a test library of Boolean definitions, each `true` when its
test passes, run against test patients (and inline fixtures for values that aren't resources). The
method is the one the CMS 2026 dQM content repository uses for its shared libraries
[src: DQMCMS-757d7c6 .claude/skills/cql/SKILL.md:74-95] [src: DQMCMS-757d7c6 .claude/skills/cql/SKILL.md:185-236]
[src: DQMCMS-739494f .claude/skills/cql/SKILL.md:269-273];
the CQL facts it relies on are cited to the spec. Running test libraries is covered by the
`vscode-cql` skill (Execute CQL) and the `cql-mcp` skill (`cql_test_run_suite`), and running one in
MADiE (as a Cohort measure on `_Passed`) by the `madie` skill. To check a run, see
[Checking a run](#checking-a-run).

## The test library

- Name it `<Library>Tests`, include the library under test, and write one `define Test…:` per test,
  each a Boolean that is `true` when the test passes.
- **Combine them with `and`**, in a final `define _Passed: TestA and TestB and …`. Not `AllTrue`:
  it ignores nulls (same in 1.4, 2.0), so a test that evaluated to null would count as passing
  [src: CQL-1.5.3 09-b-cqlreference > Aggregate Functions > AllTrue] [src: PROBES-2026-11-14 RESULTS.md §7].
  `and` gives null if any test is null, and false if any is false.
- **A test is passing only when it's `true`.** Treat `false` and `null` as failures. In particular:
  - Don't write `else null` for "doesn't apply" in a case-specific test, or wrap an assertion in
    `Coalesce(…, true)`: a null from an assertion that couldn't be evaluated then looks like "doesn't
    apply" and hides the bug. Use `else true`.
  - To assert that a value is null, write `X is null` (`X = null` is null, not true) (same in 1.4, 2.0)
    [src: CQL-1.5.3 09-b-cqlreference > Nullological Operators > IsNull].
- **Case-specific tests** with patient data: read the case's label from the data (for example the
  Patient's given name, `define "Case": First(Patient.name.given)`, converted to a String), and write
  `case "Case" when '01-Active' then <assertion> when '02-Resolved' then <assertion> else true end`.
  A misspelled label silently passes, so check the labels against the test cases.
- **Find test resources by an identifier key, not by `id`**, when the data goes through tools that
  reassign ids (MADiE does on export; see the `madie` skill).

## Test data and fixtures

- **Test functions over resources with test patients**, not with resources built inline. Retrieve
  them as the profiles the measures use, find each by its identifier key, and assert the exact
  result for each case (for a list function, exactly which keys it returns). That runs real data
  through the function, typed as measure logic types it, and through the retrieve
  [src: DQMCMS-739494f .claude/skills/cql/SKILL.md:269-273] [src: DQMCMS-739494f .claude/skills/cql/SKILL.md:307-312].
- **Per case, add only the resources the tests need, plus one near-miss of each kind** (wrong
  status, a code from another code system, outside the period), and **one case with none of the
  resources** the library retrieves, so that empty input is tested too
  [src: DQMCMS-739494f .claude/skills/cql/SKILL.md:169-172].
- **Keep test data valid against its profiles**, including required elements the tests don't read
  (the US Quality Core MedicationAdministrationNotDone and MedicationDispenseDeclined profiles
  require the `us-quality-core-recorded` extension). MADiE rejects invalid resources, and the
  libraries may assume conformant data, so a resource missing a required element (for example a
  MedicationRequest with no status) isn't a case to test
  [src: DQMCMS-739494f .claude/skills/cql/SKILL.md:173-177].
- **Give each resource the profile the logic retrieves** in `meta.profile`. A profile retrieve returns
  exactly the resources whose `meta.profile` declares that profile: not a conforming resource that
  doesn't declare it, and still one that declares it but breaks its fixed values
  [src: PROBES-2026-11-25 RESULTS.md §Profile retrieves and `meta.profile`]. Observed on 5.5.0, and
  on 4.9.0 (the VS Code CQL extension 0.9.8) [src: DQMCMS-739494f .claude/skills/cql/SKILL.md:182-185].
- **Build inline fixtures for values that aren't resources**: codes, intervals, quantities, FHIR
  primitives and data types. Keep the values a test asserts as named definitions (`"Onset Date"`),
  so the fixture and the expected value can't drift apart.
- **One fixture builder per shape, taking every element that varies as a parameter**, with null for
  "absent": `"Test Period"(start, end)`. Each test then reads as one call.
- **Build codings from code systems declared in the test library**, not from the code declarations
  of the library under test: a wrong system or code in the library would otherwise be copied into the
  fixture and the test would still pass. Test the library's declarations separately against
  independently written codes.
- A `Concept { }` selector takes only Code selectors (see [library-syntax.md](library-syntax.md)).

## Covering a function

1. **List every branch** of the function and of what it calls, down to the element: each type of a
   choice element, an element present or absent, every `if` / `case` arm and `Coalesce` fallback, each
   status value that changes the result (including a missing one), and open versus closed null
   boundaries. Note how dependencies treat null: a function using `~` gives false, not null, for a
   missing value.
2. **Write one test per branch**, named `Test<Resource><Function><Branch>`, grouped by function.
3. **Assert the whole result.** For an interval, check its start, end and closedness: a closed null
   boundary means unbounded (`end of` is the maximum value) and an open one unknown (`end of` is null),
   see [intervals.md](intervals.md). For a list of FHIR primitives, compare the System values
   (`L X return X.value`), not the FHIR elements.
4. **Run the function on a retrieve of each profile the measures use**, in a case that has data for
   it, and assert the exact result. An invariant such as
   `AllTrue([Condition] C return C.relevantPeriod() is not null)` alone isn't enough: with no data it
   is vacuously true, so it only shows that the call compiles for that type. A test library whose
   profile tests were all invariants like this passed with no data loaded, comparing `Count({})` with
   `Count({})` [src: DQMCMS-739494f .claude/skills/cql/SKILL.md:307-312]. (Where an invariant is
   still wanted, `AllTrue` is right: it's an invariant over the data, not a combination of tests.)
5. **When a test fails**, decide whether the library or the expected value is wrong before changing
   either, and report what's left uncovered.

## Checking a run

Don't read results by eye. [`scripts/check_test_library.py`](../scripts/check_test_library.py) reads the
library and a run's results, and fails unless every `Test…` is `true` on every case, no case
reported an error, and `_Passed` lists each test exactly once and is `true`. With `--cases`, it also
checks that every label in a `when '<label>' then` clause is a case label, which catches the
misspelled label that would otherwise pass silently. A test commented out of `_Passed` on a line of
its own (`// and TestX`, with the reason) is reported as a known failure, until it starts passing.

```bash
# Execute CQL's results file, or its individual results folder
python3 scripts/check_test_library.py input/cql/MyLibraryTests.cql input/tests/results/MyLibraryTests.txt --cases input/tests/MyLibraryTests
# a cql-mcp cql_test_run_suite run
python3 scripts/check_test_library.py input/cql/MyLibraryTests.cql .cql-debug/test-runs/latest-MyLibraryTests.json --cases input/tests/MyLibraryTests
```

A cql-mcp run's per-case `status` says only whether the case errored, not whether its tests passed,
so check the run with this script too. cql-mcp names a suite's latest run by a hash of the suite, the
library and the patient ids, which a re-run on the same cases repeats; the script reads the newest
run with that hash (see [`scripts/cql_mcp_runs.py`](../scripts/cql_mcp_runs.py)).

## Expected values that surprise

- `start of` / `end of` an open interval give the successor or predecessor, so an open boundary at
  midnight moves to the next or previous day; see [intervals.md](intervals.md).
- `ToDateTime(Date)` takes the evaluation request's timezone offset, so whether a UTC time is on the
  same day depends on where the tests run; keep fixture times well away from day boundaries, or use
  12:00Z when the same day is the point. See [datetime.md](datetime.md).
- A query `return` removes duplicates; use `return all` when the test expects them; see
  [lists-queries.md](lists-queries.md).
- A Boolean test can't assert that an expression raises an error (for example `singleton from` over
  two elements): say in the library's header that the case isn't covered.
- When an engine gives a result the spec doesn't, write the test to the spec, mark it, and keep it out
  of `_Passed` with a comment until the engine is fixed. Report it, with a test, to
  cqframework/cql-tests (see [diagnosing.md](diagnosing.md)).
