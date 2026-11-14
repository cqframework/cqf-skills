# CQL IG Skill Evals

Evaluation cases for the [`cql-ig`](../../skills/cql-ig/SKILL.md) skill, written against Using CQL
With FHIR 2.0.0 (`hl7.fhir.uv.cql`) for FHIR R4. When the skill's pinned version changes, check
every answer in the key against the new IG.

| File | Contents |
| --- | --- |
| [questions.md](questions.md) | Questions and one task, given to the agent under test |
| [answers.md](answers.md) | The answer key and pass criteria. Keep it from the agent under test. |
| [grade_library.py](grade_library.py) | Grader for the TK-01 Library. Run it with `python grade_library.py library.json`. |
| [test_grade_library.py](test_grade_library.py) | Tests for the grader, run in CI |
| [reference/](reference/) | The TK-01 CQL and a Library that passes the grader |
| [triggers.md](triggers.md) | Prompts that should and shouldn't load the skill |

## Running a round

1. **With the skill.** Give an agent a copy of `skills/cql-ig/` (no access to `evals/`), with the
   knowledge base built (`bash scripts/build-kb.sh`), and `questions.md`. Have it answer each
   question and save the TK-01 Library.
2. **Without the skill.** Give the same questions to the same model with no skill, as a baseline.
3. **Grade.** Run `grade_library.py` on each TK-01 Library. Have a separate agent, or a person,
   grade the other answers against `answers.md` as PASS, PARTIAL or FAIL. Where an answer contains
   CQL, translating it with the CQL-to-ELM translator settles most disputes.
4. **Compare.** The skill should pass more questions than the baseline. CF-01, CF-03 and TK-01
   test requirements that the IG's own examples don't follow, and LK-01 tests that FHIRHelpers
   is now published by this IG rather than CQF Common.
5. **Triggers.** Run each prompt in `triggers.md` in a fresh session with the skill installed, and
   record whether it loaded.

Record each round in a dated folder here (`round-YYYY-MM-DD/`) with the answers given and the
grades. Once a round is run, its questions are known, so a held-out round needs new questions
written by someone other than the skill's maintainer.
