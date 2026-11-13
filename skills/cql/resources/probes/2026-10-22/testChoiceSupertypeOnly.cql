library testChoiceSupertypeOnly

using FHIR version '4.0.1'

define fluent function f(x FHIR.DomainResource): 'domain'

define function g(event Choice<FHIR.Condition, FHIR.AllergyIntolerance>): event.f()
