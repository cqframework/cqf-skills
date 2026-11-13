library testLqRelationships

define "WithEmpty": ({ 1, 2 }) X with (List<Integer> { }) Y such that Y = X
define "WithoutEmpty": ({ 1, 2 }) X without (List<Integer> { }) Y such that Y = X
define "WithMatch": ({ 1, 2 }) X with ({ 2, 3 }) Y such that Y = X
define "WithoutMatch": ({ 1, 2 }) X without ({ 2, 3 }) Y such that Y = X
define "WithNullCondition": ({ 1, 2 }) X with ({ 2 }) Y such that (null as Boolean)
define "WithoutNullCondition": ({ 1, 2 }) X without ({ 2 }) Y such that (null as Boolean)
