library testTqWaAsThenConvert version '1.0.0'

define function g(v Choice<Integer, String>): ToDecimal(v as Integer)
define "FromInt": g(1)
define "FromStr": g('a')
