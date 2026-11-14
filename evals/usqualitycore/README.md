# US Quality Core Skill Evals

Evaluation cases for the [`usqualitycore`](../../skills/usqualitycore/SKILL.md) skill, written
against US Quality Core 0.5.0 (`fhir.onc.us-quality-core`). When the skill's pinned version
changes, check every answer in the key against the new IG.

| File | Contents |
| --- | --- |
| [questions.md](questions.md) | Questions and one task, given to the agent under test |
| [answers.md](answers.md) | The answer key and pass criteria. Keep it from the agent under test. |
| [grade_procedure.py](grade_procedure.py) | Grader for the TK-01 Procedure. Run it with `python grade_procedure.py procedure.json`. |
| [test_grade_procedure.py](test_grade_procedure.py) | Tests for the grader, run in CI |
| [triggers.md](triggers.md) | Prompts that should and shouldn't load the skill |

## Running a round

1. **With the skill.** Give an agent a copy of `skills/usqualitycore/` (no access to `evals/`),
   with the knowledge base built (`bash scripts/build-kb.sh`), and `questions.md`. Have it answer
   each question and save the TK-01 Procedure.
2. **Without the skill.** Give the same questions to the same model with no skill, as a baseline.
3. **Grade.** Run `grade_procedure.py` on each TK-01 Procedure. Have a separate agent, or a
   person, grade the other answers against `answers.md` as PASS, PARTIAL or FAIL. Translate any CQL
   in an answer with the CQL-to-ELM translator and the USQualityCore ModelInfo (see
   `evals/us-cql-ig/README.md` for the setup).
4. **Compare.** The skill should pass more questions than the baseline. CF-01, CQ-01 and CQ-02
   test behaviour that differs from QI-Core and US Core habits.
5. **Triggers.** Run each prompt in `triggers.md` in a fresh session with the skill installed, and
   record whether it loaded.

Record each round in a dated folder here (`round-YYYY-MM-DD/`) with the answers given and the
grades. Once a round is run, its questions are known, so a held-out round needs new questions
written by someone other than the skill's maintainer.
