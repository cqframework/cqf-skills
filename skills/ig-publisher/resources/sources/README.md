# Local Copies of Pinned Sources

Everything in this directory except this README is written by `scripts/fetch-sources.sh` from the
pinned locators in [../SOURCES.md](../SOURCES.md), and is not committed. The skill doesn't need
these copies to answer questions, because every source is published online (see SOURCES.md); the
linter and `gen_ig_parameters.py` use them. The files are byte-for-byte copies; don't edit them.
To re-pin, change the script, re-run it, then update `SOURCES.md` and re-run
`scripts/gen_ig_parameters.py`.

Each folder has a `REF` file holding the locator it was fetched from.

| Folder | Source ID | What was copied |
| --- | --- | --- |
| `tools-1.3.0/` | TOOLS-1.3.0 | Every JSON resource at the root of the `hl7.fhir.uv.tools#1.3.0` package, and its `package.json`. The package's `xml/` duplicates and `other/` folder are skipped. |
| `igpub-docs-3.0.5/` | IGPUB-DOCS-3.0.5 | `README.md`, `documentation.md`, `multi-version-IGs.md`, `multi-lingual-IGs.md` and `hta-copyright-rules.md` from HL7/fhir-ig-publisher at tag 3.0.4. |
| `tpl-cqf-1.0.0/` | TPL-CQF-1.0.0 | The text files of `cqf.fhir.template#1.0.0`. Images and the package index are skipped. |
| `tpl-base-1.0.0/` | TPL-BASE-1.0.0 | The text files of `fhir.base.template#1.0.0`, including `config.json` and `scripts/onLoad.xslt`. `plantuml.jar`, images and the package index are skipped. |
| `sample-ig/` | SAMPLE-IG | `ig.ini`, `package-list.json`, the IG resource (`input/myig.xml`), `input/ignoreWarnings.txt`, `input/includes/menu.xml`, the `input/cql/` sources, `input/examples/Library-example.json`, `_genonce.sh`, `_genonce.bat`, `_updatePublisher.sh` and `README.md` from FHIR/sample-ig at 74c54cd. |

The FHIR resources here are upstream artifacts, kept as evidence. They are not this skill's examples
and are not meant to be loaded into an IG.
