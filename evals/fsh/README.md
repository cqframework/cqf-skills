# FSH Skill Evals

Evaluation cases for the [`fsh`](../../skills/fsh/SKILL.md) skill, written against FHIR Shorthand
3.0.0 and SUSHI 3.21.0 for FHIR R4. When the skill's pinned FSH version changes, check every
answer in the key against the new spec.

| File | Contents |
| --- | --- |
| [questions.md](questions.md) | Questions, a debugging case and one task, given to the agent under test |
| [answers.md](answers.md) | The answer key and pass criteria. Keep it from the agent under test. |
| [grade_bp.py](grade_bp.py) | Grader for the TK-01 project. It reads the JSON that SUSHI generates. |
| [test_grade_bp.py](test_grade_bp.py) | Tests for the grader, run in CI |
| [reference/](reference/) | A reference answer to TK-01 and the SUSHI output it compiles to, used by the tests |
| [triggers.md](triggers.md) | Prompts that should and shouldn't load the skill |

## Running a round

1. **With the skill.** Give an agent a copy of `skills/fsh/` (no access to `evals/`) and
   `questions.md`. Have it answer each question and save the TK-01 project. It may run SUSHI.
2. **Without the skill.** Give the same questions to the same model with no skill, as a baseline.
3. **Grade.** For each TK-01 project, run SUSHI (`npx fsh-sushi@3.21.0 build <project>`), record
   the error count, then run `python grade_bp.py <project>/fsh-generated/resources`. Have a
   separate agent, or a person, grade the other answers against `answers.md` as PASS, PARTIAL or
   FAIL. Compiling each FSH answer with SUSHI settles most disputes.
4. **Compare.** The skill should pass more questions than the baseline. SY-03 and DB-01 test
   mistakes that SUSHI rejects but that look plausible.
5. **Triggers.** Run each prompt in `triggers.md` in a fresh session with the skill installed, and
   record whether it loaded.

Record each round in a dated folder here (`round-YYYY-MM-DD/`) with the answers given and the
grades. Once a round is run, its questions are known, so a held-out round needs new questions
written by someone other than the skill's maintainer.
