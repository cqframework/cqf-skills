# IG Publisher Skill Evals

Evaluation cases for the [`ig-publisher`](../../skills/ig-publisher/SKILL.md) skill, written against
IG Publisher 3.0.4 with cqf.fhir.template 1.0.0. When the skill is re-pinned, check every answer in
the key against the new versions; several answers (CQ-01, CQ-04, RN-03, TX-01, TP-01, VR-01) are about
version differences.

| File | Contents |
| --- | --- |
| [questions.md](questions.md) | Questions, a debugging case and one task, given to the agent under test |
| [answers.md](answers.md) | The answer key and pass criteria. Keep it from the agent under test. |
| [grade_ig.py](grade_ig.py) | Grader for the TK-01 project. It checks the files statically. |
| [test_grade_ig.py](test_grade_ig.py) | Tests for the grader, run in CI |
| [reference/tk-01/](reference/tk-01/) | A reference answer to TK-01 (synthetic), used by the tests |
| [triggers.md](triggers.md) | Prompts that should and shouldn't load the skill |

## Running a round

1. **With the skill.** Give an agent a copy of `skills/ig-publisher/` (no access to `evals/`) and
   `questions.md`; `scripts/fetch-sources.sh` doesn't need to have been run. Have it answer each
   question and save the TK-01 project. It may run the publisher and read GitHub.
2. **Without the skill.** Give the same questions to the same model with no skill, as a baseline.
3. **Grade.** For each TK-01 project, run `python grade_ig.py <project>`. For a full check, build it
   with IG Publisher 3.0.4 (`java -jar publisher.jar -ig <project> -tx n/a -no-errors`, about a
   minute) and confirm `output/Library-ExampleScreening.json` has ELM content. Have a separate agent,
   or a person, grade the other answers against `answers.md` as PASS, PARTIAL or FAIL.
4. **Compare.** The skill should pass more questions than the baseline. CQ-03, CQ-05, RN-02, TX-02
   and TP-01 test behaviour that is easy to get wrong without reading the publisher's source.
5. **Triggers.** Run each prompt in `triggers.md` in a fresh session with the skill installed, and
   record whether it loaded.

Record each round in a dated folder here (`round-YYYY-MM-DD/`) with the answers given and the
grades. Once a round is run, its questions are known, so a held-out round needs new questions
written by someone other than the skill's maintainer.
