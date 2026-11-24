# questionnaire Skill Evals

Evaluation cases for the [`questionnaire`](../../skills/questionnaire/SKILL.md) skill, written against
FHIR R4, SDC 4.0.0 and clinical-reasoning 4.16.0. When the skill is re-pinned, check every answer in the
key against the new version.

| File | Contents |
| --- | --- |
| [questions.md](questions.md) | Questions and one task, given to the agent under test |
| [answers.md](answers.md) | The answer key and pass criteria. Keep it from the agent under test. |
| [grade_questionnaire.py](grade_questionnaire.py) | Grader for the TK-01 files. It checks them statically. |
| [test_grade_questionnaire.py](test_grade_questionnaire.py) | Tests for the grader, run in CI |
| [reference/tk-01/](reference/tk-01/) | A reference answer to TK-01 (synthetic), used by the tests |
| [triggers.md](triggers.md) | Prompts that should and shouldn't load the skill |

## Running a round

1. **With the skill.** Give an agent a copy of `skills/questionnaire/` (no access to `evals/`) and
   `questions.md`. Have it answer each question and save the TK-01 folder.
2. **Without the skill.** Give the same questions to the same model with no skill, as a baseline.
3. **Grade.** Run `python grade_questionnaire.py <answer>/tk-01`. For a full check, run the skill's
   `scripts/sdc/run.sh` on the answer, as `answers.md` describes. Have a separate agent, or a person,
   grade the other answers against `answers.md` as PASS, PARTIAL or FAIL.
4. **Compare.** The skill should pass more questions than the baseline. ST-01, EX-01, EX-04, PO-01 and
   PO-02 are where the skill's original source was wrong; EX-02, EX-03, PO-03 to PO-07 and XT-01 to XT-03
   need the implementation's behavior.
5. **Triggers.** Run each prompt in `triggers.md` in a fresh session with the skill installed, and
   record whether it loaded.

Record each round in a dated folder here (`round-YYYY-MM-DD/`) with the answers given and the grades.
