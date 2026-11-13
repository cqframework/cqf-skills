library testChoiceOneExact

define fluent function f(x Integer): if x is null then 'null-int' else 'int'

define function g(v Choice<Integer, String>): v.f()

define "Int": g(1)
define "Str": g('a')
