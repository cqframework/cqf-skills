# FSH Skill Test Questions: Answer Key

Expected answers for [questions.md](questions.md). Don't give this file to an agent under test.

Facts come from the FSH 3.0.0 specification, as rendered in the `fsh` skill's
`resources/spec/` (a source written as `20-rules-assignment.md` is the file of that name there).
Each FSH answer below was compiled with SUSHI 3.21.0 against FHIR R4 (4.0.1) with no errors. Each
answer gives the expected facts, the source, what a passing answer must and must not say, and
where the skill covers it ("Skill").

An answer fails if its FSH would not compile, or compiles to something other than what was asked.
Equivalent FSH that compiles to the same result passes, for example a different local name or
alias.

## Syntax

### SY-01. Assigning a code in a profile

- **Expected:** In a profile, `=` sets `patternCodeableConcept` on `Observation.code`: the coding
  must be present, and other codings and text may appear too. `* code = http://loinc.org#85354-9
  (exactly)` sets `fixedCodeableConcept` instead, which forbids anything not specified. The spec
  says `(exactly)` is generally not the best option for interoperability, because it can reject
  valid data.
- **Source:** `20-rules-assignment.md` (Assignment Rules, the Note on `pattern[x]` and
  `fixed[x]`).
- **Pass if:** it says pattern by default, gives `(exactly)` for fixed, and cautions against it.
- **Fail if:** it says `=` produces `fixed[x]`, or that `(exactly)` is needed for the code to be
  required to match.
- **Skill:** `SKILL.md` Rules that are easy to get wrong ("`=` in a profile is a pattern").

### SY-02. Several reference targets

- **Expected:** `* subject only Reference(Patient or Group)`.
- **Source:** `03-language-basics.md` (References), `33-rules-type.md`.
- **Pass if:** both targets are inside one `Reference()`.
- **Fail if:** it writes `Reference(Patient) or Reference(Group)`, which SUSHI rejects ("No
  definition for the type "Patient)" could be found").
- **Skill:** `SKILL.md` Rules that are easy to get wrong.

### SY-03. A standard extension in a profile

- **Expected:**

  ```
  * extension contains http://hl7.org/fhir/StructureDefinition/patient-birthPlace named birthPlace 0..1 MS
  ```

  and in the instance `* extension[birthPlace].valueAddress.city = "Lisbon"`.
- **Source:** `23-rules-contains-rules-for-extensions.md`, `04-paths.md` (Extension Paths).
- **Pass if:** the rule uses `contains ... named ...` with `0..1 MS`, and the instance addresses the
  extension by its local name (or its URL) with `valueAddress`.
- **Fail if:** it omits `named` (SUSHI: "Inline extensions should only be defined in
  Extensions"), or sets the city with a string value rather than an Address.
- **Skill:** `SKILL.md` Rules that are easy to get wrong ("Extensions in profiles need `named`").

### SY-04. Repeating elements in an instance

- **Expected:**

  ```
  * name[+].given = "Ana"
  * name[=].family = "Silva"
  * name[+].given = "Ana"
  * name[=].family = "Souza"
  ```

- **Source:** `04-paths.md` (Array Paths using Soft Indexing).
- **Pass if:** it uses `[+]` to start each name and `[=]` to stay on it, giving two names.
- **Fail if:** it uses `[+]` on both rules of a name, which creates four names.
- **Skill:** `SKILL.md` Rules that are easy to get wrong ("Soft indexing").

### SY-05. A comma in a rule set argument

- **Expected:** `* insert Note(one\, two (draft\))`, escaping the comma and the closing
  parenthesis, or `* insert Note([[one, two (draft)]])`.
- **Source:** `28-rules-insert.md` (Inserting Parameterized Rule Sets).
- **Pass if:** the comma and closing parenthesis are escaped with a backslash, or the argument is in
  `[[ ]]`.
- **Fail if:** the comma is unescaped (SUSHI reads two arguments), or the opening parenthesis is
  escaped too.
- **Skill:** `SKILL.md` Rules that are easy to get wrong ("Escape rule set arguments").

### SY-06. Instance usage

- **Expected:** `Usage: #definition`, because a SearchParameter is a formal item of the IG, not an
  example. The default is `#example`.
- **Source:** `09-items-instances.md`.
- **Pass if:** `#definition`, and the default `#example`.
- **Skill:** `SKILL.md` Rules that are easy to get wrong ("Instances default to `Usage:
  #example`").

### SY-07. A FHIRPath extension context

- **Expected:**

  ```
  Extension: AssertedBy
  Id: asserted-by
  Context: "(Condition | Observation).code"
  ```

  A quoted `Context` value gives a `fhirpath` context. `Context` is trial use in FSH 3.0.0.
- **Source:** `08-items-extensions.md`.
- **Pass if:** the context is a quoted FHIRPath expression on the `Context` keyword, or an
  equivalent `^context` caret rule with type `fhirpath`.
- **Fail if:** the expression is unquoted. SUSHI then reads it as an element context and fails
  ("Could not find resource (Condition to use as extension context").
- **Skill:** `SKILL.md` Rules that are easy to get wrong ("Give extensions a `Context:`").

## Debugging

### DB-01. A SUSHI build with errors

- **Expected:** three problems.
  1. `extension contains ReviewedBy 0..1` has no `named`, so it is read as an inline extension,
     which profiles can't have. Fix: `* extension contains ReviewedBy named reviewedBy 0..1`.
  2. `component` has no slicing logic before `contains`, so SUSHI can't create the slice ("No
     slicing found for Observation.component"), and then skips the `component[systolic]` rules.
     Fix: add `^slicing.discriminator.type = #pattern`, `^slicing.discriminator.path = "code"` and
     `^slicing.rules = #open` on `component` before the `contains` rule.
  3. `Reference(Patient) or Reference(Group)` must be `Reference(Patient or Group)`.
- **Source:** `23-rules-contains-rules-for-extensions.md`, `24-rules-contains-rules-for-slicing.md`,
  `03-language-basics.md` (References).
- **Pass if:** it finds and fixes all three.
- **Partial if:** it finds two.
- **Skill:** `SKILL.md` Rules that are easy to get wrong.

## Tasks

### TK-01. A blood pressure profile

Run SUSHI on the agent's project, then grade the output with [grade_bp.py](grade_bp.py):
`python grade_bp.py path/to/fsh-generated/resources`. Read the FSH as well.

- **Script checks** (each must pass):
  - SUSHI wrote the code system, value set, extension, profile and example instance with the
    requested ids.
  - The code system has `auto` and `manual`, and the value set includes the code system.
  - The extension has an Observation context, its `value[x]` is a Reference to Practitioner, and
    `extension` is `0..0`.
  - The profile is of Observation; `code` has LOINC `85354-9`; `subject` is `1..1` and targets
    Patient only; `method` is `1..1` with a required binding to the value set.
  - The extension is a `0..1` must-support slice whose type is the `reviewed-by` profile.
  - `component` is sliced on `code`, with slices of `1..1` whose codes are `8480-6` and `8462-4`,
    each with a `Quantity` value in UCUM `mm[Hg]`.
  - The example claims the profile, with 120 and 80 mm[Hg] in the systolic and diastolic
    components.
- **Fail if:** SUSHI reports errors, or the script fails.
- **Skill:** `SKILL.md` Workflow, Rules that are easy to get wrong;
  `resources/sushi-project.md`.
