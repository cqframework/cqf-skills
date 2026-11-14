# vscode-cql Skill Trigger Prompts

Prompts for checking when the `vscode-cql` skill loads. Run each one in a fresh session with the skill
installed and no other instructions, and record whether the skill loaded.

## Should load the skill

1. The CQL Explorer doesn't show up in VS Code. How do I get it back?
2. How do I set the Measurement Period when I run CQL test cases in VS Code?
3. Execute CQL says it can't find my value set, but the file is in input/vocabulary.
4. Where does the CQL extension write test results?
5. How do I debug a CQL library against one test patient in VS Code?
6. The CQL language server won't start: "Java 17 or more recent is required".
7. How do I use a locally built cql-language-server JAR with the extension?

## Should not load the skill

1. What does `properly includes` mean for intervals in CQL?
2. Configure path-binary so the IG Publisher compiles my CQL.
3. Write a FHIR Library resource for a CQL library.
4. Install the Python extension in VS Code.
5. How do I write a CMS measure's numerator in CQL?
6. Write a FSH profile of Observation.

In the should-not list, prompt 1 belongs to the `cql` skill, prompt 2 to `ig-publisher`, prompt 3 to
`cql-ig`, prompt 5 to `cms-qmd` and prompt 6 to `fsh`.
