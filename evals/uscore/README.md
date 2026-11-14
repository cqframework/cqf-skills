# US Core Skill Evals

Evaluation cases for the [`uscore`](../../skills/uscore/SKILL.md) skill, written against US Core
6.1.0 and 9.0.0 (`hl7.fhir.us.core`). When the skill's pinned versions change, check every answer
in the key against the new packages.

| File | Contents |
| --- | --- |
| [questions.md](questions.md) | Questions and one task, given to the agent under test |
| [answers.md](answers.md) | The answer key and pass criteria. Keep it from the agent under test. |
| [grade_patient.py](grade_patient.py) | Grader for the TK-01 Patient. Run it with `python grade_patient.py patient.json`. |
| [test_grade_patient.py](test_grade_patient.py) | Tests for the grader, run in CI |
| [triggers.md](triggers.md) | Prompts that should and shouldn't load the skill |

## Running a round

1. **With the skill.** Give an agent a copy of `skills/uscore/` (no access to `evals/`), with the
   knowledge base built (`bash scripts/build-kb.sh`), and `questions.md`. Have it answer each
   question and save the TK-01 Patient.
2. **Without the skill.** Give the same questions to the same model with no skill, as a baseline.
3. **Grade.** Run `grade_patient.py` on each TK-01 Patient. Have a separate agent, or a person,
   grade the other answers against `answers.md` as PASS, PARTIAL or FAIL.
4. **Compare.** The skill should pass more questions than the baseline. LK-02, LK-03, VR-01 and
   TK-01 test the 9.0.0 Patient changes, which memory of 6.1.0 or earlier gets wrong.
5. **Triggers.** Run each prompt in `triggers.md` in a fresh session with the skill installed, and
   record whether it loaded.

Record each round in a dated folder here (`round-YYYY-MM-DD/`) with the answers given and the
grades. Once a round is run, its questions are known, so a held-out round needs new questions
written by someone other than the skill's maintainer.
