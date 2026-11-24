# Probe results, 2026-11-24

Run with clinical-reasoning **4.16.0** (`org.opencds.cqf.fhir:cqf-fhir-cr`, which brings the CQL
translator and engine 5.7.0 and HAPI FHIR 9.0.0), through `scripts/sdc/run.sh`, on the project in
[../2026-11-14/](../2026-11-14/RESULTS.md), and compared with the same runs on 4.13.0. Timestamps and
generated UUIDs were ignored in the comparison.

## 1. The 2026-11-14 probes, again

| Run | 4.16.0 compared with 4.13.0 |
| --- | --- |
| `populate pop Patient/adult-1`, with and without `patient=Patient/adult-1` (§1, §2) | identical |
| `populate no-lib Patient/adult-1`, with and without `patient=Patient/adult-1` (§2, §3) | identical |
| `populate ref Patient/adult-1`, alone, with `patient=Patient/child-1`, and with `encounter=Encounter/enc-1` (§2, §5) | identical |
| `populate two-libs Patient/adult-1`, with and without `patient=Patient/adult-1` (§4) | **one answer differs**: see §2 below |
| `extract extract-1` … `extract-4`, `extract-noq` (§6) | identical results and errors (extract-1's serialization error lists the allowed Observation value types in another order) |
| `generate probe-observation` (§7) | identical |

Everything else the 2026-11-14 record describes holds for 4.16.0.

## 2. Questionnaire/two-libs: library selection

`two-libs` has `cqf-library` PopRules then OtherRules; both define `"Given Name"`.

| Item | Expression | 4.13.0 | 4.16.0 |
| --- | --- | --- | --- |
| `noref` | `text/cql-identifier` `Given Name`, no `reference` | `From OtherRules` | **`Ada`** (PopRules) |
| `ref-other` | the same, `reference` = OtherRules | `From OtherRules` | `From OtherRules` |
| `qualified-expr` | `text/cql-expression` `OtherRules."Given Name"` | `From OtherRules` | `From OtherRules` |
| `qualified-expr-pop` | `text/cql-expression` `PopRules."Given Name"` | `Ada` | `Ada` |

With no `reference`, 4.16.0 uses PopRules, the first library declared. In 4.13.0 the `cqf-library`
libraries were collected into an unordered map, and that run happened to use the second; 4.16.0 collects
them in declaration order, so the first declared is used every time.
