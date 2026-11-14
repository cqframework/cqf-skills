# CMS QMD Skill Evals

Evaluation cases for the [`cms-qmd`](../../skills/cms-qmd/SKILL.md) skill, written against the CMS
FHIR Quality Measure Development IG at the skill's pinned commit (3 November 2026) and US Quality
Core 0.5.0. When the pin changes, check every answer in the key against the new IG.

| File | Contents |
| --- | --- |
| [questions.md](questions.md) | Questions and one task, given to the agent under test |
| [answers.md](answers.md) | The answer key and pass criteria. Keep it from the agent under test. |
| [grade_elm.py](grade_elm.py) | Grader for the TK-01 library. It reads the ELM JSON that the translator produces. |
| [test_grade_elm.py](test_grade_elm.py) | Tests for the grader, run in CI |
| [reference/](reference/) | A passing TK-01 answer and a flawed one, each with its ELM |
| [triggers.md](triggers.md) | Prompts that should and shouldn't load the skill |

## Running a round

1. **With the skill.** Give an agent a copy of `skills/cms-qmd/` (no access to `evals/`) and
   `questions.md`. Have it answer each question and save the TK-01 library.
2. **Without the skill.** Give the same questions to the same model with no skill, as a baseline.
3. **Translate TK-01.** Use the CQL-to-ELM translator CLI (3.29.0 was used for the reference), as
   described in `evals/us-cql-ig/README.md`, with these files in one folder:
   - FHIRHelpers and FHIRCommon (`cql-ig`), USCoreCommon (`us-cql-ig`), and any CMS QMD libraries
     the answer includes (this skill's `resources/libraries/`)
   - the USCore and USQualityCore ModelInfo XML, saved as `uscore-modelinfo-6.1.0-derived.xml` and
     `usqualitycore-modelinfo-0.5.0.xml`

   Rewrite namespaced includes (`include hl7.fhir.uv.cql.FHIRHelpers`, and so on) without the
   namespace in the copies, because the CLI can't resolve them.
4. **Grade.** Run `grade_elm.py` on the ELM. Have a separate agent, or a person, grade the other
   answers against `answers.md` as PASS, PARTIAL or FAIL.
5. **Compare.** The skill should pass more questions than the baseline. ML-01, ML-02 and TK-01
   test unqualified types, which translate silently to base FHIR.
6. **Triggers.** Run each prompt in `triggers.md` in a fresh session with the skill installed, and
   record whether it loaded.

Record each round in a dated folder here (`round-YYYY-MM-DD/`) with the answers given and the
grades. Once a round is run, its questions are known, so a held-out round needs new questions
written by someone other than the skill's maintainer.
