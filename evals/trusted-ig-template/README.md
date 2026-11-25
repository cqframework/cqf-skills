# trusted-ig-template Skill Evals

Evaluation cases for the [`trusted-ig-template`](../../skills/trusted-ig-template/SKILL.md) skill,
written against the IG Publisher's `trusted-template-rules.md` at 3.0.5 (14 rules), first added in commit
4e7325f (2026-11-18) with 12.
When the skill is re-pinned, check every answer in the key against the new rules.

| File | Contents |
| --- | --- |
| [questions.md](questions.md) | Questions and one task, given to the agent under test |
| [answers.md](answers.md) | The answer key and pass criteria. Keep it from the agent under test. |
| [task/tk-01/](task/tk-01/) | The template to fix in TK-01 (synthetic, with ten planted problems). Give it to the agent. |
| [grade_trusted_ig_template.py](grade_trusted_ig_template.py) | Grader for TK-01. It checks the answer statically, independently of the skill's audit script. |
| [test_grade_trusted_ig_template.py](test_grade_trusted_ig_template.py) | Tests for the grader, run in CI |
| [reference/tk-01/](reference/tk-01/) | A reference answer to TK-01, used by the tests |
| [triggers.md](triggers.md) | Prompts that should and shouldn't load the skill |

## Running a round

1. **With the skill.** Give an agent a copy of `skills/trusted-ig-template/` and of `task/tk-01/` (no
   other access to `evals/`) and `questions.md`. Have it answer each question and save its fixed
   `tk-01/` folder.
2. **Without the skill.** Give the same questions and task to the same model with no skill, as a
   baseline.
3. **Grade.** Run `python grade_trusted_ig_template.py <answer>/tk-01`. Have a separate agent, or a
   person, grade the other answers against `answers.md` as PASS, PARTIAL or FAIL.
4. **Compare.** The skill should pass more questions than the baseline. WL-02, IG-01, PP-01 and NW-01
   depend on Ant and publisher behavior the rules don't spell out (all confirmed by the skill's probes);
   TH-01 and TH-03 depend on how the publisher decides trust.
5. **Triggers.** Run each prompt in `triggers.md` in a fresh session with the skill installed, and
   record whether it loaded.

Record each round in a dated folder here (`round-YYYY-MM-DD/`) with the answers given and the grades.
