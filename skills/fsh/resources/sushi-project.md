# SUSHI Projects

How a FSH project is laid out and configured for SUSHI, the reference FSH compiler. Checked with
SUSHI 3.21.0, which implements FSH 3.0.0. Full documentation: <https://fshschool.org/docs/sushi/>.

## Running SUSHI

SUSHI is the npm package `fsh-sushi` and needs Node.js.

```sh
npx fsh-sushi@3 build .           # run without installing
npm install -g fsh-sushi          # or install the `sushi` command
sushi build .                     # compile the project in the current folder
sushi init                        # create a new project interactively
sushi update-dependencies .       # move dependencies in sushi-config.yaml to their latest versions
```

The first build downloads FHIR core and each dependency into the FHIR package cache
(`~/.fhir/packages`), so it needs network access. The run ends with a count of errors and
warnings. Read every error: SUSHI skips the rule that failed and still writes the rest, so the
output can look complete when it isn't.

## Layout

```text
my-ig/
├── sushi-config.yaml
├── input/
│   ├── fsh/                 FSH source, any number of .fsh files, any subfolders
│   ├── pagecontent/         narrative pages for the IG Publisher (index.md, ...)
│   └── includes/menu.xml    optional; otherwise SUSHI builds the menu from sushi-config.yaml
└── fsh-generated/           SUSHI output; regenerated on every build, don't edit
    └── resources/           one JSON file per item, named {ResourceType}-{id}.json
```

SUSHI reads every `.fsh` file under `input/fsh/`. How items are split across files doesn't
matter: aliases, rule sets and items are visible project-wide.

## sushi-config.yaml

To generate IG content, SUSHI requires `canonical`, `fhirVersion`, `id`, `name` and `status`.

```yaml
id: example.fhir.myig                 # package id
canonical: http://example.org/fhir/myig
name: MyIG
title: My Implementation Guide
status: draft
version: 0.1.0
fhirVersion: 4.0.1                    # R4
copyrightYear: 2026+                  # wanted by the HL7 IG Publisher
releaseLabel: ci-build                # wanted by the HL7 IG Publisher
dependencies:
  hl7.fhir.uv.extensions.r4: 5.2.0    # package id: version
pages:
  index.md:
    title: Home
```

- **canonical** is the base of every generated URL: a profile with `Id: my-patient` gets
  `{canonical}/StructureDefinition/my-patient`.
- **dependencies** makes another package's profiles, extensions and value sets resolvable by name,
  id or URL. Each needs an exact version. A package that isn't listed can still be referred to
  by canonical URL, but SUSHI can't check it or look inside it.
- **FSHOnly: true** compiles only the FSH items, with no ImplementationGuide resource. Then only
  `canonical` and `fhirVersion` are required, which suits quick checks of FSH outside an IG.

SUSHI writes `fsh-generated/resources/ImplementationGuide-{id}.json` from this file, and the HL7
IG Publisher reads it from there.
