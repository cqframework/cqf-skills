# Contributing to CQF Skills

Thanks for helping. This guide covers how to author a skill and what reviewers look for.

## Adding a skill

1. Open an issue that describes the skill: the tasks it handles, two or three example prompts, and the spec versions it targets.
2. Copy `template/` to `skills/<skill-name>/`. The folder name must equal the `name` in the frontmatter.
3. Write `SKILL.md`, plus any `references/`, `scripts/`, or `assets/` it needs.
4. Add eval cases under `evals/<skill-name>/` (see [Evals](#evals)).
5. Add the skill path (`./skills/<skill-name>`) to the right plugin in `.claude-plugin/marketplace.json`.
6. Run `python scripts/validate_skills.py`, then open a PR. Update the catalog table in `README.md` and `CHANGELOG.md`.

## Listing a plugin maintained elsewhere

Some skills belong with the tool they describe and are maintained in that tool's repository (for
example `cql-mcp`). Don't copy them here. Instead, add a `marketplace.json` entry whose `source` is
`{"source": "github", "repo": "<owner>/<repo>", "ref": "<release tag>", "sha": "<commit>"}` and that
declares the repository's `skills` path, plus any `mcpServers`. Pin both `ref` and `sha` to a
release. When the upstream project releases, update the tag, the commit, any versioned URLs (such
as a server package URL) and `version` together in one change.

## Authoring guidelines

### Frontmatter

- `name`: lowercase letters, digits, and hyphens; at most 64 characters; no leading, trailing, or doubled hyphens. Use a domain prefix where it helps (`cql-`, `fhir-`, `ig-`).
- `description`: at most 1024 characters, in the third person. State **what** the skill does and **when** to use it, including the keywords, file types (`.cql`, `.fsh`, `sushi-config.yaml`), and resource or operation names a user would mention. This is the only text the agent sees before it decides to load the skill.
- `license`: `Apache-2.0`.

### Body

- Keep `SKILL.md` under about 500 lines. Put detailed material in `references/*.md` and link to it directly from `SKILL.md`. Links go one level deep, with no reference-to-reference chains.
- Give longer reference files a table of contents at the top.
- Write for a capable model. Leave out general explanations of FHIR or CQL and spend the words on conventions, edge cases, tooling behavior, and decision criteria.
- Prefer procedures and checklists over narrative. Show at least one small, correct example of the target output.
- State the specification and tool versions the guidance assumes. Link to the canonical spec page (cql.hl7.org, hl7.org/fhir, …) instead of copying spec text.
- Use forward slashes in paths. Avoid time-sensitive phrasing ("the new version").

### Scripts

- Scripts must be deterministic, non-interactive, and print clear errors. Document required runtimes (Java, Node, Python) and versions at the top of the script and in `SKILL.md`.
- Don't download or execute remote code at run time. If a tool must be fetched (for example the IG Publisher jar), have the script tell the user how to install it.
- Scripts must not send data to external services, except for terminology or FHIR servers the user has configured explicitly.

### Self-containment

A skill must work when its folder is copied on its own. Don't link to files outside the skill folder. If two skills need the same reference, duplicate it, or split it out into its own skill.

When several skills carry a copy of the same file, such as the profile converter that `crmi` and `cpg` both use, list its path in `SHARED_FILES` in `scripts/validate_skills.py`. The validator fails if the copies differ, so a fix made in one copy has to be copied to the others.

### Data

All examples, fixtures, and test data must be **synthetic**. Never include PHI or real patient data. When a skill references licensed terminologies (SNOMED CT, CPT, and so on), use only codes that are permitted in examples, or illustrative codes that are clearly marked as such.

## Evals

Each skill needs evaluation cases under `evals/<skill-name>/` that show the skill improves results compared with the same agent without it. A case is a realistic prompt, any input files, and the expected outcome or grading criteria (for example, "the CQL translates without errors", "the measure evaluates to the expected population counts").

Include:

- **Positive trigger** prompts that should load the skill.
- **Negative trigger** prompts in nearby domains that should *not* load it.
- **Task** cases with checkable outputs.

## Versioning and releases

- The repository uses semantic versioning. The marketplace version is in `.claude-plugin/marketplace.json` under `metadata.version`.
- Record every change to a skill's behavior in `CHANGELOG.md` under the affected skill.
- Releases are tagged `vX.Y.Z` and include a zip for each skill.

## Review checklist

- [ ] `python scripts/validate_skills.py` passes
- [ ] The description says what the skill does and when to use it
- [ ] `SKILL.md` is under about 500 lines and references are one level deep
- [ ] Target spec and tool versions are stated
- [ ] Examples are correct (the CQL translates, the FSH compiles, the resources validate)
- [ ] Evals are included, and they pass with the skill and do measurably worse without it
- [ ] No PHI and no files referenced outside the skill folder
- [ ] The skill is added to `marketplace.json`, the README catalog, and `CHANGELOG.md`
