library testNoNarrowingCast

using FHIR version '4.0.1'

define fluent function f(x FHIR.DomainResource): 'domain'
define fluent function f(x FHIR.Condition): 'condition'

define function h(r FHIR.DomainResource):
  case when r is FHIR.Condition then (r as FHIR.Condition).f() else 'other' end
