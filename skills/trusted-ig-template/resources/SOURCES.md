# Sources

Registry of every source the skill's resource files cite. Cite a claim inline as
`[src: ID locator]`:

- the rules, or IG Publisher code, by path and lines at the pinned commit:
  `[src: PUB-4e7325f trusted-template-rules.md:26]`,
  `[src: PUB-4e7325f …/templates/TemplateManager.java:222-243]` (a `…` elides the middle of a path; full
  paths are listed below);
- the FHIR core library, the same way: `[src: CORE-7.0.6 …/xml/XMLUtil.java:527-532]`;
- the probe runs: `[src: PROBES-2026-11-17 RESULTS.md §1]`.

| ID | Kind | Status | Version | Pinned locator | Published URL | Local copy | Retrieved |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PUB-4e7325f | implementation-source | n/a | HL7 FHIR IG Publisher at the commit that added `trusted-template-rules.md` (2026-11-18 AEDT), 3.0.4 plus five commits; its template code matches 3.0.4 except that `.po` files became harmless | HL7/fhir-ig-publisher@4e7325f81566f341f7a3b38ed1e581a4275ae04e | <https://github.com/HL7/fhir-ig-publisher/blob/4e7325f81566f341f7a3b38ed1e581a4275ae04e/trusted-template-rules.md> | none (the fetch script caches a clone) | 2026-11-17 |
| CORE-7.0.6 | implementation-source | n/a | org.hl7.fhir.core 7.0.6, the core library IG Publisher 3.0.4 uses | hapifhir/org.hl7.fhir.core@86bf796ddc97083551c20d113aeda0e5db4f8a25 | <https://github.com/hapifhir/org.hl7.fhir.core/tree/7.0.6> | none (the fetch script caches a clone) | 2026-11-17 |
| PROBES-2026-11-17 | observed-behavior | n/a | Ant 1.10.18 (the publisher's version) and OpenJDK 21.0.9's XSLT processor, set up as the publisher sets them up | `resources/probes/2026-11-17/` | none | `resources/probes/2026-11-17/` | 2026-11-17 |

## Reading a citation

| Source | URL |
| --- | --- |
| PUB-4e7325f | `https://github.com/HL7/fhir-ig-publisher/blob/4e7325f81566f341f7a3b38ed1e581a4275ae04e/<path>#L<a>-L<b>` |
| CORE-7.0.6 | `https://github.com/hapifhir/org.hl7.fhir.core/blob/7.0.6/<path>#L<a>-L<b>` |

For a newer publisher, read the same file on `master` or at its release tag and find the code by its
content near the cited lines. The rules file is at the root of the repository.

**Cited files.** The full paths behind each `…`:

| Source | Path |
| --- | --- |
| PUB | `trusted-template-rules.md` |
| PUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/templates/TemplateManager.java` |
| PUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/templates/Template.java` |
| PUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/Publisher.java` |
| PUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/PublisherIGLoader.java` |
| PUB | `org.hl7.fhir.publisher.core/src/main/java/org/hl7/fhir/igtools/publisher/XSLTransformer.java` |
| PUB | `pom.xml` |
| CORE | `org.hl7.fhir.utilities/src/main/java/org/hl7/fhir/utilities/xml/XMLUtil.java` |
