library testLqSort2

define "SortAsc": ({ 3, 1, 2 }) X sort asc
define "SortTupleByElement": ({ Tuple { a: 2 }, Tuple { a: 1 } }) T sort by a
define "SortTupleTypedNull": ({ Tuple { a: 2 }, Tuple { a: 1 }, Tuple { a: null as Integer } }) T sort by a desc
