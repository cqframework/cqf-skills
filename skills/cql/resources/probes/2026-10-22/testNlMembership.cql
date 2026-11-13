library testNlMembership

define "NullInListWithNull": null in { 1, null }
define "NullInListWithout": null in { 1, 2 }
define "FiveInNull": 5 in (null as List<Integer>)
define "ListContainsNull": { 1, null } contains null
define "ListWithoutContainsNull": { 1, 2 } contains null
define "NullListContains": (null as List<Integer>) contains 4
define "NullUnion": (null as List<Integer>) union { 4, 5 }
define "IntersectNull": { 1, 3 } intersect (null as List<Integer>)
define "NullExcept": (null as List<Integer>) except { 1 }
define "ExceptNull": { 1, 3 } except (null as List<Integer>)
define "IntersectWithNulls": { null, 1, 3 } intersect { null, 3, 7 }
define "DistinctNulls": distinct { null, null, 1 }
