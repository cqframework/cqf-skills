# US CQL IG Skill Evals

Evaluation cases for the [`us-cql-ig`](../../skills/us-cql-ig/SKILL.md) skill, written against the
Common CQL Artifacts for FHIR (US-Based) IG 2.0.0 (`hl7.fhir.us.cql`) and US Core 6.1.0. When the
skill's pinned version changes, check every answer in the key against the new IG.

| File | Contents |
| --- | --- |
| [questions.md](questions.md) | Questions and one task, given to the agent under test |
| [answers.md](answers.md) | The answer key and pass criteria. Keep it from the agent under test. |
| [grade_elm.py](grade_elm.py) | Grader for the TK-01 library. It reads the ELM JSON that the translator produces. |
| [test_grade_elm.py](test_grade_elm.py) | Tests for the grader, run in CI |
| [reference/](reference/) | A passing TK-01 answer and a flawed one, each with its ELM |
| [triggers.md](triggers.md) | Prompts that should and shouldn't load the skill |

## Running a round

1. **With the skill.** Give an agent a copy of `skills/us-cql-ig/` (no access to `evals/`) and
   `questions.md`. Have it answer each question and save the TK-01 library.
2. **Without the skill.** Give the same questions to the same model with no skill, as a baseline.
3. **Translate TK-01.** Use the CQL-to-ELM translator CLI (`info.cqframework:cql-to-elm-cli`,
   3.29.0 was used for the reference). Put these files in one folder with the agent's library:
   - `FHIRHelpers.cql` and `FHIRCommon.cql` from the `cql-ig` skill's `resources/libraries/`
   - `USCoreCommon.cql` (and `USCoreElements.cql` if used) from this skill's `resources/libraries/`
   - the USCore ModelInfo XML (from the `USCore-ModelInfo` Library in the `hl7.fhir.us.cql`
     package), saved as `uscore-modelinfo-6.1.0-derived.xml`

   The CLI can't resolve namespaced includes, so in the copies, change
   `include hl7.fhir.uv.cql.FHIRHelpers` to `include FHIRHelpers` (and the same for FHIRCommon).
   Then run
   `java -cp "lib/*" org.cqframework.cql.cql2elm.cli.Main --input HypertensionCheck.cql --output out --format JSON`.
   Record the translator's errors and warnings.
4. **Grade.** Run `grade_elm.py` on the ELM. Have a separate agent, or a person, grade the other
   answers against `answers.md` as PASS, PARTIAL or FAIL. Translating any CQL in an answer settles
   most disputes.
5. **Compare.** The skill should pass more questions than the baseline. MD-02 and TK-01 test the
   missing primary code paths, which the IG's own ModelInfo page gets wrong.
6. **Triggers.** Run each prompt in `triggers.md` in a fresh session with the skill installed, and
   record whether it loaded.

Record each round in a dated folder here (`round-YYYY-MM-DD/`) with the answers given and the
grades. Once a round is run, its questions are known, so a held-out round needs new questions
written by someone other than the skill's maintainer.
