library testChoiceConvertible

define fluent function f(x Decimal): if x is null then 'null-dec' else 'dec'

define function g(v Choice<Integer, String>): v.f()

define "Int": g(1)
define "Str": g('a')
