# Probe results, 2026-11-24

Run with clinical-reasoning **4.16.0** (`org.opencds.cqf.fhir:cqf-fhir-cr`, which brings the CQL
translator and engine 5.7.0 and HAPI FHIR 9.0.0), through `scripts/apply/run.sh`, and compared with
the same runs on 4.13.0. All data is synthetic.

## 1. The 2026-11-14 probes, again

Every run recorded in [../2026-11-14/RESULTS.md](../2026-11-14/RESULTS.md), on that folder's project,
with both versions:

| Run | 4.16.0 compared with 4.13.0 |
| --- | --- |
| `plan probe Patient/adult-1` (§1, §2) | identical |
| `plan two-libs Patient/adult-1` (§3) | identical: with no `reference`, `Is Adult` is still resolved against ExampleRules, the first declared |
| `r5 probe Patient/adult-1` (§4) | identical |
| `activity order-test Patient/adult-1` (§5) | identical |
| `activity send-message Patient/adult-1` | identical |

Timestamps and generated UUIDs were ignored in the comparison. Everything the 2026-11-14 record
describes holds for 4.16.0.

In 4.16.0 the libraries are held in an insertion-ordered map: `PlanDefinition.library` in declaration
order, then any `cqf-library` extensions. So "the first library" is now the first one declared, by
construction rather than by chance.

## 2. Questionnaire items for action inputs, `$r5.apply`

The project in this folder: `input/resources/` holds four Observation profiles (`probe-observation` and
`probe-observation-2` to `-4`, each requiring `effective[x]` and a Quantity `value[x]`) and
`PlanDefinition/inputs`; `input/tests/` holds `Patient/adult-1`. `inputs` has three actions, each with
`input` data requirements naming profiles:

| Action | `input` profiles |
| --- | --- |
| `one-input` | `probe-observation` |
| `two-inputs` | `probe-observation-2`, `probe-observation-3` |
| `repeat-and-new` | `probe-observation` (again), `probe-observation-4` |

`run.sh . r5 inputs Patient/adult-1` returns a Questionnaire `inputs` in the Bundle. Its items, by
`linkId`, `type` and `text`:

| 4.13.0 | 4.16.0 |
| --- | --- |
| `1` group `ProbeObservation` (children `1.1`, `1.2`) | `1` group `ProbeObservation` (children `1.1`, `1.2`) |
| `2` group `Probe Observation 2` (`2.1`, `2.2`) | `2` group **`Two inputs`**, the action's title, holding `2.1` group `Probe Observation 2` (`2.1.1`, `2.1.2`) and `2.2` group `Probe Observation 3` (`2.2.1`, `2.2.2`) |
| `3` group `Probe Observation 3` (`3.1`, `3.2`) | `3` group `Probe Observation 4` (`3.1`, `3.2`) |
| `4` group `Probe Observation 4` (`4.1`, `4.2`) | |

- One item per input profile, as a group named after the profile, with a child per required element.
- A profile already in the Questionnaire isn't added again: `repeat-and-new` adds only
  `probe-observation-4`.
- **New in 4.16.0:** when one action adds more than one item, they're wrapped in a group whose text is
  the action's title (or its description), and their linkIds are renumbered under it (`2.1`, `2.1.1`…).
  An action that adds one item adds it as before, so `repeat-and-new` isn't grouped.
- `plan inputs Patient/adult-1` (R4 `$apply`) returns a CarePlan with no Questionnaire: the items are
  generated only by `$r5.apply`.
