library testQcIsElm version '1.0.0'

using QICore version '6.0.0'

define function IsSibling(c ConditionProblemsHealthConcerns): c is ConditionEncounterDiagnosis
define function IsSelf(c ConditionProblemsHealthConcerns): c is ConditionProblemsHealthConcerns
