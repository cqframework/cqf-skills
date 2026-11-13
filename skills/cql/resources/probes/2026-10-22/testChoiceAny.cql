library testChoiceAny

define function k(x Any): 'any'

define function g(v Choice<Integer, String>): k(v)

define "Str": g('a')
