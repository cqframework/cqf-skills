# FHIR R4 Profile Patterns

Source: https://hl7.org/fhir/R4/
Captured: 2026-04-28, FHIR R4.0.1

This file covers base FHIR R4 profile patterns. Some examples declare QI-Core profiles in
`meta.profile` for illustration; QI-Core's own constraints are defined in the QI-Core IG
(https://hl7.org/fhir/us/qicore/).

---

## Declaring a Profile in a Resource

```json
{
  "resourceType": "Patient",
  "id": "example-patient",
  "meta": {
    "profile": [
      "http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-patient"
    ]
  }
}
```

## Common Resource Patterns

### Patient

```json
{
  "resourceType": "Patient",
  "id": "patient-uuid",
  "meta": { "profile": ["..."] },
  "name": [{ "family": "Smith", "given": ["John"] }],
  "gender": "male",
  "birthDate": "1960-01-15"
}
```

### Encounter

```json
{
  "resourceType": "Encounter",
  "id": "encounter-uuid",
  "status": "finished",
  "class": { "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "IMP" },
  "type": [{ "coding": [{ "system": "...", "code": "...", "display": "..." }] }],
  "subject": { "reference": "Patient/patient-uuid" },
  "period": { "start": "2025-01-15T08:00:00+00:00", "end": "2025-01-17T14:00:00+00:00" }
}
```

### Condition

```json
{
  "resourceType": "Condition",
  "id": "condition-uuid",
  "meta": { "profile": ["http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-condition-problems-health-concerns"] },
  "clinicalStatus": {
    "coding": [{ "system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active" }]
  },
  "verificationStatus": {
    "coding": [{ "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status", "code": "confirmed" }]
  },
  "code": { "coding": [{ "system": "http://snomed.info/sct", "code": "44054006", "display": "Diabetes mellitus type 2" }] },
  "subject": { "reference": "Patient/patient-uuid" }
}
```

### Observation

```json
{
  "resourceType": "Observation",
  "id": "obs-uuid",
  "status": "final",
  "category": [{ "coding": [{ "system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "laboratory" }] }],
  "code": { "coding": [{ "system": "http://loinc.org", "code": "4548-4", "display": "Hemoglobin A1c/Hemoglobin.total in Blood" }] },
  "subject": { "reference": "Patient/patient-uuid" },
  "effectiveDateTime": "2025-01-10T09:00:00+00:00",
  "valueQuantity": { "value": 8.5, "unit": "%", "system": "http://unitsofmeasure.org", "code": "%" }
}
```

## Common Terminology Systems

| System | URI |
|--------|-----|
| SNOMED CT | `http://snomed.info/sct` |
| LOINC | `http://loinc.org` |
| ICD-10-CM | `http://hl7.org/fhir/sid/icd-10-cm` |
| ICD-10-PCS | `http://www.cms.gov/Medicare/Coding/ICD10` |
| CPT | `http://www.ama-assn.org/go/cpt` |
| RxNorm | `http://www.nlm.nih.gov/research/umls/rxnorm` |
| UCUM | `http://unitsofmeasure.org` |
| ActCode (v3) | `http://terminology.hl7.org/CodeSystem/v3-ActCode` |
| Condition clinical status | `http://terminology.hl7.org/CodeSystem/condition-clinical` |
| Condition verification status | `http://terminology.hl7.org/CodeSystem/condition-ver-status` |
| Observation category | `http://terminology.hl7.org/CodeSystem/observation-category` |
