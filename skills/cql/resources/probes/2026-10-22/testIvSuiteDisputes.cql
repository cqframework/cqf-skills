library testIvSuiteDisputes

define "MaxOverlaps": Interval[null, null] overlaps Interval[1, 10]
define "UnknownOverlaps": Interval(null, null) overlaps Interval[1, 10]
define "MaxStarts": Interval[null, null] starts Interval[1, 10]
define "MaxUnion": Interval[null, null] union Interval[1, 10]
define "IntersectOpenNull": Interval[1, 10] intersect Interval[5, null)
define "CollapseUnknown": collapse { Interval(null, null) }
define "MeetsAfterNull": Interval(null, 5] meets after Interval[11, null)
define "InMax": 5 in Interval[null, null]
define "InUnknown": 5 in Interval(null, null)
define "NullNullInterval": Interval[null, null]
