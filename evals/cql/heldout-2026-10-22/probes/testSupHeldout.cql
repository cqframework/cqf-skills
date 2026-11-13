library testSupHeldout

define "OverlapsClosed": Interval[1, 5] overlaps Interval[5, 10]
define "OverlapsHalfOpen": Interval[1, 5) overlaps Interval[5, 10]
define "MeetsHalfOpen": Interval[1, 5) meets Interval[5, 10]
define "MeetsClosed": Interval[1, 5] meets Interval[5, 10]
define "MonthsBetween": months between @2026-01-31 and @2026-02-28
define "MonthsDifference": difference in months between @2026-01-31 and @2026-02-28
define "MixedList": { 1, 2.0 }
define "FirstIsInteger": First({ 1, 2.0 }) is Integer
define "FirstIsDecimal": First({ 1, 2.0 }) is Decimal
define "CombineNullSep": Combine({ 'a', null, 'b' }, null)
define "UnionNullsCount": Count({ null as Integer, 1 } union { null as Integer })
define "UnionNulls": { null as Integer, 1 } union { null as Integer }
define "SubstringPastEnd": Substring('abc', 5)
define "SubstringAtLength": Substring('abc', 3)
define "SubstringLast": Substring('abc', 2)
define "DateEqDateTime": @2026-01-15 = @2026-01-15T00:00:00.000-04:00
define "DateEqDate": @2026-01-15 = @2026-01-15
define "DateSameDayDateTime": @2026-01-15 same day as @2026-01-15T10:00:00.000-04:00
