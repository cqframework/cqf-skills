library testHoMixedList version '1.0.0'

define "MixedList": { 1, 2.0 }
define "FirstIsInteger": First({ 1, 2.0 }) is Integer
define "FirstIsDecimal": First({ 1, 2.0 }) is Decimal
define "ControlIntegerList": First({ 1, 2 }) is Integer
