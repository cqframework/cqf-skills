library testNlArith

define "AddNull": 1 + (null as Integer)
define "DivideByZero": 5 / 0
define "DivByZero": 5 div 0
define "ModZero": 5 mod 0
define "PlusConcatNull": 'a' + (null as String)
define "AmpConcatNull": 'a' & (null as String)
define "LengthNullString": Length(null as String)
define "CountWithNull": Count({ null, 1 })
define "SumAllNull": Sum({ null as Integer, null as Integer })
define "IntegerOverflow": 2147483647 + 1
