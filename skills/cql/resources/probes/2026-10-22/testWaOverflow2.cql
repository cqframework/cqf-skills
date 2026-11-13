library testWaOverflow2

define "IntegerWraps": 2147483647 + 1
define "AsLong": ToLong(2147483647) + 1
define "AsDecimal": ToDecimal(2147483647) + 1
define "SumAsDecimal": Sum(({ 2147483647, 1 }) X return all ToDecimal(X))
define "SumAsInteger": Sum({ 2147483647, 1 })
