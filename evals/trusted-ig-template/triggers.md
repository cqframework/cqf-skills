# trusted-ig-template Skill Trigger Prompts

Prompts for checking when the `trusted-ig-template` skill loads. Run each one in a fresh session with
the skill installed and no other instructions, and record whether it loaded.

## Should load the skill

1. Review this change to our IG template's `scripts/ant.xml` against the trusted template rules.
2. Why won't the ci-build run my template's ant scripts? It says the template is not trusted.
3. Can our template's onGenerate target pass the IG version to a jar?
4. Add a pre-process transform to fhir.base.template that adds anchors to headings.
5. What does `otherScripts` in a template's config.json do?
6. Is it safe for the cqf.fhir.template to download schemas in onGenerate?

## Should not load the skill

1. Build my IG with the IG Publisher and explain the QA errors.
2. Set the `path-liquid` parameter for my IG.
3. Write a FSH profile of Patient.
4. Write a Liquid template that renders a Library's narrative.
5. Pin the publisher's terminology server in ig.ini.

Prompts 1, 2 and 5 of the should-not list belong to the `ig-publisher` skill, prompt 3 to `fsh`, and
prompt 4 to `ig-publisher` (Liquid narratives).
