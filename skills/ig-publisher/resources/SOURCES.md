# Sources

Registry of every source the skill's resource files cite. Cite a claim inline as
`[src: ID locator]`. The locator form depends on how the source is held:

- **Git-backed** (no local copy): `path:line[-line]` at the pinned ref, for example
  `[src: IGPUB-3.0.4 org.hl7.fhir.publisher.core/…/PublisherIGLoader.java:199]`. A `…` elides the
  middle of a path; the rest must match one file.
- **Local copy** (maintainers' copy of a published file): a file under the local copy folder, with an optional `#Lnn[-Lmm]` line anchor, for
  example `[src: TPL-BASE-1.0.0 scripts/onLoad.xslt#L265]`.
- **The IG parameters CodeSystem**: `CodeSystem-ig-parameters.json#<code>`, for example
  `[src: TOOLS-1.3.0 CodeSystem-ig-parameters.json#path-binary]`.

| ID | Kind | Status | Version | Pinned locator | Published URL | Local copy | Retrieved |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TOOLS-1.3.0 | package | informative | hl7.fhir.uv.tools 1.3.0, FHIR Tooling IG Release 1.3 (Informative), generated 2026-10-06; still the latest on 2026-11-14 | hl7.fhir.uv.tools#1.3.0 | <https://hl7.org/fhir/tools/en/> | `resources/sources/tools-1.3.0/` | 2026-11-14 |
| TOOLS-PAGES-1.3.0 | guide | informative | The tools IG's narrative pages (`input/pagecontent/`) at the inferred 1.3.0 build commit | FHIR/fhir-tools-ig@360be1883136300beee3ec3aca190c1bac54e8ad | <https://hl7.org/fhir/tools/en/> | `resources/sources/tools-pages-1.3.0/` | 2026-11-14 |
| IGPUB-3.0.4 | implementation-source | n/a | IG Publisher 3.0.4, released 2026-11-14, commit 7b7ccec6ce503cbb10e81469d8356532c939bb9f | HL7/fhir-ig-publisher@3.0.4 | <https://github.com/HL7/fhir-ig-publisher/tree/3.0.4> | none (git show 3.0.4:PATH; the fetch script caches a clone) | 2026-11-14 |
| IGPUB-DOCS-3.0.4 | guide | informative | the repository's markdown documentation at 3.0.4 | HL7/fhir-ig-publisher@3.0.4 | <https://github.com/HL7/fhir-ig-publisher/blob/3.0.4/documentation.md> | `resources/sources/igpub-docs-3.0.4/` | 2026-11-14 |
| CORE-7.0.6 | implementation-source | n/a | org.hl7.fhir.core 7.0.6, the core library IG Publisher 3.0.4 builds against | hapifhir/org.hl7.fhir.core@7.0.6 | <https://github.com/hapifhir/org.hl7.fhir.core/tree/7.0.6> | none (git show 7.0.6:PATH; the fetch script caches a clone) | 2026-11-14 |
| TPL-CQF-1.0.0 | package | n/a | cqf.fhir.template 1.0.0 (2025-09-30), base fhir.base.template 1.0.0 | cqf.fhir.template#1.0.0 | <https://packages.fhir.org/cqf.fhir.template/1.0.0> | `resources/sources/tpl-cqf-1.0.0/` | 2026-11-14 |
| TPL-BASE-1.0.0 | package | n/a | fhir.base.template 1.0.0 (2025-09-30) | fhir.base.template#1.0.0 | <https://packages.fhir.org/fhir.base.template/1.0.0> | `resources/sources/tpl-base-1.0.0/` | 2026-11-14 |
| SAMPLE-IG | convention | n/a | FHIR/sample-ig commit 74c54cd (2026-11-01) | FHIR/sample-ig@74c54cd5ffdf02b4ac96b32fb45ef1929bfc4963 | <https://github.com/FHIR/sample-ig> | `resources/sources/sample-ig/` | 2026-11-14 |
| VSCQL | implementation-source | n/a | vscode-cql 1.0.0, released 2026-11-09, commit 855eac7b5f21c788d0e0e856d741cadc35e6bda9 | cqframework/vscode-cql@v1.0.0 | <https://github.com/cqframework/vscode-cql> | none (local checkout; see scripts/lint_skill_igpub.py) | 2026-11-14 |
| EX-DQM-CMS-2025 | convention | n/a | dqm-content-cms-2025 commit 46b11c3 on branch consolidated-parity-fixes; publisher version used is unknown | raleigh-g-thompson/dqm-content-cms-2025@46b11c350448dca2974e144d49726512f70f88b2 | none | none (local checkout; see scripts/lint_skill_igpub.py) | 2026-10-22 |
| PROBES-2026-10-22 | observed-behavior | n/a | IG Publisher 3.0.1 jar (sha256 2862e545…7ecc) run on a copy of EX-DQM-CMS-2025 at 46b11c3, tx.fhir.org | `resources/probes/2026-10-22/` | none | `resources/probes/2026-10-22/` | 2026-10-22 |
| PROBES-2026-11-14 | observed-behavior | n/a | IG Publisher 3.0.4 jar (sha256 361b8aa8…e059) run on a copy of EX-DQM-CMS-2025 at 46b11c3 with its template set to `cqf.fhir.template#1.0.0`, tx.fhir.org | `resources/probes/2026-11-14/` | none | `resources/probes/2026-11-14/` | 2026-11-14 |

## Looking up a citation at another version

No local copy is needed to check a claim. Every pinned source is published online, and a citation
names the exact file and lines, so the same place can be read at the pinned version or at the
version an IG was actually built with:

| Source | URL for a citation at version `<v>` |
| --- | --- |
| IGPUB, IGPUB-DOCS | `https://github.com/HL7/fhir-ig-publisher/blob/<v>/<path>#L<a>-L<b>` (tags are the version numbers) |
| CORE | `https://github.com/hapifhir/org.hl7.fhir.core/blob/<v>/<path>#L<a>-L<b>`. The core version a publisher release builds against is `core_version` in that release's root `pom.xml` |
| TPL-CQF, TPL-BASE, TOOLS | `https://packages.fhir.org/<package>/<v>` (a `.tgz`); template files sit at the tarball root, the tools IG's resources under `package/` |
| TOOLS-PAGES, SAMPLE-IG | `https://github.com/FHIR/fhir-tools-ig/blob/<commit>/input/pagecontent/<file>`, `https://github.com/FHIR/sample-ig/blob/<commit>/<path>` |

Line numbers move between releases, so at another version, find the cited code by its content near
the cited lines rather than trusting the numbers. The CQL translator version a publisher release uses
is `info_cqframework_version` in its `org.hl7.fhir.publisher.core/pom.xml`.

**Cited files.** A `…` in a git locator elides the middle of the path. The full paths, which the
URLs need:

| Source | Path |
| --- | --- |
| CORE | `org.hl7.fhir.convertors/src/main/java/org/hl7/fhir/convertors/conv40_50/resources40_50/ImplementationGuide40_50.java` |
| CORE | `org.hl7.fhir.utilities/src/main/java/org/hl7/fhir/utilities/PathBuilder.java` |
| CORE | `org.hl7.fhir.r5/src/main/java/org/hl7/fhir/r5/model/Enumerations.java` |
| CORE | `org.hl7.fhir.utilities/src/main/java/org/hl7/fhir/utilities/npm/NpmPackage.java` |
| CORE | `org.hl7.fhir.services/src/main/java/org/hl7/fhir/services/renderers/RendererFactory.java` |
| CORE | `org.hl7.fhir.utilities/src/main/java/org/hl7/fhir/utilities/settings/FhirSettings.java` |
| CORE | `org.hl7.fhir.utilities/src/main/java/org/hl7/fhir/utilities/settings/FhirSettingsPOJO.java` |
| IGPUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/CliParams.java` |
| IGPUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/CqlSubSystem.java` |
| IGPUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/FSHRunner.java` |
| IGPUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/IGPublisherLiquidTemplateServices.java` |
| IGPUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/Publisher.java` |
| IGPUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/PublisherBase.java` |
| IGPUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/PublisherFields.java` |
| IGPUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/PublisherGenerator.java` |
| IGPUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/PublisherIGLoader.java` |
| IGPUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/PublisherProcessor.java` |
| IGPUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/R4ToR4BAnalyser.java` |
| IGPUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/SuppressedMessageInformation.java` |
| IGPUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/templates/TemplateManager.java` |
| IGPUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/comparators/PreviousVersionComparator.java` |
| IGPUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/loaders/AdjunctFileLoader.java` |
| IGPUB | `org.hl7.fhir.publisher.core/pom.xml` |
| IGPUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/renderers/ValidationPresenter.java` |
| IGPUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/templates/Template.java` |
| IGPUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/web/PublicationProcess.java` |
| IGPUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/web/WebSourceProvider.java` |

## Notes

- **Local copies are for maintenance.** The skill doesn't need them to answer a question (see above).
  The linter and the generator for `ig-parameters.md` do.
- **Rebuild.** `scripts/fetch-sources.sh` rebuilds every local copy from these locators, unmodified,
  and caches shallow clones of IGPUB-3.0.4 and CORE-7.0.6 under `~/.cache/ig-publisher-skill/` (or `$IGPUB_SKILL_CACHE`). Nothing under `resources/sources/` except its README is committed.
  Binary assets (images, jars, package indexes) are not copied. See
  [sources/README.md](sources/README.md).
- **What each kind is evidence of.** TOOLS-1.3.0 says what a parameter or extension is *meant* to do.
  IGPUB-3.0.4 and CORE-7.0.6 show what the publisher *does* at that version: evidence of behaviour, not
  of intent. TPL-CQF-1.0.0 and TPL-BASE-1.0.0 show what a template *adds or removes*. SAMPLE-IG and
  EX-DQM-CMS-2025 show what one IG *configures*, never what is required.
- **IGPUB-DOCS-3.0.4 is stale.** Its `documentation.md` lists command-line parameters that don't
  match `Publisher.java` at the same tag. Prefer IGPUB-3.0.4 for behaviour.
- **EX-DQM-CMS-2025's publisher version can't be determined.** The checkout has no `out/qa.*` and no
  `input-cache/publisher.jar`, and its `_updatePublisher.sh` downloads `releases/latest`, so each
  build uses whichever release was current when the script last ran.
- **TOOLS-PAGES-1.3.0's commit is inferred, not stated.** The 1.3.0 package names no source commit.
  360be18 is the one used because its message is "set up 1.3.0 release" (2026-10-05), it is the
  repository head with no later commits, the package was built 2026-10-06, and its
  `input/resources/codesystem-ig-parameters.xml` gives exactly the package's 137 codes with identical
  definitions. The repository has no release tags.
- **Not used as sources.** The Confluence "IG Publisher Documentation" pages
  (<https://confluence.hl7.org/display/FHIR/IG+Publisher+Documentation>) can't be pinned, and
  `confluence.hl7.org` returns a human-verification page to scripted requests. build.fhir.org HTML is
  a moving CI build. Both are pointers only, never cited.
- **Re-pinned 2026-11-14.** The skill was written against IG Publisher 3.0.1, org.hl7.fhir.core 7.0.2,
  cqf.fhir.template 0.7.1 and fhir.base.template 0.8.1. Every line citation was moved to the new pins by
  finding the cited text again; 423 of 455 were unchanged, and the rest were checked by hand. The
  3.0.1 to 3.0.4 and 0.8.1 to 1.0.0 differences that change a claim are noted where they apply.
  PROBES-2026-10-22 records 3.0.1 behaviour and is cited only as that.
