library testReproAsWritten

define function f(x Condition): 'condition'
define function f(x AllergyIntolerance): 'allergy'

define function g(event Choice<AllergyIntolerance, Condition>):
  event.f()          // binds f(AllergyIntolerance), unconditional As, no warning
