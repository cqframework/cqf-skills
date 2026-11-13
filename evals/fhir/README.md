# FHIR Skill Evals

Evaluation cases for the [`fhir`](../../skills/fhir/SKILL.md) skill.

| File | Contents |
| --- | --- |
| [questions.md](questions.md) | Questions and one task, given to the agent under test |
| [answers.md](answers.md) | The answer key and pass criteria. Keep it from the agent under test. |
| [grade_bundle.py](grade_bundle.py) | Grader for the TK-01 bundle. Run it with `python grade_bundle.py bundle.json`. |
| [test_grade_bundle.py](test_grade_bundle.py) | Tests for the grader, run in CI |
| [triggers.md](triggers.md) | Prompts that should and shouldn't load the skill |

## Running a round

1. **With the skill.** Give an agent a copy of `skills/fhir/` (no access to `evals/`) and
   `questions.md`. Have it answer each question and save the TK-01 bundle.
2. **Without the skill.** Give the same questions to the same model with no skill, as a baseline.
3. **Grade.** Run `grade_bundle.py` on each TK-01 bundle. Have a separate agent, or a person, grade
   the other answers against `answers.md` as PASS, PARTIAL or FAIL.
4. **Compare.** The skill should pass more questions than the baseline. A failure that the key
   marks as a skill gap (BD-02 at present) is a change to make in the skill, not a grading error.
5. **Triggers.** Run each prompt in `triggers.md` in a fresh session with the skill installed, and
   record whether it loaded.

Record each round in a dated folder here (`round-YYYY-MM-DD/`) with the answers given and the
grades, as `evals/cql/heldout-2026-10-22/` does. Once a round is run, its questions are known, so
a held-out round needs new questions written by someone other than the skill's maintainer.
