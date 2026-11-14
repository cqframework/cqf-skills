# CMS FHIR Quality Measure Development IG (0.8.0-cibuild): Pages

The narrative pages of the IG, from [cqframework/cms-qmd](https://github.com/cqframework/cms-qmd/tree/9bcc541e1ca4e12488fbca4e108727108be8c1aa/input/pagecontent) at commit `9bcc541` (the continuous build of 2026-11-03). Published at <https://build.fhir.org/ig/cqframework/cms-qmd/>. The IG declares its content CC0-1.0; the repository is Apache-2.0.

| File | Page | Sections |
| --- | --- | --- |
| [index.md](index.md) | Home | Summary |
| [measure_guidance.md](measure_guidance.md) | CMS Measure Authoring Guidance | CMS Measure Authoring Guidance, CMS FHIR-based CQL Style Guide |
| [test_case_guidance.md](test_case_guidance.md) | CMS Test Case Guidance | CMS Test Case Guidance, dQM Test Case Recommendations |
| [patterns.md](patterns.md) | Authoring Patterns | Authoring Patterns, Model Overview, Pattern Overview |
| [pattern_fhir.md](pattern_fhir.md) | FHIR Patterns | FHIR Patterns, Element cardinality, Must support elements, Modifier elements, Authoring against the US Quality Core model, Accessing data, References, Use of terminologies, Terminology Functions, Interval Calculations, Further considerations |
| [pattern_layers.md](pattern_layers.md) | Logic Layers | Logic Layers, Logic Layers, Choosing the Layer, Library Organization, Fluent Function Guidance |
| [pattern_index.md](pattern_index.md) | Pattern Index | Pattern Index, Overall, Patient, Allergies and intolerances, Conditions, Encounters, Observations, Services and procedures, Medications, Devices, Immunizations, Communication, Claims and coverage, Billing-related elements |
| [pattern_patient.md](pattern_patient.md) | Patient | Patient, Patient age, Patient race and ethnicity |
| [pattern_encounters.md](pattern_encounters.md) | Encounters | Encounters, Office visit encounters, Accessing Encounters with a Direct-reference code, Encounters by class, Completed encounters in a period, Encounters with a certain length, Reason for Visit, Evidence of Diagnosis during an Encounter, Present on Admission, Principal Diagnosis, Primary Procedure,  |
| [pattern_observations.md](pattern_observations.md) | Observations | Observations, Vital Signs, Pregnancy Status, Pregnancy Intent, Smoking Status, Laboratory Result, Clinical Result, Surveys and Assessments, Simple Observations, Observations Not Done, Observations Non-Patient |
| [pattern_conditions.md](pattern_conditions.md) | Conditions | Conditions, Active conditions, Verified Conditions, Encounters with a condition, History of a condition, Onset, abatement, and prevalence period, Diagnosis date and relevant period, Conditions present on admission and principal diagnoses |
| [pattern_medications.md](pattern_medications.md) | Medications | Medications, Medication status, intent, and category, Medication ordered, Medication Not Ordered, Medication administered, Medication not administered, Medication dispensed, Medication not dispensed, Medication in use |
| [pattern_procedures.md](pattern_procedures.md) | Procedures | Procedures, Procedure performed, Procedure not done, Procedure ordered, Procedure not ordered, Imaging Procedures, Nutrition Orders, Procedure Priority |
| [pattern_devices.md](pattern_devices.md) | Devices | Devices, Device ordered, Device not ordered, Device in use |
| [pattern_allergies.md](pattern_allergies.md) | Allergies | Allergies, Current Allergies, Onset, abatement, and prevalence period, Allergy date and relevant period, No Known Allergies, Verified Allergies |
| [pattern_immunizations.md](pattern_immunizations.md) | Immunizations | Immunizations, Immunization performed, Immunization not performed, Immunization recommendations |
| [pattern_communication.md](pattern_communication.md) | Communication | Communication, Communication, Communication Not Done |
| [pattern_claim.md](pattern_claim.md) | Claim | Claim, Claim elements used by measures, Encounter-related Items, Evidence of Diagnosis on an Encounter, History of a Condition, Present on Admission, Principal Diagnosis, Primary Procedure, Discharge Disposition, Admission Source |
| [pattern_coverage.md](pattern_coverage.md) | Coverage | Coverage, Coverage status, Member or subscriber ID, Payer |
| [pattern_billingrelated.md](pattern_billingrelated.md) | Billing-related Elements | Billing-related elements, Preferring claim information, Evidence of Diagnosis during an Encounter, History of a Condition, Present on Admission, Principal Diagnosis, Primary Procedure, Discharge Disposition, Admission Source |
| [pattern_negation.md](pattern_negation.md) | Negation Patterns | Negation Patterns, Choosing a negation pattern, Use cases for negation rationale, Extent of negation, Working with doNotPerform, Positive requests and rejected proposals |
| [usqc_update_process.md](usqc_update_process.md) | US Quality Core Update Process | US Quality Core Update Process, Step 1: Update Models, Step 2: Update Libraries, Step 3: Update Types, Step 4: Replace extension elements:, Step 5: Consider Functions, Step 6: Consider Elements and Patterns |
| [refactored_index.md](refactored_index.md) | Refactored Index | Refactored Index, Library Index, Function Index, Extension Index, Slice Index |
| [knownissues.md](knownissues.md) | Known Issues | Known Issues, Incorrect or Missing Primary Code Paths, Cannot Resolve Fluent Functions on Choices, Seemingly Ambiguous Type References Are Allowed, Fluent Function Overloads, Prevalence Interval Issue: |
| [MADiE.md](MADiE.md) | MADiE | MADiE, MADiE dQM Specifications, dQM Metadata Used in MADiE, Namespaces in MADiE, dQM Export Naming Conventions |
| [manifest_guidance.md](manifest_guidance.md) | CMS Manifest Guidance | CMS Manifest Guidance, CMS Manifest Creation, NLM Manifest Guidance |
| [measure_profile.md](measure_profile.md) | Profiles Used by CMS Measures | Measure Profiles, Quality Measure IG Conformance, CMS Test Case Profile, Extensions, Terminology |
| [examples.md](examples.md) | Examples | Examples |
| [change_control.md](change_control.md) | Change Control Process | Change Control Process, Stakeholders, Process, Applying Updates, Versioning, Publication, Communication |
| [changes.md](changes.md) | Change History | Change History |
