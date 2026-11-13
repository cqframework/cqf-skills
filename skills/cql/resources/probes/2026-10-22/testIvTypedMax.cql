library testIvTypedMax

define "TypedMax": Interval[null as Integer, null as Integer]
define "InTypedMax": 5 in Interval[null as Integer, null as Integer]
define "InTypedUnknown": 5 in Interval(null as Integer, null as Integer)
define "TypedMaxOverlaps": Interval[null as Integer, null as Integer] overlaps Interval[1, 10]
define "TypedUnknownOverlaps": Interval(null as Integer, null as Integer) overlaps Interval[1, 10]
define "TypedMaxStarts": Interval[null as Integer, null as Integer] starts Interval[1, 10]
define "TypedMaxUnion": Interval[null as Integer, null as Integer] union Interval[1, 10]
define "StartTypedMax": start of Interval[null as Integer, null as Integer]
define "StartUntypedMax": start of Interval[null, null]
