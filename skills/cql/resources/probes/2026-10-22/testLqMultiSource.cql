library testLqMultiSource

define "Cartesian": from ({ 1, 2 }) A, ({ 10, 20 }) B return all A + B
define "CartesianCount": Count(from ({ 1, 2 }) A, ({ 10, 20 }) B return all A + B)
define "ListAndSingleton": from ({ 1, 2 }) A, (5) B return all A + B
define "BothSingleton": from (1) A, (2) B return A + B
define "WithEmptySource": from ({ 1, 2 }) A, (List<Integer> { }) B return all A
define "WithNullSource": from ({ 1, 2 }) A, (null as List<Integer>) B return all A
define "BothNull": from (null as List<Integer>) A, (null as List<Integer>) B return all A
