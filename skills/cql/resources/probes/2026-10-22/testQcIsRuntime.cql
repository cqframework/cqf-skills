library testQcIsRuntime version '1.0.0'

using FHIR version '4.0.1'
using QICore version '6.0.0'

define NoProfile: FHIR.Condition { id: FHIR.id { value: 'c1' } }
define WithCphcProfile: FHIR.Condition {
  id: FHIR.id { value: 'c2' },
  meta: FHIR.Meta { profile: { FHIR.canonical { value: 'http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-condition-problems-health-concerns' } } }
}
define "NoProfileIsCPHC": NoProfile is QICore.ConditionProblemsHealthConcerns
define "NoProfileIsCED": NoProfile is QICore.ConditionEncounterDiagnosis
define "NoProfileIsAllergy": NoProfile is QICore.AllergyIntolerance
define "CphcProfileIsCPHC": WithCphcProfile is QICore.ConditionProblemsHealthConcerns
define "CphcProfileIsCED": WithCphcProfile is QICore.ConditionEncounterDiagnosis
