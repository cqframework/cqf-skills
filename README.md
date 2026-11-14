# CQF Skills

Open source [Agent Skills](https://agentskills.io) for working with **CQL**, **FHIR**, **FHIR Clinical Reasoning**, and **FHIR content Implementation Guides**, maintained by the [Clinical Quality Framework](https://github.com/cqframework) community.

Skills are folders of instructions, references, and scripts that an AI agent loads on demand when a task calls for them. These skills teach agents to author, review, test, and package clinical knowledge artifacts (CQL libraries, measures, PlanDefinitions, and the IGs that publish them) using the conventions of the HL7 and CQF specifications and tooling.

The skills follow the open Agent Skills format, so they work in Claude Code, Claude.ai, the Claude API, and other agents that support `SKILL.md`.

> **Status:** early development. Skills are being brought in from other repositories one at a time.

## Skill catalog

Skills are grouped into **plugins** by domain (`cql`, `fhir`, `clinical-reasoning`, `fhir-ig`), so you can install only the ones you need. Some plugins are maintained in their own repositories and listed here so they can be installed from one marketplace.

| Plugin | Skill | Purpose |
|---|---|---|
| `cql` | [`cql`](skills/cql/SKILL.md) | Author, review and debug CQL libraries, and answer semantics questions from the CQL 1.4, 1.5.3 and 2.0.0 spec text, with documented translator and engine gotchas. Run `bash skills/cql/scripts/fetch-spec.sh` once to build the local spec copy. |
| `fhir` | [`fhir`](skills/fhir/SKILL.md) | Work with FHIR R4 resources and bundles: bundle types, transaction entries, resource IDs, `meta.profile`, references and terminology system URIs, with element, cardinality and binding tables for the base R4 resources and data types. |
| `fhir` | [`fhir-extensions`](skills/fhir-extensions/SKILL.md) | Find and apply standard R4 extensions from the FHIR Extensions Pack 5.4.0: canonical URLs, value types, where each may be used, and which are draft or deprecated and what replaces them. Run `bash skills/fhir-extensions/scripts/build-kb.sh` once to build the local knowledge base. |
| `clinical-reasoning` | [`crmi`](skills/crmi/SKILL.md) | Choose and apply CRMI 2.0.0 shareable, publishable, computable and executable profiles, and look up artifact lifecycle and packaging operations such as `$package`, with the `cqf-` and `artifact-` extensions (FHIR Extensions R4 5.4.0). Run `bash skills/crmi/scripts/build-kb.sh` once to build the local knowledge base. |
| `clinical-reasoning` | [`cpg`](skills/cpg/SKILL.md) | Choose and apply CPG 2.0.0 profiles for computable guidelines: recommendation, strategy and pathway definitions, computable activities, case features and metrics, with the `cqf-` extensions they use. Run `bash skills/cpg/scripts/build-kb.sh` once to build the local knowledge base. |
| `fhir-ig` | [`fsh`](skills/fsh/SKILL.md) | Write and debug FHIR Shorthand (FSH 3.0.0) for SUSHI: profiles, extensions, value sets, code systems, instances, rule sets and slicing, with the FSH language reference and the mistakes SUSHI rejects. |
| `cql-mcp` | [`cql-mcp`](https://github.com/cqframework/cql-mcp/blob/v0.1.0-rc.2/skills/cql-mcp/SKILL.md) | The [cql-mcp](https://github.com/cqframework/cql-mcp) server and its usage skill: validate and run CQL, inspect ELM, run and diff test-case suites, and debug step by step. Maintained in cqframework/cql-mcp and pinned to a release. Requires Node.js 22+ and JDK 17+. |

## Installation

### Claude Code

This repository is a Claude Code plugin marketplace.

```text
/plugin marketplace add cqframework/cqf-skills
/plugin install cql@cqf-skills
/plugin install fhir@cqf-skills
/plugin install clinical-reasoning@cqf-skills
/plugin install cql-mcp@cqf-skills
```

To pick up new releases, run `/plugin marketplace update cqf-skills`.

Installing `cql-mcp` installs its skill and registers the cql-mcp server, with the workspace set to the project directory you start Claude Code from. The server needs Node.js 22+ and a JDK 17+. On first use it downloads the server package and the CQL language server, so the first start can be slow. If you already registered cql-mcp yourself with `claude mcp add`, remove that registration to avoid running two servers.

### Other agents that support Agent Skills

Each folder under [`skills/`](skills/) is self-contained. Copy or symlink the ones you want into your agent's skills directory, for example:

```bash
git clone https://github.com/cqframework/cqf-skills.git
cp -r cqf-skills/skills/cql ~/.claude/skills/        # Claude Code (personal)
cp -r cqf-skills/skills/cql .claude/skills/          # Claude Code (project)
cp -r cqf-skills/skills/cql .agents/skills/          # agents that use .agents/skills
```

Check your agent's documentation for the exact location it reads skills from.

Plugins maintained elsewhere aren't under `skills/`. For `cql-mcp`, set up the server for your client by following the [cql-mcp install guide](https://github.com/cqframework/cql-mcp#install-and-configure), and get the skill from the `cql-mcp-skill.zip` attached to each [cql-mcp release](https://github.com/cqframework/cql-mcp/releases).

### Claude.ai and the Claude API

Zip a skill folder (the zip must contain the folder itself, not just its contents). Then upload it under **Settings → Capabilities → Skills** on Claude.ai, or through the Skills API. Each [release](https://github.com/cqframework/cqf-skills/releases) attaches prebuilt zips.

## Repository layout

```text
cqf-skills/
├── .claude-plugin/
│   └── marketplace.json        # Claude Code marketplace: defines plugins as groups of skills
├── skills/                     # One folder per skill; the folder name is the skill name
│   └── <skill-name>/
│       ├── SKILL.md            # Required: YAML frontmatter + instructions
│       ├── references/         # Optional: detail loaded only when needed
│       ├── scripts/            # Optional: deterministic helpers the agent runs
│       └── assets/             # Optional: templates and files copied into output
├── evals/                      # Evaluation cases per skill (not shipped with the skill)
│   └── <skill-name>/
├── template/
│   └── SKILL.md                # Starting point for new skills
├── scripts/
│   └── validate_skills.py      # Lint: frontmatter, naming, marketplace consistency
├── .github/workflows/
│   └── validate.yml            # CI: runs the validator on every PR
├── AGENTS.md                   # Instructions for agents contributing to this repo
├── CONTRIBUTING.md             # Authoring guidelines and review checklist
├── CHANGELOG.md
└── LICENSE                     # Apache-2.0
```

Skills sit in a single flat `skills/` directory rather than nested under plugins. This keeps every skill installable on its own with any Agent Skills–compatible tool. The plugin groupings live only in `marketplace.json`.

## Anatomy of a skill

```markdown
---
name: cql-authoring
description: Writes and reviews CQL libraries targeting FHIR, following CQL
  authoring conventions. Use when creating or editing .cql files, defining
  retrieves, value set and code declarations, or measure population criteria.
license: Apache-2.0
---

# CQL Authoring

## Workflow
1. ...

## References
- For the FHIRHelpers and QICore model conventions, see [references/models.md](references/models.md).
```

- **`name`**: lowercase letters, digits, and hyphens; at most 64 characters; must match the folder name.
- **`description`**: at most 1024 characters, written in the third person. It must say *what the skill does* and *when to use it*. Agents decide whether to load a skill from its description alone.
- **Body**: keep it under about 500 lines. Move detail into `references/` and link to it one level deep, so the agent loads it only when it needs it (progressive disclosure).

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full authoring guidelines.

## Design principles

1. **Specification-grounded.** Guidance follows the published HL7 specifications ([CQL](https://cql.hl7.org), [Using CQL with FHIR](https://hl7.org/fhir/uv/cql/), [CRMI](https://hl7.org/fhir/uv/crmi/), [CPG](https://hl7.org/fhir/uv/cpg/), [Quality Measures](https://hl7.org/fhir/us/cqfmeasures/), [SDC](https://hl7.org/fhir/uv/sdc/)). Skills link to the canonical spec rather than copying it, and note which version they target.
2. **Teach what the model doesn't already know.** Skip general FHIR or programming background. Focus on conventions, pitfalls, tooling behavior, and decision points.
3. **Tooling-aware, not tooling-locked.** Prefer the CQF reference tooling (the [CQL translator](https://github.com/cqframework/clinical_quality_language), the [Clinical Reasoning engine](https://github.com/cqframework/clinical-reasoning), and the IG Publisher). Keep the guidance usable without any particular agent or IDE.
4. **Deterministic where possible.** When a step can be scripted (validation, translation, packaging), ship a script instead of prose.
5. **Self-contained.** A skill must not reference files outside its own folder, because each skill can be installed on its own.
6. **Evaluated.** Every skill ships with eval cases under `evals/<skill-name>/` that show it improves agent results on realistic tasks.
7. **No PHI.** Examples and test data must be synthetic.

## Contributing

Contributions are welcome, especially from implementers with hands-on CQL, measure, and IG experience. Read [CONTRIBUTING.md](CONTRIBUTING.md), start from [`template/SKILL.md`](template/SKILL.md), and run the validator before you open a PR:

```bash
pip install pyyaml
python scripts/validate_skills.py
```

To propose a new skill, open an issue that describes the tasks it should handle and two or three example prompts.

## Related projects

- [cqframework/clinical_quality_language](https://github.com/cqframework/clinical_quality_language): CQL specification tooling, translator, and engine
- [cqframework/clinical-reasoning](https://github.com/cqframework/clinical-reasoning): FHIR Clinical Reasoning operations (measure evaluation, `$apply`, `$package`)
- [cqframework/vscode-cql](https://github.com/cqframework/vscode-cql): CQL support for VS Code

## License

[Apache License 2.0](LICENSE). Unless otherwise noted, each skill is also licensed under Apache-2.0, as declared in its `SKILL.md` frontmatter.

HL7®, FHIR®, and the FHIR flame logo are registered trademarks of Health Level Seven International.
