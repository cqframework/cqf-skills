library testTqAnyVsChoiceOverload version '1.0.0'

define function f(x Any): 'any'
define function f(x Choice<Integer, String>): 'choice'
define "IntegerArg": f(5)
