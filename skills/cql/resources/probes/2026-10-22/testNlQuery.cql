library testNlQuery

define "WhereGt": ({ 1, null, 3 }) X where X > 1
define "WhereNotGt": ({ 1, null, 3 }) X where not (X > 1)
define "SortAsc": ({ 3, null, 1 }) X sort asc
define "SortDesc": ({ 3, null, 1 }) X sort desc
define "ReturnWithNulls": ({ 1, null, null }) X return X
define "ReturnAllWithNulls": ({ 1, null, null }) X return all X
define "NullListQuery": (null as List<Integer>) X return X
define "EmptyListQuery": (List<Integer> { }) X return X
define "ExistsListOfNull": exists ({ 1, 2 }) X return (null as Integer)
