# CPG Skill Evals

Evaluation cases for the [`cpg`](../../skills/cpg/SKILL.md) skill, written against CPG 2.0.0 and
FHIR Extensions (R4) 5.4.0. When the skill's pinned versions change, check every answer in the key
against the new KB.

| File | Contents |
| --- | --- |
| [questions.md](questions.md) | Questions and one task, given to the agent under test |
| [answers.md](answers.md) | The answer key and pass criteria. Keep it from the agent under test. |
| [grade_plandefinition.py](grade_plandefinition.py) | Grader for the TK-01 PlanDefinition. Run it with `python grade_plandefinition.py plandefinition.json`. |
| [test_grade_plandefinition.py](test_grade_plandefinition.py) | Tests for the grader, run in CI |
| [triggers.md](triggers.md) | Prompts that should and shouldn't load the skill |

## Running a round

1. **With the skill.** Give an agent a copy of `skills/cpg/` (no access to `evals/`), with the KB
   built (`bash scripts/build-kb.sh`), and `questions.md`. Have it answer each question and save
   the TK-01 PlanDefinition.
2. **Without the skill.** Give the same questions to the same model with no skill, as a baseline.
3. **Grade.** Run `grade_plandefinition.py` on each TK-01 PlanDefinition. Have a separate agent, or
   a person, grade the other answers against `answers.md` as PASS, PARTIAL or FAIL.
4. **Compare.** The skill should pass more questions than the baseline. VR-01 tests the change from
   CPG 1.0.0 that memory gets wrong.
5. **Triggers.** Run each prompt in `triggers.md` in a fresh session with the skill installed, and
   record whether it loaded.

Record each round in a dated folder here (`round-YYYY-MM-DD/`) with the answers given and the
grades. Once a round is run, its questions are known, so a held-out round needs new questions
written by someone other than the skill's maintainer.
