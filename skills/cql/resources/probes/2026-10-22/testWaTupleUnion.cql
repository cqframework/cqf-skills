library testWaTupleUnion

define "TypedNullBranch":
  { Tuple { d: @2025-01-01T00:00:00.000Z, v: 1 }, Tuple { d: @2025-01-02T00:00:00.000Z, v: null as Integer } }
define "DecimalBranch":
  { Tuple { d: @2025-01-03T00:00:00.000Z, v: 1.5 } }
define "RawCount": Count("TypedNullBranch" union "DecimalBranch")
define "NormalisedCount":
  Count(("TypedNullBranch" X return Tuple { d: X.d, v: ToDecimal(X.v) }) union "DecimalBranch")
