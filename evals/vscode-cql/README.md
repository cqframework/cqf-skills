# vscode-cql Skill Evals

Evaluation cases for the [`vscode-cql`](../../skills/vscode-cql/SKILL.md) skill, written against
vscode-cql 1.0.0 and cql-language-server 5.0.0. When the skill is re-pinned, check every answer in the
key against the new versions.

| File | Contents |
| --- | --- |
| [questions.md](questions.md) | Questions and one task, given to the agent under test |
| [answers.md](answers.md) | The answer key and pass criteria. Keep it from the agent under test. |
| [grade_project.py](grade_project.py) | Grader for the TK-01 project. It checks the files statically. |
| [test_grade_project.py](test_grade_project.py) | Tests for the grader, run in CI |
| [reference/tk-01/](reference/tk-01/) | A reference answer to TK-01 (synthetic), used by the tests |
| [triggers.md](triggers.md) | Prompts that should and shouldn't load the skill |

## Running a round

1. **With the skill.** Give an agent a copy of `skills/vscode-cql/` (no access to `evals/`) and
   `questions.md`. Have it answer each question and save the TK-01 project. It may read GitHub.
2. **Without the skill.** Give the same questions to the same model with no skill, as a baseline. It
   may read the project wiki, which is where most wrong answers come from.
3. **Grade.** Run `python grade_project.py <project>` on each TK-01 answer. For a full check, open it
   in VS Code with the extension, run Execute CQL on `WeightCheck.cql` and confirm the result files and
   parameter sources. Have a separate agent, or a person, grade the other answers against
   `answers.md` as PASS, PARTIAL or FAIL.
4. **Compare.** The skill should pass more questions than the baseline. PL-02, PL-03, CF-02, PA-01,
   TE-01, LR-03 and DB-01 are where the wiki or the old summary is wrong.
5. **Triggers.** Run each prompt in `triggers.md` in a fresh session with the skill installed, and
   record whether it loaded.

Record each round in a dated folder here (`round-YYYY-MM-DD/`) with the answers given and the grades.
Once a round is run, its questions are known, so a held-out round needs new questions written by
someone other than the skill's maintainer.
