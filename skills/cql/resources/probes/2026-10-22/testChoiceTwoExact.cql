library testChoiceTwoExact

define fluent function f(x Integer): 'int'
define fluent function f(x String): 'string'

define function g(v Choice<Integer, String>): v.f()

define "Int": g(1)
