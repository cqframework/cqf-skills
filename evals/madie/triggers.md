# madie Skill Trigger Prompts

Prompts for checking when the `madie` skill loads. Run each one in a fresh session with the skill
installed and no other instructions, and record whether the skill loaded.

## Should load the skill

1. MADiE says "Unable to find any valid test case json" when I import my test case zip.
2. What goes in the .madie file in a MADiE test case export?
3. Build a NUMERPass test case bundle I can import into MADiE for my US Quality Core measure.
4. Why did MADiE overwrite the library statement in my measure's CQL?
5. My imported MADiE test cases have no expected values.
6. How do I copy test cases from one MADiE measure to another?
7. Run the test cases I exported from MADiE in VS Code and tell me which ones fail.
8. Package my VS Code test cases so I can import them into MADiE.

## Should not load the skill

1. What does `properly includes` mean for intervals in CQL?
2. How do I run CQL test cases in VS Code?
3. Write the numerator for a CMS measure using CQMCommon.
4. What does the US Core Patient profile require?
5. Create a FHIR Measure resource for my CQL library.
6. Write a FSH profile of Observation.

In the should-not list, prompt 1 belongs to the `cql` skill, prompt 2 to `vscode-cql`, prompt 3 to
`cms-qmd`, prompt 4 to `uscore`, prompt 5 to `crmi` or `cql-ig`, and prompt 6 to `fsh`.
