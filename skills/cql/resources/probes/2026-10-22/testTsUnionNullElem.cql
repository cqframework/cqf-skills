library testTsUnionNullElem

define "TypedNullBranch":
  { Tuple { d: @2025-01-01T00:00:00.000Z, v: 1 }, Tuple { d: @2025-01-02T00:00:00.000Z, v: null as Integer } }
define "UntypedNullBranch":
  { Tuple { d: @2025-01-01T00:00:00.000Z, v: 1 }, Tuple { d: @2025-01-02T00:00:00.000Z, v: null } }
define "NoNullBranch":
  { Tuple { d: @2025-01-01T00:00:00.000Z, v: 1 }, Tuple { d: @2025-01-02T00:00:00.000Z, v: 2 } }
define "DecimalBranch":
  { Tuple { d: @2025-01-03T00:00:00.000Z, v: 1.5 } }

define "TypedNullUnion": "TypedNullBranch" union "DecimalBranch"
define "TypedNullCount": Count("TypedNullBranch" union "DecimalBranch")
define "UntypedNullUnion": "UntypedNullBranch" union "DecimalBranch"
define "UntypedNullCount": Count("UntypedNullBranch" union "DecimalBranch")
define "NoNullUnion": "NoNullBranch" union "DecimalBranch"
define "NoNullCount": Count("NoNullBranch" union "DecimalBranch")
