library testLqEmpty

define "FirstEmpty": First(List<Integer> { })
define "EmptyEqEmpty": List<Integer> { } = List<Integer> { }
define "ExistsEmpty": exists List<Integer> { }
define "CountEmpty": Count(List<Integer> { })
define "SumEmpty": Sum(List<Integer> { })
define "IndexerOutOfRange": { 1, 2 }[5]
define "IndexerNegative": { 1, 2 }[-1]
define "EmptyUntypedType": { }
