library testChoiceSubtypeRuntime

using FHIR version '4.0.1'

define fluent function f(x FHIR.AllergyIntolerance): if x is null then 'null-allergy' else 'allergy'
define fluent function f(x FHIR.DomainResource): 'domain'

define function g(event Choice<FHIR.Condition, FHIR.AllergyIntolerance>): event.f()

define "Cond": g(Condition { id: id { value: 'c1' } })
define "Allergy": g(AllergyIntolerance { id: id { value: 'a1' } })
define "BareCond": (Condition { id: id { value: 'c2' } }).f()
