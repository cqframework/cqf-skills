# plan-definition Skill Evals

Evaluation cases for the [`plan-definition`](../../skills/plan-definition/SKILL.md) skill, written
against FHIR R4, CPG 2.0.0 and clinical-reasoning 4.13.0. When the skill is re-pinned, check every answer
in the key against the new version.

| File | Contents |
| --- | --- |
| [questions.md](questions.md) | Questions and one task, given to the agent under test |
| [answers.md](answers.md) | The answer key and pass criteria. Keep it from the agent under test. |
| [grade_plandefinition.py](grade_plandefinition.py) | Grader for the TK-01 files. It checks them statically. |
| [test_grade_plandefinition.py](test_grade_plandefinition.py) | Tests for the grader, run in CI |
| [reference/tk-01/](reference/tk-01/) | A reference answer to TK-01 (synthetic), used by the tests |
| [triggers.md](triggers.md) | Prompts that should and shouldn't load the skill |

## Running a round

1. **With the skill.** Give an agent a copy of `skills/plan-definition/` (no access to `evals/`) and
   `questions.md`. Have it answer each question and save the TK-01 folder.
2. **Without the skill.** Give the same questions to the same model with no skill, as a baseline.
3. **Grade.** Run `python grade_plandefinition.py <answer>/tk-01`. For a full check, run the skill's
   `scripts/apply/run.sh` on the answer for each test patient, as `answers.md` describes. Have a separate
   agent, or a person, grade the other answers against `answers.md` as PASS, PARTIAL or FAIL.
4. **Compare.** The skill should pass more questions than the baseline. EX-01, BE-02, DV-01, AP-01, AP-02
   and TR-01 are where the skill's original source was wrong; EX-02, EX-03, CO-01, AP-04, AD-01 and AD-02
   need the implementation's code.
5. **Triggers.** Run each prompt in `triggers.md` in a fresh session with the skill installed, and
   record whether it loaded.

Record each round in a dated folder here (`round-YYYY-MM-DD/`) with the answers given and the grades.
