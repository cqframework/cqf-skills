# madie Skill Evals

Evaluation cases for the [`madie`](../../skills/madie/SKILL.md) skill, written against MADiE `develop`
as of 2026-11-14. When the skill is re-pinned, check every answer in the key against the new code.

| File | Contents |
| --- | --- |
| [questions.md](questions.md) | Questions and one task, given to the agent under test |
| [answers.md](answers.md) | The answer key and pass criteria. Keep it from the agent under test. |
| [grade_testcases.py](grade_testcases.py) | Grader for the TK-01 test cases. It checks the files statically. |
| [test_grade_testcases.py](test_grade_testcases.py) | Tests for the grader, run in CI |
| [reference/tk-01/](reference/tk-01/) | A reference answer to TK-01 (synthetic), used by the tests |
| [triggers.md](triggers.md) | Prompts that should and shouldn't load the skill |

## Running a round

1. **With the skill.** Give an agent a copy of `skills/madie/` (no access to `evals/`) and
   `questions.md`. Have it answer each question and save the TK-01 folder. It may read GitHub.
2. **Without the skill.** Give the same questions to the same model with no skill, as a baseline.
3. **Grade.** Run `python grade_testcases.py <answer>/tk-01` on each TK-01 answer. For a full check,
   zip the folder's contents and import it into a MADiE measure set up as the task describes, then
   confirm three test cases are created with the expected values and that they pass when run. Have a
   separate agent, or a person, grade the other answers against `answers.md` as PASS, PARTIAL or FAIL.
4. **Compare.** The skill should pass more questions than the baseline. ZP-02, EX-03, RS-01 and RS-02
   are where the skill's original source was wrong; IM-01, IM-03, IM-04, IM-05 and CQ-04 need MADiE's
   code.
5. **Triggers.** Run each prompt in `triggers.md` in a fresh session with the skill installed, and
   record whether it loaded.

Record each round in a dated folder here (`round-YYYY-MM-DD/`) with the answers given and the grades.
Once a round is run, its questions are known, so a held-out round needs new questions written by
someone other than the skill's maintainer.
