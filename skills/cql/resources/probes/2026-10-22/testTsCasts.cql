library testTsCasts

define function g(v Choice<Integer, String>): v as Integer

define "AsMismatch": g('a')
define "AsMatch": g(1)
define "ImplicitCastNull": 5 * null
define "ConvertFoo": convert 'foo' to Integer
define "ConvertFive": convert '5' to Integer
define "PointOverload": Interval[1, null] properly includes null
