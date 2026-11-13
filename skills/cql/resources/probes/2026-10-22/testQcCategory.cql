library testQcCategory version '1.0.0'

using FHIR version '4.0.1'

define function Cat(code String): FHIR.Condition {
  category: {
    FHIR.CodeableConcept {
      coding: {
        FHIR.Coding {
          system: FHIR.uri { value: 'http://terminology.hl7.org/CodeSystem/condition-category' },
          code: FHIR.code { value: code }
        }
      }
    }
  }
}

define function HasCategory(c FHIR.Condition, code String): exists (
  (c.category) CC where exists ((CC.coding) Cd where Cd.code.value = code)
)

define ProblemItem: Cat('problem-list-item')
define EncounterDx: Cat('encounter-diagnosis')
define NoCategory: FHIR.Condition { id: FHIR.id { value: 'c3' } }
define Both: FHIR.Condition {
  category: {
    FHIR.CodeableConcept { coding: { FHIR.Coding { code: FHIR.code { value: 'problem-list-item' } } } },
    FHIR.CodeableConcept { coding: { FHIR.Coding { code: FHIR.code { value: 'encounter-diagnosis' } } } }
  }
}

define "ProblemItem IsProblem": HasCategory(ProblemItem, 'problem-list-item')
define "ProblemItem IsEncounterDx": HasCategory(ProblemItem, 'encounter-diagnosis')
define "EncounterDx IsProblem": HasCategory(EncounterDx, 'problem-list-item')
define "EncounterDx IsEncounterDx": HasCategory(EncounterDx, 'encounter-diagnosis')
define "NoCategory IsProblem": HasCategory(NoCategory, 'problem-list-item')
define "NoCategory IsEncounterDx": HasCategory(NoCategory, 'encounter-diagnosis')
define "Both IsProblem": HasCategory(Both, 'problem-list-item')
define "Both IsEncounterDx": HasCategory(Both, 'encounter-diagnosis')
