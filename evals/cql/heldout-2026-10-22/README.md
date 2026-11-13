# Held-Out Question Round, 2026-10-22

Eight questions written and graded independently of the session that maintains the skill, to check
that the skill generalises beyond its own test set ([../questions.md](../questions.md)). The round
is spent: its questions and key are now known, so a future held-out round needs new questions,
written by someone other than the skill's maintainer.

| File | Contents |
| --- | --- |
| [questions.md](questions.md) | The eight questions (HO-1 to HO-8) |
| [answers.md](answers.md) | The key used for grading, amended after the answers and before grading |
| [answers.v1-before-amendment.md](answers.v1-before-amendment.md) | The key as first written |
| [answers-given.md](answers-given.md) | The answering agent's answers |
| [grades.md](grades.md) | The grades: 8 PASS, 0 PARTIAL, 0 FAIL |
| [probes/](probes/) | The key writer's probe libraries |

How it ran:

- The answering agent had a copy of the skill without `evals/`, and could not run CQL.
- A separate agent graded the answers against the amended key.
- The key's amendment added two findings the answering agent made: the 1.4 ELM `Combine` text,
  and the CQL-TESTS `SubstringEmptyAnd0` inconsistency. The amendment note at the top of
  [answers.md](answers.md) gives the detail.

The engine results these questions left open were then probed in the skill's own record,
`resources/probes/2026-10-22/RESULTS.md` §53 to §59, and folded into the topic files. The files
here are kept as they were written; paths inside them refer to the original working folders.
