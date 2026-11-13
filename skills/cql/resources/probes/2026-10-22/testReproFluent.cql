library testReproFluent

using FHIR version '4.0.1'

define fluent function f(x Condition): 'condition'
define fluent function f(x AllergyIntolerance): 'allergy'

define function g(event Choice<AllergyIntolerance, Condition>):
  event.f()          // binds f(AllergyIntolerance), unconditional As, no warning
